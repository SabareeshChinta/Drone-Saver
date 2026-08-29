"""
Drone Saver - Unit Tests for Telemetry Packet Validation & Sensor Reliability
Problem Statement: SIH26054 - DRDO
"""

import unittest
import sys
sys.path.insert(0, '.')

from src.replay.telemetry_validator import TelemetryPacketValidator

class TestPacketValidation(unittest.TestCase):
    def setUp(self):
        self.validator = TelemetryPacketValidator()
        self.nominal_packet = {
            'time_seconds': 100.0,
            'rpm': 2400.0,
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

    def test_nominal_packet_validity(self):
        valid, status, confs, notes = self.validator.validate_packet(self.nominal_packet)
        self.assertEqual(status, "VALID")
        self.assertEqual(len(notes), 0)
        self.assertEqual(confs['rpm'], 1.0)
        self.assertEqual(confs['egt_1_c'], 1.0)

    def test_out_of_bounds_detection(self):
        bad_pkt = self.nominal_packet.copy()
        bad_pkt['rpm'] = 9999.0  # Impossible RPM
        valid, status, confs, notes = self.validator.validate_packet(bad_pkt)
        self.assertEqual(status, "PARTIAL")
        self.assertLess(confs['rpm'], 1.0)
        self.assertTrue(any("breached physical bounds" in n for n in notes))

    def test_stale_packet_gap_detection(self):
        # First packet
        self.validator.validate_packet(self.nominal_packet)
        # Stale jump in time (+10 seconds)
        stale_pkt = self.nominal_packet.copy()
        stale_pkt['time_seconds'] = 110.0
        valid, status, confs, notes = self.validator.validate_packet(stale_pkt)
        self.assertEqual(status, "STALE")
        self.assertTrue(any("stale link" in n for n in notes))

    def test_flatline_sensor_freeze(self):
        # Send 35 identical packets
        for t in range(35):
            pkt = self.nominal_packet.copy()
            pkt['time_seconds'] = float(t)
            valid, status, confs, notes = self.validator.validate_packet(pkt)
        # Freeze counter should trigger warning
        self.assertTrue(any("frozen for >" in n for n in notes))

if __name__ == "__main__":
    unittest.main()
