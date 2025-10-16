"""
Radio Command Codes
===================

Command codes for LoRa Gateway serial protocol communication.
This module defines all the command constants used for device communication.

Author: Assistant
Date: October 2025
"""

class RadioCommandCodes:
    """Command codes for radio communication protocol."""
    
    # Frame markers
    START_MARK = 0x7E
    END_MARK = 0x7F
    
    # Module Functions
    MODULE_FUNCTION_SERVER = 0x00
    MODULE_FUNCTION_QUAD_BAND = 0x01
    MODULE_FUNCTION_PSU = 0x02
    MODULE_FUNCTION_TETRA = 0x03
    MODULE_FUNCTION_ULADR = 0x04
    MODULE_FUNCTION_VLADR = 0x05
    MODULE_FUNCTION_BDA = 0x06
    MODULE_FUNCTION_LNA = 0x07
    MODULE_FUNCTION_PA = 0x08
    MODULE_FUNCTION_UHF_TONE = 0x09
    MODULE_FUNCTION_SNIFFER = 0x10
    
    # Query Commands (0x10-0x2F range)
    QUERY_MODULE_ID = 0x10
    QUERY_PARAMETER_LTEL = 0x11
    QUERY_PARAMETER_SIGMA = 0x12
    QUERY_MASTER_STATUS = 0x14
    QUERY_PARAMETER_STR = 0x15
    QUERY_PARAMETER_ADC = 0x16
    QUERY_SERVER_PORT = 0x16
    ONE_DETECTION = 0x17
    MULTIPLE_DETECTION = 0x18
    
    # LoRa specific query commands
    QUERY_TX_FREQ = 0x20
    QUERY_RX_FREQ = 0x21
    QUERY_UART_BAUDRATE = 0x22
    QUERY_BANDWIDTH = 0x23
    QUERY_SPREAD_FACTOR = 0x24
    QUERY_CODING_RATE = 0x25
    QUERY_PARAMETER_PdBm = 0x26
    QUERY_OPERATION_MODE = 0x27
    
    # Set Commands (0x90+ range)
    SET_MODULE_ID = 0x90
    SET_VLAD_SERIAL_FISICA = 0x92
    
    # LoRa specific set commands
    SET_TX_FREQ = 0xB0
    SET_RX_FREQ = 0xB1
    SET_UART_BAUDRATE = 0xB2
    SET_BANDWIDTH = 0xB3
    SET_SPREAD_FACTOR = 0xB4
    SET_CODING_RATE = 0xB5
    SET_OUT = 0xB6
    SET_AOUT_0_10V = 0xB7
    SET_AOUT_4_20mA = 0xB8
    SET_AOUT_0_20mA = 0xB9
    SET_DOUT1 = 0xBA
    
    # VLAD specific commands
    SET_VLAD_MODE = 0xC0
    SET_PARAMETER_FREQOUT = 0x31
    SET_PARAMETERS = 0xC2
    SET_PARAMETER_FREQBASE = 0xC3
    
    # Power and attenuation commands
    SET_ATT_LTEL = 0x20
    SET_POUT_MAX = 0x24
    SET_POUT_MIN = 0x23
    SET_VLAD_ATTENUATION = 0x13
    
    # Operation mode command
    SET_OPERATION_MODE = 0x40
    
    # Special function commands
    MODULE_FUNCTION = 0x10
    VLAD_FUNCTION = 0x05

class OperationModes:
    """Operation modes for LoRa Gateway."""
    
    RX_ONLY = 0x00      # Receive only mode
    TX_ONLY = 0x01      # Transmit only mode
    TX_RX = 0x02        # Transmit and receive mode
    STANDBY = 0x03      # Standby mode

class BandwidthValues:
    """LoRa bandwidth values."""
    
    BW_7_8_KHZ = 0      # 7.8 kHz
    BW_10_4_KHZ = 1     # 10.4 kHz
    BW_15_6_KHZ = 2     # 15.6 kHz
    BW_20_8_KHZ = 3     # 20.8 kHz
    BW_31_25_KHZ = 4    # 31.25 kHz
    BW_41_7_KHZ = 5     # 41.7 kHz
    BW_62_5_KHZ = 6     # 62.5 kHz
    BW_125_KHZ = 7      # 125 kHz
    BW_250_KHZ = 8      # 250 kHz
    BW_500_KHZ = 9      # 500 kHz

class SpreadingFactors:
    """LoRa spreading factor values."""
    
    SF6 = 6
    SF7 = 7
    SF8 = 8
    SF9 = 9
    SF10 = 10
    SF11 = 11
    SF12 = 12

