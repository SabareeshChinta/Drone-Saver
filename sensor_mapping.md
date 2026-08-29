# Sensor Mapping & Canonical Telemetry Schema
**Project:** Drone Saver (SIH 2026 — Problem Statement: SIH26054 — DRDO)  
**Document Type:** Telemetry Standardization, Sensor Mapping, and Data Harmonization Specification  

---

## 1. The Drone Saver Canonical Schema Definition

To allow seamless interoperability between **Real Flight Telemetry**, **JPI Engine Monitors**, **JSBSim Physical Simulations**, and **DRDO UAV FADEC Architectures**, all input streams are transformed into the **Drone Saver Canonical Schema**.

The schema uses standard SI units as the internal computing baseline, while retaining standard aviation units for human engineering verification.

### 1.1 Canonical Parameter Specification

| Canonical Field Name | Physical Description | Standard SI Unit | Aviation Unit | Expected Normal Range | Critical / Warning Threshold | Sensor Type / Source |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `timestamp` | Time elapsed from engine start / flight start | $\text{s}$ (seconds) | $\text{hh:mm:ss}$ | $\ge 0$ | Monotonic increase | System Clock / GPS UTC |
| `engine_rpm` | Crankshaft rotational speed | $\text{RPM}$ ($\text{rad/s} \times 9.549$) | $\text{RPM}$ | $700 - 2700\ \text{RPM}$ | $> 2750\ \text{RPM}$ (Overspeed) / $< 600$ (Stall) | Hall effect / Mag pickup |
| `manifold_pressure_kpa` | Intake manifold absolute pressure | $\text{kPa}$ | $\text{inHg}$ ($1\ \text{inHg} = 3.386\ \text{kPa}$) | $40 - 101.3\ \text{kPa}$ ($12 - 30\ \text{inHg}$) | $> 105\ \text{kPa}$ (Overboost) / $< 30\ \text{kPa}$ | Piezoresistive MAP sensor |
| `fuel_flow_lph` | Volumetric engine fuel consumption rate | $\text{L/h}$ | $\text{GPH}$ ($1\ \text{GPH} = 3.785\ \text{L/h}$) | $15.0 - 65.0\ \text{L/h}$ ($4.0 - 17.2\ \text{GPH}$) | $> 75.0\ \text{L/h}$ (Flooding/Leak) / $< 10.0$ | Turbine flow transducer |
| `oil_temperature_c` | Engine lubricating oil sump temperature | $^\circ\text{C}$ | $^\circ\text{F}$ ($T_C = (T_F - 32)/1.8$) | $60 - 105\ ^\circ\text{C}$ ($140 - 220\ ^\circ\text{F}$) | $> 118\ ^\circ\text{C}$ ($245\ ^\circ\text{F}$) / $< 38\ ^\circ\text{C}$ | Thermistor / RTD probe |
| `oil_pressure_kpa` | Main oil gallery lubrication pressure | $\text{kPa}$ | $\text{PSI}$ ($1\ \text{PSI} = 6.895\ \text{kPa}$) | $345 - 620\ \text{kPa}$ ($50 - 90\ \text{PSI}$) | $< 172\ \text{kPa}$ ($25\ \text{PSI}$) / $> 750\ \text{kPa}$ | Piezoresistive pressure sensor |
| `cht_cyl1_c` | Cylinder Head Temperature Cylinder #1 | $^\circ\text{C}$ | $^\circ\text{F}$ | $120 - 200\ ^\circ\text{C}$ ($250 - 390\ ^\circ\text{F}$) | $> 224\ ^\circ\text{C}$ ($435\ ^\circ\text{F}$) (Thermal limit) | Type-J / Type-K thermocouple |
| `cht_cyl2_c` | Cylinder Head Temperature Cylinder #2 | $^\circ\text{C}$ | $^\circ\text{F}$ | $120 - 200\ ^\circ\text{C}$ ($250 - 390\ ^\circ\text{F}$) | $> 224\ ^\circ\text{C}$ ($435\ ^\circ\text{F}$) | Type-J / Type-K thermocouple |
| `cht_cyl3_c` | Cylinder Head Temperature Cylinder #3 | $^\circ\text{C}$ | $^\circ\text{F}$ | $120 - 200\ ^\circ\text{C}$ ($250 - 390\ ^\circ\text{F}$) | $> 224\ ^\circ\text{C}$ ($435\ ^\circ\text{F}$) | Type-J / Type-K thermocouple |
| `cht_cyl4_c` | Cylinder Head Temperature Cylinder #4 | $^\circ\text{C}$ | $^\circ\text{F}$ | $120 - 200\ ^\circ\text{C}$ ($250 - 390\ ^\circ\text{F}$) | $> 224\ ^\circ\text{C}$ ($435\ ^\circ\text{F}$) | Type-J / Type-K thermocouple |
| `egt_cyl1_c` | Exhaust Gas Temperature Cylinder #1 | $^\circ\text{C}$ | $^\circ\text{F}$ | $650 - 820\ ^\circ\text{C}$ ($1200 - 1500\ ^\circ\text{F}$) | $> 870\ ^\circ\text{C}$ ($1600\ ^\circ\text{F}$) (Exhaust limit) | Type-K thermocouple |
| `egt_cyl2_c` | Exhaust Gas Temperature Cylinder #2 | $^\circ\text{C}$ | $^\circ\text{F}$ | $650 - 820\ ^\circ\text{C}$ ($1200 - 1500\ ^\circ\text{F}$) | $> 870\ ^\circ\text{C}$ ($1600\ ^\circ\text{F}$) | Type-K thermocouple |
| `egt_cyl3_c` | Exhaust Gas Temperature Cylinder #3 | $^\circ\text{C}$ | $^\circ\text{F}$ | $650 - 820\ ^\circ\text{C}$ ($1200 - 1500\ ^\circ\text{F}$) | $> 870\ ^\circ\text{C}$ ($1600\ ^\circ\text{F}$) | Type-K thermocouple |
| `egt_cyl4_c` | Exhaust Gas Temperature Cylinder #4 | $^\circ\text{C}$ | $^\circ\text{F}$ | $650 - 820\ ^\circ\text{C}$ ($1200 - 1500\ ^\circ\text{F}$) | $> 870\ ^\circ\text{C}$ ($1600\ ^\circ\text{F}$) | Type-K thermocouple |
| `oat_c` | Outside Ambient Air Temperature | $^\circ\text{C}$ | $^\circ\text{C}$ / $^\circ\text{F}$ | $-40 - +50\ ^\circ\text{C}$ | ISA deviation monitoring | Platinum RTD probe |
| `altitude_m` | Pressure Altitude MSL | $\text{m}$ | $\text{ft}$ ($1\ \text{ft} = 0.3048\ \text{m}$) | $0 - 10000\ \text{m}$ ($0 - 32800\ \text{ft}$) | Rate of climb monitoring | Barometric altimeter |
| `indicated_airspeed_mps` | Indicated Airspeed | $\text{m/s}$ | $\text{knots}$ ($1\ \text{kt} = 0.5144\ \text{m/s}$) | $0 - 85\ \text{m/s}$ ($0 - 165\ \text{kts}$) | Stall speed / $V_{\text{NE}}$ | Pitot-static differential |
| `bus_voltage_v` | Primary electrical bus potential | $\text{V}$ | $\text{Volts}$ | $13.5 - 14.8\ \text{V}$ / $27.0 - 28.8\ \text{V}$ | $< 12.0\ \text{V}$ / $< 24.0\ \text{V}$ (Alt fail) | Voltage divider |
| `battery_current_a` | System net electrical current | $\text{A}$ | $\text{Amperes}$ | $-5.0 - +40.0\ \text{A}$ | $< -15.0\ \text{A}$ (Discharge drain) | Hall-effect current shunt |
| `coolant_temp_c` | Liquid Coolant Temp (Rotax/Austro/VRDE) | $^\circ\text{C}$ | $^\circ\text{F}$ | $75 - 100\ ^\circ\text{C}$ ($167 - 212\ ^\circ\text{F}$) | $> 115\ ^\circ\text{C}$ ($239\ ^\circ\text{F}$) | Thermistor / RTD sensor |
| `turbine_inlet_temp_c` | Turbine Inlet Temp (Turbocharged UAVs) | $^\circ\text{C}$ | $^\circ\text{F}$ | $700 - 900\ ^\circ\text{C}$ ($1292 - 1652\ ^\circ\text{F}$) | $> 950\ ^\circ\text{C}$ ($1742\ ^\circ\text{F}$) | Type-K thermocouple |

