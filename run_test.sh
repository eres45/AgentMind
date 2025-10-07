#!/bin/bash
# Shell script to process test.csv on Linux/Mac

echo "========================================"
echo "Agentic AI Reasoning System"
echo "Test Processing Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
if [ ! -f "venv/installed.flag" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/installed.flag
    echo ""
fi

# Check if test.csv exists
if [ ! -f "../test.csv" ]; then
    echo "ERROR: test.csv not found in parent directory"
    echo "Please ensure test.csv is in the correct location"
    exit 1
fi

# Run the processor
echo ""
echo "Starting test processing..."
echo ""
python process_test.py --input ../test.csv --output predictions.csv

echo ""
echo "========================================"
echo "Processing Complete!"
echo ""
echo "Output files:"
echo "  - predictions.csv"
echo "  - predictions_reasoning_traces.txt"
echo "  - predictions_summary.txt"
echo "========================================"
echo ""
