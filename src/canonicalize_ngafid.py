"""
Drone Saver - Canonicalization Engine
Converts raw Garmin G1000/NGAFID telemetry into the Drone Saver Canonical Schema
Problem Statement: SIH26054 - DRDO
"""

import os
import glob
import pandas as pd
import numpy as np

def f_to_c(f_val):
    """Fahrenheit to Celsius conversion"""
    return (f_val - 32.0) / 1.8

def inhg_to_kpa(inhg_val):
    """Inches of Mercury to Kilopascals"""
    return inhg_val * 3.386389

def gph_to_lph(gph_val):
    """Gallons per hour to Litres per hour"""
    return gph_val * 3.785412

def psi_to_kpa(psi_val):
    """Pounds per square inch to Kilopascals"""
    return psi_val * 6.894757

def ft_to_m(ft_val):
    """Feet to Metres"""
    return ft_val * 0.3048

def kt_to_mps(kt_val):
    """Knots to Metres per second"""
    return kt_val * 0.514444

def fpm_to_mps(fpm_val):
    """Feet per minute to Metres per second"""
    return fpm_val * 0.00508

def gals_to_l(gals_val):
    """US Gallons to Litres"""
    return gals_val * 3.785412

def canonicalize_flight(raw_file_path, flight_id, output_dir="data/processed/canonical"):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("data/processed/flights_healthy", exist_ok=True)
    
    # Read raw Garmin G1000 file (skip lines 0 and 1)
    df_raw = pd.read_csv(raw_file_path, skiprows=2, encoding='latin-1', low_memory=False)
    df_raw.columns = [c.strip() for c in df_raw.columns]
    
    canon_df = pd.DataFrame()
    
    # 1. Identifiers & Time
    canon_df['flight_id'] = [str(flight_id)] * len(df_raw)
    canon_df['time_seconds'] = np.arange(len(df_raw), dtype=np.float64)
    
    if 'Lcl Date' in df_raw.columns and 'Lcl Time' in df_raw.columns:
        datetime_str = df_raw['Lcl Date'].astype(str).str.strip() + ' ' + df_raw['Lcl Time'].astype(str).str.strip()
        canon_df['timestamp'] = datetime_str
    elif 'Lcl Time' in df_raw.columns:
        canon_df['timestamp'] = df_raw['Lcl Time'].astype(str).str.strip()
    else:
        canon_df['timestamp'] = canon_df['time_seconds'].apply(lambda s: f"{int(s//3600):02d}:{int((s%3600)//60):02d}:{int(s%60):02d}")

    # Helper function to extract and convert numeric column
    def get_num(col_name, default=np.nan):
        if col_name in df_raw.columns:
            return pd.to_numeric(df_raw[col_name], errors='coerce')
        return pd.Series(default, index=df_raw.index, dtype=np.float64)

    # 2. Engine Core Telemetry
    canon_df['rpm'] = get_num('E1 RPM').fillna(0.0)
    canon_df['map_kpa'] = inhg_to_kpa(get_num('E1 MAP'))
    canon_df['fuel_flow_lph'] = gph_to_lph(get_num('E1 FFlow'))
    canon_df['oil_temp_c'] = f_to_c(get_num('E1 OilT'))
    canon_df['oil_pressure_kpa'] = psi_to_kpa(get_num('E1 OilP'))

    # 3. Cylinder Head Temperatures (CHT 1-4, optional 5-6)
    canon_df['cht_1_c'] = f_to_c(get_num('E1 CHT1'))
    canon_df['cht_2_c'] = f_to_c(get_num('E1 CHT2'))
    canon_df['cht_3_c'] = f_to_c(get_num('E1 CHT3'))
    canon_df['cht_4_c'] = f_to_c(get_num('E1 CHT4'))
    canon_df['cht_5_c'] = f_to_c(get_num('E1 CHT5'))
    canon_df['cht_6_c'] = f_to_c(get_num('E1 CHT6'))

    # 4. Exhaust Gas Temperatures (EGT 1-4, optional 5-6)
    canon_df['egt_1_c'] = f_to_c(get_num('E1 EGT1'))
    canon_df['egt_2_c'] = f_to_c(get_num('E1 EGT2'))
    canon_df['egt_3_c'] = f_to_c(get_num('E1 EGT3'))
    canon_df['egt_4_c'] = f_to_c(get_num('E1 EGT4'))
    canon_df['egt_5_c'] = f_to_c(get_num('E1 EGT5'))
    canon_df['egt_6_c'] = f_to_c(get_num('E1 EGT6'))

    # 5. Turbocharger Turbine Inlet Temperatures (TIT 1-2)
    canon_df['tit_1_c'] = f_to_c(get_num('E1 TIT1'))
    canon_df['tit_2_c'] = f_to_c(get_num('E1 TIT2'))

    # 6. Air Data & Environment
    canon_df['altitude_m'] = ft_to_m(get_num('AltMSL'))
    canon_df['airspeed_mps'] = kt_to_mps(get_num('IAS'))
    canon_df['vertical_speed_mps'] = fpm_to_mps(get_num('VSpd'))
    canon_df['ambient_temp_c'] = get_num('OAT')

    # 7. Electrical System
    canon_df['voltage_1'] = get_num('volt1')
    canon_df['voltage_2'] = get_num('volt2')
    canon_df['current_1'] = get_num('amp1')
    canon_df['current_2'] = get_num('amp2')

    # 8. Fuel & Attitude Dynamics
    canon_df['fuel_qty_l_litres'] = gals_to_l(get_num('FQtyL'))
    canon_df['fuel_qty_r_litres'] = gals_to_l(get_num('FQtyR'))
    canon_df['pitch_deg'] = get_num('Pitch')
    canon_df['roll_deg'] = get_num('Roll')

    # Linear interpolation for tiny single-second sensor gaps
    core_cols = [c for c in canon_df.columns if c not in ['flight_id', 'timestamp', 'time_seconds']]
    canon_df[core_cols] = canon_df[core_cols].interpolate(method='linear', limit=3).bfill().ffill()

    # Save canonical file
    out_file = os.path.join(output_dir, f"{flight_id.lower()}_canonical.csv")
    canon_df.to_csv(out_file, index=False)
    
    # Also save to healthy baseline pool
    healthy_file = os.path.join("data/processed/flights_healthy", f"{flight_id.lower()}_healthy.csv")
    canon_df.to_csv(healthy_file, index=False)
    
    print(f"[{flight_id}] Canonicalized {len(canon_df)} rows -> {out_file}")
    return canon_df

def canonicalize_all_selected():
    selected_csv = "data/metadata/selected_flights.csv"
    if not os.path.exists(selected_csv):
        print(f"Error: {selected_csv} not found")
        return
        
    df_sel = pd.read_csv(selected_csv)
    for _, row in df_sel.iterrows():
        fid = row['flight_id']
        fname = row['source_file']
        path = os.path.join("data/raw/ngafid", fname)
        if os.path.exists(path):
            canonicalize_flight(path, fid)
        else:
            print(f"Warning: {path} not found")

if __name__ == "__main__":
    canonicalize_all_selected()
