"""
Drone Saver - FT-02: Progressive Fuel Injector Degradation Model
Physical Mechanism:
Gradual nozzle orifice restriction or varnishing reduces fuel delivery to a single cylinder.
Stages:
- Mild (blockage < 10%): Lean shift increases combustion temperature toward stoichiometric (EGT +15 to +35 °C, CHT +5 to +12 °C)
- Moderate (blockage 10-20%): EGT peaks (+50 to +75 °C), CHT reaches elevated stress (+20 to +28 °C), cylinder spread widens
- Severe (blockage > 20%): Lean misfire occurs -> incomplete burn causes dramatic EGT quenching (-150 °C) and power flutter
Literature: Heywood (2018), SAE International ICE Diagnostics
"""

import numpy as np
from src.fault_injection.base import BaseFaultModel
from src.fault_injection.profiles import linear_ramp_profile

class FuelInjectorDegradationFault(BaseFaultModel):
    def __init__(self):
        super().__init__(fault_id="FT-02", fault_name="Fuel Injector Degradation / Lean Shift", default_target_cyl=2)
        
    def inject(self, data_df, severity=0.30, onset_time_sec=1000, duration_sec=1200.0, affected_cylinder=None, seed=42):
        cyl = affected_cylinder if affected_cylinder is not None else self.default_target_cyl
        df = self._prepare_dataframe(data_df)
        t = df['time_seconds'].values
        n = len(df)
        
        # Progressive degradation ramp
        ramp = linear_ramp_profile(t, onset_time_sec, duration_sec)
        kappa = severity * ramp  # Dynamic blockage fraction [0.0, severity]
        
        egt_col = f'egt_{cyl}_c'
        cht_col = f'cht_{cyl}_c'
        
        delta_egt = np.zeros(n)
        delta_cht = np.zeros(n)
        
        for i in range(n):
            k = kappa[i]
            if k == 0.0:
                continue
            elif k <= 0.20:
                # Lean toward peak stoichiometric
                delta_egt[i] = +70.0 * (k / 0.20)
                delta_cht[i] = +24.0 * (k / 0.20)
            else:
                # Severe lean misfire quenching
                excess = (k - 0.20) / max(0.01, severity - 0.20)
                delta_egt[i] = +70.0 - 220.0 * excess
                delta_cht[i] = +24.0 - 18.0 * excess
                
        if egt_col in df.columns:
            df[egt_col] += delta_egt
        if cht_col in df.columns:
            df[cht_col] += delta_cht
            
        # Fuel flow transducer reduction for single cylinder out of 4
        df['fuel_flow_lph'] = np.maximum(5.0, df['fuel_flow_lph'] - (kappa * 0.25 * df['fuel_flow_lph']))
        
        critical_threshold = "Clogging > 20% (Combustion Misfire Limit)"
        t_rel = np.maximum(0.0, t - onset_time_sec)
        mask = t >= onset_time_sec
        # Time to reach 20% misfire threshold
        time_to_misfire = duration_sec * (0.20 / max(0.01, severity))
        scenario_rul = np.where(mask, np.maximum(0.0, time_to_misfire - t_rel), 99999.0)
        
        df['fault_active'] = mask.astype(int)
        df['fault_id'] = np.where(mask, self.fault_id, 'NONE')
        df['fault_type'] = np.where(mask, 'FT-02_INJECTOR_CLOGGING', 'HEALTHY')
        df['fault_cylinder'] = np.where(mask, cyl, 0)
        df['fault_severity'] = kappa
        df['scenario_rul_sec'] = scenario_rul
        
        metadata = {
            'fault_id': self.fault_id,
            'fault_name': self.fault_name,
            'severity': severity,
            'affected_cylinder': cyl,
            'onset_time_sec': onset_time_sec,
            'duration_sec': duration_sec,
            'critical_threshold': critical_threshold,
            'source_flight_id': df['flight_id'].iloc[0],
            'random_seed': seed
        }
        return df, metadata
