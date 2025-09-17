# -*- coding: utf-8 -*-
import sys
import os
import time
from collections import defaultdict

import cv2

# Add parent directory to path to import detector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector import YOLOv5Detector, open_camera


def test_camera_access():
    """Test different camera indices to find available cameras"""
    print("Testing camera access...")
    
    for i in range(5):  # Test camera indices 0-4
        print(f"Trying camera index {i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            # Try to read a frame to verify it actually works
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✓ Camera {i} is working! Resolution: {frame.shape[1]}x{frame.shape[0]}")
                cap.release()
                return i
            else:
                print(f"✗ Camera {i} opened but can't read frames")
        else:
            print(f"✗ Camera {i} failed to open")
        
        cap.release()
    
    print("No working cameras found!")
    return None


def open_camera_with_fallback(preferred_index=0):
    """Open camera with fallback options"""
    # First try the original open_camera function
    try:
        cap = open_camera()
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print("✓ Original open_camera() function works")
                return cap
            else:
                print("✗ Original open_camera() opened but can't read frames")
                cap.release()
    except Exception as e:
        print(f"✗ Original open_camera() failed: {e}")
    
    # Fallback: try to find any working camera
    working_index = test_camera_access()
    if working_index is not None:
        print(f"Using camera index {working_index} as fallback")
        return cv2.VideoCapture(working_index)
    
    return None


def main() -> None:
    print("Testing YOLOv5 Detection (Headless Mode)")
    
    # Initialize detector
    try:
        detector = YOLOv5Detector()
        print("✓ YOLOv5 detector initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize YOLOv5 detector: {e}")
        return
    
    # Open camera with better error handling
    cap = open_camera_with_fallback()
    if cap is None or not cap.isOpened():
        print("✗ Failed to open any camera. Possible solutions:")
        print("  1. Make sure a camera is connected")
        print("  2. Close other applications using the camera")
        print("  3. Check camera permissions")
        print("  4. Try running as administrator (Windows) or with sudo (Linux)")
        return

    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    last_fps_t = time.time()
    frames = 0
    total_frames = 0

    print("✓ Detection started. Press Ctrl+C to quit.")
    print("-" * 50)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("✗ Camera read failed, retrying...")
                time.sleep(1)
                continue

            total_frames += 1

            # Detect objects
            try:
                results = detector.detect(frame)
                counts = defaultdict(int)
                
                # Count detections
                for r in results:
                    counts[r["label"]] += 1

                # Calculate and display FPS
                frames += 1
                current_time = time.time()
                if current_time - last_fps_t >= 1.0:
                    fps = frames / (current_time - last_fps_t)
                    frames = 0
                    last_fps_t = current_time
                    print(f"FPS: {fps:.1f} | Total frames: {total_frames}")

                # Display detection counts
                if counts:
                    count_text = ", ".join([f"{k}:{v}" for k, v in counts.items()])
                    print(f"Detected: {count_text}")
                else:
                    # Only print "no objects" occasionally to reduce spam
                    if total_frames % 30 == 0:  # Every 30 frames
                        print("No objects detected")

            except Exception as e:
                print(f"✗ Detection error: {e}")

            time.sleep(0.033)  # ~30 FPS (adjust as needed)

    except KeyboardInterrupt:
        print("\n✓ Stopping detection...")

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")

    finally:
        cap.release()
        print("✓ Detection test completed.")


if __name__ == "__main__":
    main()
