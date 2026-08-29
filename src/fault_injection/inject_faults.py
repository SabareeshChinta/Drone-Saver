"""
Drone Saver - Physics-Informed Fault Injection Engine
Implements mathematically rigorous, literature-backed aero-piston failure modes:
- FT-01: Spark Plug Fouling / Single Magneto Drop
- FT-02: Fuel Injector Clogging / Lean Shift (with lean misfire quench)
- FT-03: Burnt / Leaking Exhaust Valve (with valve rotation oscillation)
- FT-04: Destructive Detonation / Knock (boundary layer breakdown)
- FT-05: Cooling Baffle Degradation (rear cylinder airflow starvation)
- FT-06: Lubrication Degradation / Oil Pressure Loss
- FT-07: Intake Manifold Runner Leak
- FT-08: Thermocouple Sensor Drift
- FT-09: Sensor Open-Circuit Dropout

Problem Statement: SIH26054 - DRDO
"""

import os
import glob
import pandas as pd
import numpy as np

class PhysicsFaultInjector:
    def __init__(self, healthy_df):
        self.df = healthy_df.copy()
        self.n = len(self.df)
        self.dt = 1.0  # 1 Hz sampling
        self.t = self.df['time_seconds'].values
        
    def inject_spark_plug_fouling(self, target_cyl=1, onset_sec=1200, severity=1.0, tau_egt=4.0, tau_cht=45.0):
        """
        FT-01: Spark Plug Fouling / Ignition Failure
        Flame front speed is halved -> peak pressure shifts later into expansion stroke.
        EGT rises (+25 to +45 °C), CHT drops (-10 to -18 °C), RPM drops (-20 to -40 RPM).
        """
        df_mod = self.df.copy()
        mask = self.t >= onset_sec
        t_rel = np.maximum(0.0, self.t - onset_sec)
        
        # Exponential response curves
        resp_egt = (1.0 - np.exp(-t_rel / tau_egt)) * mask
        resp_cht = (1.0 - np.exp(-t_rel / tau_cht)) * mask
        
        delta_egt = severity * (32.0 + 10.0 * (df_mod['rpm'].values / 2500.0)) * resp_egt
        delta_cht = -severity * (14.0 + 5.0 * (df_mod['map_kpa'].values / 85.0)) * resp_cht
        delta_rpm = -severity * 28.0 * resp_egt
        
        egt_col = f'egt_{target_cyl}_c'
        cht_col = f'cht_{target_cyl}_c'
        
        df_mod[egt_col] += delta_egt
        df_mod[cht_col] += delta_cht
        df_mod['rpm'] = np.maximum(0.0, df_mod['rpm'] + delta_rpm)
        
        # Ground truth labels
        df_mod['fault_active'] = mask.astype(int)
        df_mod['fault_type'] = np.where(mask, 'FT-01_SPARK_PLUG_FOULING', 'HEALTHY')
        df_mod['fault_cylinder'] = np.where(mask, target_cyl, 0)
        df_mod['fault_severity'] = np.where(mask, severity, 0.0)
        
        # RUL: Estimated time until thermal limit or severe power loss (seconds from onset)
        time_to_fail = 1800.0 / max(0.1, severity)
        rul = np.where(mask, np.maximum(0.0, time_to_fail - t_rel), 99999.0)
        df_mod['ground_truth_rul_sec'] = rul
        
        return df_mod

    def inject_injector_clogging(self, target_cyl=2, onset_sec=1000, max_blockage=0.35, ramp_duration=1200.0):
        """
        FT-02: Fuel Injector Clogging / Lean Imbalance
        Nozzle blockage reduces fuel delivery. In ROP, mixture leans toward stoichiometric -> EGT/CHT rise.
        If blockage exceeds 20%, lean misfire causes sudden EGT quenching.
        """
        df_mod = self.df.copy()
        mask = self.t >= onset_sec
        t_rel = np.maximum(0.0, self.t - onset_sec)
        
        # Progressive ramp blockage kappa(t)
        progress = np.minimum(1.0, t_rel / ramp_duration) * mask
        kappa = max_blockage * progress
        
        egt_col = f'egt_{target_cyl}_c'
        cht_col = f'cht_{target_cyl}_c'
        
        # Thermodynamic delta calculation
        delta_egt = np.zeros(self.n)
        delta_cht = np.zeros(self.n)
        
        for i in range(self.n):
            k = kappa[i]
            if k <= 0.20:
                delta_egt[i] = +75.0 * (k / 0.20)
                delta_cht[i] = +22.0 * (k / 0.20)
            else:
                # Severe lean misfire quenching
                excess = (k - 0.20) / 0.15
                delta_egt[i] = +75.0 - 220.0 * excess
                delta_cht[i] = +22.0 - 15.0 * excess
                
        df_mod[egt_col] += delta_egt
        df_mod[cht_col] += delta_cht
        df_mod['fuel_flow_lph'] = np.maximum(5.0, df_mod['fuel_flow_lph'] - (kappa * 0.25 * df_mod['fuel_flow_lph']))
        
        df_mod['fault_active'] = mask.astype(int)
        df_mod['fault_type'] = np.where(mask, 'FT-02_INJECTOR_CLOGGING', 'HEALTHY')
        df_mod['fault_cylinder'] = np.where(mask, target_cyl, 0)
        df_mod['fault_severity'] = kappa
        
        time_to_misfire = ramp_duration * (0.25 / max(0.01, max_blockage))
        rul = np.where(mask, np.maximum(0.0, time_to_misfire - t_rel), 99999.0)
        df_mod['ground_truth_rul_sec'] = rul
        
        return df_mod

    def inject_burnt_exhaust_valve(self, target_cyl=3, onset_sec=800, severity=0.8, rot_freq=0.07):
        """
        FT-03: Burnt / Leaking Exhaust Valve
        Combustion gas leaks past valve seat during combustion.
        Produces rhythmic sinusoidal oscillation (+-15 °C @ 0.05-0.10 Hz) superposed on elevated EGT (+30 °C).
        """
        df_mod = self.df.copy()
        mask = self.t >= onset_sec
        t_rel = np.maximum(0.0, self.t - onset_sec)
        
        resp = (1.0 - np.exp(-t_rel / 30.0)) * mask
        oscillation = np.sin(2.0 * np.pi * rot_freq * self.t)
        delta_egt = severity * (30.0 + 16.0 * oscillation) * resp
        
        egt_col = f'egt_{target_cyl}_c'
        df_mod[egt_col] += delta_egt
        
        df_mod['fault_active'] = mask.astype(int)
        df_mod['fault_type'] = np.where(mask, 'FT-03_BURNT_EXHAUST_VALVE', 'HEALTHY')
        df_mod['fault_cylinder'] = np.where(mask, target_cyl, 0)
        df_mod['fault_severity'] = np.where(mask, severity, 0.0)
        
        time_to_catastrophic = 2400.0 / max(0.1, severity)
        rul = np.where(mask, np.maximum(0.0, time_to_catastrophic - t_rel), 99999.0)
        df_mod['ground_truth_rul_sec'] = rul
        
        return df_mod

    def inject_detonation(self, target_cyl=1, onset_sec=1500, severity=1.0, tau_det=12.0):
        """
        FT-04: Destructive Detonation (Knock)
        Shockwaves scour thermal boundary layer on combustion chamber walls.
        Rapid CHT thermal surge (+40 to +80 °C), while EGT drops (-20 to -40 °C).
        """
        df_mod = self.df.copy()
        mask = self.t >= onset_sec
        t_rel = np.maximum(0.0, self.t - onset_sec)
        
        resp = (1.0 - np.exp(-t_rel / tau_det)) * mask
        delta_cht = severity * (55.0 + 25.0 * (df_mod['map_kpa'].values / 85.0)) * resp
        delta_egt = -severity * 32.0 * resp
        
        egt_col = f'egt_{target_cyl}_c'
        cht_col = f'cht_{target_cyl}_c'
        
        df_mod[cht_col] += delta_cht
        df_mod[egt_col] += delta_egt
        
        df_mod['fault_active'] = mask.astype(int)
        df_mod['fault_type'] = np.where(mask, 'FT-04_DETONATION', 'HEALTHY')
        df_mod['fault_cylinder'] = np.where(mask, target_cyl, 0)
        df_mod['fault_severity'] = np.where(mask, severity, 0.0)
        
        # Detonation causes rapid cylinder thermal destruction (< 600s)
        time_to_burnout = 450.0 / max(0.1, severity)
        rul = np.where(mask, np.maximum(0.0, time_to_burnout - t_rel), 99999.0)
        df_mod['ground_truth_rul_sec'] = rul
        
        return df_mod

    def inject_cooling_baffle_degradation(self, target_cyl=4, onset_sec=900, severity=0.85):
        """
        FT-05: Cooling Baffle Degradation
        Baffle deterioration starves rear cylinder (#4) of cooling air.
        CHT increases (+35 °C) proportional to power and inversely to airspeed. EGT unaffected.
        """
        df_mod = self.df.copy()
        mask = self.t >= onset_sec
        t_rel = np.maximum(0.0, self.t - onset_sec)
        
        resp = (1.0 - np.exp(-t_rel / 60.0)) * mask
        pwr_factor = (df_mod['map_kpa'].values / 80.0) * (df_mod['rpm'].values / 2400.0)
        cooling_factor = np.maximum(0.5, df_mod['airspeed_mps'].values / 45.0)
        
        delta_cht = severity * (38.0 * pwr_factor / cooling_factor) * resp
        
        cht_col = f'cht_{target_cyl}_c'
        df_mod[cht_col] += delta_cht
        
        df_mod['fault_active'] = mask.astype(int)
        df_mod['fault_type'] = np.where(mask, 'FT-05_COOLING_BAFFLE_DEGRADATION', 'HEALTHY')
        df_mod['fault_cylinder'] = np.where(mask, target_cyl, 0)
        df_mod['fault_severity'] = np.where(mask, severity, 0.0)
        
        time_to_overheat = 2000.0 / max(0.1, severity)
        rul = np.where(mask, np.maximum(0.0, time_to_overheat - t_rel), 99999.0)
        df_mod['ground_truth_rul_sec'] = rul
        
        return df_mod

    def inject_lubrication_loss(self, onset_sec=1100, severity=0.6):
        """
        FT-06: Lubrication Degradation / Oil Pressure Loss
        Oil pressure drops (-40%), oil temperature rises (+25 °C), slight CHT increase.
        """
        df_mod = self.df.copy()
        mask = self.t >= onset_sec
        t_rel = np.maximum(0.0, self.t - onset_sec)
        
        resp_p = (1.0 - np.exp(-t_rel / 10.0)) * mask
        resp_t = (1.0 - np.exp(-t_rel / 80.0)) * mask
        
        df_mod['oil_pressure_kpa'] = np.maximum(30.0, df_mod['oil_pressure_kpa'] - severity * df_mod['oil_pressure_kpa'] * resp_p)
        df_mod['oil_temp_c'] += severity * 35.0 * resp_t
        for i in range(1, 5):
            df_mod[f'cht_{i}_c'] += severity * 8.0 * resp_t
            
        df_mod['fault_active'] = mask.astype(int)
        df_mod['fault_type'] = np.where(mask, 'FT-06_LUBRICATION_LOSS', 'HEALTHY')
        df_mod['fault_cylinder'] = 0  # Global engine fault
        df_mod['fault_severity'] = np.where(mask, severity, 0.0)
        
        time_to_seizure = 800.0 / max(0.1, severity)
        rul = np.where(mask, np.maximum(0.0, time_to_seizure - t_rel), 99999.0)
        df_mod['ground_truth_rul_sec'] = rul
        
        return df_mod

    def inject_intake_manifold_leak(self, target_cyl=2, onset_sec=1300, severity=0.7):
        """
        FT-07: Intake Manifold Runner Leak
        Unmetered air leaks into runner: MAP rises at low throttle/idle; affected cylinder runs lean at idle.
        """
        df_mod = self.df.copy()
        mask = self.t >= onset_sec
        t_rel = np.maximum(0.0, self.t - onset_sec)
        
        resp = (1.0 - np.exp(-t_rel / 15.0)) * mask
        idle_factor = np.maximum(0.0, 1.0 - df_mod['map_kpa'].values / 90.0)
        
        delta_map = severity * 12.0 * idle_factor * resp
        delta_egt = severity * 35.0 * idle_factor * resp
        
        df_mod['map_kpa'] += delta_map
        df_mod[f'egt_{target_cyl}_c'] += delta_egt
        
        df_mod['fault_active'] = mask.astype(int)
        df_mod['fault_type'] = np.where(mask, 'FT-07_INTAKE_MANIFOLD_LEAK', 'HEALTHY')
        df_mod['fault_cylinder'] = np.where(mask, target_cyl, 0)
        df_mod['fault_severity'] = np.where(mask, severity, 0.0)
        
        rul = np.where(mask, np.maximum(0.0, 3600.0 - t_rel), 99999.0)
        df_mod['ground_truth_rul_sec'] = rul
        
        return df_mod

    def inject_sensor_drift(self, target_cyl=3, sensor_type='egt', onset_sec=700, drift_rate=0.02):
        """
        FT-08: Thermocouple Sensor Drift
        Continuous linear sensor offset drift (+0.02 °C/s) due to probe metallurgical degradation.
        """
        df_mod = self.df.copy()
        mask = self.t >= onset_sec
        t_rel = np.maximum(0.0, self.t - onset_sec)
        
        drift = drift_rate * t_rel * mask
        col = f'{sensor_type}_{target_cyl}_c'
        df_mod[col] += drift
        
        df_mod['fault_active'] = mask.astype(int)
        df_mod['fault_type'] = np.where(mask, 'FT-08_SENSOR_DRIFT', 'HEALTHY')
        df_mod['fault_cylinder'] = np.where(mask, target_cyl, 0)
        df_mod['fault_severity'] = np.where(mask, np.minimum(1.0, drift / 50.0), 0.0)
        
        rul = np.where(mask, np.maximum(0.0, 3000.0 - t_rel), 99999.0)
        df_mod['ground_truth_rul_sec'] = rul
        
        return df_mod

    def inject_sensor_dropout(self, target_cyl=1, sensor_type='cht', onset_sec=1600):
        """
        FT-09: Sensor Open-Circuit Dropout
        Instantaneous drop to 0.0 °C due to wire disconnect or probe burnout.
        """
        df_mod = self.df.copy()
        mask = self.t >= onset_sec
        
        col = f'{sensor_type}_{target_cyl}_c'
        df_mod.loc[mask, col] = 0.0
        
        df_mod['fault_active'] = mask.astype(int)
        df_mod['fault_type'] = np.where(mask, 'FT-09_SENSOR_DROPOUT', 'HEALTHY')
        df_mod['fault_cylinder'] = np.where(mask, target_cyl, 0)
        df_mod['fault_severity'] = np.where(mask, 1.0, 0.0)
        
        rul = np.where(mask, 0.0, 99999.0)
        df_mod['ground_truth_rul_sec'] = rul
        
        return df_mod


