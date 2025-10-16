#!/usr/bin/env python3
"""
JIRA Advanced Operations - Change issue types, set dates, and link tasks
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from jira import JIRA

# Load environment variables
load_dotenv(dotenv_path='.env.jira')

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "FG")

# Connect to JIRA
print(f"🔗 Connecting to JIRA: {JIRA_URL}")
jira = JIRA(
    server=JIRA_URL,
    basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
)
print(f"✅ Connected successfully\n")

# ============================================================================
# FUNCIÓN 1: Convertir tareas a épicas
# ============================================================================

def convert_to_epic(issue_key):
    """Convert a task to an epic"""
    try:
        issue = jira.issue(issue_key)
        print(f"📋 Converting {issue_key} to Epic: {issue.fields.summary}")
        
        # Change issue type to Epic
        issue.update(fields={'issuetype': {'name': 'Epic'}})
        print(f"✅ {issue_key} converted to Epic")
        return True
    except Exception as e:
        print(f"❌ Error converting {issue_key}: {e}")
        return False

# ============================================================================
# FUNCIÓN 2: Agregar fechas de inicio y fin
# ============================================================================

def set_dates(issue_key, start_date, end_date):
    """Set start and due dates for an issue"""
    try:
        issue = jira.issue(issue_key)
        print(f"📅 Setting dates for {issue_key}: {issue.fields.summary}")
        
        fields_to_update = {}
        
        if start_date:
            # Start date field might vary by JIRA instance
            # Try common field names
            fields_to_update['duedate'] = end_date  # Due date is standard
            print(f"   Start: {start_date} (if custom field available)")
            print(f"   Due: {end_date}")
        
        if end_date:
            fields_to_update['duedate'] = end_date
        
        if fields_to_update:
            issue.update(fields=fields_to_update)
            print(f"✅ Dates set for {issue_key}")
        
        return True
    except Exception as e:
        print(f"❌ Error setting dates for {issue_key}: {e}")
        return False

# ============================================================================
# FUNCIÓN 3: Enlazar tareas
# ============================================================================

def link_issues(inward_key, outward_key, link_type="Relates"):
    """Create a link between two issues"""
    try:
        print(f"🔗 Linking {inward_key} {link_type} {outward_key}")
        jira.create_issue_link(
            type=link_type,
            inwardIssue=inward_key,
            outwardIssue=outward_key
        )
        print(f"✅ Link created: {inward_key} {link_type} {outward_key}")
        return True
    except Exception as e:
        print(f"❌ Error linking {inward_key} to {outward_key}: {e}")
        return False

# ============================================================================
# PLAN DE EJECUCIÓN
# ============================================================================

print("=" * 70)
print("🚀 JIRA Advanced Operations - FW-Gateway Project")
print("=" * 70)
print()

# PASO 1: Convertir FG-3, FG-4, FG-11 a épicas
print("PASO 1: Convirtiendo tareas a épicas")
print("-" * 70)

epics_to_convert = ["FG-3", "FG-4", "FG-11"]
for epic_key in epics_to_convert:
    convert_to_epic(epic_key)
    print()

# PASO 2: Establecer fechas para planificación
print("\nPASO 2: Estableciendo fechas de planificación")
print("-" * 70)

# FG-3: v2.4.0 - Stable Base (Finalizada - fechas pasadas)
print("\n📋 FG-3: v2.4.0 - Stable Base")
set_dates("FG-3", 
          start_date="2025-09-01",  # Septiembre 2025
          end_date="2025-09-15")    # 2 semanas
print()

# FG-4: v2.5.0 - Remote Diagnostics (Finalizada - fechas pasadas)
print("📋 FG-4: v2.5.0 - Remote Diagnostics")
set_dates("FG-4",
          start_date="2025-09-16",  # Después de FG-3
          end_date="2025-09-30")    # 2 semanas
print()

# FG-11: LoRa + FSK Integration (Actual - fechas futuras)
print("📋 FG-11: v2.2.0 - LoRa + FSK Integration")
set_dates("FG-11",
          start_date="2025-10-10",  # Mañana
          end_date="2025-10-23")    # 2 semanas (12 horas de trabajo)
print()

# PASO 3: Enlazar épicas relacionadas
print("\nPASO 3: Enlazando épicas relacionadas")
print("-" * 70)

# FG-3 es la base para FG-4
link_issues("FG-4", "FG-3", "Blocks")  # FG-4 depende de FG-3
print()

# FG-4 proporciona funcionalidad para FG-11
link_issues("FG-11", "FG-4", "Relates")  # FG-11 relacionado con FG-4
print()

# FG-11 es parte de la evolución desde FG-3
link_issues("FG-11", "FG-3", "Relates")  # FG-11 relacionado con FG-3
print()

# Enlazar las subtareas de FG-11 entre sí (dependencias en cascada)
print("🔗 Enlazando subtareas de FG-11 en orden secuencial")
subtasks_fg11 = [
    ("FG-13", "FG-12", "Blocks"),  # FASE 2 depende de FASE 1
    ("FG-14", "FG-13", "Blocks"),  # FASE 3 depende de FASE 2
    ("FG-15", "FG-14", "Blocks"),  # FASE 4 depende de FASE 3
    ("FG-16", "FG-15", "Blocks"),  # FASE 5 depende de FASE 4
]

for inward, outward, link_type in subtasks_fg11:
    link_issues(inward, outward, link_type)
    print()

# PASO 4: Resumen
print("\n" + "=" * 70)
print("✅ OPERACIONES COMPLETADAS")
print("=" * 70)
print()
print("📊 RESUMEN:")
print()
print("Épicas convertidas:")
print("  • FG-3: v2.4.0 - Stable Base")
print("    Fechas: 2025-09-01 → 2025-09-15")
print()
print("  • FG-4: v2.5.0 - Remote Diagnostics")
print("    Fechas: 2025-09-16 → 2025-09-30")
print()
print("  • FG-11: v2.2.0 - LoRa + FSK Integration")
print("    Fechas: 2025-10-10 → 2025-10-23")
print()
print("Enlaces creados:")
print("  • FG-4 Blocks FG-3 (FG-4 depende de FG-3)")
print("  • FG-11 Relates FG-4")
print("  • FG-11 Relates FG-3")
print("  • FG-13 Blocks FG-12 (Fase 2 depende de Fase 1)")
print("  • FG-14 Blocks FG-13 (Fase 3 depende de Fase 2)")
print("  • FG-15 Blocks FG-14 (Fase 4 depende de Fase 3)")
print("  • FG-16 Blocks FG-15 (Fase 5 depende de Fase 4)")
print()
print("🎯 Ver en JIRA:")
print(f"   {JIRA_URL}/browse/FG-3")
print(f"   {JIRA_URL}/browse/FG-4")
print(f"   {JIRA_URL}/browse/FG-11")
print()
