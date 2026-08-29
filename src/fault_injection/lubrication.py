"""
Drone Saver - FT-05 / FT-06: Lubrication Degradation & Oil Pressure Loss Model
Physical Mechanism:
Oil pressure relief valve malfunction, oil line rupture, or severe oil aeration causes
main gallery lubrication pressure to drop (-25% to -60%).
Reduced oil circulation reduces bearing heat scavenging:
- Oil sump temperature rises (+15 to +35 °C)
- Mild CHT elevation (+5 to +10 °C across all cylinders)
- Hydraulic Viscosity Index diverges from healthy baseline
Literature: Taylor (1985) ICE in Theory and Practice, SAE Paper 2017-01-1052
"""

import numpy as np
from src.fault_injection.base import BaseFaultModel
from src.fault_injection.profiles import exponential_lag_profile

class LubricationDegradationFault(BaseFaultModel):
    def __init__(self):
        super().__init__(fault_id="FT-06", fault_name="Lubrication Degradation / Oil Pressure Loss", default_target_cyl=0)
        
    def inject(self, data_df, severity=0.60, onset_time_sec=1100, duration_sec=None, affected_cylinder=0, seed=42):
        df = self._prepare_dataframe(data_df)
        t = df['time_seconds'].values
        
        # Fast hydraulic pressure drop (tau ~ 10s), slow oil thermal rise (tau ~ 80s)
        resp_p = exponential_lag_profile(t, onset_time_sec, time_constant_sec=10.0)
        resp_t = exponential_lag_profile(t, onset_time_sec, time_constant_sec=80.0)
        
        # Pressure derating
        df['oil_pressure_kpa'] = np.maximum(30.0, df['oil_pressure_kpa'] - severity * df['oil_pressure_kpa'] * resp_p)
        df['oil_temp_c'] += severity * 32.0 * resp_t
        
        # Global slight CHT elevation
        for i in range(1, 5):
            col = f'cht_{i}_c'
            if col in df.columns:
                df[col] += severity * 8.0 * resp_t
                
        critical_threshold = "Oil Pressure < 172 kPa (25 PSI) / Engine Bearing Seizure"
        t_rel = np.maximum(0.0, t - onset_time_sec)
        mask = t >= onset_time_sec
        time_to_seizure = 900.0 / max(0.1, severity)
        scenario_rul = np.where(mask, np.maximum(0.0, time_to_seizure - t_rel), 99999.0)
        
        df['fault_active'] = mask.astype(int)
        df['fault_id'] = np.where(mask, self.fault_id, 'NONE')
        df['fault_type'] = np.where(mask, 'FT-06_LUBRICATION_LOSS', 'HEALTHY')
        df['fault_cylinder'] = 0  # Global engine fault
        df['fault_severity'] = np.where(mask, severity, 0.0)
        df['scenario_rul_sec'] = scenario_rul
        
        metadata = {
            'fault_id': self.fault_id,
            'fault_name': self.fault_name,
            'severity': severity,
            'affected_cylinder': 0,
            'onset_time_sec': onset_time_sec,
            'critical_threshold': critical_threshold,
            'source_flight_id': df['flight_id'].iloc[0],
            'random_seed': seed
        }
        return df, metadata
