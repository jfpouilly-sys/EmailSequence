@echo off
REM Lead Generator Standalone - Installation Script

echo ================================
echo Lead Generator Standalone - Install
echo ================================
echo.

set INSTALL_DIR=C:\LeadGenerator

REM Check for admin rights
net session >nul 2>&1
if errorlevel 1 (
    echo This script requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Check if executable exists
if not exist "%~dp0\..\dist\LeadGeneratorStandalone.exe" (
    echo Error: Executable not found.
    echo Please run build.bat first.
    pause
    exit /b 1
)

echo Installing to %INSTALL_DIR%...
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\data" mkdir "%INSTALL_DIR%\data"
if not exist "%INSTALL_DIR%\data\files" mkdir "%INSTALL_DIR%\data\files"
if not exist "%INSTALL_DIR%\assets" mkdir "%INSTALL_DIR%\assets"

REM Copy files
echo Copying files...
copy /Y "%~dp0\..\dist\LeadGeneratorStandalone.exe" "%INSTALL_DIR%\"
copy /Y "%~dp0\..\config.yaml" "%INSTALL_DIR%\"
xcopy /Y /E "%~dp0\..\assets\*" "%INSTALL_DIR%\assets\" 2>nul

REM Create desktop shortcut
echo Creating desktop shortcut...
set SHORTCUT_FILE=%USERPROFILE%\Desktop\Lead Generator.lnk
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_FILE%'); $s.TargetPath = '%INSTALL_DIR%\LeadGeneratorStandalone.exe'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.IconLocation = '%INSTALL_DIR%\assets\icon.ico'; $s.Save()"

echo.
echo ================================
echo Installation complete!
echo.
echo Application installed to: %INSTALL_DIR%
echo Desktop shortcut created.
echo.
echo You can now run Lead Generator from:
echo   - Desktop shortcut
echo   - %INSTALL_DIR%\LeadGeneratorStandalone.exe
echo ================================
echo.
pause
