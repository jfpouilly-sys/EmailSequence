@echo off
REM Build wrapper for Lead Generator
REM Usage: build.bat [target]
REM Targets: install, build, clean

setlocal enabledelayedexpansion

set TARGET=%1
if "%TARGET%"=="" set TARGET=build

echo ========================================
echo Lead Generator Build Script
echo Target: %TARGET%
echo ========================================
echo.

cd /d "%~dp0"

if "%TARGET%"=="install" goto :install
if "%TARGET%"=="build" goto :build
if "%TARGET%"=="clean" goto :clean
if "%TARGET%"=="run" goto :run

echo Unknown target: %TARGET%
echo Available targets: install, build, clean, run
exit /b 1

:install
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    exit /b 1
)
echo Dependencies installed successfully!
goto :end

:build
echo Building executable with PyInstaller...

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Run PyInstaller
pyinstaller --noconfirm --onedir --windowed ^
    --name "LeadGenerator" ^
    --add-data "config.yaml;." ^
    --hidden-import "ttkbootstrap" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL._tkinter_finder" ^
    main.py

if errorlevel 1 (
    echo Build failed!
    exit /b 1
)

echo.
echo ========================================
echo Build successful!
echo Output: dist\LeadGenerator\LeadGenerator.exe
echo ========================================
goto :end

:clean
echo Cleaning build artifacts...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec
echo Clean complete!
goto :end

:run
echo Starting Lead Generator...
python main.py
goto :end

:end
echo.
pause
