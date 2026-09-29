# enrollment.py
# Reads photos from the gallery folder and extracts a face encoding
# for each enrolled person, saving the result to encodings.pkl

import face_recognition
import os
import pickle
from config import GALLERY_FOLDER

def enroll_faces():
    known_encodings = []
    known_names = []

    print("Starting enrollment...")

    for person_name in os.listdir(GALLERY_FOLDER):
        person_folder = os.path.join(GALLERY_FOLDER, person_name)

        if not os.path.isdir(person_folder):
            continue

        print(f"Processing photos for '{person_name}'...")

        for image_name in os.listdir(person_folder):
            image_path = os.path.join(person_folder, image_name)

            try:
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)

                if len(encodings) > 0:
                    known_encodings.append(encodings[0])
                    known_names.append(person_name)
                    print(f"  OK {image_name} - face found")
                else:
                    print(f"  SKIP {image_name} - no face detected in this photo")

            except Exception as e:
                print(f"  ERROR {image_name} - {e}")

    data = {"encodings": known_encodings, "names": known_names}
    with open("encodings.pkl", "wb") as f:
        pickle.dump(data, f)

    print(f"\nEnrollment complete! {len(known_names)} face(s) saved.")
    print("Data saved to 'encodings.pkl'.")

if __name__ == "__main__":
    enroll_faces()