"""
Drone Saver - Stage 4: Mission Reliability & Abort Decision Support Engine
Evaluates:
1. Dynamic In-Flight Loiter Survival Probability P(Mission Success) via Monte Carlo simulation
2. Actionable UAV Autopilot Failsafe Recommendations:
   - [CONTINUE_MISSION, DERATE_POWER_AND_LOITER, ABORT_RETURN_TO_BASE, EMERGENCY_DESCENT_LANDING]
3. Risk Assessment Matrix & DRDO Ground Control Station (GCS) Telemetry Diagnostics
Problem Statement: SIH26054 - DRDO
"""

import os
import sys
sys.path.insert(0, '.')
import numpy as np
import pandas as pd

class UAVMissionReliabilityEngine:
    def __init__(self, target_mission_duration_sec=7200.0, base_return_transit_sec=1200.0):
        self.target_mission_duration_sec = target_mission_duration_sec
        self.base_return_transit_sec = base_return_transit_sec
        
    def evaluate_mission_risk(self, current_time_sec, health_score, fault_type, fault_prob, rul_pred_sec, rul_lower_sec):
        """
        Calculates real-time mission survival probability and provides operator decision support.
        """
        time_remaining_mission = max(0.0, self.target_mission_duration_sec - current_time_sec)
        time_needed_to_rtb = self.base_return_transit_sec
        
        # Monte Carlo estimation of survival probability
        n_mc = 1000
        sigma = max(0.05, (rul_pred_sec - rul_lower_sec) / (rul_pred_sec + 1e-3))
        mc_ruls = np.random.lognormal(mean=np.log(max(1.0, rul_pred_sec)), sigma=sigma, size=n_mc)
        
        p_mission_success = float(np.mean(mc_ruls > time_remaining_mission))
        p_rtb_safe = float(np.mean(mc_ruls > time_needed_to_rtb))
        
        # Explainable Decision Logic Matrix
        if health_score >= 0.80 and (fault_type == 'HEALTHY' or fault_prob < 0.60):
            recommendation = "CONTINUE_MISSION"
            risk_level = "LOW (NOMINAL)"
            action_protocol = "Maintain scheduled altitude and waypoint loiter plan."
        elif health_score >= 0.50 and fault_type in ['FT-05_COOLING_BAFFLE_DEGRADATION', 'FT-08_SENSOR_DRIFT', 'FT-07_INTAKE_MANIFOLD_LEAK']:
            recommendation = "DERATE_POWER_AND_LOITER"
            risk_level = "MODERATE (CAUTION)"
            action_protocol = "Derate engine throttle to 65% power; increase loiter airspeed by 5 m/s for ram air cooling."
        elif health_score < 0.35 or p_rtb_safe < 0.60 or fault_type in ['FT-04_DETONATION', 'FT-06_LUBRICATION_LOSS']:
            recommendation = "EMERGENCY_DESCENT_LANDING"
            risk_level = "CRITICAL (EMERGENCY)"
            action_protocol = "Imminent engine failure risk. Divert to nearest emergency recovery airstrip immediately."
        elif p_mission_success < 0.75 or health_score < 0.70:
            recommendation = "ABORT_RETURN_TO_BASE"
            risk_level = "HIGH (WARNING - ABORT)"
            action_protocol = "Disengage loiter orbit; initiate immediate return-to-base (RTB) navigation."
        else:
            recommendation = "CONTINUE_MISSION"
            risk_level = "LOW (NOMINAL)"
            action_protocol = "Maintain flight plan."
            
        return {
            'time_elapsed_sec': current_time_sec,
            'time_remaining_mission_sec': time_remaining_mission,
            'health_score': round(health_score, 3),
            'detected_fault': fault_type,
            'fault_confidence': round(fault_prob * 100.0, 1),
            'predicted_rul_min': round(rul_pred_sec / 60.0, 1),
            'rul_lower_bound_min': round(rul_lower_sec / 60.0, 1),
            'p_mission_success': round(p_mission_success, 3),
            'p_rtb_safe': round(p_rtb_safe, 3),
            'risk_level': risk_level,
            'operator_recommendation': recommendation,
            'action_protocol': action_protocol
        }
