#!/usr/bin/env python3
"""
LoRa Gateway Logger Monitor
===========================

Monitor serial logger output from LoRa Gateway via RS485.

This script connects to the RS485 output (UART3) of the LoRa Gateway
to monitor real-time logging information.

Usage:
    python logger_monitor.py [COM_PORT] [BAUDRATE]
    
Example:
    python logger_monitor.py COM5 115200

Author: Assistant
Date: October 2025
"""

import sys
import serial
import serial.tools.list_ports
import time
from datetime import datetime
import argparse
import re

class LoggerMonitor:
    """Monitor for LoRa Gateway logger output."""
    
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = False
        
        # Log message pattern
        self.log_pattern = re.compile(r'\[(\d+)\] (\w+):(\w+) (.+)')
        
        # Statistics
        self.message_count = 0
        self.start_time = time.time()
        
    def connect(self):
        """Connect to serial port."""
        try:
            print(f"Connecting to {self.port} at {self.baudrate} baud...")
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1.0
            )
            print(f"✓ Connected to {self.port}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print(f"\n✓ Disconnected from {self.port}")
    
    def parse_log_message(self, line):
        """Parse log message and return formatted output."""
        match = self.log_pattern.match(line.strip())
        if match:
            timestamp_ms = int(match.group(1))
            level = match.group(2)
            source = match.group(3)
            message = match.group(4)
            
            # Convert timestamp to seconds and format
            timestamp_sec = timestamp_ms / 1000.0
            hours = int(timestamp_sec // 3600)
            minutes = int((timestamp_sec % 3600) // 60)
            seconds = timestamp_sec % 60
            
            # Color coding for different levels
            colors = {
                'DBG': '\033[36m',  # Cyan
                'INF': '\033[32m',  # Green
                'WRN': '\033[33m',  # Yellow
                'ERR': '\033[31m',  # Red
                'CRT': '\033[91m',  # Bright Red
            }
            
            source_colors = {
                'SYS': '\033[94m',  # Blue
                'U2': '\033[95m',   # Magenta
                'LRX': '\033[92m',  # Bright Green
                'LTX': '\033[93m',  # Bright Yellow
                'CMD': '\033[96m',  # Bright Cyan
                'CFG': '\033[97m',  # White
            }
            
            reset = '\033[0m'
            level_color = colors.get(level, '')
            source_color = source_colors.get(source, '')
            
            formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
            
            return f"[{formatted_time}] {level_color}{level}{reset}:{source_color}{source}{reset} {message}"
        
        return line.strip()
    
    def monitor(self):
        """Monitor logger output."""
        if not self.connect():
            return
        
        print("\n" + "="*80)
        print("LoRa Gateway Logger Monitor - Press Ctrl+C to stop")
        print("="*80)
        print(f"Port: {self.port} | Baudrate: {self.baudrate}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        self.running = True
        
        try:
            while self.running:
                if self.serial_conn.in_waiting > 0:
                    try:
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore')
                        if line.strip():
                            formatted_line = self.parse_log_message(line)
                            print(formatted_line)
                            self.message_count += 1
                    except UnicodeDecodeError:
                        # Handle binary data or corrupted messages
                        raw_data = self.serial_conn.readline()
                        print(f"[RAW] {raw_data.hex().upper()}")
                
                time.sleep(0.01)  # Small delay to prevent high CPU usage
                
        except KeyboardInterrupt:
            print("\n\nStopping monitor...")
            self.running = False
            
        finally:
            self.disconnect()
            self.print_statistics()
    
    def print_statistics(self):
        """Print monitoring statistics."""
        duration = time.time() - self.start_time
        print("\n" + "="*50)
        print("MONITORING STATISTICS")
        print("="*50)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Messages received: {self.message_count}")
        if duration > 0:
            print(f"Average rate: {self.message_count/duration:.1f} messages/second")
        print("="*50)

def list_serial_ports():
    """List available serial ports."""
    print("Available serial ports:")
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("  No serial ports found")
        return []
    
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port.device} - {port.description}")
    
    return [port.device for port in ports]

def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor LoRa Gateway logger output via RS485"
    )
    parser.add_argument('port', nargs='?', help='Serial port (e.g., COM5, /dev/ttyUSB0)')
    parser.add_argument('baudrate', nargs='?', type=int, default=115200, help='Baudrate (default: 115200)')
    parser.add_argument('-l', '--list', action='store_true', help='List available serial ports')
    
    args = parser.parse_args()
    
    if args.list:
        list_serial_ports()
        return
    
    if not args.port:
        print("Available serial ports:")
        ports = list_serial_ports()
        
        if not ports:
            print("No serial ports found")
            return
        
        try:
            choice = input(f"\nSelect port (1-{len(ports)}) or enter port name: ").strip()
            if choice.isdigit():
                port_index = int(choice) - 1
                if 0 <= port_index < len(ports):
                    args.port = ports[port_index]
                else:
                    print("Invalid selection")
                    return
            else:
                args.port = choice
        except KeyboardInterrupt:
            print("\nCancelled")
            return
    
    if not args.port:
        print("No port specified")
        return
    
    # Create and start monitor
    monitor = LoggerMonitor(args.port, args.baudrate)
    monitor.monitor()

if __name__ == "__main__":
    main()