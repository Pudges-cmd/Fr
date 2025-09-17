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
	print("Testing YOLOv5 Detection (Visual Mode)")
	
	detector = YOLOv5Detector()
	cap = open_camera()
	if not cap.isOpened():
		raise RuntimeError("Camera open failed")

	last_fps_t = time.time()
	frames = 0

	print("Detection started. Press 'q' or ESC to quit.")

	while True:
		ok, frame = cap.read()
		if not ok:
			break

		# Detect objects
		results = detector.detect(frame)
		counts = defaultdict(int)
		
		# Draw detections
		for r in results:
			counts[r["label"]] += 1
			x, y, w, h = r["box"]
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
			cv2.putText(frame, f"{r['label']} {r['confidence']:.2f}", (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

		# Calculate and display FPS
		frames += 1
		if time.time() - last_fps_t >= 1.0:
			fps = frames
			frames = 0
			last_fps_t = time.time()
			cv2.putText(frame, f"FPS: {fps}", (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2, cv2.LINE_AA)

		# Display detection counts
		if counts:
			count_text = ", ".join([f"{k}:{v}" for k, v in counts.items()])
			cv2.putText(frame, f"Detected: {count_text}", (8, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)

		cv2.imshow("YOLOv5 Detection Test", frame)
		key = cv2.waitKey(1) & 0xFF
		if key == 27 or key == ord("q"):
			break

	cap.release()
	cv2.destroyAllWindows()
	print("Detection test completed.")


if __name__ == "__main__":
	main()
