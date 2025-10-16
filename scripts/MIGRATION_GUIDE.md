# Migration Guide: Old JIRA Scripts → jira_manager.py

## Overview

This document maps the old individual scripts to the new unified `jira_manager.py` commands.

## Scripts to be Deprecated

The following scripts are **DEPRECATED** and replaced by `jira_manager.py`:

### 1. ❌ `create_version.py`
**Old usage:**
```bash
python scripts/create_version.py
```

**New usage:**
```bash
python scripts/jira_manager.py --action create-version \
  --version v2.6.0 \
  --description "New release" \
  --release-date 2025-10-15
```

---

### 2. ❌ `create_subtasks_final.py`
**Old usage:**
```bash
python scripts/create_subtasks_final.py
```

**New usage:**
```bash
python scripts/jira_manager.py --action create-subtasks \
  --parent FG-5 \
  --subtasks-json scripts/subtasks_example.json
```

---

### 3. ❌ `add_worklogs_today.py`
**Old usage:**
```bash
python scripts/add_worklogs_today.py
```

**New usage:**
```bash
python scripts/jira_manager.py --action add-worklog \
  --task FG-4 \
  --hours 8 \
  --comment "Daily work on FSK implementation"
```

---

### 4. ❌ `mark_tasks_done.py`
**Old usage:**
```bash
python scripts/mark_tasks_done.py
```

**New usage:**
```bash
python scripts/jira_manager.py --action mark-done \
  --task FG-4 \
  --comment "✅ Completed and tested"
```

---

### 5. ❌ `link_fg_tasks.py`
**Old usage:**
```bash
python scripts/link_fg_tasks.py
```

**New usage:**
```bash
python scripts/jira_manager.py --action link-tasks \
  --inward FG-5 \
  --outward FG-4 \
  --link-type Relates
```

---

### 6. ❌ `fix_fg_hierarchy.py`
**Old usage:**
```bash
python scripts/fix_fg_hierarchy.py
```

**New usage:**
```bash
# List all tasks to verify hierarchy
python scripts/jira_manager.py --action list-tasks

# Get details of specific task
python scripts/jira_manager.py --action get-details --task FG-4
```

---

### 7. ❌ `update_jira_from_changelog.py`
**Old usage:**
```bash
python scripts/update_jira_from_changelog.py
```

**New usage:**
```bash
python scripts/jira_manager.py --action update-from-changelog
```

---

### 8. ❌ `create_proper_subtasks.py`
**Old usage:**
```bash
python scripts/create_proper_subtasks.py
```

**New usage:**
```bash
python scripts/jira_manager.py --action create-subtasks \
  --parent FG-5 \
  --subtasks-json scripts/subtasks_example.json
```

---

## Benefits of Migration

### ✅ Single Tool
- One script to maintain instead of 8+
- Consistent interface and error handling
- Unified configuration

### ✅ Better Parameter Support
- Flexible command-line arguments
- No need to edit scripts for different values
- Easy to script and automate

### ✅ Improved Output
- Colorized output for better readability
- Consistent formatting
- Better error messages

### ✅ More Features
- Query and list tasks
- Get detailed task information
- Flexible filtering options
- Support for custom dates and comments

## Migration Checklist

- [ ] Install dependencies: `pip install jira python-dotenv`
- [ ] Test connection: `python scripts/jira_manager.py --action list-tasks`
- [ ] Update automation scripts to use new commands
- [ ] Replace cron jobs or scheduled tasks
- [ ] Update documentation references
- [ ] Archive old scripts to `scripts/deprecated/`

## Example Migration

### Before: Daily Workflow
```bash
# Morning
python scripts/list_tasks.py

# During work
python scripts/add_worklogs_today.py
# Edit script each time...

# End of day
python scripts/mark_tasks_done.py
# Edit script to specify task...
```

### After: Daily Workflow
```bash
# Morning
python scripts/jira_manager.py --action list-tasks --status "In Progress"

# During work
python scripts/jira_manager.py --action add-worklog \
  --task FG-11 \
  --hours 4 \
  --comment "FSK implementation progress"

# End of day
python scripts/jira_manager.py --action mark-done \
  --task FG-11 \
  --comment "Completed FSK frequency control"
```

## Automated Migration Script

```bash
#!/bin/bash
# migrate_to_jira_manager.sh

echo "🔄 Migrating to jira_manager.py..."

# Create deprecated directory
mkdir -p scripts/deprecated

# Move old scripts
OLD_SCRIPTS=(
  "create_version.py"
  "create_subtasks_final.py"
  "add_worklogs_today.py"
  "mark_tasks_done.py"
  "link_fg_tasks.py"
  "fix_fg_hierarchy.py"
  "update_jira_from_changelog.py"
  "create_proper_subtasks.py"
)

for script in "${OLD_SCRIPTS[@]}"; do
  if [ -f "scripts/$script" ]; then
    echo "📦 Archiving scripts/$script"
    mv "scripts/$script" "scripts/deprecated/"
  fi
done

echo "✅ Migration complete!"
echo "📝 Old scripts moved to scripts/deprecated/"
echo "🚀 Use: python scripts/jira_manager.py --help"
```

## Rollback Plan

If you need to rollback:

```bash
# Restore old scripts
mv scripts/deprecated/*.py scripts/

# Verify
ls scripts/*.py
```

## Support

Questions about migration?
1. Read `scripts/JIRA_MANAGER_README.md`
2. Run `python scripts/jira_manager.py --help`
3. Test with `--action list-tasks` first

---

**Migration Date:** 2025-10-09  
**Deprecated Scripts:** 8  
**Replacement:** jira_manager.py v1.0.0
