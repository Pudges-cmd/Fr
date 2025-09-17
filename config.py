#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration file for YOLOv5 Detection and SMS Alert System
"""

import os
from pathlib import Path

# Model settings
MODEL_DIR = Path("models")
YOLOV5_MODEL_PATH = MODEL_DIR / "yolov5n.pt"

# Detection settings
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.35"))
NMS_IOU_THRESHOLD = float(os.getenv("NMS_IOU_THRESHOLD", "0.45"))
TARGET_CLASSES = {0: "person", 15: "cat", 16: "dog"}  # COCO class IDs

# Video capture settings
CAPTURE_INDEX = int(os.getenv("CAPTURE_INDEX", "0"))
FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", "640"))
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", "384"))
TARGET_FPS = int(os.getenv("TARGET_FPS", "15"))

# SMS settings
SERIAL_BAUDRATE = int(os.getenv("SERIAL_BAUDRATE", "115200"))
SERIAL_PORT = os.getenv("SERIAL_PORT", "")  # Auto-detect if empty
DESTINATION_NUMBERS = os.getenv("DESTINATION_NUMBERS", "+639514343942").split(",")

# Alert settings
EVENT_COOLDOWN_SECONDS = int(os.getenv("EVENT_COOLDOWN_SECONDS", "60"))

# Paths
LOG_DIR = Path("logs")
PID_FILE = Path("run/raspi-detect.pid")

# Create directories
MODEL_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
PID_FILE.parent.mkdir(parents=True, exist_ok=True)
