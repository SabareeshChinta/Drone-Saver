"""
Drone Saver - Packet Loss & Network Drop Robustness Tests
Evaluates:
- 1% packet loss
- 5% packet loss
- 10% packet loss
- Burst loss (5 to 10 consecutive missing packets)
Problem Statement: SIH26054 - DRDO
"""

import unittest
import sys
sys.path.insert(0, '.')
import numpy as np
import pandas as pd

from src.replay.live_pipeline import LiveDigitalTwinPipeline
from src.replay.scenario_loader import ScenarioLoader

class TestPacketLossRobustness(unittest.TestCase):
    def setUp(self):
        self.pipeline = LiveDigitalTwinPipeline()
        loader = ScenarioLoader()
        self.df_feed, _ = loader.load_scenario("scenarios/live_demo/DEMO-01_healthy.yaml")
        
    def _run_with_loss_rate(self, loss_rate=0.05):
        np.random.seed(42)
        states = []
        for idx in range(min(500, len(self.df_feed))):
            if np.random.rand() < loss_rate:
                continue  # Drop packet
            pkt = self.df_feed.iloc[idx].to_dict()
            state, _, _ = self.pipeline.process_packet(pkt)
            states.append(state)
        return states

    def test_one_percent_loss(self):
        states = self._run_with_loss_rate(0.01)
        self.assertGreater(len(states), 450)
        # Verify pipeline stayed healthy on nominal flight
        mean_health = np.mean([s.engine_health for s in states])
        self.assertGreater(mean_health, 0.65)

    def test_five_percent_loss(self):
        states = self._run_with_loss_rate(0.05)
        self.assertGreater(len(states), 400)
        mean_health = np.mean([s.engine_health for s in states])
        self.assertGreater(mean_health, 0.60)

    def test_ten_percent_loss(self):
        states = self._run_with_loss_rate(0.10)
        self.assertGreater(len(states), 350)
        mean_health = np.mean([s.engine_health for s in states])
        self.assertGreater(mean_health, 0.60)

    def test_burst_packet_loss(self):
        states = []
        for idx in range(min(500, len(self.df_feed))):
            # Drop 10 consecutive packets from idx=100 to 110
            if 100 <= idx < 110:
                continue
            pkt = self.df_feed.iloc[idx].to_dict()
            state, _, _ = self.pipeline.process_packet(pkt)
            states.append(state)
        # Pipeline must survive burst gap and resume valid tracking
        self.assertEqual(len(states), 500 - 10)
        final_state = states[-1]
        self.assertIn(final_state.failsafe_state, ['HEALTHY', 'DEGRADED', 'RTB'])

if __name__ == "__main__":
    unittest.main()