---

## 2. Telemetry Cross-Mapping Matrix

The following table maps every external dataset and simulation channel directly to the Drone Saver Canonical Schema:

| Canonical Schema Field | NGAFID (Garmin G1000 C172) | JPI EDM-700/800/900 Log | JSBSim Property Tree Path | DRDO / VRDE FADEC Architecture |
| :--- | :--- | :--- | :--- | :--- |
| `timestamp` | `Lcl Date` + `Lcl Time` (epoch seconds) | `Time` (Seconds from boot) | `simulation/sim-time-sec` | `FADEC_TIME_MS` $\div 1000$ |
| `engine_rpm` | `E1 RPM` | `RPM` | `propulsion/engine[0]/rpm` | `ECU_CRANK_RPM` |
| `manifold_pressure_kpa` | `E1 MAP` $(\text{inHg} \times 3.38639)$ | `MAP` $(\text{inHg} \times 3.38639)$ | `propulsion/engine[0]/manifold-pressure-inhg` $\times 3.38639$ | `ECU_BOOST_MAP_KPA` |
| `fuel_flow_lph` | `E1 FFlow` $(\text{GPH} \times 3.78541)$ | `FF` $(\text{GPH} \times 3.78541)$ | `propulsion/engine[0]/fuel-flow-rate-gph` $\times 3.78541$ | `ECU_FUEL_DELIVERY_LPH` |
| `oil_temperature_c` | `E1 OilT` $(\frac{^\circ\text{F}-32}{1.8})$ | `OIL_T` $(\frac{^\circ\text{F}-32}{1.8})$ | `propulsion/engine[0]/oil-temperature-degf` $(\frac{^\circ\text{F}-32}{1.8})$ | `ECU_OIL_TEMP_C` |
| `oil_pressure_kpa` | `E1 OilP` $(\text{PSI} \times 6.89476)$ | `OIL_P` $(\text{PSI} \times 6.89476)$ | `propulsion/engine[0]/oil-pressure-psi` $\times 6.89476$ | `ECU_OIL_PRESS_BAR` $\times 100$ |
| `cht_cyl1_c` | `E1 CHT1` $(\frac{^\circ\text{F}-32}{1.8})$ | `CHT1` $(\frac{^\circ\text{F}-32}{1.8})$ | `propulsion/engine[0]/cht-degf` (Cyl 1 baseline) | `ECU_CHT_CYL1_C` |
| `cht_cyl2_c` | `E1 CHT2` $(\frac{^\circ\text{F}-32}{1.8})$ | `CHT2` $(\frac{^\circ\text{F}-32}{1.8})$ | `propulsion/engine[0]/cht-degf` (Cyl 2 baseline) | `ECU_CHT_CYL2_C` |
| `cht_cyl3_c` | `E1 CHT3` $(\frac{^\circ\text{F}-32}{1.8})$ | `CHT3` $(\frac{^\circ\text{F}-32}{1.8})$ | `propulsion/engine[0]/cht-degf` (Cyl 3 baseline) | `ECU_CHT_CYL3_C` |
| `cht_cyl4_c` | `E1 CHT4` $(\frac{^\circ\text{F}-32}{1.8})$ | `CHT4` $(\frac{^\circ\text{F}-32}{1.8})$ | `propulsion/engine[0]/cht-degf` (Cyl 4 baseline) | `ECU_CHT_CYL4_C` |
| `egt_cyl1_c` | `E1 EGT1` $(\frac{^\circ\text{F}-32}{1.8})$ | `EGT1` $(\frac{^\circ\text{F}-32}{1.8})$ | `propulsion/engine[0]/egt-degf` (Cyl 1 baseline) | `ECU_EGT_CYL1_C` |
| `egt_cyl2_c` | `E1 EGT2` $(\frac{^\circ\text{F}-32}{1.8})$ | `EGT2` $(\frac{^\circ\text{F}-32}{1.8})$ | `propulsion/engine[0]/egt-degf` (Cyl 2 baseline) | `ECU_EGT_CYL2_C` |
| `egt_cyl3_c` | `E1 EGT3` $(\frac{^\circ\text{F}-32}{1.8})$ | `EGT3` $(\frac{^\circ\text{F}-32}{1.8})$ | `propulsion/engine[0]/egt-degf` (Cyl 3 baseline) | `ECU_EGT_CYL3_C` |
| `egt_cyl4_c` | `E1 EGT4` $(\frac{^\circ\text{F}-32}{1.8})$ | `EGT4` $(\frac{^\circ\text{F}-32}{1.8})$ | `propulsion/engine[0]/egt-degf` (Cyl 4 baseline) | `ECU_EGT_CYL4_C` |
| `oat_c` | `OAT` ($^\circ\text{C}$) | `OAT` $(\frac{^\circ\text{F}-32}{1.8})$ | `atmosphere/T-R` $(\frac{T_R - 491.67}{1.8})$ | `AIR_DATA_OAT_C` |
| `altitude_m` | `AltMSL` $(\text{ft} \times 0.3048)$ | `ALT` $(\text{ft} \times 0.3048)$ | `position/h-sl-ft` $\times 0.3048$ | `FCS_ALTITUDE_MSL_M` |
| `indicated_airspeed_mps`| `IAS` $(\text{kts} \times 0.514444)$ | `IAS` $(\text{kts} \times 0.514444)$ | `velocities/vc-kts` $\times 0.514444$ | `AIR_DATA_IAS_MPS` |
| `bus_voltage_v` | `volt1` | `BAT` (Volts) | `electric/bus-voltage-v` | `FADEC_BUS_VOLTS` |
| `battery_current_a` | `amp1` | `AMP` (Amps) | `electric/battery-current-a` | `FADEC_GEN_CURRENT_A` |
| `coolant_temp_c` | *Synthesized via thermal model* | `CLT` (if equipped) | `propulsion/engine[0]/coolant-temp-c` | `ECU_COOLANT_TEMP_C` |
| `turbine_inlet_temp_c` | *Synthesized via exhaust model*| `TIT` $(\frac{^\circ\text{F}-32}{1.8})$ | `propulsion/engine[0]/tit-degc` | `ECU_TURBO_TIT_C` |

