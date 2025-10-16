#!/bin/bash
# Example automation scripts using jira_manager.py

# ===========================================================================
# DAILY STANDUP REPORT
# ===========================================================================

daily_standup() {
    echo "📊 Daily Standup Report - $(date)"
    echo ""
    
    echo "🔄 In Progress Tasks:"
    python scripts/jira_manager.py --action list-tasks --status "In Progress"
    
    echo ""
    echo "✅ Completed Yesterday:"
    python scripts/jira_manager.py --action list-tasks --status "Done" --max-results 5
}

# ===========================================================================
# RELEASE WORKFLOW
# ===========================================================================

create_release() {
    VERSION=$1
    DESCRIPTION=$2
    RELEASE_DATE=$3
    
    if [ -z "$VERSION" ]; then
        echo "❌ Usage: create_release <version> <description> <release-date>"
        echo "   Example: create_release v2.6.0 'FSK Features' 2025-10-15"
        return 1
    fi
    
    echo "🚀 Creating release: $VERSION"
    
    # Create version
    python scripts/jira_manager.py --action create-version \
        --version "$VERSION" \
        --description "$DESCRIPTION" \
        --release-date "$RELEASE_DATE"
    
    # Update from changelog
    python scripts/jira_manager.py --action update-from-changelog
    
    echo "✅ Release $VERSION created!"
}

# ===========================================================================
# BATCH WORKLOG
# ===========================================================================

log_daily_work() {
    TASK=$1
    HOURS=${2:-8}
    COMMENT=${3:-"Daily development work"}
    
    if [ -z "$TASK" ]; then
        echo "❌ Usage: log_daily_work <task> [hours] [comment]"
        echo "   Example: log_daily_work FG-11 6 'FSK implementation'"
        return 1
    fi
    
    echo "⏱️  Logging $HOURS hours to $TASK"
    python scripts/jira_manager.py --action add-worklog \
        --task "$TASK" \
        --hours "$HOURS" \
        --comment "$COMMENT"
}

# ===========================================================================
# COMPLETE TASK WORKFLOW
# ===========================================================================

complete_task() {
    TASK=$1
    HOURS=${2:-0}
    COMMENT=${3:-"✅ Task completed"}
    
    if [ -z "$TASK" ]; then
        echo "❌ Usage: complete_task <task> [hours] [comment]"
        echo "   Example: complete_task FG-11 2 'Final testing complete'"
        return 1
    fi
    
    echo "🎯 Completing task: $TASK"
    
    # Add worklog if hours specified
    if [ "$HOURS" -gt 0 ]; then
        python scripts/jira_manager.py --action add-worklog \
            --task "$TASK" \
            --hours "$HOURS" \
            --comment "Final work: $COMMENT"
    fi
    
    # Mark as done
    python scripts/jira_manager.py --action mark-done \
        --task "$TASK" \
        --comment "$COMMENT"
    
    echo "✅ Task $TASK completed!"
}

# ===========================================================================
# SPRINT PLANNING
# ===========================================================================

create_sprint_tasks() {
    EPIC=$1
    SPRINT=$2
    
    if [ -z "$EPIC" ] || [ -z "$SPRINT" ]; then
        echo "❌ Usage: create_sprint_tasks <epic> <sprint>"
        echo "   Example: create_sprint_tasks FG-5 Sprint-10"
        return 1
    fi
    
    echo "📋 Creating sprint tasks for $EPIC"
    
    # Create subtasks from JSON
    python scripts/jira_manager.py --action create-subtasks \
        --parent "$EPIC" \
        --subtasks-json "scripts/subtasks_example.json"
    
    echo "✅ Sprint tasks created for $SPRINT"
}

# ===========================================================================
# WEEKLY SUMMARY
# ===========================================================================

weekly_summary() {
    echo "📅 Weekly Summary Report - $(date)"
    echo ""
    
    echo "📊 All Tasks:"
    python scripts/jira_manager.py --action list-tasks --max-results 20
    
    echo ""
    echo "🎯 Epics:"
    python scripts/jira_manager.py --action list-tasks --issue-type Epic
    
    echo ""
    echo "✅ Completed This Week:"
    python scripts/jira_manager.py --action list-tasks --status "Done" --max-results 10
}

# ===========================================================================
# BULK OPERATIONS
# ===========================================================================

link_related_tasks() {
    BASE_TASK=$1
    shift
    RELATED_TASKS=("$@")
    
    if [ -z "$BASE_TASK" ] || [ ${#RELATED_TASKS[@]} -eq 0 ]; then
        echo "❌ Usage: link_related_tasks <base-task> <related-task1> [related-task2] ..."
        echo "   Example: link_related_tasks FG-5 FG-4 FG-3"
        return 1
    fi
    
    echo "🔗 Linking tasks to $BASE_TASK"
    
    for task in "${RELATED_TASKS[@]}"; do
        echo "  → Linking $task to $BASE_TASK"
        python scripts/jira_manager.py --action link-tasks \
            --inward "$BASE_TASK" \
            --outward "$task" \
            --link-type "Relates"
    done
    
    echo "✅ All tasks linked!"
}

# ===========================================================================
# HELP
# ===========================================================================

show_help() {
    cat << EOF
🛠️  JIRA Manager Automation Scripts

Available functions:

  📊 Reporting:
    daily_standup              Daily standup report
    weekly_summary            Weekly summary with all tasks

  🚀 Release Management:
    create_release <version> <description> <date>
                             Create new release version

  ⏱️  Time Tracking:
    log_daily_work <task> [hours] [comment]
                             Log work hours to task
    complete_task <task> [hours] [comment]
                             Complete task and log final hours

  📋 Sprint Planning:
    create_sprint_tasks <epic> <sprint>
                             Create sprint tasks from JSON

  🔗 Bulk Operations:
    link_related_tasks <base> <task1> [task2] ...
                             Link multiple tasks together

Examples:

  # Daily standup
  ./automation_examples.sh && daily_standup

  # Create release
  create_release v2.6.0 "FSK Advanced Features" 2025-10-15

  # Log work
  log_daily_work FG-11 6 "FSK protocol implementation"

  # Complete task
  complete_task FG-11 2 "Testing complete, ready for release"

  # Link tasks
  link_related_tasks FG-5 FG-4 FG-3 FG-2

EOF
}

# ===========================================================================
# MAIN
# ===========================================================================

# If script is sourced, just load functions
# If executed directly, show help
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    show_help
fi
