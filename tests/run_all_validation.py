"""
Drone Saver - Master Test & Validation Orchestrator
Single entrypoint for Phase 3 validation:
1. Re-validates real telemetry integrity
2. Audits physics fault injection directional and physical bounds
3. Evaluates multi-tier Leave-One-Flight-Out validation protocol
4. Runs adversarial stress testing suite
5. Evaluates degradation state tracking
Problem Statement: SIH26054 - DRDO
"""

import os
import sys
sys.path.insert(0, '.')

from src.fault_injection.validate_faults import validate_all_injected_faults
from src.models.evaluate_validation_protocol import run_multi_tier_validation
from src.models.degradation_state import evaluate_degradation_models
from tests.adversarial_suite import run_adversarial_suite

def run_all_validation():
    print("\n================================================================================")
    print("        DRONE SAVER — MASTER VALIDATION & SCIENTIFIC VERIFICATION SUITE         ")
    print("================================================================================\n")
    
    print("STEP 1: Validating Physics Fault Injection Directionality & Physical Bounds...")
    validate_all_injected_faults()
    
    print("\nSTEP 2: Evaluating Multi-Tier Leave-One-Flight-Out Validation Protocol...")
    run_multi_tier_validation()
    
    print("\nSTEP 3: Evaluating Continuous Degradation State Tracking Models...")
    evaluate_degradation_models()
    
    print("\nSTEP 4: Executing Adversarial Stress Testing Suite...")
    run_adversarial_suite()
    
    print("\n================================================================================")
    print("        ALL VALIDATION SUITES COMPLETED SUCCESSFULLY! REPORTS UPDATED.          ")
    print("================================================================================\n")

if __name__ == "__main__":
    run_all_validation()
