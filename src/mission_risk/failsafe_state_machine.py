"""
Drone Saver - UAV Failsafe State Machine & Event Logging Engine
Implements deterministic state machine:
HEALTHY -> DEGRADED -> CRITICAL -> RTB -> EMERGENCY
Logs all state transitions to results/events/decision_events.csv
Problem Statement: SIH26054 - DRDO
"""

import os
import sys
sys.path.insert(0, '.')
import yaml
import pandas as pd
from datetime import datetime

class FailsafeStateMachine:
    def __init__(self, policy_path="config/mission_policy.yaml", log_dir="results/events"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.events_log_file = os.path.join(log_dir, "decision_events.csv")
        
        self.current_state = "HEALTHY"
        self.policy = self._load_policy(policy_path)
        self.transition_history = []
        
    def _load_policy(self, path):
        if os.path.exists(path):
            with open(path, 'r') as fp:
                return yaml.safe_load(fp)
        return {
            'thresholds': {
                'nominal_health_min': 0.85,
                'degraded_health_min': 0.50,
                'critical_health_min': 0.35,
                'continue_mission_p_min': 0.85,
                'derate_power_p_min': 0.70,
                'rtb_safe_p_min': 0.65
            }
        }
        
    def update(self, t_sec, health_score, anomaly_score, fault_type, fault_prob, scenario_rul_sec, p_mission_success, p_rtb_safe, sensor_confidence=1.0):
        """
        Evaluates state transitions based on incoming Digital Twin telemetry and policy thresholds.
        """
        old_state = self.current_state
        new_state = old_state
        trigger = "STEADY_STATE"
        action = "MAINTAIN_CURRENT_DIRECTIVE"
        
        th = self.policy.get('thresholds', {})
        h_nom = th.get('nominal_health_min', 0.85)
        h_deg = th.get('degraded_health_min', 0.50)
        h_crit = th.get('critical_health_min', 0.35)
        
        # 0. Check if engine is parked on ground / off
        rpm = kwargs.get('rpm', 2400.0) if 'kwargs' in locals() else 2400.0
        
        # 1. Evaluate State Transitions
        if sensor_confidence < 0.30:
            # Telemetry link degradation fallback
            if old_state not in ['RTB', 'EMERGENCY']:
                new_state = "DEGRADED"
                trigger = "TELEMETRY_LINK_DEGRADATION"
                action = "FAILSAFE_CONSERVATIVE_HOLD"
                
        elif fault_type in ['FT-04_DETONATION', 'FT-06_LUBRICATION_LOSS'] and fault_prob > 0.75:
            new_state = "EMERGENCY"
            trigger = f"CATASTROPHIC_FAULT_CONFIRMED ({fault_type})"
            action = "CMD_NAV_EMERGENCY_DIVERSION"
            
        elif health_score < h_crit or p_rtb_safe < 0.60:
            new_state = "EMERGENCY" if p_rtb_safe < 0.40 else "RTB"
            trigger = f"CRITICAL_HEALTH_DECAY (H={health_score:.2f}, P_rtb={p_rtb_safe:.2f})"
            action = "CMD_NAV_EMERGENCY_DIVERSION" if new_state == "EMERGENCY" else "CMD_NAV_RTB"
            
        elif health_score < h_deg or p_mission_success < 0.75:
            new_state = "RTB"
            trigger = f"MISSION_SURVIVAL_DEFICIT (P_succ={p_mission_success:.2f})"
            action = "CMD_NAV_RTB"
            
        elif health_score < h_nom or (fault_type != 'HEALTHY' and fault_prob > 0.60):
            if old_state not in ['RTB', 'EMERGENCY']:
                new_state = "DEGRADED"
                trigger = f"DEVELOPING_ANOMALY_DETECTED ({fault_type} p={fault_prob:.2f})"
                action = "CMD_PWR_DERATE_65"
                
        else:
            if old_state not in ['RTB', 'EMERGENCY']:
                new_state = "HEALTHY"
                trigger = "NOMINAL_OPERATION"
                action = "CMD_NAV_CONTINUE"
                
        # If transition occurred, log event
        if new_state != old_state:
            event = {
                'timestamp_utc': datetime.utcnow().isoformat(),
                'time_seconds': t_sec,
                'old_state': old_state,
                'new_state': new_state,
                'trigger': trigger,
                'health_score': round(health_score, 3),
                'anomaly_score': round(anomaly_score, 3),
                'diagnosed_fault': fault_type,
                'scenario_rul_sec': round(scenario_rul_sec, 1),
                'p_mission_success': round(p_mission_success, 3),
                'action_command': action
            }
            self.transition_history.append(event)
            self._append_to_event_log(event)
            self.current_state = new_state
            print(f"[FAILSAFE EVENT @ t={t_sec:.0f}s] State Transition: {old_state} -> {new_state} | Trigger: {trigger}")
            
        return self.current_state, action

    def _append_to_event_log(self, event):
        df_new = pd.DataFrame([event])
        if not os.path.exists(self.events_log_file):
            df_new.to_csv(self.events_log_file, index=False)
        else:
            df_new.to_csv(self.events_log_file, mode='a', header=False, index=False)

    def reset(self):
        self.current_state = "HEALTHY"
        self.transition_history = []
