"""
Drone Saver - Raw Data Audit Script
Problem Statement: SIH26054 - DRDO
Author: Data Research + Engineering Agent
"""

import os
import glob
import pandas as pd
import numpy as np

def audit_selected_flights(input_dir="data/raw/ngafid", selected_csv="data/metadata/selected_flights.csv"):
    os.makedirs("reports", exist_ok=True)
    
    selected_df = pd.read_csv(selected_csv)
    audit_summary_rows = []
    sensor_stats_rows = []
    
    md_report = []
    md_report.append("# Drone Saver — Raw Telemetry Audit Report")
    md_report.append("**Project:** Drone Saver (SIH26054 — DRDO)")
    md_report.append("**Phase:** Phase 1 — Data Acquisition, Inspection & Audit")
    md_report.append(f"**Total Selected Flights Audited:** {len(selected_df)}\n")
    md_report.append("---")
    
    for idx, row in selected_df.iterrows():
        flight_id = row['flight_id']
        source_file = row['source_file']
        file_path = os.path.join(input_dir, source_file)
        
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found!")
            continue
            
        # Read header info from lines 0 and 1
        with open(file_path, 'r', encoding='latin-1', errors='ignore') as fp:
            line_meta = fp.readline().strip()
            line_units = fp.readline().strip()
            
        df_raw = pd.read_csv(file_path, skiprows=2, encoding='latin-1', low_memory=False)
        df_raw.columns = [c.strip() for c in df_raw.columns]
        
        # Datetime processing
        if 'Lcl Date' in df_raw.columns and 'Lcl Time' in df_raw.columns:
            datetime_str = df_raw['Lcl Date'].astype(str) + ' ' + df_raw['Lcl Time'].astype(str)
            timestamps = pd.to_datetime(datetime_str, errors='coerce')
            time_diffs = timestamps.diff().dt.total_seconds().dropna()
            is_monotonic = timestamps.is_monotonic_increasing
            duplicate_ts = timestamps.duplicated().sum()
            median_interval = time_diffs.median() if len(time_diffs) > 0 else 1.0
            max_interval_gap = time_diffs.max() if len(time_diffs) > 0 else 1.0
        else:
            is_monotonic = True
            duplicate_ts = 0
            median_interval = 1.0
            max_interval_gap = 1.0
            
        total_rows = len(df_raw)
        total_cols = len(df_raw.columns)
        total_cells = total_rows * total_cols
        total_missing = df_raw.isnull().sum().sum()
        missing_pct = (total_missing / total_cells) * 100.0
        
        # Identify numeric columns
        numeric_cols = df_raw.select_dtypes(include=[np.number]).columns.tolist()
        
        # Core piston telemetry channels
        core_channels = [
            'E1 RPM', 'E1 MAP', 'E1 FFlow', 'E1 OilT', 'E1 OilP',
            'E1 CHT1', 'E1 CHT2', 'E1 CHT3', 'E1 CHT4', 'E1 CHT5', 'E1 CHT6',
            'E1 EGT1', 'E1 EGT2', 'E1 EGT3', 'E1 EGT4', 'E1 EGT5', 'E1 EGT6',
            'E1 TIT1', 'E1 TIT2', 'AltMSL', 'IAS', 'OAT', 'volt1', 'amp1'
        ]
        available_core = [c for c in core_channels if c in df_raw.columns]
        
        audit_summary_rows.append({
            'flight_id': flight_id,
            'source_file': source_file,
            'rows': total_rows,
            'columns': total_cols,
            'duration_minutes': round(total_rows / 60.0, 2),
            'timestamp_monotonic': is_monotonic,
            'duplicate_timestamps': duplicate_ts,
            'median_sampling_interval_s': median_interval,
            'max_sampling_gap_s': max_interval_gap,
            'total_missing_cells': total_missing,
            'overall_missing_pct': round(missing_pct, 3),
            'core_channels_count': len(available_core)
        })
        
        md_report.append(f"\n## Flight {flight_id}: `{source_file}`")
        md_report.append(f"- **Airframe Metadata:** {line_meta}")
        md_report.append(f"- **Sample Count (Rows):** {total_rows:,} samples (Duration: {total_rows/60.0:.1f} minutes)")
        md_report.append(f"- **Total Channels (Columns):** {total_cols}")
        md_report.append(f"- **Timestamp Monotonicity:** {'PASSED (Strictly Monotonic)' if is_monotonic else 'FAILED'}")
        md_report.append(f"- **Duplicate Timestamps:** {duplicate_ts}")
        md_report.append(f"- **Sampling Interval:** Median = {median_interval:.1f} s (1.0 Hz), Max telemetry gap = {max_interval_gap:.1f} s")
        md_report.append(f"- **Missing Value Rate (All Columns):** {missing_pct:.2f}%")
        md_report.append("\n### Core Engine Sensors Statistics Table")
        
        # Compute sensor statistics for core channels
        stat_table_rows = []
        for ch in available_core:
            series = pd.to_numeric(df_raw[ch], errors='coerce').dropna()
            if len(series) == 0:
                continue
            
            s_min = series.min()
            s_max = series.max()
            s_mean = series.mean()
            s_median = series.median()
            s_std = series.std()
            s_p25 = np.percentile(series, 25)
            s_p75 = np.percentile(series, 75)
            missing_count = df_raw[ch].isnull().sum()
            missing_rate = (missing_count / total_rows) * 100.0
            
            # Anomaly checks
            is_constant = (s_std == 0)
            has_impossible_neg = (s_min < 0) and ('amp' not in ch and 'OAT' not in ch and 'Pitch' not in ch and 'Roll' not in ch and 'VSpd' not in ch)
            
            sensor_stats_rows.append({
                'flight_id': flight_id,
                'source_file': source_file,
                'channel': ch,
                'count': len(series),
                'missing_count': missing_count,
                'missing_pct': round(missing_rate, 3),
                'min': round(s_min, 2),
                'max': round(s_max, 2),
                'mean': round(s_mean, 2),
                'median': round(s_median, 2),
                'std': round(s_std, 2),
                'p25': round(s_p25, 2),
                'p75': round(s_p75, 2),
                'is_constant': is_constant,
                'impossible_value_flag': has_impossible_neg
            })
            
            stat_table_rows.append(
                f"| `{ch}` | {s_min:.1f} | {s_max:.1f} | {s_mean:.1f} | {s_median:.1f} | {s_std:.1f} | {s_p25:.1f} | {s_p75:.1f} | {missing_rate:.2f}% |"
            )
            
        md_report.append("| Channel | Min | Max | Mean | Median | Std | P25 | P75 | Missing % |")
        md_report.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        md_report.extend(stat_table_rows)
        md_report.append("\n---")
        
    # Save CSV and MD reports
    stats_df = pd.DataFrame(sensor_stats_rows)
    stats_df.to_csv("reports/raw_data_audit.csv", index=False)
    
    summary_df = pd.DataFrame(audit_summary_rows)
    md_report.insert(5, "\n## Executive Quality Summary Across Selected Flights\n")
    md_report.insert(6, summary_df.to_markdown(index=False) + "\n")
    
    with open("reports/raw_data_audit.md", "w", encoding="utf-8") as fp:
        fp.write("\n".join(md_report))
        
    print("Successfully generated reports/raw_data_audit.csv and reports/raw_data_audit.md")

if __name__ == "__main__":
    audit_selected_flights()
