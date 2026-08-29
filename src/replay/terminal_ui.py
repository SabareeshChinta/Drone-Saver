"""
Drone Saver - Live Terminal Replay Dashboard & Telemetry UI
Renders real-time avionics telemetry gauges, fault probabilities,
scenario RUL forecasts, and failsafe decision support.
Problem Statement: SIH26054 - DRDO
"""

import os
import sys

class TerminalDashboardUI:
    def __init__(self):
        # ANSI escape codes for styling
        self.RESET = "\033[0m"
        self.BOLD = "\033[1m"
        self.GREEN = "\033[32m"
        self.YELLOW = "\033[33m"
        self.RED = "\033[31m"
        self.CYAN = "\033[36m"
        self.MAGENTA = "\033[35m"
        self.BG_RED = "\033[41m\033[37m"
        self.BG_YELLOW = "\033[43m\033[30m"
        self.BG_GREEN = "\033[42m\033[30m"
        
    def _format_bar(self, val, length=20, fill_char="■", empty_char="·"):
        fill_len = int(np.clip(val, 0.0, 1.0) * length)
        return fill_char * fill_len + empty_char * (length - fill_len)
        
    def render_frame(self, state_dict):
        """
        Renders a single frame of the live Digital Twin diagnostic dashboard.
        """
        t_sec = state_dict.get('time_seconds', 0)
        tot_sec = state_dict.get('total_mission_sec', 7200)
        
        hrs = int(t_sec // 3600)
        mins = int((t_sec % 3600) // 60)
        secs = int(t_sec % 60)
        time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        
        tot_hrs = int(tot_sec // 3600)
        tot_mins = int((tot_sec % 3600) // 60)
        tot_str = f"{tot_hrs:02d}:{tot_mins:02d}:00"
        
        scenario_id = state_dict.get('scenario_id', 'MISSION_DEMO')
        alt_ft = state_dict.get('altitude_m', 0.0) * 3.28084
        ias_kt = state_dict.get('airspeed_mps', 0.0) * 1.94384
        rpm = state_dict.get('rpm', 0.0)
        map_kpa = state_dict.get('map_kpa', 0.0)
        
        health_score = state_dict.get('health_score', 1.0)
        anom_score = state_dict.get('anomaly_score', 0.0)
        top_fault = state_dict.get('predicted_fault', 'HEALTHY')
        fault_prob = state_dict.get('fault_probability', 1.0)
        top_cyl = state_dict.get('predicted_cylinder', 0)
        
        rul_min = state_dict.get('scenario_rul_sec', 0.0) / 60.0
        rem_min = state_dict.get('remaining_mission_sec', 0.0) / 60.0
        p_success = state_dict.get('p_mission_success', 1.0)
        decision = state_dict.get('decision', 'CONTINUE_MISSION')
        
        # Color coding
        if health_score >= 0.80:
            h_color = self.GREEN
            eng_state = "NOMINAL (HEALTHY)"
            dec_banner = f"{self.BG_GREEN}  [DIRECTIVE: CONTINUE MISSION - MAINTAIN SCHEDULED LOITER]  {self.RESET}"
        elif health_score >= 0.50:
            h_color = self.YELLOW
            eng_state = "DEGRADED (CAUTION)"
            dec_banner = f"{self.BG_YELLOW}  [DIRECTIVE: DERATE THROTTLE TO 65% & MONITOR THERMALS]  {self.RESET}"
        else:
            h_color = self.RED
            eng_state = "CRITICAL FAILURE IMMINENT"
            dec_banner = f"{self.BG_RED}  [DIRECTIVE: ABORT LOITER - INITIATE IMMEDIATE RTB NAVIGATION]  {self.RESET}"
            
        cyl_str = f"Cylinder #{top_cyl}" if top_cyl > 0 else "Global Engine (All Cylinders)"
        
        output = [
            f"{self.CYAN}================================================================================{self.RESET}",
            f"{self.BOLD}             DRONE SAVER — AI DIGITAL TWIN MISSION DIAGNOSTICS                  {self.RESET}",
            f"{self.CYAN}================================================================================{self.RESET}",
            f"  SCENARIO: {self.BOLD}{scenario_id}{self.RESET} | TIME: {time_str} / {tot_str} | ALT: {alt_ft:,.0f} ft | IAS: {ias_kt:.0f} kt",
            f"  RPM: {rpm:.0f} | MAP: {map_kpa:.1f} kPa | ENGINE STATUS: {h_color}{self.BOLD}{eng_state}{self.RESET}",
            f"--------------------------------------------------------------------------------",
            f"  ENGINE HEALTH INDEX H(t) : {h_color}{health_score:.3f}{self.RESET}  [{self.GREEN}{'='*int(health_score*25)}{'.'*(25-int(health_score*25))}{self.RESET}]",
            f"  ANOMALY RESIDUAL SCORE   : {self.RED if anom_score > 0.5 else self.CYAN}{anom_score:.3f}{self.RESET}  [{self.RED}{'='*int(anom_score*25)}{'.'*(25-int(anom_score*25))}{self.RESET}]",
            f"--------------------------------------------------------------------------------",
            f"  PRIMARY DIAGNOSED FAULT  : {self.BOLD}{top_fault}{self.RESET} (Confidence: {fault_prob*100:.1f}%)",
            f"  ISOLATED ENGINE COMPONENT: {self.BOLD}{cyl_str}{self.RESET}",
            f"--------------------------------------------------------------------------------",
            f"  SCENARIO TIME-TO-LIMIT   : {self.BOLD}{rul_min:.1f} min{self.RESET} (Simulated Redline Margin)",
            f"  SCHEDULED MISSION REMAIN : {rem_min:.1f} min",
            f"  SURVIVAL PROBABILITY     : {self.BOLD}{p_success*100:.1f}%{self.RESET} (Monte Carlo 1,000 runs)",
            f"--------------------------------------------------------------------------------",
            f"  {dec_banner}",
            f"{self.CYAN}================================================================================{self.RESET}\n"
        ]
        return "\n".join(output)
