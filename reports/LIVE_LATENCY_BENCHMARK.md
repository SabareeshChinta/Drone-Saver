# Drone Saver — Real-Time Live Streaming Latency Benchmark Report
**Project:** Drone Saver (SIH26054 — DRDO)
**Evaluated Live Packet Count:** 150 packets @ 1.0 Hz

---

## Stage-by-Stage Latency Profiling Table

| Pipeline Processing Stage | Mean Latency (ms) | 95th Percentile Latency (ms) | 99th Percentile Latency (ms) | Budget Limit |
| :--- | :--- | :--- | :--- | :--- |
| **1. Network Ingestion & Packet Validation** | `0.077 ms` | `0.129 ms` | `0.140 ms` | $< 10.0\ \text{ms}$ |
| **2. Airframe Normalization & Calibration** | `0.004 ms` | `0.004 ms` | `0.005 ms` | $< 5.0\ \text{ms}$ |
| **3. Causal Feature & Residual Computation** | `3.028 ms` | `3.932 ms` | `4.131 ms` | $< 15.0\ \text{ms}$ |
| **4. Stage 1: Unsupervised Anomaly Detection** | `19.704 ms` | `24.973 ms` | `26.824 ms` | $< 25.0\ \text{ms}$ |
| **5. Stage 2: Fault Classification & Isolation**| `45.017 ms` | `56.102 ms` | `76.682 ms` | $< 50.0\ \text{ms}$ |
| **6. Stage 3: Scenario RUL Quantile Forecast** | `9.355 ms` | `11.918 ms` | `12.962 ms` | $< 25.0\ \text{ms}$ |
| **7. Stage 4: Mission Risk & Failsafe State Machine**| `0.252 ms` | `0.297 ms` | `0.314 ms` | $< 10.0\ \text{ms}$ |
| **TOTAL END-TO-END LATENCY PER PACKET** | **`77.439 ms`** | **`93.992 ms`** | **`114.988 ms`** | **$< 1,000.0\ \text{ms}$** |

---
### Latency Conclusion:
The complete 7-stage live digital twin pipeline executes in **77.44 ms** per packet on a standard CPU, consuming less than **7.74% of the 1,000 ms frame budget** at 1.0 Hz.