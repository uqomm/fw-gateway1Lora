#!/usr/bin/env python3
"""
Add comments and links to FG tasks
"""
import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv(dotenv_path='.env.jira')

jira = JIRA(
    server=os.getenv("JIRA_URL"),
    basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
)

print("✅ Connected to JIRA\n")

# Link FG-4 to FG-3
print("📋 Linking FG-4 → FG-3...")
jira.create_issue_link(
    type="Relates",
    inwardIssue="FG-4",
    outwardIssue="FG-3",
    comment={"body": "v2.5.0 builds upon v2.4.0 stable base"}
)
print("✅ Done")

# Add comments
print("\n📋 Adding version comments...")
jira.add_comment("FG-3", "Versión: v2.4.0 - Released: 2025-07-07 (Migrated from ID-540)")
jira.add_comment("FG-4", "Versión: v2.5.0 - In Development (based on FG-3)")
print("✅ Done")

# Link to FSK Epic
print("\n📋 Linking tasks to FG-2 (FSK Server Epic)...")
jira.create_issue_link(
    type="Relates",
    inwardIssue="FG-3",
    outwardIssue="FG-2",
    comment={"body": "Stable base for FSK Server development"}
)
jira.create_issue_link(
    type="Relates",
    inwardIssue="FG-4",
    outwardIssue="FG-2",
    comment={"body": "Diagnostic tools for FSK Server development"}
)
print("✅ Done")

print("\n" + "="*50)
print("✅ ALL DONE!")
print("="*50)
print("FG-1: Base Versions Epic")
print("FG-2: FSK Server Epic")
print("FG-3: v2.4.0 (migrated from ID-540)")
print("FG-4: v2.5.0 Remote Diagnostics")
print("\nVersions created: v2.4.0, v2.5.0")