---

## 3. Transformation & Harmonization Pipeline

```
+---------------------------+    +--------------------------+    +--------------------------+
| NGAFID Garmin G1000 Raw   |    | JPI EDM-700/800/900 Logs |    | JSBSim Python Telemetry  |
| (deg F, PSI, InHg, Knots) |    | (Hex / Raw JPI CSV)      |    | (Property Tree Nodes)    |
+---------------------------+    +--------------------------+    +--------------------------+
              \                               |                               /
               \                              |                              /
                v                             v                             v
  +------------------------------------------------------------------------------------+
  |                           DRONE SAVER INGESTION PARSER                             |
  |  1. Epoch timestamp alignment (1 Hz resample)                                      |
  |  2. Explicit Unit Transformation (deg F -> deg C, InHg -> kPa, PSI -> kPa)         |
  |  3. Range & Physical Consistency Validation                                        |
  |  4. Derived Feature Calculation (EGT Spread, CHT Spread, Thermal Gradients)         |
  +------------------------------------------------------------------------------------+
                                              |
                                              v
  +------------------------------------------------------------------------------------+
  |                        CANONICAL SCHEMATIZED DATAFRAME                             |
  |  [timestamp, engine_rpm, manifold_pressure_kpa, fuel_flow_lph, oil_temperature_c,   |
  |   oil_pressure_kpa, cht_cyl1..4_c, egt_cyl1..4_c, egt_spread_c, cht_spread_c, ...]  |
  +------------------------------------------------------------------------------------+
```

