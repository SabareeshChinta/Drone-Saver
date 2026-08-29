# Drone Saver — Hardware-in-the-Loop (HIL) & SITL Validation Report
**Project:** Drone Saver (SIH26054 — DRDO)
**Target Platform:** ArduPilot SITL / PX4 Hardware Companion Computer

---

## HIL Robustness & Network Stress Summary

| Stress Condition | Simulation Method | Digital Twin Behavior | Integrity Status |
| :--- | :--- | :--- | :--- |
| **1% Packet Loss** | Random drop | Zero false alarms; state maintained continuously | **PASS (100% Stable)** |
| **5% Packet Loss** | Random drop | Health score remains within $\pm 0.02$; fallback active | **PASS (100% Stable)** |
| **10% Packet Loss** | Random drop | Degrades sensor confidence; maintains RTB capability | **PASS (100% Stable)** |
| **Burst Loss (10 pkts)** | Consecutive drop | Link flagged as `STALE`; resumes immediately on reconnect | **PASS (100% Stable)** |
| **Holdout Airframe** | `FLIGHT_05` | Normalizer centers offsets; FPR $< 1.0\%$ | **PASS (Calibrated)** |
| **Gaussian Jitter** | $1.5^\circ\text{C}$ noise | 5s causal moving window smooths noise spikes | **PASS (Filter Active)** |