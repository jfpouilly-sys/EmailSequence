@echo off
REM Email Sequence Automation System - Windows Installation Script
REM Run as Administrator for best results

echo ========================================
echo Email Sequence Installation
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo WARNING: Not running as Administrator
    echo Some features may not work correctly
    echo Right-click this file and select "Run as Administrator"
    echo.
    pause
)

echo Step 1: Checking Python installation...
python --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python --version
echo Python found!
echo.

echo Step 2: Checking pip...
pip --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ERROR: pip is not available
    echo Please reinstall Python with pip enabled
    pause
    exit /b 1
)

pip --version
echo pip found!
echo.

echo Step 3: Installing Python dependencies...
echo This may take a few minutes...
echo.

pip install -r requirements.txt
if %errorLevel% NEQ 0 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

echo Step 4: Configuring pywin32...
python -m pywin32_postinstall -install
if %errorLevel% NEQ 0 (
    echo WARNING: pywin32 post-install may have failed
    echo The system might still work, continuing...
)
echo.

echo Step 5: Initializing system...
python main.py init
if %errorLevel% NEQ 0 (
    echo WARNING: Initialization may have encountered issues
    echo Continuing anyway...
)
echo.

echo Step 6: Creating desktop shortcuts...

REM Create shortcut for GUI application
set SCRIPT_DIR=%~dp0
set SHORTCUT_PATH=%USERPROFILE%\Desktop\Email Sequence.lnk

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = 'pythonw.exe'; $s.Arguments = 'gui_main.py'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = 'shell32.dll,176'; $s.Description = 'Email Sequence Automation'; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo Desktop shortcut created: Email Sequence
) else (
    echo WARNING: Could not create desktop shortcut
)

REM Create shortcut for Configuration Editor
set CONFIG_SHORTCUT=%USERPROFILE%\Desktop\Email Sequence Config.lnk

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%CONFIG_SHORTCUT%'); $s.TargetPath = 'pythonw.exe'; $s.Arguments = 'gui_config.py'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = 'shell32.dll,70'; $s.Description = 'Email Sequence Configuration Editor'; $s.Save()"

if exist "%CONFIG_SHORTCUT%" (
    echo Desktop shortcut created: Email Sequence Config
)

echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit config.yaml to customize settings
echo 2. Add contacts to contacts.xlsx
echo 3. Edit email templates in templates/ folder
echo 4. Run 'Email Sequence' from desktop to start
echo.
echo For detailed instructions, see INSTALL_WINDOWS.md
echo.

echo Press any key to open the GUI application...
pause >nul

REM Launch the GUI
start pythonw gui_main.py

echo.
echo Enjoy!
