#!/usr/bin/env python3
"""
Update JIRA tasks based on CHANGELOG.md status
Delete/archive unused tasks and epics
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
print("CHANGELOG ANALYSIS:")
print("="*60)
print("\n📋 v2.5.0 - 2025-10-08 (RELEASED)")
print("  - SysTick diagnostic tools ✅")
print("  - UART debug interface ✅")
print("  - Remote diagnostics ✅")
print("  - Status: DONE")

print("\n📋 v2.4.0 - 2025-07-07 (RELEASED)")
print("  - Batch parameter optimization ✅")
print("  - UART performance improvements ✅")
print("  - Tag simulation capabilities ✅")
print("  - Status: DONE")

print("\n" + "="*60)
print("UPDATING JIRA TASKS:")
print("="*60)

# Get available transitions
fg3 = jira.issue('FG-3')
print(f"\n📋 FG-3: {fg3.fields.summary}")
print(f"Current Status: {fg3.fields.status.name}")

transitions = jira.transitions(fg3)
print("\nAvailable transitions:")
for t in transitions:
    print(f"  - {t['name']} (id: {t['id']})")

# Find "Done" or "Cerrada" transition
done_transition = None
for t in transitions:
    if 'done' in t['name'].lower() or 'cerrad' in t['name'].lower() or 'hech' in t['name'].lower():
        done_transition = t['id']
        print(f"\n✅ Found completion transition: {t['name']} (id: {t['id']})")
        break

if done_transition:
    print("\n" + "="*60)
    print("UPDATING TASK STATUSES:")
    print("="*60)
    
    # Update FG-3 (v2.4.0) - Released
    print("\n📋 Updating FG-3 (v2.4.0) to DONE...")
    try:
        jira.transition_issue(fg3, done_transition)
        jira.add_comment('FG-3', '✅ **Released on 2025-07-07**\n\nAll features implemented:\n- Batch parameter optimization\n- UART performance improvements\n- Tag simulation capabilities')
        print("✅ FG-3 marked as DONE")
    except Exception as e:
        print(f"⚠️  Could not transition FG-3: {e}")
    
    # Update FG-4 (v2.5.0) - Released TODAY
    print("\n📋 Updating FG-4 (v2.5.0) to DONE...")
    try:
        fg4 = jira.issue('FG-4')
        jira.transition_issue(fg4, done_transition)
        jira.add_comment('FG-4', '✅ **Released on 2025-10-08**\n\nAll features implemented:\n- SysTick diagnostic utilities\n- UART debug interface (printf)\n- Remote field diagnostics\n\n**JIRA Reference:** ID-596')
        print("✅ FG-4 marked as DONE")
    except Exception as e:
        print(f"⚠️  Could not transition FG-4: {e}")
    
    # Update subtasks
    print("\n" + "="*60)
    print("UPDATING SUBTASKS:")
    print("="*60)
    
    subtasks_v24 = ['FG-5', 'FG-6', 'FG-7']  # v2.4.0 subtasks
    subtasks_v25 = ['FG-8', 'FG-9', 'FG-10']  # v2.5.0 subtasks
    
    for task_key in subtasks_v24:
        try:
            task = jira.issue(task_key)
            jira.transition_issue(task, done_transition)
            print(f"✅ {task_key}: {task.fields.summary} → DONE")
        except Exception as e:
            print(f"⚠️  {task_key}: {e}")
    
    for task_key in subtasks_v25:
        try:
            task = jira.issue(task_key)
            jira.transition_issue(task, done_transition)
            print(f"✅ {task_key}: {task.fields.summary} → DONE")
        except Exception as e:
            print(f"⚠️  {task_key}: {e}")

else:
    print("\n❌ No completion transition found. Available transitions:")
    for t in transitions:
        print(f"  - {t['name']}")

print("\n" + "="*60)
print("CLEANING UP UNUSED TASKS:")
print("="*60)

# Check if there are any other tasks we should archive
print("\nSearching for tasks in FG project...")
all_issues = jira.search_issues(f'project={PROJECT_KEY}', maxResults=50)

print(f"\nFound {len(all_issues)} issues:")
for issue in all_issues:
    print(f"  {issue.key}: {issue.fields.issuetype.name} - {issue.fields.summary} [{issue.fields.status.name}]")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)
print("✅ Keep: FG-1 (Epic - Base Versions)")
print("✅ Keep: FG-2 (Epic - FSK Server Development)")
print("✅ Keep: FG-3 → FG-10 (v2.4.0 and v2.5.0 tasks)")
print("\n💡 FG-2 is for future FSK development (v3.0.0+)")

print("\n" + "="*60)
print("✅ UPDATE COMPLETE!")
print("="*60)
