#!/usr/bin/env python3
"""
Fix FG project hierarchy by converting FG-3 and FG-4 to subtasks
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

# Get existing issues
print("📋 Getting existing issues...")
fg1 = jira.issue('FG-1')
fg2 = jira.issue('FG-2')
fg3 = jira.issue('FG-3')
fg4 = jira.issue('FG-4')

print(f"Found: {fg1.key} - {fg1.fields.summary}")
print(f"Found: {fg2.key} - {fg2.fields.summary}")
print(f"Found: {fg3.key} - {fg3.fields.summary}")
print(f"Found: {fg4.key} - {fg4.fields.summary}")

print("\n" + "="*60)
print("CURRENT STRUCTURE:")
print("="*60)
print(f"{fg1.key}: {fg1.fields.issuetype.name} - {fg1.fields.summary}")
print(f"{fg2.key}: {fg2.fields.issuetype.name} - {fg2.fields.summary}")
print(f"{fg3.key}: {fg3.fields.issuetype.name} - {fg3.fields.summary}")
print(f"{fg4.key}: {fg4.fields.issuetype.name} - {fg4.fields.summary}")

print("\n" + "="*60)
print("PROPOSED NEW STRUCTURE:")
print("="*60)
print(f"{fg1.key}: Epic - Base Versions & Historical Releases")
print(f"  └── (Subtask) v2.4.0 - Stable Base (migrated from ID-540)")
print(f"  └── (Subtask) v2.5.0 - Remote Diagnostics")
print(f"{fg2.key}: Epic - FSK Server Development")
print(f"  └── (Subtask) FSK Protocol Implementation (v3.0.0)")
print(f"  └── (Subtask) Becker Protocol Support")

print("\n" + "="*60)
print("OPTIONS:")
print("="*60)
print("1. Delete FG-3 and FG-4, create new subtasks under FG-1")
print("2. Convert FG-3 and FG-4 to subtasks (if JIRA API allows)")
print("3. Keep FG-3 and FG-4 as tasks, create additional subtasks under them")
print("4. Create new subtasks under FG-1 and FG-2, keep FG-3/FG-4 as-is")

print("\n⚠️  This script is in ANALYSIS MODE - no changes made yet")
print("Choose your preferred option and I'll implement it.")

# Let's check what subtask types are available
print("\n" + "="*60)
print("AVAILABLE ISSUE TYPES:")
print("="*60)
project = jira.project(PROJECT_KEY)
issue_types = jira.issue_types()
for itype in issue_types:
    print(f"- {itype.name} (subtask: {itype.subtask})")

# Check current parent-child relationships
print("\n" + "="*60)
print("CURRENT RELATIONSHIPS:")
print("="*60)
for issue_key in ['FG-1', 'FG-2', 'FG-3', 'FG-4']:
    issue = jira.issue(issue_key)
    print(f"\n{issue_key}:")
    print(f"  Type: {issue.fields.issuetype.name}")
    if hasattr(issue.fields, 'parent') and issue.fields.parent:
        print(f"  Parent: {issue.fields.parent.key}")
    if hasattr(issue.fields, 'subtasks') and issue.fields.subtasks:
        print(f"  Subtasks: {[st.key for st in issue.fields.subtasks]}")
    else:
        print(f"  Subtasks: None")
