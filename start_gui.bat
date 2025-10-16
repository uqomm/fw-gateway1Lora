@echo off
echo ================================
echo LoRa Gateway Configuration Tool
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later
    pause
    exit /b 1
)

echo Python found. Checking dependencies...

REM Install dependencies if needed
pip show pyserial >nul 2>&1
if errorlevel 1 (
    echo Installing pyserial...
    pip install pyserial
)

pip show crccheck >nul 2>&1
if errorlevel 1 (
    echo Installing crccheck...
    pip install crccheck
)

echo.
echo Starting LoRa Gateway Configuration Tool...
echo.

REM Run the application
python lora_gui_config.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo Check the error messages above
    pause
)