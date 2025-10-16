#!/usr/bin/env python3
"""
LoRa Gateway Configuration GUI
==============================

GUI application for configuring and monitoring LoRa Gateway parameters
using serial communication protocol.

Author: Assistant
Date: October 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial.tools.list_ports
import threading
import time
import queue
import struct
from typing import Dict, List, Optional, Tuple
from crccheck.crc import Crc16Xmodem
import json
import logging
from datetime import datetime

# Protocol Constants
START_MARK = 0x7E
END_MARK = 0x7F
MIN_FRAME_HEADER_SIZE = 9

# Module Functions
MODULE_FUNCTION_SERVER = 0x00
MODULE_FUNCTION_VLAD = 0x05
MODULE_FUNCTION_SNIFFER = 0x10

# Command Codes - Query Commands
QUERY_MODULE_ID = 0x10
QUERY_PARAMETER_LTEL = 0x11
QUERY_PARAMETER_SIGMA = 0x12
QUERY_UART1 = 0x15
QUERY_PARAMETER_ADC = 0x16
QUERY_TX_FREQ = 0x20
QUERY_RX_FREQ = 0x21
QUERY_UART_BAUDRATE = 0x22
QUERY_BANDWIDTH = 0x23
QUERY_SPREAD_FACTOR = 0x24
QUERY_CODING_RATE = 0x25
QUERY_PARAMETER_PdBm = 0x26

# Command Codes - Set Commands
SET_MODULE_ID = 0x90
SET_TX_FREQ = 0xB0
SET_RX_FREQ = 0xB1
SET_UART_BAUDRATE = 0xB2
SET_BANDWIDTH = 0xB3
SET_SPREAD_FACTOR = 0xB4
SET_CODING_RATE = 0xB5
SET_ATT_LTEL = 0x20
SET_POUT_MAX = 0x24
SET_POUT_MIN = 0x23
SET_VLAD_SERIAL_FISICA = 0x92

# Special Commands
ONE_DETECTION = 0x17
MULTIPLE_DETECTION = 0x18

class FrameBuilder:
    """Frame builder for serial communication protocol."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _calculate_crc(self, data: bytes) -> bytes:
        """Calculate CRC16 XMODEM checksum."""
        return struct.pack("<H", Crc16Xmodem.calc(data))
    
    def build_frame(self, module_function: int, module_id: int, command_id: int, data: Optional[bytes] = None) -> bytes:
        """Build generic frame with CRC."""
        frame = bytearray([START_MARK, module_function, module_id, command_id, 0, len(data or [])])
        frame.extend(data or b"")
        frame += self._calculate_crc(frame[1:])
        frame.append(END_MARK)
        return bytes(frame)

class SerialManager:
    """Manages serial communication with the LoRa Gateway."""
    
    def __init__(self):
        self.serial_port = None
        self.is_connected = False
        self.frame_builder = FrameBuilder()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.response_queue = queue.Queue()
        self.read_thread = None
        self.stop_reading = False
    
    def get_available_ports(self) -> List[str]:
        """Get list of available serial ports."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port: str, baudrate: int = 115200) -> bool:
        """Connect to serial port."""
        try:
            if self.is_connected:
                self.disconnect()
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1.0
            )
            
            self.is_connected = True
            self.stop_reading = False
            self.read_thread = threading.Thread(target=self._read_serial_data, daemon=True)
            self.read_thread.start()
            
            self.logger.info(f"Connected to {port} at {baudrate} baud")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port."""
        self.is_connected = False
        self.stop_reading = True
        
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2.0)
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.logger.info("Serial port disconnected")
    
    def _read_serial_data(self):
        """Read data from serial port in background thread."""
        while not self.stop_reading and self.is_connected:
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    self.response_queue.put(('data', data))
                time.sleep(0.01)
            except Exception as e:
                self.logger.error(f"Error reading serial data: {e}")
                self.response_queue.put(('error', str(e)))
                break
    
    def send_frame(self, frame: bytes) -> bool:
        """Send frame to device."""
        if not self.is_connected or not self.serial_port:
            return False
        
        try:
            self.serial_port.write(frame)
            self.logger.debug(f"Sent frame: {frame.hex().upper()}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending frame: {e}")
            return False
    
    def query_parameter(self, module_function: int, module_id: int, command: int) -> bool:
        """Send query parameter command."""
        frame = self.frame_builder.build_frame(module_function, module_id, command)
        return self.send_frame(frame)
    
    def set_parameter(self, module_function: int, module_id: int, command: int, data: bytes) -> bool:
        """Send set parameter command."""
        frame = self.frame_builder.build_frame(module_function, module_id, command, data)
        return self.send_frame(frame)

