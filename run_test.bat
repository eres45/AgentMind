@echo off
REM Batch script to process test.csv on Windows

echo ========================================
echo Agentic AI Reasoning System
echo Test Processing Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10 or higher.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
if not exist "venv\installed.flag" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo. > venv\installed.flag
    echo.
)

REM Check if test.csv exists
if not exist "..\test.csv" (
    echo ERROR: test.csv not found in parent directory
    echo Please ensure test.csv is in the correct location
    pause
    exit /b 1
)

REM Run the processor
echo.
echo Starting test processing...
echo.
python process_test.py --input ..\test.csv --output predictions.csv

echo.
echo ========================================
echo Processing Complete!
echo.
echo Output files:
echo   - predictions.csv
echo   - predictions_reasoning_traces.txt
echo   - predictions_summary.txt
echo ========================================
echo.

pause
