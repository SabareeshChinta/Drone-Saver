"""
Drone Saver - Unit Tests for Telemetry Listener & Sources
Problem Statement: SIH26054 - DRDO
"""

import unittest
import os
import sys
sys.path.insert(0, '.')

from src.replay.telemetry_listener import ReplaySource, UDPSource

class TestTelemetryListener(unittest.TestCase):
    def test_replay_source_loading(self):
        source = ReplaySource("scenarios/FINAL_LIVE_DEMO.yaml")
        source.connect()
        self.assertIsNotNone(source.df_feed)
        self.assertGreater(len(source.df_feed), 100)
        
        pkt1 = source.read()
        self.assertIsInstance(pkt1, dict)
        self.assertIn('time_seconds', pkt1)
        self.assertIn('rpm', pkt1)
        source.close()
        self.assertIsNone(source.df_feed)

    def test_udp_source_socket_creation(self):
        source = UDPSource(host="127.0.0.1", port=14599)
        source.connect()
        self.assertIsNotNone(source.sock)
        # Non-blocking read with short timeout
        pkt = source.read(timeout_sec=0.01)
        self.assertIsNone(pkt)  # Expect timeout when no packets sent
        source.close()
        self.assertIsNone(source.sock)

if __name__ == "__main__":
    unittest.main()
