"""
Drone Saver - Streamlit Operator Dashboard
Lightweight alternative UI for SIH 2026 Jury Demonstration.
Problem Statement: SIH26054 - DRDO
"""

import os
import sys
sys.path.insert(0, '.')
import time
import streamlit as st
import pandas as pd
import numpy as np

from src.replay.live_pipeline import LiveDigitalTwinPipeline
from src.replay.telemetry_listener import ReplaySource

st.set_page_config(
    page_title="Drone Saver — UAV Engine Health Digital Twin",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme styling
st.markdown("""
<style>
    .metric-card { background-color: #131b2e; padding: 12px; border-radius: 8px; border: 1px solid #1f2d4a; text-align: center; }
    .directive-box { padding: 16px; border-radius: 8px; font-weight: 800; font-size: 1.3rem; text-align: center; margin-bottom: 12px; }
    .dir-green { background-color: rgba(16, 185, 129, 0.2); border: 2px solid #10b981; color: #10b981; }
    .dir-yellow { background-color: rgba(245, 158, 11, 0.2); border: 2px solid #f59e0b; color: #f59e0b; }
    .dir-orange { background-color: rgba(249, 115, 22, 0.2); border: 2px solid #f97316; color: #f97316; }
    .dir-red { background-color: rgba(239, 68, 68, 0.3); border: 2px solid #ef4444; color: #ef4444; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Drone Saver — UAV Engine Health Digital Twin")
st.caption("Smart India Hackathon 2026 · Problem SIH26054 (DRDO) · Physics-Informed Real-Time Prognostics")

# Sidebar Controls
st.sidebar.header("🕹️ Demo & Telemetry Controls")
scenario_option = st.sidebar.selectbox(
    "Select Mission Scenario:",
    [
        "scenarios/FINAL_SIH_DEMO.yaml",
        "scenarios/live_demo/DEMO-01_healthy.yaml",
        "scenarios/live_demo/DEMO-02_injector_clogging.yaml",
        "scenarios/live_demo/DEMO-03_cooling_degradation.yaml",
        "scenarios/live_demo/DEMO-04_lubrication_failure.yaml",
        "scenarios/live_demo/DEMO-05_sensor_dropout.yaml",
        "scenarios/live_demo/DEMO-06_compound_failure.yaml"
    ]
)

speed = st.sidebar.slider("Replay Speed Multiplier", 0.5, 10.0, 2.0, step=0.5)
run_btn = st.sidebar.button("▶ Run Interactive Stream", type="primary")

if 'pipeline' not in st.session_state:
    st.session_state.pipeline = LiveDigitalTwinPipeline()

# Main Display Placeholders
directive_ph = st.empty()
stats_cols = st.columns(5)
tel_cols = st.columns(4)
cyl_cols = st.columns(4)
chart_cols = st.columns(2)

if run_btn:
    source = ReplaySource(scenario_option)
    source.connect()
    
    h_history = []
    t_history = []
    
    step = 0
    while True:
        pkt = source.read()
        if pkt is None or step > 1000:
            break
        step += 1
        
        state, lat, feats = st.session_state.pipeline.process_packet(pkt)
        t_curr = state.time_seconds
        h_history.append(state.engine_health)
        t_history.append(t_curr)
        
        # 1. Directive Banner
        if state.failsafe_state == 'HEALTHY':
            directive_ph.markdown('<div class="directive-box dir-green">🟢 CONTINUE MISSION — All Powertrain Thermals Nominal</div>', unsafe_allow_html=True)
        elif state.failsafe_state == 'DEGRADED':
            directive_ph.markdown(f'<div class="directive-box dir-yellow">🟡 DERATE POWER / REDUCE LOITER — Developing {state.fault}</div>', unsafe_allow_html=True)
        elif state.failsafe_state == 'RTB':
            directive_ph.markdown(f'<div class="directive-box dir-orange">🟠 RETURN TO BASE (RTB) — Mission Survival Risk High ({state.mission_success_probability*100:.0f}%)</div>', unsafe_allow_html=True)
        else:
            directive_ph.markdown(f'<div class="directive-box dir-red">🔴 EMERGENCY LANDING — Redline Breach ({state.fault})</div>', unsafe_allow_html=True)
            
        # 2. Top Stats
        stats_cols[0].metric("ENGINE HEALTH", f"{state.engine_health*100:.1f}%")
        stats_cols[1].metric("ANOMALY SCORE", f"{state.anomaly_score:.2f}")
        stats_cols[2].metric("DIAGNOSED FAULT", state.fault)
        stats_cols[3].metric("SCENARIO TIME-TO-CRITICAL", f"{state.scenario_rul_sec/60:.1f} min")
        stats_cols[4].metric("INFERENCE LATENCY", f"{lat['total_ms']:.1f} ms")
        
        # 3. Cylinders
        for i in range(1, 5):
            egt = feats.get(f'egt_{i}_c', 0)
            cht = feats.get(f'cht_{i}_c', 0)
            cyl_cols[i-1].metric(f"CYLINDER #{i}", f"{egt:.0f} °C EGT", f"{cht:.0f} °C CHT")
            
        time.sleep(1.0 / speed)
        
    source.close()
