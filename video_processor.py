# video_processor.py
# Ye file kisi bhi uploaded video file ko process karti hai
# YOLO se person detect, face_recognition se pehchaan, aur result video save karti hai

import cv2
import face_recognition
import pickle
import time
import imageio                     # Browser-friendly video likhne ke liye
from ultralytics import YOLO
from database import save_detection

COOLDOWN_SECONDS = 15

def load_known_faces():
    with open("encodings.pkl", "rb") as f:
        data = pickle.load(f)
    return data["encodings"], data["names"]

def process_video(input_path, output_path="output_video.mp4"):
    """
    Ek video file ko process karta hai:
    - Har frame me person detect (YOLO) aur face pehchaan (face_recognition) karta hai
    - Result ko ek nayi (browser-playable) video file me save karta hai
    - Database me bhi log karta hai
    """
    known_encodings, known_names = load_known_faces()
    yolo_model = YOLO("yolov8n.pt")

    video_capture = cv2.VideoCapture(input_path)

    fps = video_capture.get(cv2.CAP_PROP_FPS) or 20

    # imageio writer banao - H.264 codec use karta hai, ye browsers me chalta hai
    writer = imageio.get_writer(output_path, fps=fps, codec="libx264", quality=7)

    last_saved_time = {}
    frame_count = 0

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        frame_count += 1

        results = yolo_model(frame, classes=[0], verbose=False)

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            person_crop = frame[y1:y2, x1:x2]

            if person_crop.size == 0:
                continue

            rgb_crop = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_crop)
            face_encodings = face_recognition.face_encodings(rgb_crop, face_locations)

            name = "Person Detected"

            if len(face_encodings) > 0:
                face_encoding = face_encodings[0]
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)

                if len(face_distances) > 0:
                    best_match_index = face_distances.argmin()
                    if matches[best_match_index]:
                        name = known_names[best_match_index]

                        current_time = time.time()
                        last_time = last_saved_time.get(name, 0)
                        if current_time - last_time > COOLDOWN_SECONDS:
                            save_detection(name)
                            last_saved_time[name] = current_time
                    else:
                        name = "Unknown Face"

            box_color = (0, 255, 0) if name not in ["Person Detected", "Unknown Face"] else (255, 150, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            cv2.rectangle(frame, (x1, y2 - 30), (x2, y2), box_color, cv2.FILLED)
            cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        # imageio ko RGB chahiye, OpenCV frames BGR me hote hain - isliye convert karo
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        writer.append_data(rgb_frame)

    video_capture.release()
    writer.close()

    return output_path, frame_count