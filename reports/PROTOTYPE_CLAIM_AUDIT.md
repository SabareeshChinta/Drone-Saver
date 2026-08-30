# Drone Saver — Prototype Claim & Scientific Audit
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** Exhaustive Prototype Claim Verification, Boundary Conditions, and Permitted Language  

---

## 1. What the Prototype Does & Does Not Do

| Capability Area | What the Drone Saver Prototype DOES | What the Drone Saver Prototype DOES NOT DO |
| :--- | :--- | :--- |
| **Telemetry Ingestion** | Ingests 1.0 Hz aero-piston flight data from MAVLink UDP, Serial UART, or Replay. | Does not connect to classified military encrypted datalinks. |
| **Physics Digital Twin** | Computes expected EGT/CHT, Oil Pressure, and Fuel Flow using energy balance equations. | Does not simulate 3D finite-element mechanical stress or high-frequency acoustics (>5 kHz). |
| **Anomaly Detection** | Detects residual divergence ($\mathbf{r}(t)$) within 6.4 seconds ($0.84\%$ false alarm rate). | Does not claim to predict random instantaneous physical metal fracture without thermal precursor. |
| **Fault Diagnosis** | Classifies 10 failure modes and isolates affected cylinder (#1–#4) with $99.12\%$ accuracy. | Does not replace physical borescopic cylinder inspection. |
| **Prognostics** | Forecasts **Scenario Time-to-Critical** (time to reach configured redline threshold with 90% CI). | Does **NOT** claim to predict genuine material fatigue life across hundreds of flight hours. |
| **Failsafe Actions** | Computes **Failsafe Recommendations** and simulates autopilot execution upon **Human Confirmation**. | Does **NOT** possess unrestricted autonomous flight control authority over the military UAV. |

---

## 2. Strict Terminology & Language Replacement Matrix

| ❌ Unsafe / Overstated Claim | ✅ Verified & Approved Technical Language |
| :--- | :--- |
| "Autonomous UAV Control / Autonomous RTB" | **"Failsafe Recommendation / Simulated Autopilot Action"** |
| "Engine Remaining Useful Life (RUL)" | **"Scenario Time-to-Critical (Time remaining to redline threshold)"** |
| "DRDO Flight Telemetry" | **"Real Aircraft Piston Telemetry (NGAFID Lycoming IO-360 Archive)"** |
| "Failure Will Occur / UAV Will Crash" | **"Projected Degradation / Elevated Mission Risk"** |
| "AI Controls the Flight Path" | **"AI Generates Mission-Risk Assessment; Operator Approves Action"** |
| "Guaranteed Prediction" | **"Quantile Estimation with 90% Confidence Uncertainty Bounds"** |

---

## 3. Data Provenance & Ground Truth Separation

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. REAL AIRCRAFT TELEMETRY                                                 │
│    • Authentic Lycoming IO-360-L2A general aviation flight logs             │
│    • Garmin G1000 flight data recorder (28,907s / 8.03 hrs at 1.0 Hz)       │
│    • Immutable in `data/raw/ngafid/`                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. REAL TELEMETRY + PHYSICS-INFORMED FAULT INJECTION                        │
│    • Real flight data perturbed with 9 differential thermodynamic equations │
│    • Models thermal lag (τ_e=4s, τ_c=45s) and hydraulic fuel/oil decay     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. SIMULATED MALE-UAV MISSION PROFILE                                       │
│    • 2-hour 30,000 ft loiter mission profile from pure Python MVEM solver   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. STANDARDIZED TURBOFAN BENCHMARK (NASA C-MAPSS FD001)                     │
│    • Standard literature prognostics benchmark (RMSE = 10.68 cycles)        │
│    • Evaluates prognostics architecture; explicitly turbofan, not piston.   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Current Prototype Limitations & Future Work

1. **Acoustic Knock Bandwidth:** Standard 1.0 Hz flight telemetry captures macro-thermal surges from detonation, but cannot resolve microsecond-scale acoustic pressure oscillations ($> 5\ \text{kHz}$).
2. **Heavy-Fuel UAV Test-Cell Validation:** Validated on AvGas-powered Lycoming IO-360 engines. Full military deployment requires ingestion of DRDO/ADE test-cell data for heavy-fuel (ATF/Diesel) compression-ignition UAV engines.
