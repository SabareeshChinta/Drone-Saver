"""
Drone Saver - Live Streaming Digital Twin Pipeline & Ingestion Engine
Integrates live UDP / Serial / Replay streams with 1.0 Hz causal inference:
Packet -> Validator -> Causal Buffer -> Baseline -> Residual Normalizer -> Anomaly -> Fault -> RUL -> Failsafe State Machine
Problem Statement: SIH26054 - DRDO
"""

import os
import sys
sys.path.insert(0, '.')
import time
import glob
import pickle
import argparse
import pandas as pd
import numpy as np

from src.replay.telemetry_listener import UDPSource, SerialSource, ReplaySource
from src.replay.telemetry_validator import TelemetryPacketValidator
from src.models.airframe_normalizer import AirframeBaselineNormalizer
from src.replay.state_tracker import StreamingStateTracker
from src.mission_risk.failsafe_state_machine import FailsafeStateMachine
from src.replay.state_export import EngineHealthState
from src.healthy_baseline import PolynomialFeatureRegressor
from src.mission_risk.mission_reliability import UAVMissionReliabilityEngine

class LiveDigitalTwinPipeline:
    def __init__(self, model_dir="data/models", results_dir="results"):
        self.model_dir = model_dir
        self.results_dir = results_dir
        os.makedirs(f"{results_dir}/replay", exist_ok=True)
        os.makedirs(f"{results_dir}/events", exist_ok=True)
        os.makedirs(f"{results_dir}/figures", exist_ok=True)
        
        self.validator = TelemetryPacketValidator()
        self.normalizer = AirframeBaselineNormalizer()
        self.tracker = StreamingStateTracker()
        self.failsafe_sm = FailsafeStateMachine()
        
        self.anomaly_detector = None
        self.fault_classifier = None
        self.rul_estimator = None
        self.baseline_models = {}
        
        self._load_models()
        self._fit_or_load_baseline_models()
        
    def _load_models(self):
        with open(os.path.join(self.model_dir, "anomaly_detector.pkl"), "rb") as fp:
            self.anomaly_detector = pickle.load(fp)
        with open(os.path.join(self.model_dir, "fault_classifier.pkl"), "rb") as fp:
            self.fault_classifier = pickle.load(fp)
        with open(os.path.join(self.model_dir, "rul_estimator.pkl"), "rb") as fp:
            self.rul_estimator = pickle.load(fp)
            
    def _fit_or_load_baseline_models(self):
        healthy_files = sorted(glob.glob("data/processed/canonical/*_canonical.csv"))
        dfs = []
        for f in healthy_files:
            df = pd.read_csv(f)
            act = df[(df['rpm'] > 1200) & (df['map_kpa'] > 40.0)].copy()
            dfs.append(act)
        train_pool = pd.concat(dfs, ignore_index=True)
        
        X_fuel = train_pool[['rpm', 'map_kpa']].values
        y_fuel = train_pool['fuel_flow_lph'].values
        self.baseline_models['fuel_flow'] = PolynomialFeatureRegressor().fit(X_fuel, y_fuel)
        
        X_oil_p = train_pool[['rpm', 'oil_temp_c']].values
        y_oil_p = train_pool['oil_pressure_kpa'].values
        self.baseline_models['oil_pressure'] = PolynomialFeatureRegressor().fit(X_oil_p, y_oil_p)
        
        X_egt = train_pool[['rpm', 'map_kpa', 'fuel_flow_lph', 'ambient_temp_c']].values
        X_cht = train_pool[['rpm', 'map_kpa', 'ambient_temp_c', 'altitude_m', 'airspeed_mps']].values
        
        for i in range(1, 5):
            self.baseline_models[f'egt_{i}_c'] = PolynomialFeatureRegressor().fit(X_egt, train_pool[f'egt_{i}_c'].values)
            self.baseline_models[f'cht_{i}_c'] = PolynomialFeatureRegressor().fit(X_cht, train_pool[f'cht_{i}_c'].values)

    def process_packet(self, raw_packet, total_mission_duration_sec=7200.0):
        """
        Executes real-time single packet processing loop.
        Returns:
            state (EngineHealthState): Canonical serializable state object.
            latency_dict (dict): Microsecond profiling breakdown.
        """
        t_start = time.perf_counter()
        
        # 1. Packet Validation & Sensor Confidence
        t0 = time.perf_counter()
        valid_packet, p_status, confidences, notes = self.validator.validate_packet(raw_packet)
        t_val = (time.perf_counter() - t0) * 1000.0
        
        t_curr = valid_packet.get('time_seconds', 0.0)
        
        # 2. Update Causal State Tracker
        t0 = time.perf_counter()
        step_feats = self.tracker.update(valid_packet)
        
        # 3. Compute Physics Baseline Residuals
        rpm = step_feats.get('rpm', 0.0)
        map_kpa = step_feats.get('map_kpa', 0.0)
        fflow = step_feats.get('fuel_flow_lph', 0.0)
        oat = step_feats.get('ambient_temp_c', 15.0)
        alt = step_feats.get('altitude_m', 500.0)
        ias = step_feats.get('airspeed_mps', 40.0)
        oil_t = step_feats.get('oil_temp_c', 80.0)
        
        exp_fflow = float(self.baseline_models['fuel_flow'].predict([[rpm, map_kpa]])[0])
        exp_oil_p = float(self.baseline_models['oil_pressure'].predict([[rpm, oil_t]])[0])
        
        step_feats['expected_fuel_flow_lph'] = exp_fflow
        step_feats['residual_fuel_flow_lph'] = fflow - exp_fflow
        step_feats['expected_oil_pressure_kpa'] = exp_oil_p
        step_feats['residual_oil_pressure_kpa'] = step_feats.get('oil_pressure_kpa', 450.0) - exp_oil_p
        
        for i in range(1, 5):
            exp_egt = float(self.baseline_models[f'egt_{i}_c'].predict([[rpm, map_kpa, fflow, oat]])[0])
            exp_cht = float(self.baseline_models[f'cht_{i}_c'].predict([[rpm, map_kpa, oat, alt, ias]])[0])
            
            step_feats[f'expected_egt_{i}_c'] = exp_egt
            step_feats[f'residual_egt_{i}_c'] = step_feats.get(f'egt_{i}_c', 0.0) - exp_egt
            step_feats[f'expected_cht_{i}_c'] = exp_cht
            step_feats[f'residual_cht_{i}_c'] = step_feats.get(f'cht_{i}_c', 0.0) - exp_cht
            
        # 4. Airframe Baseline Residual Calibration
        t0_norm = time.perf_counter()
        calibrated_step_feats = self.normalizer.calibrate_residuals(step_feats, is_engine_active=(rpm > 1200))
        t_norm = (time.perf_counter() - t0_norm) * 1000.0
        
        single_df = pd.DataFrame([calibrated_step_feats])
        t_feats = (time.perf_counter() - t0) * 1000.0
        
        # 5. Stage 1: Anomaly Detector
        t0 = time.perf_counter()
        for c in self.anomaly_detector.actual_cols:
            if c not in single_df.columns:
                single_df[c] = 0.0
        anom_score, health_idx, is_anom = self.anomaly_detector.predict_anomaly_score(single_df)
        anom_val = float(anom_score[0])
        health_val = float(health_idx[0])
        t_anom = (time.perf_counter() - t0) * 1000.0
        
        # 6. Stage 2: Fault Classifier & Cylinder Isolator
        t0 = time.perf_counter()
        for c in self.fault_classifier.feature_cols:
            if c not in single_df.columns:
                single_df[c] = 0.0
        pred_fault, pred_probs, pred_cyl = self.fault_classifier.predict_fault(single_df)
        top_fault = pred_fault[0]
        top_prob = float(np.max(pred_probs[0]))
        top_cyl = int(pred_cyl[0])
        t_clf = (time.perf_counter() - t0) * 1000.0
        
        # 7. Stage 3: Scenario RUL Forecaster
        t0 = time.perf_counter()
        for c in self.rul_estimator.feature_cols:
            if c not in single_df.columns:
                single_df[c] = 0.0
        rul_pred, rul_low, rul_high = self.rul_estimator.predict_rul(single_df)
        rul_val = float(rul_pred[0])
        rul_low_val = float(rul_low[0])
        t_rul = (time.perf_counter() - t0) * 1000.0
        
        # 8. Stage 4: Mission Reliability & Failsafe State Machine
        t0 = time.perf_counter()
        time_remaining_mission = max(0.0, total_mission_duration_sec - t_curr)
        time_needed_to_rtb = 1200.0
        
        sigma = max(0.05, (rul_val - rul_low_val) / (rul_val + 1e-3))
        mc_ruls = np.random.lognormal(mean=np.log(max(1.0, rul_val)), sigma=sigma, size=1000)
        p_mission_success = float(np.mean(mc_ruls > time_remaining_mission))
        p_rtb_safe = float(np.mean(mc_ruls > time_needed_to_rtb))
        
        # Failsafe State Machine Update
        mean_conf = float(np.mean(list(confidences.values())))
        current_state, action_cmd = self.failsafe_sm.update(
            t_sec=t_curr,
            health_score=health_val,
            anomaly_score=anom_val,
            fault_type=top_fault,
            fault_prob=top_prob,
            scenario_rul_sec=rul_val,
            p_mission_success=p_mission_success,
            p_rtb_safe=p_rtb_safe,
            sensor_confidence=mean_conf
        )
        t_risk = (time.perf_counter() - t0) * 1000.0
        
        total_latency_ms = (time.perf_counter() - t_start) * 1000.0
        
        # Safe float conversion for timestamp
        raw_ts = valid_packet.get('timestamp', t_curr)
        try:
            ts_val = float(raw_ts)
        except Exception:
            ts_val = float(t_curr)
            
        state = EngineHealthState(
            timestamp=ts_val,
            time_seconds=float(t_curr),
            engine_health=round(health_val, 3),
            anomaly_score=round(anom_val, 3),
            fault=top_fault,
            fault_probability=round(top_prob, 3),
            affected_cylinder=top_cyl,
            scenario_rul_sec=round(rul_val, 1),
            mission_success_probability=round(p_mission_success, 3),
            p_rtb_safe=round(p_rtb_safe, 3),
            failsafe_state=current_state,
            recommendation=action_cmd,
            sensor_confidences=confidences
        )
        
        latencies = {
            'validation_ms': t_val,
            'normalization_ms': t_norm,
            'features_ms': t_feats,
            'anomaly_ms': t_anom,
            'classifier_ms': t_clf,
            'rul_ms': t_rul,
            'risk_state_ms': t_risk,
            'total_ms': total_latency_ms
        }
        return state, latencies, calibrated_step_feats

    def run_live_stream(self, source: TelemetrySource, max_packets=None, print_interval=100):
        source.connect()
        packet_count = 0
        log_rows = []
        
        print("\n[LIVE PIPELINE] Streaming active. Processing 1.0 Hz telemetry packets...")
        
        try:
            while True:
                packet = source.read()
                if packet is None:
                    break
                    
                packet_count += 1
                state, lat, step_feats = self.process_packet(packet)
                
                log_row = {
                    **state.to_dict(),
                    'total_latency_ms': lat['total_ms'],
                    **{k: step_feats.get(k, 0.0) for k in ['rpm', 'map_kpa', 'altitude_m', 'airspeed_mps',
                                                           'egt_1_c', 'egt_2_c', 'egt_3_c', 'egt_4_c',
                                                           'cht_1_c', 'cht_2_c', 'cht_3_c', 'cht_4_c',
                                                           'residual_egt_1_c', 'residual_cht_1_c']}
                }
                log_rows.append(log_row)
                
                if packet_count % print_interval == 0 or packet_count == 1 or state.failsafe_state in ['RTB', 'EMERGENCY']:
                    print(f"[@ t={state.time_seconds:.0f}s] Health={state.engine_health:.3f} | Anom={state.anomaly_score:.3f} | Fault={state.fault} ({state.fault_probability*100:.0f}%) | Cyl={state.affected_cylinder} | RUL={state.scenario_rul_sec/60:.1f}m | State={state.failsafe_state} | Latency={lat['total_ms']:.2f}ms")
                    
                if max_packets and packet_count >= max_packets:
                    break
        finally:
            source.close()
            
        df_out = pd.DataFrame(log_rows)
        return df_out
