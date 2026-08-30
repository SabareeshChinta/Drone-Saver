"""
Drone Saver - Human-in-the-Loop Decision Tests
Verifies that AI failsafe recommendations require explicit operator confirmation
and that simulated actions are never executed without human authorization.
Problem Statement: SIH26054 - DRDO
"""

import unittest
import sys
sys.path.insert(0, '.')

from src.mission_risk.failsafe_state_machine import FailsafeStateMachine

class TestHumanInTheLoop(unittest.TestCase):
    def setUp(self):
        self.fsm = FailsafeStateMachine(log_dir="results/events")
        self.fsm.reset()

    def test_nominal_monitoring_state(self):
        engine_st, rec, op_dec, sim_act, _ = self.fsm.update(
            t_sec=10.0,
            health_score=0.98,
            anomaly_score=0.10,
            fault_type="HEALTHY",
            fault_prob=1.0,
            scenario_rul_sec=7200.0,
            p_mission_success=0.99,
            p_rtb_safe=0.99
        )
        self.assertEqual(engine_st, "HEALTHY")
        self.assertEqual(rec, "CONTINUE_MISSION")
        self.assertEqual(op_dec, "MONITORING")
        self.assertEqual(sim_act, "NONE")

    def test_recommendation_requires_operator_approval(self):
        # Trigger severe degradation -> Recommendation: RETURN_TO_BASE
        engine_st, rec, op_dec, sim_act, _ = self.fsm.update(
            t_sec=120.0,
            health_score=0.45,
            anomaly_score=0.88,
            fault_type="FT-02_INJECTOR_CLOGGING",
            fault_prob=0.92,
            scenario_rul_sec=850.0,
            p_mission_success=0.35,
            p_rtb_safe=0.82
        )
        self.assertEqual(engine_st, "WARNING")
        self.assertEqual(rec, "RETURN_TO_BASE")
        self.assertEqual(op_dec, "PENDING")
        # Action MUST be NONE prior to confirmation
        self.assertEqual(sim_act, "NONE")

    def test_operator_confirmation_triggers_simulated_action(self):
        # Trigger RTB recommendation
        self.fsm.update(
            t_sec=120.0,
            health_score=0.45,
            anomaly_score=0.88,
            fault_type="FT-02_INJECTOR_CLOGGING",
            fault_prob=0.92,
            scenario_rul_sec=850.0,
            p_mission_success=0.35,
            p_rtb_safe=0.82
        )
        self.assertEqual(self.fsm.operator_decision, "PENDING")
        self.assertEqual(self.fsm.simulated_action, "NONE")

        # Operator confirms
        event = self.fsm.operator_confirm(t_sec=125.0)
        self.assertEqual(self.fsm.operator_decision, "CONFIRMED")
        self.assertEqual(self.fsm.simulated_action, "SIMULATED_RTB_ACTION")
        self.assertEqual(event["operator_action"], "CONFIRMED")
        self.assertEqual(event["simulated_action"], "SIMULATED_RTB_ACTION")

    def test_operator_rejection_maintains_monitoring(self):
        # Trigger Power Derate recommendation
        self.fsm.update(
            t_sec=70.0,
            health_score=0.80,
            anomaly_score=0.65,
            fault_type="FT-02_INJECTOR_CLOGGING",
            fault_prob=0.85,
            scenario_rul_sec=2200.0,
            p_mission_success=0.82,
            p_rtb_safe=0.95
        )
        self.assertEqual(self.fsm.mission_recommendation, "DERATE_POWER")
        self.assertEqual(self.fsm.operator_decision, "PENDING")

        # Operator rejects recommendation
        event = self.fsm.operator_reject(t_sec=75.0)
        self.assertEqual(self.fsm.operator_decision, "REJECTED")
        self.assertEqual(self.fsm.simulated_action, "NONE")
        self.assertEqual(event["operator_action"], "REJECTED")

if __name__ == "__main__":
    unittest.main()
