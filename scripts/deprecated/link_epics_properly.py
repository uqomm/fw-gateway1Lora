#!/usr/bin/env python3
"""
Create proper hierarchy: Epic → Task → Subtask
Since Epics can't have direct subtasks, we need an intermediate Task layer
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

# Option 1: Convert FG-3 and FG-4 to Stories, then add subtasks
# Option 2: Link FG-3 and FG-4 to epics using Epic Link
# Option 3: Create Stories under Epics, then create subtasks

print("="*60)
print("CHECKING EPIC LINK CAPABILITY...")
print("="*60)

# Try to link FG-3 to FG-1 using different methods
fg3 = jira.issue('FG-3')

# Check fields available
fields = jira.fields()
epic_link_field = None
for field in fields:
    if 'epic' in field['name'].lower() and 'link' in field['name'].lower():
        epic_link_field = field['id']
        print(f"Found Epic Link field: {field['name']} ({field['id']})")

if epic_link_field:
    print(f"\n✅ Epic Link field available: {epic_link_field}")
    print("We can link FG-3 and FG-4 to their epics!")
    
    # Link FG-3 to FG-1
    print(f"\nLinking FG-3 to Epic FG-1...")
    try:
        fg3.update(fields={epic_link_field: 'FG-1'})
        print("✅ FG-3 linked to FG-1")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Link FG-4 to FG-1
    print(f"\nLinking FG-4 to Epic FG-1...")
    try:
        fg4 = jira.issue('FG-4')
        fg4.update(fields={epic_link_field: 'FG-1'})
        print("✅ FG-4 linked to FG-1")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ No Epic Link field found")
    print("\nAlternative: Create subtasks under FG-3 and FG-4 for detailed work items")

print("\n" + "="*60)
print("PROPOSED FINAL STRUCTURE:")
print("="*60)
print("FG-1: Epic - Base Versions & Historical Releases")
print("  ├── FG-3: Task - v2.4.0 - Stable Base")
print("  │     ├── (Subtask) Batch parameter optimization")
print("  │     ├── (Subtask) UART performance improvements")
print("  │     └── (Subtask) Tag simulation capabilities")
print("  └── FG-4: Task - v2.5.0 - Remote Diagnostics")
print("        ├── (Subtask) SysTick diagnostic utilities")
print("        ├── (Subtask) UART debug interface")
print("        └── (Subtask) Remote field diagnostics")
print("\nFG-2: Epic - FSK Server Development")
print("  ├── (Task) v3.0.0 - FSK Protocol Implementation")
print("  │     ├── (Subtask) FSK mode configuration")
print("  │     ├── (Subtask) Command handlers")
print("  │     └── (Subtask) Testing & validation")
print("  └── (Task) v3.1.0 - Becker Protocol Support")
print("        ├── (Subtask) Protocol research")
print("        ├── (Subtask) RF implementation")
print("        └── (Subtask) Varis device support")
