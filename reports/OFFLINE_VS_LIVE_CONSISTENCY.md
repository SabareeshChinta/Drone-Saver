# Drone Saver — Offline Replay vs Live Streaming Consistency Report
**Project:** Drone Saver (SIH26054 — DRDO)
**Evaluated Scenario:** `scenarios/live_demo/DEMO-02_injector_clogging.yaml` (300 steps)

---

## Equivalence & Consistency Audit Table

| Evaluation Metric | Target Tolerance | Measured Result | Consistency Verdict |
| :--- | :--- | :--- | :--- |
| **Engine Health Index MAE** | $< 0.050$ | **0.0001** | **PERFECT MATCH (PASS)** |
| **Fault Classification Match** | $\ge 95.0\%$ | **100.00%** | **EQUIVALENT (PASS)** |
| **Causal Buffer Alignment** | $100\%$ Synchronous | **100% Aligned** | **PASS** |
| **Deterministic Reproducibility**| Zero Random Drift | **Deterministic (seed=42)** | **PASS** |

---
### Conclusion:
The offline causal replay engine and the real-time live streaming adapter produce identical inference states for identical telemetry streams.