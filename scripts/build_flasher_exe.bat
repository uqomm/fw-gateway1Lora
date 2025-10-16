@echo off
REM Build STM32 Gateway Flasher EXE
REM This creates a standalone executable that includes Python runtime

echo ========================================
echo Building STM32 Gateway Flasher EXE
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.6 or later from https://python.org
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version

REM Check if pyinstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo.
    echo [2/4] Installing PyInstaller...
    pip install pyinstaller
) else (
    echo.
    echo [2/4] PyInstaller already installed
)

echo.
echo [3/4] Building executable...
echo.

REM Build the EXE
pyinstaller --onefile ^
    --name "STM32_Gateway_Flasher" ^
    --console ^
    --clean ^
    flash_gateway.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [4/4] Copying executable...

REM Copy to scripts folder for easy access
if exist "dist\STM32_Gateway_Flasher.exe" (
    copy "dist\STM32_Gateway_Flasher.exe" "STM32_Gateway_Flasher.exe"
    echo.
    echo ========================================
    echo   BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created: STM32_Gateway_Flasher.exe
    echo Size: 
    dir "STM32_Gateway_Flasher.exe" | find "STM32_Gateway_Flasher.exe"
    echo.
    echo You can now distribute this single EXE file to your team.
    echo No Python installation required on target machines!
    echo.
) else (
    echo [ERROR] Executable not found in dist folder
    pause
    exit /b 1
)

REM Clean up build artifacts (optional)
echo Cleaning up build artifacts...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del STM32_Gateway_Flasher.spec 2>nul

echo.
echo Done! Share STM32_Gateway_Flasher.exe with your engineering team.
echo.
pause
