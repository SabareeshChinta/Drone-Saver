# Drone Saver — MAVLink Engine Telemetry Mapping & Bridge Architecture
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** MAVLink Message Interface, Conversion Formulas, and Companion Computer Payload Specification  

---

## 1. MAVLink Protocol Integration Overview

Drone Saver connects to ArduPilot / PX4 UAV autopilots and Software-in-the-Loop (SITL) simulators via standard MAVLink v2.0 UDP/Serial connections:

```
[ ArduPilot SITL / Pixhawk 6X Autopilot ]
                   │
    MAVLink v2.0 (UDP :14550 / UART Serial 115200)
                   ▼
┌─────────────────────────────────────────────────────────┐
│        Drone Saver MAVLink Ingestion Bridge             │
│  - Parses standard EFI_STATUS (#225) & VFR_HUD (#74)    │
│  - Decodes companion NAMED_VALUE_FLOAT (#251) payloads  │
│  - Validates timestamps, ranges, and CRC integrity      │
└─────────────────────────────────────────────────────────┘
                   │
       1.0 Hz Canonical Telemetry Packet
                   ▼
┌─────────────────────────────────────────────────────────┐
│    Drone Saver 4-Stage AI Digital Twin Diagnostics      │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Field-by-Field MAVLink Message Mapping Table

| Drone Saver Field | Target Canonical Unit | MAVLink Message | MAVLink Field | Raw MAVLink Unit | Conversion Formula | Availability Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `rpm` | $\text{RPM}$ | `EFI_STATUS` (#225) | `engine_speed` | $\text{RPM}$ | $x$ | **AVAILABLE (Native)** |
| `map_kpa` | $\text{kPa}$ | `EFI_STATUS` (#225) | `intake_manifold_pressure` | $\text{bar}$ | $x \times 100.0$ | **AVAILABLE (Native)** |
| `fuel_flow_lph` | $\text{L/h}$ | `EFI_STATUS` (#225) | `fuel_consumption` | $\text{cm}^3/\text{min}$ | $x \times 0.060$ | **AVAILABLE (Native)** |
| `oil_pressure_kpa`| $\text{kPa}$ | `NAMED_VALUE_FLOAT` (#251)| `name="OilP"` | $\text{PSI}$ or $\text{kPa}$ | $x \times 6.89476$ (if PSI) | **AVAILABLE (Companion)** |
| `oil_temp_c` | $^\circ\text{C}$ | `NAMED_VALUE_FLOAT` (#251)| `name="OilT"` | $^\circ\text{C}$ | $x$ | **AVAILABLE (Companion)** |
| `cht_1..4_c` | $^\circ\text{C}$ | `EFI_STATUS` (#225) | `cylinder_head_temperature`| $^\circ\text{C}$ | $x$ | **AVAILABLE (Native/Companion)**|
| `egt_1..4_c` | $^\circ\text{C}$ | `EFI_STATUS` (#225) | `exhaust_gas_temperature` | $^\circ\text{C}$ | $x$ | **AVAILABLE (Native/Companion)**|
| `altitude_m` | $\text{m}$ | `GLOBAL_POSITION_INT` (#33)| `relative_alt` | $\text{mm}$ | $x / 1000.0$ | **AVAILABLE (Native)** |
| `airspeed_mps` | $\text{m/s}$ | `VFR_HUD` (#74) | `airspeed` | $\text{m/s}$ | $x$ | **AVAILABLE (Native)** |
| `throttle_pct` | $\%$ | `VFR_HUD` (#74) | `throttle` | $\%$ | $x$ | **AVAILABLE (Native)** |
| `ambient_temp_c`| $^\circ\text{C}$ | `HIGHRES_IMU` (#105) | `temperature` | $^\circ\text{C}$ | $x$ | **AVAILABLE (Native)** |

---

## 3. Custom Companion Payload Specification (`NAMED_VALUE_FLOAT`)

For airframes where single-cylinder EGT/CHT multi-channel probes are routed through an engine monitoring unit (EMU) companion microcontroller (e.g. STM32 / Arduino CAN node):
* `EGT1`, `EGT2`, `EGT3`, `EGT4` (Floats, $^\circ\text{C}$)
* `CHT1`, `CHT2`, `CHT3`, `CHT4` (Floats, $^\circ\text{C}$)
* `OilP` (Float, $\text{kPa}$)
* `OilT` (Float, $^\circ\text{C}$)

These messages are broadcast over MAVLink at 1.0 Hz and parsed directly by `telemetry_listener.py`.

---

## 4. Operational Limitations & Edge Cases

1. **Standard MAVLink EFI Limitations:** Standard `EFI_STATUS` in ArduPilot provides only an aggregate engine CHT/EGT scalar in legacy builds; multi-cylinder diagnostics utilize `NAMED_VALUE_FLOAT` or the extended `EFI_STATUS` multi-head fields introduced in ArduPilot 4.3+.
2. **Clock Jitter & Timestamp Synchronization:** Autopilot time is transmitted as `time_boot_ms` (milliseconds since boot). The Drone Saver listener normalizes this into relative elapsed flight seconds ($t = \frac{\text{boot\_ms} - \text{boot}_0}{1000}$).