def generate_fault_dataset_batch():
    healthy_files = sorted(glob.glob("data/processed/flights_healthy/*_healthy.csv"))
    if not healthy_files:
        print("Error: No healthy baseline files found.")
        return
        
    categories = {
        'ignition': 'data/injected/ignition',
        'injector': 'data/injected/injector',
        'valve': 'data/injected/valve',
        'thermal': 'data/injected/thermal',
        'lubrication': 'data/injected/lubrication',
        'sensor': 'data/injected/sensor'
    }
    for cat_dir in categories.values():
        os.makedirs(cat_dir, exist_ok=True)
        
    manifest_rows = []
    
    for h_path in healthy_files:
        df_h = pd.read_csv(h_path)
        fid = df_h['flight_id'].iloc[0]
        base_name = os.path.basename(h_path).replace('_healthy.csv', '')
        injector = PhysicsFaultInjector(df_h)
        
        # 1. Spark Plug Fouling on Cyl 1 and Cyl 3
        df_f1 = injector.inject_spark_plug_fouling(target_cyl=1, onset_sec=1200, severity=0.9)
        f1_path = f"data/injected/ignition/{base_name}_ft01_spark_cyl1.csv"
        df_f1.to_csv(f1_path, index=False)
        manifest_rows.append({'flight_id': fid, 'fault_id': 'FT-01', 'fault_name': 'Spark Plug Fouling', 'cylinder': 1, 'path': f1_path, 'rows': len(df_f1)})
        
        # 2. Fuel Injector Clogging on Cyl 2
        df_f2 = injector.inject_injector_clogging(target_cyl=2, onset_sec=1000, max_blockage=0.35)
        f2_path = f"data/injected/injector/{base_name}_ft02_injector_cyl2.csv"
        df_f2.to_csv(f2_path, index=False)
        manifest_rows.append({'flight_id': fid, 'fault_id': 'FT-02', 'fault_name': 'Fuel Injector Clogging', 'cylinder': 2, 'path': f2_path, 'rows': len(df_f2)})
        
        # 3. Burnt Exhaust Valve on Cyl 3
        df_f3 = injector.inject_burnt_exhaust_valve(target_cyl=3, onset_sec=800, severity=0.85)
        f3_path = f"data/injected/valve/{base_name}_ft03_valve_cyl3.csv"
        df_f3.to_csv(f3_path, index=False)
        manifest_rows.append({'flight_id': fid, 'fault_id': 'FT-03', 'fault_name': 'Burnt Exhaust Valve', 'cylinder': 3, 'path': f3_path, 'rows': len(df_f3)})
        
        # 4. Detonation on Cyl 1
        df_f4 = injector.inject_detonation(target_cyl=1, onset_sec=1400, severity=1.0)
        f4_path = f"data/injected/thermal/{base_name}_ft04_detonation_cyl1.csv"
        df_f4.to_csv(f4_path, index=False)
        manifest_rows.append({'flight_id': fid, 'fault_id': 'FT-04', 'fault_name': 'Detonation (Knock)', 'cylinder': 1, 'path': f4_path, 'rows': len(df_f4)})
        
        # 5. Cooling Baffle Degradation on Cyl 4
        df_f5 = injector.inject_cooling_baffle_degradation(target_cyl=4, onset_sec=900, severity=0.9)
        f5_path = f"data/injected/thermal/{base_name}_ft05_baffle_cyl4.csv"
        df_f5.to_csv(f5_path, index=False)
        manifest_rows.append({'flight_id': fid, 'fault_id': 'FT-05', 'fault_name': 'Cooling Baffle Leak', 'cylinder': 4, 'path': f5_path, 'rows': len(df_f5)})
        
        # 6. Lubrication Loss
        df_f6 = injector.inject_lubrication_loss(onset_sec=1100, severity=0.6)
        f6_path = f"data/injected/lubrication/{base_name}_ft06_lubrication_loss.csv"
        df_f6.to_csv(f6_path, index=False)
        manifest_rows.append({'flight_id': fid, 'fault_id': 'FT-06', 'fault_name': 'Lubrication Loss', 'cylinder': 0, 'path': f6_path, 'rows': len(df_f6)})
        
        # 7. Intake Manifold Leak on Cyl 2
        df_f7 = injector.inject_intake_manifold_leak(target_cyl=2, onset_sec=1300, severity=0.75)
        f7_path = f"data/injected/valve/{base_name}_ft07_intake_leak_cyl2.csv"
        df_f7.to_csv(f7_path, index=False)
        manifest_rows.append({'flight_id': fid, 'fault_id': 'FT-07', 'fault_name': 'Intake Manifold Leak', 'cylinder': 2, 'path': f7_path, 'rows': len(df_f7)})
        
        # 8. Sensor Drift on Cyl 3 EGT
        df_f8 = injector.inject_sensor_drift(target_cyl=3, sensor_type='egt', onset_sec=700, drift_rate=0.025)
        f8_path = f"data/injected/sensor/{base_name}_ft08_sensor_drift_cyl3.csv"
        df_f8.to_csv(f8_path, index=False)
        manifest_rows.append({'flight_id': fid, 'fault_id': 'FT-08', 'fault_name': 'Thermocouple Drift', 'cylinder': 3, 'path': f8_path, 'rows': len(df_f8)})
        
        # 9. Sensor Dropout on Cyl 1 CHT
        df_f9 = injector.inject_sensor_dropout(target_cyl=1, sensor_type='cht', onset_sec=1600)
        f9_path = f"data/injected/sensor/{base_name}_ft09_dropout_cyl1.csv"
        df_f9.to_csv(f9_path, index=False)
        manifest_rows.append({'flight_id': fid, 'fault_id': 'FT-09', 'fault_name': 'Sensor Dropout', 'cylinder': 1, 'path': f9_path, 'rows': len(df_f9)})
        
    manifest_df = pd.DataFrame(manifest_rows)
    manifest_path = "data/metadata/injected_fault_manifest.csv"
    manifest_df.to_csv(manifest_path, index=False)
    print(f"Generated {len(manifest_df)} physics-injected fault datasets across 6 categories!")
    print(f"Manifest saved to {manifest_path}")

if __name__ == "__main__":
    generate_fault_dataset_batch()
