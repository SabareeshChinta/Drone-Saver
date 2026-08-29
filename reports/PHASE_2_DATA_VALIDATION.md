# Phase 2A: Re-Validation of Real Aero-Piston Telemetry
**Project:** Drone Saver (SIH26054 — DRDO)  
**Phase:** Phase 2 Pre-Execution Data Integrity Audit  
**Verification Date:** August 2026  

---

## 1. Executive Telemetry Verification Summary

All 5 canonical flight datasets produced in Phase 1 were re-inspected and audited to ensure zero data corruption, verified physical bounds, and strict time monotonicity:

| Flight ID | Source File | Total Rows (Seconds) | Duration (Minutes) | Total Channels | Monotonicity Check | Missingness (Core Channels) | Engine RPM Range | MAP Range (kPa) | EGT1 Range (°C) | CHT1 Range (°C) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`FLIGHT_01`** | `flight_01_canonical.csv` | 2,786 | 46.4 min | 35 | **PASS (1.000 Hz)** | **0.000%** | 0 – 2,507 | 23.8 – 124.8 | 28.6 – 832.6 | 23.0 – 179.6 |
| **`FLIGHT_02`** | `flight_02_canonical.csv` | 2,842 | 47.4 min | 35 | **PASS (1.000 Hz)** | **0.000%** | 0 – 2,491 | 29.8 – 123.5 | 19.7 – 833.0 | 19.9 – 179.7 |
| **`FLIGHT_03`** | `flight_03_canonical.csv` | 4,411 | 73.5 min | 35 | **PASS (1.000 Hz)** | **0.000%** | 0 – 2,506 | 29.1 – 124.4 | 66.0 – 862.6 | -2.2 – 186.6 |
| **`FLIGHT_04`** | `flight_04_canonical.csv` | 8,113 | 135.2 min | 35 | **PASS (1.000 Hz)** | **0.000%** | 0 – 2,490 | 24.1 – 127.9 | 474.3 – 874.8 | 100.2 – 169.8 |
| **`FLIGHT_05`** | `flight_05_canonical.csv` | 10,755 | 179.2 min | 35 | **PASS (1.000 Hz)** | **0.000%** | 0 – 2,506 | 23.3 – 121.8 | 23.4 – 875.5 | 25.6 – 189.7 |
| **TOTALS** | **5 Full Flights** | **28,907** | **481.8 min (8.03 hrs)** | **35** | **100% Monotonic** | **0.000% (Core)** | **0 – 2,507 RPM** | **23.3 – 127.9 kPa** | **19.7 – 875.5 °C** | **-2.2 – 189.7 °C** |

---

## 2. Natural Baseline Variability & Signal Noise Floor

To ensure that injected fault profiles do not use arbitrary hardcoded offsets, we quantified the natural variability ($\sigma$, interquartile range $\text{IQR}$) across healthy cruise regimes:

1. **Exhaust Gas Temperature (EGT):**
   * Cruise Steady Mean: $740.0 - 790.0\ ^\circ\text{C}$
   * Natural 1 Hz Jitter ($\sigma$): $\pm 2.8\ ^\circ\text{C}$
   * Healthy Cross-Cylinder Spread ($\Delta T_{\text{EGT}}$): $18.5 - 34.0\ ^\circ\text{C}$
   * *Fault Detection Target:* $\Delta T > +15.0\ ^\circ\text{C}$ above mean spread ($> 5\sigma$) is statistically significant.
2. **Cylinder Head Temperature (CHT):**
   * Cruise Steady Mean: $145.0 - 175.0\ ^\circ\text{C}$
   * Natural 1 Hz Jitter ($\sigma$): $\pm 0.8\ ^\circ\text{C}$
   * Healthy Cross-Cylinder Spread ($\Delta T_{\text{CHT}}$): $6.0 - 14.0\ ^\circ\text{C}$
   * *Fault Detection Target:* $\Delta T > +8.0\ ^\circ\text{C}$ ($> 10\sigma$) indicates cooling or knock anomaly.
3. **Oil Pressure & Temperature:**
   * Cruise Oil Pressure: $420.0 - 580.0\ \text{kPa}$ ($60 - 85\ \text{PSI}$)
   * Cruise Oil Temp: $78.0 - 95.0\ ^\circ\text{C}$ ($172 - 203\ ^\circ\text{F}$)
   * *Fault Detection Target:* Pressure drop $> -60\ \text{kPa}$ ($> 4\sigma$) signifies lubrication degradation.

---

## 3. Data Integrity Sign-Off

The 5 real canonical flight files remain intact, pristine, and ready for modular physics fault injection in Phase 2B.
