# Drone Saver — Live Telemetry Ingestion Schema & Channel Inventory
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** Live Telemetry Packet Specification & Channel Availability  

---

## 1. Live Telemetry Packet Schema

All live streams (UDP sockets, Serial UART, MAVLink adapters, or Replay feeds) conform to the following canonical JSON / dictionary packet format delivered at 1.0 Hz:

```json
{
  "timestamp": 1724968800.0,
  "time_seconds": 1200.0,
  "rpm": 2450.0,
  "map_kpa": 85.2,
  "fuel_flow_lph": 42.5,
  "oil_temp_c": 82.4,
  "oil_pressure_kpa": 465.0,
  "cht_1_c": 156.2,
  "cht_2_c": 158.4,
  "cht_3_c": 155.1,
  "cht_4_c": 160.0,
  "egt_1_c": 762.0,
  "egt_2_c": 768.5,
  "egt_3_c": 759.0,
  "egt_4_c": 764.2,
  "altitude_m": 2500.0,
  "airspeed_mps": 45.2,
  "ambient_temp_c": 14.5,
  "throttle_pct": 78.0
}
```

---

## 2. Channel Availability & Provenance Classification

| Channel Name | Units | Expected Physical Range | MAVLink Source | Status | Degradation Fallback |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `time_seconds` | $\text{s}$ | $\ge 0.0$ | `SYSTEM_TIME.time_boot_ms` | **AVAILABLE** | Timestamp clock delta $\Delta t$ |
| `rpm` | $\text{RPM}$ | $0 - 3,000$ | `EFI_STATUS.engine_speed` / `RPM` | **AVAILABLE** | Derived from throttle / alternator frequency |
| `map_kpa` | $\text{kPa}$ | $20.0 - 135.0$ | `EFI_STATUS.intake_manifold_pressure` | **AVAILABLE** | Ambient barometric pressure lapse estimate |
| `fuel_flow_lph`| $\text{L/h}$ | $0.0 - 120.0$ | `EFI_STATUS.fuel_consumption` | **DERIVED** | Indicated load map $\dot{m}_f = f(\text{RPM}, \text{MAP})$ |
| `oil_temp_c` | $^\circ\text{C}$ | $-20.0 - 140.0$ | `NAMED_VALUE_FLOAT("OilT")` | **AVAILABLE** | Thermal sump differential node |
| `oil_pressure_kpa`| $\text{kPa}$ | $0.0 - 700.0$ | `NAMED_VALUE_FLOAT("OilP")` | **AVAILABLE** | Engine RPM hydraulic baseline |
| `cht_1..4_c` | $^\circ\text{C}$ | $-30.0 - 260.0$ | `EFI_STATUS.cylinder_head_temperature` | **AVAILABLE** | Multi-node thermal conduction baseline |
| `egt_1..4_c` | $^\circ\text{C}$ | $-30.0 - 950.0$ | `EFI_STATUS.exhaust_gas_temperature` | **AVAILABLE** | Stoichiometric heat release model |
| `altitude_m` | $\text{m}$ | $-100.0 - 12,000$| `GLOBAL_POSITION_INT.relative_alt` | **AVAILABLE** | Barometric pressure altitude |
| `airspeed_mps`| $\text{m/s}$ | $0.0 - 120.0$ | `VFR_HUD.airspeed` | **AVAILABLE** | GPS Groundspeed estimation |
| `ambient_temp_c`| $^\circ\text{C}$ | $-55.0 - 55.0$ | `HIGHRES_IMU.temperature` | **AVAILABLE** | Standard Atmosphere (ISA) lapse calculation |
| `throttle_pct` | $\%$ | $0.0 - 100.0$ | `VFR_HUD.throttle` | **AVAILABLE** | Servo command output |

---

## 3. Handling Missing or Derived Telemetry

When an auxiliary channel (e.g. `fuel_flow_lph` or `ambient_temp_c`) is absent in standard telemetry frames:
1. The packet validator flags the packet status as `PARTIAL`.
2. The canonicalizer invokes physics fallback models (e.g. ISA atmospheric temperature lapse $T(h) = T_0 - 0.0065 \cdot h$).
3. Sensor reliability confidence for derived channels is explicitly adjusted to $0.85$ (vs $1.00$ for direct ADC transducers).
