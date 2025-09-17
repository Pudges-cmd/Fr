# -*- coding: utf-8 -*-
import sys
import os
import time
from collections import defaultdict

# Add parent directory to path to import detector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector import YOLOv5Detector, SIM7600SMS, open_camera

# Configuration
DESTINATION_NUMBERS = ["+639514343942"]  # Change to your phone number
EVENT_COOLDOWN_SECONDS = 60


def format_message(counts: dict[str, int]) -> str:
	parts = []
	for key in ("person", "dog", "cat"):
		if counts.get(key, 0) > 0:
			parts.append(f"{key}:{counts[key]}")
	return "Detected " + ", ".join(parts) if parts else "No targets"


def main() -> None:
	print("Testing Detection and SMS Integration")
	
	# Initialize detector
	detector = YOLOv5Detector()
	
	# Initialize camera
	cap = open_camera()
	if not cap.isOpened():
		raise RuntimeError("Camera open failed")

	# Initialize SMS
	try:
		modem = SIM7600SMS()
		print("SMS initialized successfully")
	except Exception as e:
		print(f"SMS initialization failed: {e}")
		modem = None

	last_sent: dict[str, float] = {}

	print("Starting detection loop. Press Ctrl+C to stop.")
	
	try:
		while True:
			ok, frame = cap.read()
			if not ok:
				print("Camera read failed, retrying...")
				time.sleep(1)
				continue
			
			# Detect objects
			results = detector.detect(frame)
			counts = defaultdict(int)
			for r in results:
				counts[r["label"]] += 1
			
			# Print detection results
			if counts:
				msg = format_message(counts)
				print(f"Detected: {msg}")
			else:
				print("No objects detected")
			
			# Send SMS if objects detected and cooldown passed
			total = sum(counts.values())
			if total > 0:
				key = "any"
				now = time.time()
				if now - last_sent.get(key, 0) >= EVENT_COOLDOWN_SECONDS:
					msg = format_message(counts)
					if modem:
						print(f"Sending SMS: {msg}")
						modem.send_sms(DESTINATION_NUMBERS, msg)
					last_sent[key] = now
			
			time.sleep(0.1)  # Small delay to prevent overwhelming CPU
			
	except KeyboardInterrupt:
		print("\nStopping detection...")
	finally:
		cap.release()
		if modem:
			modem.close()


if __name__ == "__main__":
	main()
