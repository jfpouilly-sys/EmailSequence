@echo off
REM ============================================================
REM Lead Generator - Backend Stop Script
REM Stops API and Mail Service processes
REM ============================================================

echo.
echo ============================================================
echo    LEAD GENERATOR - STOPPING BACKEND SERVICES
echo ============================================================
echo.

echo Stopping API Server (port 5000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000 " ^| findstr "LISTENING"') do (
    echo       Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)
echo       [OK] API stopped
echo.

echo Stopping Mail Service...
taskkill /F /IM "LeadGenerator.MailService.exe" >nul 2>&1
echo       [OK] Mail Service stopped
echo.

echo ============================================================
echo    ALL BACKEND SERVICES STOPPED
echo ============================================================
echo.

pause
