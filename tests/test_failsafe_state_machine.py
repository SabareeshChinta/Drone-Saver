"""
Drone Saver - Unit Tests for Failsafe State Machine
Problem Statement: SIH26054 - DRDO
"""

import unittest
import os
import sys
sys.path.insert(0, '.')

from src.mission_risk.failsafe_state_machine import FailsafeStateMachine

class TestFailsafeStateMachine(unittest.TestCase):
    def setUp(self):
        self.sm = FailsafeStateMachine(log_dir="results/events")
        self.sm.reset()

    def test_nominal_healthy_state(self):
        state, action = self.sm.update(
            t_sec=100.0, health_score=0.95, anomaly_score=0.05,
            fault_type="HEALTHY", fault_prob=0.99, scenario_rul_sec=3600.0,
            p_mission_success=0.98, p_rtb_safe=0.99
        )
        self.assertEqual(state, "HEALTHY")
        self.assertEqual(action, "CMD_NAV_CONTINUE")

    def test_transition_to_degraded(self):
        # Trigger mild cooling fault
        state, action = self.sm.update(
            t_sec=200.0, health_score=0.75, anomaly_score=0.35,
            fault_type="FT-05_COOLING_BAFFLE_DEGRADATION", fault_prob=0.85, scenario_rul_sec=1800.0,
            p_mission_success=0.88, p_rtb_safe=0.92
        )
        self.assertEqual(state, "DEGRADED")
        self.assertEqual(action, "CMD_PWR_DERATE_65")

    def test_transition_to_rtb(self):
        # Low mission success probability
        state, action = self.sm.update(
            t_sec=300.0, health_score=0.45, anomaly_score=0.65,
            fault_type="FT-02_INJECTOR_CLOGGING", fault_prob=0.90, scenario_rul_sec=600.0,
            p_mission_success=0.40, p_rtb_safe=0.75
        )
        self.assertEqual(state, "RTB")
        self.assertEqual(action, "CMD_NAV_RTB")

    def test_catastrophic_emergency_transition(self):
        state, action = self.sm.update(
            t_sec=400.0, health_score=0.15, anomaly_score=0.95,
            fault_type="FT-06_LUBRICATION_LOSS", fault_prob=0.98, scenario_rul_sec=120.0,
            p_mission_success=0.05, p_rtb_safe=0.20
        )
        self.assertEqual(state, "EMERGENCY")
        self.assertEqual(action, "CMD_NAV_EMERGENCY_DIVERSION")

if __name__ == "__main__":
    unittest.main()
