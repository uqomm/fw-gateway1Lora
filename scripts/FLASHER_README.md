# STM32 Gateway Flasher - Engineering Team Guide

## 📦 What You Need

### Option 1: Standalone STM32CubeProgrammer (Recommended)
- **Download**: [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html)
- **Size**: ~400 MB
- **Install to**: `C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\`
- **Advantage**: Professional tool, GUI available, no dependencies

### Option 2: Use Bundled OpenOCD (Already Included)
- **Location**: `tools/bin/openocd.exe` (already in this repo)
- **Size**: ~10 MB
- **Advantage**: No installation needed, portable
- **Note**: Already configured for STM32G474

### Option 3: Extract Portable Tools
If you can't install software:
1. Download STM32CubeProgrammer (see Option 1)
2. Extract only `STM32_Programmer_CLI.exe` and its DLLs
3. Copy to `scripts/tools/` folder
4. Portable and shareable!

---

## 🚀 Quick Start (3 Steps)

### Step 1: Connect Hardware
```
ST-Link V3 → STM32G474 Board
  SWDIO   →   SWDIO
  SWCLK   →   SWCLK
  GND     →   GND
  3.3V    →   3.3V (optional, if board has no power)
```

### Step 2: Run Flasher
**Windows:**
```
Double-click: scripts\flash_gateway_portable.bat
```

**Or from command line:**
```cmd
cd scripts
flash_gateway_portable.bat
```

### Step 3: Verify
Open serial terminal:
- **Port**: COM? (check Device Manager)
- **Baud**: 115200
- **Settings**: 8N1

You should see:
```
[INFO ] Auto-starting FSK Scanner at 175 MHz...
[INFO ] FSK Scanner started! (Default timeout: 1000ms = ~2.7 hours total)
```

---

## 📋 Tool Priority (Automatic Detection)

The flasher automatically searches in this order:

1. ✅ **Bundled tools** (`scripts/tools/STM32_Programmer_CLI.exe`)
2. ✅ **Standalone STM32CubeProgrammer** (`C:\Program Files\STMicroelectronics\...`)
3. ✅ **STM32CubeIDE** (`C:\ST\STM32CubeIDE_*\...`)
4. ✅ **OpenOCD** (`tools/bin/openocd.exe`) ← Already in repo!

---

## 🎯 For Engineering Team Distribution

### Package for Team (No Installation Required)

Create a folder with:
```
STM32_Gateway_Flasher/
├── flash_gateway.exe           ← (Batch to EXE conversion)
├── gateway-2lora.bin           ← (Firmware binary)
├── tools/
│   ├── STM32_Programmer_CLI.exe
│   ├── *.dll (all required DLLs)
│   └── api/ (folder with libraries)
└── README.txt
```

**To create portable tools folder:**

1. Install STM32CubeProgrammer on your machine
2. Copy from: `C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\`
3. Copy these files:
   ```
   STM32_Programmer_CLI.exe
   STM32CubeProgrammerLauncher.exe (optional)
   libCrypto-1_1-x64.dll
   libssl-1_1-x64.dll
   libusb-1.0.dll
   STLinkUSBDriver.dll
   api/ (entire folder)
   ```
4. Put in `scripts/tools/` folder

---

## 🔧 Alternative: Use OpenOCD (Already Included!)

Your repo already has OpenOCD in `tools/bin/openocd.exe`!

The portable flasher will automatically use it if STM32CubeProgrammer is not found.

**Manual flash with OpenOCD:**
```bash
cd tools/bin
./openocd.exe -s ../share/openocd/scripts \
  -f interface/stlink.cfg \
  -f target/stm32g4x.cfg \
  -c "program ../../projects/gateway-2lora/Debug/gateway-2lora.bin verify reset exit 0x08000000"
```

---

## 🎭 Convert Batch to EXE (Optional)

To create a standalone `.exe` file:

### Method 1: Bat to Exe Converter
1. Download: [Bat To Exe Converter](http://www.f2ko.de/en/b2e.php)
2. Open `flash_gateway_portable.bat`
3. Set icon (optional)
4. Click "Compile"
5. Output: `flash_gateway_portable.exe`

### Method 2: PS2EXE (PowerShell)
```powershell
Install-Module ps2exe
Invoke-ps2exe .\flash_gateway.ps1 .\flash_gateway.exe
```

### Method 3: IExpress (Built into Windows)
1. Run `iexpress.exe` (built into Windows)
2. Create self-extracting package
3. Include batch file + firmware

---

## 📊 Firmware Information

| Property | Value |
|----------|-------|
| **Target** | STM32G474CBTx |
| **Flash Size** | 128 KB |
| **Firmware Size** | ~70 KB (54% usage) |
| **RAM Usage** | ~6 KB |
| **Flash Address** | 0x08000000 |

### Features
- ✅ Auto-start FSK scanner on boot
- ✅ Fixed frequency: 175 MHz (Becker Varis)
- ✅ 9,600 parameter combinations
- ✅ Auto-save to EEPROM on detection
- ✅ Estimated scan time: 2.7 hours (default)

---

## 🐛 Troubleshooting

### "STM32 Programmer not found"
**Solution:**
- Install STM32CubeProgrammer (Option 1 above)
- OR use OpenOCD (already in repo)

### "Failed to connect to ST-Link"
**Check:**
- ✅ ST-Link USB cable connected
- ✅ Target board powered (3.3V)
- ✅ SWDIO/SWCLK wires connected
- ✅ No other tools using ST-Link (close STM32CubeIDE)

### "Device not found"
**Fix:**
1. Disconnect ST-Link USB
2. Close all ST-Link tools
3. Reconnect ST-Link
4. Try again

### "Dual-bank error" (should be fixed already)
If you see "Operation exceeds memory limits":
```cmd
# Disable dual-bank mode (one-time fix)
STM32_Programmer_CLI.exe -c port=SWD -ob DBANK=0
```

---

## 📞 Support

**Questions?**
- Check logs in serial terminal (115200 baud)
- Verify ST-Link drivers installed
- Ensure target board is STM32G474CBTx

**Success indicator:**
```
[INFO ] === FSK Scanner Initialization ===
[INFO ] Scan Frequency: 175.000 MHz (FIXED - no frequency sweep)
[INFO ] Total parameter combinations: 9600
[INFO ] >>> STARTING FSK SCAN <<<
```

---

## 📝 Download Links

| Tool | Link | Size |
|------|------|------|
| **STM32CubeProgrammer** | https://www.st.com/stm32cubeprog | 400 MB |
| **ST-Link Driver** | https://www.st.com/en/development-tools/stsw-link009.html | 5 MB |
| **Bat to Exe Converter** | http://www.f2ko.de/en/b2e.php | 2 MB |

---

**Created**: October 14, 2025  
**Firmware**: gateway-2lora v2.x  
**Target**: STM32G474CBTx with FSK Scanner
