"""
Drone Saver - Data Provenance Propagation Tests
Verifies that exact data origin, dataset source, and scenario ID
propagate through ingestion and inference without getting lost or obscured.
Problem Statement: SIH26054 - DRDO
"""

import unittest
import sys
sys.path.insert(0, '.')

from src.replay.live_pipeline import LiveDigitalTwinPipeline

class TestDataProvenance(unittest.TestCase):
    def setUp(self):
        self.pipeline = LiveDigitalTwinPipeline()

    def test_provenance_propagation_in_pipeline(self):
        raw_packet = {
            'timestamp': 100.0,
            'time_seconds': 100.0,
            'rpm': 2400.0,
            'map_kpa': 85.0,
            'fuel_flow_lph': 42.0,
            'oil_pressure_kpa': 450.0,
            'oil_temp_c': 80.0,
            'altitude_m': 1000.0,
            'airspeed_mps': 45.0,
            'ambient_temp_c': 15.0,
            'egt_1_c': 760.0,
            'egt_2_c': 762.0,
            'egt_3_c': 758.0,
            'egt_4_c': 764.0,
            'cht_1_c': 155.0,
            'cht_2_c': 156.0,
            'cht_3_c': 154.0,
            'cht_4_c': 158.0,
            'throttle_pct': 78.0,
            # Provenance metadata
            'data_origin': 'REAL_PLUS_INJECTED_FAULT',
            'source_dataset': 'NGAFID',
            'source_flight_id': 'FLIGHT_01',
            'scenario_id': 'SIH_FLAGSHIP_DEMO'
        }

        state, lat, feats = self.pipeline.process_packet(raw_packet)
        self.assertEqual(state.data_origin, 'REAL_PLUS_INJECTED_FAULT')
        self.assertEqual(state.source_dataset, 'NGAFID')
        self.assertEqual(state.source_flight_id, 'FLIGHT_01')
        self.assertEqual(state.scenario_id, 'SIH_FLAGSHIP_DEMO')

if __name__ == "__main__":
    unittest.main()
