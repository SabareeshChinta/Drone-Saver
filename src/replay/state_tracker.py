"""
Drone Saver - Stateful Real-Time History & Feature Buffer
Provides strictly causal, backward-looking moving averages, derivatives,
and state-space smoothing without future lookahead.
Problem Statement: SIH26054 - DRDO
"""

import numpy as np
from collections import deque

class StreamingStateTracker:
    def __init__(self, window_size=10, alpha_health=0.05):
        self.window_size = window_size
        self.alpha_health = alpha_health
        self.history = deque(maxlen=window_size)
        self.current_health = 1.0
        self.anomaly_buffer = deque(maxlen=5)
        
    def update(self, current_telemetry_dict):
        """
        Updates internal FIFO buffer with latest single telemetry timestep t.
        Returns extracted causal rolling features.
        """
        self.history.append(current_telemetry_dict)
        n_pts = len(self.history)
        
        # Current values
        curr = current_telemetry_dict
        
        # 1. Multi-Cylinder Spreads at timestamp t
        egt_vals = [curr.get(f'egt_{i}_c', 0.0) for i in range(1, 5)]
        cht_vals = [curr.get(f'cht_{i}_c', 0.0) for i in range(1, 5)]
        
        egt_spread = max(egt_vals) - min(egt_vals)
        cht_spread = max(cht_vals) - min(cht_vals)
        egt_mean = np.mean(egt_vals)
        cht_mean = np.mean(cht_vals)
        
        # Deviations from mean
        egt_devs = [egt_vals[i] - egt_mean for i in range(4)]
        cht_devs = [cht_vals[i] - cht_mean for i in range(4)]
        
        # 2. Causal Backward Thermal Derivatives (dT/dt over available past window)
        degt_dt = [0.0] * 4
        dcht_dt = [0.0] * 4
        if n_pts >= 2:
            prev = self.history[-2]
            dt = max(1.0, curr.get('time_seconds', 0) - prev.get('time_seconds', 0))
            for i in range(4):
                degt_dt[i] = (egt_vals[i] - prev.get(f'egt_{i+1}_c', 0.0)) / dt
                dcht_dt[i] = (cht_vals[i] - prev.get(f'cht_{i+1}_c', 0.0)) / dt
                
        # 3. Dynamic Health Decay Tracking (Only when engine is actively running)
        rpm = curr.get('rpm', 2400.0)
        oil_p = curr.get('oil_pressure_kpa', 450.0)
        
        if rpm > 600:
            norm_egt_pen = max(0.0, (egt_spread - 35.0) / 45.0)
            norm_cht_pen = max(0.0, (cht_spread - 15.0) / 25.0)
            norm_oil_pen = max(0.0, (380.0 - oil_p) / 250.0) if rpm > 1200 else 0.0
            
            instant_damage = min(1.0, 0.45 * norm_egt_pen + 0.35 * norm_cht_pen + 0.20 * norm_oil_pen)
            raw_h = 1.0 - instant_damage
            
            # Asymmetric state-space health filter
            if raw_h < self.current_health:
                self.current_health = (1.0 - self.alpha_health) * self.current_health + self.alpha_health * raw_h
            else:
                self.current_health = (1.0 - (self.alpha_health * 0.2)) * self.current_health + (self.alpha_health * 0.2) * raw_h
        else:
            # Engine parked / off on ramp
            instant_damage = 0.0
            self.current_health = 1.0
            
        self.current_health = np.clip(self.current_health, 0.0, 1.0)
        
        # Assemble complete single-step feature dictionary
        features = {
            **curr,
            'egt_spread_c': egt_spread,
            'cht_spread_c': cht_spread,
            'egt_mean_c': egt_mean,
            'cht_mean_c': cht_mean,
            'egt_dev_mean_cyl1_c': egt_devs[0],
            'egt_dev_mean_cyl2_c': egt_devs[1],
            'egt_dev_mean_cyl3_c': egt_devs[2],
            'egt_dev_mean_cyl4_c': egt_devs[3],
            'cht_dev_mean_cyl1_c': cht_devs[0],
            'cht_dev_mean_cyl2_c': cht_devs[1],
            'cht_dev_mean_cyl3_c': cht_devs[2],
            'cht_dev_mean_cyl4_c': cht_devs[3],
            'degt_dt_cyl1_cps': degt_dt[0],
            'degt_dt_cyl2_cps': degt_dt[1],
            'degt_dt_cyl3_cps': degt_dt[2],
            'degt_dt_cyl4_cps': degt_dt[3],
            'dcht_dt_cyl1_cps': dcht_dt[0],
            'dcht_dt_cyl2_cps': dcht_dt[1],
            'dcht_dt_cyl3_cps': dcht_dt[2],
            'dcht_dt_cyl4_cps': dcht_dt[3],
        }
        features['health_state_h'] = self.current_health
        return features

    def reset(self):
        self.history.clear()
        self.prev_raw = None
        self.current_health = 1.0
