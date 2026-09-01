# Drone Saver — Physics-Informed AI Digital Twin & Aerospace GCS for Aero-Piston UAVs

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![SIH2026](https://img.shields.io/badge/SIH%202026-Problem%20SIH26054%20(DRDO)-red.svg)](https://www.sih.gov.in/)
[![Hardware](https://img.shields.io/badge/Hardware-100%25%20CPU%20Only%20(<200MB%20RAM)-green.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Smart India Hackathon 2026 — Problem Statement SIH26054 (DRDO)**  
> **Core Objective:** A physics-informed AI Digital Twin and Ground Control Station (GCS) for real-time propulsion health monitoring, thermal anomaly detection, multi-cylinder fault isolation, Scenario Time-to-Critical forecasting, and Human-in-the-Loop failsafe management for aero-piston engines powering Medium-Altitude Long-Endurance (MALE) Unmanned Aerial Vehicles (UAVs).

---

## 🏛️ Engineering & Scientific Philosophy

$$\text{REAL AIRCRAFT TELEMETRY} \longrightarrow \text{PHYSICS DIGITAL TWIN} \longrightarrow \text{THERMODYNAMIC RESIDUALS } \mathbf{r}(t) \longrightarrow \text{4-STAGE AI ENGINE} \longrightarrow \text{HUMAN CONFIRMATION} \longrightarrow \text{AUTOPILOT ACTION}$$

1. **Real Measured Flight Telemetry:** Built from **28,907 seconds (8.03 flight hours)** of authentic 1.0 Hz Garmin G1000 flight data from certified Lycoming IO-360 aero-piston engines (NGAFID Zenodo Archive, CC-BY 4.0).
2. **First-Principles Digital Twin:** Dynamic energy-balance equations compute expected exhaust gas temperatures ($\hat{T}_{\text{EGT}}$), cylinder head thermals ($\hat{T}_{\text{CHT}}$), manifold pressure, and oil gallery pressures.
3. **Physics Residuals $\mathbf{r}(t) = \mathbf{y}(t) - \hat{\mathbf{y}}_{\text{physics}}(t)$:** AI models evaluate physics deviations rather than raw noisy sensors, ensuring cross-flight generalization.
4. **Human-in-the-Loop Safety:** The AI produces **Failsafe Recommendations**; simulated autopilot actions require explicit operator confirmation.
5. **Truthful Scenario RUL:** Prognostics output is strictly labeled **Scenario Time-to-Critical** (minutes remaining before crossing thermodynamic redline thresholds: $T_{\text{CHT}} > 224^\circ\text{C}$ or $P_{\text{oil}} < 172\ \text{kPa}$).
6. **Edge Compute Efficiency:** Pure CPU execution ($74.9\text{ ms}$ latency per frame, $< 200\text{ MB}$ RAM), zero GPU requirement.

---

## 🖥️ Aerospace Ground Control Station (GCS)

The Drone Saver Ground Control Station is accessible via browser at `http://127.0.0.1:8000`:

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DRONE SAVER // GCS-TWIN-01    ENGINE HEALTH: 96%    ANOMALY: NOMINAL    LATENCY: 74.9 ms   [PROVENANCE]│
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [DIRECTIVE STRIP]   STATUS: NOMINAL MONITORING ──► CONTINUE MISSION                                    │
│                     OPERATOR: MONITORING       SIMULATED ACTION: NONE   [CONFIRM] [REJECT]             │
├───────────────────────┬─────────────────────────────────────────────────┬──────────────────────────────┤
│ 1. ENGINE TELEMETRY   │ 2. 4-CYLINDER MONITOR & DIGITAL TWIN            │ 3. FAULT DIAGNOSIS & EVIDENCE│
│  • Engine Speed       │  • CYL 1: EGT 672°C | CHT 137°C | ΔEGT +12.1°C  │  • Diagnosed Fault Code      │
│  • Manifold Pressure  │  • CYL 2: EGT 647°C | CHT 118°C | ΔEGT -13.0°C  │  • Isolated Cylinder (#1-#4) │
│  • Fuel Flow Rate     │  • CYL 3: EGT 667°C | CHT 128°C | ΔEGT +6.8°C   │  • Classifier Confidence     │
│  • Oil Pressure/Temp  │  • CYL 4: EGT 654°C | CHT 127°C | ΔEGT -5.9°C   │  • Physical Evidence Bars    │
│  • Barometric Altitude│ ─────────────────────────────────────────────── │  • Real-Time Event Log       │
│  • Indicated Airspeed │  [PHYSICS BASELINE vs OBSERVED EGT (CYL 2)]     │                              │
│  • Commanded Throttle │  ── Observed (Orange)  ┄ Baseline (Cyan) ┄ Red  │                              │
├───────────────────────┴─────────────────────────────────────────────────┴──────────────────────────────┤
│ 4. SCENARIO TIME-TO-CRITICAL     5. HEALTH TRAJECTORY H(t)              6. MISSION RISK & RELIABILITY  │
│    120 min [98.4 to 150 min]        Continuous State-Space Decay           P(Mission Success): 99%     │
│    (Not material fatigue life)      H(t) = 0.96 (Nominal Cruise)           P(Safe RTB): 99%            │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [ ▶ RUN FLAGSHIP SIH DEMO ]  [SCENARIOS: HEALTHY | INJECTOR | COOLING | OIL | SENSOR]  [SPEED: 1x 2x 5x] │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 End-to-End System Architecture

```text
REAL MEASURED AIRCRAFT TELEMETRY (1.0 Hz)
                 ↓
DYNAMIC SENSOR VALIDATION & AIRFRAME NORMALIZATION
                 ↓
FIRST-PRINCIPLES DIGITAL TWIN BASELINE
                 ↓
PHYSICS RESIDUAL DIVERGENCE r(t)
                 ↓
┌─────────────────────────────────────────────────────────────┐
│ 4-STAGE AI ENGINE                                           │
│  • Stage 1: Isolation Forest Anomaly Detector (< 7s alert)  │
│  • Stage 2: LightGBM 10-Class Fault & Cylinder Isolator     │
│  • Stage 3: Quantile Scenario Time-to-Critical Regressor    │
│  • Stage 4: Monte Carlo Mission Loiter Reliability Model    │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
                 FAILSAFE RECOMMENDATION GENERATED
                               ↓
         OPERATOR GCS CONFIRMATION [ ✓ CONFIRM / ✗ REJECT ]
                               ↓
                    SIMULATED AUTOPILOT ACTION
```

---

## 🛡️ Human-in-the-Loop (HITL) Decision Framework

In military and strategic UAV operations, AI systems must **never** execute non-deterministic airframe flight actions without human command:

| State Variable | Permitted States | Description |
| :--- | :--- | :--- |
| **`engine_state`** | `HEALTHY`, `ADVISORY`, `WARNING`, `CRITICAL` | Physical thermodynamic health condition of the propulsion plant. |
| **`mission_recommendation`** | `CONTINUE_MISSION`, `DERATE_POWER`, `RETURN_TO_BASE`, `EMERGENCY_LANDING` | Advisory generated by the AI Mission Risk Engine. |
| **`operator_decision`** | `MONITORING`, `PENDING`, `CONFIRMED`, `REJECTED` | Human-in-the-loop authorization state. |
| **`simulated_action`** | `NONE`, `SIMULATED_POWER_DERATE`, `SIMULATED_RTB_ACTION`, `SIMULATED_EMERGENCY_DIVERSION` | Simulated autopilot execution occurring **only upon confirmation**. |

All state transitions and operator interactions are recorded in [`results/events/decision_events.csv`](results/events/decision_events.csv).

---

## 📊 Benchmark & Validation Results

| Component / Evaluation Tier | Target Metric | Measured Performance | DRDO / Literature Baseline |
| :--- | :--- | :--- | :--- |
| **Stage 1: Anomaly Detector** | False Alarm Rate (Healthy) | **0.84%** | $< 2.0\%$ |
| | Fault Detection Recall | **98.72%** | $> 95.0\%$ |
| | Detection Time | **6.4 seconds** | $< 30.0\ \text{s}$ |
| **Stage 2: Fault Classifier** | 10-Class Accuracy (In-Sample) | **97.46%** | $> 90.0\%$ |
| | Leave-One-Flight-Out (LOFO) | **88.38% (F1 = 0.878)** | $> 80.0\%$ |
| | Cylinder Isolation Accuracy | **99.12%** | $> 95.0\%$ |
| **Stage 3: Scenario RUL** | Coefficient of Determination $R^2$ | **0.9346** | $> 0.85$ |
| | Mean Absolute Error (MAE) | **1.78 min (106.8 s)** | $< 3.0\ \text{min}$ |
| | 90% Confidence Interval Coverage | **92.8%** | $\ge 90.0\%$ |
| **NASA C-MAPSS Benchmark** | Turbofan FD001 RMSE | **10.68 cycles** | $14.5 - 18.2\ \text{cycles}$ |
| **Edge Compute Footprint** | End-to-End Latency / Step | **74.9 ms** | $< 250.0\ \text{ms}$ |
| | Working Set Memory | **< 200 MB** | $< 500\ \text{MB}$ |
| | GPU Hardware Requirement | **0.0% (Pure CPU)** | Laptop / Embedded Ready |

---

## 🚀 Quick Start Guide

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/SabareeshChinta/Drone-Saver.git
cd Drone-Saver

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Aerospace GCS Server
```bash
# Starts the FastAPI/Uvicorn GCS server at http://127.0.0.1:8000
python src/dashboard/server.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

### 3. Run the Flagship SIH Jury Demonstration
Click **`[ ▶ RUN FLAGSHIP SIH DEMO ]`** on the bottom control bar to observe the full failure sequence:
* **$0 - 60\text{s}$:** Nominal steady cruise ($H = 99\%$, Directive = `CONTINUE_MISSION`).
* **$60\text{s}$:** Progressive Fuel Injector Restriction begins on Cylinder #2.
* **$72\text{s}$:** Early thermal asymmetry detected, Directive shifts to `DERATE_POWER` (65%).
* **$180\text{s}$:** Fault isolated to Cylinder #2 ($91\%$), Scenario RUL counts down, Directive recommends `RETURN_TO_BASE`.
* **Interactive HITL:** Click **`[ ✓ CONFIRM RETURN TO BASE ]`** to execute the simulated autopilot action and observe the event log update.

### 4. Run Automated Test Suites
```bash
# Execute unit and prototype hardening test suite (14 passing tests)
python -m unittest tests/test_human_in_loop.py tests/test_scenario_rul_labeling.py tests/test_data_provenance.py tests/test_decision_logging.py tests/test_demo_reset.py tests/test_dashboard_api.py
```

---

## 🗂️ Repository Structure

```
Drone Saver/
├── dashboard/               # Aerospace GCS web application (HTML, CSS, JS)
├── data/
│   ├── models/              # Serialized ML model weights (Isolation Forest, LightGBM, Quantile GBDT)
│   ├── processed/           # Canonical SI unit aero-engine flight data
│   └── raw/ngafid/          # Immutable authentic G1000 flight telemetry files
├── presentation/            # Official 12-slide SIH PowerPoint pitch deck (.pptx)
├── reports/                 # Comprehensive scientific audit & verification reports
│   ├── PROTOTYPE_HARDENING_REPORT.md   # Final hardening engineering summary
│   ├── HUMAN_IN_LOOP_DESIGN.md         # Failsafe command & confirmation spec
│   ├── DATA_PROVENANCE.md              # 3-tier data provenance tracking
│   ├── SCENARIO_RUL_DEFINITION.md      # Scenario Time-to-Critical mathematical definition
│   ├── PROTOTYPE_CLAIM_AUDIT.md        # Technical claim verification matrix
│   └── SIH_2026_PRESENTATION_DECK.md   # Slide-by-slide rehearsal script
├── results/
│   ├── events/              # Tamper-proof decision_events.csv audit logs
│   └── figures/             # 9-panel diagnostic visualization charts
├── scenarios/               # Declarative YAML flight & fault injection scenarios
├── src/
│   ├── dashboard/           # GCS FastAPI backend server & REST controllers
│   ├── fault_injection/     # 9 physics-informed differential ODE fault modes
│   ├── mission_risk/        # Monte Carlo survival & failsafe state machine
│   ├── models/              # Digital Twin baseline, anomaly detector, classifier, RUL
│   └── replay/              # Causal state tracker, UDP listener & pipeline runner
└── tests/                   # Multi-tier automated unit and integration tests
```

---

## ⚖️ Scientific Scope & Domain Boundaries

1. **Aero-Piston vs. Heavy-Fuel Propulsion:** Baseline flight telemetry is sourced from certified Lycoming IO-360 AvGas engines. Integration with DRDO/ADE heavy-fuel (ATF/Diesel) compression-ignition test-cell data is designated for future production deployment.
2. **Acoustic Knock Resolution:** 1.0 Hz avionics bus telemetry resolves macro-thermal detonation head surges, but does not capture microsecond acoustic pressure oscillation ($> 5\ \text{kHz}$).
3. **Scenario RUL vs. Material Fatigue:** `scenario_rul_sec` denotes the time remaining before crossing simulated thermodynamic redline limits ($T_{\text{CHT}} > 224^\circ\text{C}$ or $P_{\text{oil}} < 172\ \text{kPa}$). It is **not** a claim of structural metal fatigue lifing over thousands of operating hours.

---

## 📄 License & Attribution

Developed for **Smart India Hackathon (SIH) 2026** under Problem Statement **SIH26054 (DRDO)**.  
Released under the **MIT License**.
