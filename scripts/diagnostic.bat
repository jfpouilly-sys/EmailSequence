@echo off
REM ============================================================
REM Lead Generator - System Diagnostic Script
REM Checks all backend components and provides installation help
REM ============================================================
setlocal enabledelayedexpansion

set PASSED=0
set FAILED=0
set WARNINGS=0

echo.
echo ============================================================
echo    LEAD GENERATOR - SYSTEM DIAGNOSTIC
echo    %DATE% %TIME%
echo ============================================================
echo.

REM Configuration - Edit these if needed
set API_URL=http://localhost:5000
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=leadgenerator

echo [CONFIG] API URL: %API_URL%
echo [CONFIG] Database: %DB_HOST%:%DB_PORT%/%DB_NAME%
echo.
echo ============================================================
echo.

REM ============================================================
REM 1. Check API Health
REM ============================================================
echo [1/8] Checking API Server...
curl -s -o nul -w "%%{http_code}" %API_URL%/health > temp_status.txt 2>nul
set /p HTTP_STATUS=<temp_status.txt
del temp_status.txt 2>nul

if "%HTTP_STATUS%"=="200" (
    echo       [PASS] API is running and healthy
    set /a PASSED+=1
) else if "%HTTP_STATUS%"=="" (
    echo       [FAIL] API is not responding - server may not be running
    echo              FIX: Start the API with: dotnet run --project src\LeadGenerator.Api
    set /a FAILED+=1
) else (
    echo       [FAIL] API returned HTTP %HTTP_STATUS%
    echo              FIX: Check API logs at logs\api\api-*.log
    set /a FAILED+=1
)
echo.

REM ============================================================
REM 2. Check API Version Endpoint
REM ============================================================
echo [2/8] Checking API Version...
curl -s %API_URL%/api/version > temp_version.txt 2>nul
findstr /C:"version" temp_version.txt >nul 2>&1
if %ERRORLEVEL%==0 (
    echo       [PASS] API version endpoint responding
    type temp_version.txt
    set /a PASSED+=1
) else (
    echo       [WARN] Could not retrieve API version
    set /a WARNINGS+=1
)
del temp_version.txt 2>nul
echo.

REM ============================================================
REM 3. Check Database Connection (via API)
REM ============================================================
echo [3/8] Checking Database Connection...
curl -s -o nul -w "%%{http_code}" "%API_URL%/api/auth/me" > temp_db.txt 2>nul
set /p DB_STATUS=<temp_db.txt
del temp_db.txt 2>nul

if "%DB_STATUS%"=="401" (
    echo       [PASS] Database connection working (auth endpoint responding)
    set /a PASSED+=1
) else if "%DB_STATUS%"=="200" (
    echo       [PASS] Database connection working
    set /a PASSED+=1
) else if "%DB_STATUS%"=="" (
    echo       [FAIL] Cannot verify database - API not responding
    set /a FAILED+=1
) else (
    echo       [WARN] Database check returned HTTP %DB_STATUS%
    echo              This may indicate database connection issues
    echo              FIX: Check PostgreSQL is running on %DB_HOST%:%DB_PORT%
    echo              FIX: Verify connection string in appsettings.json
    set /a WARNINGS+=1
)
echo.

REM ============================================================
REM 4. Check PostgreSQL Service
REM ============================================================
echo [4/8] Checking PostgreSQL Service...
sc query postgresql-x64-16 >nul 2>&1
if %ERRORLEVEL%==0 (
    sc query postgresql-x64-16 | findstr /C:"RUNNING" >nul 2>&1
    if !ERRORLEVEL!==0 (
        echo       [PASS] PostgreSQL service is running
        set /a PASSED+=1
    ) else (
        echo       [FAIL] PostgreSQL service exists but is not running
        echo              FIX: net start postgresql-x64-16
        set /a FAILED+=1
    )
) else (
    sc query postgresql-x64-15 >nul 2>&1
    if !ERRORLEVEL!==0 (
        echo       [PASS] PostgreSQL 15 service found
        set /a PASSED+=1
    ) else (
        sc query postgresql-x64-14 >nul 2>&1
        if !ERRORLEVEL!==0 (
            echo       [PASS] PostgreSQL 14 service found
            set /a PASSED+=1
        ) else (
            echo       [WARN] PostgreSQL Windows service not found
            echo              This is OK if PostgreSQL runs differently on your system
            set /a WARNINGS+=1
        )
    )
)
echo.

