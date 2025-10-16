@echo off
REM =========================================================================
REM STM32 Gateway Flasher
REM Flashes gateway-2lora firmware to STM32G474 via ST-Link
REM =========================================================================

title STM32 Gateway Flasher

echo.
echo ========================================
echo   STM32 Gateway Firmware Flasher
echo ========================================
echo.

REM Define paths
set "PROGRAMMER=C:\ST\STM32CubeIDE_1.11.0\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.win32_2.2.200.202503041107\tools\bin\STM32_Programmer_CLI.exe"
set "SCRIPT_DIR=%~dp0"
set "BIN_FILE=%SCRIPT_DIR%..\projects\gateway-2lora\Debug\gateway-2lora.bin"

REM Check if programmer exists
if not exist "%PROGRAMMER%" (
    echo [ERROR] STM32CubeProgrammer not found!
    echo Expected location: %PROGRAMMER%
    echo.
    echo Please install STM32CubeIDE or STM32CubeProgrammer
    echo.
    pause
    exit /b 1
)

REM Check if binary file exists
if not exist "%BIN_FILE%" (
    echo [ERROR] Firmware binary not found!
    echo Expected location: %BIN_FILE%
    echo.
    echo Please build the project first.
    echo.
    pause
    exit /b 1
)

echo [INFO] Programmer: Found
echo [INFO] Firmware:   %BIN_FILE%
echo.

REM Get file size
for %%A in ("%BIN_FILE%") do set SIZE=%%~zA
set /a SIZE_KB=%SIZE%/1024
echo [INFO] Firmware size: %SIZE_KB% KB
echo.

echo [STEP 1/3] Connecting to ST-Link...
echo.

REM Mass erase first
"%PROGRAMMER%" -c port=SWD mode=UR reset=HWrst -e all
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to erase flash memory!
    echo Please check:
    echo   - ST-Link is connected
    echo   - Target board has power
    echo   - No other tools are using ST-Link
    echo.
    pause
    exit /b 1
)

echo.
echo [STEP 2/3] Programming flash memory...
echo.

REM Program the flash
"%PROGRAMMER%" -c port=SWD mode=UR reset=HWrst -w "%BIN_FILE%" 0x08000000 -v -rst
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to program flash memory!
    echo.
    pause
    exit /b 1
)

echo.
echo [STEP 3/3] Verifying...
echo.
echo ========================================
echo   PROGRAMMING SUCCESSFUL!
echo ========================================
echo.
echo The device will now reset and start running.
echo.
echo FSK Scanner features:
echo   - Auto-starts at 175 MHz on boot
echo   - Scans 9,600 parameter combinations
echo   - Auto-saves detected configurations
echo   - Estimated scan time: ~2.7 hours
echo.
echo Next steps:
echo   1. Open serial terminal at 115200 baud
echo   2. Press Becker remote every 30-60 seconds
echo   3. Wait for detection message
echo.
pause
