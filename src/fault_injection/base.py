"""
Drone Saver - Base Fault Model & Injection Interface
Defines the standard abstract base class for all physics-informed failure modes.
Problem Statement: SIH26054 - DRDO
"""

import abc
import numpy as np
import pandas as pd

class BaseFaultModel(abc.ABC):
    """
    Abstract base class for all physics-informed aero-piston failure modes.
    Every subclass implements the standard inject() interface.
    """
    def __init__(self, fault_id, fault_name, default_target_cyl=1):
        self.fault_id = fault_id
        self.fault_name = fault_name
        self.default_target_cyl = default_target_cyl

    @abc.abstractmethod
    def inject(self, data_df, severity=1.0, onset_time_sec=1200, duration_sec=None, affected_cylinder=None, seed=42):
        """
        Applies physics-grounded perturbation to input telemetry.
        
        Parameters:
            data_df (pd.DataFrame): Canonical healthy telemetry DataFrame.
            severity (float): Dimensionless severity parameter [0.0, 1.0].
            onset_time_sec (float): Flight elapsed time (seconds) when degradation begins.
            duration_sec (float, optional): Duration of transient degradation ramp.
            affected_cylinder (int, optional): Cylinder index (1..4/6) or 0 for global engine.
            seed (int): Random seed for reproducible secondary jitter.
            
        Returns:
            modified_df (pd.DataFrame): Telemetry with injected fault and metadata.
            metadata (dict): Comprehensive provenance and scenario parameters.
        """
        pass
        
    def _prepare_dataframe(self, data_df):
        """Creates a clean copy of the input telemetry with explicit provenance."""
        df = data_df.copy()
        df['data_origin'] = "real_telemetry_with_physics_informed_fault_injection"
        return df
