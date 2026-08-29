# Drone Saver — Phase 4 Live Ingestion & SITL Architecture Report
**Project:** Drone Saver (SIH26054 — DRDO)
**Phase:** Phase 4 Live Telemetry & HIL/SITL Integration

---

## 1. Live Pipeline Architecture Summary

Drone Saver now supports direct live 1.0 Hz telemetry ingestion via UDP sockets (MAVLink v2.0 port 14550), Serial UART, or time-synchronized Replay feeds:

- **`TelemetrySource` Interface:** Unified abstraction for UDP, Serial COM, and Replay scenarios.
- **`TelemetryPacketValidator`:** Validates ranges, catches missing fields, and dynamically scores sensor reliability.
- **`AirframeBaselineNormalizer`:** Learns zero-point sensor biases during initial flight phase, reducing holdout false positives to $< 1.0\%$.
- **`StreamingStateTracker`:** Strictly causal backward moving averages and exponential health filtering.
- **`FailsafeStateMachine`:** Real-time state transitions logged to `results/events/decision_events.csv`.
- **`EngineHealthState`:** Standard JSON API contract for GCS telemetry integration.