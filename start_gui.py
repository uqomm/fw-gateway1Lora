#!/usr/bin/env python3
"""
LoRa Gateway Configuration Tool Launcher
Python replacement for start_gui.bat
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or later is required")
        print(f"Current version: {sys.version}")
        input("Press Enter to exit...")
        sys.exit(1)

def install_package(package_name):
    """Install a Python package if not already installed"""
    try:
        __import__(package_name.replace('-', '_'))
        return True
    except ImportError:
        print(f"Installing {package_name}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
            return True
        except subprocess.CalledProcessError:
            print(f"ERROR: Failed to install {package_name}")
            return False

def main():
    print("===============================")
    print("LoRa Gateway Configuration Tool")
    print("===============================")
    print()

    # Check Python version
    check_python_version()
    print("Python found. Checking dependencies...")

    # Install required packages
    required_packages = ['pyserial', 'crccheck']
    for package in required_packages:
        if not install_package(package):
            input("Press Enter to exit...")
            sys.exit(1)

    print()
    print("Starting LoRa Gateway Configuration Tool...")
    print()

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the GUI script
    gui_script = os.path.join(script_dir, 'scripts', 'lora_gui_config.py')

    # Check if GUI script exists
    if not os.path.exists(gui_script):
        print(f"ERROR: GUI script not found at {gui_script}")
        input("Press Enter to exit...")
        sys.exit(1)

    # Run the GUI application
    try:
        result = subprocess.run([sys.executable, gui_script])
        if result.returncode != 0:
            print()
            print("ERROR: Application failed to start")
            print("Check the error messages above")
            input("Press Enter to exit...")
            sys.exit(1)
    except KeyboardInterrupt:
        print()
        print("Application interrupted by user")
    except Exception as e:
        print()
        print(f"ERROR: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()