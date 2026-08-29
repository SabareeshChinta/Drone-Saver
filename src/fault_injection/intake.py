"""
Drone Saver - FT-07: Intake Manifold Runner Leak Model
Physical Mechanism:
Intake runner gasket leak admits unmetered ambient air into a single cylinder intake runner.
Under low throttle / high manifold vacuum (idle/descent), leak causes manifold pressure to rise (+5 to +15 kPa)
and causes the affected cylinder to run excessively lean at idle.
Literature: Miljkovic (2019) MIPRO Proceedings
"""

import numpy as np
from src.fault_injection.base import BaseFaultModel
from src.fault_injection.profiles import exponential_lag_profile

class IntakeManifoldLeakFault(BaseFaultModel):
    def __init__(self):
        super().__init__(fault_id="FT-07", fault_name="Intake Manifold Runner Leak", default_target_cyl=2)
        
    def inject(self, data_df, severity=0.75, onset_time_sec=1300, duration_sec=None, affected_cylinder=2, seed=42):
        cyl = affected_cylinder
        df = self._prepare_dataframe(data_df)
        t = df['time_seconds'].values
        
        resp = exponential_lag_profile(t, onset_time_sec, time_constant_sec=15.0)
        # Leak impact is highest when manifold vacuum is high (low MAP)
        idle_factor = np.maximum(0.0, 1.0 - df['map_kpa'].values / 90.0)
        
        delta_map = severity * 12.0 * idle_factor * resp
        delta_egt = severity * 35.0 * idle_factor * resp
        
        df['map_kpa'] += delta_map
        egt_col = f'egt_{cyl}_c'
        if egt_col in df.columns:
            df[egt_col] += delta_egt
            
        critical_threshold = "Severe Idle Lean Stalling / Throttle Inconsistency"
        t_rel = np.maximum(0.0, t - onset_time_sec)
        mask = t >= onset_time_sec
        scenario_rul = np.where(mask, np.maximum(0.0, 3600.0 - t_rel), 99999.0)
        
        df['fault_active'] = mask.astype(int)
        df['fault_id'] = np.where(mask, self.fault_id, 'NONE')
        df['fault_type'] = np.where(mask, 'FT-07_INTAKE_MANIFOLD_LEAK', 'HEALTHY')
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
