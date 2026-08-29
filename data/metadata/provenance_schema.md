# Drone Saver — Provenance & Telemetry Data Lineage Schema
**Project:** Drone Saver (SIH 2026 — Problem Statement: SIH26054 — DRDO)  
**Document Type:** Scientific Provenance, Data Lineage, and Origin Tracking Standards  

---

## 1. Non-Negotiable Data Origin Taxonomy

To prevent data contamination and maintain strict scientific reproducibility, every file and observation in the Drone Saver project is explicitly labeled with its `data_origin`:

| Origin Code | Full Description | Storage Directory | Permitted Usage | Prohibited Usage |
| :--- | :--- | :--- | :--- | :--- |
| **`REAL`** | Uncorrupted, authentic telemetry recorded on real general aviation aircraft (NGAFID / Garmin G1000 / JPI EDM). | `data/raw/` & `data/processed/flights_healthy/` | Healthy digital twin baseline fitting, signal noise floor estimation, zero-fault anomaly benchmark. | Must never be modified or overwritten. |
| **`INJECTED_FROM_REAL`** | Real flight baseline telemetry with mathematically rigorous, literature-backed physics perturbations superimposed. | `data/injected/` | Fault classification training, anomaly detection testing, scenario RUL modeling. | Must **NEVER** be described as real operational engine failure data. |
| **`SIMULATED`** | Synthetically generated telemetry from physics differential equation solvers (JSBSim `FGPiston`, Python MVEM). | `data/simulation/` | Missing operating regime expansion (e.g. 30,000 ft cold soak), mission reliability testing. | Must **NEVER** be conflated with measured engine data. |
| **`BENCHMARK_PROGNOSTICS`** | Standard NASA C-MAPSS gas turbine degradation datasets. | `data/raw/nasa/` | Generic algorithmic RUL architecture benchmarking (LSTM, Transformer). | Must **NEVER** be described as UAV piston telemetry. |

---

## 2. Mandatory Provenance Metadata Fields

Every processed dataset in `data/processed/` and `data/injected/` contains the following traceability columns:

```text
data_origin           : [REAL | INJECTED_FROM_REAL | SIMULATED]
source_flight_id      : Unique identifier of underlying airframe flight log (e.g. FLIGHT_01)
source_file           : Original raw CSV filename (e.g. log_210617_063632_LOWG.csv)
fault_id              : [NONE | FT-01 | FT-02 | FT-03 | FT-04 | FT-05 | FT-06 | FT-07 | FT-08 | FT-09]
fault_type            : Detailed failure mode name or 'HEALTHY'
fault_cylinder        : [0 = Global Engine | 1 | 2 | 3 | 4]
fault_severity        : Dimensionless degradation parameter \theta \in [0.0, 1.0]
onset_time_sec        : Exact elapsed timestamp when perturbation begins
scenario_rul_sec      : Time remaining until predefined simulated critical threshold
random_seed           : Cryptographic / pseudo-random seed used for reproducible jitter
```