class ParameterConfig:
    """Configuration for device parameters."""
    
    PARAMETERS = {
        # Query Parameters
        'module_id': {
            'name': 'Module ID',
            'query_cmd': QUERY_MODULE_ID,
            'set_cmd': SET_MODULE_ID,
            'data_type': 'uint8',
            'range': (1, 255),
            'description': 'Unique module identifier'
        },
        'tx_freq': {
            'name': 'TX Frequency',
            'query_cmd': QUERY_TX_FREQ,
            'set_cmd': SET_TX_FREQ,
            'data_type': 'uint32',
            'range': (860000000, 930000000),
            'description': 'Transmit frequency in Hz'
        },
        'rx_freq': {
            'name': 'RX Frequency',
            'query_cmd': QUERY_RX_FREQ,
            'set_cmd': SET_RX_FREQ,
            'data_type': 'uint32',
            'range': (860000000, 930000000),
            'description': 'Receive frequency in Hz'
        },
        'uart_baudrate': {
            'name': 'UART Baudrate',
            'query_cmd': QUERY_UART_BAUDRATE,
            'set_cmd': SET_UART_BAUDRATE,
            'data_type': 'uint32',
            'options': [9600, 19200, 38400, 57600, 115200, 230400],
            'description': 'UART communication speed'
        },
        'bandwidth': {
            'name': 'Bandwidth',
            'query_cmd': QUERY_BANDWIDTH,
            'set_cmd': SET_BANDWIDTH,
            'data_type': 'uint8',
            'options': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'description': 'LoRa bandwidth setting'
        },
        'spread_factor': {
            'name': 'Spread Factor',
            'query_cmd': QUERY_SPREAD_FACTOR,
            'set_cmd': SET_SPREAD_FACTOR,
            'data_type': 'uint8',
            'range': (6, 12),
            'description': 'LoRa spreading factor'
        },
        'coding_rate': {
            'name': 'Coding Rate',
            'query_cmd': QUERY_CODING_RATE,
            'set_cmd': SET_CODING_RATE,
            'data_type': 'uint8',
            'options': [1, 2, 3, 4],
            'description': 'LoRa coding rate'
        },
        'output_power': {
            'name': 'Output Power (dBm)',
            'query_cmd': QUERY_PARAMETER_PdBm,
            'set_cmd': None,  # No direct set command
            'data_type': 'int8',
            'range': (-20, 20),
            'description': 'RF output power in dBm'
        },
        'ltel_attenuation': {
            'name': 'LTEL Attenuation',
            'query_cmd': QUERY_PARAMETER_LTEL,
            'set_cmd': SET_ATT_LTEL,
            'data_type': 'uint8',
            'range': (0, 63),
            'description': 'LTEL attenuation value'
        }
    }

