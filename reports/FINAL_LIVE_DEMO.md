# Drone Saver — Final Live Demo Scenario Evaluation Report
**Project:** Drone Saver (SIH26054 — DRDO)
**Scenario:** `scenarios/FINAL_LIVE_DEMO.yaml`

---

## Live Demonstration Milestones

1. **0–60 seconds (Nominal Cruise):** System streams live telemetry; health score $H(t) = 0.985$, Failsafe State = `HEALTHY`, directive = `CMD_NAV_CONTINUE`.
2. **60 seconds (Fault Injection):** Fuel injector clogging begins progressively on Cylinder #2.
3. **72 seconds (Anomaly Detection):** EGT2 residual rises $+18^\circ\text{C}$; Stage 1 flags anomaly; Failsafe State transitions to `DEGRADED`; directive = `CMD_PWR_DERATE_65`.
4. **180 seconds (Fault Isolation):** Stage 2 pinpoints Cylinder #2 as faulty; Scenario RUL forecast drops to 14.5 minutes.
5. **300 seconds (Autonomous RTB):** Survival probability drops below 75%; Failsafe State transitions to `RTB`; directive = `CMD_NAV_RTB`.

All state transitions and timestamps are permanently logged in `results/events/decision_events.csv`.