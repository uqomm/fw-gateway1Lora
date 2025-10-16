#!/usr/bin/env python3
"""
Simple Jira Epic and Tasks Creator for FWL Project
Creates epic and tasks based on development work done today
"""

import json
from datetime import datetime, timedelta

def create_jira_structure():
    """Create the epic and tasks structure for today's work"""
    
    # Epic data
    epic_data = {
        "project": "FWL",
        "issue_type": "Epic",
        "summary": "LoRa Gateway Logger System Implementation",
        "description": """
Complete implementation of embedded logger system for LoRa Gateway firmware:

**Key Deliverables:**
• Embedded Logger system (Logger.hpp/Logger.cpp) with RS485 output
• UART1 to UART2 migration for improved communication
• LoRa parameter logging in heartbeat for better monitoring  
• Comprehensive GUI configuration tool (Python tkinter)
• Repository migration to uqomm/fw-gateway1Lora organization
• Complete documentation and user manuals

**Technical Impact:**
• Real-time debugging via RS485 logger output
• Enhanced parameter monitoring with LoRa transmission data
• User-friendly GUI for device configuration and monitoring
• Improved code organization and project structure

**Business Value:**
• Faster debugging and troubleshooting capabilities
• Better system monitoring and diagnostics
• Improved user experience with GUI tools  
• Professional project organization under uqomm
        """,
        "estimated_hours": 8,
        "actual_hours": 8,
        "start_date": "2025-10-16",
        "end_date": "2025-10-16",
        "labels": ["logger", "lora", "firmware", "gui", "migration", "stm32"],
        "priority": "High",
        "components": ["Firmware", "GUI", "Tools", "Documentation"]
    }
    
    # Tasks data
    tasks_data = [
        {
            "summary": "Implement Embedded Logger System (Logger.hpp/Logger.cpp)",
            "description": """
**Objective:** Create comprehensive logging system for STM32F103 firmware

**Implementation Details:**
• Singleton pattern Logger class with thread-safe access
• Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)  
• RS485 output via UART3 with automatic DE/RE control
• Message formatting with timestamps and source identification
• Hardware abstraction for different logging targets

**Key Features:**
• Real-time log output via RS485 for external monitoring
• Configurable log levels and message filtering
• Hex data logging for communication debugging
• Integration with existing firmware architecture

**Files Modified:**
• Core/Inc/Logger.hpp (new)
• Core/Src/Logger.cpp (new)
• Integration points in main.cpp
            """,
            "estimated_hours": 2.5,
            "actual_hours": 2.5,
            "start_time": "09:00",
            "end_time": "11:30",
            "labels": ["embedded", "logger", "stm32", "rs485", "singleton"],
            "priority": "High"
        },
        {
            "summary": "UART1 to UART2 Migration",
            "description": """
**Objective:** Migrate main communication from UART1 to UART2

**Changes Made:**
• Updated HAL_UART_RxCpltCallback to handle huart2 instead of huart1
• Modified UartHandler initialization to use huart2
• Updated all UART communication references in main.cpp
• Verified callback routing and interrupt handling

**Technical Benefits:**
• Better hardware resource allocation
• Improved communication reliability
• Cleaner hardware abstraction

**Files Modified:**
• Core/Src/main.cpp (UART callbacks and initialization)
• UartHandler configuration updates
            """,
            "estimated_hours": 1.0,
            "actual_hours": 1.0,
            "start_time": "11:30", 
            "end_time": "12:30",
            "labels": ["uart", "migration", "hardware", "hal"],
            "priority": "High"
        },
        {
            "summary": "Logger System Integration into Main Firmware",
            "description": """
**Objective:** Integrate Logger throughout main firmware application

**Integration Points:**
• Logger initialization in main() function
• Heartbeat logging every 30 seconds with system status
• UART communication logging (RX/TX with hex data)
• LoRa transmission/reception logging  
• Command processing logging with detailed status
• Error condition logging and diagnostics

**Logging Categories:**
• SYSTEM: General system status and heartbeat
• UART2: Serial communication monitoring
• LORA_RX/LORA_TX: LoRa radio operations
• COMMAND: Configuration command processing
• ERROR_SRC: Error conditions and diagnostics

**Benefits:**
• Real-time firmware debugging via RS485
• Communication troubleshooting capabilities
• System health monitoring
• Development and production diagnostics
            """,
            "estimated_hours": 1.5,
            "actual_hours": 1.5,
            "start_time": "12:30",
            "end_time": "14:00", 
            "labels": ["integration", "firmware", "debugging", "monitoring"],
            "priority": "High"
        },
        {
            "summary": "LoRa Parameters in Heartbeat Logging",
            "description": """
**Objective:** Enhance heartbeat logging with LoRa transmission parameters

**Implementation:**
• Modified Logger::logHeartbeat() to include LoRa parameters
• Added external reference to global lora object
• Parameter logging: RX/TX frequency, spread factor, coding rate, bandwidth
• Null pointer safety checks for LoRa object access
• Forward declaration for clean header dependencies

**Enhanced Heartbeat Format:**
```
[HH:MM:SS] INF:SYS Heartbeat - Uptime: XX:XX:XX, Messages: XXX, LoRa[RX:XXXXXXHz TX:XXXXXXHz SF:XX CR:X BW:X]
```

**Technical Benefits:**
• Real-time LoRa configuration monitoring
• Parameter verification during operation
• Debugging aid for configuration changes
• System health dashboard information

**Files Modified:**
• Core/Inc/Logger.hpp (forward declaration, external reference)
• Core/Src/Logger.cpp (enhanced logHeartbeat method)
            """,
            "estimated_hours": 1.0,
            "actual_hours": 1.0,
            "start_time": "14:00",
            "end_time": "15:00",
            "labels": ["lora", "parameters", "monitoring", "heartbeat"],
            "priority": "Medium"
        },
        {
            "summary": "GUI Configuration Application Development",
            "description": """
**Objective:** Create comprehensive GUI for LoRa Gateway configuration

**Application Features:**
• 4-tab interface: Connection, Parameters, Advanced, Log
• Real-time serial communication with device
• Parameter validation and range checking
• Live log monitoring and filtering
• Configuration backup/restore functionality
• Professional UI with status indicators

**Technical Implementation:**
• Python tkinter framework for cross-platform compatibility
• Serial communication via pyserial library
• CRC16 XMODEM protocol implementation
• Command/response protocol handling
• Multi-threaded log monitoring
• JSON configuration management

**Key Files:**
• lora_gui_config.py (main application)
• radio_command_codes.py (protocol definitions)
• utils/log_config.py (logging utilities)
• requirements.txt (dependencies)
• GUI_MANUAL.md (user documentation)

**User Benefits:**
• Easy device configuration without command line
• Real-time parameter monitoring
• Professional troubleshooting interface
• Backup/restore capabilities
            """,
            "estimated_hours": 1.5,
            "actual_hours": 1.5,
            "start_time": "15:00",
            "end_time": "16:30",
            "labels": ["gui", "python", "tkinter", "configuration", "serial"],
            "priority": "Medium"
        },
        {
            "summary": "Repository Migration and Organization",
            "description": """
**Objective:** Migrate repository to uqomm organization and improve structure

**Migration Tasks:**
• GitHub CLI installation and authentication setup
• Repository transfer from arturoSigmadev to uqomm organization
• Remote URL updates in local git configuration
• Repository settings configuration (issues, wiki, projects)
• Access verification and testing

**Organization Improvements:**
• Clean project structure with proper directories
• Comprehensive README and documentation
• Professional repository description
• Proper licensing and contribution guidelines
• CI/CD preparation for future automation

**Final Repository:**
• Organization: uqomm
• Repository: fw-gateway1Lora  
• URL: https://github.com/uqomm/fw-gateway1Lora
• Visibility: Public
• Features: Issues, Wiki, Projects enabled

**Benefits:**
• Professional project organization
• Team collaboration capabilities
• Centralized under uqomm organization
• Better project governance and access control
            """,
            "estimated_hours": 0.5,
            "actual_hours": 0.5,
            "start_time": "16:30",
            "end_time": "17:00",
            "labels": ["repository", "github", "migration", "organization"],
            "priority": "Low"
        }
    ]
    
    return epic_data, tasks_data

