@echo off
REM ============================================================
REM Lead Generator - Backend Startup Script
REM Starts API and Mail Service (PostgreSQL should already be running)
REM ============================================================
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo    LEAD GENERATOR - BACKEND STARTUP
echo    %DATE% %TIME%
echo ============================================================
echo.

cd /d "%~dp0\.."

REM ============================================================
REM Check Prerequisites
REM ============================================================
echo [1/3] Checking prerequisites...

REM Check if dotnet is available
dotnet --version >nul 2>&1
if errorlevel 1 (
    echo       [ERROR] .NET SDK not found!
    echo       Please install .NET 8 SDK from: https://dotnet.microsoft.com/download
    pause
    exit /b 1
)
echo       [OK] .NET SDK found

REM Check if PostgreSQL is running
netstat -an | findstr ":5432 " | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo       [WARN] PostgreSQL does not appear to be running on port 5432
    echo       The API will fail to start without a database connection.
    echo.
    choice /C YN /M "Continue anyway?"
    if errorlevel 2 exit /b 1
) else (
    echo       [OK] PostgreSQL is running
)
echo.

REM ============================================================
REM Start API Server
REM ============================================================
echo [2/3] Starting API Server...
echo       URL: http://localhost:5000
echo       Swagger: http://localhost:5000/swagger
echo.

start "Lead Generator API" cmd /k "cd /d "%~dp0\..\src\LeadGenerator.Api" && dotnet run"

REM Wait for API to start
echo       Waiting for API to start...
timeout /t 5 /nobreak >nul

REM Verify API is running
curl -s -o nul -w "%%{http_code}" http://localhost:5000/health > temp_check.txt 2>nul
set /p API_STATUS=<temp_check.txt
del temp_check.txt 2>nul

if "%API_STATUS%"=="200" (
    echo       [OK] API started successfully
) else (
    echo       [WAIT] API still starting... check the API window for status
)
echo.

REM ============================================================
REM Start Mail Service (Optional)
REM ============================================================
echo [3/3] Mail Service...
choice /C YN /M "Start Mail Service?"
if errorlevel 2 (
    echo       [SKIP] Mail Service not started
    goto :summary
)

echo       Starting Mail Service...
start "Lead Generator Mail Service" cmd /k "cd /d "%~dp0\..\src\LeadGenerator.MailService" && dotnet run"
echo       [OK] Mail Service starting...
echo.

:summary
REM ============================================================
REM Summary
REM ============================================================
echo.
echo ============================================================
echo    STARTUP COMPLETE
echo ============================================================
echo.
echo    Services Started:
echo    -----------------
echo    API Server:    http://localhost:5000
echo    Swagger UI:    http://localhost:5000/swagger
echo    Health Check:  http://localhost:5000/health
echo.
echo    Log Files:
echo    ----------
echo    API Logs:      logs\api\api-*.log
echo    Mail Logs:     logs\mailservice\mailservice-*.log
echo.
echo    To stop services, close the respective command windows.
echo.
echo    Default Login:
echo    --------------
echo    Username: admin
echo    Password: Admin123!
echo.
echo ============================================================
echo.

pause
