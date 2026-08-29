"""
Drone Saver - Operating Regime Segmentation Engine
Segments continuous telemetry into physical operating regimes:
[STARTUP, TAXI, TAKEOFF, CLIMB, CRUISE, DESCENT, APPROACH_LANDING, IDLE]
Problem Statement: SIH26054 - DRDO
"""

import os
import glob
import pandas as pd
import numpy as np

def smooth_labels(labels, window_size=5):
    """Applies a sliding majority-vote window to smooth categorical regime transitions."""
    n = len(labels)
    half_w = window_size // 2
    smoothed = list(labels)
    for i in range(n):
        start = max(0, i - half_w)
        end = min(n, i + half_w + 1)
        sub = labels[start:end]
        # Find mode
        vals, counts = np.unique(sub, return_counts=True)
        smoothed[i] = vals[np.argmax(counts)]
    return smoothed

def segment_flight_regimes(flight_csv_path):
    df = pd.read_csv(flight_csv_path)
    fid = df['flight_id'].iloc[0]
    
    rpm = df['rpm'].values
    ias = df['airspeed_mps'].values
    vspd = df['vertical_speed_mps'].values
    alt = df['altitude_m'].values
    map_kpa = df['map_kpa'].values
    
    n = len(df)
    regimes = []
    
    # Ground elevation estimate (first 60s average)
    ground_alt = np.median(alt[:min(60, n)])
    
    flight_taken_off = False
    
    for i in range(n):
        r = rpm[i]
        v = ias[i]
        vz = vspd[i]
        h = alt[i]
        m = map_kpa[i]
        h_agl = max(0.0, h - ground_alt)
        
        # State machine logic
        if r < 600:
            reg = "STARTUP"
        elif v < 18.0 and h_agl < 25.0 and not flight_taken_off:
            reg = "TAXI"
        elif v >= 18.0 and vz > 1.5 and r > 2200 and h_agl < 300.0:
            reg = "TAKEOFF"
            flight_taken_off = True
        elif v >= 22.0 and vz > 0.8:
            reg = "CLIMB"
            flight_taken_off = True
        elif v >= 30.0 and abs(vz) <= 0.8 and h_agl > 300.0:
            reg = "CRUISE"
            flight_taken_off = True
        elif v >= 25.0 and vz < -0.8 and h_agl > 150.0:
            reg = "DESCENT"
        elif v >= 18.0 and h_agl <= 150.0 and flight_taken_off:
            reg = "APPROACH_LANDING"
        elif v < 18.0 and flight_taken_off and h_agl < 25.0:
            reg = "POST_FLIGHT_IDLE"
        elif r > 600 and v < 18.0:
            reg = "GROUND_IDLE"
        else:
            reg = "CRUISE" if h_agl > 300.0 else "MANEUVERING"
            
        regimes.append(reg)
        
    smoothed_regimes = smooth_labels(regimes, window_size=5)
    df['operating_regime'] = smoothed_regimes
    
    # Save regime-annotated canonical CSV
    regime_file = flight_csv_path.replace('_canonical.csv', '_regimes.csv')
    df.to_csv(regime_file, index=False)
    
    # Also update the canonical file with operating_regime column
    df.to_csv(flight_csv_path, index=False)
    
    # Compute regime summary breakdown
    regime_counts = df['operating_regime'].value_counts()
    print(f"\n=======================================================")
    print(f"REGIME SEGMENTATION: {fid}")
    print(f"=======================================================")
    for reg_name, count in regime_counts.items():
        pct = (count / n) * 100.0
        dur_min = count / 60.0
        print(f" - {reg_name:<18}: {count:>5} samples ({dur_min:>5.1f} min, {pct:>5.1f}%)")
        
    return df

def segment_all():
    files = sorted(glob.glob("data/processed/canonical/*_canonical.csv"))
    for f in files:
        segment_flight_regimes(f)

if __name__ == "__main__":
    segment_all()
