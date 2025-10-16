# Deprecated JIRA Scripts

⚠️ **THESE SCRIPTS ARE DEPRECATED AND NO LONGER MAINTAINED**

Date: October 9, 2025

## Reason for Deprecation

These scripts have been consolidated into a single unified tool: `scripts/jira_manager.py`

The new unified tool provides:
- ✅ Better parameter handling with argparse
- ✅ Comprehensive error handling
- ✅ Colorized output
- ✅ Single point of maintenance
- ✅ Better documentation
- ✅ All features from deprecated scripts

## Migration

See `scripts/MIGRATION_GUIDE.md` for detailed migration instructions.

## Deprecated Scripts

| Old Script | New Command |
|------------|-------------|
| `create_version.py` | `jira_manager.py --action create-version` |
| `create_subtasks_final.py` | `jira_manager.py --action create-subtasks` |
| `create_proper_subtasks.py` | `jira_manager.py --action create-subtasks` |
| `add_worklogs_today.py` | `jira_manager.py --action add-worklog` |
| `mark_tasks_done.py` | `jira_manager.py --action mark-done` |
| `link_fg_tasks.py` | `jira_manager.py --action link-tasks` |
| `fix_fg_hierarchy.py` | `jira_manager.py --action link-tasks` |
| `update_jira_from_changelog.py` | `jira_manager.py --action update-from-changelog` |
| `create_fg_tasks.py` | `jira_manager.py --action create-task` |
| `link_epics_properly.py` | `jira_manager.py --action link-tasks` |

## Do Not Use

These scripts are kept for historical reference only. They may not work correctly and are not supported.

**Use `scripts/jira_manager.py` instead.**

For help:
```bash
python scripts/jira_manager.py --help
```

See also: `scripts/JIRA_MANAGER_README.md`
