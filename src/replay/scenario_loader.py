"""
Drone Saver - Replay Scenario Loader & Provenance Tracker
Parses YAML scenario specifications and provides deterministic telemetry feeds.
Problem Statement: SIH26054 - DRDO
"""

import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import yaml
import pandas as pd
import numpy as np

from src.fault_injection.ignition import SparkPlugFoulingFault
from src.fault_injection.fuel import FuelInjectorDegradationFault
from src.fault_injection.valve import BurntExhaustValveFault
from src.fault_injection.thermal import CoolingDegradationFault
from src.fault_injection.lubrication import LubricationDegradationFault
from src.fault_injection.intake import IntakeManifoldLeakFault
from src.fault_injection.sensors import SensorDriftFault, SensorDropoutFault

class ScenarioLoader:
    def __init__(self, scenarios_dir=None):
        if scenarios_dir is None:
            scenarios_dir = os.path.join(PROJECT_ROOT, "scenarios")
        self.scenarios_dir = scenarios_dir
        
    def load_scenario(self, scenario_yaml_path):
        if not os.path.isabs(scenario_yaml_path):
            scenario_yaml_path = os.path.join(PROJECT_ROOT, scenario_yaml_path)
            
        if not os.path.exists(scenario_yaml_path):
            raise FileNotFoundError(f"Scenario file not found: {scenario_yaml_path}")
            
        with open(scenario_yaml_path, 'r') as fp:
            spec = yaml.safe_load(fp)
            
        flight_id = spec.get('flight_id', 'FLIGHT_01')
        fault_type = spec.get('fault_type', 'HEALTHY')
        cyl = spec.get('affected_cylinder', 1)
        onset_sec = spec.get('onset_time_sec', 1200)
        severity = spec.get('severity', 1.0)
        duration_sec = spec.get('duration_sec', 600)
        seed = spec.get('random_seed', 42)
        
        # Load baseline healthy flight
        fid_num = flight_id.lower().replace('flight_', '')
        base_file = os.path.join(PROJECT_ROOT, "data", "processed", "flights_healthy", f"flight_{fid_num}_healthy.csv")
        if not os.path.exists(base_file):
            # Fallback to canonical
            base_file = os.path.join(PROJECT_ROOT, "data", "processed", "canonical", f"flight_{fid_num}_canonical.csv")
            
        df_base = pd.read_csv(base_file)
        if 'rpm' in df_base.columns and (df_base['rpm'] > 1800).any():
            first_cruise_idx = df_base[df_base['rpm'] > 1800].index[0]
            if first_cruise_idx > 0:
                df_base = df_base.iloc[first_cruise_idx:].copy().reset_index(drop=True)
                df_base['time_seconds'] = range(len(df_base))
        
        # Apply Fault Injection based on spec
        if fault_type == 'HEALTHY' or fault_type == 'NONE':
            df_feed = df_base.copy()
            df_feed['data_origin'] = "real_telemetry"
            df_feed['fault_active'] = 0
            df_feed['fault_type'] = 'HEALTHY'
            df_feed['fault_cylinder'] = 0
            df_feed['fault_severity'] = 0.0
            df_feed['scenario_rul_sec'] = 99999.0
            meta = {'fault_id': 'NONE', 'fault_name': 'Nominal Healthy Baseline'}
            
        elif fault_type == 'FT-01_SPARK_PLUG_FOULING':
            injector = SparkPlugFoulingFault()
            df_feed, meta = injector.inject(df_base, severity=severity, onset_time_sec=onset_sec, affected_cylinder=cyl, seed=seed)
        elif fault_type == 'FT-02_INJECTOR_CLOGGING':
            injector = FuelInjectorDegradationFault()
            df_feed, meta = injector.inject(df_base, severity=severity, onset_time_sec=onset_sec, duration_sec=duration_sec, affected_cylinder=cyl, seed=seed)
        elif fault_type == 'FT-03_BURNT_EXHAUST_VALVE':
            injector = BurntExhaustValveFault()
            df_feed, meta = injector.inject(df_base, severity=severity, onset_time_sec=onset_sec, duration_sec=duration_sec, affected_cylinder=cyl, seed=seed)
        elif fault_type == 'FT-04_DETONATION':
            injector = CoolingDegradationFault()
            df_feed, meta = injector.inject(df_base, severity=severity, onset_time_sec=onset_sec, affected_cylinder=cyl, mode='detonation', seed=seed)
        elif fault_type == 'FT-05_COOLING_BAFFLE_DEGRADATION':
            injector = CoolingDegradationFault()
            df_feed, meta = injector.inject(df_base, severity=severity, onset_time_sec=onset_sec, duration_sec=duration_sec, affected_cylinder=cyl, mode='baffle', seed=seed)
        elif fault_type == 'FT-06_LUBRICATION_LOSS':
            injector = LubricationDegradationFault()
            df_feed, meta = injector.inject(df_base, severity=severity, onset_time_sec=onset_sec, seed=seed)
        elif fault_type == 'FT-07_INTAKE_MANIFOLD_LEAK':
            injector = IntakeManifoldLeakFault()
            df_feed, meta = injector.inject(df_base, severity=severity, onset_time_sec=onset_sec, affected_cylinder=cyl, seed=seed)
        elif fault_type == 'FT-08_SENSOR_DRIFT':
            injector = SensorDriftFault()
            df_feed, meta = injector.inject(df_base, severity=severity, onset_time_sec=onset_sec, affected_cylinder=cyl, seed=seed)
        elif fault_type == 'FT-09_SENSOR_DROPOUT':
            injector = SensorDropoutFault()
            df_feed, meta = injector.inject(df_base, severity=severity, onset_time_sec=onset_sec, affected_cylinder=cyl, seed=seed)
        else:
            df_feed = df_base.copy()
            meta = {}
            
        return df_feed, spec
