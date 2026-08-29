# Unit Conversions & Physical Scaling Standards
**Project:** Drone Saver (SIH 2026 — Problem Statement: SIH26054 — DRDO)  
**Document Type:** Telemetry Unit Transformation and Precision Standards  

---

## 1. Overview & Conversion Formulae

Raw general aviation Garmin G1000 and JPI telemetry logs record in standard US Aviation / Imperial units.
The **Drone Saver Canonical Schema** transforms all measurements into standard SI / Metric engineering units to maintain dimensional consistency across physical equations and machine learning layers.

| Telemetry Parameter | Raw Garmin / JPI Unit | Canonical SI / Metric Unit | Exact Mathematical Conversion Formula | Scale Factor / Offset |
| :--- | :--- | :--- | :--- | :--- |
| **Engine Speed (`rpm`)** | $\text{RPM}$ | $\text{RPM}$ | $\text{RPM} = \text{RPM}_{\text{raw}}$ | $\times 1.0$ |
| **Manifold Pressure (`map_kpa`)** | $\text{inHg}$ (Inches of Mercury) | $\text{kPa}$ (Kilopascals) | $P_{\text{kPa}} = P_{\text{inHg}} \times 3.386389$ | $\times 3.386389$ |
| **Fuel Flow (`fuel_flow`)** | $\text{GPH}$ (US Gallons / Hour) | $\text{L/h}$ (Litres / Hour) | $\dot{V}_{\text{L/h}} = \dot{V}_{\text{GPH}} \times 3.785412$ | $\times 3.785412$ |
| **Oil Temperature (`oil_temp_c`)** | $^\circ\text{F}$ (Fahrenheit) | $^\circ\text{C}$ (Celsius) | $T_C = \frac{T_F - 32}{1.8}$ | $-32,\ \div 1.8$ |
| **Oil Pressure (`oil_pressure_kpa`)** | $\text{PSI}$ (Pounds / Sq Inch) | $\text{kPa}$ (Kilopascals) | $P_{\text{kPa}} = P_{\text{PSI}} \times 6.894757$ | $\times 6.894757$ |
| **Cylinder Head Temp (`cht_i_c`)** | $^\circ\text{F}$ (Fahrenheit) | $^\circ\text{C}$ (Celsius) | $T_C = \frac{T_F - 32}{1.8}$ | $-32,\ \div 1.8$ |
| **Exhaust Gas Temp (`egt_i_c`)** | $^\circ\text{F}$ (Fahrenheit) | $^\circ\text{C}$ (Celsius) | $T_C = \frac{T_F - 32}{1.8}$ | $-32,\ \div 1.8$ |
| **Turbine Inlet Temp (`tit_i_c`)** | $^\circ\text{F}$ (Fahrenheit) | $^\circ\text{C}$ (Celsius) | $T_C = \frac{T_F - 32}{1.8}$ | $-32,\ \div 1.8$ |
| **Pressure Altitude (`altitude_m`)** | $\text{ft}$ (Feet MSL) | $\text{m}$ (Metres) | $h_{\text{m}} = h_{\text{ft}} \times 0.3048$ | $\times 0.3048$ |
| **Indicated Airspeed (`airspeed`)** | $\text{kt}$ (Knots) | $\text{m/s}$ (Metres / Second) | $v_{\text{m/s}} = v_{\text{kt}} \times 0.514444$ | $\times 0.514444$ |
| **Vertical Speed (`vertical_speed_mps`)** | $\text{fpm}$ (Feet / Minute) | $\text{m/s}$ (Metres / Second) | $v_z = v_{\text{fpm}} \times 0.00508$ | $\times 0.00508$ |
| **Ambient Temperature (`ambient_temp_c`)**| $^\circ\text{C}$ (Celsius) | $^\circ\text{C}$ (Celsius) | $T_{\text{ambient}} = T_{\text{raw}}$ | $\times 1.0$ |
| **Electrical Voltage (`voltage_1`, `2`)** | $\text{Volts}$ | $\text{Volts}$ | $V = V_{\text{raw}}$ | $\times 1.0$ |
| **Electrical Current (`current_1`)** | $\text{Amperes}$ | $\text{Amperes}$ | $I = I_{\text{raw}}$ | $\times 1.0$ |
| **Fuel Quantity (`fuel_qty_l`, `r`)** | $\text{gals}$ (Gallons) | $\text{L}$ (Litres) | $V_{\text{L}} = V_{\text{gals}} \times 3.785412$ | $\times 3.785412$ |

---

## 2. Validation & Physical Plausibility Checks

During canonical transformation, every row is validated against physical bounds:
1. **RPM:** $[0, 3500]\ \text{RPM}$
2. **Manifold Pressure:** $[20, 150]\ \text{kPa}$
3. **Fuel Flow:** $[0, 120]\ \text{L/h}$
4. **Oil Temperature:** $[-20, 150]\ ^\circ\text{C}$
5. **Oil Pressure:** $[0, 900]\ \text{kPa}$
6. **CHT:** $[-20, 300]\ ^\circ\text{C}$
7. **EGT:** $[-20, 1050]\ ^\circ\text{C}$
8. **Altitude:** $[-500, 12000]\ \text{m}$
9. **Airspeed:** $[0, 120]\ \text{m/s}$

Any values falling outside physical boundaries are recorded in the data quality audit log.
