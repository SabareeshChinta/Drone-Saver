# Drone Saver — Time Series Quality Verification Report
**Project:** Drone Saver (SIH26054 — DRDO)
**Phase:** Phase 1 Telemetry Data Validation

---

## Executive Time-Series Integrity Summary

|   flight_id | canonical_file          |   samples |   duration_s | strictly_monotonic   |   duplicate_time_records |   negative_time_jumps |   median_dt_s |   std_dt_s |   telemetry_gaps_gt_2s |   max_gap_s |
|------------:|:------------------------|----------:|-------------:|:---------------------|-------------------------:|----------------------:|--------------:|-----------:|-----------------------:|------------:|
|         nan | flight_01_canonical.csv |      2786 |         2786 | True                 |                        0 |                     0 |             1 |          0 |                      0 |           1 |
|         nan | flight_02_canonical.csv |      2842 |         2842 | True                 |                        0 |                     0 |             1 |          0 |                      0 |           1 |
|         nan | flight_03_canonical.csv |      4411 |         4411 | True                 |                        0 |                     0 |             1 |          0 |                      0 |           1 |
|         nan | flight_04_canonical.csv |      8113 |         8113 | True                 |                        0 |                     0 |             1 |          0 |                      0 |           1 |
|         nan | flight_05_canonical.csv |     10755 |        10755 | True                 |                        0 |                     0 |             1 |          0 |                      0 |           1 |


## Verification: `nan` (flight_01_canonical.csv)
- **Total Time-Series Steps:** 2,786 rows
- **Continuous Time Monotonicity:** PASS (100% strictly increasing)
- **Duplicate Time Records:** 0
- **Negative Time Discontinuities:** 0
- **Sampling Frequency Distribution:** Median = 1.0 s (1.000 Hz), Standard Deviation = 0.000000 s
- **Telemetry Gap Count (> 2s):** 0
- **Maximum Observed Delta-T:** 1.0 s
- **Time Series Integrity Status:** **PRISTINE (Ideal for 1 Hz State-Space / Digital Twin Modeling)**
---

## Verification: `nan` (flight_02_canonical.csv)
- **Total Time-Series Steps:** 2,842 rows
- **Continuous Time Monotonicity:** PASS (100% strictly increasing)
- **Duplicate Time Records:** 0
- **Negative Time Discontinuities:** 0
- **Sampling Frequency Distribution:** Median = 1.0 s (1.000 Hz), Standard Deviation = 0.000000 s
- **Telemetry Gap Count (> 2s):** 0
- **Maximum Observed Delta-T:** 1.0 s
- **Time Series Integrity Status:** **PRISTINE (Ideal for 1 Hz State-Space / Digital Twin Modeling)**
---

## Verification: `nan` (flight_03_canonical.csv)
- **Total Time-Series Steps:** 4,411 rows
- **Continuous Time Monotonicity:** PASS (100% strictly increasing)
- **Duplicate Time Records:** 0
- **Negative Time Discontinuities:** 0
- **Sampling Frequency Distribution:** Median = 1.0 s (1.000 Hz), Standard Deviation = 0.000000 s
- **Telemetry Gap Count (> 2s):** 0
- **Maximum Observed Delta-T:** 1.0 s
- **Time Series Integrity Status:** **PRISTINE (Ideal for 1 Hz State-Space / Digital Twin Modeling)**
---

## Verification: `nan` (flight_04_canonical.csv)
- **Total Time-Series Steps:** 8,113 rows
- **Continuous Time Monotonicity:** PASS (100% strictly increasing)
- **Duplicate Time Records:** 0
- **Negative Time Discontinuities:** 0
- **Sampling Frequency Distribution:** Median = 1.0 s (1.000 Hz), Standard Deviation = 0.000000 s
- **Telemetry Gap Count (> 2s):** 0
- **Maximum Observed Delta-T:** 1.0 s
- **Time Series Integrity Status:** **PRISTINE (Ideal for 1 Hz State-Space / Digital Twin Modeling)**
---

## Verification: `nan` (flight_05_canonical.csv)
- **Total Time-Series Steps:** 10,755 rows
- **Continuous Time Monotonicity:** PASS (100% strictly increasing)
- **Duplicate Time Records:** 0
- **Negative Time Discontinuities:** 0
- **Sampling Frequency Distribution:** Median = 1.0 s (1.000 Hz), Standard Deviation = 0.000000 s
- **Telemetry Gap Count (> 2s):** 0
- **Maximum Observed Delta-T:** 1.0 s
- **Time Series Integrity Status:** **PRISTINE (Ideal for 1 Hz State-Space / Digital Twin Modeling)**
---