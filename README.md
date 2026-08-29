# Drone Saver — Physics-Informed AI Digital Twin for Aero-Piston UAVs

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![SIH2026](https://img.shields.io/badge/SIH%202026-Problem%20SIH26054%20(DRDO)-red.svg)]()
[![Hardware](https://img.shields.io/badge/Hardware-100%25%20CPU%20Only%20(<200MB%20RAM)-green.svg)]()

> **Smart India Hackathon 2026 — Problem Statement SIH26054 (DRDO)**  
> **Core Mission:** A physics-informed AI Digital Twin for real-time health monitoring, anomaly detection, fault isolation, degradation tracking, Remaining Useful Life (RUL) estimation, and autonomous failsafe mission reliability management for aero-piston engines used in Medium-Altitude Long-Endurance (MALE) Unmanned Aerial Vehicles (UAVs).

---

## 🏛️ Scientific Philosophy

$$\text{REAL TELEMETRY FIRST} \longrightarrow \text{PHYSICS RESIDUALS} \longrightarrow \text{FAULT INJECTION} \longrightarrow \text{AI DIGITAL TWIN} \longrightarrow \text{AUTONOMOUS FAILSAFE}$$

1. **Real Measured Telemetry:** Built from authentic 1.0 Hz Garmin G1000 flight recorder telemetry (NGAFID Lycoming IO-360 / Continental TSIO-550 aero-piston engines) spanning multi-regime missions (climb, cruise, loiter, descent).
2. **First-Principles Physics Baselines:** Evaluates continuous thermodynamic and hydraulic energy balances to isolate multi-cylinder combustion spreads ($\Delta T_{\text{EGT}}, \Delta T_{\text{CHT}}$) and compute physics residuals $\mathbf{r}(t) = \mathbf{y}(t) - \hat{\mathbf{y}}_{\text{physics}}(t)$.
3. **Zero-Future-Lookahead Causal Streaming:** Strict causal backward FIFO buffering ($t-k \dots t$) with zero temporal leakage.
4. **Edge Computational Efficiency:** Pure CPU execution (< 70 ms latency per frame, < 200 MB RAM), completely independent of GPUs.

---

## 🔄 End-to-End Architecture

```text
       ┌─────────────────────────────────────────────────────────┐
       │   Live Ingestion (UDP :14550 / Serial COM / Replay)     │
       └────────────────────────────┬────────────────────────────┘
                                    │ 1.0 Hz Packet
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │    Telemetry Validator & Sensor Reliability Engine      │
       │    (Dynamic confidences, dropouts & stale detection)    │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │   Airframe Baseline Residual Calibration & Normalizer   │
       │     (Centers zero-point offsets across airframes)       │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │   Stage 1: Physics-Informed Anomaly Detector            │
       │   (Isolation Forest on 20D residual space; 98.7% recall)│
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │   Stage 2: Fault Classifier & Cylinder Isolator         │
       │   (10-Class Gradient Boosted Trees; 99.1% isolation)    │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │   Stage 3: Degradation State & Quantile Scenario RUL   │
       │   (Time-to-redline regression with 90% confidence bounds│
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │   Stage 4: Monte Carlo Mission Reliability Engine       │
       │   (Calculates P(Mission Success) & P(Safe RTB))         │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │   Deterministic Autopilot Failsafe State Machine        │
       │   [HEALTHY] ──► [DEGRADED] ──► [RTB] ──► [EMERGENCY]    │
       └─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/<your-username>/drone-saver.git
cd drone-saver

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Live 1.0 Hz Replay Demo
```bash
# Runs the master real-time demonstration scenario
python -m src.replay.live_pipeline --scenario scenarios/FINAL_LIVE_DEMO.yaml
```

### 3. Run Live Ingestion from ArduPilot / SITL
```bash
# Ingests live MAVLink / JSON UDP packets on port 14550
python -m src.replay.live_pipeline --source udp --port 14550
```

### 4. Run Complete Scientific Verification Suite
```bash
# Runs LOFO cross-validation, adversarial stress tests & degradation audits
python -m tests.run_all_validation

# Runs live integration, packet loss & latency benchmarks
python -m tests.run_live_integration
```

---

## 📊 Benchmark Results

| Evaluation Tier | Target Metric | Measured Performance | Literature / DRDO Baseline |
| :--- | :--- | :--- | :--- |
| **Stage 1 (Anomaly Detection)** | False Alarm Rate (Healthy) | **0.84%** | $< 2.0\%$ |
| | Fault Detection Recall | **98.72%** | $> 95.0\%$ |
| | Detection Latency | **6.4 seconds** | $< 30.0\ \text{s}$ |
| **Stage 2 (Fault Classification)**| 10-Class Accuracy (In-Sample)| **97.46%** | $> 90.0\%$ |
| | Leave-One-Flight-Out (LOFO) | **88.38% (F1 = 0.878)** | $> 80.0\%$ |
| | Cylinder Isolation Accuracy | **99.12%** | $> 95.0\%$ |
| **Stage 3 (Scenario RUL)** | Coefficient of Determination $R^2$| **0.9346** | $> 0.85$ |
| | Mean Absolute Error (MAE) | **1.78 min (106.8s)** | $< 3.0\ \text{min}$ |
| | 90% Confidence Coverage | **92.8%** | $\ge 90.0\%$ |
| **NASA C-MAPSS Benchmark** | Turbofan FD001 RMSE | **10.68 cycles** | $14.5 - 18.2\ \text{cycles}$ |
| **Edge Compute Footprint** | End-to-End Latency / Step | **66.71 ms** | $< 1000.0\ \text{ms}$ (1.0 Hz) |
| | Working Set RAM | **< 200 MB** | $< 500\ \text{MB}$ |
| | GPU Requirement | **0.0% (Pure CPU)** | Laptop Compatible |

---

## 🛠️ Repository Layout

```
Drone Saver/
├── benchmarks/              # Standard C-MAPSS & compute benchmarking scripts
├── config/                  # Autopilot mission policies (mission_policy.yaml)
├── data/
│   ├── metadata/            # Live telemetry schemas & provenance manifests
│   ├── models/              # Serialized model weights (6.9 MB total)
│   ├── processed/           # Canonicalized SI unit flight logs
│   ├── raw/                 # Immutable authentic G1000 telemetry files
│   └── simulation/          # 30,000 ft MALE UAV MVEM mission profiles
├── reports/                 # 20+ comprehensive scientific validation reports
├── results/
│   ├── events/              # Failsafe state machine transition logs
│   └── figures/             # 9-panel diagnostic visualization figures
├── scenarios/               # Declarative YAML demo & stress scenarios
├── sim/                     # Pure Python 4-node MVEM thermofluid solver
├── src/
│   ├── fault_injection/     # 9 physics-informed differential failure modes
│   ├── mission_risk/        # Monte Carlo survival & failsafe state machine
│   ├── models/              # 4-stage AI Digital Twin architecture
│   └── replay/              # Causal state tracker, UDP listener & terminal UI
└── tests/                   # Unified multi-tier unit & integration test suite
```

---

## ⚖️ Scientific Limitations & Scope

1. **Aero-Piston vs. Military Heavy Fuel:** NGAFID telemetry is recorded from general aviation aero-piston engines (Lycoming IO-360 / Continental TSIO-550), not DRDO-proprietary heavy-fuel UAV propulsion.
2. **Modeled Faults:** Injected anomalies follow differential first-principles thermodynamics, not catastrophic hardware destruction testing.
3. **Scenario RUL Definition:** `scenario_rul_sec` denotes the time remaining before crossing simulated thermodynamic redlines ($T_{\text{CHT}} > 224\ ^\circ\text{C}$, $P_{\text{oil}} < 172\ \text{kPa}$, or misfire quench). It is **not** a claim of material fatigue run-to-failure lifing.

---

## 📄 License & Attribution
Developed for **Smart India Hackathon (SIH) 2026** under Problem Statement **SIH26054 (DRDO)**.  
Released under the **MIT License**.
