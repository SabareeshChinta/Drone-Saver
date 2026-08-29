# Physics-Informed Fault Injection Research & Mathematical Models
**Project:** Drone Saver (SIH 2026 — Problem Statement: SIH26054 — DRDO)  
**Document Type:** Theoretical Literature Review, Diagnostic Signatures, and Mathematical Fault Injection Formulations  

---

## 1. Core Philosophy: Physics-Grounded Fault Injection

Rather than corrupting sensor streams with arbitrary Gaussian noise, **Drone Saver** injects mathematically rigorous, thermodynamically grounded fault profiles validated by experimental general aviation and aero-engine research literature.

$$\mathbf{Measured\ Telemetry}\ [y(t)] = \mathbf{Healthy\ Baseline\ Signal}\ [x_0(t)] + \mathbf{\Delta_{Physics\ Fault}}\ [f(\theta, t, \mathbf{u})] + \mathbf{\epsilon_{\text{sensor}}}(t)$$

Where:
* $x_0(t)$ is the healthy real measured baseline telemetry from the aircraft engine monitor.
* $\mathbf{\Delta_{Physics\ Fault}}$ is the deterministic thermodynamic / mechanical perturbation vector.
* $\theta$ represents physical degradation severity parameters (e.g. nozzle clogging percentage, valve leak orifice area, thermal contact resistance).
* $\mathbf{u}$ is the operational vector (Engine RPM, Manifold Pressure, Airspeed, Outside Air Temp).
* $\mathbf{\epsilon_{\text{sensor}}}$ is the residual transducer noise.

---

## 2. Master Fault Signatures & Literature Matrix

