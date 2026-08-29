# Drone Saver — SIH 2026 Grand Finale Master Presentation Runbook
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** Live Demonstration Script, Team Roles, Commands & Speech Guidelines  

---

## 1. Quick Launch Commands

To start the complete Drone Saver GCS Operator Dashboard for the jury:

```bash
# Terminal 1: Launch Drone Saver Real-Time GCS Server
python src/dashboard/server.py

# Open browser at: http://127.0.0.1:8000
```

*(Optional Streamlit Alternative: `streamlit run src/dashboard/app.py`)*

---

## 2. 3-Minute Live Demonstration Script

```
   00:00 ──────────────── 00:45 ──────────────── 01:15 ──────────────── 01:45 ──────────────── 03:00
  [Nominal Cruise]       [Fault Injection]      [Anomaly & Derate]     [Fault & Cylinder]     [Autonomous RTB]
```

### Phase 1: Nominal Flight (0:00 – 0:45)
* **Action:** Click `[ ▶ RUN FINAL SIH DEMO ]` or `[ HEALTHY ]`. Replay speed set to `2.0x`.
* **Visual State:** Top directive is `🟢 CONTINUE MISSION`. 4-cylinder health badges are all green (`NORMAL`). Observed temperatures track the physics baseline curve with near-zero residuals.
* **Speaker 1 (Systems Lead):**  
  > *"Respected Jury, we present Drone Saver, a physics-informed AI digital twin for aero-piston UAVs. Right now, our system is ingesting 1.0 Hz flight telemetry from an authentic aero-piston aircraft. Notice how our first-principles thermodynamic model predicts expected cylinder head and exhaust gas temperatures in real time. Because thermal residuals are near zero, our engine health index is 98.5% and the autopilot directive is CONTINUE MISSION."*

---

### Phase 2: Fault Injection & Early Anomaly Detection (0:45 – 1:15)
* **Action:** At $t = 60\ \text{s}$, progressive fuel injector clogging begins on Cylinder #2.
* **Visual State:** EGT2 starts drifting upward ($+18^\circ\text{C}$). Stage 1 Isolation Forest flags an anomaly at $t = 72\ \text{s}$. Directive banner instantly turns yellow (`🟡 DERATE POWER / REDUCE LOITER`).
* **Speaker 2 (AI & Physics Lead):**  
  > *"At $t=60$ seconds, an in-flight fuel injector restriction develops on Cylinder #2. Rather than relying on rigid threshold alarms that only trigger when an engine is about to fail, our AI digital twin detects the thermodynamic residual divergence within 12 seconds. The health index begins decaying, and the autopilot immediately recommends DERATING THROTTLE TO 65% to protect the cylinder."*

---

### Phase 3: Fault Isolation & Cylinder Localization (1:15 – 1:45)
* **Action:** Cylinder #2 box pulses in red with `CRITICAL` badge. AI panel displays `FT-02 — Fuel Injector Degradation (91.2% Confidence)` on `CYLINDER #2`.
* **Visual State:** Physical evidence meters show EGT cross-cylinder spread expanding to $48^\circ\text{C}$. Scenario time-to-critical drops to `14.2 min [11.8 – 19.5 min 90% CI]`.
* **Speaker 3 (Propulsion & Reliability Lead):**  
  > *"Stage 2 gradient-boosted trees classify the failure mode as Fuel Injector Degradation with 91% confidence, pinpointing Cylinder #2 without false alarms on healthy adjacent runners. Stage 3 calculates our Scenario Time-to-Critical as 14.2 minutes with full 90% confidence uncertainty bounds."*

---

### Phase 4: Mission Risk Assessment & Autonomous RTB (1:45 – 2:30)
* **Action:** Mission success probability decays below $75\%$. Directive banner shifts to orange (`🟠 RETURN TO BASE`). Event is logged in `results/events/decision_events.csv`.
* **Speaker 1 (Conclusion):**  
  > *"Because the remaining mission requires 24 minutes but our engine time-to-critical is 14 minutes, our Monte Carlo risk engine determines mission survival probability is under 75%. The state machine autonomously issues a RETURN TO BASE directive, saving the multimillion-rupee UAV and its strategic payload. All of this runs locally on a student laptop with < 70 ms CPU latency and zero GPU requirements."*

---

## 3. Team Member Roles

| Team Member | Role | Key Talking Points |
| :--- | :--- | :--- |
| **Member 1 (Presenter)** | Mission & Architecture | Problem statement SIH26054 (DRDO), MALE UAVs (Rustom/Tapas), GCS decisions |
| **Member 2 (AI/Data Lead)** | Physics Digital Twin | NGAFID authentic telemetry, polynomial physics baselines, residual space, LOFO benchmarks |
| **Member 3 (Systems Lead)** | Replay & Failsafe FSM | Causal streaming, zero temporal leakage, Monte Carlo survival risk, edge compute latency |

---

## 4. Emergency Backup / Recovery Procedures

1. **Browser Freezes or Glitches:**  
   Refresh the browser page (`F5`). The backend continues running independently; the frontend will reconnect instantly via SSE.
2. **Scenario Reset Needed:**  
   Click `[ ↺ RESET ]` on the bottom toolbar or hit `POST /api/control/reset`.
3. **No Internet Access at Venue:**  
   The system is **100% self-contained and offline-ready**. All assets, models, and dependencies run locally on `localhost:8000`.
