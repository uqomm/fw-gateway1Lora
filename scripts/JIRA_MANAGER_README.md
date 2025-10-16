# 📋 JIRA Manager - Unified Project Management Tool

## Overview

`jira_manager.py` consolidates all JIRA operations into a single, powerful CLI tool.

**Replaces these scripts:**
- `create_version.py`
- `create_subtasks_final.py`
- `add_worklogs_today.py`
- `mark_tasks_done.py`
- `link_fg_tasks.py`
- `fix_fg_hierarchy.py`
- `update_jira_from_changelog.py`
- `create_proper_subtasks.py`

## Installation

```bash
# Install dependencies
pip install jira python-dotenv

# Configure environment
cp .env.jira.example .env.jira
# Edit .env.jira with your credentials
```

## Common Operations

### 📝 List All Tasks

```bash
python scripts/jira_manager.py --action list-tasks
```

**Filter by status:**
```bash
python scripts/jira_manager.py --action list-tasks --status "In Progress"
```

**Filter by type:**
```bash
python scripts/jira_manager.py --action list-tasks --issue-type Epic
```

### 🔍 Get Task Details

```bash
python scripts/jira_manager.py --action get-details --task FG-4
```

### ✅ Mark Task as Done

```bash
python scripts/jira_manager.py --action mark-done --task FG-4
```

**With comment:**
```bash
python scripts/jira_manager.py --action mark-done --task FG-4 \
  --comment "✅ FSK implementation completed and tested"
```

### 📦 Create New Version

```bash
python scripts/jira_manager.py --action create-version \
  --version v2.6.0 \
  --description "Advanced FSK features" \
  --release-date 2025-10-15
```

**Mark as released:**
```bash
python scripts/jira_manager.py --action create-version \
  --version v2.6.0 \
  --released
```

### 📋 Create Task

```bash
python scripts/jira_manager.py --action create-task \
  --summary "Implement Becker protocol support" \
  --description "Add reverse engineering capabilities for Becker Varis" \
  --type Task \
  --labels fsk becker v3.0.0
```

### 📑 Create Subtasks

**Create JSON file with subtasks (see `subtasks_example.json`):**
```json
[
  {
    "summary": "FSK frequency scanner",
    "description": "Implement automatic frequency scanning 160-190 MHz",
    "labels": ["fsk", "scanner"]
  },
  {
    "summary": "Data capture buffer",
    "description": "Circular buffer for FSK data storage",
    "labels": ["fsk", "buffer"]
  }
]
```

**Create subtasks:**
```bash
python scripts/jira_manager.py --action create-subtasks \
  --parent FG-5 \
  --subtasks-json scripts/subtasks_example.json
```

### ⏱️ Add Worklog

```bash
python scripts/jira_manager.py --action add-worklog \
  --task FG-4 \
  --hours 4 \
  --comment "FSK protocol implementation and testing"
```

**For specific date:**
```bash
python scripts/jira_manager.py --action add-worklog \
  --task FG-4 \
  --hours 6 \
  --date 2025-10-08 \
  --comment "System clock configuration debugging"
```

### 🔗 Link Tasks

```bash
python scripts/jira_manager.py --action link-tasks \
  --inward FG-5 \
  --outward FG-4 \
  --link-type "Relates" \
  --comment "v2.6.0 builds upon v2.5.0 diagnostics"
```

**Available link types:**
- `Relates` - General relationship
- `Blocks` - Blocking relationship
- `Depends` - Dependency
- `Duplicates` - Duplicate issue

### 📄 Update from CHANGELOG

```bash
python scripts/jira_manager.py --action update-from-changelog
```

**Custom changelog path:**
```bash
python scripts/jira_manager.py --action update-from-changelog \
  --changelog docs/CHANGELOG_EXPERIMENTAL.md
```

## Advanced Examples

### 🚀 Complete Release Workflow

```bash
# 1. Create version
python scripts/jira_manager.py --action create-version \
  --version v2.6.0 \
  --description "FSK Advanced Features Release"

# 2. Create main task
python scripts/jira_manager.py --action create-task \
  --summary "v2.6.0 - FSK Advanced Features" \
  --description "Implementation of advanced FSK capabilities" \
  --type Task \
  --labels v2.6.0 fsk

# 3. Create subtasks (using JSON)
python scripts/jira_manager.py --action create-subtasks \
  --parent FG-11 \
  --subtasks-json scripts/subtasks_example.json

# 4. Add worklog
python scripts/jira_manager.py --action add-worklog \
  --task FG-11 \
  --hours 8 \
  --comment "Initial FSK scanner implementation"

# 5. Mark as done when complete
python scripts/jira_manager.py --action mark-done \
  --task FG-11 \
  --comment "✅ v2.6.0 released successfully"
```

### 📊 Project Status Report

```bash
# Get all tasks
python scripts/jira_manager.py --action list-tasks --max-results 100 > tasks.txt

# Get only in-progress tasks
python scripts/jira_manager.py --action list-tasks --status "In Progress"

# Get all epics
python scripts/jira_manager.py --action list-tasks --issue-type Epic
```

