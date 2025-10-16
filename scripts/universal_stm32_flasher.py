#!/usr/bin/env python3
"""
Universal STM32 Flasher
Flash any STM32 microcontroller via ST-Link (ELF, HEX, or BIN files)

Usage:
    STM32_Flasher.exe                    # Interactive mode
    STM32_Flasher.exe firmware.bin       # Flash BIN file
    STM32_Flasher.exe firmware.hex       # Flash HEX file
    STM32_Flasher.exe firmware.elf       # Flash ELF file
    STM32_Flasher.exe firmware.bin 0x08000000  # Flash BIN to specific address

To create EXE:
    pip install pyinstaller
    pyinstaller --onefile --name=STM32_Flasher universal_stm32_flasher.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading

class UniversalSTM32Flasher:
    def __init__(self):
        self.programmer = None
        self.use_openocd = False
        
    def find_programmer(self):
        """Find STM32 programmer tool"""
        # Common installation paths
        search_paths = [
            # Bundled with this tool
            Path(sys.executable).parent / "tools" / "STM32_Programmer_CLI.exe",
            Path(__file__).parent / "tools" / "STM32_Programmer_CLI.exe",
            
            # Standalone STM32CubeProgrammer
            Path("C:/Program Files/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/STM32_Programmer_CLI.exe"),
            Path("C:/Program Files (x86)/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/STM32_Programmer_CLI.exe"),
            
            # STM32CubeIDE installations
            Path("C:/ST").glob("**/STM32_Programmer_CLI.exe"),
        ]
        
        for path in search_paths:
            if isinstance(path, Path) and path.exists():
                return str(path)
            # Handle glob results
            try:
                for p in path:
                    if p.exists():
                        return str(p)
            except:
                pass
        
        return None
    
    def detect_device(self):
        """Detect connected STM32 device"""
        if not self.programmer:
            return None
        
        try:
            result = subprocess.run(
                [self.programmer, "-c", "port=SWD", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Parse device info from output
            if "Device name" in result.stdout:
                for line in result.stdout.split('\n'):
                    if "Device name" in line:
                        return line.split(':')[1].strip()
        except:
            pass
        
        return None
    
    def get_default_address(self, device_name):
        """Get default flash address based on device"""
        # Most STM32 devices start at 0x08000000
        return "0x08000000"
    
    def flash_file(self, firmware_path, address="0x08000000", erase_all=True, verify=True, reset=True):
        """Flash firmware file to STM32"""
        firmware_path = Path(firmware_path)
        
        if not firmware_path.exists():
            return False, f"File not found: {firmware_path}"
        
        if not self.programmer:
            return False, "STM32 Programmer not found. Please install STM32CubeProgrammer."
        
        # Determine file type
        file_ext = firmware_path.suffix.lower()
        if file_ext not in ['.bin', '.hex', '.elf']:
            return False, f"Unsupported file type: {file_ext}\nSupported: .bin, .hex, .elf"
        
        print(f"\n{'='*60}")
        print(f"  Universal STM32 Flasher")
        print(f"{'='*60}")
        print(f"\nFirmware: {firmware_path.name}")
        print(f"Size:     {firmware_path.stat().st_size / 1024:.1f} KB")
        print(f"Type:     {file_ext[1:].upper()}")
        print(f"Address:  {address}")
        print()
        
        # Step 1: Connect and erase
        if erase_all:
            print("[STEP 1/3] Erasing flash memory...")
            cmd_erase = [
                self.programmer,
                "-c", "port=SWD", "mode=UR", "reset=HWrst",
                "-e", "all"
            ]
            
            result = subprocess.run(cmd_erase, capture_output=False)
            if result.returncode != 0:
                return False, "Failed to erase flash memory"
        else:
            print("[STEP 1/3] Skipping erase (will erase only needed sectors)...")
        
        # Step 2: Program
        print("\n[STEP 2/3] Programming flash memory...")
        
        cmd_program = [
            self.programmer,
            "-c", "port=SWD", "mode=UR", "reset=HWrst",
            "-w", str(firmware_path)
        ]
        
        # Add address only for BIN files (HEX and ELF have embedded addresses)
        if file_ext == '.bin':
            cmd_program.append(address)
        
        if verify:
            cmd_program.append("-v")
        
        if reset:
            cmd_program.append("-rst")
        
        result = subprocess.run(cmd_program, capture_output=False)
        if result.returncode != 0:
            return False, "Failed to program flash memory"
        
        # Step 3: Done
        print("\n[STEP 3/3] Programming complete!")
        print(f"\n{'='*60}")
        print("  SUCCESS! Device programmed successfully.")
        print(f"{'='*60}\n")
        
        return True, "Programming successful"

class FlasherGUI:
    def __init__(self):
        self.flasher = UniversalSTM32Flasher()
        self.root = tk.Tk()
        self.root.title("Universal STM32 Flasher")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        self.create_widgets()
        self.check_programmer()
        
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#0066cc", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="Universal STM32 Flasher",
            font=("Arial", 18, "bold"),
            bg="#0066cc",
            fg="white"
        ).pack(pady=15)
        
        # Main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection
        file_frame = tk.LabelFrame(main_frame, text="Firmware File", padx=10, pady=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_path = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.file_path, width=50, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(file_frame, text="Browse...", command=self.browse_file, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Flash address (for BIN files)
        addr_frame = tk.LabelFrame(main_frame, text="Flash Address (for BIN files only)", padx=10, pady=10)
        addr_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.address = tk.StringVar(value="0x08000000")
        tk.Entry(addr_frame, textvariable=self.address, width=20).pack(side=tk.LEFT)
        tk.Label(addr_frame, text="(HEX and ELF files use embedded address)", fg="gray").pack(side=tk.LEFT, padx=(10, 0))
        
        # Options
        opt_frame = tk.LabelFrame(main_frame, text="Options", padx=10, pady=10)
        opt_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.erase_all = tk.BooleanVar(value=True)
        self.verify = tk.BooleanVar(value=True)
        self.reset = tk.BooleanVar(value=True)
        
        tk.Checkbutton(opt_frame, text="Mass erase before programming", variable=self.erase_all).pack(anchor=tk.W)
        tk.Checkbutton(opt_frame, text="Verify after programming", variable=self.verify).pack(anchor=tk.W)
        tk.Checkbutton(opt_frame, text="Reset device after programming", variable=self.reset).pack(anchor=tk.W)
        
        # Flash button
        self.flash_btn = tk.Button(
            main_frame,
            text="FLASH DEVICE",
            command=self.start_flash,
            bg="#0066cc",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2
        )
        self.flash_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Log output
        log_frame = tk.LabelFrame(main_frame, text="Output Log", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', bg="#f0f0f0")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def log(self, message):
        """Add message to log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()
        
    def check_programmer(self):
        """Check if programmer is available"""
        self.log("Searching for STM32 programming tools...")
        self.flasher.programmer = self.flasher.find_programmer()
        
        if self.flasher.programmer:
            self.log(f"✓ Found: {Path(self.flasher.programmer).name}")
            self.status_var.set("Ready - ST-Link programmer found")
        else:
            self.log("✗ STM32CubeProgrammer not found!")
            self.log("\nPlease install from:")
            self.log("https://www.st.com/stm32cubeprog")
            self.status_var.set("ERROR - Programmer not found")
            self.flash_btn.config(state='disabled')
    
    def browse_file(self):
        """Browse for firmware file"""
        filename = filedialog.askopenfilename(
            title="Select Firmware File",
            filetypes=[
                ("All Firmware", "*.bin *.hex *.elf"),
                ("Binary files", "*.bin"),
                ("Intel HEX files", "*.hex"),
                ("ELF files", "*.elf"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            self.file_path.set(filename)
            self.log(f"\nSelected: {Path(filename).name}")
            
            # Auto-detect if it's a BIN file and suggest address
            if filename.lower().endswith('.bin'):
                self.log("Note: BIN file requires flash address (default: 0x08000000)")
            else:
                self.log("Note: HEX/ELF files contain address information")
    
    def start_flash(self):
        """Start flashing in background thread"""
        if not self.file_path.get():
            messagebox.showwarning("No File", "Please select a firmware file first.")
            return
        
        if not self.flasher.programmer:
            messagebox.showerror("No Programmer", "STM32 Programmer not found. Please install STM32CubeProgrammer.")
            return
        
        # Disable button during flash
        self.flash_btn.config(state='disabled')
        self.status_var.set("Flashing...")
        
        # Run in thread to keep GUI responsive
        thread = threading.Thread(target=self.flash_thread)
        thread.daemon = True
        thread.start()
    
    def flash_thread(self):
        """Flash in background thread"""
        try:
            # Redirect stdout to GUI
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            success, message = self.flasher.flash_file(
                self.file_path.get(),
                self.address.get(),
                self.erase_all.get(),
                self.verify.get(),
                self.reset.get()
            )
            
            # Get captured output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # Show in log
            self.log(output)
            
            if success:
                self.status_var.set("SUCCESS - Device programmed")
                messagebox.showinfo("Success", "Device programmed successfully!")
            else:
                self.status_var.set("FAILED - See log for details")
                messagebox.showerror("Failed", message)
        
        except Exception as e:
            self.log(f"\nERROR: {str(e)}")
            self.status_var.set("ERROR - Flash failed")
            messagebox.showerror("Error", str(e))
        
        finally:
            self.flash_btn.config(state='normal')
    
    def run(self):
        """Start GUI"""
        self.root.mainloop()

def main():
    """Main entry point"""
    flasher = UniversalSTM32Flasher()
    
    # Check if file provided as command line argument
    if len(sys.argv) > 1:
        # CLI mode
        firmware_file = sys.argv[1]
        address = sys.argv[2] if len(sys.argv) > 2 else "0x08000000"
        
        flasher.programmer = flasher.find_programmer()
        if not flasher.programmer:
            print("\n[ERROR] STM32CubeProgrammer not found!")
            print("\nPlease install from: https://www.st.com/stm32cubeprog")
            return 1
        
        success, message = flasher.flash_file(firmware_file, address)
        return 0 if success else 1
    else:
        # GUI mode
        gui = FlasherGUI()
        gui.run()
        return 0

if __name__ == "__main__":
    sys.exit(main())
