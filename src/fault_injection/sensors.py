"""
Drone Saver - Sensor Fault Models: FT-08 Sensor Drift & FT-09 Sensor Dropout
Physical Mechanisms:
1. Sensor Drift: Metallurgical degradation of thermocouple junction or cold junction drift.
   Produces a continuous linear offset: bias(t) = drift_rate * elapsed_time.
2. Sensor Dropout: Intermittent probe wire disconnect or ADC failure.
   Explicitly represents missingness (NaN) or electrical open-circuit (0.0 °C).
Literature: IEEE Trans. Instrumentation & Measurement (2021), NGAFID Data Quality Assessment
"""

import numpy as np
from src.fault_injection.base import BaseFaultModel

class SensorDriftFault(BaseFaultModel):
    def __init__(self):
        super().__init__(fault_id="FT-08", fault_name="Thermocouple Sensor Drift", default_target_cyl=3)
        
    def inject(self, data_df, severity=1.0, onset_time_sec=700, drift_rate=0.025, sensor_type='egt', affected_cylinder=3, seed=42):
        cyl = affected_cylinder
        df = self._prepare_dataframe(data_df)
        t = df['time_seconds'].values
        
        mask = t >= onset_time_sec
        t_rel = np.maximum(0.0, t - onset_time_sec)
        
        drift = severity * drift_rate * t_rel * mask
        col = f'{sensor_type}_{cyl}_c'
        if col in df.columns:
            df[col] += drift
            
        critical_threshold = "Sensor Offset > 50°C (False Diagnostic Trigger Limit)"
        time_to_crit = 50.0 / max(0.001, severity * drift_rate)
        scenario_rul = np.where(mask, np.maximum(0.0, time_to_crit - t_rel), 99999.0)
        
        df['fault_active'] = mask.astype(int)
        df['fault_id'] = np.where(mask, self.fault_id, 'NONE')
        df['fault_type'] = np.where(mask, 'FT-08_SENSOR_DRIFT', 'HEALTHY')
        df['fault_cylinder'] = np.where(mask, cyl, 0)
        df['fault_severity'] = np.where(mask, np.minimum(1.0, drift / 50.0), 0.0)
        df['scenario_rul_sec'] = scenario_rul
        
        metadata = {
            'fault_id': self.fault_id,
            'fault_name': self.fault_name,
            'sensor_channel': col,
            'drift_rate_cps': drift_rate,
            'severity': severity,
            'affected_cylinder': cyl,
            'onset_time_sec': onset_time_sec,
            'critical_threshold': critical_threshold,
            'source_flight_id': df['flight_id'].iloc[0],
            'random_seed': seed
        }
        return df, metadata

class SensorDropoutFault(BaseFaultModel):
    def __init__(self):
        super().__init__(fault_id="FT-09", fault_name="Sensor Open-Circuit Dropout", default_target_cyl=1)
        
    def inject(self, data_df, severity=1.0, onset_time_sec=1600, duration_sec=None, sensor_type='cht', affected_cylinder=1, seed=42):
        cyl = affected_cylinder
        df = self._prepare_dataframe(data_df)
        t = df['time_seconds'].values
        
        mask = t >= onset_time_sec
        col = f'{sensor_type}_{cyl}_c'
        
        if col in df.columns:
            # Set to 0.0 °C (thermocouple open circuit reading in avionics)
            df.loc[mask, col] = 0.0
            
        critical_threshold = "Immediate Channel Loss"
        scenario_rul = np.where(mask, 0.0, 99999.0)
        
        df['fault_active'] = mask.astype(int)
        df['fault_id'] = np.where(mask, self.fault_id, 'NONE')
        df['fault_type'] = np.where(mask, 'FT-09_SENSOR_DROPOUT', 'HEALTHY')
        df['fault_cylinder'] = np.where(mask, cyl, 0)
        df['fault_severity'] = np.where(mask, 1.0, 0.0)
        df['scenario_rul_sec'] = scenario_rul
        
        metadata = {
            'fault_id': self.fault_id,
            'fault_name': self.fault_name,
            'sensor_channel': col,
            'severity': severity,
            'affected_cylinder': cyl,
            'onset_time_sec': onset_time_sec,
            'critical_threshold': critical_threshold,
            'source_flight_id': df['flight_id'].iloc[0],
            'random_seed': seed
        }
        return df, metadata
