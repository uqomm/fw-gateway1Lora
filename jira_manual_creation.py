#!/usr/bin/env python3
"""
Quick Jira Issue Creation Commands for FWL Project
Use these commands in Jira CLI or REST API
"""

# Epic Creation
epic_command = """
# Create Epic
curl -X POST \\
  https://your-jira-instance.atlassian.net/rest/api/2/issue \\
  -H 'Authorization: Basic <your-auth>' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "fields": {
      "project": {"key": "FWL"},
      "summary": "LoRa Gateway Logger System Implementation",
      "description": "Complete implementation of embedded logger system for LoRa Gateway firmware with GUI tools, UART migration, parameter logging, and repository organization.",
      "issuetype": {"name": "Epic"},
      "priority": {"name": "High"},
      "labels": ["logger", "lora", "firmware", "gui", "migration", "stm32"],
      "customfield_10011": "FWL-EPIC-001",
      "timetracking": {
        "originalEstimate": "8h",
        "remainingEstimate": "0h"
      }
    }
  }'
"""

# Task Creation Commands
tasks_commands = [
    {
        "key": "FWL-001",
        "summary": "Implement Embedded Logger System (Logger.hpp/Logger.cpp)",
        "estimate": "2h 30m",
        "labels": ["embedded", "logger", "stm32", "rs485", "singleton"]
    },
    {
        "key": "FWL-002", 
        "summary": "UART1 to UART2 Migration",
        "estimate": "1h",
        "labels": ["uart", "migration", "hardware", "hal"]
    },
    {
        "key": "FWL-003",
        "summary": "Logger System Integration into Main Firmware", 
        "estimate": "1h 30m",
        "labels": ["integration", "firmware", "debugging", "monitoring"]
    },
    {
        "key": "FWL-004",
        "summary": "LoRa Parameters in Heartbeat Logging",
        "estimate": "1h", 
        "labels": ["lora", "parameters", "monitoring", "heartbeat"]
    },
    {
        "key": "FWL-005",
        "summary": "GUI Configuration Application Development",
        "estimate": "1h 30m",
        "labels": ["gui", "python", "tkinter", "configuration", "serial"]
    },
    {
        "key": "FWL-006",
        "summary": "Repository Migration and Organization", 
        "estimate": "30m",
        "labels": ["repository", "github", "migration", "organization"]
    }
]

def print_manual_instructions():
    print("=" * 80)
    print("MANUAL JIRA CREATION INSTRUCTIONS")
    print("=" * 80)
    print()
    
    print("1️⃣  CREATE EPIC FIRST:")
    print("   - Go to FWL project in Jira")
    print("   - Create Issue → Epic")
    print("   - Title: 'LoRa Gateway Logger System Implementation'")
    print("   - Priority: High") 
    print("   - Estimate: 8h")
    print("   - Labels: logger, lora, firmware, gui, migration, stm32")
    print("   - Date: 2025-10-16")
    print()
    
    print("2️⃣  CREATE TASKS (link to epic):")
    for i, task in enumerate(tasks_commands, 1):
        print(f"   Task {i}: {task['summary']}")
        print(f"            Estimate: {task['estimate']}")
        print(f"            Labels: {', '.join(task['labels'])}")
        print()
    
    print("3️⃣  LOG TIME (for each completed task):")
    print("   - Go to each task")
    print("   - Log Work → Add time spent")
    print("   - Mark as 'Done' status")
    print()
    
    print("4️⃣  QUICK SUMMARY FOR JIRA:")
    print("   Epic: FWL Logger System (8h total)")
    print("   Tasks: 6 items, all completed 2025-10-16")
    print("   Repository: https://github.com/uqomm/fw-gateway1Lora")
    print("=" * 80)

if __name__ == "__main__":
    print_manual_instructions()