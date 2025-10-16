#!/usr/bin/env python3
"""
STM32 Build System - PATH Setup Script
Python replacement for setup_path.ps1 PowerShell script

This script permanently adds make to Windows PATH for STM32 development.
Run with administrator privileges for system-wide installation.
"""

import os
import sys
import subprocess
import platform
import argparse

def is_admin():
    """Check if running with administrator privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_make_path():
    """Get the path to GnuWin32 make"""
    return r"C:\Program Files (x86)\GnuWin32\bin"

def check_make_exists(make_path):
    """Check if make.exe exists at the specified path"""
    make_exe = os.path.join(make_path, "make.exe")
    return os.path.exists(make_exe)

def get_current_path(scope="user"):
    """Get current PATH from environment"""
    if scope == "system":
        return os.environ.get('PATH', '')
    else:
        # For user scope, we need to read from registry or use current session
        return os.environ.get('PATH', '')

def update_path_registry(new_path, scope="user"):
    """Update PATH in Windows registry"""
    try:
        import winreg

        if scope == "system":
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                               0, winreg.KEY_SET_VALUE)
        else:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r"Environment",
                               0, winreg.KEY_SET_VALUE)

        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"❌ Failed to update registry: {e}")
        return False

def test_make():
    """Test if make command works"""
    try:
        result = subprocess.run(["make", "--version"],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.strip().split('\n')[0]
            print(f"✅ Make is working: {version_line}")
            return True
        else:
            print("❌ Make command failed")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Make command not found or not working")
        return False

def main():
    if platform.system() != "Windows":
        print("❌ This script is designed for Windows only")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Setup PATH for STM32 development")
    parser.add_argument("--system", action="store_true",
                       help="Install system-wide (requires administrator)")
    parser.add_argument("--force", action="store_true",
                       help="Force installation even if already in PATH")

    args = parser.parse_args()

    print("🔧 STM32 Build System - PATH Setup")
    print("=================================")
    print()

    make_path = get_make_path()

    # Check current PATH
    current_path = os.environ.get('PATH', '')
    path_contains_make = make_path in current_path

    if path_contains_make and not args.force:
        print("✅ Make is already in current session PATH")
    else:
        print("⚠️  Make is NOT in current session PATH")

    # Check if make exists
    if check_make_exists(make_path):
        print(f"✅ Found make.exe at: {make_path}")
    else:
        print(f"❌ ERROR: make.exe not found at: {make_path}")
        print("Please install GnuWin32 make or update the path in this script")
        sys.exit(1)

    print()
    print("Choose installation scope:")

    scope = "user"
    if args.system:
        if not is_admin():
            print("❌ System-wide installation requires administrator privileges")
            print("Run with: python setup_path.py --system")
            print("(or run your terminal/PyCharm as Administrator)")
            sys.exit(1)
        scope = "system"
        print("Installing system-wide...")
    else:
        print("Installing for current user only...")

    # Check if already in registry PATH
    try:
        import winreg
        if scope == "system":
            key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
        else:
            key_path = r"Environment"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)

        reg_path, _ = winreg.QueryValueEx(key, "PATH")
        winreg.CloseKey(key)

        if make_path in reg_path and not args.force:
            print(f"✅ Make path is already in {scope} PATH!")
            print("No changes needed.")
        else:
            print(f"Adding to {scope} PATH...")

            # Add the new path
            if reg_path.endswith(';'):
                new_path = reg_path + make_path
            else:
                new_path = reg_path + ";" + make_path

            # Update registry
            if update_path_registry(new_path, scope):
                print(f"✅ Successfully added to {scope} PATH!")
                print(f"New PATH length: {len(new_path)} characters")
            else:
                print("❌ Failed to update PATH in registry")
                sys.exit(1)

    except Exception as e:
        print(f"❌ Error accessing registry: {e}")
        print("Falling back to session-only PATH update...")

        # Fallback: just update current session
        os.environ['PATH'] = current_path + ";" + make_path
        print("✅ Updated PATH for current session only")

    print()
    print("🔄 Testing make command...")

    # Test make command
    if test_make():
        print()
        print("✅ PATH setup completed!")
        print()
        if scope == "system":
            print("📝 Note: Restart applications to use the new PATH")
        else:
            print("📝 Note: New terminals will automatically have the updated PATH")
    else:
        print()
        print("❌ Make command test failed")
        print("You may need to restart your terminal or computer")

if __name__ == "__main__":
    main()