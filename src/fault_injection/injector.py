"""
Drone Saver - Master Fault Injector Engine
Executes parameter sweeps and generates labeled, provenance-tracked fault telemetry datasets.
Problem Statement: SIH26054 - DRDO
"""

import os
import sys
sys.path.insert(0, '.')
import glob
import pandas as pd
import numpy as np

from src.fault_injection.ignition import SparkPlugFoulingFault
from src.fault_injection.fuel import FuelInjectorDegradationFault
from src.fault_injection.valve import BurntExhaustValveFault
from src.fault_injection.thermal import CoolingDegradationFault
from src.fault_injection.lubrication import LubricationDegradationFault
from src.fault_injection.intake import IntakeManifoldLeakFault
from src.fault_injection.sensors import SensorDriftFault, SensorDropoutFault

def generate_all_fault_scenarios(input_dir="data/processed/flights_healthy", output_base="data/injected"):
    healthy_files = sorted(glob.glob(f"{input_dir}/*_healthy.csv"))
    if not healthy_files:
        print(f"Error: No healthy files found in {input_dir}")
        return
        
    models = {
        'FT-01': SparkPlugFoulingFault(),
        'FT-02': FuelInjectorDegradationFault(),
        'FT-03': BurntExhaustValveFault(),
        'FT-04': CoolingDegradationFault(),
        'FT-05': CoolingDegradationFault(),
        'FT-06': LubricationDegradationFault(),
        'FT-07': IntakeManifoldLeakFault(),
        'FT-08': SensorDriftFault(),
        'FT-09': SensorDropoutFault()
    }
    
    dir_map = {
        'FT-01': f'{output_base}/ignition',
        'FT-02': f'{output_base}/injector',
        'FT-03': f'{output_base}/valve',
        'FT-04': f'{output_base}/thermal',
        'FT-05': f'{output_base}/thermal',
        'FT-06': f'{output_base}/lubrication',
        'FT-07': f'{output_base}/valve',
        'FT-08': f'{output_base}/sensor',
        'FT-09': f'{output_base}/sensor'
    }
    for d in dir_map.values():
        os.makedirs(d, exist_ok=True)
        
    manifest = []
    
    for h_path in healthy_files:
        df_h = pd.read_csv(h_path)
        fid = df_h['flight_id'].iloc[0]
        base_name = os.path.basename(h_path).replace('_healthy.csv', '')
        
        # Scenario 1: FT-01 Spark Plug Fouling on Cyl 1 (Severity 0.9, onset 1200s)
        df_mod, meta = models['FT-01'].inject(df_h, severity=0.9, onset_time_sec=1200, affected_cylinder=1)
        p = f"{dir_map['FT-01']}/{base_name}_ft01_spark_cyl1.csv"
        df_mod.to_csv(p, index=False)
        manifest.append({**meta, 'file_path': p, 'rows': len(df_mod)})
        
        # Scenario 2: FT-02 Injector Clogging on Cyl 2 (Severity 0.35, onset 1000s)
        df_mod, meta = models['FT-02'].inject(df_h, severity=0.35, onset_time_sec=1000, duration_sec=1200, affected_cylinder=2)
        p = f"{dir_map['FT-02']}/{base_name}_ft02_injector_cyl2.csv"
        df_mod.to_csv(p, index=False)
        manifest.append({**meta, 'file_path': p, 'rows': len(df_mod)})
        
        # Scenario 3: FT-03 Burnt Valve on Cyl 3 (Severity 0.85, onset 800s)
        df_mod, meta = models['FT-03'].inject(df_h, severity=0.85, onset_time_sec=800, duration_sec=600, affected_cylinder=3)
        p = f"{dir_map['FT-03']}/{base_name}_ft03_valve_cyl3.csv"
        df_mod.to_csv(p, index=False)
        manifest.append({**meta, 'file_path': p, 'rows': len(df_mod)})
        
        # Scenario 4: FT-04 Detonation on Cyl 1 (Severity 1.0, onset 1400s)
        df_mod, meta = models['FT-04'].inject(df_h, severity=1.0, onset_time_sec=1400, affected_cylinder=1, mode='detonation')
        p = f"{dir_map['FT-04']}/{base_name}_ft04_detonation_cyl1.csv"
        df_mod.to_csv(p, index=False)
        manifest.append({**meta, 'file_path': p, 'rows': len(df_mod)})
        
        # Scenario 5: FT-05 Cooling Baffle on Cyl 4 (Severity 0.9, onset 900s)
        df_mod, meta = models['FT-05'].inject(df_h, severity=0.9, onset_time_sec=900, duration_sec=400, affected_cylinder=4, mode='baffle')
        p = f"{dir_map['FT-05']}/{base_name}_ft05_baffle_cyl4.csv"
        df_mod.to_csv(p, index=False)
        manifest.append({**meta, 'file_path': p, 'rows': len(df_mod)})
        
        # Scenario 6: FT-06 Lubrication Loss (Severity 0.6, onset 1100s)
        df_mod, meta = models['FT-06'].inject(df_h, severity=0.6, onset_time_sec=1100)
        p = f"{dir_map['FT-06']}/{base_name}_ft06_lubrication_loss.csv"
        df_mod.to_csv(p, index=False)
        manifest.append({**meta, 'file_path': p, 'rows': len(df_mod)})
        
        # Scenario 7: FT-07 Intake Manifold Leak on Cyl 2 (Severity 0.75, onset 1300s)
        df_mod, meta = models['FT-07'].inject(df_h, severity=0.75, onset_time_sec=1300, affected_cylinder=2)
        p = f"{dir_map['FT-07']}/{base_name}_ft07_intake_leak_cyl2.csv"
        df_mod.to_csv(p, index=False)
        manifest.append({**meta, 'file_path': p, 'rows': len(df_mod)})
        
        # Scenario 8: FT-08 Sensor Drift on Cyl 3 EGT (Severity 1.0, onset 700s)
        df_mod, meta = models['FT-08'].inject(df_h, severity=1.0, onset_time_sec=700, drift_rate=0.025, sensor_type='egt', affected_cylinder=3)
        p = f"{dir_map['FT-08']}/{base_name}_ft08_sensor_drift_cyl3.csv"
        df_mod.to_csv(p, index=False)
        manifest.append({**meta, 'file_path': p, 'rows': len(df_mod)})
        
        # Scenario 9: FT-09 Sensor Dropout on Cyl 1 CHT (Severity 1.0, onset 1600s)
        df_mod, meta = models['FT-09'].inject(df_h, severity=1.0, onset_time_sec=1600, sensor_type='cht', affected_cylinder=1)
        p = f"{dir_map['FT-09']}/{base_name}_ft09_dropout_cyl1.csv"
        df_mod.to_csv(p, index=False)
        manifest.append({**meta, 'file_path': p, 'rows': len(df_mod)})
        
    m_df = pd.DataFrame(manifest)
    m_path = "data/metadata/injected_fault_manifest.csv"
    m_df.to_csv(m_path, index=False)
    print(f"Generated {len(m_df)} physics-injected fault datasets -> {m_path}")
    return m_df

if __name__ == "__main__":
    generate_all_fault_scenarios()
