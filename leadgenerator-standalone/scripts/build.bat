@echo off
REM Lead Generator Standalone - Build Script
REM Creates a standalone executable using PyInstaller

echo ================================
echo Lead Generator Standalone - Build
echo ================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Navigate to project root
cd /d "%~dp0\.."

REM Clean previous builds
echo Cleaning previous builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

REM Run PyInstaller
echo Building executable...
pyinstaller ^
    --name "LeadGeneratorStandalone" ^
    --onefile ^
    --windowed ^
    --icon=assets/icon.ico ^
    --add-data "config.yaml;." ^
    --add-data "assets;assets" ^
    --hidden-import=win32com.client ^
    --hidden-import=win32timezone ^
    --hidden-import=ttkbootstrap ^
    --hidden-import=PIL ^
    --hidden-import=pandas ^
    --hidden-import=matplotlib ^
    main.py

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ================================
echo Build complete!
echo Executable: dist\LeadGeneratorStandalone.exe
echo ================================
echo.
pause
