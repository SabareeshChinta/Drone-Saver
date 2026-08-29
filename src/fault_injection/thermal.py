"""
Drone Saver - FT-04: Thermal & Cooling Degradation Model
Physical Mechanism:
1. Cooling Baffle Deterioration: Air baffle warping/detachment starves rear cylinders (#3/#4) of cooling air.
   CHT rises dynamically: proportional to engine brake power (RPM x MAP) and inversely to ram airspeed.
   Effect is severe during high-load climb/cruise and negligible at idle. EGT is unaffected.
2. Detonation (Knock): End-gas auto-ignition destroys the insulating gas boundary layer.
   Extreme heat transfers directly into head metal (CHT surges +40 to +80 °C), while EGT drops (-20 to -35 °C).
Literature: FAA AC 20-105B, Burluka et al. (2020) Combustion and Flame
"""

import numpy as np
from src.fault_injection.base import BaseFaultModel
from src.fault_injection.profiles import linear_ramp_profile, exponential_lag_profile

class CoolingDegradationFault(BaseFaultModel):
    def __init__(self):
        super().__init__(fault_id="FT-04", fault_name="Cooling Baffle / Thermal Degradation", default_target_cyl=4)
        
    def inject(self, data_df, severity=0.85, onset_time_sec=900, duration_sec=400.0, affected_cylinder=None, mode='baffle', seed=42):
        cyl = affected_cylinder if affected_cylinder is not None else self.default_target_cyl
        df = self._prepare_dataframe(data_df)
        t = df['time_seconds'].values
        
        cht_col = f'cht_{cyl}_c'
        egt_col = f'egt_{cyl}_c'
        
        mask = t >= onset_time_sec
        t_rel = np.maximum(0.0, t - onset_time_sec)
        
        if mode == 'baffle':
            # Dynamic power & airspeed scaling
            ramp = linear_ramp_profile(t, onset_time_sec, duration_sec)
            pwr_factor = (df['map_kpa'].values / 80.0) * (df['rpm'].values / 2400.0)
            cooling_factor = np.maximum(0.5, df['airspeed_mps'].values / 45.0)
            
            delta_cht = severity * (36.0 * pwr_factor / cooling_factor) * ramp
            if cht_col in df.columns:
                df[cht_col] += delta_cht
                
            critical_threshold = "CHT Redline Limit > 224°C (435°F)"
            time_to_redline = 1800.0 / max(0.1, severity)
            scenario_rul = np.where(mask, np.maximum(0.0, time_to_redline - t_rel), 99999.0)
            fault_type_str = 'FT-05_COOLING_BAFFLE_DEGRADATION'
            
        elif mode == 'detonation':
            # Rapid thermal surge (tau = 12s)
            resp = exponential_lag_profile(t, onset_time_sec, time_constant_sec=12.0)
            map_ratio = df['map_kpa'].values / 85.0
            
            delta_cht = severity * (55.0 + 25.0 * map_ratio) * resp
            delta_egt = -severity * 30.0 * resp
            
            if cht_col in df.columns:
                df[cht_col] += delta_cht
            if egt_col in df.columns:
                df[egt_col] += delta_egt
                
            critical_threshold = "Piston Crown Melting / Catastrophic Detonation Seizure"
            time_to_melt = 450.0 / max(0.1, severity)
            scenario_rul = np.where(mask, np.maximum(0.0, time_to_melt - t_rel), 99999.0)
            fault_type_str = 'FT-04_DETONATION'
            
        df['fault_active'] = mask.astype(int)
        df['fault_id'] = np.where(mask, self.fault_id, 'NONE')
        df['fault_type'] = np.where(mask, fault_type_str, 'HEALTHY')
        df['fault_cylinder'] = np.where(mask, cyl, 0)
        df['fault_severity'] = np.where(mask, severity, 0.0)
        df['scenario_rul_sec'] = scenario_rul
        
        metadata = {
            'fault_id': self.fault_id,
            'fault_name': self.fault_name,
            'mode': mode,
            'severity': severity,
            'affected_cylinder': cyl,
            'onset_time_sec': onset_time_sec,
            'critical_threshold': critical_threshold,
            'source_flight_id': df['flight_id'].iloc[0],
            'random_seed': seed
        }
        return df, metadata
