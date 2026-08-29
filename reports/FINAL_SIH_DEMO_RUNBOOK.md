# Drone Saver — Flagship SIH 2026 Presentation Runbook
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** 60-Second Flagship Demonstration Script, Team Narration & Judge Q&A Guide  

---

## 1. Quick Startup Commands

To launch the complete Drone Saver Aerospace Ground Control Station:

```bash
# 1. Start the GCS Backend Server (Runs completely offline on localhost)
python src/dashboard/server.py

# 2. Open your web browser at:
# http://127.0.0.1:8000
```

---

## 2. 60-Second Flagship Demonstration Script

Set replay speed to **`2.0x`** or click **`[ ▶ RUN FLAGSHIP SIH DEMO ]`**:

| Time (Replay) | Visual State on Dashboard | Spoken Team Narration |
| :--- | :--- | :--- |
| **0:00 – 0:10** | Top directive: `🟢 CONTINUE MISSION`. All 4 cylinder cards show green `NORM`. Observed EGT matches blue physics baseline. | *"Drone Saver learns the nominal operating behavior of an aircraft piston engine from authentic 1.0 Hz telemetry using a first-principles thermodynamic digital twin."* |
| **0:10 – 0:20** | At $t = 60\ \text{s}$, EGT on Cylinder #2 begins drifting upward ($+18^\circ\text{C}$). Blue baseline curve stays steady. | *"A physically modeled fuel injector restriction begins on Cylinder #2, causing the observed exhaust temperature to diverge from the physics baseline."* |
| **0:20 – 0:30** | Stage 1 Isolation Forest flags an anomaly ($t = 72\ \text{s}$). Directive box shifts to yellow: `🟡 DERATE POWER / REDUCE LOITER`. | *"The digital twin detects that the observed thermodynamic behavior is diverging from expected energy balances and immediately recommends power derating to 65%."* |
| **0:30 – 0:40** | Cylinder #2 card turns red (`CRIT`). Diagnostics panel displays `FT-02: Fuel Injector Restriction` ($91.2\%$ confidence) on `Cylinder #2`. | *"Stage 2 gradient-boosted trees identify the failure mode as Fuel Injector Restriction and pinpoint Cylinder #2 without false alarms on adjacent cylinders."* |
| **0:40 – 0:50** | Health score $H(t)$ decays along the trajectory chart. RUL panel displays: `Scenario Time-to-Critical: 14.2 min [11.8–19.5 min 90% CI]`. | *"Stage 3 tracks the continuous degradation trajectory and forecasts the Scenario Time-to-Critical as 14.2 minutes with 90% confidence bounds."* |
| **0:50 – 1:00** | Monte Carlo loiter survival probability drops below 75% for the 24-minute mission. Directive banner transitions to `🟠 RETURN TO BASE (RTB)`. | *"Because the remaining mission requires 24 minutes but engine time-to-critical is 14 minutes, the failsafe engine issues an autonomous RETURN TO BASE recommendation, saving the strategic UAV."* |

---

## 3. Technical Judge Q&A Defense Guide

### Q1: "Is this trained on real UAV military engine data?"
> **Defense:** *"No, we strictly do not fabricate or claim access to classified DRDO test-cell data. We train our baselines on 28,907 seconds of real general-aviation aero-piston telemetry from the NGAFID archive (Lycoming IO-360 on Garmin G1000). We then inject 9 differential thermodynamic failure modes based on SAE/FAA physics equations. The entire pipeline is designed to plug directly into DRDO test-cell telemetry without architectural changes."*

### Q2: "Why not use a standard deep learning LSTM or Autoencoder?"
> **Defense:** *"Deep learning autoencoders act as black boxes with high edge computational overhead and vulnerability to unphysical hallucinations. Drone Saver uses first-principles thermodynamic energy balance equations as the baseline, feeding structured physics residuals into Isolation Forests and Quantile Gradient Boosted Trees. This guarantees physical explainability, zero GPU dependency, and an inference latency of just 66.7 ms on a standard CPU."*

### Q3: "What is the difference between RUL and Scenario Time-to-Critical?"
> **Defense:** *"True RUL measures material fatigue and mechanical component lifing across hundreds of flight hours. Our models estimate Scenario Time-to-Critical: the exact time remaining during an active mission before an overheating cylinder or collapsing oil pressure crosses safety redlines ($T_{\text{CHT}} > 224^\circ\text{C}$ or $P_{\text{oil}} < 172\ \text{kPa}$)."*

### Q4: "How does the system handle different aircraft airframes without retraining?"
> **Defense:** *"Phase 3 discovered that uncalibrated airframe sensor depths caused a 13% false alarm rate. We developed an autonomous Airframe Baseline Normalizer that learns zero-point thermocouple offsets during the initial 60 seconds of flight, centering residual vectors and reducing false positives to < 1.0%."*

---

## 4. Reset & Emergency Recovery Procedure

* **Resetting the Demo:** Click `[ ↺ RESET ]` on the bottom GCS bar. This deterministically clears all chart points, resets the state machine to `HEALTHY`, and restarts the flagship scenario at $t = 0\ \text{s}$.
* **Refreshing Browser:** Hit `F5`. The local backend server maintains state streaming independently.
