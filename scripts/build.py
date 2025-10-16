#!/usr/bin/env python3
"""
STM32 Build System - Cross Platform Build Script
Works on Windows, Linux, and macOS
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path
from datetime import datetime
import shutil

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

def show_help():
    print()
    print(color_text("🔨 STM32 LoRa Gateway Build System", Colors.GREEN))
    print(color_text("===================================", Colors.GREEN))
    print()
    print(color_text("Usage:", Colors.CYAN))
    print("  python scripts/build.py <action>")
    print()
    print(color_text("Available Actions:", Colors.YELLOW))
    print("  build     - Build the firmware")
    print("  clean     - Clean build files")
    print("  rebuild   - Clean and rebuild")
    print("  flash     - Flash firmware to device")
    print("  debug     - Start debug session")
    print("  validate  - Validate environment")
    print("  help      - Show this help")
    print()
    print(color_text("Examples:", Colors.BLUE))
    print("  python scripts/build.py build")
    print("  python scripts/build.py flash")
    print("  python scripts/build.py validate")
    print()

def get_version_info():
    """Get version information from git and changelog"""
    version_info = {
        "version": "2.0.0",  # Default version
        "build_date": datetime.now().strftime("%Y-%m-%d"),
        "build_time": datetime.now().strftime("%H:%M:%S"),
        "git_hash": "unknown",
        "git_tag": "v2.0.0"
    }
    
    try:
        # Try to get git hash
        result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_info["git_hash"] = result.stdout.strip()
    except:
        pass
    
    try:
        # Try to get latest git tag
        result = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            tag = result.stdout.strip()
            version_info["git_tag"] = tag
            # Extract version number from tag (remove 'v' prefix if present)
            if tag.startswith('v'):
                version_info["version"] = tag[1:]
            else:
                version_info["version"] = tag
    except:
        pass
    
    return version_info

def create_version_header(version_info):
    """Create version header file"""
    header_content = f"""/* Auto-generated version header file */
/* Generated on {version_info['build_date']} at {version_info['build_time']} */

#ifndef VERSION_H
#define VERSION_H

#define FIRMWARE_VERSION "{version_info['version']}"
#define BUILD_DATE "{version_info['build_date']}"
#define BUILD_TIME "{version_info['build_time']}"
#define GIT_HASH "{version_info['git_hash']}"
#define GIT_TAG "{version_info['git_tag']}"

#define VERSION_STRING "{version_info['git_tag']} ({version_info['build_date']})"

#endif /* VERSION_H */
"""
    
    # Get the absolute path to the project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    inc_dir = project_root / "gateway_lora" / "Core" / "Inc"
    
    version_header_path = inc_dir / "version.h"
    
    try:
        with open(version_header_path, 'w') as f:
            f.write(header_content)
        print(f"{color_text('📝', Colors.BLUE)} Version header created: {version_header_path}")
        return True
    except Exception as e:
        print(f"{color_text('⚠️', Colors.YELLOW)} Could not create version header: {e}")
        return False

def copy_versioned_elf(version_info):
    """Copy the compiled ELF file with version information in the filename"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Source ELF file path
    source_elf = project_root / "gateway_lora" / "Debug" / "gateway_lora.elf"
    
    # Destination with version info
    versioned_filename = f"gateway_lora_v{version_info['version']}_{version_info['build_date']}.elf"
    dest_elf = project_root / versioned_filename
    
    try:
        if source_elf.exists():
            shutil.copy2(source_elf, dest_elf)
            print(f"{color_text('📦', Colors.GREEN)} Versioned ELF created: {versioned_filename}")
            
            # Also copy HEX file if it exists
            source_hex = project_root / "gateway_lora" / "Debug" / "gateway_lora.hex"
            if source_hex.exists():
                hex_filename = f"gateway_lora_v{version_info['version']}_{version_info['build_date']}.hex"
                dest_hex = project_root / hex_filename
                shutil.copy2(source_hex, dest_hex)
                print(f"{color_text('📦', Colors.GREEN)} Versioned HEX created: {hex_filename}")
            
            # Also copy BIN file if it exists
            source_bin = project_root / "gateway_lora" / "Debug" / "gateway_lora.bin"
            if source_bin.exists():
                bin_filename = f"gateway_lora_v{version_info['version']}_{version_info['build_date']}.bin"
                dest_bin = project_root / bin_filename
                shutil.copy2(source_bin, dest_bin)
                print(f"{color_text('📦', Colors.GREEN)} Versioned BIN created: {bin_filename}")
            
            return True
        else:
            print(f"{color_text('⚠️', Colors.YELLOW)} Source ELF file not found: {source_elf}")
            return False
    except Exception as e:
        print(f"{color_text('❌', Colors.RED)} Error copying versioned ELF: {e}")
        return False

def create_build_info_file(version_info):
    """Create build info file for tracking (metadata only)"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    filename = f"gateway_lora_v{version_info['version']}_{version_info['build_date']}_build_info.txt"
    build_info_path = project_root / filename
    
    # Create detailed build info content
    build_content = f"""# Gateway LoRa Firmware - Release v{version_info['version']}
# Build Date: {version_info['build_date']} {version_info['build_time']}
# Project: gateway_lora
# Git Hash: {version_info['git_hash']}
# Git Tag: {version_info['git_tag']}

