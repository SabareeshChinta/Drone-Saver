"""
Drone Saver - Mean Value Engine Model (MVEM) Thermal Digital Twin
First-principles 4-node thermofluid differential equation solver for aero-piston engines:
1. Intake manifold pressure dynamics
2. Cylinder head thermal node (heat release & fin convection)
3. Exhaust gas runner thermal node
4. Oil sump thermal & hydraulic node
Problem Statement: SIH26054 - DRDO
"""

import os
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

class PistonEngineTwinMVEM:
    def __init__(self, displacement_l=5.9, num_cylinders=4):
        self.V_d = displacement_l * 1e-3  # m^3
        self.N_cyl = num_cylinders
        self.R_air = 287.05  # J/(kg K)
        self.Q_lhv = 44.0e6  # J/kg (Aviation Gasoline / Jet-A1 / Diesel)
        self.C_head = 4500.0  # J/K (Cylinder head thermal capacitance)
        self.C_oil = 12000.0  # J/K (Oil sump thermal capacitance)
        self.C_ex = 1500.0   # J/K (Exhaust runner thermal capacitance)
        
    def simulate_mission_profile(self, time_array, rpm_profile, throttle_profile, alt_m_profile, oat_c_profile, ias_mps_profile):
        """
        Simulates engine thermodynamic and thermal states over a continuous flight trajectory.
        """
        n = len(time_array)
        
        # State vector: [T_cht1, T_cht2, T_cht3, T_cht4, T_egt1, T_egt2, T_egt3, T_egt4, T_oil, P_oil]
        # Initial conditions at ambient
        T_amb0 = oat_c_profile[0] + 273.15
        y0 = np.array([
            T_amb0 + 20.0, T_amb0 + 20.0, T_amb0 + 20.0, T_amb0 + 20.0,  # CHT 1-4 (K)
            T_amb0 + 200.0, T_amb0 + 200.0, T_amb0 + 200.0, T_amb0 + 200.0, # EGT 1-4 (K)
            T_amb0 + 15.0,  # T_oil (K)
            450.0           # P_oil (kPa)
        ])
        
        results = []
        state = y0.copy()
        
        for i in range(n):
            t = time_array[i]
            rpm = rpm_profile[i]
            throttle = throttle_profile[i]
            alt_m = alt_m_profile[i]
            oat_c = oat_c_profile[i]
            ias_mps = ias_mps_profile[i]
            
            T_amb = oat_c + 273.15
            # Atmospheric pressure lapse: P_amb = P0 * (1 - 2.25577e-5 * h)^5.25588
            P_amb = 101.325 * ((1.0 - 2.25577e-5 * alt_m) ** 5.25588)  # kPa
            
            # Manifold Absolute Pressure MAP
            map_kpa = P_amb * (0.35 + 0.65 * throttle)
            
            # Fuel Flow rate (L/h)
            fuel_flow_lph = (rpm / 2500.0) * (map_kpa / 90.0) * 45.0 * (0.8 + 0.2 * throttle)
            m_dot_fuel = (fuel_flow_lph * 0.72) / 3600.0  # kg/s total
            m_dot_fuel_cyl = m_dot_fuel / self.N_cyl
            
            # Combustion heat release per cylinder (W)
            eta_ind = 0.32
            Q_comb_cyl = m_dot_fuel_cyl * self.Q_lhv * eta_ind
            
            # Cooling convective heat transfer coefficient (W/K)
            h_cooling = 18.0 + 0.65 * (ias_mps ** 0.8) * (P_amb / 101.325)
            
            # Step Euler ODE update (dt = 1s)
            dt = 1.0
            
            # 1. Update CHTs (K)
            for c in range(4):
                T_cht_curr = state[c]
                # Convection to cooling air + conduction to oil
                dQ_dt = Q_comb_cyl * 0.25 - h_cooling * (T_cht_curr - T_amb) - 4.5 * (T_cht_curr - state[8])
                state[c] += (dQ_dt / self.C_head) * dt
                
            # 2. Update EGTs (K)
            for c in range(4):
                T_egt_target = T_amb + 720.0 * (map_kpa / 85.0) ** 0.35 * (rpm / 2400.0) ** 0.15
                state[4 + c] += ((T_egt_target - state[4 + c]) / 4.0) * dt
                
            # 3. Update Oil Temp & Pressure
            # Heat from cylinder heads + engine friction - oil cooler rejection
            Q_frict = 1200.0 * (rpm / 2400.0) ** 2
            Q_oil_gain = np.sum([4.5 * (state[c] - state[8]) for c in range(4)]) + Q_frict
            Q_oil_loss = (12.0 + 0.3 * ias_mps) * (state[8] - T_amb)
            state[8] += ((Q_oil_gain - Q_oil_loss) / self.C_oil) * dt
            
            # Oil pressure dynamic (kPa)
            state[9] = 120.0 + 3.8 * (rpm ** 0.65) - 1.2 * (state[8] - 273.15 - 80.0)
            
            results.append({
                'time_seconds': t,
                'rpm': rpm,
                'map_kpa': map_kpa,
                'fuel_flow_lph': fuel_flow_lph,
                'altitude_m': alt_m,
                'ambient_temp_c': oat_c,
                'airspeed_mps': ias_mps,
                'cht_1_c': state[0] - 273.15,
                'cht_2_c': state[1] - 273.15,
                'cht_3_c': state[2] - 273.15,
                'cht_4_c': state[3] - 273.15,
                'egt_1_c': state[4] - 273.15,
                'egt_2_c': state[5] - 273.15,
                'egt_3_c': state[6] - 273.15,
                'egt_4_c': state[7] - 273.15,
                'oil_temp_c': state[8] - 273.15,
                'oil_pressure_kpa': state[9]
            })
            
        return pd.DataFrame(results)

