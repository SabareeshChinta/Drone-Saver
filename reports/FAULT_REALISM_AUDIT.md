# Drone Saver — Physics-Informed Fault Realism & Plausibility Audit
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** Exhaustive Physics Audit of 9 Modeled Failure Modes  
**Auditor:** Drone Saver Systems & Propulsion Integrity Team  

---

## 1. Physics Realism Scoring Matrix

Every modeled failure mode is scored against 7 empirical criteria:
1. **Physical Directionality:** Do thermal and hydraulic signals move in accordance with thermodynamic laws?
2. **Temporal Behavior:** Does the transition follow physical thermal inertia ($\tau$) or mechanical progression?
3. **Severity Scaling:** Does increasing severity monotonically widen diagnostic margins?
4. **Cylinder Locality:** Does the fault isolate to the target cylinder without corrupting adjacent healthy runners?
5. **Operating Regime Dependence:** Does the perturbation scale with engine indicated load (RPM, MAP) and ram airspeed?
6. **Signal Plausibility:** Are values strictly within physical boundaries (no impossible pressures/temperatures)?
7. **Literature Backing:** Is the mechanism supported by peer-reviewed SAE/AIAA/IEEE literature or FAA advisories?

---

## 2. Comprehensive Fault Audit Table

| Fault ID | Mode Name | Physical Directionality | Temporal Transition Profile | Severity Scaling | Cylinder Locality | Regime Dependence | Plausibility & Literature Support | Overall Realism Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`FT-01`** | **Spark Plug Fouling** | $T_{\text{EGT}} \uparrow, T_{\text{CHT}} \downarrow, \text{RPM} \downarrow$ | First-order lag ($\tau_e=4\text{s}, \tau_c=45\text{s}$) | Linear $[0.5, 1.0]$ | Isolated to target cylinder | Proportional to RPM / flame angle | Busch (2018), Miljković (2017) | **HIGH CONFIDENCE** |
| **`FT-02`** | **Injector Clogging** | Lean rise $\to$ misfire quench | Multi-stage ramp over $1200\ \text{s}$ | Dynamic blockage $\kappa \in [0.05, 0.35]$ | Isolated to target cylinder | Load-dependent fuel delivery | Heywood (2018), SAE 2017-01-1052 | **HIGH CONFIDENCE** |
| **`FT-03`** | **Burnt Exhaust Valve** | Sinusoidal EGT ripple | Harmonic oscillation ($0.065\ \text{Hz}$) | Leakage magnitude $[0.3, 1.0]$ | Isolated to target cylinder | Proportional to combustion pressure | Savvy Aviation Borescope Logs | **HIGH CONFIDENCE** |
| **`FT-04`** | **Detonation (Knock)** | $T_{\text{CHT}} \Uparrow (+80^\circ\text{C}), T_{\text{EGT}} \downarrow$ | Rapid surge ($\tau = 12\ \text{s}$) | Non-linear $[0.5, 1.0]$ | Isolated to target cylinder | MAP / Cylinder load threshold | Burluka et al. (2020) Comb. Flame | **HIGH CONFIDENCE** |
| **`FT-05`** | **Cooling Baffle Leak** | $T_{\text{CHT}} \uparrow (+35^\circ\text{C}), T_{\text{EGT}} \text{ const}$ | Progressive linear ramp | Airflow restriction $[0.2, 0.9]$ | Rear cylinder localized (#3/#4) | Inversely proportional to airspeed | FAA AC 20-105B | **HIGH CONFIDENCE** |
| **`FT-06`** | **Lubrication Loss** | $P_{\text{oil}} \Downarrow (-40\%), T_{\text{oil}} \Uparrow (+30^\circ\text{C})$ | Hydraulic lag ($\tau_p=10\text{s}, \tau_t=80\text{s}$) | Pressure drop $[0.2, 0.8]$ | Global engine wide | Proportional to pump RPM | Taylor (1985) ICE Theory | **HIGH CONFIDENCE** |
| **`FT-07`** | **Intake Manifold Leak** | $\text{MAP} \uparrow (+12\text{ kPa}), T_{\text{EGT}} \uparrow$ | Exponential lag ($\tau = 15\ \text{s}$) | Vacuum leak $[0.3, 0.8]$ | Single intake runner | Maximum effect at idle vacuum | Miljković (2019) MIPRO | **MEDIUM CONFIDENCE** |
| **`FT-08`** | **Thermocouple Drift** | Linear continuous bias | Monotonic ramp $+0.025^\circ\text{C/s}$ | Continuous duration scaling | Single sensor channel | Invariant to engine load | IEEE Trans. Inst. & Meas. (2021) | **HIGH CONFIDENCE** |
| **`FT-09`** | **Sensor Open Dropout** | Step drop to $0.0^\circ\text{C}$ | Instantaneous step ($< 1\ \text{s}$) | Binary open circuit | Single sensor channel | Invariant to engine load | Garmin G1000 Maintenance Manual | **HIGH CONFIDENCE** |

---

## 3. Realism Strengths & Remaining Uncertainties

### 3.1 Physics Modeling Strengths
* **No Artificial Step Discontinuities:** With the exception of electronic sensor dropout (FT-09), all thermal and mechanical faults exhibit physical dynamic response times ($\tau = 4\text{s}$ to $80\text{s}$) reflecting real heat transfer and hydrodynamic inertia.
* **Cross-Cylinder Thermodynamic Isolation:** Injecting a fuel or ignition fault into Cylinder #2 modifies Cylinder #2's combustion energy without artificially altering adjacent manifold runners.

### 3.2 Key Uncertainties Requiring DRDO Hardware Calibration
1. **Intake Manifold Pressure Pulsations (FT-07):** In high-speed UAV multi-cylinder intake plenums, runner leaks produce high-frequency acoustic pressure flutter ($> 50\ \text{Hz}$) that is low-pass filtered by 1.0 Hz avionics transducers. Confidence is rated **MEDIUM** until high-speed pressure transducer dyno data is available.
2. **Oil Aeration Foam Dynamics (FT-06):** Lubrication pressure collapse is modeled via lumped first-order hydraulic decay, whereas extreme high-g UAV maneuvers may induce transient pump cavitation.