REM ============================================================
REM 5. Check Mail Service
REM ============================================================
echo [5/8] Checking Mail Service...
sc query "Lead Generator Mail Service" >nul 2>&1
if %ERRORLEVEL%==0 (
    sc query "Lead Generator Mail Service" | findstr /C:"RUNNING" >nul 2>&1
    if !ERRORLEVEL!==0 (
        echo       [PASS] Mail Service is running
        set /a PASSED+=1
    ) else (
        echo       [WARN] Mail Service exists but is not running
        echo              FIX: net start "Lead Generator Mail Service"
        echo              Or run manually: dotnet run --project src\LeadGenerator.MailService
        set /a WARNINGS+=1
    )
) else (
    echo       [INFO] Mail Service not installed as Windows service
    echo              This is normal for development
    echo              To run manually: dotnet run --project src\LeadGenerator.MailService
    set /a WARNINGS+=1
)
echo.

REM ============================================================
REM 6. Check Log Directories
REM ============================================================
echo [6/8] Checking Log Directories...
set LOG_OK=1

if exist "logs\api" (
    echo       [PASS] API log directory exists: logs\api
) else (
    echo       [INFO] API log directory will be created on first run
    set LOG_OK=0
)

if exist "logs\mailservice" (
    echo       [PASS] Mail Service log directory exists: logs\mailservice
) else (
    echo       [INFO] Mail Service log directory will be created on first run
    set LOG_OK=0
)

if exist "client\logs\gui" (
    echo       [PASS] GUI log directory exists: client\logs\gui
) else (
    echo       [INFO] GUI log directory will be created on first run
    set LOG_OK=0
)

if %LOG_OK%==1 (
    set /a PASSED+=1
) else (
    set /a WARNINGS+=1
)
echo.

REM ============================================================
REM 7. Check File Storage Directory
REM ============================================================
echo [7/8] Checking File Storage...
if exist "C:\LeadGenerator\Files" (
    echo       [PASS] File storage directory exists: C:\LeadGenerator\Files
    set /a PASSED+=1
) else (
    echo       [WARN] File storage directory not found: C:\LeadGenerator\Files
    echo              FIX: mkdir C:\LeadGenerator\Files
    echo              Or update FileStorage:BasePath in appsettings.json
    set /a WARNINGS+=1
)
echo.

REM ============================================================
REM 8. Check Required Ports
REM ============================================================
echo [8/8] Checking Network Ports...
netstat -an | findstr ":5000 " | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo       [PASS] Port 5000 (API) is listening
    set /a PASSED+=1
) else (
    echo       [WARN] Port 5000 (API) is not listening
    echo              FIX: Start the API server
    set /a WARNINGS+=1
)

netstat -an | findstr ":5432 " | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo       [PASS] Port 5432 (PostgreSQL) is listening
    set /a PASSED+=1
) else (
    echo       [FAIL] Port 5432 (PostgreSQL) is not listening
    echo              FIX: Start PostgreSQL service
    set /a FAILED+=1
)
echo.

REM ============================================================
REM Summary
REM ============================================================
echo ============================================================
echo    DIAGNOSTIC SUMMARY
echo ============================================================
echo.
echo    Passed:   %PASSED%
echo    Warnings: %WARNINGS%
echo    Failed:   %FAILED%
echo.

if %FAILED%==0 (
    if %WARNINGS%==0 (
        echo    STATUS: ALL SYSTEMS OPERATIONAL
        echo.
        echo    The Lead Generator backend is fully operational.
        echo    You can now start the GUI client.
    ) else (
        echo    STATUS: SYSTEM OPERATIONAL WITH WARNINGS
        echo.
        echo    The system should work but review the warnings above.
    )
) else (
    echo    STATUS: SYSTEM HAS ISSUES
    echo.
    echo    Please fix the failed items above before using the system.
    echo.
    echo    COMMON FIXES:
    echo    -------------
    echo    1. Start PostgreSQL: net start postgresql-x64-16
    echo    2. Start API: cd src\LeadGenerator.Api ^&^& dotnet run
    echo    3. Initialize DB: psql -f scripts\database\001_create_tables.sql
    echo    4. Seed admin user: psql -f scripts\database\003_seed_admin_user.sql
)

echo.
echo ============================================================
echo    QUICK START COMMANDS
echo ============================================================
echo.
echo    Start API:
echo      dotnet run --project src\LeadGenerator.Api
echo.
echo    Start Mail Service:
echo      dotnet run --project src\LeadGenerator.MailService
echo.
echo    Start GUI Client:
echo      cd client ^&^& python main.py
echo.
echo    Default Login:
echo      Username: admin
echo      Password: Admin123!
echo.
echo ============================================================
echo.

pause
exit /b %FAILED%
