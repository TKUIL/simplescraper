@echo off

REM Step 1: Check if Python is installed
echo Checking if Python is installed...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not found in PATH. Please install Python before running this script.
    pause
    exit /b 1
)

REM Step 2: Install required Python packages
echo Installing required Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install required Python packages.
    pause
    exit /b 1
)

echo Requirements installed successfully.
pause
exit /b 0
