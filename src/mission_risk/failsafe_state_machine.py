"""
Drone Saver - UAV Failsafe State Machine & Human-in-the-Loop Decision Engine
Implements decoupled states:
- ENGINE STATE: HEALTHY -> ADVISORY -> WARNING -> CRITICAL
- MISSION RECOMMENDATION: CONTINUE_MISSION -> DERATE_POWER -> RETURN_TO_BASE -> EMERGENCY_LANDING
- OPERATOR DECISION: MONITORING -> PENDING -> CONFIRMED -> REJECTED
- SIMULATED AUTOPILOT ACTION: NONE -> SIMULATED_POWER_DERATE -> SIMULATED_RTB_ACTION -> SIMULATED_EMERGENCY_DIVERSION

Logs all state transitions and operator interactions to results/events/decision_events.csv
Problem Statement: SIH26054 - DRDO
"""

import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import yaml
import pandas as pd
from datetime import datetime, timezone

class FailsafeStateMachine:
    def __init__(self, policy_path=None, log_dir=None):
        if policy_path is None:
            policy_path = os.path.join(PROJECT_ROOT, "config", "mission_policy.yaml")
        if log_dir is None:
            log_dir = os.path.join(PROJECT_ROOT, "results", "events")
            
        self.log_dir = log_dir
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception:
            pass
        self.events_log_file = os.path.join(log_dir, "decision_events.csv")
        
        self.engine_state = "HEALTHY"
        self.mission_recommendation = "CONTINUE_MISSION"
        self.operator_decision = "MONITORING"
        self.simulated_action = "NONE"
        
        self.current_state = "HEALTHY"  # Backwards-compatible alias
        self.policy = self._load_policy(policy_path)
        self.transition_history = []
        self._last_evaluated_recommendation = "CONTINUE_MISSION"
        
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

    def reset(self):
        self.engine_state = "HEALTHY"
        self.mission_recommendation = "CONTINUE_MISSION"
        self.operator_decision = "MONITORING"
        self.simulated_action = "NONE"
        self.current_state = "HEALTHY"
        self.transition_history.clear()
        self._last_evaluated_recommendation = "CONTINUE_MISSION"

    def operator_confirm(self, t_sec: float = 0.0) -> dict:
        """Operator explicitly confirms the AI failsafe recommendation."""
        old_op = self.operator_decision
        self.operator_decision = "CONFIRMED"
        
        # Determine simulated autopilot action based on confirmed recommendation
        if self.mission_recommendation == "RETURN_TO_BASE":
            self.simulated_action = "SIMULATED_RTB_ACTION"
        elif self.mission_recommendation == "DERATE_POWER":
            self.simulated_action = "SIMULATED_POWER_DERATE"
        elif self.mission_recommendation == "EMERGENCY_LANDING":
            self.simulated_action = "SIMULATED_EMERGENCY_DIVERSION"
        else:
            self.simulated_action = "NONE"
            
        event = {
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'time_seconds': t_sec,
            'engine_state': self.engine_state,
            'health_score': getattr(self, '_latest_health', 1.0),
            'anomaly_score': getattr(self, '_latest_anomaly', 0.0),
            'fault_type': getattr(self, '_latest_fault', "HEALTHY"),
            'fault_probability': getattr(self, '_latest_fault_prob', 1.0),
            'scenario_rul_sec': getattr(self, '_latest_rul', 7200.0),
            'mission_success_probability': getattr(self, '_latest_p_succ', 1.0),
            'recommended_action': self.mission_recommendation,
            'operator_action': "CONFIRMED",
            'simulated_action': self.simulated_action,
            'event_type': "OPERATOR_DECISION_CONFIRMED"
        }
        self.transition_history.append(event)
        self._append_to_event_log(event)
        return event

    def operator_reject(self, t_sec: float = 0.0) -> dict:
        """Operator rejects the recommendation, continuing manual/health monitoring."""
        self.operator_decision = "REJECTED"
        self.simulated_action = "NONE"
        
        event = {
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'time_seconds': t_sec,
            'engine_state': self.engine_state,
            'health_score': getattr(self, '_latest_health', 1.0),
            'anomaly_score': getattr(self, '_latest_anomaly', 0.0),
            'fault_type': getattr(self, '_latest_fault', "HEALTHY"),
            'fault_probability': getattr(self, '_latest_fault_prob', 1.0),
            'scenario_rul_sec': getattr(self, '_latest_rul', 7200.0),
            'mission_success_probability': getattr(self, '_latest_p_succ', 1.0),
            'recommended_action': self.mission_recommendation,
            'operator_action': "REJECTED",
            'simulated_action': "NONE",
            'event_type': "OPERATOR_DECISION_REJECTED"
        }
        self.transition_history.append(event)
        self._append_to_event_log(event)
        return event

    def update(self, t_sec, health_score, anomaly_score, fault_type, fault_prob, scenario_rul_sec, p_mission_success, p_rtb_safe, sensor_confidence=1.0):
        """
        Evaluates engine health state and computes AI failsafe recommendation.
        Decouples engine physical state from operator decision.
        """
        self._latest_health = round(health_score, 3)
        self._latest_anomaly = round(anomaly_score, 3)
        self._latest_fault = fault_type
        self._latest_fault_prob = round(fault_prob, 3)
        self._latest_rul = round(scenario_rul_sec, 1)
        self._latest_p_succ = round(p_mission_success, 3)
        
        old_engine_state = self.engine_state
        old_rec = self.mission_recommendation
        
        th = self.policy.get('thresholds', {})
        h_nom = th.get('nominal_health_min', 0.85)
        h_deg = th.get('degraded_health_min', 0.50)
        h_crit = th.get('critical_health_min', 0.35)
        
        # 1. Evaluate Engine Physical State
        if fault_type in ['FT-04_DETONATION', 'FT-06_LUBRICATION_LOSS'] and fault_prob > 0.75:
            new_engine_state = "CRITICAL"
            new_rec = "EMERGENCY_LANDING"
            short_cmd = "CMD_NAV_EMERGENCY_DIVERSION"
            trigger = f"CATASTROPHIC_FAULT_CONFIRMED ({fault_type})"
        elif health_score < h_crit or p_rtb_safe < 0.60:
            new_engine_state = "CRITICAL" if p_rtb_safe < 0.40 else "WARNING"
            new_rec = "EMERGENCY_LANDING" if new_engine_state == "CRITICAL" else "RETURN_TO_BASE"
            short_cmd = "CMD_NAV_EMERGENCY_DIVERSION" if new_rec == "EMERGENCY_LANDING" else "CMD_NAV_RTB"
            trigger = f"CRITICAL_HEALTH_DECAY (H={health_score:.2f}, P_rtb={p_rtb_safe:.2f})"
        elif health_score < h_deg or p_mission_success < 0.75:
            new_engine_state = "WARNING"
            new_rec = "RETURN_TO_BASE"
            short_cmd = "CMD_NAV_RTB"
            trigger = f"MISSION_SURVIVAL_DEFICIT (P_succ={p_mission_success:.2f})"
        elif health_score < h_nom or (fault_type != 'HEALTHY' and fault_prob > 0.60):
            if old_engine_state not in ['WARNING', 'CRITICAL']:
                new_engine_state = "ADVISORY"
                new_rec = "DERATE_POWER"
                short_cmd = "CMD_PWR_DERATE_65"
                trigger = f"DEVELOPING_ANOMALY_DETECTED ({fault_type} p={fault_prob:.2f})"
            else:
                new_engine_state = old_engine_state
                new_rec = old_rec
                short_cmd = "CMD_NAV_RTB" if old_rec == "RETURN_TO_BASE" else "CMD_NAV_EMERGENCY_DIVERSION"
                trigger = "MAINTAIN_WARNING_STATE"
        else:
            if old_engine_state not in ['WARNING', 'CRITICAL']:
                new_engine_state = "HEALTHY"
                new_rec = "CONTINUE_MISSION"
                short_cmd = "CMD_NAV_CONTINUE"
                trigger = "NOMINAL_OPERATION"
            else:
                new_engine_state = old_engine_state
                new_rec = old_rec
                short_cmd = "CMD_NAV_RTB" if old_rec == "RETURN_TO_BASE" else "CMD_NAV_EMERGENCY_DIVERSION"
                trigger = "MAINTAIN_WARNING_STATE"

        # 2. Check if recommendation changed -> set operator state to PENDING if actionable
        if new_rec != old_rec:
            if new_rec != "CONTINUE_MISSION":
                self.operator_decision = "PENDING"
                self.simulated_action = "NONE"  # Awaiting human confirmation
            else:
                self.operator_decision = "MONITORING"
                self.simulated_action = "NONE"

        # 3. Log state changes
        if new_engine_state != old_engine_state or new_rec != old_rec:
            event = {
                'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                'time_seconds': t_sec,
                'engine_state': new_engine_state,
                'health_score': self._latest_health,
                'anomaly_score': self._latest_anomaly,
                'fault_type': fault_type,
                'fault_probability': self._latest_fault_prob,
                'scenario_rul_sec': self._latest_rul,
                'mission_success_probability': self._latest_p_succ,
                'recommended_action': new_rec,
                'operator_action': self.operator_decision,
                'simulated_action': self.simulated_action,
                'event_type': "RECOMMENDATION_CHANGE" if new_rec != old_rec else "STATE_CHANGE"
            }
            self.transition_history.append(event)
            self._append_to_event_log(event)
            print(f"[FAILSAFE EVENT @ t={t_sec:.0f}s] Recommendation: {old_rec} -> {new_rec} | Engine State: {new_engine_state} | Op Decision: {self.operator_decision}")
            
        self.engine_state = new_engine_state
        self.mission_recommendation = new_rec
        self.current_state = new_engine_state
        
        return self.engine_state, self.mission_recommendation, self.operator_decision, self.simulated_action, short_cmd

    def _append_to_event_log(self, event):
        try:
            df_new = pd.DataFrame([event])
            if not os.path.exists(self.events_log_file):
                df_new.to_csv(self.events_log_file, index=False)
            else:
                df_new.to_csv(self.events_log_file, mode='a', header=False, index=False)
        except Exception:
            pass
