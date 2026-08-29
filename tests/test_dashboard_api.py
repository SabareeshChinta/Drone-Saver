"""
Drone Saver - Ground Control Station Dashboard API Tests
Tests REST endpoints, state streaming contracts, and scenario controllers.
Problem Statement: SIH26054 - DRDO
"""

import unittest
import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient

from src.dashboard.server import app

class TestDashboardAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        import time
        for _ in range(20):
            res = self.client.get("/api/state")
            if res.status_code == 200:
                break
            time.sleep(0.1)

    def test_get_state_endpoint(self):
        response = self.client.get("/api/state")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("state", data)
        self.assertIn("telemetry", data)
        self.assertIn("control", data)
        self.assertIn("engine_health", data["state"])
        self.assertIn("failsafe_state", data["state"])

    def test_get_scenarios_endpoint(self):
        response = self.client.get("/api/scenarios")
        self.assertEqual(response.status_code, 200)
        scenarios = response.json()
        self.assertIsInstance(scenarios, list)
        self.assertGreater(len(scenarios), 3)

    def test_control_speed_endpoint(self):
        response = self.client.post("/api/control/speed", json={"speed": 5.0})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["speed"], 5.0)

    def test_control_scenario_switch(self):
        response = self.client.post("/api/control/scenario", json={"scenario_path": "scenarios/live_demo/DEMO-01_healthy.yaml"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "SUCCESS")

    def test_get_history_endpoint(self):
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        history = response.json()
        self.assertIsInstance(history, list)

if __name__ == "__main__":
    unittest.main()
