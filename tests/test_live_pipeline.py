"""
Drone Saver - Unit Tests for Live Streaming Pipeline
Problem Statement: SIH26054 - DRDO
"""

import unittest
import sys
sys.path.insert(0, '.')

from src.replay.live_pipeline import LiveDigitalTwinPipeline
from src.replay.telemetry_listener import ReplaySource

class TestLivePipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = LiveDigitalTwinPipeline()

    def test_single_packet_inference(self):
        nominal_packet = {
            'time_seconds': 500.0,
            'rpm': 2450.0,
            'map_kpa': 85.0,
            'fuel_flow_lph': 42.0,
            'oil_temp_c': 80.0,
            'oil_pressure_kpa': 450.0,
            'cht_1_c': 155.0, 'cht_2_c': 156.0, 'cht_3_c': 154.0, 'cht_4_c': 157.0,
            'egt_1_c': 760.0, 'egt_2_c': 762.0, 'egt_3_c': 758.0, 'egt_4_c': 764.0,
            'altitude_m': 2000.0,
            'airspeed_mps': 45.0,
            'ambient_temp_c': 12.0
        }
        state, latencies, step_feats = self.pipeline.process_packet(nominal_packet)
        self.assertIsNotNone(state)
        self.assertGreaterEqual(state.engine_health, 0.0)
        self.assertLessEqual(state.engine_health, 1.0)
        self.assertIn(state.failsafe_state, ['HEALTHY', 'DEGRADED', 'CRITICAL', 'RTB', 'EMERGENCY'])
        self.assertLess(latencies['total_ms'], 250.0)  # Verify real-time latency target

    def test_live_stream_execution(self):
        source = ReplaySource("scenarios/live_demo/DEMO-01_healthy.yaml")
        df_out = self.pipeline.run_live_stream(source, max_packets=50, print_interval=100)
        self.assertEqual(len(df_out), 50)
        self.assertIn('engine_health', df_out.columns)
        self.assertIn('failsafe_state', df_out.columns)

if __name__ == "__main__":
    unittest.main()