class CodingRates:
    """LoRa coding rate values."""
    
    CR_4_5 = 1      # 4/5
    CR_4_6 = 2      # 4/6
    CR_4_7 = 3      # 4/7
    CR_4_8 = 4      # 4/8

class UARTBaudrates:
    """Standard UART baudrates."""
    
    BAUD_9600 = 9600
    BAUD_19200 = 19200
    BAUD_38400 = 38400
    BAUD_57600 = 57600
    BAUD_115200 = 115200
    BAUD_230400 = 230400
    BAUD_460800 = 460800
    BAUD_921600 = 921600

class FrequencyBands:
    """LoRa frequency bands (Hz)."""
    
    # European ISM band
    EU_868_MIN = 863000000
    EU_868_MAX = 870000000
    
    # US ISM band
    US_915_MIN = 902000000
    US_915_MAX = 928000000
    
    # Asian ISM band
    AS_433_MIN = 430000000
    AS_433_MAX = 440000000

class FrameConstants:
    """Frame structure constants."""
    
    MIN_FRAME_SIZE = 8
    MAX_FRAME_SIZE = 255
    CRC_SIZE = 2
    HEADER_SIZE = 6
    
    # Frame indices
    START_INDEX = 0
    MODULE_FUNC_INDEX = 1
    MODULE_ID_INDEX = 2
    COMMAND_INDEX = 3
    RESERVED_INDEX = 4
    DATA_LEN_INDEX = 5
    DATA_START_INDEX = 6

def get_command_name(command_code: int) -> str:
    """Get human-readable name for command code."""
    command_names = {
        # Query commands
        0x10: "QUERY_MODULE_ID",
        0x11: "QUERY_PARAMETER_LTEL",
        0x12: "QUERY_PARAMETER_SIGMA",
        0x14: "QUERY_MASTER_STATUS",
        0x15: "QUERY_PARAMETER_STR",
        0x16: "QUERY_PARAMETER_ADC",
        0x17: "ONE_DETECTION",
        0x18: "MULTIPLE_DETECTION",
        0x20: "QUERY_TX_FREQ",
        0x21: "QUERY_RX_FREQ",
        0x22: "QUERY_UART_BAUDRATE",
        0x23: "QUERY_BANDWIDTH",
        0x24: "QUERY_SPREAD_FACTOR",
        0x25: "QUERY_CODING_RATE",
        0x26: "QUERY_PARAMETER_PdBm",
        0x27: "QUERY_OPERATION_MODE",
        
        # Set commands
        0x90: "SET_MODULE_ID",
        0x92: "SET_VLAD_SERIAL_FISICA",
        0xB0: "SET_TX_FREQ",
        0xB1: "SET_RX_FREQ",
        0xB2: "SET_UART_BAUDRATE",
        0xB3: "SET_BANDWIDTH",
        0xB4: "SET_SPREAD_FACTOR",
        0xB5: "SET_CODING_RATE",
        0xB6: "SET_OUT",
        0xB7: "SET_AOUT_0_10V",
        0xB8: "SET_AOUT_4_20mA",
        0xB9: "SET_AOUT_0_20mA",
        0xBA: "SET_DOUT1",
        
        # Special commands
        0x20: "SET_ATT_LTEL",
        0x23: "SET_POUT_MIN",
        0x24: "SET_POUT_MAX",
        0x40: "SET_OPERATION_MODE",
        0xC0: "SET_VLAD_MODE",
        0xC2: "SET_PARAMETERS",
        0xC3: "SET_PARAMETER_FREQBASE",
    }
    
    return command_names.get(command_code, f"UNKNOWN_0x{command_code:02X}")

def get_bandwidth_name(bw_value: int) -> str:
    """Get human-readable name for bandwidth value."""
    bw_names = {
        0: "7.8 kHz",
        1: "10.4 kHz", 
        2: "15.6 kHz",
        3: "20.8 kHz",
        4: "31.25 kHz",
        5: "41.7 kHz",
        6: "62.5 kHz",
        7: "125 kHz",
        8: "250 kHz",
        9: "500 kHz"
    }
    return bw_names.get(bw_value, f"Unknown ({bw_value})")

def get_coding_rate_name(cr_value: int) -> str:
    """Get human-readable name for coding rate value."""
    cr_names = {
        1: "4/5",
        2: "4/6", 
        3: "4/7",
        4: "4/8"
    }
    return cr_names.get(cr_value, f"Unknown ({cr_value})")

def get_operation_mode_name(mode_value: int) -> str:
    """Get human-readable name for operation mode value."""
    mode_names = {
        0: "RX Only",
        1: "TX Only",
        2: "TX/RX",
        3: "Standby"
    }
    return mode_names.get(mode_value, f"Unknown ({mode_value})")