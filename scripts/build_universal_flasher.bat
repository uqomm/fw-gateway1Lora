@echo off
REM Build Universal STM32 Flasher EXE
REM Creates a standalone GUI application for flashing any STM32 device

echo ========================================
echo Building Universal STM32 Flasher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.6+ from https://python.org
    pause
    exit /b 1
)

echo [1/4] Checking Python...
python --version

REM Install PyInstaller if needed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo.
    echo [2/4] Installing PyInstaller...
    pip install pyinstaller
) else (
    echo.
    echo [2/4] PyInstaller found
)

echo.
echo [3/4] Building executable with GUI...
echo.

REM Build the EXE with GUI support
pyinstaller --onefile ^
    --windowed ^
    --name "STM32_Universal_Flasher" ^
    --icon=NONE ^
    --clean ^
    --add-data "README.txt;." ^
    universal_stm32_flasher.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [4/4] Finalizing...

if exist "dist\STM32_Universal_Flasher.exe" (
    copy "dist\STM32_Universal_Flasher.exe" "STM32_Universal_Flasher.exe" >nul
    
    echo.
    echo ========================================
    echo   BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Created: STM32_Universal_Flasher.exe
    dir "STM32_Universal_Flasher.exe" | find "STM32_Universal_Flasher.exe"
    echo.
    echo Features:
    echo   - GUI for easy use
    echo   - Supports BIN, HEX, and ELF files
    echo   - Works with any STM32 device
    echo   - No Python required on target PC
    echo.
    echo Requirements on target PC:
    echo   - STM32CubeProgrammer installed
    echo   - ST-Link drivers
    echo.
) else (
    echo [ERROR] Build failed - executable not found
    pause
    exit /b 1
)

REM Clean up
echo Cleaning build artifacts...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del STM32_Universal_Flasher.spec 2>nul

echo.
echo Distribution package:
echo   STM32_Universal_Flasher.exe  ← Share this!
echo.
pause
