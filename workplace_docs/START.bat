@echo off
title Workplace Documentation Tool
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                              ║
echo  ║     📝  WORKPLACE DOCUMENTATION TOOL                         ║
echo  ║                                                              ║
echo  ║     Document • Analyze • Build Your Case                     ║
echo  ║                                                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ⚠️  Python is not installed!
    echo.
    echo  Please install Python first:
    echo.
    echo  1. Go to: https://www.python.org/downloads/
    echo  2. Download Python 3.10 or newer
    echo  3. Run the installer
    echo  4. ⚠️  IMPORTANT: Check the box "Add Python to PATH"
    echo  5. Click "Install Now"
    echo  6. Restart your computer
    echo  7. Double-click this file again
    echo.
    pause
    exit /b 1
)

echo  ✓ Python found
echo.

REM Check if Copilot CLI is available (for AI features)
copilot --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ⚠️  Copilot CLI not found - AI features will be limited
    echo     To enable AI: Run "winget install GitHub.Copilot" then "copilot auth login"
    echo.
) else (
    echo  ✓ Copilot CLI found - AI features enabled
    echo.
)

REM Install required packages if needed
echo  Checking dependencies...
pip show github-copilot-sdk >nul 2>&1
if %errorlevel% neq 0 (
    echo  Installing Copilot SDK...
    pip install github-copilot-sdk --quiet 2>nul
)

echo.
echo  ════════════════════════════════════════════════════════════════
echo  Starting the tool... Your browser will open automatically!
echo  ════════════════════════════════════════════════════════════════
echo.
echo  To stop: Close this window or press Ctrl+C
echo.

REM Run the unified app
python "%~dp0app.py"

pause
