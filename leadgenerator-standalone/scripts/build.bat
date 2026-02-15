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

REM Build PyInstaller command with conditional assets
set PYINSTALLER_ARGS=--name "LeadGeneratorStandalone" --onefile --windowed
set PYINSTALLER_ARGS=%PYINSTALLER_ARGS% --add-data "config.yaml;."
set PYINSTALLER_ARGS=%PYINSTALLER_ARGS% --hidden-import=win32com.client
set PYINSTALLER_ARGS=%PYINSTALLER_ARGS% --hidden-import=win32timezone
set PYINSTALLER_ARGS=%PYINSTALLER_ARGS% --hidden-import=ttkbootstrap
set PYINSTALLER_ARGS=%PYINSTALLER_ARGS% --hidden-import=PIL
set PYINSTALLER_ARGS=%PYINSTALLER_ARGS% --hidden-import=pandas
set PYINSTALLER_ARGS=%PYINSTALLER_ARGS% --hidden-import=matplotlib

if exist "assets\icon.ico" (
    set PYINSTALLER_ARGS=%PYINSTALLER_ARGS% --icon=assets/icon.ico
) else (
    echo Warning: assets\icon.ico not found, building without icon
)

if exist "assets" (
    set PYINSTALLER_ARGS=%PYINSTALLER_ARGS% --add-data "assets;assets"
) else (
    echo Warning: assets directory not found, skipping asset bundling
)

REM Run PyInstaller
echo Building executable...
pyinstaller %PYINSTALLER_ARGS% main.py

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
