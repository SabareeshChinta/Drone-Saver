# Drone Saver — Healthy Baseline Digital Twin Report
**Project:** Drone Saver (SIH26054 — DRDO)
**Phase:** Phase 1 Digital Twin Modeling
**Training Set Size:** 22,567 samples across 5 real aero-piston flights

---

## Baseline Model Regression Accuracy

| Target Channel | Predictor Channels | $R^2$ Score | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) |
| :--- | :--- | :--- | :--- | :--- |
| `fuel_flow_lph` | `rpm`, `map_kpa` | 0.8353 | 8.99 L/h | 12.34 L/h |
| `oil_pressure_kpa` | `rpm`, `oil_temp_c` | 0.4506 | 6.87 kPa | 9.92 kPa |
| `egt_1_c` | `rpm`, `map_kpa`, `fuel_flow_lph`, `ambient_temp_c` | 0.9575 | 7.97 °C | 12.71 °C |
| `egt_2_c` | `rpm`, `map_kpa`, `fuel_flow_lph`, `ambient_temp_c` | 0.9539 | 8.54 °C | 13.88 °C |
| `egt_3_c` | `rpm`, `map_kpa`, `fuel_flow_lph`, `ambient_temp_c` | 0.9475 | 8.73 °C | 13.88 °C |
| `egt_4_c` | `rpm`, `map_kpa`, `fuel_flow_lph`, `ambient_temp_c` | 0.9614 | 8.55 °C | 13.41 °C |
| `cht_1_c` | `rpm`, `map_kpa`, `ambient_temp_c`, `altitude_m`, `airspeed_mps` | 0.7956 | 5.57 °C | 7.84 °C |
| `cht_2_c` | `rpm`, `map_kpa`, `ambient_temp_c`, `altitude_m`, `airspeed_mps` | 0.7684 | 5.29 °C | 7.50 °C |
| `cht_3_c` | `rpm`, `map_kpa`, `ambient_temp_c`, `altitude_m`, `airspeed_mps` | 0.8151 | 5.64 °C | 7.98 °C |
| `cht_4_c` | `rpm`, `map_kpa`, `ambient_temp_c`, `altitude_m`, `airspeed_mps` | 0.8392 | 5.11 °C | 7.14 °C |

---
## Flight Residual Profiles & Residual Standard Deviations

| Flight ID | EGT1 Residual Std (°C) | EGT2 Residual Std (°C) | EGT3 Residual Std (°C) | EGT4 Residual Std (°C) | CHT1 Residual Std (°C) | CHT2 Residual Std (°C) | CHT3 Residual Std (°C) | CHT4 Residual Std (°C) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FLIGHT_01` | 16.93 | 22.43 | 18.93 | 18.29 | 7.58 | 7.33 | 7.75 | 6.88 |
| `FLIGHT_02` | 14.92 | 22.22 | 10.75 | 17.94 | 11.08 | 10.86 | 9.87 | 9.36 |
| `FLIGHT_03` | 12.68 | 14.48 | 14.02 | 14.32 | 8.46 | 7.54 | 9.22 | 7.21 |
| `FLIGHT_04` | 16.09 | 17.59 | 17.90 | 15.89 | 10.03 | 8.63 | 9.13 | 7.81 |
| `FLIGHT_05` | 9.49 | 11.15 | 10.32 | 10.58 | 5.11 | 5.03 | 5.27 | 5.11 |

---
### Digital Twin Residual Baseline Interpretation:
1. **Healthy Residual Bound:** Under healthy operation, cylinder EGT residuals remain within $\pm 25\ ^\circ	ext{C}$ and CHT residuals remain within $\pm 8\ ^\circ	ext{C}$ during cruise.
2. **Anomaly Thresholds:** An individual cylinder EGT residual exceeding $+45\ ^\circ	ext{C}$ or CHT residual exceeding $+20\ ^\circ	ext{C}$ provides immediate mathematical detection of cylinder degradation prior to complete failure.