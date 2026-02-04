#!/usr/bin/env python3
"""
Lead Generator Launcher
Double-click this file to run the application (no console window).
"""
import sys
import os

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add to path and run main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main
main()