class LoRaGatewayGUI:
    """Main GUI application for LoRa Gateway configuration."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LoRa Gateway Configuration Tool")
        self.root.geometry("1200x800")
        
        # Setup logging
        self.setup_logging()
        
        # Initialize components
        self.serial_manager = SerialManager()
        self.parameter_config = ParameterConfig()
        self.parameter_values = {}
        
        # GUI Components
        self.setup_gui()
        
        # Start response processing
        self.process_responses()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def setup_gui(self):
        """Setup the main GUI interface."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Connection tab
        self.setup_connection_tab(notebook)
        
        # Parameters tab
        self.setup_parameters_tab(notebook)
        
        # Advanced tab
        self.setup_advanced_tab(notebook)
        
        # Log tab
        self.setup_log_tab(notebook)
    
    def setup_connection_tab(self, notebook):
        """Setup connection configuration tab."""
        conn_frame = ttk.Frame(notebook)
        notebook.add(conn_frame, text="Connection")
        
        # Connection settings
        settings_frame = ttk.LabelFrame(conn_frame, text="Serial Connection Settings")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Port selection
        ttk.Label(settings_frame, text="Port:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(settings_frame, textvariable=self.port_var, state="readonly")
        self.port_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Refresh ports button
        ttk.Button(settings_frame, text="Refresh", command=self.refresh_ports).grid(row=0, column=2, padx=5, pady=5)
        
        # Baudrate selection
        ttk.Label(settings_frame, text="Baudrate:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.baudrate_var = tk.StringVar(value="115200")
        baudrate_combo = ttk.Combobox(settings_frame, textvariable=self.baudrate_var, 
                                     values=["9600", "19200", "38400", "57600", "115200", "230400"])
        baudrate_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # Connection controls
        controls_frame = ttk.Frame(conn_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.connect_btn = ttk.Button(controls_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(controls_frame, text="Disconnected", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Device information
        device_frame = ttk.LabelFrame(conn_frame, text="Device Information")
        device_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Module function and ID
        info_frame = ttk.Frame(device_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text="Module Function:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.module_func_var = tk.StringVar(value="5")  # VLAD default
        ttk.Entry(info_frame, textvariable=self.module_func_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Module ID:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.module_id_var = tk.StringVar(value="1")
        ttk.Entry(info_frame, textvariable=self.module_id_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        # Initialize port list
        self.refresh_ports()
    
    def setup_parameters_tab(self, notebook):
        """Setup parameters configuration tab."""
        param_frame = ttk.Frame(notebook)
        notebook.add(param_frame, text="Parameters")
        
        # Parameters list with scrollbar
        canvas = tk.Canvas(param_frame)
        scrollbar = ttk.Scrollbar(param_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Parameters controls
        controls_frame = ttk.Frame(param_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Query All Parameters", 
                  command=self.query_all_parameters).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Save Configuration", 
                  command=self.save_configuration).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Load Configuration", 
                  command=self.load_configuration).pack(side=tk.LEFT, padx=5)
        
        # Create parameter entries
        self.parameter_entries = {}
        self.setup_parameter_entries(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_parameter_entries(self, parent):
        """Setup parameter entry widgets."""
        row = 0
        for param_key, param_info in self.parameter_config.PARAMETERS.items():
            # Parameter frame
            param_frame = ttk.LabelFrame(parent, text=param_info['name'])
            param_frame.grid(row=row, column=0, sticky=tk.EW, padx=5, pady=5)
            parent.columnconfigure(0, weight=1)
            
            # Description
            desc_label = ttk.Label(param_frame, text=param_info['description'], 
                                 font=('TkDefaultFont', 8), foreground='gray')
            desc_label.grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=5, pady=2)
            
            # Current value
            ttk.Label(param_frame, text="Current:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
            current_var = tk.StringVar(value="Unknown")
            current_label = ttk.Label(param_frame, textvariable=current_var, font=('TkDefaultFont', 9, 'bold'))
            current_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
            
            # New value entry
            ttk.Label(param_frame, text="New:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
            
            if 'options' in param_info:
                # Combobox for predefined options
                new_var = tk.StringVar()
                new_entry = ttk.Combobox(param_frame, textvariable=new_var, 
                                       values=param_info['options'], state="readonly")
            else:
                # Entry for custom values
                new_var = tk.StringVar()
                new_entry = ttk.Entry(param_frame, textvariable=new_var, width=20)
            
            new_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
            
            # Buttons
            query_btn = ttk.Button(param_frame, text="Query", 
                                 command=lambda k=param_key: self.query_parameter(k))
            query_btn.grid(row=1, column=2, padx=5, pady=2)
            
            if param_info['set_cmd'] is not None:
                set_btn = ttk.Button(param_frame, text="Set", 
                                   command=lambda k=param_key: self.set_parameter(k))
                set_btn.grid(row=2, column=2, padx=5, pady=2)
            
            param_frame.columnconfigure(1, weight=1)
            
            # Store references
            self.parameter_entries[param_key] = {
                'current_var': current_var,
                'new_var': new_var,
                'new_entry': new_entry,
                'frame': param_frame
            }
            
            row += 1
    
    def setup_advanced_tab(self, notebook):
        """Setup advanced configuration tab."""
        adv_frame = ttk.Frame(notebook)
        notebook.add(adv_frame, text="Advanced")
        
        # Custom command frame
        custom_frame = ttk.LabelFrame(adv_frame, text="Custom Command")
        custom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Command builder
        ttk.Label(custom_frame, text="Module Function:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.custom_func_var = tk.StringVar(value="5")
        ttk.Entry(custom_frame, textvariable=self.custom_func_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(custom_frame, text="Module ID:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.custom_id_var = tk.StringVar(value="1")
        ttk.Entry(custom_frame, textvariable=self.custom_id_var, width=10).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(custom_frame, text="Command:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.custom_cmd_var = tk.StringVar()
        ttk.Entry(custom_frame, textvariable=self.custom_cmd_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(custom_frame, text="Data (hex):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.custom_data_var = tk.StringVar()
        ttk.Entry(custom_frame, textvariable=self.custom_data_var, width=20).grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Button(custom_frame, text="Send Custom Command", 
                  command=self.send_custom_command).grid(row=2, column=0, columnspan=4, pady=10)
        
        # Raw data viewer
        raw_frame = ttk.LabelFrame(adv_frame, text="Raw Data")
        raw_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.raw_text = scrolledtext.ScrolledText(raw_frame, height=15, font=('Courier', 9))
        self.raw_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_log_tab(self, notebook):
        """Setup logging tab."""
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Log")
        
        # Log controls
        controls_frame = ttk.Frame(log_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=5)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=25, font=('Courier', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Redirect logging to GUI
        self.setup_log_handler()
    
    def setup_log_handler(self):
        """Setup custom log handler for GUI."""
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                self.text_widget.after(0, append)
        
        handler = GUILogHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)
    
    def refresh_ports(self):
        """Refresh available serial ports."""
        ports = self.serial_manager.get_available_ports()
        self.port_combo['values'] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])
    
    def toggle_connection(self):
        """Toggle serial connection."""
        if not self.serial_manager.is_connected:
            port = self.port_var.get()
            baudrate = int(self.baudrate_var.get())
            
            if not port:
                messagebox.showerror("Error", "Please select a serial port")
                return
            
            if self.serial_manager.connect(port, baudrate):
                self.connect_btn.config(text="Disconnect")
                self.status_label.config(text="Connected", foreground="green")
                messagebox.showinfo("Success", f"Connected to {port}")
            else:
                messagebox.showerror("Error", f"Failed to connect to {port}")
        else:
            self.serial_manager.disconnect()
            self.connect_btn.config(text="Connect")
            self.status_label.config(text="Disconnected", foreground="red")
    
    def query_parameter(self, param_key: str):
        """Query specific parameter."""
        if not self.serial_manager.is_connected:
            messagebox.showerror("Error", "Not connected to device")
            return
        
        param_info = self.parameter_config.PARAMETERS[param_key]
        module_func = int(self.module_func_var.get())
        module_id = int(self.module_id_var.get())
        
        success = self.serial_manager.query_parameter(module_func, module_id, param_info['query_cmd'])
        if success:
            self.log_message(f"Queried {param_info['name']}")
        else:
            self.log_message(f"Failed to query {param_info['name']}", "ERROR")
    
    def set_parameter(self, param_key: str):
        """Set specific parameter."""
        if not self.serial_manager.is_connected:
            messagebox.showerror("Error", "Not connected to device")
            return
        
        param_info = self.parameter_config.PARAMETERS[param_key]
        if param_info['set_cmd'] is None:
            messagebox.showerror("Error", f"Parameter {param_info['name']} is read-only")
            return
        
        new_value_str = self.parameter_entries[param_key]['new_var'].get()
        if not new_value_str:
            messagebox.showerror("Error", "Please enter a value")
            return
        
        try:
            # Convert value to appropriate data type
            data = self.encode_parameter_value(param_info, new_value_str)
            
            module_func = int(self.module_func_var.get())
            module_id = int(self.module_id_var.get())
            
            success = self.serial_manager.set_parameter(module_func, module_id, param_info['set_cmd'], data)
            if success:
                self.log_message(f"Set {param_info['name']} to {new_value_str}")
                # Query the parameter again to confirm
                self.query_parameter(param_key)
            else:
                self.log_message(f"Failed to set {param_info['name']}", "ERROR")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value: {e}")
    
    def encode_parameter_value(self, param_info: dict, value_str: str) -> bytes:
        """Encode parameter value according to data type."""
        data_type = param_info['data_type']
        
        try:
            if data_type == 'uint8':
                value = int(value_str)
                if 'range' in param_info:
                    min_val, max_val = param_info['range']
                    if not (min_val <= value <= max_val):
                        raise ValueError(f"Value must be between {min_val} and {max_val}")
                return struct.pack('B', value)
            
            elif data_type == 'int8':
                value = int(value_str)
                if 'range' in param_info:
                    min_val, max_val = param_info['range']
                    if not (min_val <= value <= max_val):
                        raise ValueError(f"Value must be between {min_val} and {max_val}")
                return struct.pack('b', value)
            
            elif data_type == 'uint32':
                value = int(value_str)
                if 'range' in param_info:
                    min_val, max_val = param_info['range']
                    if not (min_val <= value <= max_val):
                        raise ValueError(f"Value must be between {min_val} and {max_val}")
                return struct.pack('<I', value)
            
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
        except ValueError:
            raise ValueError(f"Cannot convert '{value_str}' to {data_type}")
    
    def query_all_parameters(self):
        """Query all available parameters."""
        if not self.serial_manager.is_connected:
            messagebox.showerror("Error", "Not connected to device")
            return
        
        for param_key in self.parameter_config.PARAMETERS:
            self.query_parameter(param_key)
            time.sleep(0.1)  # Small delay between commands
    
    def send_custom_command(self):
        """Send custom command."""
        if not self.serial_manager.is_connected:
            messagebox.showerror("Error", "Not connected to device")
            return
        
        try:
            module_func = int(self.custom_func_var.get())
            module_id = int(self.custom_id_var.get())
            command = int(self.custom_cmd_var.get(), 0)  # Support hex input
            
            data_str = self.custom_data_var.get()
            data = bytes.fromhex(data_str) if data_str else None
            
            frame = self.serial_manager.frame_builder.build_frame(module_func, module_id, command, data)
            success = self.serial_manager.send_frame(frame)
            
            if success:
                self.log_message(f"Sent custom command: {frame.hex().upper()}")
            else:
                self.log_message("Failed to send custom command", "ERROR")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def save_configuration(self):
        """Save current configuration to file."""
        try:
            config = {
                'timestamp': datetime.now().isoformat(),
                'module_function': self.module_func_var.get(),
                'module_id': self.module_id_var.get(),
                'parameters': {}
            }
            
            for param_key, entry in self.parameter_entries.items():
                current_value = entry['current_var'].get()
                if current_value != "Unknown":
                    config['parameters'][param_key] = current_value
            
            filename = f"lora_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo("Success", f"Configuration saved to {filename}")
            self.log_message(f"Configuration saved to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def load_configuration(self):
        """Load configuration from file."""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            
            # Load module settings
            if 'module_function' in config:
                self.module_func_var.set(config['module_function'])
            if 'module_id' in config:
                self.module_id_var.set(config['module_id'])
            
            # Load parameter values
            if 'parameters' in config:
                for param_key, value in config['parameters'].items():
                    if param_key in self.parameter_entries:
                        self.parameter_entries[param_key]['current_var'].set(value)
                        self.parameter_entries[param_key]['new_var'].set(value)
            
            messagebox.showinfo("Success", f"Configuration loaded from {filename}")
            self.log_message(f"Configuration loaded from {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def process_responses(self):
        """Process responses from serial port."""
        try:
            while True:
                msg_type, data = self.serial_manager.response_queue.get_nowait()
                
                if msg_type == 'data':
                    self.handle_serial_data(data)
                elif msg_type == 'error':
                    self.log_message(f"Serial error: {data}", "ERROR")
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_responses)
    
    def handle_serial_data(self, data: bytes):
        """Handle incoming serial data."""
        hex_data = data.hex().upper()
        self.log_message(f"Received: {hex_data}")
        
        # Add to raw data viewer
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.raw_text.insert(tk.END, f"[{timestamp}] RX: {hex_data}\n")
        self.raw_text.see(tk.END)
        
        # Try to parse response
        self.parse_response(data)
    
    def parse_response(self, data: bytes):
        """Parse device response and update parameter values."""
        if len(data) < 8:  # Minimum frame size
            return
        
        try:
            # Basic frame parsing
            if data[0] == START_MARK and data[-1] == END_MARK:
                module_func = data[1]
                module_id = data[2]
                command = data[3]
                data_len = data[5]
                payload = data[6:6+data_len]
                
                # Find matching parameter
                for param_key, param_info in self.parameter_config.PARAMETERS.items():
                    if param_info['query_cmd'] == command:
                        value = self.decode_parameter_value(param_info, payload)
                        if value is not None:
                            self.parameter_entries[param_key]['current_var'].set(str(value))
                            self.log_message(f"Updated {param_info['name']}: {value}")
                        break
                        
        except Exception as e:
            self.log_message(f"Error parsing response: {e}", "ERROR")
    
    def decode_parameter_value(self, param_info: dict, payload: bytes):
        """Decode parameter value from payload."""
        if not payload:
            return None
        
        try:
            data_type = param_info['data_type']
            
            if data_type == 'uint8':
                return struct.unpack('B', payload[:1])[0]
            elif data_type == 'int8':
                return struct.unpack('b', payload[:1])[0]
            elif data_type == 'uint32':
                if len(payload) >= 4:
                    return struct.unpack('<I', payload[:4])[0]
            
        except struct.error:
            pass
        
        return None
    
    def log_message(self, message: str, level: str = "INFO"):
        """Log message to GUI and logger."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {level}: {message}"
        
        if level == "ERROR":
            self.logger.error(message)
        else:
            self.logger.info(message)
    
    def clear_log(self):
        """Clear log text area."""
        self.log_text.delete(1.0, tk.END)
        self.raw_text.delete(1.0, tk.END)
    
    def save_log(self):
        """Save log to file."""
        try:
            filename = f"lora_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(self.log_text.get(1.0, tk.END))
            
            messagebox.showinfo("Success", f"Log saved to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {e}")
    
    def run(self):
        """Start the GUI application."""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
    
    def on_closing(self):
        """Handle application closing."""
        if self.serial_manager.is_connected:
            self.serial_manager.disconnect()
        self.root.destroy()

def main():
    """Main application entry point."""
    app = LoRaGatewayGUI()
    app.run()

if __name__ == "__main__":
    main()