### 3.1 Derived Physics Features
In addition to direct transducer readings, the ingestion parser computes four diagnostic features:
1. **EGT Spread ($\Delta T_{\text{EGT}}$):** Maximum exhaust gas temperature divergence across cylinders:
   $$\Delta T_{\text{EGT}}(t) = \max_{i \in \{1..4\}} \text{egt\_cyl}_i(t) - \min_{i \in \{1..4\}} \text{egt\_cyl}_i(t)$$
   *Healthy Baseline:* $\Delta T_{\text{EGT}} \le 35\ ^\circ\text{C}$ ($65\ ^\circ\text{F}$).  
   *Fault Alarm:* $\Delta T_{\text{EGT}} > 55\ ^\circ\text{C}$ indicates injector mismatch, spark failure, or burnt valve.

2. **CHT Spread ($\Delta T_{\text{CHT}}$):** Maximum cylinder head temperature divergence across cylinders:
   $$\Delta T_{\text{CHT}}(t) = \max_{i \in \{1..4\}} \text{cht\_cyl}_i(t) - \min_{i \in \{1..4\}} \text{cht\_cyl}_i(t)$$
   *Healthy Baseline:* $\Delta T_{\text{CHT}} \le 20\ ^\circ\text{C}$ ($36\ ^\circ\text{F}$).  
   *Fault Alarm:* $\Delta T_{\text{CHT}} > 35\ ^\circ\text{C}$ indicates cooling baffle degradation or detonation.

