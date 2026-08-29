"""
Drone Saver - Temporal Degradation Envelopes & Physical Transition Profiles
Implements deterministic, continuous temporal profiles:
- Step activation
- Linear progressive ramp
- First-order thermal/hydraulic exponential lag
- Harmonic valve rotation oscillation
Problem Statement: SIH26054 - DRDO
"""

import numpy as np

def step_profile(time_array, onset_sec):
    """Instantaneous step activation envelope."""
    return np.where(time_array >= onset_sec, 1.0, 0.0)

def linear_ramp_profile(time_array, onset_sec, duration_sec):
    """Continuous linear progression from 0.0 to 1.0 over duration_sec."""
    t_rel = np.maximum(0.0, time_array - onset_sec)
    ramp = np.minimum(1.0, t_rel / max(1.0, duration_sec))
    return np.where(time_array >= onset_sec, ramp, 0.0)

def exponential_lag_profile(time_array, onset_sec, time_constant_sec):
    """First-order thermal or hydraulic dynamic response envelope: 1 - exp(-t / tau)."""
    t_rel = np.maximum(0.0, time_array - onset_sec)
    resp = 1.0 - np.exp(-t_rel / max(0.1, time_constant_sec))
    return np.where(time_array >= onset_sec, resp, 0.0)

def rotational_oscillation_profile(time_array, onset_sec, frequency_hz=0.07, phase_rad=0.0):
    """Harmonic sinusoidal envelope representing periodic mechanical rotation (e.g. exhaust valve)."""
    mask = np.where(time_array >= onset_sec, 1.0, 0.0)
    t_rel = np.maximum(0.0, time_array - onset_sec)
    osc = np.sin(2.0 * np.pi * frequency_hz * t_rel + phase_rad)
    return osc * mask
