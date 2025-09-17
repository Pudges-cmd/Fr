# YOLOv5 Detection and SMS Alert System

A simplified, integrated system that detects people, dogs, and cats using YOLOv5n.pt and sends SMS alerts via SIM7600 modem. Everything is contained in a single `detector.py` file for simplicity.

## Features

- **Integrated Design**: Single file contains both detection and SMS functionality
- **YOLOv5n.pt Model**: Uses the lightweight YOLOv5 nano model for fast detection
- **Auto-Download**: Automatically downloads the model on first run
- **SMS Alerts**: Sends SMS notifications when objects are detected
- **Configurable**: Easy to modify detection classes, confidence thresholds, and phone numbers
- **Raspberry Pi Ready**: Optimized for Raspberry Pi with systemd service

## Quick Start

### 1. Installation

```bash
# Clone or download this repository
cd Fred

# Run the installation script
./install.sh
```

### 2. Configuration

Edit `detector.py` to configure your settings:

```python
# Change these values in detector.py
DESTINATION_NUMBERS = ["+639514343942"]  # Your phone number
CONFIDENCE_THRESHOLD = 0.35              # Detection confidence (0.0-1.0)
EVENT_COOLDOWN_SECONDS = 60              # Seconds between SMS alerts
```

### 3. Hardware Setup

1. **Camera**: Connect USB camera or use Raspberry Pi camera
2. **SIM7600**: Connect SIM7600 module via USB or serial
3. **SIM Card**: Insert SIM card with SMS capability

### 4. Running the System

#### Manual Run
```bash
./start.sh
```

#### As a Service (Recommended)
```bash
# Start the service
sudo systemctl start raspi-detect.service

# Check status
sudo systemctl status raspi-detect.service

# View logs
journalctl -u raspi-detect.service -f

# Stop service
sudo systemctl stop raspi-detect.service
```

## File Structure

```
Fred/
├── detector.py              # Main detection and SMS system
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── start.sh               # Manual startup script
├── install.sh             # Installation script
├── raspi-detect.service   # Systemd service file
├── models/                # YOLOv5 model storage
├── logs/                  # Log files
└── run/                   # PID files
```

## Configuration Options

### Environment Variables

You can override settings using environment variables:

```bash
export CONFIDENCE_THRESHOLD=0.4
export EVENT_COOLDOWN_SECONDS=30
export DESTINATION_NUMBERS="+1234567890,+0987654321"
export CAPTURE_INDEX=1
export FRAME_WIDTH=1280
export FRAME_HEIGHT=720
```

### Detection Classes

The system detects these COCO classes by default:
- **Person** (class ID: 0)
- **Cat** (class ID: 15) 
- **Dog** (class ID: 16)

To modify, edit the `TARGET_CLASSES` dictionary in `detector.py`.

## Model Management

### Manual Download Required
You must manually download the YOLOv5n.pt model:

```bash
# Create models directory
mkdir -p models

# Download the model
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt -O models/yolov5n.pt
```

**File Location**: `models/yolov5n.pt`

## SMS Configuration

### SIM7600 Setup
1. Connect SIM7600 to USB port
2. Insert SIM card with SMS capability
3. The system auto-detects the port

### Phone Number Format
Use international format: `+[country code][number]`
- Philippines: `+639123456789`
- US: `+1234567890`

## Troubleshooting

### Camera Issues
```bash
# List available cameras
ls /dev/video*

# Test camera
ffmpeg -f v4l2 -i /dev/video0 -t 5 test.mp4
```

### SIM7600 Issues
```bash
# List serial ports
ls /dev/ttyUSB* /dev/ttyACM*

# Test SIM7600
sudo minicom -D /dev/ttyUSB2
# Type: AT
# Should respond: OK
```

### Permission Issues
```bash
# Add user to dialout group for serial access
sudo usermod -a -G dialout $USER
# Log out and back in
```

### Model Download Issues
```bash
# Check internet connection
ping google.com

# Manual model download
python3 -c "from ultralytics import YOLO; YOLO('yolov5n.pt')"
```

## Performance Tuning

### For Raspberry Pi Zero 2W
- Use `FRAME_WIDTH=320` and `FRAME_HEIGHT=192`
- Set `TARGET_FPS=10`
- Use `CONFIDENCE_THRESHOLD=0.5`

### For Raspberry Pi 4
- Use `FRAME_WIDTH=640` and `FRAME_HEIGHT=384`
- Set `TARGET_FPS=15`
- Use `CONFIDENCE_THRESHOLD=0.35`

## Logs and Monitoring

### View Real-time Logs
```bash
journalctl -u raspi-detect.service -f
```

### Check Service Status
```bash
sudo systemctl status raspi-detect.service
```

### Manual Testing
```bash
# Test detection only (no SMS)
python3 -c "
import cv2
from detector import YOLOv5Detector
detector = YOLOv5Detector()
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    results = detector.detect(frame)
    print(f'Detected: {results}')
cap.release()
"
```

## Customization

### Adding New Detection Classes
Edit `TARGET_CLASSES` in `detector.py`:
```python
TARGET_CLASSES = {
    0: "person",
    15: "cat", 
    16: "dog",
    2: "car",      # Add car detection
    3: "motorcycle" # Add motorcycle detection
}
```

### Custom SMS Message Format
Edit the `format_alert_message()` function in `detector.py`:
```python
def format_alert_message(counts: Dict[str, int]) -> str:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    parts = []
    for key in ("person", "dog", "cat"):
        if counts.get(key, 0) > 0:
            parts.append(f"{key}:{counts[key]}")
    return f"[{timestamp}] Alert: " + ", ".join(parts)
```

## System Requirements

- **OS**: Raspberry Pi OS (64-bit recommended)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 2GB free space
- **Camera**: USB camera or Raspberry Pi camera
- **SIM7600**: 4G/LTE module with SMS capability
- **Python**: 3.8 or higher

## Dependencies

- PyTorch
- OpenCV
- Ultralytics YOLO
- PySerial
- NumPy

## License

This project is open source. Feel free to modify and distribute.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs: `journalctl -u raspi-detect.service -f`
3. Test components individually using the manual testing commands