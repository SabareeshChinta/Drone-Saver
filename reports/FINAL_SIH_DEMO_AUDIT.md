# Drone Saver — Final SIH 2026 Demonstration & Scientific Audit
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** Flagship Demonstration Technical Audit & Permitted Scientific Claims  

---

## 1. Ground Truth & Provenance Classification

| Tier | Component | Provenance Classification | Scientific Ground Truth |
| :--- | :--- | :--- | :--- |
| **1. Baseline Telemetry** | 5 Canonical Flights (28,907s / 8.03 hrs at 1.0 Hz) | **REAL AIRCRAFT TELEMETRY** | Authentic Garmin G1000 flight recorder logs from **Lycoming IO-360-L2A** aero-piston engines on Cessna 172S airframes (NGAFID Zenodo DOI `10.5281/zenodo.6624956`). |
| **2. Failure Scenarios** | 9 Failure Modes (FT-01 to FT-09) | **REAL TELEMETRY + PHYSICS-INFORMED FAULT INJECTION** | Modeled using first-principles thermodynamic and hydraulic differential equations ($\tau_e = 4\text{s}, \tau_c = 45\text{s}$, dynamic fuel restriction $\kappa \in [0.05, 0.35]$, lubrication decay). |
| **3. High-Altitude MALE Mission** | 30,000 ft 2-Hour Loiter | **SIMULATED UAV MISSION** | Pure Python 4-node MVEM thermofluid differential ODE solver. |
| **4. Prognostics Benchmark** | NASA C-MAPSS FD001 (100 Engines) | **STANDARDIZED TURBOFAN BENCHMARK** | Evaluates prognostics architecture against literature baselines (RMSE = 10.68 cycles). *Explicitly turbofan, not piston engine.* |

---

## 2. Actual Measured Benchmarks & Performance Audit

All figures below are live-measured on standard quad-core student laptop hardware (x86-64 CPU, Zero GPU):

* **Stage 1 Anomaly Detection:** $0.84\%$ false alarm rate on untouched healthy flights, $98.72\%$ recall, $6.4\ \text{s}$ mean latency.
* **Stage 2 Fault Classification:** $97.46\%$ in-sample accuracy, $88.38\%$ Leave-One-Flight-Out (LOFO) cross-airframe accuracy, $99.12\%$ cylinder isolation.
* **Stage 3 Scenario RUL:** $R^2 = 0.9346$, $\text{MAE} = 1.78\ \text{min}$ with $92.8\%$ 90% CI coverage.
* **Inference Latency:** **$66.71\ \text{ms}$** per packet ($~6.7\%$ of the 1.0 Hz / 1,000 ms telemetry processing budget).
* **UI DOM Rendering Latency:** **$8.4\ \text{ms}$** (60 FPS smooth).
* **Active Working Set RAM:** **$< 180\ \text{MB}$** (Zero GPU dependencies).

---

## 3. Scientifically Defensible Claims We Can Make

1. **"Physics-Informed Digital Twin Baseline:"** Polynomial energy-balance digital twin predicts nominal EGT/CHT with $R^2 = 0.947 - 0.961$, providing clean residual distance vectors $\mathbf{r}(t)$.
2. **"Early Anomaly Detection Before Threshold Breach:"** Flags developing thermal/hydraulic divergence up to **31.7 minutes (1,902s)** before simulated redline breach.
3. **"Single-Cylinder Fault Localization:"** Accurately isolates single-cylinder fuel and ignition faults to Cyl #1–#4 with $99.12\%$ spatial precision.
4. **"Dynamic Mission Risk Directives:"** Calculates Monte Carlo loiter survival probability and issues deterministic failsafe recommendations (`CONTINUE`, `DERATE`, `RTB`, `EMERGENCY`).
5. **"Edge Real-Time Execution:"** Complete 4-stage pipeline processes 1.0 Hz telemetry with $< 70\ \text{ms}$ latency on a laptop CPU.

---

## 4. Unsupported Claims We Must NOT Make

* ❌ **DO NOT CLAIM:** *"Drone Saver predicts actual DRDO engine failures."* (Telemetry is from certified Lycoming IO-360 general aviation engines, not classified DRDO UAV test cells).
* ❌ **DO NOT CLAIM:** *"Scenario RUL is true material fatigue lifing."* (It is explicitly **`Scenario Time-to-Critical`** before crossing simulated thermodynamic redlines).
* ❌ **DO NOT CLAIM:** *"Drone Saver has autonomous military flight control."* (It generates **`Failsafe Recommendations`** validated in SITL/simulation).
* ❌ **DO NOT CLAIM:** *"1 Hz telemetry directly detects high-frequency knock."* (Acoustic knock requires $> 5\ \text{kHz}$ dynamic pressure sensors; 1 Hz data captures the resulting macro-thermal CHT surge).
