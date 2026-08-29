"""
Drone Saver - Physics Feature Extraction Engine
Extracts physically grounded multi-cylinder imbalance, rate-of-change, and residual features.
Problem Statement: SIH26054 - DRDO
"""

import os
import glob
import pandas as pd
import numpy as np

def extract_cylinder_features(input_file, output_dir="data/processed/features"):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(input_file)
    fid = df['flight_id'].iloc[0]
    
    feat_df = df.copy()
    
    # 1. Multi-Cylinder EGT Aggregates & Deviations
    egt_cols = [c for c in ['egt_1_c', 'egt_2_c', 'egt_3_c', 'egt_4_c'] if c in df.columns]
    cht_cols = [c for c in ['cht_1_c', 'cht_2_c', 'cht_3_c', 'cht_4_c'] if c in df.columns]
    
    feat_df['egt_mean_c'] = df[egt_cols].mean(axis=1)
    feat_df['egt_std_c'] = df[egt_cols].std(axis=1)
    feat_df['egt_max_c'] = df[egt_cols].max(axis=1)
    feat_df['egt_min_c'] = df[egt_cols].min(axis=1)
    feat_df['egt_spread_c'] = feat_df['egt_max_c'] - feat_df['egt_min_c']
    
    # Individual cylinder deviations from engine mean
    for i, col in enumerate(egt_cols, 1):
        feat_df[f'egt_dev_mean_cyl{i}_c'] = df[col] - feat_df['egt_mean_c']
        
    # 2. Multi-Cylinder CHT Aggregates & Deviations
    feat_df['cht_mean_c'] = df[cht_cols].mean(axis=1)
    feat_df['cht_std_c'] = df[cht_cols].std(axis=1)
    feat_df['cht_max_c'] = df[cht_cols].max(axis=1)
    feat_df['cht_min_c'] = df[cht_cols].min(axis=1)
    feat_df['cht_spread_c'] = feat_df['cht_max_c'] - feat_df['cht_min_c']
    
    for i, col in enumerate(cht_cols, 1):
        feat_df[f'cht_dev_mean_cyl{i}_c'] = df[col] - feat_df['cht_mean_c']
        
    # 3. Dynamic Thermal Rates of Change (First Derivatives with 3-second smoothing)
    dt = 1.0  # 1 Hz sampling
    for i, col in enumerate(egt_cols, 1):
        raw_diff = df[col].diff().fillna(0.0) / dt
        feat_df[f'degt_dt_cyl{i}_cps'] = raw_diff.rolling(3, min_periods=1, center=True).mean()
        
    for i, col in enumerate(cht_cols, 1):
        raw_diff = df[col].diff().fillna(0.0) / dt
        feat_df[f'dcht_dt_cyl{i}_cps'] = raw_diff.rolling(3, min_periods=1, center=True).mean()
        
    # 4. Lubrication Thermal & Hydraulic Rates
    feat_df['doil_temp_dt_cps'] = (df['oil_temp_c'].diff().fillna(0.0) / dt).rolling(5, min_periods=1, center=True).mean()
    feat_df['doil_press_dt_kpaps'] = (df['oil_pressure_kpa'].diff().fillna(0.0) / dt).rolling(5, min_periods=1, center=True).mean()
    
    # 5. Dimensionless Thermal-Hydraulic Health Indices
    # Lubrication Index: Oil Pressure to RPM ratio normalized by temperature
    rpm_safe = np.maximum(df['rpm'].values, 100.0)
    feat_df['oil_hydraulic_index'] = (df['oil_pressure_kpa'].values / rpm_safe) * np.exp(0.01 * df['oil_temp_c'].values)
    
    # Combustion Thermal Stress Ratio: (EGT_mean / CHT_mean)
    cht_safe = np.maximum(feat_df['cht_mean_c'].values, 10.0)
    feat_df['thermal_stress_ratio'] = feat_df['egt_mean_c'].values / cht_safe
    
    out_file = os.path.join(output_dir, f"{fid.lower()}_features.csv")
    feat_df.to_csv(out_file, index=False)
    print(f"[{fid}] Extracted {len(feat_df.columns)} total features ({len(feat_df)} rows) -> {out_file}")
    return feat_df

def extract_all_features():
    files = sorted(glob.glob("data/processed/canonical/*_baseline.csv"))
    for f in files:
        extract_cylinder_features(f)

if __name__ == "__main__":
    extract_all_features()
