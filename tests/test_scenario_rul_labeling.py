"""
Drone Saver - Scenario RUL Terminology & Disclaimer Tests
Verifies that all prognostics outputs are strictly labeled as SCENARIO TIME-TO-CRITICAL
with required disclaimers, avoiding misleading material fatigue lifing claims.
Problem Statement: SIH26054 - DRDO
"""

import unittest
import sys
sys.path.insert(0, '.')

from src.replay.state_export import EngineHealthState
from src.dashboard.server import gcs_mgr

class TestScenarioRULLabeling(unittest.TestCase):
    def test_state_export_contains_scenario_rul_field(self):
        state = EngineHealthState(
            timestamp=100.0,
            time_seconds=100.0,
            engine_health=0.85,
            anomaly_score=0.25,
            fault="HEALTHY",
            fault_probability=0.95,
            affected_cylinder=0,
            scenario_rul_sec=1800.0,
            mission_success_probability=0.90,
            p_rtb_safe=0.95,
            engine_state="HEALTHY",
            failsafe_state="HEALTHY",
            mission_recommendation="CONTINUE_MISSION",
            recommendation="CMD_NAV_CONTINUE",
            operator_decision="MONITORING",
            simulated_action="NONE",
            data_origin="REAL_TELEMETRY",
            source_dataset="NGAFID",
            source_flight_id="FLIGHT_01",
            scenario_id="SIH_FLAGSHIP_DEMO",
            sensor_confidences={"rpm": 1.0}
        )
        d = state.to_dict()
        self.assertIn("scenario_rul_sec", d)
        self.assertEqual(d["scenario_rul_sec"], 1800.0)

    def test_gcs_payload_disclaimer_presence(self):
        payload = gcs_mgr.get_full_payload()
        if payload.get("status") != "INITIALIZING":
            self.assertIn("scenario_rul", payload)
            rul_data = payload["scenario_rul"]
            self.assertIn("time_to_critical_min", rul_data)
            self.assertIn("disclaimer", rul_data)
            self.assertIn("not material fatigue life", rul_data["disclaimer"])

if __name__ == "__main__":
    unittest.main()
