"""
Drone Saver - FT-01: Ignition & Spark Plug Degradation Model
Physical Mechanism:
Fouling of one spark plug in a dual-ignition cylinder halves flame front velocity,
retarding the angle of peak cylinder pressure (theta_Pmax) later into the expansion stroke.
Effects:
- Exhaust Gas Temperature (EGT) rises (+20 to +45 °C) due to combustion continuing into exhaust runner
- Cylinder Head Temperature (CHT) drops (-8 to -18 °C) due to reduced peak compression heat transfer
- Slight brake power / RPM drop (-15 to -35 RPM)
- Increased cross-cylinder imbalance
Literature: Busch (2018), Miljkovic (2017) [10.23919/MIPRO.2017.7973581]
"""

import numpy as np
from src.fault_injection.base import BaseFaultModel
from src.fault_injection.profiles import exponential_lag_profile

class SparkPlugFoulingFault(BaseFaultModel):
    def __init__(self):
        super().__init__(fault_id="FT-01", fault_name="Spark Plug Fouling / Ignition Drop", default_target_cyl=1)
        
    def inject(self, data_df, severity=1.0, onset_time_sec=1200, duration_sec=None, affected_cylinder=None, seed=42):
        cyl = affected_cylinder if affected_cylinder is not None else self.default_target_cyl
        df = self._prepare_dataframe(data_df)
        t = df['time_seconds'].values
        n = len(df)
        
        # Thermal response time constants: EGT fast (tau ~ 4s), CHT slow thermal inertia (tau ~ 45s)
        resp_egt = exponential_lag_profile(t, onset_time_sec, time_constant_sec=4.0)
        resp_cht = exponential_lag_profile(t, onset_time_sec, time_constant_sec=45.0)
        
        # Directional scaling normalized by engine operating state
        # Higher RPM -> higher EGT elevation (flame has less crank angle time to burn)
        rpm_ratio = np.maximum(0.5, df['rpm'].values / 2400.0)
        map_ratio = np.maximum(0.5, df['map_kpa'].values / 85.0)
        
        delta_egt = severity * (28.0 + 12.0 * rpm_ratio) * resp_egt
        delta_cht = -severity * (12.0 + 5.0 * map_ratio) * resp_cht
        delta_rpm = -severity * (22.0 * map_ratio) * resp_egt
        
        egt_col = f'egt_{cyl}_c'
        cht_col = f'cht_{cyl}_c'
        
        if egt_col in df.columns:
            df[egt_col] += delta_egt
        if cht_col in df.columns:
            df[cht_col] += delta_cht
        df['rpm'] = np.maximum(0.0, df['rpm'] + delta_rpm)
        
        # Scenario RUL: Time until thermal degradation causes critical misfire
        critical_threshold = "EGT divergence > +45°C or RPM drop > 40"
        t_rel = np.maximum(0.0, t - onset_time_sec)
        mask = t >= onset_time_sec
        time_to_fail = 2400.0 / max(0.1, severity)
        scenario_rul = np.where(mask, np.maximum(0.0, time_to_fail - t_rel), 99999.0)
        
        df['fault_active'] = mask.astype(int)
        df['fault_id'] = np.where(mask, self.fault_id, 'NONE')
        df['fault_type'] = np.where(mask, 'FT-01_SPARK_PLUG_FOULING', 'HEALTHY')
        df['fault_cylinder'] = np.where(mask, cyl, 0)
        df['fault_severity'] = np.where(mask, severity, 0.0)
        df['scenario_rul_sec'] = scenario_rul
        
        metadata = {
            'fault_id': self.fault_id,
            'fault_name': self.fault_name,
            'severity': severity,
            'affected_cylinder': cyl,
            'onset_time_sec': onset_time_sec,
            'critical_threshold': critical_threshold,
            'source_flight_id': df['flight_id'].iloc[0],
            'random_seed': seed
        }
        return df, metadata
