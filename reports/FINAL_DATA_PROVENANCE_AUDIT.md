# Drone Saver — Final Data Provenance & Real-Data Audit
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** Scientific Data Provenance, Engine Type Verification, and Provenance Categorization  

---

## 1. Verified Real Telemetry Dataset Specifications

All real telemetry utilized in Drone Saver is sourced directly from the peer-reviewed National General Aviation Flight Information Database (NGAFID) aviation maintenance archive:

| Parameter | Exact Verified Value | Verification Source |
| :--- | :--- | :--- |
| **Dataset Title** | A Large-Scale Annotated Multivariate Time Series Aviation Maintenance Dataset from the NGAFID | Zenodo Repository DOI: `10.5281/zenodo.6624956` (arXiv:2210.07317) |
| **Dataset Creators** | Hong Yang & Travis Desell (Rochester Institute of Technology / Univ. of North Dakota) | Published Open-Access Research Archive |
| **License** | Creative Commons Attribution 4.0 International (CC-BY 4.0) | Verified Open Access |
| **Propulsion Type** | **Lycoming IO-360-L2A Aero-Piston Engine** | Direct manufacturer specification from airframe type certificate |
| **Engine Architecture** | 4-Cylinder Horizontally Opposed, Naturally Aspirated, Air-Cooled, Fuel-Injected (180 HP) | Lycoming IO-360 Operator's Manual (FAA TC 1E10) |
| **Airframe Type** | **Cessna 172S Skyhawk** | Flight recorder installation logs |
| **Avionics / DAQ** | **Garmin G1000 Integrated Flight Deck** | Authentic 1.0 Hz ADC Flight Data Recorder logs |
| **Sampling Frequency** | **1.0 Hz (1.000 s interval $\pm 0.02\text{s}$)** | Verified monotonic timestamp delta |
| **Canonical Flight Count** | 5 complete multi-regime flights (`FLIGHT_01` to `FLIGHT_05`) | `data/processed/canonical/*_canonical.csv` |
| **Total Real Telemetry** | **28,907 seconds (8.03 flight hours)** | Exact time-series row count across 5 flights |
| **Sensor Channels** | 23 physical telemetry channels (EGT1–4, CHT1–4, RPM, MAP, OilP, OilT, Fuel Flow, Alt, IAS, OAT, Throttle) | Standardized into SI units |

---

## 2. Three-Tier Data Provenance Categorization

Drone Saver enforces strict provenance separation across all code, models, reports, and UI screens:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. REAL AIRCRAFT TELEMETRY                                                 │
│    - Authentic Lycoming IO-360-L2A flight logs from Garmin G1000 recorders. │
│    - Immutable in `data/raw/ngafid/`.                                       │
│    - Used to train healthy physics baselines and Stage 1 anomaly bounds.   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. REAL TELEMETRY + PHYSICS-INFORMED FAULT INJECTION                        │
│    - Real flight baseline with differential thermodynamic fault perturbations│
│      (FT-01 to FT-09) applied via dynamic thermal/hydraulic differential lag.│
│    - Used for multi-class classification and scenario time-to-critical RUL. │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. SIMULATED UAV MISSION (JSBSim / MVEM)                                    │
│    - Synthetic 2-hour 30,000 ft high-altitude loiter mission profile         │
│      generated via the pure Python 4-node MVEM thermofluid differential ODE.│
│    - Used for extreme altitude envelope verification.                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Explicit Prohibitions & Unvalidated Boundary Conditions

* **DRDO Military Heavy-Fuel Propulsion:** The baseline data represents aviation gasoline (AvGas 100LL) spark-ignited Lycoming IO-360 engines. It is **not** military heavy-fuel (ATF Kerosene / Diesel) compression-ignition UAV telemetry.
* **Acoustic Knock Bandwidth:** Standard 1.0 Hz avionics flight logs cannot resolve microsecond-scale acoustic detonation flutter ($> 5\ \text{kHz}$). Detonation (FT-04) is modeled via its observed macro-thermal signature (rapid CHT elevation and thermal runaway).
* **RUL Terminology:** All estimated remaining life figures are explicitly designated **`SCENARIO TIME-TO-CRITICAL`** (time remaining before crossing simulated redlines), not material fatigue run-to-failure lifing.
