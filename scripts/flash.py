#!/usr/bin/env python3
"""
STM32 Flash Script - Cross Platform Flashing Utility
Works on Windows, Linux, and macOS
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

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

def flash_firmware(config="Debug", project="gateway_lora"):
    print(color_text("🚀 STM32 Flash Utility", Colors.GREEN))
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
    flash_config = project_root / "tools" / "config" / "flash" / "flash_stm32.cfg"
    
    if isinstance(openocd_path, Path) and not openocd_path.exists():
        print(color_text(f"❌ OpenOCD not found: {openocd_path}", Colors.RED))
        return False
    
    if not flash_config.exists():
        print(color_text(f"❌ Flash config not found: {flash_config}", Colors.RED))
        return False
    
    print(color_text("📋 Flash Information:", Colors.BLUE))
    print(color_text(f"  Project: {project}", Colors.BLUE))
    print(color_text(f"  Config:  {config}", Colors.BLUE))
    print(color_text(f"  ELF:     {elf_file}", Colors.BLUE))
    print()
    
    # Display binary information
    print(color_text("📊 Binary Information:", Colors.YELLOW))
    try:
        subprocess.run(["arm-none-eabi-size", str(elf_file)], check=True)
    except subprocess.CalledProcessError:
        print(color_text("⚠️ Could not get binary size information", Colors.YELLOW))
    print()
      # Flash the device
    print(color_text("📡 Programming STM32 via ST-Link...", Colors.YELLOW))
    print(color_text("🔌 Connecting to device...", Colors.BLUE))
    
    try:
        # Create temporary OpenOCD script with correct path
        import tempfile
        
        # Convert path to forward slashes for OpenOCD
        elf_path_for_openocd = str(elf_file).replace('\\', '/')
        
        openocd_script = f"""# OpenOCD Flash Script for STM32F103C8 (Generated)
# Interface configuration
source [find interface/stlink.cfg]

# Target configuration
source [find target/stm32f1x.cfg]

# Optional: Set working area for faster flash operations
$_TARGETNAME configure -work-area-phys 0x20000000 -work-area-size 0x1000 -work-area-backup 0

# Flash and run
init
reset halt
flash write_image erase {elf_path_for_openocd}
reset run
shutdown
"""
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as temp_file:
            temp_file.write(openocd_script)
            temp_config_path = temp_file.name
        
        if platform.system() == "Windows":
            scripts_path = project_root / "tools" / "share" / "openocd" / "scripts"
            cmd = [
                str(openocd_path),
                "-s", str(scripts_path),
                "-f", temp_config_path
            ]
        else:
            cmd = [str(openocd_path), "-f", temp_config_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temporary file
        Path(temp_config_path).unlink(missing_ok=True)
        
        if result.returncode == 0:
            print(color_text("✅ Flashing completed successfully!", Colors.GREEN))
            print(color_text("🎯 Device is ready to run", Colors.BLUE))
            return True
        else:
            print(color_text(f"❌ Flashing failed with exit code: {result.returncode}", Colors.RED))
            print(color_text("💡 Check ST-Link connection and device power", Colors.YELLOW))
            if result.stderr:
                print(color_text("Error output:", Colors.RED))
                print(result.stderr)
            if result.stdout:
                print(color_text("Output:", Colors.YELLOW))
                print(result.stdout)
            return False
    
    except Exception as e:
        print(color_text(f"❌ Error during flashing: {e}", Colors.RED))
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="STM32 Cross-Platform Flash Utility")
    parser.add_argument("--config", default="Debug", choices=["Debug", "Release"],
                       help="Build configuration")
    parser.add_argument("--project", default="gateway_lora",
                       help="Project name")
    
    args = parser.parse_args()
    
    print(color_text("🚀 STM32 Flash System", Colors.MAGENTA))
    print(color_text(f"Platform: {platform.system()}", Colors.CYAN))
    print()
    
    success = flash_firmware(args.config, args.project)
    
    if success:
        print()
        print(color_text("🎉 Flash operation completed!", Colors.GREEN))
    else:
        print()
        print(color_text("❌ Flash operation failed!", Colors.RED))
        sys.exit(1)

if __name__ == "__main__":
    main()
