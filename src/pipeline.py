"""
Drone Saver - Master End-to-End AI Digital Twin Diagnostic Pipeline
Integrates all 4 Stages:
1. Stage 1: Unsupervised Anomaly Detection & Continuous Health Scoring
2. Stage 2: Physics-Guided Fault Isolation & Multi-Class Classification
3. Stage 3: Degradation Tracking & Remaining Useful Life (RUL) Forecasting
4. Stage 4: Dynamic UAV Mission Reliability & Abort Risk Decision Engine

Problem Statement: SIH26054 - DRDO
"""

import os
import sys
sys.path.insert(0, '.')
import glob
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.features import extract_cylinder_features
from src.healthy_baseline import PolynomialFeatureRegressor
from src.mission_risk.mission_reliability import UAVMissionReliabilityEngine
from src.models.anomaly_detector import DigitalTwinAnomalyDetector
from src.models.fault_classifier import DigitalTwinFaultClassifier
from src.models.rul_estimator import DigitalTwinRULEstimator

class DroneSaverDigitalTwinPipeline:
    def __init__(self, model_dir="data/models"):
        self.model_dir = model_dir
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
        print("Loaded Digital Twin AI Models (Anomaly Detector, Fault Classifier, RUL Estimator).")

    def _fit_or_load_baseline_models(self):
        healthy_files = sorted(glob.glob("data/processed/canonical/*_canonical.csv"))
        dfs = []
        for f in healthy_files:
            df = pd.read_csv(f)
            # Filter active engine states
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
            
        print("Initialized Physics Baseline Predictors for Residual Tracking.")

    def _attach_baseline_residuals(self, df):
        """Computes predicted physics baseline and residual columns if missing."""
        df_out = df.copy()
        
        # Check required columns
        req_cols = ['rpm', 'map_kpa', 'fuel_flow_lph', 'ambient_temp_c', 'altitude_m', 'airspeed_mps', 'oil_temp_c', 'oil_pressure_kpa']
        for rc in req_cols:
            if rc not in df_out.columns:
                df_out[rc] = 0.0
                
        X_fuel = df_out[['rpm', 'map_kpa']].values
        X_oil_p = df_out[['rpm', 'oil_temp_c']].values
        X_egt = df_out[['rpm', 'map_kpa', 'fuel_flow_lph', 'ambient_temp_c']].values
        X_cht = df_out[['rpm', 'map_kpa', 'ambient_temp_c', 'altitude_m', 'airspeed_mps']].values
        
        df_out['expected_fuel_flow_lph'] = self.baseline_models['fuel_flow'].predict(X_fuel)
        df_out['residual_fuel_flow_lph'] = df_out['fuel_flow_lph'] - df_out['expected_fuel_flow_lph']
        
        df_out['expected_oil_pressure_kpa'] = self.baseline_models['oil_pressure'].predict(X_oil_p)
        df_out['residual_oil_pressure_kpa'] = df_out['oil_pressure_kpa'] - df_out['expected_oil_pressure_kpa']
        
        for i in range(1, 5):
            egt_col = f'egt_{i}_c'
            cht_col = f'cht_{i}_c'
            if egt_col in df_out.columns:
                exp_egt = self.baseline_models[egt_col].predict(X_egt)
                df_out[f'expected_{egt_col}'] = exp_egt
                df_out[f'residual_{egt_col}'] = df_out[egt_col] - exp_egt
            else:
                df_out[f'residual_{egt_col}'] = 0.0
                
            if cht_col in df_out.columns:
                exp_cht = self.baseline_models[cht_col].predict(X_cht)
                df_out[f'expected_{cht_col}'] = exp_cht
                df_out[f'residual_{cht_col}'] = df_out[cht_col] - exp_cht
            else:
                df_out[f'residual_{cht_col}'] = 0.0
                
        return df_out

    def process_flight(self, flight_csv_path, output_dir="reports/digital_twin_evaluations"):
        os.makedirs(output_dir, exist_ok=True)
        fid = os.path.basename(flight_csv_path).replace('.csv', '')
        print(f"\n================================================================================")
        print(f"RUNNING DIGITAL TWIN DIAGNOSTIC PIPELINE ON: {fid}")
        print(f"================================================================================")
        
        df = pd.read_csv(flight_csv_path)
        
        # Step 1: Attach Baseline Residuals if not present
        df_with_residuals = self._attach_baseline_residuals(df)
        
        # Step 2: Feature Extraction
        temp_residual_path = f"data/processed/canonical/{fid}_temp_res.csv"
        df_with_residuals.to_csv(temp_residual_path, index=False)
        feat_df = extract_cylinder_features(temp_residual_path, output_dir="data/processed/features")
        if os.path.exists(temp_residual_path):
            os.remove(temp_residual_path)
            
        # Step 3: Stage 1 Anomaly Detection
        anom_scores, health_indices, is_anom = self.anomaly_detector.predict_anomaly_score(feat_df)
        feat_df['anomaly_score'] = anom_scores
        feat_df['health_index'] = health_indices
        feat_df['is_anomaly'] = is_anom
        
        # Step 4: Stage 2 Fault Classification & Cylinder Isolation
        pred_faults, pred_probs, pred_cyls = self.fault_classifier.predict_fault(feat_df)
        feat_df['predicted_fault_type'] = pred_faults
        feat_df['fault_probability'] = np.max(pred_probs, axis=1)
        feat_df['predicted_cylinder'] = pred_cyls
        
        # Step 5: Stage 3 Remaining Useful Life (RUL) Estimation
        rul_preds, rul_lows, rul_highs = self.rul_estimator.predict_rul(feat_df)
        feat_df['predicted_rul_sec'] = rul_preds
        feat_df['predicted_rul_lower_sec'] = rul_lows
        feat_df['predicted_rul_upper_sec'] = rul_highs
        
        # Step 6: Stage 4 Mission Reliability & Abort Recommendation
        risk_engine = UAVMissionReliabilityEngine(target_mission_duration_sec=7200.0)
        risk_rows = []
        for i in range(len(feat_df)):
            t = feat_df['time_seconds'].iloc[i]
            hs = feat_df['health_index'].iloc[i]
            f_type = feat_df['predicted_fault_type'].iloc[i]
            f_prob = feat_df['fault_probability'].iloc[i]
            r_pred = feat_df['predicted_rul_sec'].iloc[i]
            r_low = feat_df['predicted_rul_lower_sec'].iloc[i]
            
            risk_info = risk_engine.evaluate_mission_risk(t, hs, f_type, f_prob, r_pred, r_low)
            risk_rows.append(risk_info)
            
        risk_df = pd.DataFrame(risk_rows)
        feat_df['p_mission_success'] = risk_df['p_mission_success']
        feat_df['operator_recommendation'] = risk_df['operator_recommendation']
        feat_df['risk_level'] = risk_df['risk_level']
        
        # Save enriched Digital Twin Telemetry CSV
        processed_csv_path = os.path.join(output_dir, f"{fid}_digital_twin_output.csv")
        feat_df.to_csv(processed_csv_path, index=False)
        print(f"Saved Digital Twin Telemetry Log -> {processed_csv_path}")
        
        # Step 7: Generate Visual Dashboard Timeline Plot
        self._plot_digital_twin_dashboard(feat_df, fid, output_dir)
        
        # Step 8: Generate Markdown Diagnostic Executive Report
        self._generate_markdown_report(feat_df, fid, output_dir)
        
        return feat_df

    def _plot_digital_twin_dashboard(self, df, fid, output_dir):
        time_min = df['time_seconds'] / 60.0
        
        fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
        fig.suptitle(f"Drone Saver — AI Digital Twin Diagnostics: {fid}", fontsize=14, fontweight='bold', y=0.98)
        
        # 1. Thermal Telemetry (EGT & CHT)
        for i in range(1, 5):
            axes[0].plot(time_min, df[f'egt_{i}_c'], label=f'EGT {i}', lw=1.2)
        axes[0].set_ylabel('EGT (°C)')
        axes[0].set_title('Exhaust Gas Temperatures & Thermal Profile')
        axes[0].grid(True)
        axes[0].legend(loc='upper right', ncol=4)
        
        # 2. Continuous Health Index & Anomaly Score
        axes[1].plot(time_min, df['health_index'], color='#2ca02c', lw=2.0, label='Engine Health Score H(t)')
        axes[1].plot(time_min, df['anomaly_score'], color='#d62728', lw=1.5, linestyle='--', label='Anomaly Score A(t)')
        axes[1].axhline(y=0.5, color='orange', linestyle=':', label='Warning Threshold (0.50)')
        axes[1].set_ylabel('Health / Anomaly')
        axes[1].set_ylim([-0.05, 1.05])
        axes[1].set_title('Stage 1: Real-Time Anomaly Health Scoring')
        axes[1].grid(True)
        axes[1].legend(loc='upper right')
        
        # 3. Remaining Useful Life (RUL) Forecast with 90% Confidence Bounds
        axes[2].plot(time_min, df['predicted_rul_sec'] / 60.0, color='#1f77b4', lw=2.0, label='Predicted RUL (Minutes)')
        axes[2].fill_between(
            time_min, 
            df['predicted_rul_lower_sec'] / 60.0, 
            df['predicted_rul_upper_sec'] / 60.0, 
            color='#1f77b4', alpha=0.25, label='90% Confidence Interval'
        )
        axes[2].set_ylabel('RUL (Minutes)')
        axes[2].set_title('Stage 3: Degradation Tracking & RUL Forecast')
        axes[2].grid(True)
        axes[2].legend(loc='upper right')
        
        # 4. Mission Reliability & Survival Probability
        axes[3].plot(time_min, df['p_mission_success'], color='#9467bd', lw=2.0, label='P(Mission Success)')
        axes[3].set_ylabel('Survival Probability')
        axes[3].set_ylim([-0.05, 1.05])
        axes[3].set_xlabel('Flight Time (Minutes)')
        axes[3].set_title('Stage 4: Mission Survival Probability & Failsafe Boundaries')
        axes[3].grid(True)
        axes[3].legend(loc='upper right')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        plot_path = os.path.join(output_dir, f"{fid}_digital_twin_dashboard.png")
        plt.savefig(plot_path, dpi=180)
        plt.close()
        print(f"Generated Digital Twin Diagnostic Dashboard -> {plot_path}")

    def _generate_markdown_report(self, df, fid, output_dir):
        min_health = df['health_index'].min()
        final_health = df['health_index'].iloc[-1]
        
        fault_counts = df[df['predicted_fault_type'] != 'HEALTHY']['predicted_fault_type'].value_counts()
        top_fault = fault_counts.index[0] if len(fault_counts) > 0 else 'HEALTHY (NO FAULT)'
        
        cyl_counts = df[df['predicted_fault_type'] != 'HEALTHY']['predicted_cylinder'].value_counts()
        top_cyl = cyl_counts.index[0] if len(cyl_counts) > 0 else 0
        
        final_rul_min = df['predicted_rul_sec'].iloc[-1] / 60.0
        final_rec = df['operator_recommendation'].iloc[-1]
        final_risk = df['risk_level'].iloc[-1]
        
        report_lines = [
            f"# Drone Saver — AI Digital Twin Mission Diagnostic Report: `{fid}`",
            f"**Project:** Drone Saver (SIH26054 — DRDO)",
            f"**Total Evaluated Telemetry Duration:** {len(df):,} seconds ({len(df)/60.0:.1f} flight minutes)",
            "",
            "---",
            "## Executive Diagnostic Summary",
            "",
            f"| Metric | Assessment / Value | Status |",
            f"| :--- | :--- | :--- |",
            f"| **Overall Engine Health Score** | `{final_health:.3f}` (Minimum during flight: `{min_health:.3f}`) | {'🟢 NOMINAL' if final_health > 0.8 else '🔴 DEGRADED'} |",
            f"| **Primary Detected Fault Class** | `{top_fault}` | {'🟢 NONE' if top_fault.startswith('HEALTHY') else '⚠️ ACTIVE'} |",
            f"| **Isolated Faulty Cylinder** | `Cylinder #{top_cyl}` (0 = Global Engine) | {'🟢 BALANCED' if top_cyl == 0 and top_fault.startswith('HEALTHY') else '⚠️ ISOLATED'} |",
            f"| **Predicted Remaining Useful Life** | `{final_rul_min:.1f} flight minutes` | {'🟢 HIGH' if final_rul_min > 30 else '⚠️ CRITICAL'} |",
            f"| **Mission Risk Level** | `{final_risk}` | - |",
            f"| **Operator / Autopilot Directive** | `{final_rec}` | - |",
            "",
            "---",
            "## Multi-Stage Digital Twin Architecture Telemetry",
            "- **Stage 1 (Anomaly Detection):** Isolation Forest evaluated on 20-dimensional physics residuals.",
            "- **Stage 2 (Fault Classification):** Gradient Boosted classifier on 85 physics-derived multi-cylinder features.",
            "- **Stage 3 (RUL Prognostics):** Dual-quantile regression trees estimating median RUL and 90% confidence bounds.",
            "- **Stage 4 (Mission Reliability):** Monte Carlo survival simulation evaluating in-flight loiter survivability.",
            "",
            f"![Digital Twin Timeline Dashboard]({fid}_digital_twin_dashboard.png)"
        ]
        
        report_file = os.path.join(output_dir, f"{fid}_diagnostic_report.md")
        with open(report_file, "w", encoding="utf-8") as fp:
            fp.write("\n".join(report_lines))
        print(f"Generated Executive Diagnostic Report -> {report_file}")

def test_full_pipeline():
    pipeline = DroneSaverDigitalTwinPipeline()
    
    test_flights = [
        "data/processed/flights_healthy/flight_01_healthy.csv",
        "data/injected/ignition/flight_01_ft01_spark_cyl1.csv",
        "data/injected/valve/flight_01_ft03_valve_cyl3.csv",
        "data/injected/thermal/flight_01_ft04_detonation_cyl1.csv",
        "data/injected/lubrication/flight_01_ft06_lubrication_loss.csv",
        "data/simulation/sim_male_uav_30kft_mission.csv"
    ]
    
    for tf in test_flights:
        if os.path.exists(tf):
            pipeline.process_flight(tf)

if __name__ == "__main__":
    test_full_pipeline()
