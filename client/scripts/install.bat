@echo off
REM Lead Generator - Installation Script
REM Installs the application for the current user

echo ========================================
echo Lead Generator - Installation Script
echo ========================================
echo.

set INSTALL_DIR=%LOCALAPPDATA%\LeadGenerator
set DESKTOP=%USERPROFILE%\Desktop

REM Check if executable exists
if not exist "..\dist\LeadGenerator.exe" (
    echo Error: LeadGenerator.exe not found!
    echo Please run build.bat first.
    exit /b 1
)

REM Create installation directory
echo Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
echo Copying files...
copy /y "..\dist\LeadGenerator.exe" "%INSTALL_DIR%\"
copy /y "..\config.yaml" "%INSTALL_DIR%\"

REM Copy assets if they exist
if exist "..\assets" (
    if not exist "%INSTALL_DIR%\assets" mkdir "%INSTALL_DIR%\assets"
    xcopy /y /e "..\assets\*" "%INSTALL_DIR%\assets\"
)

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Lead Generator.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\LeadGenerator.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Lead Generator - Digital Marketing Campaign Tool'; $Shortcut.Save()"

REM Create Start Menu shortcut
set STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
echo Creating Start Menu shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU%\Lead Generator.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\LeadGenerator.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Lead Generator - Digital Marketing Campaign Tool'; $Shortcut.Save()"

echo.
echo ========================================
echo Installation completed successfully!
echo.
echo Location: %INSTALL_DIR%
echo Desktop shortcut: %DESKTOP%\Lead Generator.lnk
echo.
echo You can now launch Lead Generator from your desktop!
echo ========================================

pause