| Fault ID | Failure Mode | Primary Affected Sensors | Perturbation Direction | Progression Dynamic | Target Cylinder | Primary Literature Citation (DOI) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **F-01** | **Spark Plug Fouling / Ignition Drop** | $T_{\text{EGT}}$, $T_{\text{CHT}}$, $\text{RPM}$ | $T_{\text{EGT}} \uparrow$, $T_{\text{CHT}} \downarrow$, $\text{RPM} \downarrow$ | Ramp / Step (5–60 s) | Single cylinder | Busch (2018) *Engines*, Miljković (2017) [10.23919/MIPRO.2017.7973581] |
| **F-02** | **Fuel Injector Clogging (Lean Shift)** | $T_{\text{EGT}}$, $T_{\text{CHT}}$, $\text{FFlow}$ | ROP: $T_{\text{EGT}} \uparrow$, $T_{\text{CHT}} \uparrow$; LOP: $T_{\text{EGT}} \downarrow$, $T_{\text{CHT}} \downarrow$ | Progressive (Hours) | Single cylinder | Yang et al. (2022) [10.5281/zenodo.6624956], Heywood (2018) *ICE Fundamentals* |
| **F-03** | **Burnt / Leaking Exhaust Valve** | $T_{\text{EGT}}$, $T_{\text{CHT}}$ | $T_{\text{EGT}}$ Rhythmic Oscillation ($\pm 25\ ^\circ\text{C}$), $T_{\text{CHT}} \approx \text{const}$ | Slow ramp (10–50 hrs) | Single cylinder | Busch (2016) *Savvy Aviation Valve Analysis*, Miljković (2014) |
| **F-04** | **Detonation (Explosive Knock)** | $T_{\text{CHT}}$, $T_{\text{EGT}}$ | $T_{\text{CHT}} \Uparrow\ (+40\text{ to }+80\ ^\circ\text{C})$, $T_{\text{EGT}} \Downarrow\ (-30\ ^\circ\text{C})$ | Fast exponential ($< 30\ \text{s}$) | Single / Multi | Burluka et al. (2020) *Combustion & Flame*, Busch (2018) |
| **F-05** | **Pre-Ignition (Runaway Hotspot)** | $T_{\text{CHT}}$, $T_{\text{EGT}}$, $\text{RPM}$ | $T_{\text{CHT}} \Uparrow\Uparrow\ (> 250\ ^\circ\text{C})$, $T_{\text{EGT}} \Uparrow$, Catastrophic fail | Ultra-fast ($< 10\ \text{s}$) | Single cylinder | Heywood (2018), SAE Technical Papers on Aero-Piston Knock |
| **F-06** | **Cylinder Cooling Baffle Degradation** | $T_{\text{CHT}}$ | $T_{\text{CHT}} \uparrow\ (+20\text{ to }+45\ ^\circ\text{C})$, $T_{\text{EGT}} \approx \text{const}$ | Steady offset / Ramp | Rear cylinders (#3, #4) | NGAFID Discrepancy Reports (2022), FAA AC 20-105B |
| **F-07** | **Lubrication Loss / Pump Wear** | $P_{\text{oil}}$, $T_{\text{oil}}$, $T_{\text{CHT}}$ | $P_{\text{oil}} \Downarrow\ (-30\text{ to }-70\%)$, $T_{\text{oil}} \Uparrow\ (+25\ ^\circ\text{C})$ | Progressive / Step | All cylinders (Global) | Taylor (1985) *Internal Combustion Engine in Theory and Practice* |
| **F-08** | **Intake Manifold Runner Leak** | $\text{MAP}$, $T_{\text{EGT}}$, $T_{\text{CHT}}$ | $\text{MAP} \uparrow$ (at idle), $T_{\text{EGT}} \uparrow$ (lean at idle) | Steady leak | Single cylinder | Miljković (2019) *MIPRO Proceedings* |
| **F-09** | **Turbocharger Wastegate Sticking** | $\text{MAP}$, $\text{TIT}$, $\text{RPM}$ | $\text{MAP} \downarrow$ (underboost) / $\text{MAP} \uparrow$ (overboost) | Regime-dependent | Global engine | Rotax 914 Maintenance Manual, Austro AE300 FADEC Specs |
| **F-10** | **Thermocouple Sensor Drift** | $T_{\text{EGT}}$ or $T_{\text{CHT}}$ | Linear offset $+ \alpha \cdot t$ ($+15\text{ to }+50\ ^\circ\text{C}$) | Linear drift | Single sensor channel | IEEE Trans. on Instrumentation & Measurement (2021) |
| **F-11** | **Thermocouple Open-Circuit Dropout** | $T_{\text{EGT}}$ or $T_{\text{CHT}}$ | Abrupt step to $0\ ^\circ\text{C}$, $-99\ ^\circ\text{C}$, or full-scale ($1370\ ^\circ\text{C}$) | Step function | Single sensor channel | NGAFID Sensor Data Quality Assessment (2022) |
| **F-12** | **Ignition EMI High-Frequency Noise** | $T_{\text{EGT}}$, $T_{\text{CHT}}$, $\text{RPM}$ | High variance Gaussian noise ($\sigma = 15\ ^\circ\text{C}$) | Continuous | Random channels | FAA General Aviation Avionics EMI Guidelines |
| **F-13** | **Piston Ring Blow-By / Compression Loss** | $P_{\text{oil}}$, $T_{\text{oil}}$, $\text{Power}$ | $P_{\text{crankcase}} \uparrow$, $T_{\text{oil}} \uparrow$, $\text{RPM} \downarrow\ (-3\text{ to }-8\%)$ | Long-term degradation | Single cylinder | SAE International Paper 2017-01-1052 |
| **F-14** | **Magneto Timing Retardation** | $T_{\text{EGT}}$, $T_{\text{CHT}}$, $\text{RPM}$ | $T_{\text{EGT}} \uparrow\ (+35\ ^\circ\text{C})$, $T_{\text{CHT}} \downarrow\ (-15\ ^\circ\text{C})$ | Synchronous offset | All cylinders (Global) | Busch (2018) *Manifestations of Ignition Timing Errors* |
| **F-15** | **Valve Lifter Spalling / Cam Wear** | $\text{Vibration}$, $\text{Power}$, $T_{\text{EGT}}$ | Mechanical vibration $\uparrow$, $T_{\text{EGT}} \downarrow$ (low charge) | Progressive wear | Single cylinder | IEEE DataPort IC Engine Vibration Dataset (2021) |

---

## 3. Mathematical Physics Formulations for Top 6 Fault Modes

### 3.1 Fault Mode 1: Spark Plug Fouling / Single Ignition Failure
* **Physical Mechanism:** Standard aero-piston engines utilize dual spark plugs per cylinder for redundancy and rapid flame propagation. If one spark plug fouls (e.g. lead/carbon deposits), flame front velocity is halved. The combustion duration doubles, shifting the angle of peak cylinder pressure ($\theta_{P_{\max}}$) later into the expansion stroke. Consequently, less heat transfers into the cylinder head ($T_{\text{CHT}} \downarrow$) while unburned gases continue burning as the exhaust valve opens ($T_{\text{EGT}} \uparrow$).
* **Governing Mathematical Formulation:**
  $$\Delta T_{\text{EGT}, i}(t) = \delta_{\text{plug}}(t) \cdot \left[ +25.0 + 15.0 \cdot \left(\frac{\text{RPM}(t)}{2500}\right) \right] \cdot \left(1 - e^{-(t - t_0)/\tau_{\text{egt}}}\right)$$
  $$\Delta T_{\text{CHT}, i}(t) = -\delta_{\text{plug}}(t) \cdot \left[ 12.0 + 8.0 \cdot \left(\frac{\text{MAP}(t)}{25.0}\right) \right] \cdot \left(1 - e^{-(t - t_0)/\tau_{\text{cht}}}\right)$$
  $$\Delta \text{RPM}(t) = -\delta_{\text{plug}}(t) \cdot \left[ 30.0 + 20.0 \cdot \eta_{\text{power}} \right]$$
  Where $\delta_{\text{plug}}(t) \in [0, 1]$ is the fault activation magnitude, $\tau_{\text{egt}} \approx 4.0\ \text{s}$, and $\tau_{\text{cht}} \approx 45.0\ \text{s}$ (thermal mass time constant).

### 3.2 Fault Mode 2: Fuel Injector Clogging / Lean Imbalance
* **Physical Mechanism:** A restricted fuel injector nozzle decreases the local equivalence ratio $\phi_i = (\text{Fuel}/\text{Air})_i / (\text{Fuel}/\text{Air})_{\text{stoich}}$. In standard Rich-of-Peak (ROP) operation ($\phi \approx 1.15$), a lean shift increases combustion temperature toward stoichiometric ($\phi = 1.0$), driving both $T_{\text{EGT}}$ and $T_{\text{CHT}}$ upward. If the restriction exceeds critical starvation, Lean-of-Peak misfire occurs, causing $T_{\text{EGT}}$ to plummet sharply.
* **Governing Mathematical Formulation:**
  Let $\kappa_i(t) \in [0, 0.40]$ represent the percentage nozzle blockage:
  $$\Delta \dot{m}_{f, i}(t) = -\kappa_i(t) \cdot \dot{m}_{f, 0}(t)$$
  $$\Delta T_{\text{EGT}, i}(t) = \begin{cases} +80.0 \cdot \left(\frac{\kappa_i(t)}{0.20}\right) \cdot \left(1 - e^{-(t - t_0)/\tau_{\text{egt}}}\right), & \kappa_i \le 0.20\ (\text{Lean toward peak}) \\ +80.0 - 250.0 \cdot \left(\frac{\kappa_i - 0.20}{0.20}\right), & \kappa_i > 0.20\ (\text{Lean misfire quench}) \end{cases}$$
  $$\Delta T_{\text{CHT}, i}(t) = +25.0 \cdot \left(\frac{\kappa_i(t)}{0.20}\right) \cdot \left(1 - e^{-(t - t_0)/\tau_{\text{cht}}}\right)$$

### 3.3 Fault Mode 3: Burnt / Leaking Exhaust Valve
* **Physical Mechanism:** When an exhaust valve develops a thermal hotspot or guide misalignment, sealing integrity fails during peak combustion. Superheated burning combustion gas ($> 1800\ ^\circ\text{C}$) leaks past the valve seat into the exhaust runner. As the valve slowly rotates in its guide (approx. 1 revolution every 10–30 seconds of engine operation), the leak gap periodically expands and contracts, producing a signature low-frequency sinusoidal oscillation in EGT accompanied by a slow long-term temperature rise.
* **Governing Mathematical Formulation:**
  $$\Delta T_{\text{EGT}, i}(t) = \gamma_{\text{valve}}(t) \cdot \left[ \Delta T_{\text{mean}} + A_{\text{rot}} \sin\left(2\pi f_{\text{rot}} t + \phi_0\right) \right] \cdot \left(1 - e^{-(t - t_0)/\tau_{\text{egt}}}\right)$$
  Where:
  * $\Delta T_{\text{mean}} = 35.0\ ^\circ\text{C}$ ($63\ ^\circ\text{F}$)
  * $A_{\text{rot}} = 18.0\ ^\circ\text{C}$ (Oscillation amplitude)
  * $f_{\text{rot}} = \frac{\text{RPM}(t)}{2 \times 60 \times N_{\text{rot\_ratio}}} \approx 0.05 - 0.10\ \text{Hz}$ (1 cycle per 10–20 seconds)
  * $\Delta T_{\text{CHT}, i}(t) \approx 0$ (CHT is largely unaffected because the leaking gas escapes before heating the head).

### 3.4 Fault Mode 4: Destructive Detonation (Knock)
* **Physical Mechanism:** Detonation occurs when the end-gas ahead of the flame front spontaneously auto-ignites. The resulting sonic shockwaves ($> 1500\ \text{m/s}$) scour away the microscopic insulating stagnant boundary layer of gas protecting the piston crown and combustion chamber walls. Heat transfer coefficient ($h_{\text{cyl}}$) increases by $300\%–500\%$. Heat rushes into the cylinder head ($T_{\text{CHT}} \Uparrow$), while less heat remains in the expanding gas exiting the exhaust runner ($T_{\text{EGT}} \Downarrow$).
* **Governing Mathematical Formulation:**
  $$\Delta T_{\text{CHT}, i}(t) = +\Gamma_{\text{det}} \cdot \left[ 55.0 + 35.0 \cdot \left(\frac{\text{MAP}(t)}{28.0}\right) \right] \cdot \left(1 - e^{-(t - t_0)/\tau_{\text{det\_therm}}}\right)$$
  $$\Delta T_{\text{EGT}, i}(t) = -\Gamma_{\text{det}} \cdot \left[ 30.0 + 15.0 \cdot \left(\frac{\text{RPM}(t)}{2500}\right) \right] \cdot \left(1 - e^{-(t - t_0)/\tau_{\text{egt}}}\right)$$
  $$\text{where}\ \tau_{\text{det\_therm}} \approx 12.0\ \text{s}\ (\text{Extremely rapid thermal surge}).$$
  *Diagnostic Criterion:* Rapid positive derivative $\frac{dT_{\text{CHT}}}{dt} > 0.8\ ^\circ\text{C/s}$ concurrent with negative $\Delta T_{\text{EGT}}$ is a $100\%$ unique physical indicator of detonation.

### 3.5 Fault Mode 5: Cylinder Cooling Baffle Degradation
* **Physical Mechanism:** Air-cooled piston aircraft engines rely on flexible silicone/aluminum baffles to force ram air evenly through cylinder fins. Warped or detached baffles cause cooling air starvation on the rear cylinders (#3 and #4 in 4-cylinder engines; #5 and #6 in 6-cylinder engines). CHT rises in proportion to engine power and inversely with airspeed, while EGT remains perfectly normal.
* **Governing Mathematical Formulation:**
  $$\Delta T_{\text{CHT}, 3}(t) = +\eta_{\text{baffle}} \cdot \left[ 28.0 \cdot \left(\frac{\text{MAP}(t) \cdot \text{RPM}(t)}{25.0 \times 2400}\right) - 10.0 \cdot \left(\frac{\text{IAS}(t)}{100.0}\right) \right]$$
  $$\Delta T_{\text{EGT}, 3}(t) = 0.0\ ^\circ\text{C}\ (\text{Combustion chemistry is unchanged}).$$

### 3.6 Fault Mode 6: Lubrication Degradation / Oil Pressure Loss
* **Physical Mechanism:** Oil pump relief valve sticking, oil line leakage, or severe oil aeration causes gallery pressure drop and reduced oil heat scavenging from crankpin bearings and cylinder skirts.
* **Governing Mathematical Formulation:**
  $$\Delta P_{\text{oil}}(t) = -\psi_{\text{oil}}(t) \cdot P_{\text{oil}, 0}(t)$$
  $$\Delta T_{\text{oil}}(t) = +\psi_{\text{oil}}(t) \cdot \left[ 30.0 + 15.0 \cdot \left(\frac{\text{RPM}(t)}{2400}\right) \right] \cdot \left(1 - e^{-(t - t_0)/\tau_{\text{oil\_therm}}}\right)$$
  Where $\tau_{\text{oil\_therm}} \approx 60.0\ \text{s}$ and $\psi_{\text{oil}}(t) \in [0.2, 0.8]$ represents lubrication loss severity.

---

## 4. Implementation Validation Workflow

```
+---------------------------+
| Real Healthy Flight File  |
| (e.g. c172_healthy_01.csv)|
+---------------------------+
              |
              v
+-------------------------------------------------------------------------------+
|                      PHYSICS FAULT INJECTION ENGINE                           |
|  1. Select fault mode (e.g. F-03: Burnt Exhaust Valve on Cylinder #3)         |
|  2. Select fault onset timestamp (e.g. t_start = 1200 s, progressive ramp)    |
|  3. Compute continuous thermodynamic perturbation vectors \Delta T_EGT, etc.  |
|  4. Add perturbation to raw sensor array while enforcing thermodynamic bounds |
+-------------------------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------------------------+
|                     FAULT-AUGMENTED TELEMETRY STREAM                          |
|  - Retains authentic flight dynamics, turbulence, pilot throttle adjustments  |
|  - Contains mathematically rigorous, literature-backed fault signatures       |
|  - Fully labeled with exact fault ground truth (Fault ID, Severity, RUL)      |
+-------------------------------------------------------------------------------+
```