## Build Information
Version: {version_info['version']}
Build Date: {version_info['build_date']}
Build Time: {version_info['build_time']}
Project Name: gateway_lora
Target: STM32F103C8T6
Toolchain: arm-none-eabi-gcc
Git Hash: {version_info['git_hash']}
Git Tag: {version_info['git_tag']}

## Binary Files
ELF: projects/gateway_lora/Debug/gateway_lora.elf
HEX: projects/gateway_lora/Debug/gateway_lora.hex
BIN: projects/gateway_lora/Debug/gateway_lora.bin

## Versioned Files
ELF: gateway_lora_v{version_info['version']}_{version_info['build_date']}.elf
HEX: gateway_lora_v{version_info['version']}_{version_info['build_date']}.hex
BIN: gateway_lora_v{version_info['version']}_{version_info['build_date']}.bin

## Build Commands
Build: python .\\scripts\\build.py build
Flash: python .\\scripts\\flash.py flash
Debug: python .\\scripts\\debug.py debug
Validate: python .\\scripts\\validate.py validate

---
Generated automatically by Gateway LoRa Build System
Build completed on {version_info['build_date']} at {version_info['build_time']}
"""
    
    try:
        with open(build_info_path, 'w') as f:
            f.write(build_content)
        print(f"{color_text('📋', Colors.GREEN)} Build info file created: {filename}")
        return True
    except Exception as e:
        print(f"{color_text('⚠️', Colors.YELLOW)} Could not create build info file: {e}")
        return False

def run_command(cmd, cwd=None):
    """Run a command and return True if successful"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{color_text('❌', Colors.RED)} Command failed: {e}")
        return False

def build_project(action="build"):
    print(color_text(f"🔨 {action.capitalize()} project...", Colors.GREEN))
    
    # Get version information
    version_info = get_version_info()
    print(f"{color_text('📊', Colors.CYAN)} Version: {version_info['version']}")
    print(f"{color_text('📅', Colors.CYAN)} Build Date: {version_info['build_date']} {version_info['build_time']}")
    print(f"{color_text('🔗', Colors.CYAN)} Git: {version_info['git_tag']} ({version_info['git_hash']})")
    
    # Create version header
    create_version_header(version_info)
    
    # Get the absolute path to the project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    build_dir = project_root / "gateway_lora" / "Debug"
    
    if not build_dir.exists():
        print(color_text("❌ Build directory not found!", Colors.RED))
        print(f"Expected: {build_dir}")
        return False
    
    try:
        if action in ["clean", "rebuild"]:
            print(color_text("🧹 Cleaning previous build...", Colors.YELLOW))
            if not run_command("make clean", cwd=build_dir):
                return False
        
        if action in ["build", "rebuild"]:
            print(color_text("⚙️ Compiling firmware...", Colors.BLUE))
            if not run_command("make all -j4", cwd=build_dir):
                return False
            
            # Generate HEX and BIN files
            project = "gateway_lora"
            elf_file = build_dir / f"{project}.elf"
            
            if elf_file.exists():
                print(color_text("🔄 Generating HEX file...", Colors.YELLOW))
                hex_cmd = f"arm-none-eabi-objcopy -O ihex {project}.elf {project}.hex"
                if not run_command(hex_cmd, cwd=build_dir):
                    return False
                
                print(color_text("🔄 Generating BIN file...", Colors.YELLOW))
                bin_cmd = f"arm-none-eabi-objcopy -O binary {project}.elf {project}.bin"
                if not run_command(bin_cmd, cwd=build_dir):
                    return False
                
                print(color_text("✅ Build successful!", Colors.GREEN))
                print(color_text("📊 Binary size:", Colors.BLUE))
                run_command(f"arm-none-eabi-size {project}.elf", cwd=build_dir)
                
                # Copy versioned ELF, HEX, and BIN files
                copy_versioned_elf(version_info)
                
                # Create build info file
                create_build_info_file(version_info)
        
        return True
    except Exception as e:
        print(color_text(f"❌ Build failed: {e}", Colors.RED))
        return False

def check_environment():
    print(color_text("🔍 Checking environment...", Colors.BLUE))
    # Basic environment check
    tools = ["arm-none-eabi-gcc", "make", "git"]
    for tool in tools:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True)
            if result.returncode == 0:
                print(f"{color_text('✅', Colors.GREEN)} {tool} found")
            else:
                print(f"{color_text('❌', Colors.RED)} {tool} not found")
        except:
            print(f"{color_text('❌', Colors.RED)} {tool} not found")

def main():
    parser = argparse.ArgumentParser(description="STM32 Cross-Platform Build System")
    parser.add_argument("action", nargs="?", default="help",
                       choices=["build", "clean", "rebuild", "flash", "debug", "validate", "help"],
                       help="Action to perform")
    
    args = parser.parse_args()
    
    print(color_text("🚀 STM32 Build System", Colors.MAGENTA))
    print(color_text(f"Action: {args.action}", Colors.CYAN))
    print()
    
    if args.action in ["build", "clean", "rebuild"]:
        build_project(args.action)
    elif args.action == "flash":
        print(color_text("📡 Flash functionality", Colors.YELLOW))
        print("Use: python scripts/flash.py")
    elif args.action == "debug":
        print(color_text("🐛 Debug functionality", Colors.YELLOW))
        print("Use: python scripts/debug.py")
    elif args.action == "validate":
        check_environment()
    else:
        show_help()

if __name__ == "__main__":
    main()