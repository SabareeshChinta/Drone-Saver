# Drone Saver — Scenario Time-to-Critical Definition & Lifing Scope
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** Mathematical Definition of Scenario RUL vs. Material Fatigue Lifing  

---

## 1. Mathematical Definition: Scenario Time-to-Critical

In the Drone Saver aero-piston digital twin, the prognostics metric is strictly defined as **`Scenario Time-to-Critical`**:

$$\text{RUL}_{\text{scenario}}(t) = \inf \left\{ \Delta t \ge 0 \;\middle|\; T_{\text{CHT}}(t + \Delta t) \ge T_{\text{redline}} \;\lor\; P_{\text{oil}}(t + \Delta t) \le P_{\text{redline}} \right\}$$

Where:
* $T_{\text{redline}} = 224^\circ\text{C}$ ($435^\circ\text{F}$) for Cylinder Head Temperature (FAA Lycoming Operating Limits).
* $P_{\text{redline}} = 172\ \text{kPa}$ ($25\ \text{PSI}$) for Engine Oil Gallery Pressure.

### What Scenario Time-to-Critical Means:
* It estimates the **in-flight time remaining before a developing defect (e.g. leaking fuel injector or collapsing oil pump) crosses thermodynamic safety redlines**.
* It provides the GCS flight commander with an actionable countdown to decide between continuing power derating or initiating Return-to-Base (RTB).

### What Scenario Time-to-Critical DOES NOT Mean:
* It is **not** long-term material fatigue life (e.g. cumulative cycle fatigue on crankshafts or turbine blades over 2,000 operating hours).
* It does **not** represent time to physical structural disintegration.

---

## 2. Separation from NASA C-MAPSS Turbofan Benchmark

To prevent technical confusion between propulsion architectures:

| Parameter | Drone Saver Piston Twin | NASA C-MAPSS FD001 Benchmark |
| :--- | :--- | :--- |
| **Engine Architecture** | 4-Cylinder Horizontally Opposed Aero-Piston (Lycoming IO-360) | High-Bypass Commercial Turbofan Engine |
| **Prognostics Target** | **Scenario Time-to-Critical (Minutes to Thermal Redline)** | **Run-to-Failure Lifing (Remaining Flight Cycles)** |
| **Degradation Mode** | Real-time thermal asymmetry & hydraulic decay | Blade tip rub, high-pressure turbine erosion |
| **Validation Score** | $R^2 = 0.9346$, $\text{MAE} = 1.78\ \text{min}$ | $\text{RMSE} = 10.68\ \text{cycles}$ |

---

## 3. Mandatory UI Disclaimer

All GCS screens and technical reports display the explicit disclaimer:
> *"Scenario time remaining before reaching configured redline threshold. Not material fatigue life."*
