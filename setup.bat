@echo off
REM ============================================================================
REM Lead Generator - First Time Setup (Batch Launcher)
REM This script unblocks PowerShell files so they can run without errors
REM ============================================================================

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║       Lead Generator - First Time Setup               ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo This will unblock all PowerShell scripts in this project.
echo.

REM Check for PowerShell
where powershell >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] PowerShell is not installed or not in PATH
    echo Please install PowerShell and try again.
    pause
    exit /b 1
)

echo Running setup script...
echo.

REM Run setup.ps1 with execution policy bypass
powershell -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% equ 0 (
    echo.
    echo ════════════════════════════════════════════════════════
    echo  Setup completed successfully!
    echo ════════════════════════════════════════════════════════
    echo.
    echo You can now run:
    echo   - make help
    echo   - make build
    echo   - make install-all
    echo.
) else (
    echo.
    echo ════════════════════════════════════════════════════════
    echo  Setup failed!
    echo ════════════════════════════════════════════════════════
    echo.
    echo Please check the error messages above.
    echo See EXECUTION_POLICY.md for troubleshooting.
    echo.
)

pause
exit /b %EXIT_CODE%
