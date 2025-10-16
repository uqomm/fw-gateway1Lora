#!/usr/bin/env python3
"""
Create version tasks in FG project
Epics FG-1 and FG-2 already exist
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

# Epic FG-1: Base Versions (already exists)
# Epic FG-2: FSK Server (already exists)

# Create v2.4.0 task
print("📋 Creating v2.4.0 task...")
v24 = jira.create_issue(
    fields={
        'project': {'key': PROJECT_KEY},
        'summary': 'v2.4.0 - Stable Base (migrated from ID-540)',
        'description': 'Batch parameter optimization, UART performance, tag simulation. Migrated from ID-540. Part of Epic FG-1.',
        'issuetype': {'name': 'Task'},
        'labels': ['v2.4.0', 'stable', 'migrated', 'epic-fg-1']
    }
)
print(f"✅ Created: {v24.key}")

# Create v2.5.0 task  
print("📋 Creating v2.5.0 task...")
v25 = jira.create_issue(
    fields={
        'project': {'key': PROJECT_KEY},
        'summary': 'v2.5.0 - Remote Diagnostics',
        'description': 'SysTick diagnostic tools, UART debug interface, TX_RX mode, improved LoRa reliability. Part of Epic FG-1.',
        'issuetype': {'name': 'Task'},
        'labels': ['v2.5.0', 'diagnostics', 'epic-fg-1']
    }
)
print(f"✅ Created: {v25.key}")

# Create versions
print("\n📦 Creating versions...")
ver24 = jira.create_version(
    name="v2.4.0",
    project=PROJECT_KEY,
    released=True,
    releaseDate="2025-07-07"
)
print(f"✅ Version: {ver24.name}")

ver25 = jira.create_version(
    name="v2.5.0", 
    project=PROJECT_KEY,
    released=False
)
print(f"✅ Version: {ver25.name}")

# Create links
jira.create_issue_link(
    type="Relates",
    inwardIssue=v25.key,
    outwardIssue=v24.key
)
print(f"✅ Linked {v25.key} → {v24.key}")

# Add comments about versions
jira.add_comment(v24.key, f"Versión: {ver24.name} - Released: 2025-07-07")
jira.add_comment(v25.key, f"Versión: {ver25.name} - In Development")
print("\n✅ Comments added with version info")

print("\n" + "="*50)
print(f"✅ DONE!")
print("="*50)
print(f"FG-1: Base Versions Epic")
print(f"FG-2: FSK Server Epic")
print(f"{v24.key}: v2.4.0 Base")
print(f"{v25.key}: v2.5.0 Diagnostics")
