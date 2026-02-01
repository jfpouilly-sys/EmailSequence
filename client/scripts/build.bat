@echo off
REM Lead Generator - PyInstaller Build Script
REM Creates a single .exe file for distribution

echo ========================================
echo Lead Generator - Build Script
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "..\main.py" (
    echo Error: Please run this script from the client\scripts directory
    exit /b 1
)

REM Change to client directory
cd ..

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: No virtual environment found
    echo Consider creating one with: python -m venv venv
)

REM Install/update dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Install PyInstaller if not present
pip install pyinstaller

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Build the executable
echo.
echo Building executable...
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "LeadGenerator" ^
    --icon "assets\icon.ico" ^
    --add-data "config.yaml;." ^
    --add-data "assets;assets" ^
    --hidden-import "ttkbootstrap" ^
    --hidden-import "pandas" ^
    --hidden-import "matplotlib" ^
    --hidden-import "keyring" ^
    main.py

if errorlevel 1 (
    echo.
    echo Build FAILED!
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo Executable: dist\LeadGenerator.exe
echo ========================================

REM Return to scripts directory
cd scripts
