@echo off
echo Running Python Application...

REM Step 1: Run the web scraper
echo Running web scraper...
python main.py
if %errorlevel% neq 0 (
    echo Error: Web scraper failed to run.
    exit /b 1
)

REM Step 2: Update the database
echo Updating database...
python update_database.py
if %errorlevel% neq 0 (
    echo Error: Failed to update the database.
    exit /b 1
)

REM Step 3: Launch the visualization process
echo Launching visualization...
python visualize_data.py
if %errorlevel% neq 0 (
    echo Error: Failed to visualize the data.
    exit /b 1
)

echo Python application completed successfully.
exit /b 0