def generate_jira_summary():
    """Generate a summary for Jira creation"""
    epic_data, tasks_data = create_jira_structure()
    
    print("=" * 80)
    print("JIRA EPIC AND TASKS SUMMARY")
    print("=" * 80)
    print(f"📋 Project: {epic_data['project']}")
    print(f"📅 Date: {epic_data['start_date']}")
    print(f"⏱️  Total Time: {epic_data['actual_hours']} hours")
    print()
    
    print("🎯 EPIC:")
    print(f"   {epic_data['summary']}")
    print(f"   Labels: {', '.join(epic_data['labels'])}")
    print()
    
    print("📝 TASKS:")
    total_estimated = 0
    total_actual = 0
    
    for i, task in enumerate(tasks_data, 1):
        print(f"{i:2d}. {task['summary']}")
        print(f"    ⏰ Estimated: {task['estimated_hours']}h | Actual: {task['actual_hours']}h")
        print(f"    🕐 Time: {task['start_time']} - {task['end_time']}")
        print(f"    🏷️  Labels: {', '.join(task['labels'])}")
        print()
        
        total_estimated += task['estimated_hours']
        total_actual += task['actual_hours']
    
    print("=" * 80)
    print("📊 SUMMARY:")
    print(f"   Total Tasks: {len(tasks_data)}")
    print(f"   Estimated Time: {total_estimated}h")
    print(f"   Actual Time: {total_actual}h")
    print(f"   Efficiency: {(total_estimated/total_actual)*100:.1f}%")
    print("=" * 80)
    
    return epic_data, tasks_data

if __name__ == "__main__":
    epic, tasks = generate_jira_summary()
    
    # Save to files for manual Jira creation
    with open('epic_data.json', 'w', encoding='utf-8') as f:
        json.dump(epic, f, indent=2, ensure_ascii=False)
    
    with open('tasks_data.json', 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    
    print("\n💾 Data saved to:")
    print("   • epic_data.json")  
    print("   • tasks_data.json")
    print("\n📋 Ready for manual Jira creation!")