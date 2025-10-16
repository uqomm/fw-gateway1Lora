@echo off
REM =========================================================================
REM STM32 Gateway Flasher (Portable - No STM32CubeIDE required)
REM Flashes gateway-2lora firmware to STM32G474 via ST-Link
REM =========================================================================

title STM32 Gateway Flasher (Portable)

echo.
echo ========================================
echo   STM32 Gateway Firmware Flasher
echo   Portable Version
echo ========================================
echo.

REM Define paths - Try multiple common locations
set "PROGRAMMER="
set "SCRIPT_DIR=%~dp0"
set "BIN_FILE=%SCRIPT_DIR%..\projects\gateway-2lora\Debug\gateway-2lora.bin"

REM Check 1: Bundled tools in scripts folder
if exist "%SCRIPT_DIR%tools\STM32_Programmer_CLI.exe" (
    set "PROGRAMMER=%SCRIPT_DIR%tools\STM32_Programmer_CLI.exe"
    echo [INFO] Using bundled STM32 Programmer
    goto :found_programmer
)

REM Check 2: Standalone STM32CubeProgrammer installation
if exist "C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe" (
    set "PROGRAMMER=C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe"
    echo [INFO] Using STM32CubeProgrammer installation
    goto :found_programmer
)

REM Check 3: STM32CubeIDE installation
if exist "C:\ST\STM32CubeIDE_1.11.0\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.2.200.202503041107\tools\bin\STM32_Programmer_CLI.exe" (
    set "PROGRAMMER=C:\ST\STM32CubeIDE_1.11.0\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.2.200.202503041107\tools\bin\STM32_Programmer_CLI.exe"
    echo [INFO] Using STM32CubeIDE installation
    goto :found_programmer
)

REM Check 4: OpenOCD (alternative flasher)
if exist "%SCRIPT_DIR%..\tools\bin\openocd.exe" (
    echo [INFO] STM32CubeProgrammer not found, using OpenOCD instead
    goto :use_openocd
)

REM Not found anywhere
echo [ERROR] STM32 Programmer not found!
echo.
echo Please install one of:
echo   1. STM32CubeProgrammer (standalone, ~400MB)
echo      Download: https://www.st.com/en/development-tools/stm32cubeprog.html
echo.
echo   2. OR extract STM32_Programmer_CLI.exe to: %SCRIPT_DIR%tools\
echo.
pause
exit /b 1

:found_programmer
REM Check if binary file exists
if not exist "%BIN_FILE%" (
    echo [ERROR] Firmware binary not found!
    echo Expected location: %BIN_FILE%
    echo.
    pause
    exit /b 1
)

echo [INFO] Firmware: %BIN_FILE%
for %%A in ("%BIN_FILE%") do set SIZE=%%~zA
set /a SIZE_KB=%SIZE%/1024
echo [INFO] Size: %SIZE_KB% KB
echo.

echo [STEP 1/3] Connecting to ST-Link...
"%PROGRAMMER%" -c port=SWD mode=UR reset=HWrst -e all
if errorlevel 1 goto :flash_error

echo.
echo [STEP 2/3] Programming flash...
"%PROGRAMMER%" -c port=SWD mode=UR reset=HWrst -w "%BIN_FILE%" 0x08000000 -v -rst
if errorlevel 1 goto :flash_error

goto :success

:use_openocd
REM Alternative: Use OpenOCD
set "OPENOCD=%SCRIPT_DIR%..\tools\bin\openocd.exe"
set "OPENOCD_SCRIPTS=%SCRIPT_DIR%..\tools\share\openocd\scripts"

if not exist "%BIN_FILE%" (
    echo [ERROR] Firmware binary not found: %BIN_FILE%
    pause
    exit /b 1
)

echo [INFO] Using OpenOCD flasher
echo [INFO] Firmware: %BIN_FILE%
echo.

echo [STEP 1/2] Connecting and erasing...
"%OPENOCD%" -s "%OPENOCD_SCRIPTS%" -f interface/stlink.cfg -f target/stm32g4x.cfg -c "init" -c "reset halt" -c "flash erase_sector 0 0 last" -c "exit"
if errorlevel 1 goto :flash_error

echo.
echo [STEP 2/2] Programming flash...
"%OPENOCD%" -s "%OPENOCD_SCRIPTS%" -f interface/stlink.cfg -f target/stm32g4x.cfg -c "program %BIN_FILE% verify reset exit 0x08000000"
if errorlevel 1 goto :flash_error

goto :success

:flash_error
echo.
echo [ERROR] Flash programming failed!
echo.
echo Troubleshooting:
echo   - Ensure ST-Link is connected
echo   - Check target board has power (3.3V)
echo   - Close other tools using ST-Link
echo   - Try disconnecting and reconnecting ST-Link
echo.
pause
exit /b 1

:success
echo.
echo ========================================
echo   PROGRAMMING SUCCESSFUL!
echo ========================================
echo.
echo Device is now running FSK Scanner firmware.
echo.
echo Features:
echo   - Auto-starts scanning at 175 MHz
echo   - Tests 9,600 parameter combinations
echo   - Auto-saves detected configurations
echo.
echo Usage:
echo   1. Connect serial monitor (115200 baud)
echo   2. Press Becker remote every 30-60 seconds
echo   3. Wait for "SIGNAL DETECTED" message
echo.
pause
exit /b 0
