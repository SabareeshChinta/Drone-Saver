"""
Drone Saver - Fault Injection Module
Exposes all physics-informed aero-piston failure modes:
- SparkPlugFoulingFault (FT-01)
- FuelInjectorDegradationFault (FT-02)
- BurntExhaustValveFault (FT-03)
- CoolingDegradationFault (FT-04/FT-05)
- LubricationDegradationFault (FT-06)
- IntakeManifoldLeakFault (FT-07)
- SensorDriftFault (FT-08)
- SensorDropoutFault (FT-09)
"""

from src.fault_injection.base import BaseFaultModel
from src.fault_injection.ignition import SparkPlugFoulingFault
from src.fault_injection.fuel import FuelInjectorDegradationFault
from src.fault_injection.valve import BurntExhaustValveFault
from src.fault_injection.thermal import CoolingDegradationFault
from src.fault_injection.lubrication import LubricationDegradationFault
from src.fault_injection.intake import IntakeManifoldLeakFault
from src.fault_injection.sensors import SensorDriftFault, SensorDropoutFault

__all__ = [
    'BaseFaultModel',
    'SparkPlugFoulingFault',
    'FuelInjectorDegradationFault',
    'BurntExhaustValveFault',
    'CoolingDegradationFault',
    'LubricationDegradationFault',
    'IntakeManifoldLeakFault',
    'SensorDriftFault',
    'SensorDropoutFault'
]
