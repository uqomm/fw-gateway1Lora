#!/usr/bin/env python3
"""
Create subtasks under FG-3 and FG-4 to break down the work
Epic → Task → Subtask hierarchy
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
print("Creating subtasks under FG-3 (v2.4.0)...")
print("="*60)

sub1 = jira.create_issue(
    fields={
        'project': {'key': PROJECT_KEY},
        'summary': 'Batch Parameter Optimization',
        'description': 'Implement batch parameter optimization for LoRa communication',
        'issuetype': {'name': 'Subtarea'},
        'parent': {'key': 'FG-3'}
    }
)
print(f"✅ {sub1.key}: {sub1.fields.summary}")

sub2 = jira.create_issue(
    fields={
        'project': {'key': PROJECT_KEY},
        'summary': 'UART Performance Improvements',
        'description': 'Optimize UART handling and buffer management',
        'issuetype': {'name': 'Subtarea'},
        'parent': {'key': 'FG-3'}
    }
)
print(f"✅ {sub2.key}: {sub2.fields.summary}")

sub3 = jira.create_issue(
    fields={
        'project': {'key': PROJECT_KEY},
        'summary': 'Tag Simulation Capabilities',
        'description': 'Implement sniffer device simulation for testing',
        'issuetype': {'name': 'Subtarea'},
        'parent': {'key': 'FG-3'}
    }
)
print(f"✅ {sub3.key}: {sub3.fields.summary}")

print("\n" + "="*60)
print("Creating subtasks under FG-4 (v2.5.0)...")
print("="*60)

sub4 = jira.create_issue(
    fields={
        'project': {'key': PROJECT_KEY},
        'summary': 'SysTick Diagnostic Utilities',
        'description': 'Implement SysTick monitoring and HAL_Delay diagnostics',
        'issuetype': {'name': 'Subtarea'},
        'parent': {'key': 'FG-4'}
    }
)
print(f"✅ {sub4.key}: {sub4.fields.summary}")

sub5 = jira.create_issue(
    fields={
        'project': {'key': PROJECT_KEY},
        'summary': 'UART Debug Interface (printf)',
        'description': 'Implement printf redirection via UART1 for remote debugging',
        'issuetype': {'name': 'Subtarea'},
        'parent': {'key': 'FG-4'}
    }
)
print(f"✅ {sub5.key}: {sub5.fields.summary}")

sub6 = jira.create_issue(
    fields={
        'project': {'key': PROJECT_KEY},
        'summary': 'Remote Field Diagnostics',
        'description': 'Enable remote diagnostic capabilities for field deployment',
        'issuetype': {'name': 'Subtarea'},
        'parent': {'key': 'FG-4'}
    }
)
print(f"✅ {sub6.key}: {sub6.fields.summary}")

print("\n" + "="*60)
print("Adding Epic relationship notes...")
print("="*60)

jira.add_comment('FG-3', "📁 **Epic:** FG-1 - Base Versions & Historical Releases")
jira.add_comment('FG-4', "📁 **Epic:** FG-1 - Base Versions & Historical Releases")

print("✅ Comments added")

print("\n" + "="*60)
print("✅ FINAL STRUCTURE CREATED:")
print("="*60)
print("FG-1: Epic - Base Versions & Historical Releases")
print("  ├── FG-3: Task - v2.4.0 - Stable Base (migrated from ID-540)")
print(f"  │     ├── {sub1.key}: Batch Parameter Optimization")
print(f"  │     ├── {sub2.key}: UART Performance Improvements")
print(f"  │     └── {sub3.key}: Tag Simulation Capabilities")
print("  └── FG-4: Task - v2.5.0 - Remote Diagnostics")
print(f"        ├── {sub4.key}: SysTick Diagnostic Utilities")
print(f"        ├── {sub5.key}: UART Debug Interface (printf)")
print(f"        └── {sub6.key}: Remote Field Diagnostics")
print("\nFG-2: Epic - FSK Server Development")
print("  └── (Future tasks to be created)")

print("\n💡 Note: Epic links must be set manually in JIRA UI")
print("   Go to FG-3 and FG-4, set Epic Link to FG-1")
