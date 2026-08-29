# Drone Saver — Phase 3 Implementation & Architecture Audit
**Project:** Drone Saver (SIH26054 — DRDO)  
**Phase:** Phase 3 Pre-Execution System Audit  
**Date:** August 2026  

---

## 1. System Inventory & Component Mapping

| Subsystem | Source Path | Artifact / Model Output | Role in Digital Twin |
| :--- | :--- | :--- | :--- |
| **Data Ingestion & SI Canonicalization** | `src/canonicalize_ngafid.py` | `data/processed/canonical/` | 1.0 Hz SI unit mapping, missingness filtering, timestamp indexing. |
| **Healthy Physics Baseline Regressor** | `src/healthy_baseline.py` | 2nd-order polynomial fits | Predicts expected $T_{\text{EGT}}, T_{\text{CHT}}, P_{\text{oil}}, \dot{m}_f$ from RPM, MAP, OAT, Altitude. |
| **Feature Extraction Engine** | `src/features.py` | `data/processed/features/` | Multi-cylinder spreads ($\Delta T_{\text{EGT}}, \Delta T_{\text{CHT}}$), thermal derivatives, dimensionless indices. |
| **Physics Fault Injection Suite** | `src/fault_injection/` | `data/injected/` (45 files) | 9 modular failure modes with first-principles thermodynamic and hydraulic profiles. |
| **Stage 1 Anomaly Detector** | `src/models/anomaly_detector.py` | `data/models/anomaly_detector.pkl` | Isolation Forest on 20-dimensional physics residual space; outputs Health Index $\mathcal{H}(t)$. |
| **Stage 2 Fault Classifier** | `src/models/fault_classifier.py` | `data/models/fault_classifier.pkl` | Multi-class gradient boosted trees (10 classes) + cylinder isolation classifier. |
| **Stage 3 Degradation & RUL Regressor** | `src/models/rul_estimator.py` | `data/models/rul_estimator.pkl` | Quantile gradient-boosted trees predicting median scenario RUL and 90% confidence intervals. |
| **Stage 4 Mission Reliability Engine** | `src/mission_risk/mission_reliability.py` | Dynamic risk & abort engine | Monte Carlo loiter survival probability $P(\text{Mission Success})$ and failsafe directives. |
| **Simulation Foundations** | `sim/mvem_engine_twin.py`, `sim/jsbsim_mission_runner.py` | `data/simulation/` | 4-node thermofluid differential solver (`solve_ivp`) & 30,000 ft MALE UAV mission profile. |

---

## 2. Rigorous Data Leakage & Methodology Audit

We conducted an exhaustive audit of feature engineering and validation pipelines across 6 potential leakage vectors:

### 2.1 Absolute Time Dependency (`time_seconds`)
* **Finding:** In Phase 2, `time_seconds` was inadvertently included in the general numerical feature list.
* **Risk:** A tree model could split on absolute timestamps (e.g. `time > 1200`) rather than purely physical thermal deviations.
* **Remediation Action:** Explicitly blacklist `time_seconds`, `timestamp`, `onset_time_sec`, and scenario metadata from all training and inference feature sets. All features must be strictly physical, causal, and time-invariant.

### 2.2 Future Lookahead in Feature Extraction
* **Finding:** Rolling statistics in `features.py` originally used `center=True` for offline exploratory smoothing.
* **Risk:** Centered rolling windows peek 2 seconds into the future, which is non-causal during real-time streaming.
* **Remediation Action:** For the real-time replay engine (`src/replay/`), implement a stateful causal buffer (`state_tracker.py`) that computes backward-only exponential moving averages ($t-k \dots t$).

### 2.3 Train/Test Airframe Generalization
* **Finding:** Random row splitting creates severe data leakage.
* **Remediation Action:** Maintain strict Leave-One-Flight-Out (LOFO) airframe holdouts and severity holdouts. Scalers and healthy baselines are fitted strictly on training airframes.

---

## 3. Assumptions & Terminology Clarifications

1. **Scenario RUL vs Genuine RUL:**
   * In all injected scenarios, the target is explicitly designated `scenario_rul_sec` (time remaining before reaching simulated physical redlines).
   * It is never displayed or documented as real run-to-failure fatigue data.
2. **Deterministic Reproducibility:**
   * All scenarios and jitter models use fixed, documented pseudo-random seeds (`seed=42`).
