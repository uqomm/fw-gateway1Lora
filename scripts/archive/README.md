# Scripts Archive

This folder contains archived/deprecated scripts that are no longer in active use.

## Purpose

Scripts are moved here instead of being deleted to:
- 🔍 Maintain historical reference
- 📚 Preserve legacy functionality documentation
- 🔄 Allow rollback if needed
- 📖 Help understand evolution of the codebase

## Archives

### jira-old-scripts-backup-2025-10-09/

**Date:** October 9, 2025  
**Reason:** Consolidated into unified `jira_manager.py` tool

**Archived Scripts:**
- `create_version.py` - Version creation
- `create_subtasks_final.py` - Subtask creation (v1)
- `create_proper_subtasks.py` - Subtask creation (v2)
- `add_worklogs_today.py` - Worklog management
- `mark_tasks_done.py` - Task completion
- `link_fg_tasks.py` - Task linking
- `fix_fg_hierarchy.py` - Hierarchy fixing
- `update_jira_from_changelog.py` - Changelog sync
- `create_fg_tasks.py` - Task creation
- `link_epics_properly.py` - Epic linking

**Replacement:** All functionality available in `scripts/jira_manager.py`  
**Documentation:** See `scripts/JIRA_MANAGER_README.md` and `scripts/MIGRATION_GUIDE.md`

## Usage

⚠️ **Do not use archived scripts in production**

These scripts are kept for reference only. Use current tools instead.

## Retention Policy

Archives older than 1 year may be removed if:
- No active references in documentation
- Functionality fully replaced and tested
- No rollback anticipated

---

*For questions about archived scripts, check git history or migration documentation.*
