"""
Drone Saver - Real-Time Ground Control Station (GCS) Dashboard Server
FastAPI backend driving the Operator Interface via Server-Sent Events (SSE) and REST APIs.
Zero duplicate ML logic - directly streams from the 4-Stage LiveDigitalTwinPipeline.
Problem Statement: SIH26054 - DRDO
"""

import os
import sys
sys.path.insert(0, '.')
import time
import json
import glob
import asyncio
import threading
from typing import Dict, Any, Optional
from collections import deque

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.replay.live_pipeline import LiveDigitalTwinPipeline
from src.replay.telemetry_listener import ReplaySource, UDPSource
from src.replay.state_export import EngineHealthState

app = FastAPI(title="Drone Saver GCS API", version="5.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Global Streaming State Manager
# -------------------------------------------------------------
class DashboardStateManager:
    def __init__(self):
        self.pipeline = LiveDigitalTwinPipeline()
        self.active_scenario = "scenarios/FINAL_SIH_DEMO.yaml"
        self.source_type = "replay"  # "replay" or "udp"
        self.source = None
        
        self.speed_multiplier = 1.0
        self.is_paused = False
        self.is_running = True
        
        self.latest_state: Optional[EngineHealthState] = None
        self.latest_latencies: Dict[str, float] = {}
        self.latest_features: Dict[str, Any] = {}
        
        self.history = deque(maxlen=300)
        self.subscribers = []
        self.lock = threading.Lock()
        
        self.worker_thread = threading.Thread(target=self._run_streaming_loop, daemon=True)
        self.worker_thread.start()
        
    def _init_source(self):
        if self.source_type == "udp":
            self.source = UDPSource(port=14550)
        else:
            self.source = ReplaySource(self.active_scenario)
        self.source.connect()

    def _run_streaming_loop(self):
        self._init_source()
        
        while self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue
                
            raw_pkt = self.source.read()
            if raw_pkt is None:
                # Loop scenario on replay completion
                time.sleep(1.0)
                self._init_source()
                continue
                
            state, lat, feats = self.pipeline.process_packet(raw_pkt)
            
            with self.lock:
                self.latest_state = state
                self.latest_latencies = lat
                self.latest_features = feats
                
                # Append historical point
                hist_item = {
                    'time_seconds': state.time_seconds,
                    'health_score': state.engine_health,
                    'anomaly_score': state.anomaly_score,
                    'fault_prob': state.fault_probability,
                    'scenario_rul_sec': state.scenario_rul_sec,
                    'p_mission_success': state.mission_success_probability,
                    'egt_1': feats.get('egt_1_c', 0.0),
                    'egt_2': feats.get('egt_2_c', 0.0),
                    'egt_3': feats.get('egt_3_c', 0.0),
                    'egt_4': feats.get('egt_4_c', 0.0),
                    'expected_egt_2': feats.get('expected_egt_2_c', 0.0),
                    'cht_1': feats.get('cht_1_c', 0.0),
                    'cht_2': feats.get('cht_2_c', 0.0),
                    'cht_3': feats.get('cht_3_c', 0.0),
                    'cht_4': feats.get('cht_4_c', 0.0),
                    'expected_cht_2': feats.get('expected_cht_2_c', 0.0),
                    'rpm': feats.get('rpm', 0.0),
                    'oil_pressure_kpa': feats.get('oil_pressure_kpa', 0.0),
                    'failsafe_state': state.failsafe_state
                }
                self.history.append(hist_item)
                
            # Sleep according to speed multiplier (1.0 Hz base rate = 1.0 sec)
            delay = 1.0 / max(0.1, self.speed_multiplier)
            time.sleep(delay)

    def set_scenario(self, scenario_path: str):
        with self.lock:
            self.active_scenario = scenario_path
            self.source_type = "replay"
            self.history.clear()
            self.pipeline.normalizer.reset()
            self.pipeline.tracker.reset()
            self.pipeline.failsafe_sm.reset()
            if self.source:
                self.source.close()
            self._init_source()
            print(f"[GCS CONTROLLER] Switched to scenario: {scenario_path}")

    def set_speed(self, speed: float):
        with self.lock:
            self.speed_multiplier = max(0.1, min(20.0, speed))
            print(f"[GCS CONTROLLER] Speed multiplier set to: {self.speed_multiplier}x")

    def toggle_pause(self):
        with self.lock:
            self.is_paused = not self.is_paused
            return self.is_paused

    def reset(self):
        self.set_scenario(self.active_scenario)

state_mgr = DashboardStateManager()

# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------
@app.get("/api/state")
def get_current_state():
    with state_mgr.lock:
        if not state_mgr.latest_state:
            return JSONResponse(status_code=503, content={"status": "INITIALIZING"})
            
        data = {
            "state": state_mgr.latest_state.to_dict(),
            "latencies": state_mgr.latest_latencies,
            "telemetry": {
                "rpm": state_mgr.latest_features.get("rpm", "N/A"),
                "map_kpa": state_mgr.latest_features.get("map_kpa", "N/A"),
                "fuel_flow_lph": state_mgr.latest_features.get("fuel_flow_lph", "N/A"),
                "oil_temp_c": state_mgr.latest_features.get("oil_temp_c", "N/A"),
                "oil_pressure_kpa": state_mgr.latest_features.get("oil_pressure_kpa", "N/A"),
                "altitude_m": state_mgr.latest_features.get("altitude_m", "N/A"),
                "airspeed_mps": state_mgr.latest_features.get("airspeed_mps", "N/A"),
                "ambient_temp_c": state_mgr.latest_features.get("ambient_temp_c", "N/A"),
                "throttle_pct": state_mgr.latest_features.get("throttle_pct", 75.0),
                "egt_1_c": state_mgr.latest_features.get("egt_1_c", "N/A"),
                "egt_2_c": state_mgr.latest_features.get("egt_2_c", "N/A"),
                "egt_3_c": state_mgr.latest_features.get("egt_3_c", "N/A"),
                "egt_4_c": state_mgr.latest_features.get("egt_4_c", "N/A"),
                "cht_1_c": state_mgr.latest_features.get("cht_1_c", "N/A"),
                "cht_2_c": state_mgr.latest_features.get("cht_2_c", "N/A"),
                "cht_3_c": state_mgr.latest_features.get("cht_3_c", "N/A"),
                "cht_4_c": state_mgr.latest_features.get("cht_4_c", "N/A"),
                "egt_spread_c": state_mgr.latest_features.get("egt_spread_c", 0.0),
                "cht_spread_c": state_mgr.latest_features.get("cht_spread_c", 0.0),
                "residual_egt_2_c": state_mgr.latest_features.get("residual_egt_2_c", 0.0),
                "residual_cht_2_c": state_mgr.latest_features.get("residual_cht_2_c", 0.0),
            },
            "control": {
                "active_scenario": os.path.basename(state_mgr.active_scenario),
                "speed_multiplier": state_mgr.speed_multiplier,
                "is_paused": state_mgr.is_paused,
                "provenance": "REAL NGAFID + INJECTED FAULT" if "DEMO" in state_mgr.active_scenario else "REAL NGAFID TELEMETRY"
            }
        }
        return data

@app.get("/api/history")
def get_history():
    with state_mgr.lock:
        return list(state_mgr.history)

@app.get("/api/scenarios")
def list_scenarios():
    scenarios = []
    for p in sorted(glob.glob("scenarios/**/*.yaml", recursive=True) + glob.glob("scenarios/*.yaml")):
        scenarios.append({
            "path": p.replace("\\", "/"),
            "name": os.path.basename(p).replace(".yaml", "").upper()
        })
    return scenarios

@app.post("/api/control/scenario")
def set_scenario_endpoint(payload: Dict[str, str]):
    path = payload.get("scenario_path")
    if path and os.path.exists(path):
        state_mgr.set_scenario(path)
        return {"status": "SUCCESS", "scenario": path}
    return JSONResponse(status_code=400, content={"status": "ERROR", "message": "Invalid scenario path"})

@app.post("/api/control/speed")
def set_speed_endpoint(payload: Dict[str, float]):
    spd = payload.get("speed", 1.0)
    state_mgr.set_speed(float(spd))
    return {"status": "SUCCESS", "speed": state_mgr.speed_multiplier}

@app.post("/api/control/pause")
def toggle_pause_endpoint():
    paused = state_mgr.toggle_pause()
    return {"status": "SUCCESS", "is_paused": paused}

@app.post("/api/control/reset")
def reset_endpoint():
    state_mgr.reset()
    return {"status": "SUCCESS", "message": "Pipeline reset"}

# -------------------------------------------------------------
# SSE Real-Time Streaming Endpoint
# -------------------------------------------------------------
@app.get("/api/stream")
async def sse_stream(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            with state_mgr.lock:
                if state_mgr.latest_state:
                    payload = get_current_state()
                    yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.5 / max(0.1, state_mgr.speed_multiplier))
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Mount static frontend dashboard if directory exists
os.makedirs("dashboard", exist_ok=True)
app.mount("/static", StaticFiles(directory="dashboard"), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join("dashboard", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as fp:
            return HTMLResponse(content=fp.read())
    return HTMLResponse("<h1>Drone Saver GCS Dashboard is initializing...</h1>")

def start_server(host="127.0.0.1", port=8000):
    print(f"\n=======================================================")
    print(f" DRONE SAVER — GCS OPERATOR DASHBOARD SERVER ONLINE    ")
    print(f" URL: http://{host}:{port}                           ")
    print(f"=======================================================\n")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    start_server()
