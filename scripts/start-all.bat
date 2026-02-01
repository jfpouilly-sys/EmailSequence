@echo off
REM ============================================================
REM Lead Generator - Start All Components
REM Starts API, Mail Service, and GUI Client
REM ============================================================

echo.
echo ============================================================
echo    LEAD GENERATOR - FULL SYSTEM STARTUP
echo ============================================================
echo.

cd /d "%~dp0"

REM Start backend first
call start-backend.bat

REM Ask to start GUI
echo.
choice /C YN /M "Start GUI Client?"
if errorlevel 2 (
    echo [SKIP] GUI not started
    goto :end
)

echo.
echo Starting GUI Client...
cd /d "%~dp0\..\client"
start "Lead Generator GUI" pythonw main.py
echo [OK] GUI Client starting...

:end
echo.
echo ============================================================
echo    ALL COMPONENTS STARTED
echo ============================================================
echo.
pause
