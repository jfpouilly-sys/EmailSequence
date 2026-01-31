@echo off
REM ============================================================================
REM Lead Generator Build System Launcher
REM Version: 260128-2
REM ============================================================================

setlocal enabledelayedexpansion

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: PowerShell is not installed or not in PATH
    exit /b 1
)

REM Get the target from command line (default: help)
set TARGET=%1
if "%TARGET%"=="" set TARGET=help

REM Additional parameters
set CONFIG=%2
if "%CONFIG%"=="" set CONFIG=Release

REM Run the PowerShell build script
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║      Lead Generator Build System (Batch Launcher)     ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Executing target: %TARGET%
echo Configuration: %CONFIG%
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0build.ps1" -Target %TARGET% -Configuration %CONFIG%

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% equ 0 (
    echo.
    echo [SUCCESS] Build completed successfully!
) else (
    echo.
    echo [FAILED] Build failed with exit code: %EXIT_CODE%
)

exit /b %EXIT_CODE%
