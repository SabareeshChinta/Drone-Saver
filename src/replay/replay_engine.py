"""
Drone Saver - Interactive Digital Twin Telemetry Replay Engine
Executes real-time, sequential single-step inference:
t -> baseline -> residuals -> anomaly -> fault -> cylinder -> RUL -> mission risk -> decision
Problem Statement: SIH26054 - DRDO
"""

import os
import sys
sys.path.insert(0, '.')
import glob
import pickle
import argparse
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.replay.state_tracker import StreamingStateTracker
from src.replay.scenario_loader import ScenarioLoader
from src.replay.terminal_ui import TerminalDashboardUI
from src.healthy_baseline import PolynomialFeatureRegressor
from src.mission_risk.mission_reliability import UAVMissionReliabilityEngine
from src.models.anomaly_detector import DigitalTwinAnomalyDetector
from src.models.fault_classifier import DigitalTwinFaultClassifier
from src.models.rul_estimator import DigitalTwinRULEstimator

class DigitalTwinReplayEngine:
    def __init__(self, model_dir="data/models", results_dir="results"):
        self.model_dir = model_dir
        self.results_dir = results_dir
        os.makedirs(f"{results_dir}/replay", exist_ok=True)
        os.makedirs(f"{results_dir}/figures", exist_ok=True)
        
        self.anomaly_detector = None
        self.fault_classifier = None
        self.rul_estimator = None
        self.baseline_models = {}
        self.ui = TerminalDashboardUI()
        
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

    def run_replay(self, scenario_path, step_delay_sec=0.0, render_terminal=True):
        loader = ScenarioLoader()
        df_feed, spec = loader.load_scenario(scenario_path)
        scenario_id = spec.get('scenario_id', 'SCENARIO_DEMO')
        total_mission_sec = spec.get('total_mission_duration_sec', 7200.0)
        
        tracker = StreamingStateTracker()
        risk_engine = UAVMissionReliabilityEngine(target_mission_duration_sec=total_mission_sec)
        
        n_steps = len(df_feed)
        replay_log = []
        
        print(f"\n[DRONE SAVER] Starting Sequential Telemetry Replay for: {scenario_id} ({n_steps} steps)")
        
        for idx in range(n_steps):
            row_dict = df_feed.iloc[idx].to_dict()
            t_curr = row_dict.get('time_seconds', idx)
            
            # Step 1: Update causal state history tracker
            step_feats = tracker.update(row_dict)
            
            # Step 2: Compute baseline predictions & physics residuals
            rpm = step_feats.get('rpm', 0.0)
            map_kpa = step_feats.get('map_kpa', 0.0)
            fflow = step_feats.get('fuel_flow_lph', 0.0)
            oat = step_feats.get('ambient_temp_c', 15.0)
            alt = step_feats.get('altitude_m', 500.0)
            ias = step_feats.get('airspeed_mps', 40.0)
            oil_t = step_feats.get('oil_temp_c', 80.0)
            
            exp_fflow = float(self.baseline_models['fuel_flow'].predict([[rpm, map_kpa]])[0])
            exp_oil_p = float(self.baseline_models['oil_pressure'].predict([[rpm, oil_t]])[0])
            
            res_fflow = fflow - exp_fflow
            res_oil_p = step_feats.get('oil_pressure_kpa', 450.0) - exp_oil_p
            
            step_feats['expected_fuel_flow_lph'] = exp_fflow
            step_feats['residual_fuel_flow_lph'] = res_fflow
            step_feats['expected_oil_pressure_kpa'] = exp_oil_p
            step_feats['residual_oil_pressure_kpa'] = res_oil_p
            
            for i in range(1, 5):
                exp_egt = float(self.baseline_models[f'egt_{i}_c'].predict([[rpm, map_kpa, fflow, oat]])[0])
                exp_cht = float(self.baseline_models[f'cht_{i}_c'].predict([[rpm, map_kpa, oat, alt, ias]])[0])
                
                step_feats[f'expected_egt_{i}_c'] = exp_egt
                step_feats[f'residual_egt_{i}_c'] = step_feats.get(f'egt_{i}_c', 0.0) - exp_egt
                step_feats[f'expected_cht_{i}_c'] = exp_cht
                step_feats[f'residual_cht_{i}_c'] = step_feats.get(f'cht_{i}_c', 0.0) - exp_cht
                
            # Convert single step features to DataFrame for model predictions
            single_df = pd.DataFrame([step_feats])
            
            # Step 3: Stage 1 Anomaly Detection
            anom_score, health_idx, is_anom = self.anomaly_detector.predict_anomaly_score(single_df)
            anom_val = float(anom_score[0])
            health_val = float(health_idx[0])
            
            # Step 4: Stage 2 Fault Classification & Cylinder Isolation
            pred_fault, pred_probs, pred_cyl = self.fault_classifier.predict_fault(single_df)
            top_fault = pred_fault[0]
            top_prob = float(np.max(pred_probs[0]))
            top_cyl = int(pred_cyl[0])
            
            # Step 5: Stage 3 Scenario RUL Estimation
            rul_pred, rul_low, rul_high = self.rul_estimator.predict_rul(single_df)
            rul_val = float(rul_pred[0])
            rul_low_val = float(rul_low[0])
            
            # Step 6: Stage 4 Mission Reliability & Decision Support
            risk_info = risk_engine.evaluate_mission_risk(
                current_time_sec=t_curr,
                health_score=health_val,
                fault_type=top_fault,
                fault_prob=top_prob,
                rul_pred_sec=rul_val,
                rul_lower_sec=rul_low_val
            )
            
            # Assemble Log Entry
            log_entry = {
                'timestamp': row_dict.get('timestamp', str(t_curr)),
                'time_seconds': t_curr,
                'rpm': rpm,
                'map_kpa': map_kpa,
                'altitude_m': alt,
                'airspeed_mps': ias,
                'health_score': health_val,
                'anomaly_score': anom_val,
                'predicted_fault': top_fault,
                'fault_probability': top_prob,
                'predicted_cylinder': top_cyl,
                'scenario_rul_sec': rul_val,
                'scenario_rul_lower_sec': rul_low_val,
                'scenario_rul_upper_sec': float(rul_high[0]),
                'remaining_mission_sec': risk_info['time_remaining_mission_sec'],
                'p_mission_success': risk_info['p_mission_success'],
                'p_rtb_safe': risk_info['p_rtb_safe'],
                'risk_level': risk_info['risk_level'],
                'decision': risk_info['operator_recommendation'],
                'action_protocol': risk_info['action_protocol']
            }
            
            # Copy all thermal values for plotting
            for i in range(1, 5):
                log_entry[f'egt_{i}_c'] = step_feats.get(f'egt_{i}_c', 0.0)
                log_entry[f'cht_{i}_c'] = step_feats.get(f'cht_{i}_c', 0.0)
                log_entry[f'expected_egt_{i}_c'] = step_feats.get(f'expected_egt_{i}_c', 0.0)
                log_entry[f'expected_cht_{i}_c'] = step_feats.get(f'expected_cht_{i}_c', 0.0)
                log_entry[f'residual_egt_{i}_c'] = step_feats.get(f'residual_egt_{i}_c', 0.0)
                log_entry[f'residual_cht_{i}_c'] = step_feats.get(f'residual_cht_{i}_c', 0.0)
                
            replay_log.append(log_entry)
            
            # Render to Terminal UI every 150 seconds or on major alert
            if render_terminal and (idx % 150 == 0 or idx == n_steps - 1 or (anom_val > 0.5 and idx % 30 == 0)):
                frame_state = {
                    'scenario_id': scenario_id,
                    'total_mission_sec': total_mission_sec,
                    **log_entry
                }
                print(self.ui.render_frame(frame_state))
                if step_delay_sec > 0:
                    time.sleep(step_delay_sec)
                    
        # Save replay output CSV
        df_out = pd.DataFrame(replay_log)
        csv_path = f"{self.results_dir}/replay/{scenario_id}.csv"
        df_out.to_csv(csv_path, index=False)
        print(f"[DRONE SAVER] Replay Complete! Saved Replay Telemetry -> {csv_path}")
        
        # Generate 9-Panel Visualization Dashboard
        self._generate_dashboard_plot(df_out, scenario_id, spec)
        return df_out

    def _generate_dashboard_plot(self, df, scenario_id, spec):
        t_min = df['time_seconds'] / 60.0
        onset_sec = spec.get('onset_time_sec', None)
        onset_min = (onset_sec / 60.0) if (onset_sec and spec.get('fault_type') != 'HEALTHY') else None
        
        fig, axes = plt.subplots(4, 2, figsize=(16, 12), sharex=True)
        fig.suptitle(f"Drone Saver — Real-Time Replay Dashboard: {scenario_id}", fontsize=14, fontweight='bold', y=0.98)
        
        # 1. Observed vs Baseline EGT
        for i in range(1, 5):
            axes[0, 0].plot(t_min, df[f'egt_{i}_c'], label=f'Obs EGT {i}', lw=1.2)
        axes[0, 0].plot(t_min, df['expected_egt_1_c'], color='black', linestyle='--', label='Baseline Physics Twin', lw=1.5)
        axes[0, 0].set_ylabel('EGT (°C)')
        axes[0, 0].set_title('Exhaust Gas Temperature (EGT) vs Baseline')
        axes[0, 0].grid(True)
        axes[0, 0].legend(loc='upper right', ncol=2, fontsize=8)
        
        # 2. Observed vs Baseline CHT
        for i in range(1, 5):
            axes[0, 1].plot(t_min, df[f'cht_{i}_c'], label=f'Obs CHT {i}', lw=1.2)
        axes[0, 1].plot(t_min, df['expected_cht_1_c'], color='black', linestyle='--', label='Baseline Physics Twin', lw=1.5)
        axes[0, 1].set_ylabel('CHT (°C)')
        axes[0, 1].set_title('Cylinder Head Temperature (CHT) vs Baseline')
        axes[0, 1].grid(True)
        axes[0, 1].legend(loc='upper right', ncol=2, fontsize=8)
        
        # 3. Residual Vectors
        for i in range(1, 5):
            axes[1, 0].plot(t_min, df[f'residual_egt_{i}_c'], label=f'Res EGT {i}', lw=1.0)
        axes[1, 0].axhline(y=45.0, color='red', linestyle=':', label='Threshold (+45°C)')
        axes[1, 0].axhline(y=-45.0, color='red', linestyle=':')
        axes[1, 0].set_ylabel('Residual (°C)')
        axes[1, 0].set_title('Physics-Informed Residual Divergence r(t)')
        axes[1, 0].grid(True)
        axes[1, 0].legend(loc='upper right', ncol=3, fontsize=8)
        
        # 4. Anomaly Score & Health Trajectory
        axes[1, 1].plot(t_min, df['health_score'], color='green', lw=2.0, label='Health Score H(t)')
        axes[1, 1].plot(t_min, df['anomaly_score'], color='red', lw=1.5, linestyle='--', label='Anomaly Score A(t)')
        axes[1, 1].axhline(y=0.5, color='orange', linestyle=':', label='Warning Threshold (0.50)')
        axes[1, 1].set_ylabel('Score [0, 1]')
        axes[1, 1].set_title('Stage 1: Real-Time Anomaly & Health Trajectory')
        axes[1, 1].grid(True)
        axes[1, 1].legend(loc='upper right', fontsize=8)
        
        # 5. Fault Probabilities & Cylinder Attribution
        axes[2, 0].plot(t_min, df['fault_probability'], color='purple', lw=2.0, label='Top Fault Confidence')
        axes[2, 0].set_ylabel('Confidence')
        axes[2, 0].set_title('Stage 2: Fault Classifier Probability')
        axes[2, 0].grid(True)
        axes[2, 0].legend(loc='upper right', fontsize=8)
        
        # 6. Scenario RUL Trajectory with 90% Confidence Bounds
        axes[2, 1].plot(t_min, df['scenario_rul_sec'] / 60.0, color='#1f77b4', lw=2.0, label='Scenario Time-to-Limit (Min)')
        axes[2, 1].fill_between(
            t_min,
            df['scenario_rul_lower_sec'] / 60.0,
            df['scenario_rul_upper_sec'] / 60.0,
            color='#1f77b4', alpha=0.25, label='90% Quantile Bounds'
        )
        axes[2, 1].set_ylabel('Time Margin (Min)')
        axes[2, 1].set_title('Stage 3: Scenario RUL & Prognostics Margin')
        axes[2, 1].grid(True)
        axes[2, 1].legend(loc='upper right', fontsize=8)
        
        # 7. Mission Survival Probability
        axes[3, 0].plot(t_min, df['p_mission_success'], color='#9467bd', lw=2.0, label='P(Mission Success)')
        axes[3, 0].plot(t_min, df['p_rtb_safe'], color='#2ca02c', lw=1.5, linestyle='--', label='P(Safe RTB Reachable)')
        axes[3, 0].axhline(y=0.70, color='orange', linestyle=':', label='RTB Failsafe Threshold (0.70)')
        axes[3, 0].set_ylabel('Probability')
        axes[3, 0].set_xlabel('Flight Time (Minutes)')
        axes[3, 0].set_title('Stage 4: Dynamic Mission Survival Probability')
        axes[3, 0].grid(True)
        axes[3, 0].legend(loc='upper right', fontsize=8)
        
        # 8. Decision Timeline
        dec_numeric = df['decision'].map({
            'CONTINUE_MISSION': 3,
            'DERATE_POWER_AND_LOITER': 2,
            'ABORT_RETURN_TO_BASE': 1,
            'EMERGENCY_DESCENT_LANDING': 0
        }).fillna(3)
        axes[3, 1].step(t_min, dec_numeric, color='navy', lw=2.0, where='post')
        axes[3, 1].set_yticks([0, 1, 2, 3])
        axes[3, 1].set_yticklabels(['EMERGENCY', 'RTB ABORT', 'DERATE 65%', 'CONTINUE'], fontsize=9)
        axes[3, 1].set_xlabel('Flight Time (Minutes)')
        axes[3, 1].set_title('Autopilot Failsafe Decision Directives')
        axes[3, 1].grid(True)
        
        # Mark fault onset on all subplots if active
        if onset_min is not None:
            for r in range(4):
                for c in range(2):
                    axes[r, c].axvline(x=onset_min, color='crimson', linestyle='--', alpha=0.7)
                    
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        fig_path = f"{self.results_dir}/figures/{scenario_id}_dashboard.png"
        plt.savefig(fig_path, dpi=180)
        plt.close()
        print(f"[DRONE SAVER] Generated 9-Panel Diagnostic Figure -> {fig_path}")

def main():
    parser = argparse.ArgumentParser(description="Drone Saver - Interactive Digital Twin Replay")
    parser.add_argument("--scenario", type=str, default="scenarios/FINAL_DEMO.yaml", help="Path to scenario YAML file")
    parser.add_argument("--delay", type=float, default=0.0, help="Terminal replay delay per step in seconds")
    args = parser.parse_args()
    
    engine = DigitalTwinReplayEngine()
    engine.run_replay(args.scenario, step_delay_sec=args.delay)

if __name__ == "__main__":
    main()
