# Drone Saver — Human-in-the-Loop Decision Architecture
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** Human-in-the-Loop (HITL) Failsafe Command & Confirmation Specification  

---

## 1. Architectural Philosophy: Recommendations vs. Autonomous Action

In military and strategic UAV command and control (C2), autonomous AI systems must **never** execute non-deterministic flight actions (such as in-flight power cut, flight abort, or route alteration) without explicit authorization from the Ground Control Station (GCS) flight commander:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Telemetry Ingestion (1.0 Hz)                                             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. First-Principles Digital Twin & Physics Residuals                        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. 4-Stage AI Engine (Anomaly → Classifier → Scenario RUL → Mission Risk)   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. FAILSAFE RECOMMENDATION GENERATION                                       │
│    • CONTINUE_MISSION / DERATE_POWER / RETURN_TO_BASE / EMERGENCY_LANDING   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. OPERATOR / GCS COMMAND CONFIRMATION (Interactive HITL Interface)         │
│    • [ ✓ CONFIRM RECOMMENDATION ]     [ ✗ REJECT & MAINTAIN MONITORING ]    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                  ┌────────────────────┴────────────────────┐
                  ▼                                         ▼
┌───────────────────────────────────┐     ┌───────────────────────────────────┐
│ IF OPERATOR CONFIRMS:             │     │ IF OPERATOR REJECTS:              │
│ State = OPERATOR_CONFIRMED        │     │ State = OPERATOR_REJECTED         │
│ Simulated Action = SIMULATED_RTB  │     │ Simulated Action = NONE           │
│ Autopilot flies diversion profile │     │ Continue passive health monitoring│
└───────────────────────────────────┘     └───────────────────────────────────┘
```

---

## 2. Decoupled State Variable Schema

To prevent semantic conflation between engine physics and operational commands, Drone Saver strictly separates:

1. **`engine_state`:** The thermodynamic health state of the propulsion plant:
   * `HEALTHY` ($H \ge 0.85$, residuals near zero)
   * `ADVISORY` ($0.50 \le H < 0.85$, developing thermal asymmetry)
   * `WARNING` ($0.35 \le H < 0.50$, loiter survival deficit)
   * `CRITICAL` ($H < 0.35$ or catastrophic detonation / oil loss)
2. **`mission_recommendation`:** The AI failsafe recommendation:
   * `CONTINUE_MISSION`
   * `DERATE_POWER` (65% throttle recommendation)
   * `RETURN_TO_BASE` (Abort loiter and RTB)
   * `EMERGENCY_LANDING` (Immediate descent and recovery)
3. **`operator_decision`:** The human-in-the-loop authorization state:
   * `MONITORING` (Nominal steady-state flight)
   * `PENDING` (Failsafe recommendation awaits operator confirmation)
   * `CONFIRMED` (Operator approved the recommendation)
   * `REJECTED` (Operator rejected the recommendation)
4. **`simulated_action`:** The simulated autopilot execution:
   * `NONE`
   * `SIMULATED_POWER_DERATE`
   * `SIMULATED_RTB_ACTION`
   * `SIMULATED_EMERGENCY_DIVERSION`

---

## 3. Auditable Event Logging Contract

Every state transition and operator decision is recorded in [`results/events/decision_events.csv`](file:///c:/Users/chint/Drone%20Saver/results/events/decision_events.csv):

```csv
timestamp_utc,time_seconds,engine_state,health_score,anomaly_score,fault_type,fault_probability,scenario_rul_sec,mission_success_probability,recommended_action,operator_action,simulated_action,event_type
2026-08-30T10:00:31Z,120.0,WARNING,0.450,0.880,FT-02_INJECTOR_CLOGGING,0.920,850.0,0.350,RETURN_TO_BASE,PENDING,NONE,RECOMMENDATION_CHANGE
2026-08-30T10:00:34Z,123.0,WARNING,0.440,0.890,FT-02_INJECTOR_CLOGGING,0.925,840.0,0.340,RETURN_TO_BASE,CONFIRMED,SIMULATED_RTB_ACTION,OPERATOR_DECISION_CONFIRMED
```
