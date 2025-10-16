#!/usr/bin/env python3
"""
STM32 Environment Validation Script - Cross Platform
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

def check_command(command, name):
    """Check if a command is available"""
    try:
        result = subprocess.run([command, "--version"], 
                              capture_output=True, check=True, text=True)
        version_line = result.stdout.split('\n')[0]
        print(f"{color_text('✅', Colors.GREEN)} {name}: {version_line}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{color_text('❌', Colors.RED)} {name} not found")
        return False

def check_file_or_dir(path, name, optional=False):
    """Check if a file or directory exists"""
    if path.exists():
        print(f"{color_text('✅', Colors.GREEN)} {name}")
        return True
    elif optional:
        print(f"{color_text('⚠️', Colors.YELLOW)} {name} (optional)")
        return True
    else:
        print(f"{color_text('❌', Colors.RED)} {name} not found")
        return False

def validate_environment(detailed=False):
    print(color_text("🔍 STM32 Development Environment Validation", Colors.GREEN))
    print(color_text("=" * 48, Colors.GREEN))
    print()
    
    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Platform information
    current_platform = platform.system()
    python_version = platform.python_version()
    print(color_text("📋 System Information:", Colors.BLUE))
    print(f"Platform: {color_text(current_platform, Colors.CYAN)}")
    print(f"Python: {color_text(python_version, Colors.CYAN)}")
    print(f"Working directory: {color_text(str(project_root), Colors.CYAN)}")
    print()
    
    all_good = True
    
    # Check project structure
    print(color_text("📁 Project Structure:", Colors.YELLOW))
    structure_checks = [
        (project_root / "gateway_lora", "STM32 Project Directory", False),
        (project_root / "gateway_lora" / "Debug", "Build Directory", False),
        (project_root / "tools", "Tools Directory", False),
        (project_root / "tools" / "bin" / "openocd.exe", "OpenOCD (Windows)", current_platform != "Windows"),
        (project_root / ".vscode", "VS Code Configuration", True),
        (project_root / "scripts", "Build Scripts", False),
        (project_root / "tools" / "config", "OpenOCD Configurations", False)
    ]
    
    for path, name, optional in structure_checks:
        if not check_file_or_dir(path, name, optional):
            if not optional:
                all_good = False
    
    print()
    
    # Check development tools
    print(color_text("🔧 Development Tools:", Colors.YELLOW))
    tool_checks = [
        ("arm-none-eabi-gcc", "ARM GCC Toolchain"),
        ("arm-none-eabi-objcopy", "ARM Objcopy"),
        ("arm-none-eabi-size", "ARM Size Utility"),
        ("make", "GNU Make"),
        ("python", "Python")
    ]
    
    for command, name in tool_checks:
        if not check_command(command, name):
            all_good = False
    
    # Check OpenOCD
    if current_platform == "Windows":
        openocd_path = project_root / "tools" / "bin" / "openocd.exe"
        if openocd_path.exists():
            try:
                result = subprocess.run([str(openocd_path), "--version"], 
                                      capture_output=True, check=True, text=True)
                version_line = result.stdout.split('\n')[0]
                print(f"{color_text('✅', Colors.GREEN)} OpenOCD: {version_line}")
            except subprocess.CalledProcessError:
                print(f"{color_text('❌', Colors.RED)} OpenOCD executable error")
                all_good = False
        else:
            print(f"{color_text('❌', Colors.RED)} OpenOCD not found")
            all_good = False
    else:
        if not check_command("openocd", "OpenOCD"):
            all_good = False
    
    print()
    
    # Check build output
    print(color_text("🏗️ Build Output:", Colors.YELLOW))
    build_dir = project_root / "gateway_lora" / "Debug"
    build_files = [
        (build_dir / "gateway_lora.elf", "ELF executable"),
        (build_dir / "gateway_lora.hex", "HEX file"),
        (build_dir / "gateway_lora.bin", "Binary file"),
        (build_dir / "makefile", "Makefile")
    ]
    
    for file_path, name in build_files:
        check_file_or_dir(file_path, name, optional=True)
    
    print()
    
    if detailed:
        # Detailed checks
        print(color_text("🔍 Detailed Analysis:", Colors.YELLOW))
        
        # Check PATH
        path_env = os.environ.get('PATH', '')
        arm_in_path = any('arm' in p.lower() for p in path_env.split(os.pathsep))
        print(f"ARM tools in PATH: {color_text('Yes' if arm_in_path else 'No', Colors.GREEN if arm_in_path else Colors.YELLOW)}")
        
        # Check VS Code extensions (if .vscode exists)
        vscode_dir = project_root / ".vscode"
        if vscode_dir.exists():
            extensions_file = vscode_dir / "extensions.json"
            if extensions_file.exists():
                print(f"{color_text('✅', Colors.GREEN)} VS Code extensions configuration found")
            else:
                print(f"{color_text('⚠️', Colors.YELLOW)} VS Code extensions configuration not found")
        
        # Check build artifacts size
        elf_file = build_dir / "gateway_lora.elf"
        if elf_file.exists():
            try:
                result = subprocess.run(["arm-none-eabi-size", str(elf_file)], 
                                      capture_output=True, check=True, text=True)
                print(f"{color_text('📊', Colors.BLUE)} Binary size information:")
                print(result.stdout)
            except subprocess.CalledProcessError:
                pass
        
        print()
    
    # Summary
    print(color_text("📋 Validation Summary:", Colors.BLUE))
    if all_good:
        print(f"{color_text('✅', Colors.GREEN)} All essential checks passed!")
        print(f"{color_text('🎉', Colors.GREEN)} Your STM32 development environment is ready!")
    else:
        print(f"{color_text('❌', Colors.RED)} Some essential components are missing.")
        print(f"{color_text('💡', Colors.YELLOW)} Please install missing tools and try again.")
    
    print()
    
    # Quick start guide
    if all_good:
        print(color_text("🚀 Quick Start:", Colors.GREEN))
        print("  python scripts/build.py          # Build firmware")
        print("  python scripts/flash.py          # Flash to device")
        print("  python scripts/debug.py          # Start debug session")
        print("  python scripts/validate.py       # Validate environment")
    
    return all_good

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="STM32 Environment Validation")
    parser.add_argument("--detailed", action="store_true",
                       help="Show detailed analysis")
    
    args = parser.parse_args()
    
    print(color_text("🚀 STM32 Environment Validator", Colors.MAGENTA))
    print(color_text(f"Platform: {platform.system()}", Colors.CYAN))
    print()
    
    success = validate_environment(args.detailed)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
