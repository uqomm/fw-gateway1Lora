#!/usr/bin/env python3
"""
Convert subtasks to regular tasks linked to epic
Creates new Task issues and archives old Subtasks
"""

import os
from jira import JIRA
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment
load_dotenv('.env.jira')

JIRA_SERVER = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
JIRA_PROJECT = os.getenv('JIRA_PROJECT_KEY', 'FG')

print(f"🔄 Converting subtasks to regular tasks...")
print(f"📡 Connecting to JIRA: {JIRA_SERVER}")

# Connect
jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

# Get epic link field ID
def get_epic_link_field():
    """Find the epic link custom field"""
    fields = jira.fields()
    for field in fields:
        if 'epic link' in field['name'].lower():
            return field['id']
    # Common defaults
    return 'customfield_10014'

epic_link_field = get_epic_link_field()
print(f"📌 Epic link field: {epic_link_field}")

epic_link_field = get_epic_link_field()
print(f"📌 Epic link field: {epic_link_field}")

# Define subtasks to convert
subtasks_data = [
    {
        'old_key': 'FG-12',
        'summary': 'FASE 1: Sistema de Modos Persistente',
        'epic': 'FG-11',
        'due_date': '2025-10-14',
        'labels': ['v2.2.0', 'fase-1', 'eeprom', 'persistence']
    },
    {
        'old_key': 'FG-13',
        'summary': 'FASE 2: Logger Simple',
        'epic': 'FG-11',
        'due_date': '2025-10-16',
        'labels': ['v2.2.0', 'fase-2', 'logger', 'uart']
    },
    {
        'old_key': 'FG-14',
        'summary': 'FASE 3: Comandos de Control',
        'epic': 'FG-11',
        'due_date': '2025-10-17',
        'labels': ['v2.2.0', 'fase-3', 'commands', 'uart']
    },
    {
        'old_key': 'FG-15',
        'summary': 'FASE 4: Integración LoRa + FSK',
        'epic': 'FG-11',
        'due_date': '2025-10-21',
        'labels': ['v2.2.0', 'fase-4', 'integration', 'lora', 'fsk']
    },
    {
        'old_key': 'FG-16',
        'summary': 'FASE 5: Testing y Documentación',
        'epic': 'FG-11',
        'due_date': '2025-10-23',
        'labels': ['v2.2.0', 'fase-5', 'testing', 'documentation']
    }
]

print("\n" + "="*70)
print("Creating new tasks from subtasks...")
print("="*70)

new_tasks = []

for data in subtasks_data:
    try:
        print(f"\n� Processing {data['old_key']}: {data['summary']}")
        
        # Get old subtask to copy description
        try:
            old_issue = jira.issue(data['old_key'])
            description = old_issue.fields.description or "No description"
            print(f"   ✓ Retrieved original description")
        except Exception as e:
            description = "Converted from subtask"
            print(f"   ⚠️  Could not get original: {e}")
        
        # Create new task (without epic link in creation)
        issue_dict = {
            'project': {'key': JIRA_PROJECT},
            'summary': data['summary'],
            'description': description,
            'issuetype': {'name': 'Task'},
            'labels': data['labels'],
            'duedate': data['due_date']
        }
        
        print(f"   ➕ Creating new task...")
        new_issue = jira.create_issue(fields=issue_dict)
        
        print(f"   ✅ Created: {new_issue.key} - {data['summary']}")
        print(f"   � Due date: {data['due_date']}")
        
        # Link to epic after creation
        try:
            jira.add_issues_to_epic(data['epic'], [new_issue.key])
            print(f"   � Linked to epic: {data['epic']}")
        except Exception as e:
            print(f"   ⚠️  Could not link to epic: {e}")
        
        new_tasks.append({
            'old': data['old_key'],
            'new': new_issue.key,
            'summary': data['summary']
        })
        
        # Add comment to old subtask
        try:
            comment = f"⚠️ Esta subtarea ha sido convertida a tarea regular: {new_issue.key}\n\n" \
                     f"Por favor usa {new_issue.key} en lugar de {data['old_key']}."
            jira.add_comment(old_issue, comment)
            print(f"   💬 Added migration comment to old subtask")
        except Exception as e:
            print(f"   ⚠️  Could not add comment: {e}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        continue

print("\n" + "="*70)
print("\n✅ Conversion completed!")
print("\n� Summary:")
print("-" * 70)

for task in new_tasks:
    print(f"  {task['old']} → {task['new']}: {task['summary']}")

print("\n" + "="*70)
print("\n📝 Next steps:")
print("  1. Verify new tasks in JIRA")
print("  2. Check they appear in roadmap/timeline")
print("  3. Manually delete old subtasks if needed")
print("\n🔗 View epic: https://uqomm-teams.atlassian.net/browse/FG-11")
print("="*70)

