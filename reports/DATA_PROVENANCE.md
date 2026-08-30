# Drone Saver — Data Provenance & Metadata Propagation
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** End-to-End Telemetry Provenance Architecture & Metadata Tracking  

---

## 1. Provenance Schema & Metadata Survival

To guarantee scientific honesty, every telemetry packet carries explicit provenance metadata that propagates untouched from ingestion through model inference to the GCS dashboard:

```json
{
  "data_origin": "REAL_PLUS_INJECTED_FAULT",
  "source_dataset": "NGAFID",
  "source_flight_id": "FLIGHT_01",
  "scenario_id": "SIH_FLAGSHIP_DEMO",
  "fault_type": "FT-02_INJECTOR_CLOGGING"
}
```

---

## 2. Three Verified Provenance Tiers

1. **`REAL AIRCRAFT TELEMETRY`:**
   * Authentic flight data from Garmin G1000 flight data recorders on Lycoming IO-360-L2A naturally aspirated, 4-cylinder aero-piston engines (Cessna 172S Skyhawk airframe).
   * Sourced from the peer-reviewed National General Aviation Flight Information Database (NGAFID Zenodo DOI `10.5281/zenodo.6624956`, CC-BY 4.0).
   * **28,907 seconds / 8.03 hours** across 5 canonical multi-regime flights.
   * Stored immutably in `data/raw/ngafid/`.
2. **`REAL TELEMETRY + PHYSICS-INFORMED FAULT INJECTION`:**
   * Authentic flight baselines perturbed with differential thermodynamic and hydraulic governing equations ($\tau_e = 4\text{s}, \tau_c = 45\text{s}$, dynamic fuel restriction $\kappa \in [0.05, 0.35]$, lubrication decay).
   * Generates 9 distinct failure modes (`FT-01` to `FT-09`) with realistic physical inertia.
3. **`SIMULATED UAV MISSION (JSBSim / MVEM)`:**
   * 2-hour 30,000 ft high-altitude loiter mission profiles generated via the pure Python 4-node MVEM thermofluid differential ODE solver.

---

## 3. UI Display Standards

The GCS dashboard visibly displays the exact data origin at all times:
* `SOURCE: REAL AIRCRAFT TELEMETRY (NGAFID G1000)` during nominal baseline replay.
* `SOURCE: REAL AIRCRAFT TELEMETRY + INJECTED FAULT` during fault injection demonstrations.
* `SOURCE: SIMULATED UAV MISSION (JSBSIM / MVEM)` during synthetic high-altitude loiter testing.
