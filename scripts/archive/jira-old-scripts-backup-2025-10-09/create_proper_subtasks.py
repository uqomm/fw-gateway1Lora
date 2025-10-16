#!/usr/bin/env python3
"""
Create proper subtasks under FG-1 and FG-2 epics
Keep FG-3 and FG-4 as regular tasks for reference
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

# Create subtasks under FG-1 (Base Versions Epic)
print("="*60)
print("Creating subtasks under FG-1 (Base Versions Epic)...")
print("="*60)

subtask_v24 = jira.create_issue(
    fields={
        'project': {'key': PROJECT_KEY},
        'summary': 'v2.4.0 - Stable Base Implementation',
        'description': '''**Version:** v2.4.0
**Release Date:** 2025-07-07
**Status:** Released

**Features:**
- Batch parameter optimization
- UART performance improvements  
- Tag simulation capabilities
- LoRa communication enhancements

**Original Task:** Migrated from ID-540
**Parent Epic:** FG-1 - Base Versions & Historical Releases''',
        'issuetype': {'name': 'Subtarea'},
        'parent': {'key': 'FG-1'},
        'labels': ['v2.4.0', 'released', 'stable']
    }
)
print(f"✅ Created subtask: {subtask_v24.key} - {subtask_v24.fields.summary}")

subtask_v25 = jira.create_issue(
    fields={
        'project': {'key': PROJECT_KEY},
        'summary': 'v2.5.0 - Remote Diagnostics Implementation',
        'description': '''**Version:** v2.5.0
**Status:** In Development

**Features:**
- SysTick diagnostic utilities
- UART debug interface (printf via UART1)
- TX_RX mode improvements
- Remote field diagnostics
- HAL_Delay monitoring tools

**Parent Epic:** FG-1 - Base Versions & Historical Releases
**Dependencies:** Builds upon v2.4.0 stable base''',
        'issuetype': {'name': 'Subtarea'},
        'parent': {'key': 'FG-1'},
        'labels': ['v2.5.0', 'in-development', 'diagnostics']
    }
)
print(f"✅ Created subtask: {subtask_v25.key} - {subtask_v25.fields.summary}")

# Create subtasks under FG-2 (FSK Server Epic)
print("\n" + "="*60)
print("Creating subtasks under FG-2 (FSK Server Epic)...")
print("="*60)

subtask_fsk_protocol = jira.create_issue(
    fields={
        'project': {'key': PROJECT_KEY},
        'summary': 'FSK Protocol Implementation (v3.0.0)',
        'description': '''**Target Version:** v3.0.0
**Planned:** Q4 2025 - Q1 2026

**Objectives:**
- Implement FSK mode configuration and control
- Add frequency, bitrate, and deviation settings
- Create FSK-specific command handlers
- Test FSK communication reliability

**Parent Epic:** FG-2 - FSK Server Development''',
        'issuetype': {'name': 'Subtarea'},
        'parent': {'key': 'FG-2'},
        'labels': ['v3.0.0', 'fsk', 'planned']
    }
)
print(f"✅ Created subtask: {subtask_fsk_protocol.key} - {subtask_fsk_protocol.fields.summary}")

subtask_becker = jira.create_issue(
    fields={
        'project': {'key': PROJECT_KEY},
        'summary': 'Becker Protocol Support',
        'description': '''**Target Version:** v3.1.0+
**Planned:** Q2 2026

**Objectives:**
- Research Becker protocol specifications
- Implement Becker RF communication
- Add Varis device support
- Integration testing with Becker hardware

**Parent Epic:** FG-2 - FSK Server Development''',
        'issuetype': {'name': 'Subtarea'},
        'parent': {'key': 'FG-2'},
        'labels': ['v3.1.0', 'becker', 'varis', 'planned']
    }
)
print(f"✅ Created subtask: {subtask_becker.key} - {subtask_becker.fields.summary}")

# Link subtasks
print("\n" + "="*60)
print("Creating relationships between subtasks...")
print("="*60)

jira.create_issue_link(
    type="Relates",
    inwardIssue=subtask_v25.key,
    outwardIssue=subtask_v24.key,
    comment={"body": "v2.5.0 builds upon v2.4.0 stable base"}
)
print(f"✅ Linked {subtask_v25.key} → {subtask_v24.key}")

jira.create_issue_link(
    type="Relates",
    inwardIssue=subtask_fsk_protocol.key,
    outwardIssue=subtask_v25.key,
    comment={"body": "FSK development requires v2.5.0 diagnostic tools"}
)
print(f"✅ Linked {subtask_fsk_protocol.key} → {subtask_v25.key}")

jira.create_issue_link(
    type="Relates",
    inwardIssue=subtask_becker.key,
    outwardIssue=subtask_fsk_protocol.key,
    comment={"body": "Becker protocol requires FSK implementation"}
)
print(f"✅ Linked {subtask_becker.key} → {subtask_fsk_protocol.key}")

# Add comments to old tasks explaining the new structure
print("\n" + "="*60)
print("Adding migration notes to FG-3 and FG-4...")
print("="*60)

jira.add_comment('FG-3', f'''⚠️ **MIGRATED TO SUBTASK STRUCTURE**

This task has been superseded by proper subtask hierarchy:
- **New Subtask:** {subtask_v24.key} under Epic FG-1

The new subtask contains the same information but is properly organized under the Base Versions epic.
This task (FG-3) is kept for historical reference.''')

jira.add_comment('FG-4', f'''⚠️ **MIGRATED TO SUBTASK STRUCTURE**

This task has been superseded by proper subtask hierarchy:
- **New Subtask:** {subtask_v25.key} under Epic FG-1

The new subtask contains the same information but is properly organized under the Base Versions epic.
This task (FG-4) is kept for historical reference.''')

print("✅ Migration notes added")

print("\n" + "="*60)
print("✅ FINAL STRUCTURE:")
print("="*60)
print(f"FG-1: Epic - Base Versions & Historical Releases")
print(f"  ├── {subtask_v24.key}: v2.4.0 - Stable Base")
print(f"  └── {subtask_v25.key}: v2.5.0 - Remote Diagnostics")
print(f"\nFG-2: Epic - FSK Server Development")
print(f"  ├── {subtask_fsk_protocol.key}: FSK Protocol Implementation")
print(f"  └── {subtask_becker.key}: Becker Protocol Support")
print(f"\n📝 Reference (legacy):")
print(f"  - FG-3: v2.4.0 (original task, now archived)")
print(f"  - FG-4: v2.5.0 (original task, now archived)")

print("\n" + "="*60)
print("✅ ALL DONE!")
print("="*60)
