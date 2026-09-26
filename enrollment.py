# enrollment.py
# Ye file gallery folder ke andar ki photos se logo ka chehra "seekh" ti hai
# aur ek data file (encodings.pkl) me save kar deti hai

import face_recognition   # Chehra pehchanne wali library
import os                 # Folders/files ke saath kaam karne ke liye
import pickle              # Data ko file me save/load karne ke liye
from config import GALLERY_FOLDER   # config.py se gallery ka path le rahe hain

def enroll_faces():
    known_encodings = []   # Har chehre ka "fingerprint" yahan store hoga
    known_names = []       # Us chehre ka naam yahan store hoga

    print("Enrollment shuru ho raha hai...")

    # gallery folder ke andar jitne bhi log (folders) hain, unpe loop chalao
    for person_name in os.listdir(GALLERY_FOLDER):
        person_folder = os.path.join(GALLERY_FOLDER, person_name)

        # Agar ye folder nahi hai (koi galti se file ho gayi), toh skip karo
        if not os.path.isdir(person_folder):
            continue

        print(f"'{person_name}' ki photos process ho rahi hain...")

        # Us insaan ke folder ke andar har photo pe loop chalao
        for image_name in os.listdir(person_folder):
            image_path = os.path.join(person_folder, image_name)

            try:
                # Photo ko load karo
                image = face_recognition.load_image_file(image_path)

                # Photo me se chehre ka "fingerprint" (encoding) nikalo
                encodings = face_recognition.face_encodings(image)

                # Agar photo me chehra mila (kabhi kabhi nahi milta agar photo unclear ho)
                if len(encodings) > 0:
                    known_encodings.append(encodings[0])
                    known_names.append(person_name)
                    print(f"  ✓ {image_name} - chehra mil gaya")
                else:
                    print(f"  ✗ {image_name} - is photo me chehra nahi mila, skip kar rahe hain")

            except Exception as e:
                print(f"  ✗ {image_name} - error aaya: {e}")

    # Sab kuch ek file me save kar do (taaki baar baar photos process na karni pade)
    data = {"encodings": known_encodings, "names": known_names}
    with open("encodings.pkl", "wb") as f:
        pickle.dump(data, f)

    print(f"\nEnrollment complete! Total {len(known_names)} chehre save kiye gaye.")
    print("Data 'encodings.pkl' file me save ho gaya hai.")

# Jab ye file directly run ki jaye, tab enroll_faces() function chalao
if __name__ == "__main__":
    enroll_faces()