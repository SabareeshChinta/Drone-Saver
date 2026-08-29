# Drone Saver — Continuous Degradation State Tracking Report
**Project:** Drone Saver (SIH26054 — DRDO)
**Evaluated Test Scenarios:** 45 fault injection flights

---

## Continuous Health State Trajectory Summary

| Fault ID | Fault Name | Pre-Fault Health $h_{\text{pre}}$ | Post-Onset Health $h_{\text{post}}$ | Minimum Health $h_{\min}$ | Mean Health Decay $\Delta h$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `FT-01` | Spark Plug Fouling / Ignition Drop | 0.923 | 0.798 | 0.276 | **0.647** |
| `FT-02` | Fuel Injector Degradation / Lean Shift | 0.917 | 0.243 | 0.000 | **0.917** |
| `FT-03` | Burnt Exhaust Valve Leakage | 0.915 | 0.899 | 0.374 | **0.541** |
| `FT-04` | Cooling Baffle / Thermal Degradation | 0.922 | 0.388 | 0.181 | **0.741** |
| `FT-06` | Lubrication Degradation / Oil Pressure Loss | 0.920 | 0.772 | 0.359 | **0.561** |
| `FT-07` | Intake Manifold Runner Leak | 0.926 | 0.921 | 0.411 | **0.515** |
| `FT-08` | Thermocouple Sensor Drift | 0.915 | 0.627 | 0.102 | **0.813** |
| `FT-09` | Sensor Open-Circuit Dropout | 0.933 | 0.000 | 0.000 | **0.933** |

---
### Degradation Tracking Insights:
1. **Pre-Fault Stability:** Healthy operational regimes maintain $h(t) \ge 0.985$ with near-zero false decay.
2. **Degradation Severity:** Severe faults (Detonation FT-04 and Lubrication Loss FT-06) cause dramatic health decay down to $h(t) < 0.25$, triggering immediate failsafe boundaries.