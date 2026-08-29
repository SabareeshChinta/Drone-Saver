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
    failsafe_state: str
    recommendation: str
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
