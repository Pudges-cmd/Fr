#!/bin/bash
# Installation script for YOLOv5 Detection and SMS Alert System

set -e

echo "Installing YOLOv5 Detection and SMS Alert System..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Make scripts executable
chmod +x start.sh
chmod +x install.sh

# Install system dependencies
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt install -y libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt install -y libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev
sudo apt install -y libswscale-dev libswresample-dev libavfilter-dev

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install systemd service
echo "Installing systemd service..."
sudo cp raspi-detect.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable raspi-detect.service

echo "Installation complete!"
echo ""
echo "To start the service:"
echo "  sudo systemctl start raspi-detect.service"
echo ""
echo "To stop the service:"
echo "  sudo systemctl stop raspi-detect.service"
echo ""
echo "To check status:"
echo "  sudo systemctl status raspi-detect.service"
echo ""
echo "To view logs:"
echo "  journalctl -u raspi-detect.service -f"
echo ""
echo "To run manually:"
echo "  ./start.sh"
