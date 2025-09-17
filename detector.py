#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrated YOLOv5 Detection and SMS Alert System
Detects people, dogs, and cats using YOLOv5n.pt and sends SMS alerts via SIM7600
"""

import os
import sys
import time
import glob
import serial
import urllib.request
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

import cv2
import numpy as np
import torch
from ultralytics import YOLO

# Configuration
CONFIDENCE_THRESHOLD = 0.35
NMS_IOU_THRESHOLD = 0.45
TARGET_CLASSES = {0: "person", 15: "cat", 16: "dog"}  # COCO class IDs
EVENT_COOLDOWN_SECONDS = 60  # Cooldown between SMS alerts
SERIAL_BAUDRATE = 115200
DESTINATION_NUMBERS = ["+639514343942"]  # Change this to your phone number

# Model and paths
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)
YOLOV5_MODEL_PATH = MODEL_DIR / "yolov5n.pt"

# Video capture settings
CAPTURE_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 384
TARGET_FPS = 15

# Logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
PID_FILE = Path("run/raspi-detect.pid")
PID_FILE.parent.mkdir(parents=True, exist_ok=True)


class YOLOv5Detector:
    """YOLOv5 detector using ultralytics YOLO"""
    
    def __init__(self):
        self.model = self._load_model()
        self.last_sent = {}
        
    def _load_model(self):
        """Load YOLOv5n.pt model"""
        if not YOLOV5_MODEL_PATH.exists():
            print(f"Model not found at {YOLOV5_MODEL_PATH}")
            print("Please download yolov5n.pt and place it in the models/ directory")
            print("Download from: https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt")
            sys.exit(1)
        
        print(f"Loading model from {YOLOV5_MODEL_PATH}")
        model = YOLO(str(YOLOV5_MODEL_PATH))
        return model
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """Detect objects in frame"""
        results = self.model(frame, conf=CONFIDENCE_THRESHOLD, iou=NMS_IOU_THRESHOLD)
        detections = []
        
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                if class_id in TARGET_CLASSES:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    detections.append({
                        "class_id": class_id,
                        "label": TARGET_CLASSES[class_id],
                        "confidence": confidence,
                        "box": [int(x1), int(y1), int(x2-x1), int(y2-y1)]
                    })
        
        return detections


class SIM7600SMS:
    """SIM7600 SMS handler"""
    
    def __init__(self, port: Optional[str] = None):
        self.port = port or self._auto_detect_port()
        if not self.port:
            raise RuntimeError("SIM7600 serial port not found")
        
        print(f"SIM7600 using port: {self.port}")
        self.ser = serial.Serial(self.port, baudrate=SERIAL_BAUDRATE, timeout=2.0)
        self._init_modem()
    
    def _auto_detect_port(self) -> Optional[str]:
        """Auto-detect SIM7600 port"""
        candidates = [
            "/dev/ttyUSB2", "/dev/ttyUSB3", "/dev/ttyUSB1", "/dev/ttyUSB0",
            "/dev/ttyS0", "/dev/serial0",
        ]
        candidates.extend(sorted(glob.glob("/dev/ttyUSB*")))
        candidates.extend(sorted(glob.glob("/dev/ttyACM*")))
        
        for port in candidates:
            if self._test_port(port):
                return port
        return None
    
    def _test_port(self, port: str) -> bool:
        """Test if port responds to AT commands"""
        try:
            ser = serial.Serial(port, baudrate=SERIAL_BAUDRATE, timeout=1.0)
            ser.write(b"AT\r")
            time.sleep(0.2)
            resp = ser.read(64).decode(errors="ignore")
            ser.close()
            return "OK" in resp or "AT" in resp
        except:
            return False
    
    def _init_modem(self):
        """Initialize modem"""
        self._send_cmd("AT")
        self._send_cmd("ATE0")  # echo off
        self._send_cmd("AT+CMGF=1")  # SMS text mode
        self._send_cmd("AT+CSCS=\"GSM\"")  # charset
        self._send_cmd("AT+CNMI=2,1,0,0,0")  # new message indications
    
    def _send_cmd(self, cmd: str, wait: float = 0.5) -> str:
        """Send AT command"""
        self.ser.reset_input_buffer()
        self.ser.write((cmd + "\r").encode())
        time.sleep(wait)
        resp = self.ser.read(self.ser.in_waiting or 256).decode(errors="ignore")
        return resp
    
    def send_sms(self, numbers: List[str], text: str):
        """Send SMS to multiple numbers"""
        for num in numbers:
            try:
                self.ser.write(f"AT+CMGS=\"{num}\"\r".encode())
                time.sleep(0.5)
                self.ser.write(text.encode() + b"\x1A")  # Ctrl+Z
                
                # Wait for confirmation
                t0 = time.time()
                buf = ""
                while time.time() - t0 < 20:
                    buf += self.ser.read(self.ser.in_waiting or 64).decode(errors="ignore")
                    if "+CMGS:" in buf or "OK" in buf:
                        print(f"SMS sent to {num}")
                        break
                    time.sleep(0.2)
                time.sleep(0.5)
            except Exception as e:
                print(f"Failed to send SMS to {num}: {e}")
    
    def close(self):
        """Close serial connection"""
        try:
            self.ser.close()
        except:
            pass


def format_alert_message(counts: Dict[str, int]) -> str:
    """Format detection counts into SMS message"""
    parts = []
    for key in ("person", "dog", "cat"):
        if counts.get(key, 0) > 0:
            parts.append(f"{key}:{counts[key]}")
    return "Detected " + ", ".join(parts)


def open_camera():
    """Open camera with optimal settings"""
    cap = cv2.VideoCapture(CAPTURE_INDEX, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
    return cap


def main():
    """Main detection loop"""
    print("Starting YOLOv5 Detection and SMS Alert System")
    
    # Write PID file
    PID_FILE.write_text(str(int(time.time())))
    
    detector = None
    sms_handler = None
    cap = None
    
    try:
        # Initialize detector
        print("Initializing YOLOv5 detector...")
        detector = YOLOv5Detector()
        
        # Initialize camera
        print("Opening camera...")
        cap = open_camera()
        if not cap.isOpened():
            raise RuntimeError("Failed to open camera")
        
        # Initialize SMS (optional)
        try:
            print("Initializing SMS handler...")
            sms_handler = SIM7600SMS()
        except Exception as e:
            print(f"SMS initialization failed: {e}")
            print("Continuing without SMS alerts...")
            sms_handler = None
        
        print("Detection system ready. Press Ctrl+C to stop.")
        
        # Main detection loop
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Camera read failed, retrying...")
                time.sleep(1)
                continue
            
            # Detect objects
            detections = detector.detect(frame)
            
            if detections and sms_handler:
                # Count detections by class
                counts = defaultdict(int)
                for det in detections:
                    counts[det["label"]] += 1
                
                # Check cooldown
                now = time.time()
                if now - detector.last_sent.get("any", 0) >= EVENT_COOLDOWN_SECONDS:
                    message = format_alert_message(counts)
                    print(f"Sending alert: {message}")
                    sms_handler.send_sms(DESTINATION_NUMBERS, message)
                    detector.last_sent["any"] = now
            
            # Print detection results
            if detections:
                for det in detections:
                    print(f"Detected: {det['label']} (confidence: {det['confidence']:.2f})")
            else:
                print("No objects detected")
            
            time.sleep(0.1)  # Small delay to prevent overwhelming CPU
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        if cap:
            cap.release()
        if sms_handler:
            sms_handler.close()
        try:
            PID_FILE.unlink(missing_ok=True)
        except:
            pass


if __name__ == "__main__":
    main()
