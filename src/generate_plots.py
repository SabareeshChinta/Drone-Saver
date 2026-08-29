"""
Drone Saver - Telemetry Visualization Suite
Generates high-resolution diagnostic engineering plots for all selected real flights.
Problem Statement: SIH26054 - DRDO
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate_flight_plots(output_dir="reports/plots"):
    os.makedirs(output_dir, exist_ok=True)
    files = sorted(glob.glob("data/processed/canonical/*_canonical.csv"))
    
    # Configure plotting style
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
    plt.rcParams['axes.edgecolor'] = '#333333'
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['grid.color'] = '#e0e0e0'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.7
    
    for f in files:
        df = pd.read_csv(f)
        fid = df['flight_id'].iloc[0]
        time_min = df['time_seconds'] / 60.0
        
        print(f"Generating diagnostic plots for {fid}...")
        
        # -------------------------------------------------------------
        # PLOT 1: Comprehensive Multi-Panel Time-Series Telemetry
        # -------------------------------------------------------------
        fig, axes = plt.subplots(4, 2, figsize=(16, 12), sharex=True)
        fig.suptitle(f"Drone Saver — Real Aero-Piston Telemetry Overview: {fid}", fontsize=15, fontweight='bold', y=0.98)
        
        # 1. Engine RPM
        axes[0, 0].plot(time_min, df['rpm'], color='#1f77b4', lw=1.5, label='Crankshaft RPM')
        axes[0, 0].set_ylabel('Engine RPM')
        axes[0, 0].grid(True)
        axes[0, 0].legend(loc='upper right')
        
        # 2. Manifold Absolute Pressure (MAP)
        axes[0, 1].plot(time_min, df['map_kpa'], color='#ff7f0e', lw=1.5, label='Manifold Press (kPa)')
        axes[0, 1].set_ylabel('MAP (kPa)')
        axes[0, 1].grid(True)
        axes[0, 1].legend(loc='upper right')
        
        # 3. Fuel Flow
        axes[1, 0].plot(time_min, df['fuel_flow_lph'], color='#2ca02c', lw=1.5, label='Fuel Flow (L/h)')
        axes[1, 0].set_ylabel('Fuel Flow (L/h)')
        axes[1, 0].grid(True)
        axes[1, 0].legend(loc='upper right')
        
        # 4. Oil Temperature & Pressure
        ax_oil_p = axes[1, 1]
        ax_oil_t = ax_oil_p.twinx()
        l1 = ax_oil_p.plot(time_min, df['oil_pressure_kpa'], color='#d62728', lw=1.2, label='Oil Pressure (kPa)')
        l2 = ax_oil_t.plot(time_min, df['oil_temp_c'], color='#9467bd', lw=1.2, linestyle='--', label='Oil Temp (°C)')
        ax_oil_p.set_ylabel('Oil Press (kPa)', color='#d62728')
        ax_oil_t.set_ylabel('Oil Temp (°C)', color='#9467bd')
        ax_oil_p.grid(True)
        
        # 5. Cylinder Head Temperatures (CHT 1-4)
        colors_cyl = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
        for i in range(1, 5):
            col_name = f'cht_{i}_c'
            if col_name in df.columns and not df[col_name].isnull().all():
                axes[2, 0].plot(time_min, df[col_name], color=colors_cyl[i-1], lw=1.2, label=f'CHT {i}')
        axes[2, 0].set_ylabel('CHT (°C)')
        axes[2, 0].grid(True)
        axes[2, 0].legend(loc='upper right', ncol=2)
        
        # 6. Exhaust Gas Temperatures (EGT 1-4)
        for i in range(1, 5):
            col_name = f'egt_{i}_c'
            if col_name in df.columns and not df[col_name].isnull().all():
                axes[2, 1].plot(time_min, df[col_name], color=colors_cyl[i-1], lw=1.2, label=f'EGT {i}')
        axes[2, 1].set_ylabel('EGT (°C)')
        axes[2, 1].grid(True)
        axes[2, 1].legend(loc='upper right', ncol=2)
        
        # 7. Altitude MSL
        axes[3, 0].plot(time_min, df['altitude_m'], color='#8c564b', lw=1.5, label='Altitude MSL (m)')
        axes[3, 0].set_ylabel('Altitude (m)')
        axes[3, 0].set_xlabel('Flight Elapsed Time (Minutes)')
        axes[3, 0].grid(True)
        axes[3, 0].legend(loc='upper right')
        
        # 8. Indicated Airspeed (IAS)
        axes[3, 1].plot(time_min, df['airspeed_mps'], color='#e377c2', lw=1.5, label='Airspeed (m/s)')
        axes[3, 1].set_ylabel('IAS (m/s)')
        axes[3, 1].set_xlabel('Flight Elapsed Time (Minutes)')
        axes[3, 1].grid(True)
        axes[3, 1].legend(loc='upper right')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        plot_path1 = os.path.join(output_dir, f"{fid.lower()}_timeseries_telemetry.png")
        plt.savefig(plot_path1, dpi=180)
        plt.close()
        
        # -------------------------------------------------------------
        # PLOT 2: Cross-Sensor Thermal & Operational Relationships
        # -------------------------------------------------------------
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle(f"Drone Saver — Thermal & Physical State Relationships: {fid}", fontsize=15, fontweight='bold', y=0.98)
        
        # A. RPM vs EGT1
        axes[0, 0].scatter(df['rpm'], df['egt_1_c'], c=df['altitude_m'], cmap='viridis', s=4, alpha=0.6)
        axes[0, 0].set_xlabel('Engine RPM')
        axes[0, 0].set_ylabel('EGT 1 (°C)')
        axes[0, 0].set_title('RPM vs EGT 1 (colored by Altitude)')
        axes[0, 0].grid(True)
        
        # B. RPM vs CHT1
        axes[0, 1].scatter(df['rpm'], df['cht_1_c'], c=df['airspeed_mps'], cmap='plasma', s=4, alpha=0.6)
        axes[0, 1].set_xlabel('Engine RPM')
        axes[0, 1].set_ylabel('CHT 1 (°C)')
        axes[0, 1].set_title('RPM vs CHT 1 (colored by Airspeed)')
        axes[0, 1].grid(True)
        
        # C. EGT1 vs CHT1
        axes[0, 2].scatter(df['egt_1_c'], df['cht_1_c'], c=df['fuel_flow_lph'], cmap='coolwarm', s=4, alpha=0.6)
        axes[0, 2].set_xlabel('EGT 1 (°C)')
        axes[0, 2].set_ylabel('CHT 1 (°C)')
        axes[0, 2].set_title('EGT 1 vs CHT 1 (colored by Fuel Flow)')
        axes[0, 2].grid(True)
        
        # D. MAP vs EGT1
        axes[1, 0].scatter(df['map_kpa'], df['egt_1_c'], c=df['rpm'], cmap='magma', s=4, alpha=0.6)
        axes[1, 0].set_xlabel('Manifold Pressure MAP (kPa)')
        axes[1, 0].set_ylabel('EGT 1 (°C)')
        axes[1, 0].set_title('MAP vs EGT 1 (colored by RPM)')
        axes[1, 0].grid(True)
        
        # E. Ambient Temp vs CHT1
        axes[1, 1].scatter(df['ambient_temp_c'], df['cht_1_c'], c=df['map_kpa'], cmap='cividis', s=4, alpha=0.6)
        axes[1, 1].set_xlabel('Ambient Temp OAT (°C)')
        axes[1, 1].set_ylabel('CHT 1 (°C)')
        axes[1, 1].set_title('OAT vs CHT 1 (colored by MAP)')
        axes[1, 1].grid(True)
        
        # F. Multi-Cylinder EGT Cross-Spread
        axes[1, 2].scatter(df['egt_1_c'], df['egt_2_c'], label='EGT 2 vs 1', s=3, alpha=0.5, color='#377eb8')
        axes[1, 2].scatter(df['egt_1_c'], df['egt_3_c'], label='EGT 3 vs 1', s=3, alpha=0.5, color='#4daf4a')
        axes[1, 2].scatter(df['egt_1_c'], df['egt_4_c'], label='EGT 4 vs 1', s=3, alpha=0.5, color='#984ea3')
        lims = [axes[1, 2].get_xlim()[0], axes[1, 2].get_xlim()[1]]
        axes[1, 2].plot(lims, lims, 'k--', alpha=0.7, label='1:1 Line')
        axes[1, 2].set_xlabel('Cylinder 1 EGT (°C)')
        axes[1, 2].set_ylabel('Cylinder i EGT (°C)')
        axes[1, 2].set_title('Cross-Cylinder EGT Linearity & Balance')
        axes[1, 2].grid(True)
        axes[1, 2].legend(loc='upper left')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        plot_path2 = os.path.join(output_dir, f"{fid.lower()}_thermal_relationships.png")
        plt.savefig(plot_path2, dpi=180)
        plt.close()
        
    print(f"Generated all diagnostic plots in {output_dir}/")

if __name__ == "__main__":
    generate_flight_plots()
