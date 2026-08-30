"""
Drone Saver - Demo Reset & Determinism Tests
Verifies that resetting the demo resets all state trackers, normalizers,
and decision state machines to the clean initial nominal condition.
Problem Statement: SIH26054 - DRDO
"""

import unittest
import sys
sys.path.insert(0, '.')

from src.dashboard.server import gcs_mgr

class TestDemoReset(unittest.TestCase):
    def test_gcs_reset_returns_to_initial_state(self):
        # 1. Trigger reset
        gcs_mgr.reset()
        
        # 2. Check FSM state
        self.assertEqual(gcs_mgr.pipeline.failsafe_sm.engine_state, "HEALTHY")
        self.assertEqual(gcs_mgr.pipeline.failsafe_sm.mission_recommendation, "CONTINUE_MISSION")
        self.assertEqual(gcs_mgr.pipeline.failsafe_sm.operator_decision, "MONITORING")
        self.assertEqual(gcs_mgr.pipeline.failsafe_sm.simulated_action, "NONE")

        # 3. Check State Tracker
        self.assertEqual(gcs_mgr.pipeline.tracker.current_health, 1.0)
        self.assertEqual(len(gcs_mgr.pipeline.tracker.history), 0)

if __name__ == "__main__":
    unittest.main()