### 🔄 Batch Operations

**Create multiple subtasks script:**
```bash
#!/bin/bash
# batch_subtasks.sh

PARENT="FG-11"

# Create subtasks
for subtask in "FSK Scanner" "Data Logger" "Protocol Analyzer"; do
    python scripts/jira_manager.py --action create-task \
        --summary "$subtask" \
        --type Subtarea \
        --parent "$PARENT"
done
```

## Configuration

### Environment Variables

Required in `.env.jira`:

```env
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
JIRA_PROJECT_KEY=FG
```

### Get JIRA API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy token to `.env.jira`

## Tips & Best Practices

### 🎯 Naming Conventions

**Versions:**
- Use semantic versioning: `v2.6.0`, `v3.0.0`
- Include prefix for clarity: `FW-Gateway-v2.6.0`

**Tasks:**
- Start with version: `v2.6.0 - Feature Name`
- Be specific: `FSK Frequency Scanner` not `Scanner`

**Labels:**
- Use consistent labels: `fsk`, `uart`, `diagnostics`
- Include version: `v2.6.0`, `v3.0.0`

### 📝 Comments

Add meaningful comments:
```bash
# Good
--comment "✅ Implemented FSK frequency scanning with 1kHz resolution, tested on 160-190 MHz range"

# Not so good
--comment "Done"
```

### ⏱️ Worklog Tracking

Log work regularly:
```bash
# End of each day
python scripts/jira_manager.py --action add-worklog \
  --task FG-11 \
  --hours 6 \
  --comment "FSK protocol reverse engineering: analyzed Becker Varis signals"
```

## Quick Reference

| Action | Required Args | Optional Args | Example |
|--------|---------------|---------------|---------|
| `list-tasks` | - | `--status`, `--issue-type`, `--max-results` | `--action list-tasks --status "Done"` |
| `get-details` | `--task` | - | `--action get-details --task FG-4` |
| `create-version` | `--version` | `--description`, `--release-date`, `--released` | `--action create-version --version v2.6.0` |
| `create-task` | `--summary` | `--description`, `--type`, `--parent`, `--labels` | `--action create-task --summary "New Feature"` |
| `create-subtasks` | `--parent`, `--subtasks-json` | - | `--action create-subtasks --parent FG-5 --subtasks-json file.json` |
| `mark-done` | `--task` | `--comment` | `--action mark-done --task FG-4` |
| `add-worklog` | `--task`, `--hours` | `--comment`, `--date` | `--action add-worklog --task FG-4 --hours 4` |
| `link-tasks` | `--inward`, `--outward` | `--link-type`, `--comment` | `--action link-tasks --inward FG-5 --outward FG-4` |
| `update-from-changelog` | - | `--changelog` | `--action update-from-changelog` |

## Troubleshooting

### Connection Issues

```bash
# Test connection
python scripts/jira_manager.py --action list-tasks --max-results 1
```

### Permission Errors

Ensure your API token has:
- Browse projects
- Create issues
- Edit issues
- Add worklogs

### Task Not Found

```bash
# Verify task exists
python scripts/jira_manager.py --action get-details --task FG-XX
```

## Migration from Old Scripts

### Before (multiple scripts):
```bash
python scripts/create_version.py
python scripts/create_subtasks_final.py
python scripts/add_worklogs_today.py
python scripts/mark_tasks_done.py
```

### After (unified):
```bash
python scripts/jira_manager.py --action create-version --version v2.6.0
python scripts/jira_manager.py --action create-subtasks --parent FG-11 --subtasks-json scripts/subtasks_example.json
python scripts/jira_manager.py --action add-worklog --task FG-11 --hours 8
python scripts/jira_manager.py --action mark-done --task FG-11
```

## Examples for Common Workflows

### Daily Workflow
```bash
# Morning: Check tasks
python scripts/jira_manager.py --action list-tasks --status "In Progress"

# During work: Log progress
python scripts/jira_manager.py --action add-worklog --task FG-11 --hours 4 --comment "FSK implementation"

# End of day: Update status
python scripts/jira_manager.py --action mark-done --task FG-11 --comment "Completed FSK scanner"
```

### Release Workflow
```bash
# 1. Create version
python scripts/jira_manager.py --action create-version --version v2.6.0 --description "FSK Advanced Features"

# 2. Update changelog integration
python scripts/jira_manager.py --action update-from-changelog

# 3. Review all tasks
python scripts/jira_manager.py --action list-tasks --max-results 100

# 4. Mark version as released
python scripts/jira_manager.py --action create-version --version v2.6.0 --released
```

## Contributing

To add new features to `jira_manager.py`:

1. Add method to `JiraManager` class
2. Add CLI argument to `main()` parser
3. Add handling in `main()` execution block
4. Update this documentation

## Support

For issues or questions:
- Check JIRA API docs: https://jira.readthedocs.io/
- Review error messages (colorized output)
- Use `--help` for usage information

```bash
python scripts/jira_manager.py --help
```

---

**Last Updated:** 2025-10-09  
**Version:** 1.0.0  
**Maintainer:** FW-Gateway Team