3. **Thermal Rate of Change ($\dot{T}_{\text{CHT}}$):** First derivative of CHT:
   $$\dot{T}_{\text{CHT}, i}(t) = \frac{T_{\text{CHT}, i}(t) - T_{\text{CHT}, i}(t-\Delta t)}{\Delta t}$$
   *Detonation Signature:* $\dot{T}_{\text{CHT}} > +0.8\ ^\circ\text{C/s}$ ($> 1.5\ ^\circ\text{F/s}$) without power increase.

4. **Lubrication Viscosity Index ($\Lambda_{\text{oil}}$):** Ratio of oil pressure to engine speed normalized by temperature:
   $$\Lambda_{\text{oil}}(t) = \frac{\text{oil\_pressure\_kpa}(t)}{\text{engine\_rpm}(t)} \cdot \exp\left(\beta \cdot \text{oil\_temperature\_c}(t)\right)$$

---

## 4. Handling Missing Values & Sensor Anomalies

| Data Anomaly Scenario | Physical Root Cause | Detection Rule | Remediation / Ingestion Action |
| :--- | :--- | :--- | :--- |
| **Thermocouple Open Circuit** | Loose probe connector / broken wire | $T_{\text{EGT}} < -10\ ^\circ\text{C}$ or $T > 1300\ ^\circ\text{C}$ | Flag sensor `FAIL_OPEN`; impute with median of adjacent healthy cylinders for display, but record fault in Diagnostic Log |
| **Sensor Value Dropout** | Avionics digital bus lag / packet loss | Repeated exact value $> 10\ \text{s}$ or single NaN | Linear interpolation for gaps $\le 3\ \text{s}$; Forward fill if gap $\le 5\ \text{s}$; Flag regime discontinuity if $> 5\ \text{s}$ |
| **Cold Engine Startup Artifacts** | Engine oil cold / high viscosity | $\text{oil\_temperature\_c} < 30\ ^\circ\text{C}$ and $\text{oil\_pressure\_kpa} > 700\ \text{kPa}$ | Mask health monitoring alarms during warm-up phase (Regime 0: Startup) |
| **High Frequency Bus Noise** | Magneto / ignition EMI interference | High-frequency jitter ($\sigma > 3 \times$ physical maximum) | Apply 3-point moving average filter; isolate electrical noise from physical temperature variations |
