"""
Drone Saver - Live Engine Health State Exporter & API Contract
Provides standard JSON-serializable structured state representations for GCS telemetry APIs.
Problem Statement: SIH26054 - DRDO
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, Optional

@dataclass
class EngineHealthState:
    timestamp: float
    time_seconds: float
    engine_health: float
    anomaly_score: float
    fault: str
    fault_probability: float
    affected_cylinder: int
    scenario_rul_sec: float
    mission_success_probability: float
    p_rtb_safe: float
    
    # Decoupled Engine State, Recommendation & Human-in-the-Loop decision
    engine_state: str                 # HEALTHY, ADVISORY, WARNING, CRITICAL
    failsafe_state: str               # Backwards-compatible alias for engine_state
    mission_recommendation: str       # CONTINUE_MISSION, DERATE_POWER, RETURN_TO_BASE, EMERGENCY_LANDING
    recommendation: str               # Short command alias (e.g. CMD_NAV_RTB)
    operator_decision: str            # MONITORING, PENDING, CONFIRMED, REJECTED
    simulated_action: str             # NONE, SIMULATED_POWER_DERATE, SIMULATED_RTB_ACTION, SIMULATED_EMERGENCY_DIVERSION
    
    # End-to-End Data Provenance Metadata
    data_origin: str                  # REAL_TELEMETRY, REAL_PLUS_INJECTED_FAULT, SIMULATION
    source_dataset: str               # NGAFID, NASA_CMAPSS, JSBSIM_MVEM
    source_flight_id: str             # FLIGHT_01, etc.
    scenario_id: str                  # SIH_FLAGSHIP_DEMO, etc.
    
    sensor_confidences: Dict[str, float]
    
    def to_dict(self) -> dict:
        return asdict(self)
        
    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent)

def export_state_to_json(state: EngineHealthState, output_file: Optional[str] = None) -> str:
    json_str = state.to_json(indent=2)
    if output_file:
        with open(output_file, 'w') as fp:
            fp.write(json_str)
    return json_str