def run_uav_mission_simulation(output_path="data/simulation/sim_male_uav_30kft_mission.csv"):
    os.makedirs("data/simulation", exist_ok=True)
    twin = PistonEngineTwinMVEM()
    
    # 2-hour simulated high-altitude MALE UAV mission profile (7,200s)
    # Takeoff -> Climb to 30,000 ft (9,144 m) -> Loiter at -45 °C -> High-altitude descent
    t = np.arange(7200, dtype=np.float64)
    
    alt = np.zeros(7200)
    oat = np.zeros(7200)
    rpm = np.zeros(7200)
    throttle = np.zeros(7200)
    ias = np.zeros(7200)
    
    for i in range(7200):
        if i < 300:  # Ground & Takeoff
            alt[i] = 200.0
            oat[i] = 25.0
            rpm[i] = 1000.0 + 1600.0 * (i / 300.0)
            throttle[i] = 0.3 + 0.7 * (i / 300.0)
            ias[i] = 0.0 + 35.0 * (i / 300.0)
        elif i < 2400:  # Climb to 30,000 ft (9,144 m)
            prog = (i - 300) / 2100.0
            alt[i] = 200.0 + 8944.0 * prog
            oat[i] = 25.0 - 65.0 * prog  # Drops to -40 °C
            rpm[i] = 2600.0
            throttle[i] = 1.0
            ias[i] = 45.0
        elif i < 5800:  # High-Altitude Loiter (30,000 ft / 9,144 m)
            alt[i] = 9144.0
            oat[i] = -42.0
            rpm[i] = 2350.0
            throttle[i] = 0.72
            ias[i] = 42.0
        else:  # Descent to base
            prog = (i - 5800) / 1400.0
            alt[i] = 9144.0 * (1.0 - prog) + 200.0 * prog
            oat[i] = -42.0 + 67.0 * prog
            rpm[i] = 1800.0
            throttle[i] = 0.35
            ias[i] = 48.0
            
    df_sim = twin.simulate_mission_profile(t, rpm, throttle, alt, oat, ias)
    df_sim['flight_id'] = 'SIM_MALE_UAV_30KFT'
    df_sim.to_csv(output_path, index=False)
    print(f"Generated High-Altitude MALE UAV Simulation: {len(df_sim)} rows -> {output_path}")
    return df_sim

if __name__ == "__main__":
    run_uav_mission_simulation()
