"""Live webcam tracking.

    python tracker.py                         # default camera 0
    python tracker.py --camera 1 --name Gate  # another camera, labelled 'Gate'

Press 'q' in the video window to quit.
"""

import argparse
import time
from datetime import datetime

import cv2

import config
from database import init_db, save_detection
from recognizer import KNOWN, PersonRecognizer
from utils import CooldownGate


def run(camera_index=0, camera_name="webcam"):
    print("Checking database...")
    init_db()

    print("Loading models and enrolled faces...")
    recognizer = PersonRecognizer()
    print(f"{len(recognizer.known_names)} enrolled face(s) loaded "
          f"(match tolerance {recognizer.tolerance}).")

    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        raise SystemExit(f"Could not open camera {camera_index}. Check the connection / index.")

    gate = CooldownGate(config.COOLDOWN_SECONDS)
    detections = []
    frame_index = 0
    fps = 0.0
    last_tick = time.perf_counter()
    print("Tracking started. Press 'q' to quit.")

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                print("Could not read a frame from the camera.")
                break

            # Heavy models run on every Nth frame; skipped frames reuse the last result.
            if frame_index % config.PROCESS_EVERY_N_FRAMES == 0:
                detections = recognizer.process_frame(frame)
                now = time.time()
                for d in detections:
                    if d.status == KNOWN and gate.should_log(d.name, now):
                        try:
                            save_detection(d.name, event_time=datetime.now(),
                                           distance=d.distance, source="live",
                                           source_name=camera_name)
                            print(f"Logged: {d.name} (distance {d.distance:.2f})")
                        except Exception as exc:  # keep the camera loop alive
                            print(f"Database write failed: {exc}")

            recognizer.annotate(frame, detections)

            tick = time.perf_counter()
            fps = 0.9 * fps + 0.1 * (1.0 / max(tick - last_tick, 1e-6))
            last_tick = tick
            cv2.putText(frame, f"{fps:.1f} FPS", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow("IdentiTrack - Live Tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            frame_index += 1
    finally:
        capture.release()
        cv2.destroyAllWindows()
        print("Tracking stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IdentiTrack live tracker")
    parser.add_argument("--camera", type=int, default=0, help="camera index (default 0)")
    parser.add_argument("--name", default="webcam", help="label stored with each detection")
    args = parser.parse_args()
    run(args.camera, args.name)
