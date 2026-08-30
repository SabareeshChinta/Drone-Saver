"""
Drone Saver - Decision & Event Logging Tests
Verifies that all failsafe state changes and operator confirmation/rejection events
are logged to results/events/decision_events.csv with the required schema.
Problem Statement: SIH26054 - DRDO
"""

import unittest
import os
import sys
sys.path.insert(0, '.')
import pandas as pd

from src.mission_risk.failsafe_state_machine import FailsafeStateMachine

class TestDecisionLogging(unittest.TestCase):
    def setUp(self):
        self.test_log_dir = "results/events"
        self.fsm = FailsafeStateMachine(log_dir=self.test_log_dir)
        self.fsm.reset()

    def test_decision_events_file_logging(self):
        # 1. State change to RTB
        self.fsm.update(
            t_sec=200.0,
            health_score=0.40,
            anomaly_score=0.90,
            fault_type="FT-02_INJECTOR_CLOGGING",
            fault_prob=0.95,
            scenario_rul_sec=700.0,
            p_mission_success=0.20,
            p_rtb_safe=0.85
        )

        # 2. Operator Confirmation
        self.fsm.operator_confirm(t_sec=205.0)

        # Check CSV file
        log_file = self.fsm.events_log_file
        self.assertTrue(os.path.exists(log_file))

        df = pd.read_csv(log_file)
        self.assertGreaterEqual(len(df), 2)
        
        # Verify columns exist
        required_cols = [
            'timestamp_utc', 'time_seconds', 'engine_state', 'health_score',
            'anomaly_score', 'fault_type', 'fault_probability', 'scenario_rul_sec',
            'mission_success_probability', 'recommended_action', 'operator_action',
            'simulated_action'
        ]
        for col in required_cols:
            self.assertIn(col, df.columns)

if __name__ == "__main__":
    unittest.main()
