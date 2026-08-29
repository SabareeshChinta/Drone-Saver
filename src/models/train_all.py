"""
Drone Saver - Unified Model Training & Serialization Script
Trains and serializes all 3 AI models with standard module provenance:
1. Anomaly Detector
2. Fault Classifier & Cylinder Isolator
3. RUL Regressor & Quantile Forecaster
Problem Statement: SIH26054 - DRDO
"""

import os
import sys
sys.path.insert(0, '.')
import pickle
import pandas as pd
import numpy as np

from src.models.anomaly_detector import train_and_save_anomaly_model
from src.models.fault_classifier import train_and_evaluate_classifier
from src.models.rul_estimator import train_and_save_rul_model

def train_all():
    print("Training Stage 1: Anomaly Detector...")
    train_and_save_anomaly_model()
    
    print("\nTraining Stage 2: Fault Classifier...")
    train_and_evaluate_classifier()
    
    print("\nTraining Stage 3: RUL Estimator...")
    train_and_save_rul_model()
    
    print("\nAll Digital Twin AI Models Successfully Trained & Serialized to data/models/!")

if __name__ == "__main__":
    train_all()
