# tracker.py
# Live webcam-based detection: YOLO detects a person, face_recognition
# identifies who they are. Includes cooldown logic to avoid duplicate
# database entries for a continuously visible person.

import cv2
import face_recognition
import pickle
import time
from ultralytics import YOLO
from database import save_detection

COOLDOWN_SECONDS = 15  # Minimum gap before the same person is logged again

def load_known_faces():
    """Loads previously enrolled face encodings from encodings.pkl"""
    with open("encodings.pkl", "rb") as f:
        data = pickle.load(f)
    return data["encodings"], data["names"]

def start_tracking():
    print("Loading known faces...")
    known_encodings, known_names = load_known_faces()
    print(f"{len(known_names)} face(s) loaded.")

    print("Loading YOLO model (first run may take a moment to download)...")
    yolo_model = YOLO("yolov8n.pt")
    print("YOLO ready! Starting webcam...")
    print("Press 'q' to quit")

    last_saved_time = {}

    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()

        if not ret:
            print("Couldn't read frame from webcam, check camera connection")
            break

        # ===== STEP 1: Detect people using YOLO =====
        results = yolo_model(frame, classes=[0], verbose=False)  # class 0 = person

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            person_crop = frame[y1:y2, x1:x2]

            if person_crop.size == 0:
                continue

            # ===== STEP 2: Look for a face within this person's box =====
            rgb_crop = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_crop)
            face_encodings = face_recognition.face_encodings(rgb_crop, face_locations)

            name = "Person Detected"  # default if no face is visible

            if len(face_encodings) > 0:
                face_encoding = face_encodings[0]
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)

                if len(face_distances) > 0:
                    best_match_index = face_distances.argmin()
                    if matches[best_match_index]:
                        name = known_names[best_match_index]

                        # ===== Cooldown logic =====
                        current_time = time.time()
                        last_time = last_saved_time.get(name, 0)

                        if current_time - last_time > COOLDOWN_SECONDS:
                            save_detection(name)
                            last_saved_time[name] = current_time
                            print(f"Logged to database: {name}")
                    else:
                        name = "Unknown Face"

            # ===== Draw box and label on the frame =====
            box_color = (0, 255, 0) if name not in ["Person Detected", "Unknown Face"] else (255, 150, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            cv2.rectangle(frame, (x1, y2 - 30), (x2, y2), box_color, cv2.FILLED)
            cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow("IdentiTrack - Live Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    print("Tracking stopped.")

if __name__ == "__main__":
    start_tracking()