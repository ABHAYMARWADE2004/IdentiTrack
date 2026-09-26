# tracker.py
# Ye file webcam se live video lekar 2-step detection karti hai:
# Step 1: YOLO se "person" (poora insaan) detect karta hai
# Step 2: Us person ke andar face_recognition se chehra pehchanta hai
# Agar chehra na mile bhi, "Person Detected" dikhayega (sirf naam nahi dikhega)

import cv2
import face_recognition
import pickle
import time
from ultralytics import YOLO          # YOLO model ke liye
from database import save_detection

COOLDOWN_SECONDS = 15   # Itne second ke andar same banda dobara save nahi hoga

def load_known_faces():
    """encodings.pkl file se saare known chehre load karo"""
    with open("encodings.pkl", "rb") as f:
        data = pickle.load(f)
    return data["encodings"], data["names"]

def start_tracking():
    print("Known faces load ho rahe hain...")
    known_encodings, known_names = load_known_faces()
    print(f"{len(known_names)} chehre load ho gaye.")

    print("YOLO model load ho raha hai (pehli baar thoda time lagega, download hoga)...")
    yolo_model = YOLO("yolov8n.pt")   # 'n' = nano, sabse halka/fast model (CPU ke liye best)
    print("YOLO ready! Webcam shuru ho raha hai...")
    print("Band karne ke liye 'q' key dabao")

    last_saved_time = {}   # Har banda ka "aakhri baar kab save hua"

    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()

        if not ret:
            print("Webcam se frame nahi mil raha, check karo camera connected hai")
            break

        # ===== STEP 1: YOLO se "person" detect karo =====
        # classes=[0] matlab sirf "person" class detect karo (COCO dataset me 0 = person)
        results = yolo_model(frame, classes=[0], verbose=False)

        # Har detected person pe loop chalao
        for box in results[0].boxes:
            # Box ki coordinates nikalo (person kahan hai frame me)
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Us person ke box ka crop nikalo (sirf uska hissa, poora frame nahi)
            person_crop = frame[y1:y2, x1:x2]

            # Agar crop khaali hai (edge case), skip karo
            if person_crop.size == 0:
                continue

            # ===== STEP 2: Is crop ke andar chehra dhundo =====
            rgb_crop = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_crop)
            face_encodings = face_recognition.face_encodings(rgb_crop, face_locations)

            name = "Person Detected"   # Default - agar chehra na mile

            if len(face_encodings) > 0:
                # Chehra mila, ab match karke dekho kaun hai
                face_encoding = face_encodings[0]
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)

                if len(face_distances) > 0:
                    best_match_index = face_distances.argmin()
                    if matches[best_match_index]:
                        name = known_names[best_match_index]

                        # ===== COOLDOWN LOGIC =====
                        current_time = time.time()
                        last_time = last_saved_time.get(name, 0)

                        if current_time - last_time > COOLDOWN_SECONDS:
                            save_detection(name)
                            last_saved_time[name] = current_time
                            print(f"Database me save hua: {name}")
                    else:
                        name = "Unknown Face"

            # ===== Box aur Naam Draw Karo (Original Frame Pe) =====
            # Agar naam pehchana gaya (koi enrolled banda), green box; warna neela box
            box_color = (0, 255, 0) if name not in ["Person Detected", "Unknown Face"] else (255, 150, 0)

            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            cv2.rectangle(frame, (x1, y2 - 30), (x2, y2), box_color, cv2.FILLED)
            cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        # Screen pe dikhao
        cv2.imshow("IdentiTrack - Live Tracking (YOLO + Face Recognition)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    print("Tracking band ho gaya.")

if __name__ == "__main__":
    start_tracking()