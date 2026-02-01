@echo off
REM Lead Generator - Python Tkinter Client Launcher
REM Double-click this file to run the application

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import ttkbootstrap" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run the application
python main.py

REM Keep window open if there's an error
if errorlevel 1 pause
