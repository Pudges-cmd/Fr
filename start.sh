#!/bin/bash
# Startup script for YOLOv5 Detection and SMS Alert System

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run as root. Use a regular user account."
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if model exists, download if not
if [ ! -f "models/yolov5n.pt" ]; then
    echo "Model not found. It will be downloaded on first run."
fi

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Start the detector
echo "Starting YOLOv5 Detection and SMS Alert System..."
echo "Press Ctrl+C to stop"
python3 detector.py
