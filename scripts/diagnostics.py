# -*- coding: utf-8 -*-
import sys
import os
import traceback
from pathlib import Path

import cv2

# Add parent directory to path to import detector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector import YOLOv5Detector, SIM7600SMS, open_camera

# Configuration
MODEL_PATH = Path("models/yolov5n.pt")
CONFIDENCE_THRESHOLD = 0.35
NMS_IOU_THRESHOLD = 0.45
FRAME_WIDTH = 640
FRAME_HEIGHT = 384


def main(argv: list[str]) -> int:
	print("== YOLOv5 Detection System Diagnostics ==")
	print(f"Model path: {MODEL_PATH}")
	print(f"Thresholds: conf={CONFIDENCE_THRESHOLD}, nms={NMS_IOU_THRESHOLD}")
	print(f"Frame size: {FRAME_WIDTH}x{FRAME_HEIGHT}")
	print()

	# Model existence check
	if not MODEL_PATH.exists():
		print(f"❌ Model not found at {MODEL_PATH}")
		print("   Please download yolov5n.pt and place it in the models/ directory")
		print("   Download from: https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt")
		return 1
	else:
		print(f"✅ Model found: {MODEL_PATH}")

	# Camera check
	print("\n--- Camera Test ---")
	cap = open_camera()
	if not cap.isOpened():
		print("❌ Camera open failed")
		print("   Check if camera is connected and not in use by another application")
		return 2
	
	ok, frame = cap.read()
	cap.release()
	if not ok or frame is None:
		print("❌ Camera read failed (empty frame)")
		return 2
	
	print(f"✅ Camera working: {frame.shape[1]}x{frame.shape[0]}")

	# Detection test
	print("\n--- Detection Test ---")
	try:
		detector = YOLOv5Detector()
		print("✅ YOLOv5 detector initialized successfully")
		
		# Test detection on a frame
		cap = open_camera()
		ok, frame = cap.read()
		if ok:
			results = detector.detect(frame)
			print(f"✅ Detection test: Found {len(results)} objects")
			for r in results:
				print(f"   - {r['label']}: {r['confidence']:.2f}")
		cap.release()
		
	except Exception as e:
		print(f"❌ Detection test failed: {e}")
		traceback.print_exc()
		return 3

	# SMS test
	print("\n--- SMS Test ---")
	modem = None
	try:
		modem = SIM7600SMS()
		print("✅ SIM7600 initialized successfully")
		print("   SMS functionality is ready")
	except Exception as e:
		print(f"❌ SIM7600 error: {e}")
		print("   Make sure SIM7600 is connected and SIM card is inserted")
		return 4
	finally:
		try:
			if modem is not None:
				modem.close()
		except Exception:
			pass

	print("\n✅ All diagnostics passed! System is ready to run.")
	print("\nTo start the system:")
	print("  ./start.sh")
	print("\nTo run as a service:")
	print("  sudo systemctl start raspi-detect.service")
	return 0


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
