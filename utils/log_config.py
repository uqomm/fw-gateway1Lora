"""
Logging Configuration Utilities
===============================

Utilities for setting up consistent logging across the application.

Author: Assistant
Date: October 2025
"""

import logging
import os
from datetime import datetime
from typing import Optional

def setup_logging(
    logger_name: str = None,
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    log_dir: str = "logs"
) -> logging.Logger:
    """
    Setup logging configuration for the application.
    
    Args:
        logger_name: Name of the logger (if None, uses root logger)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file in addition to console
        log_dir: Directory to store log files
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if log_to_file:
        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(log_dir, f"lora_gateway_{timestamp}.log")
        
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_filename}")
    
    return logger

def setup_debug_logging(logger_name: str = None) -> logging.Logger:
    """Setup debug-level logging."""
    return setup_logging(logger_name, logging.DEBUG)

def setup_production_logging(logger_name: str = None) -> logging.Logger:
    """Setup production-level logging (INFO and above)."""
    return setup_logging(logger_name, logging.INFO)

class LogColors:
    """ANSI color codes for console logging."""
    
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability."""
    
    COLORS = {
        'DEBUG': LogColors.CYAN,
        'INFO': LogColors.GREEN,
        'WARNING': LogColors.YELLOW,
        'ERROR': LogColors.RED,
        'CRITICAL': LogColors.RED + LogColors.BOLD,
    }
    
    def format(self, record):
        # Get the original formatted message
        message = super().format(record)
        
        # Add color based on log level
        color = self.COLORS.get(record.levelname, '')
        if color:
            message = f"{color}{message}{LogColors.RESET}"
        
        return message

def setup_colored_logging(
    logger_name: str = None,
    log_level: int = logging.INFO
) -> logging.Logger:
    """Setup logging with colored console output."""
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Colored console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    colored_formatter = ColoredFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)
    
    return logger

def log_frame_data(logger: logging.Logger, direction: str, data: bytes, description: str = ""):
    """
    Log frame data in a formatted way.
    
    Args:
        logger: Logger instance
        direction: "TX" or "RX" 
        data: Frame data as bytes
        description: Optional description of the frame
    """
    hex_data = data.hex().upper()
    
    # Format hex data in groups of 2 bytes
    formatted_hex = ' '.join(hex_data[i:i+2] for i in range(0, len(hex_data), 2))
    
    # Create log message
    message = f"{direction}: {formatted_hex}"
    if description:
        message += f" ({description})"
    
    logger.debug(message)

def log_parameter_update(logger: logging.Logger, param_name: str, old_value, new_value):
    """Log parameter value updates."""
    logger.info(f"Parameter '{param_name}' updated: {old_value} -> {new_value}")

def log_connection_event(logger: logging.Logger, event: str, port: str, details: str = ""):
    """Log connection-related events."""
    message = f"Connection {event}: {port}"
    if details:
        message += f" ({details})"
    logger.info(message)

# Create package-level logger
package_logger = setup_logging("lora_gateway")