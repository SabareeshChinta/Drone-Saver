# Drone Saver — Master Final Demo Evaluation Report
**Project:** Drone Saver (SIH26054 — DRDO)  
**Scenario:** `scenarios/FINAL_DEMO.yaml`  
**Failure Mode Demonstrated:** Progressive Fuel Injector Clogging on Cylinder #2 (`FT-02_INJECTOR_CLOGGING`)  
**Underlying Telemetry:** Real Flight Recorder Telemetry (`FLIGHT_01`, 2,786 continuous 1.0 Hz steps)  

---

## 1. End-to-End Diagnostic Sequence Timeline

The sequential real-time replay engine processed 2,786 consecutive telemetry timestamps in streaming mode with zero future lookahead:

```
+-----------------------------------------------------------------------------------------------------------------------------+
|                                     MASTER REPLAY DIAGNOSTIC STATE PROGRESSION TIMELINE                                     |
+-----------------------------------------------------------------------------------------------------------------------------+
| Time (sec / min)   | Engine State | Health H(t) | Anomaly A(t) | Top Diagnosed Fault     | Cylinder | Scenario RUL | Decision Directive       |
+-----------------------------------------------------------------------------------------------------------------------------+
| 00:00 - 16:39      | NOMINAL      | 0.985       | 0.015        | HEALTHY (99.8%)         | Cyl 0    | > 45.0 min   | CONTINUE_MISSION         |
| 16:40 (t=1000s)    | DEGRADING    | 0.940       | 0.060        | HEALTHY (78.2%)         | Cyl 0    | 24.2 min     | CONTINUE_MISSION         |
| 16:52 (t=1012s)    | ANOMALY ONSET| 0.812       | 0.288        | FT-02_INJECTOR (68.4%)  | Cyl #2   | 18.4 min     | DERATE_POWER_AND_LOITER  |
| 20:00 (t=1200s)    | ACTIVE LEAN  | 0.671       | 0.429        | FT-02_INJECTOR (84.5%)  | Cyl #2   | 11.5 min     | ABORT_RETURN_TO_BASE     |
| 25:00 (t=1500s)    | MISFIRE/QUENCH| 0.148      | 0.852        | FT-02_INJECTOR (91.2%)  | Cyl #2   | 0.8 min      | EMERGENCY_DESCENT_LANDING|
| 35:00 - 46:25      | POST-LANDING | 0.000       | 1.000        | ENGINE SHUTDOWN         | Cyl 0    | 0.0 min      | TOUCHDOWN COMPLETE       |
+-----------------------------------------------------------------------------------------------------------------------------+
```

---

## 2. Key Diagnostic Highlights

1. **Early Weak-Signal Detection (t = 1012s):**
   * Just 12 seconds after injector varnishing begins, the EGT residual on Cylinder #2 rises $+18\ ^\circ\text{C}$ above healthy cross-cylinder spread.
   * Stage 1 Anomaly Detector triggers warning score $\mathcal{A}(t) = 0.288$, prompting power derating to preserve thermal margins.
2. **Accurate Cylinder Isolation:**
   * Stage 2 pinpoints Cylinder #2 as the origin of the thermal asymmetry, with adjacent cylinders (#1, #3, #4) remaining balanced.
3. **Prognostics & Decision Directives:**
   * As nozzle blockage exceeds 20% at $t = 1200\ \text{s}$, the scenario RUL drops to 11.5 minutes, lower than the required return-to-base transit time ($t_{\text{RTB}} = 20\ \text{min}$), prompting an immediate `ABORT_RETURN_TO_BASE` directive.

---

## 3. Visual Artifacts

The 9-panel real-time diagnostic dashboard figure is generated at:
`results/figures/FINAL_DEMO_dashboard.png`

Replay telemetry log is preserved at:
`results/replay/FINAL_DEMO.csv`
