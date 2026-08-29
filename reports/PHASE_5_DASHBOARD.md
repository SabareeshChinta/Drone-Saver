# Drone Saver — Phase 5 Interactive Operator Dashboard & GCS Report
**Project:** Drone Saver (SIH26054 — DRDO)  
**Document:** Interactive Ground Control Station (GCS) Operator Dashboard Architecture  

---

## 1. Dashboard Architecture & Interface

The Drone Saver Operator Interface is designed for high-consequence UAV command and control (C2):

```
┌────────────────────────────────────────────────────────┐
│   Drone Saver Live 4-Stage AI Digital Twin Engine      │
└──────────────────────────┬─────────────────────────────┘
                           │ 1.0 Hz Structured JSON
                           ▼
┌────────────────────────────────────────────────────────┐
│     FastAPI SSE & REST Backend (src/dashboard/server.py│
└──────────────────────────┬─────────────────────────────┘
                           │ Server-Sent Events (SSE)
                           ▼
┌────────────────────────────────────────────────────────┐
│    Responsive GCS Operator Dashboard (dashboard/)       │
│  - Real-Time SVG Dials & Multi-Cylinder Thermal Head   │
│  - AI Diagnostic Confidence & Physical Indicators      │
│  - Scenario Time-to-Critical (with 90% CI bounds)      │
│  - Prominent Autopilot Failsafe Directives             │
│  - Interactive Scenario Controller & Speed Multipliers │
└────────────────────────────────────────────────────────┘
```

---

## 2. Key Interface Panels

1. **Top Telemetry Status Bar:**
   * Displays Engine Health (%), Anomaly Score, Mission Risk (%), Telemetry Link Status, Measured Inference Latency (~65 ms), and Data Provenance (`REAL NGAFID G1000` / `REAL TELEMETRY + INJECTED FAULT`).
2. **Master Autopilot Directive Banner:**
   * High-contrast color-coded directive:
     - `🟢 CONTINUE MISSION`
     - `🟡 DERATE POWER / REDUCE LOITER`
     - `🟠 RETURN TO BASE (RTB)`
     - `🔴 EMERGENCY DESCENT & LANDING`
3. **4-Cylinder Thermal Head Health:**
   * Individual Cylinder Head visualization (Cyl 1–4) reporting EGT, CHT, and cross-cylinder deviation from mean ($\delta T$).
   * Dynamically highlights the affected cylinder in red with pulsing glow during single-cylinder failure modes.
4. **AI Diagnostics & Contributing Physical Indicators:**
   * Diagnosed Failure Mode (e.g. `FT-02 — Fuel Injector Degradation`).
   * Diagnostic Probability Bar (e.g. $91.2\%$).
   * Physical Evidence meters showing EGT cross-cylinder spread, CHT deviation, and oil pressure residual.
5. **Scenario Time-to-Critical (Scenario RUL):**
   * Clear countdown of simulated time remaining before reaching redline limits with dynamic 90% confidence uncertainty interval bounds $[t_{\text{low}}, t_{\text{high}}]$.
6. **Digital Twin Baseline vs. Observed Charts:**
   * Dynamic Chart.js multi-line timeline comparing Observed EGT/CHT against First-Principles Physics Baseline with dynamic onset markers.
7. **Mode Switching:**
   * **`⚖️ JUDGE VIEW`:** Clean, distraction-free high-level executive summary.
   * **`⚙️ ENGINEERING VIEW`:** Full telemetry charts, polynomial residuals, and sensor reliability details.

---

## 3. Technology Stack & Edge Footprint

* **Backend:** FastAPI + Uvicorn (Pure Python, zero external binary daemon requirements).
* **Frontend:** Standalone HTML5 / Modern CSS3 / Vanilla JS / Chart.js (Zero Node.js/npm dependencies; runs 100% offline).
* **Alternative Python UI:** Streamlit (`src/dashboard/app.py`).
* **RAM Footprint:** $< 180\ \text{MB}$ total active memory.
* **UI Update Latency:** $< 12\ \text{ms}$ DOM rendering overhead.
