"""Build face encodings from the photos in gallery/<PersonName>/.

    python enrollment.py
    python enrollment.py --gallery my_photos

Writes encodings.pkl (read by the tracker, video processor and evaluator).
"""

import argparse
import os
import pickle
from collections import Counter

import face_recognition

import config

MIN_RECOMMENDED_PHOTOS = 3


def enroll_faces(gallery=config.GALLERY_FOLDER, output=config.ENCODINGS_FILE):
    if not os.path.isdir(gallery):
        raise SystemExit(f"Gallery folder '{gallery}' not found. "
                         f"Create {gallery}/<PersonName>/ and add clear photos.")

    encodings, names = [], []
    skipped = Counter()
    print(f"Enrolling from '{gallery}'...")

    for person in sorted(os.listdir(gallery)):
        folder = os.path.join(gallery, person)
        if not os.path.isdir(folder):
            continue
        print(f"\n{person}")
        for image_name in sorted(os.listdir(folder)):
            if not image_name.lower().endswith(config.IMAGE_EXTENSIONS):
                continue
            path = os.path.join(folder, image_name)
            try:
                image = face_recognition.load_image_file(path)
                locations = face_recognition.face_locations(image)
                if len(locations) == 0:
                    print(f"  skip  {image_name}: no face found")
                    skipped[person] += 1
                    continue
                if len(locations) > 1:
                    # Ambiguous: we cannot know which face is this person's.
                    print(f"  skip  {image_name}: {len(locations)} faces (use single-person photos)")
                    skipped[person] += 1
                    continue
                encoding = face_recognition.face_encodings(
                    image, locations, num_jitters=config.ENROLL_NUM_JITTERS)[0]
                encodings.append(encoding)
                names.append(person)
                print(f"  ok    {image_name}")
            except Exception as exc:  # noqa: BLE001
                print(f"  error {image_name}: {exc}")
                skipped[person] += 1

    with open(output, "wb") as f:
        pickle.dump({"encodings": encodings, "names": names}, f)

    counts = Counter(names)
    print("\n===== Enrollment summary =====")
    for person, n in counts.items():
        note = "" if n >= MIN_RECOMMENDED_PHOTOS else \
            f"  <- only {n}; add more photos (different angles/lighting) for reliable matching"
        print(f"{person}: {n} usable photo(s), {skipped[person]} skipped{note}")
    print(f"Saved {len(names)} encoding(s) for {len(counts)} person(s) to '{output}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IdentiTrack enrollment")
    parser.add_argument("--gallery", default=config.GALLERY_FOLDER)
    parser.add_argument("--out", default=config.ENCODINGS_FILE)
    args = parser.parse_args()
    enroll_faces(args.gallery, args.out)
