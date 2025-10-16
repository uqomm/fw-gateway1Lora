#!/usr/bin/env python3
"""
Create FW-Gateway version in JIRA with changelog information
"""
import os
from dotenv import load_dotenv
from jira import JIRA
import sys

# Load environment variables
load_dotenv(dotenv_path='.env.jira')

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

def create_version():
    """Create version v2.5.0 in JIRA with changelog details"""
    try:
        # Connect to JIRA
        jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        print("✅ Connected to JIRA")
        
        # Version details
        version_name = "FW-Gateway-2024-v2.5.0"
        version_description = """Remote Diagnostic Data Capture Implementation (ID-596)

**Base Version**: v2.4.0 (ID-540)
**Release Date**: 2025-10-08

## Key Features

### Added - Remote Diagnostics
- **SysTick Diagnostic Tools**: Comprehensive debugging utilities
  - GetSysTickDiagnostic(), PrintSysTickDiagnostic(), TestDelay()
  - DBGMCU freeze configuration monitoring
  - Real-time register capture and analysis

- **UART Debug Interface**: Printf support via UART1
  - Remote diagnostic data transmission
  - Debug message streaming for field troubleshooting

- **JIRA Integration**: Automated project tracking

### Changed - Operational Improvements  
- Gateway operation mode: RX_MODE → TX_RX_MODE (full-duplex)
- LoRa RX timeout: 0ms → 2000ms (improved reliability)

### Fixed
- STM32CubeIDE compiler environment synchronization
- Build consistency across STM32F103 and STM32G474 projects

## Technical Details
- Memory Footprint: +2KB flash
- Runtime Overhead: <0.1% CPU
- UART Bandwidth: ~1200 bytes/s
- Latency: <5ms diagnostic response

## Related Issues
- ID-596: Remote diagnostic capture implementation
- ID-540: Base version v2.4.0
"""
        
        # Create version
        version = jira.create_version(
            name=version_name,
            project=JIRA_PROJECT_KEY,
            description=version_description,
            released=False
        )
        
        print(f"✅ Version created: {version.name}")
        print(f"   ID: {version.id}")
        
        # Link version to ID-596
        try:
            issue = jira.issue('ID-596')
            
            # Add version to fixVersions
            current_versions = issue.fields.fixVersions
            current_versions.append({'name': version_name})
            issue.update(fields={'fixVersions': current_versions})
            
            print(f"✅ Version linked to ID-596")
            
            # Add comment to ID-596
            comment_text = f"""Version {version_name} created with remote diagnostic capabilities.

## Implementation Complete
- SysTick diagnostic tools implemented
- UART debug interface operational  
- Full-duplex communication enabled
- LoRa reliability improvements deployed

Ready for field testing and remote diagnostic validation.
"""
            jira.add_comment('ID-596', comment_text)
            print(f"✅ Comment added to ID-596")
            
        except Exception as e:
            print(f"⚠️  Warning linking to ID-596: {e}")
        
        # Try to link to ID-540 as well
        try:
            issue_540 = jira.issue('ID-540')
            jira.create_issue_link(
                type="Relates",
                inwardIssue="ID-596",
                outwardIssue="ID-540",
                comment={
                    "body": f"Version {version_name} built on base version v2.4.0"
                }
            )
            print(f"✅ Linked ID-596 to ID-540")
        except Exception as e:
            print(f"⚠️  Warning linking to ID-540: {e}")
        
        return version
        
    except Exception as e:
        print(f"🔥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    version = create_version()
    print(f"\n✅ Version {version.name} created successfully!")
    print(f"   URL: {JIRA_URL}/projects/{JIRA_PROJECT_KEY}/versions/{version.id}")
