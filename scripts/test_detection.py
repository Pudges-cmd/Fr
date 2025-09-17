# -*- coding: utf-8 -*-
import sys
import os
import time
from collections import defaultdict

import cv2

# Add parent directory to path to import detector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector import YOLOv5Detector, open_camera


def main() -> None:
	print("Testing YOLOv5 Detection (Headless Mode)")
	
	detector = YOLOv5Detector()
	cap = open_camera()
	if not cap.isOpened():
		raise RuntimeError("Camera open failed")

	last_fps_t = time.time()
	frames = 0

	print("Detection started. Press Ctrl+C to quit.")

	try:
		while True:
			ok, frame = cap.read()
			if not ok:
				break

			# Detect objects
			results = detector.detect(frame)
			counts = defaultdict(int)
			
			# Count detections
			for r in results:
				counts[r["label"]] += 1

			# Calculate and display FPS
			frames += 1
			if time.time() - last_fps_t >= 1.0:
				fps = frames
				frames = 0
				last_fps_t = time.time()
				print(f"FPS: {fps}")

			# Display detection counts
			if counts:
				count_text = ", ".join([f"{k}:{v}" for k, v in counts.items()])
				print(f"Detected: {count_text}")
			else:
				print("No objects detected")

			time.sleep(0.1)  # Small delay to prevent overwhelming output

	except KeyboardInterrupt:
		print("\nStopping detection...")

	cap.release()
	print("Detection test completed.")


if __name__ == "__main__":
	main()
