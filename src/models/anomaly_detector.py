"""
Drone Saver - Stage 1: Unsupervised Anomaly Detection Engine
Fits multi-dimensional residual distance and Isolation Forest models on healthy flight baseline:
- Monitors residual vector r(t) = [res_egt1..4, res_cht1..4, res_oil_p, res_fflow, EGT_spread, CHT_spread]
- Computes continuous Anomaly Score A(t) in [0.0, 1.0] and Health Index H(t) = 1 - A(t)
- Detects early anomaly onset prior to catastrophic breakdown
Problem Statement: SIH26054 - DRDO
"""

import os
import glob
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class DigitalTwinAnomalyDetector:
    def __init__(self, contamination=0.01, random_state=42):
        self.scaler = StandardScaler()
        self.iso_forest = IsolationForest(
            n_estimators=150,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1
        )
        self.feature_cols = [
            'residual_egt_1_c', 'residual_egt_2_c', 'residual_egt_3_c', 'residual_egt_4_c',
            'residual_cht_1_c', 'residual_cht_2_c', 'residual_cht_3_c', 'residual_cht_4_c',
            'residual_oil_pressure_kpa', 'residual_fuel_flow_lph',
            'egt_spread_c', 'cht_spread_c',
            'egt_dev_mean_cyl1_c', 'egt_dev_mean_cyl2_c', 'egt_dev_mean_cyl3_c', 'egt_dev_mean_cyl4_c',
            'cht_dev_mean_cyl1_c', 'cht_dev_mean_cyl2_c', 'cht_dev_mean_cyl3_c', 'cht_dev_mean_cyl4_c'
        ]
        self.is_fitted = False
        self.healthy_threshold = 0.50
        
    def fit_healthy_baseline(self, healthy_feature_files):
        """Fits the anomaly model exclusively on healthy baseline flights."""
        dfs = []
        for f in healthy_feature_files:
            df = pd.read_csv(f)
            if 'operating_regime' in df.columns:
                active_df = df[df['operating_regime'].isin(['CLIMB', 'CRUISE', 'DESCENT'])].copy()
            else:
                active_df = df[(df['rpm'] > 1200) & (df['map_kpa'] > 40.0)].copy()
            dfs.append(active_df)
            
        train_df = pd.concat(dfs, ignore_index=True)
        # Select available columns
        self.actual_cols = [c for c in self.feature_cols if c in train_df.columns]
        X = train_df[self.actual_cols].values
        
        X_scaled = self.scaler.fit_transform(X)
        self.iso_forest.fit(X_scaled)
        self.is_fitted = True
        
        # Calculate baseline anomaly score distribution
        raw_scores = -self.iso_forest.score_samples(X_scaled)
        self.score_min = np.percentile(raw_scores, 1)
        self.score_max = np.percentile(raw_scores, 99)
        print(f"Fitted Anomaly Detector on {len(train_df):,} healthy telemetry samples across {len(self.actual_cols)} features.")
        return self
        
    def predict_anomaly_score(self, df):
        """
        Computes normalized Anomaly Score A(t) in [0.0, 1.0] and Health Index H(t) in [0.0, 1.0].
        """
        if not self.is_fitted:
            raise ValueError("Anomaly detector is not fitted yet.")
            
        X = df[self.actual_cols].values
        X_scaled = self.scaler.transform(X)
        
        raw_scores = -self.iso_forest.score_samples(X_scaled)
        
        # Normalize into [0.0, 1.0]
        norm_scores = (raw_scores - self.score_min) / (self.score_max - self.score_min + 1e-6)
        anomaly_scores = np.clip(norm_scores, 0.0, 1.0)
        
        # Smooth with 5-second moving average to eliminate single-second transient spikes
        smoothed_scores = pd.Series(anomaly_scores).rolling(5, min_periods=1, center=True).mean().values
        health_index = np.clip(1.0 - smoothed_scores, 0.0, 1.0)
        
        is_anomaly = (smoothed_scores > self.healthy_threshold).astype(int)
        return smoothed_scores, health_index, is_anomaly

def train_and_save_anomaly_model(model_dir="data/models"):
    os.makedirs(model_dir, exist_ok=True)
    
    # Load all healthy feature files
    healthy_files = sorted(glob.glob("data/processed/features/*_features.csv"))
    if not healthy_files:
        print("Error: No feature files found in data/processed/features/")
        return None
        
    detector = DigitalTwinAnomalyDetector()
    detector.fit_healthy_baseline(healthy_files)
    
    model_path = os.path.join(model_dir, "anomaly_detector.pkl")
    with open(model_path, "wb") as fp:
        pickle.dump(detector, fp)
    print(f"Saved fitted Anomaly Detector model to {model_path}")
    return detector

if __name__ == "__main__":
    train_and_save_anomaly_model()
