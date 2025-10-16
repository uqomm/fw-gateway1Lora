#!/usr/bin/env python3
"""
Update JIRA tasks to "Listo" (Done) based on CHANGELOG.md
"""
import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv(dotenv_path='.env.jira')

jira = JIRA(
    server=os.getenv("JIRA_URL"),
    basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
)

PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

print("✅ Connected to JIRA")
print(f"📊 Project: {PROJECT_KEY}\n")

print("="*60)
print("UPDATING TO 'LISTO' (DONE) STATUS:")
print("="*60)

# Transition ID for "Listo" is 31
LISTO_TRANSITION = '31'

# Update FG-3 (v2.4.0) - Released 2025-07-07
print("\n📋 FG-3: v2.4.0 - Stable Base")
try:
    fg3 = jira.issue('FG-3')
    jira.transition_issue(fg3, LISTO_TRANSITION)
    jira.add_comment('FG-3', '''✅ **v2.4.0 Released: 2025-07-07**

**Completed Features:**
- ✅ Batch Parameter Configuration Optimization
- ✅ Enhanced UART Interrupt Management  
- ✅ Optimized Message Composition
- ✅ UART Response Time Optimization
- ✅ LoRa Parameter Query Performance
- ✅ Enhanced Tag Simulation

**Status:** DONE - All features implemented and tested
**JIRA Reference:** ID-540 (migrated)''')
    print("✅ FG-3 → LISTO")
except Exception as e:
    print(f"❌ Error: {e}")

# Update FG-4 (v2.5.0) - Released 2025-10-08
print("\n📋 FG-4: v2.5.0 - Remote Diagnostics")
try:
    fg4 = jira.issue('FG-4')
    jira.transition_issue(fg4, LISTO_TRANSITION)
    jira.add_comment('FG-4', '''✅ **v2.5.0 Released: 2025-10-08**

**Completed Features:**
- ✅ SysTick Diagnostic Tools (debug_utils.h/c)
- ✅ UART Debug Interface (printf via UART1)
- ✅ Remote Field Diagnostics
- ✅ Gateway Operation Mode (TX_RX_MODE)
- ✅ LoRa Reception Reliability improvements

**Technical Implementation:**
- GetSysTickDiagnostic() - Complete timer state capture
- PrintSysTickDiagnostic() - Formatted diagnostic output
- TestDelay() - HAL_Delay validation
- __io_putchar() - Printf UART redirection

**Status:** DONE - All features implemented and deployed
**JIRA Reference:** ID-596
**Branch:** feature/fsk-reader-becker-varis''')
    print("✅ FG-4 → LISTO")
except Exception as e:
    print(f"❌ Error: {e}")

# Update subtasks for v2.4.0
print("\n" + "="*60)
print("UPDATING v2.4.0 SUBTASKS:")
print("="*60)

subtasks_v24 = {
    'FG-5': 'Batch Parameter Optimization',
    'FG-6': 'UART Performance Improvements',
    'FG-7': 'Tag Simulation Capabilities'
}

for key, name in subtasks_v24.items():
    try:
        task = jira.issue(key)
        jira.transition_issue(task, LISTO_TRANSITION)
        print(f"✅ {key}: {name} → LISTO")
    except Exception as e:
        print(f"❌ {key}: {e}")

# Update subtasks for v2.5.0
print("\n" + "="*60)
print("UPDATING v2.5.0 SUBTASKS:")
print("="*60)

subtasks_v25 = {
    'FG-8': 'SysTick Diagnostic Utilities',
    'FG-9': 'UART Debug Interface (printf)',
    'FG-10': 'Remote Field Diagnostics'
}

for key, name in subtasks_v25.items():
    try:
        task = jira.issue(key)
        jira.transition_issue(task, LISTO_TRANSITION)
        print(f"✅ {key}: {name} → LISTO")
    except Exception as e:
        print(f"❌ {key}: {e}")

# Mark epics as "En curso" (In Progress) since they contain completed work
print("\n" + "="*60)
print("UPDATING EPIC STATUS:")
print("="*60)

EN_CURSO_TRANSITION = '21'

print("\n📋 FG-1: Base Versions Epic")
try:
    fg1 = jira.issue('FG-1')
    jira.transition_issue(fg1, EN_CURSO_TRANSITION)
    jira.add_comment('FG-1', '''📊 **Epic Status Update**

**Completed Versions:**
- ✅ v2.4.0 (FG-3) - Released 2025-07-07
- ✅ v2.5.0 (FG-4) - Released 2025-10-08

**Status:** EN CURSO (contains completed releases)
**Next:** Future maintenance releases will be added here''')
    print("✅ FG-1 → EN CURSO")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n📋 FG-2: FSK Server Development Epic")
try:
    fg2 = jira.issue('FG-2')
    # Keep as "Por hacer" since no work started yet
    jira.add_comment('FG-2', '''📊 **Epic Status Update**

**Status:** POR HACER (awaiting v3.0.0 planning)

**Planned Work:**
- FSK Protocol Implementation (v3.0.0)
- Becker Protocol Support (v3.1.0)
- Varis Device Integration

**Dependencies:**
- Requires v2.5.0 diagnostic tools (✅ DONE)
- Base on stable v2.4.0 platform (✅ DONE)

**Timeline:** Q4 2025 - Q2 2026''')
    print("✅ FG-2 → Comment added (remains POR HACER)")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("✅ FINAL STATUS:")
print("="*60)
print("FG-1: Epic - EN CURSO (contains completed releases)")
print("  ├── FG-3: v2.4.0 → LISTO ✅")
print("  │     ├── FG-5 → LISTO ✅")
print("  │     ├── FG-6 → LISTO ✅")
print("  │     └── FG-7 → LISTO ✅")
print("  └── FG-4: v2.5.0 → LISTO ✅")
print("        ├── FG-8 → LISTO ✅")
print("        ├── FG-9 → LISTO ✅")
print("        └── FG-10 → LISTO ✅")
print("\nFG-2: Epic - POR HACER (future FSK development)")

print("\n" + "="*60)
print("✅ ALL UPDATES COMPLETE!")
print("="*60)
