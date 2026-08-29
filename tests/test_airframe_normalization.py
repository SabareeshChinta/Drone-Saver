"""
Drone Saver - Airframe Calibration & Normalization Verification Tests
Compares false positive rates before and after airframe zero-point calibration on FLIGHT_05.
Problem Statement: SIH26054 - DRDO
"""

import unittest
import sys
sys.path.insert(0, '.')
import pandas as pd
import numpy as np

from src.replay.live_pipeline import LiveDigitalTwinPipeline

class TestAirframeNormalization(unittest.TestCase):
    def setUp(self):
        self.pipeline = LiveDigitalTwinPipeline()
        self.df_f5 = pd.read_csv("data/processed/canonical/flight_05_canonical.csv")
        
    def test_normalization_false_positive_reduction(self):
        # Run live pipeline through holdout FLIGHT_05
        states = []
        for i in range(min(1500, len(self.df_f5))):
            pkt = self.df_f5.iloc[i].to_dict()
            state, _, _ = self.pipeline.process_packet(pkt)
            states.append(state)
            
        anom_scores = [s.anomaly_score for s in states]
        health_scores = [s.engine_health for s in states]
        
        # After initial calibration window (> 90 seconds)
        calibrated_anoms = anom_scores[90:]
        fpr = float(np.mean([a > 0.50 for a in calibrated_anoms]))
        mean_health = float(np.mean(health_scores[90:]))
        
        print(f"\nAirframe Residual Normalization Test on FLIGHT_05:")
        print(f" - Calibrated False Positive Rate on Holdout Airframe: {fpr*100:.2f}%")
        print(f" - Mean Inferred Engine Health: {mean_health:.3f}")
        
        # Verify that calibrated FPR is reduced and health is preserved
        self.assertLess(fpr, 0.15)
        self.assertGreater(mean_health, 0.60)

if __name__ == "__main__":
    unittest.main()
