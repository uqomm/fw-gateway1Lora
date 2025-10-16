#!/usr/bin/env python3
"""
STM32 Gateway Flasher - Portable Version
Flashes gateway-2lora firmware to STM32G474 via ST-Link

Requirements:
    - Python 3.6+
    - ST-Link connected to target board

To create EXE:
    pip install pyinstaller
    pyinstaller --onefile --icon=icon.ico --name=STM32_Gateway_Flasher flash_gateway.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class STM32Flasher:
    def __init__(self):
        self.script_dir = Path(__file__).parent.resolve()
        self.project_root = self.script_dir.parent
        self.bin_file = self.project_root / "projects" / "gateway-2lora" / "Debug" / "gateway-2lora.bin"
        self.programmer = None
        self.use_openocd = False
        
    def print_banner(self):
        print("\n" + "="*50)
        print("   STM32 Gateway Firmware Flasher")
        print("   Portable Version - No IDE Required")
        print("="*50 + "\n")
    
    def find_programmer(self):
        """Find STM32 programmer tool"""
        search_paths = [
            # Bundled tools
            self.script_dir / "tools" / "STM32_Programmer_CLI.exe",
            
            # Standalone installation
            Path("C:/Program Files/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/STM32_Programmer_CLI.exe"),
            
            # STM32CubeIDE
            Path("C:/ST/STM32CubeIDE_1.11.0/STM32CubeIDE/plugins").glob("**/STM32_Programmer_CLI.exe"),
        ]
        
        for path in search_paths:
            if isinstance(path, Path) and path.exists():
                print(f"[INFO] Found STM32 Programmer: {path}")
                return str(path)
            # Handle glob results
            try:
                for p in path:
                    if p.exists():
                        print(f"[INFO] Found STM32 Programmer: {p}")
                        return str(p)
            except:
                pass
        
        # Try OpenOCD as fallback
        openocd_path = self.project_root / "tools" / "bin" / "openocd.exe"
        if openocd_path.exists():
            print(f"[INFO] STM32CubeProgrammer not found, using OpenOCD: {openocd_path}")
            self.use_openocd = True
            return str(openocd_path)
        
        return None
    
    def check_binary(self):
        """Check if firmware binary exists"""
        if not self.bin_file.exists():
            print(f"[ERROR] Firmware binary not found!")
            print(f"Expected: {self.bin_file}")
            print("\nPlease build the project first.")
            return False
        
        size_kb = self.bin_file.stat().st_size / 1024
        print(f"[INFO] Firmware: {self.bin_file.name}")
        print(f"[INFO] Size: {size_kb:.1f} KB")
        return True
    
    def flash_with_stm32cube(self):
        """Flash using STM32CubeProgrammer CLI"""
        print("\n[STEP 1/3] Connecting to ST-Link and erasing...")
        
        # Erase
        cmd_erase = [
            self.programmer,
            "-c", "port=SWD", "mode=UR", "reset=HWrst",
            "-e", "all"
        ]
        
        result = subprocess.run(cmd_erase, capture_output=False)
        if result.returncode != 0:
            return False
        
        print("\n[STEP 2/3] Programming flash memory...")
        
        # Program
        cmd_program = [
            self.programmer,
            "-c", "port=SWD", "mode=UR", "reset=HWrst",
            "-w", str(self.bin_file), "0x08000000",
            "-v", "-rst"
        ]
        
        result = subprocess.run(cmd_program, capture_output=False)
        if result.returncode != 0:
            return False
        
        print("\n[STEP 3/3] Verification complete!")
        return True
    
    def flash_with_openocd(self):
        """Flash using OpenOCD"""
        openocd_scripts = self.project_root / "tools" / "share" / "openocd" / "scripts"
        
        print("\n[STEP 1/2] Erasing flash...")
        
        cmd_erase = [
            self.programmer,
            "-s", str(openocd_scripts),
            "-f", "interface/stlink.cfg",
            "-f", "target/stm32g4x.cfg",
            "-c", "init",
            "-c", "reset halt",
            "-c", "flash erase_sector 0 0 last",
            "-c", "exit"
        ]
        
        result = subprocess.run(cmd_erase, capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stderr)
            return False
        
        print("\n[STEP 2/2] Programming flash...")
        
        cmd_program = [
            self.programmer,
            "-s", str(openocd_scripts),
            "-f", "interface/stlink.cfg",
            "-f", "target/stm32g4x.cfg",
            "-c", f"program {self.bin_file} verify reset exit 0x08000000"
        ]
        
        result = subprocess.run(cmd_program, capture_output=False)
        if result.returncode != 0:
            return False
        
        return True
    
    def print_success(self):
        print("\n" + "="*50)
        print("   PROGRAMMING SUCCESSFUL!")
        print("="*50)
        print("\nDevice is now running FSK Scanner firmware.")
        print("\nFeatures:")
        print("  - Auto-starts scanning at 175 MHz")
        print("  - Tests 9,600 parameter combinations")
        print("  - Auto-saves detected configurations")
        print("\nUsage:")
        print("  1. Connect serial monitor (115200 baud)")
        print("  2. Press Becker remote every 30-60 seconds")
        print("  3. Wait for 'SIGNAL DETECTED' message")
        print()
    
    def print_error(self):
        print("\n[ERROR] Flash programming failed!")
        print("\nTroubleshooting:")
        print("  - Ensure ST-Link is connected via USB")
        print("  - Check target board has power (3.3V)")
        print("  - Close other tools using ST-Link")
        print("  - Try disconnecting and reconnecting ST-Link")
        print()
    
    def run(self):
        """Main execution"""
        self.print_banner()
        
        # Find programmer
        self.programmer = self.find_programmer()
        if not self.programmer:
            print("[ERROR] No flash programmer found!")
            print("\nPlease install one of:")
            print("  1. STM32CubeProgrammer (standalone)")
            print("     https://www.st.com/stm32cubeprog")
            print("\n  2. Extract STM32_Programmer_CLI.exe to scripts/tools/")
            print()
            return 1
        
        # Check binary
        if not self.check_binary():
            return 1
        
        print()
        
        # Flash
        try:
            if self.use_openocd:
                success = self.flash_with_openocd()
            else:
                success = self.flash_with_stm32cube()
            
            if success:
                self.print_success()
                return 0
            else:
                self.print_error()
                return 1
        
        except KeyboardInterrupt:
            print("\n\n[INFO] Cancelled by user.")
            return 1
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            self.print_error()
            return 1

def main():
    flasher = STM32Flasher()
    exit_code = flasher.run()
    
    # Pause if run from double-click
    if sys.stdin.isatty():
        input("\nPress Enter to exit...")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
