#!/usr/bin/env python3
"""
STM32 Debug Script - Cross Platform Debug Utility
Works on Windows, Linux, and macOS
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import signal

# Colors for console output
class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'

def color_text(text, color):
    return f"{color}{text}{Colors.RESET}"

def get_openocd_path():
    """Get the appropriate OpenOCD path for the current platform"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    if platform.system() == "Windows":
        return project_root / "tools" / "bin" / "openocd.exe"
    else:
        # On Unix systems, try to use system OpenOCD first
        try:
            subprocess.run(["openocd", "--version"], capture_output=True, check=True)
            return "openocd"
        except:
            # Fallback to local installation if available
            return project_root / "tools" / "bin" / "openocd"

def create_debug_config(project_root, elf_file):
    """Create a temporary debug configuration with absolute paths"""
    debug_config_content = f"""# Debug script for STM32F103C8
# Auto-generated debug configuration

# Interface configuration
source [find interface/stlink.cfg]

# Target configuration  
source [find target/stm32f1x.cfg]

# Optional: Set working area
$_TARGETNAME configure -work-area-phys 0x20000000 -work-area-size 0x1000 -work-area-backup 0

# GDB configuration
gdb_port 3333
telnet_port 4444

# Initialize and halt
init
reset halt

echo "OpenOCD server started. Connect GDB to localhost:3333"
echo "Use: arm-none-eabi-gdb {elf_file}"
echo "Then in GDB: target remote localhost:3333"
echo "Load with: (gdb) load"
"""
    
    # Write temporary config file
    temp_config = project_root / "tools" / "config" / "debug" / "debug_temp.cfg"
    temp_config.parent.mkdir(parents=True, exist_ok=True)
    
    with open(temp_config, 'w') as f:
        f.write(debug_config_content)
    
    return temp_config

def start_debug_session(config="Debug", project="gateway_lora"):
    print(color_text("🐛 STM32 Debug Utility", Colors.GREEN))
    print(color_text("======================", Colors.GREEN))
    print()
    
    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    build_dir = project_root / project / config
    elf_file = build_dir / f"{project}.elf"
    
    # Check if ELF file exists
    if not elf_file.exists():
        print(color_text(f"❌ ELF file not found: {elf_file}", Colors.RED))
        print(color_text("Please build the project first: python scripts/build.py", Colors.YELLOW))
        return False
    
    # Check OpenOCD
    openocd_path = get_openocd_path()
    
    if isinstance(openocd_path, Path) and not openocd_path.exists():
        print(color_text(f"❌ OpenOCD not found: {openocd_path}", Colors.RED))
        return False
    
    # Create debug configuration with absolute paths
    debug_config = create_debug_config(project_root, elf_file)
    
    print(color_text("📋 Debug Session Information:", Colors.BLUE))
    print(color_text(f"  Project: {project}", Colors.BLUE))
    print(color_text(f"  Config:  {config}", Colors.BLUE))
    print(color_text(f"  ELF:     {elf_file}", Colors.BLUE))
    print()
    
    print(color_text("🔌 Starting OpenOCD GDB Server...", Colors.YELLOW))
    print(color_text("📡 Server will listen on localhost:3333", Colors.BLUE))
    print()
    
    print(color_text("💡 Debug Instructions:", Colors.GREEN))
    print(color_text("  1. OpenOCD will start and halt the target", Colors.BLUE))
    print(color_text("  2. In another terminal, run:", Colors.BLUE))
    print(color_text(f"     arm-none-eabi-gdb {elf_file}", Colors.YELLOW))
    print(color_text("  3. In GDB, connect to OpenOCD:", Colors.BLUE))
    print(color_text("     (gdb) target remote localhost:3333", Colors.YELLOW))
    print(color_text("     (gdb) load", Colors.YELLOW))
    print(color_text("     (gdb) monitor reset halt", Colors.YELLOW))
    print(color_text("     (gdb) break main", Colors.YELLOW))
    print(color_text("     (gdb) continue", Colors.YELLOW))
    print()
    
    print(color_text("💡 VS Code Users:", Colors.GREEN))
    print(color_text("  Press F5 in VS Code to start integrated debugging", Colors.BLUE))
    print(color_text("  Or use 'STM32 Debug (External OpenOCD)' launch config", Colors.BLUE))
    print()
    
    print(color_text("🛑 Press Ctrl+C to stop the debug server", Colors.YELLOW))
    print()
    
    temp_config_created = False
    try:
        if platform.system() == "Windows":
            scripts_path = project_root / "tools" / "share" / "openocd" / "scripts"
            cmd = [
                str(openocd_path),
                "-s", str(scripts_path),
                "-f", str(debug_config)
            ]
        else:
            cmd = [str(openocd_path), "-f", str(debug_config)]
        
        temp_config_created = True
        
        # Start OpenOCD debug server
        print(color_text("🔌 OpenOCD starting...", Colors.BLUE))
        process = subprocess.Popen(cmd)
        
        # Wait for process to complete or be interrupted
        try:
            process.wait()
        except KeyboardInterrupt:
            print()
            print(color_text("🛑 Stopping debug server...", Colors.YELLOW))
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        
        return True
    
    except Exception as e:
        print(color_text(f"❌ Error starting debug server: {e}", Colors.RED))
        return False
    finally:
        # Clean up temporary config file
        if temp_config_created and debug_config.exists() and debug_config.name == "debug_temp.cfg":
            try:
                debug_config.unlink()
            except:
                pass
        
        print()
        print(color_text("🔌 Debug server stopped", Colors.YELLOW))

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="STM32 Cross-Platform Debug Utility")
    parser.add_argument("--config", default="Debug", choices=["Debug", "Release"],
                       help="Build configuration")
    parser.add_argument("--project", default="gateway_lora",
                       help="Project name")
    
    args = parser.parse_args()
    
    print(color_text("🚀 STM32 Debug System", Colors.MAGENTA))
    print(color_text(f"Platform: {platform.system()}", Colors.CYAN))
    print()
    
    success = start_debug_session(args.config, args.project)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
