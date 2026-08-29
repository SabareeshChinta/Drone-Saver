# Drone Saver — Dashboard Metric Provenance & Calculation Audit
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** Exhaustive Provenance & Formula Mapping for All Dashboard Display Metrics  

---

## 1. Metric-by-Metric Calculation & Source Mapping

Every displayed number on the Drone Saver Ground Control Station is derived directly from live telemetry, physics baselines, machine learning inferences, or state-space filters:

| Dashboard Metric | Display Location | Data Source / Engine | Exact Mathematical Calculation / Formula | Output Unit | Update Frequency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`ENGINE HEALTH`** | Header / Top Strip | State-Space Health Decay Filter (`state_tracker.py`) | $H(t) = \text{clip}(H(t-1) \cdot (1-\alpha) + \alpha \cdot (1 - \text{Damage}(t)), 0, 1)$ | $\%$ ($0-100\%$) | 1.0 Hz |
| **`ANOMALY STATE`** | Header / Top Strip | Stage 1 Isolation Forest (`anomaly_detector.py`) | $A(t) = \text{IsolationForest}(\mathbf{r}_{\text{physics}}(t)) \in [0.0, 1.0]$ | `NOMINAL` / `ELEVATED` | 1.0 Hz |
| **`MISSION RISK`** | Header / Mission Panel | Stage 4 Monte Carlo Engine (`mission_reliability.py`) | $\text{Risk}(t) = 1.0 - P(\text{RUL}_{\text{MC}} > t_{\text{remaining}})$ | $\%$ ($0-100\%$) | 1.0 Hz |
| **`INFERENCE LATENCY`**| Header / System Tab | High-Resolution Clock (`time.perf_counter`) | $t_{\text{inf}} = t_{\text{val}} + t_{\text{norm}} + t_{\text{feats}} + t_{\text{S1}} + t_{\text{S2}} + t_{\text{S3}} + t_{\text{S4}}$ | $\text{ms}$ | 1.0 Hz (Live measured) |
| **`RPM`** | Telemetry Table | Transducer ADC / `EFI_STATUS` | Direct physical shaft rotational speed | $\text{RPM}$ | 1.0 Hz |
| **`MANIFOLD PRESS`** | Telemetry Table | Transducer ADC / `EFI_STATUS` | Absolute intake plenum air pressure | $\text{kPa}$ | 1.0 Hz |
| **`FUEL CONSUMPTION`**| Telemetry Table | Transducer ADC / Baseline Fallback | Volumetric fuel delivery rate | $\text{L/h}$ | 1.0 Hz |
| **`OIL PRESSURE`** | Telemetry Table | Transducer ADC / `NAMED_VALUE_FLOAT` | Hydraulic oil pump gallery pressure | $\text{kPa}$ | 1.0 Hz |
| **`OIL TEMPERATURE`** | Telemetry Table | Thermistor ADC / `NAMED_VALUE_FLOAT` | Lubrication oil sump temperature | $^\circ\text{C}$ | 1.0 Hz |
| **`PRESSURE ALTITUDE`**| Telemetry Table | Barometric Altimeter ADC | $h_{\text{ft}} = h_{\text{meters}} \times 3.28084$ | $\text{ft}$ / $\text{m}$ | 1.0 Hz |
| **`INDICATED AIRSPEED`**| Telemetry Table | Pitot-Static Transducer | $v_{\text{kt}} = v_{\text{mps}} \times 1.94384$ | $\text{kt}$ / $\text{m/s}$ | 1.0 Hz |
| **`EGT 1..4`** | Cylinder Array | Type K Thermocouple Probes | Direct exhaust manifold runner gas temperature | $^\circ\text{C}$ | 1.0 Hz |
| **`CHT 1..4`** | Cylinder Array | Type J/K Thermocouple Probes | Direct cylinder head spark plug boss temperature | $^\circ\text{C}$ | 1.0 Hz |
| **`ΔEGT` (Deviation)** | Cylinder Array | Cross-Cylinder Asymmetry Engine | $\delta T_{\text{EGT}, i}(t) = T_{\text{EGT}, i}(t) - \frac{1}{4}\sum_{j=1}^4 T_{\text{EGT}, j}(t)$ | $^\circ\text{C}$ | 1.0 Hz |
| **`FAULT DIAGNOSIS`** | Diagnostics Panel | Stage 2 Gradient-Boosted Trees (`fault_classifier.py`) | $\hat{y}_{\text{fault}} = \arg\max_k P(k \mid \mathbf{x}(t))$ across 10 failure modes | Text Name | 1.0 Hz |
| **`AFFECTED CYLINDER`**| Diagnostics Panel | Spatial Thermal Heatmap Isolator | $\arg\max_i \delta T_i(t)$ when cylinder localized | `Cylinder #1..#4` / `Global` | 1.0 Hz |
| **`CLASSIFICATION CONF`**| Diagnostics Panel | Softmax / Tree Probability Output | $P(\hat{y}_{\text{fault}} \mid \mathbf{x}(t)) \times 100\%$ | $\%$ ($0-100\%$) | 1.0 Hz |
| **`SCENARIO TIME-TO-CRIT`**| RUL Panel | Stage 3 Quantile Regressor (`rul_estimator.py`) | $\text{RUL}_{\text{scenario}} = \hat{f}_{0.50}(\mathbf{x}(t))$ with 90% bounds $[\hat{f}_{0.05}, \hat{f}_{0.95}]$ | $\text{minutes}$ | 1.0 Hz |
| **`FAILSAFE DIRECTIVE`** | Directive Strip | Failsafe State Machine (`failsafe_state_machine.py`) | Evaluates $H(t), P_{\text{mission}}, P_{\text{RTB}}$ against `config/mission_policy.yaml` | `CONTINUE` / `DERATE` / `RTB` / `EMERGENCY` | 1.0 Hz |
| **`EVENT LOG`** | Event Log Box | FSM Transition Logger (`decision_events.csv`) | Timestamped state transitions and threshold breaches | Monospace Log | On event trigger |

---

## 2. Zero Hard-Coded Demonstration Values Policy

* No mock numbers or synthetic animations exist in the frontend UI.
* If a sensor disconnects or emits `NaN`, the UI displays `--` or `N/A` with degraded confidence warnings rather than inventing plausible numbers.
