"""
Drone Saver - FT-03: Burnt / Leaking Exhaust Valve Degradation Model
Physical Mechanism:
Combustion gas leaks past the exhaust valve seat into the exhaust runner during peak firing.
Because aircraft exhaust valves slowly rotate inside their guide bushings (1 rev per 10-20s),
the leak orifice area periodically opens and contracts, producing a signature low-frequency
sinusoidal oscillation (+-12 to +-18 °C @ 0.05 - 0.10 Hz) superposed on an elevated mean EGT.
CHT is largely unaffected as heat exits into the exhaust runner before conducting into head metal.
Literature: Busch (2016) Savvy Aviation Valve Failure Analysis, Miljkovic (2014)
"""

import numpy as np
from src.fault_injection.base import BaseFaultModel
from src.fault_injection.profiles import linear_ramp_profile, rotational_oscillation_profile

class BurntExhaustValveFault(BaseFaultModel):
    def __init__(self):
        super().__init__(fault_id="FT-03", fault_name="Burnt Exhaust Valve Leakage", default_target_cyl=3)
        
    def inject(self, data_df, severity=0.85, onset_time_sec=800, duration_sec=600.0, affected_cylinder=None, seed=42):
        cyl = affected_cylinder if affected_cylinder is not None else self.default_target_cyl
        df = self._prepare_dataframe(data_df)
        t = df['time_seconds'].values
        
        # Progressive degradation ramp
        ramp = linear_ramp_profile(t, onset_time_sec, duration_sec)
        
        # Rotational valve oscillation (freq ~ 0.065 Hz / 1 cycle per 15s)
        osc = rotational_oscillation_profile(t, onset_time_sec, frequency_hz=0.065)
        
        # Mean EGT elevation + harmonic modulation
        delta_egt = severity * (28.0 + 15.0 * osc) * ramp
        
        egt_col = f'egt_{cyl}_c'
        if egt_col in df.columns:
            df[egt_col] += delta_egt
            
        critical_threshold = "Valve guttering breach / Loss of compression"
        t_rel = np.maximum(0.0, t - onset_time_sec)
        mask = t >= onset_time_sec
        time_to_breach = 2200.0 / max(0.1, severity)
        scenario_rul = np.where(mask, np.maximum(0.0, time_to_breach - t_rel), 99999.0)
        
        df['fault_active'] = mask.astype(int)
        df['fault_id'] = np.where(mask, self.fault_id, 'NONE')
        df['fault_type'] = np.where(mask, 'FT-03_BURNT_EXHAUST_VALVE', 'HEALTHY')
        df['fault_cylinder'] = np.where(mask, cyl, 0)
        df['fault_severity'] = severity * ramp
        df['scenario_rul_sec'] = scenario_rul
        
        metadata = {
            'fault_id': self.fault_id,
            'fault_name': self.fault_name,
            'severity': severity,
            'affected_cylinder': cyl,
            'onset_time_sec': onset_time_sec,
            'duration_sec': duration_sec,
            'oscillation_freq_hz': 0.065,
            'critical_threshold': critical_threshold,
            'source_flight_id': df['flight_id'].iloc[0],
            'random_seed': seed
        }
        return df, metadata
