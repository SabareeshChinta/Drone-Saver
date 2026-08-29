"""
Drone Saver - Live Telemetry Listener & Multi-Source Ingestion Bridge
Implements common TelemetrySource interface supporting:
- UDPSource (MAVLink / JSON UDP socket listener)
- SerialSource (Hardware UART / COM radio telemetry)
- ReplaySource (Deterministic offline/HIL flight playback acting as live 1.0 Hz feed)
Problem Statement: SIH26054 - DRDO
"""

import abc
import os
import sys
sys.path.insert(0, '.')
import time
import socket
import json
import pandas as pd
import numpy as np

from src.replay.telemetry_validator import TelemetryPacketValidator
from src.replay.scenario_loader import ScenarioLoader

class TelemetrySource(abc.ABC):
    @abc.abstractmethod
    def connect(self):
        """Initializes connection to telemetry stream."""
        pass
        
    @abc.abstractmethod
    def read(self, timeout_sec=1.0):
        """Reads a single telemetry packet dictionary."""
        pass
        
    @abc.abstractmethod
    def close(self):
        """Closes connection."""
        pass

class UDPSource(TelemetrySource):
    def __init__(self, host="127.0.0.1", port=14550):
        self.host = host
        self.port = port
        self.sock = None
        
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(1.0)
        print(f"[UDP LISTENER] Bound to {self.host}:{self.port} (Ready for MAVLink/JSON packets)")
        return self
        
    def read(self, timeout_sec=1.0):
        if not self.sock:
            raise ConnectionError("UDP socket is not connected.")
        try:
            self.sock.settimeout(timeout_sec)
            data, addr = self.sock.recvfrom(4096)
            # Try decoding JSON payload
            try:
                packet = json.loads(data.decode('utf-8'))
                return packet
            except Exception:
                # Raw text or CSV line format
                line = data.decode('utf-8', errors='ignore').strip()
                return {'raw_payload': line}
        except socket.timeout:
            return None
            
    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print("[UDP LISTENER] Connection closed.")

class SerialSource(TelemetrySource):
    def __init__(self, port="COM3", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        
    def connect(self):
        try:
            import serial
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1.0)
            print(f"[SERIAL LISTENER] Connected to {self.port} @ {self.baudrate} baud.")
        except Exception as e:
            print(f"[SERIAL LISTENER] Note: Serial hardware {self.port} not available ({e}). Using mock/fallback.")
            self.serial_conn = None
        return self
        
    def read(self, timeout_sec=1.0):
        if not self.serial_conn:
            return None
        try:
            line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
            if line:
                return json.loads(line)
        except Exception:
            return None
        return None
        
    def close(self):
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None

class ReplaySource(TelemetrySource):
    def __init__(self, scenario_yaml_path="scenarios/FINAL_LIVE_DEMO.yaml", real_time_delay=0.0):
        self.scenario_path = scenario_yaml_path
        self.real_time_delay = real_time_delay
        self.df_feed = None
        self.spec = None
        self.current_idx = 0
        
    def connect(self):
        loader = ScenarioLoader()
        self.df_feed, self.spec = loader.load_scenario(self.scenario_path)
        self.current_idx = 0
        scenario_id = self.spec.get('scenario_id', 'REPLAY_SCENARIO')
        print(f"[REPLAY SOURCE] Loaded {scenario_id} ({len(self.df_feed):,} steps from {self.spec.get('flight_id', 'FLIGHT_01')})")
        return self
        
    def read(self, timeout_sec=1.0):
        if self.df_feed is None or self.current_idx >= len(self.df_feed):
            return None
            
        row = self.df_feed.iloc[self.current_idx].to_dict()
        self.current_idx += 1
        
        if self.real_time_delay > 0:
            time.sleep(self.real_time_delay)
            
        return row
        
    def close(self):
        self.df_feed = None
        self.current_idx = 0
