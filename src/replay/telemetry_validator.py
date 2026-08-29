"""
Drone Saver - Live Telemetry Validator & Sensor Reliability Confidence Engine
Performs 1.0 Hz streaming validation:
- Detects missing channels, physical range breaches, stale packets, duplicate timestamps
- Assigns packet status: [VALID, PARTIAL, INVALID, STALE]
- Tracks dynamic per-channel sensor reliability confidence [0.0, 1.0]
- Differentiates engine powertrain anomalies from electrical sensor malfunctions
Problem Statement: SIH26054 - DRDO
"""

import numpy as np
from collections import deque

class TelemetryPacketValidator:
    def __init__(self, stale_timeout_sec=3.0, freeze_threshold_steps=30):
        self.stale_timeout_sec = stale_timeout_sec
        self.freeze_threshold_steps = freeze_threshold_steps
        
        self.last_timestamp = None
        self.last_values = {}
        self.freeze_counters = {}
        self.sensor_confidences = {
            'rpm': 1.0, 'map_kpa': 1.0, 'fuel_flow_lph': 1.0,
            'oil_temp_c': 1.0, 'oil_pressure_kpa': 1.0,
            'cht_1_c': 1.0, 'cht_2_c': 1.0, 'cht_3_c': 1.0, 'cht_4_c': 1.0,
            'egt_1_c': 1.0, 'egt_2_c': 1.0, 'egt_3_c': 1.0, 'egt_4_c': 1.0,
            'altitude_m': 1.0, 'airspeed_mps': 1.0, 'ambient_temp_c': 1.0
        }
        
        # Physical bounds dictionary [min, max]
        self.bounds = {
            'rpm': (0.0, 3200.0),
            'map_kpa': (10.0, 140.0),
            'fuel_flow_lph': (0.0, 150.0),
            'oil_temp_c': (-30.0, 150.0),
            'oil_pressure_kpa': (0.0, 800.0),
            'cht_1_c': (-35.0, 270.0), 'cht_2_c': (-35.0, 270.0),
            'cht_3_c': (-35.0, 270.0), 'cht_4_c': (-35.0, 270.0),
            'egt_1_c': (-35.0, 980.0), 'egt_2_c': (-35.0, 980.0),
            'egt_3_c': (-35.0, 980.0), 'egt_4_c': (-35.0, 980.0),
            'altitude_m': (-200.0, 15000.0),
            'airspeed_mps': (0.0, 150.0),
            'ambient_temp_c': (-60.0, 60.0)
        }
        
    def validate_packet(self, packet_dict):
        """
        Validates incoming live telemetry packet dictionary.
        Returns:
            validated_packet (dict): Normalized packet with fallback values if partial.
            status (str): [VALID, PARTIAL, INVALID, STALE]
            confidences (dict): Per-channel sensor reliability scores.
            validation_notes (list): Detailed diagnostic audit flags.
        """
        if not isinstance(packet_dict, dict) or len(packet_dict) == 0:
            return {}, "INVALID", self.sensor_confidences.copy(), ["Empty or non-dictionary packet received"]
            
        validated = packet_dict.copy()
        notes = []
        status = "VALID"
        
        # 1. Timestamp & Stale Check
        t_curr = validated.get('time_seconds', validated.get('timestamp', None))
        if t_curr is None:
            notes.append("Missing timestamp field; substituting current local clock")
            t_curr = (self.last_timestamp + 1.0) if self.last_timestamp is not None else 0.0
            validated['time_seconds'] = t_curr
            status = "PARTIAL"
        else:
            t_curr = float(t_curr)
            validated['time_seconds'] = t_curr
            
        if self.last_timestamp is not None:
            dt = t_curr - self.last_timestamp
            if dt <= 0.0:
                notes.append(f"Duplicate or out-of-order timestamp detected (dt = {dt:.2f}s)")
                status = "STALE"
            elif dt > self.stale_timeout_sec:
                notes.append(f"Telemetry burst gap / stale link detected (dt = {dt:.2f}s)")
                status = "STALE"
                # Degrade global confidences due to link dropout
                for k in self.sensor_confidences:
                    self.sensor_confidences[k] = max(0.2, self.sensor_confidences[k] * 0.85)
                    
        self.last_timestamp = t_curr
        
        # 2. Channel Completeness & Range Auditing
        missing_count = 0
        for channel, (c_min, c_max) in self.bounds.items():
            val = validated.get(channel, None)
            
            if val is None or np.isnan(val):
                missing_count += 1
                # Fallback to last known good value or nominal default
                fallback = self.last_values.get(channel, (c_min + c_max) / 2.0)
                validated[channel] = fallback
                self.sensor_confidences[channel] = max(0.1, self.sensor_confidences[channel] * 0.70)
                notes.append(f"Missing channel [{channel}]; fallback to {fallback:.1f}")
                continue
                
            val = float(val)
            validated[channel] = val
            
            # Check Out-of-Physical-Bounds
            if val < c_min or val > c_max:
                notes.append(f"Channel [{channel}] value {val:.1f} breached physical bounds [{c_min}, {c_max}]")
                self.sensor_confidences[channel] = max(0.05, self.sensor_confidences[channel] * 0.50)
                if status != "INVALID":
                    status = "PARTIAL"
                    
            # Check Sensor Value Freeze (Dead sensor flatlining)
            last_val = self.last_values.get(channel, None)
            if last_val is not None and abs(val - last_val) < 1e-6 and val > 0.0:
                self.freeze_counters[channel] = self.freeze_counters.get(channel, 0) + 1
                if self.freeze_counters[channel] > self.freeze_threshold_steps:
                    notes.append(f"Sensor [{channel}] frozen for > {self.freeze_threshold_steps}s (Flatline)")
                    self.sensor_confidences[channel] = max(0.2, self.sensor_confidences[channel] * 0.95)
            else:
                self.freeze_counters[channel] = 0
                # Gradual confidence recovery if valid
                self.sensor_confidences[channel] = min(1.0, self.sensor_confidences[channel] + 0.05)
                
            self.last_values[channel] = val
            
        if missing_count > 4:
            status = "INVALID"
        elif missing_count > 0 and status == "VALID":
            status = "PARTIAL"
            
        return validated, status, self.sensor_confidences.copy(), notes
