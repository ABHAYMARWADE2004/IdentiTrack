"""Central configuration for IdentiTrack.

Secrets and machine-specific values come from environment variables (.env);
everything else is a tunable default that lives here, in one place.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ===== MySQL =====
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "identitrack_db")
DB_POOL_SIZE = 5

# ===== Paths =====
GALLERY_FOLDER = "gallery"          # gallery/<PersonName>/*.jpg
ENCODINGS_FILE = "encodings.pkl"    # produced by enrollment.py
YOLO_MODEL = "yolov8n.pt"           # downloaded automatically on first run
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

# ===== Face matching =====
# Maximum face distance (dlib/face_recognition) to accept a match.
# Lower = stricter. The library default is 0.6, which is lenient and produces
# more false matches; 0.5 is a safer starting point. Use evaluate.py to pick
# a value from your own data instead of guessing.
FACE_MATCH_TOLERANCE = float(os.getenv("FACE_MATCH_TOLERANCE", "0.5"))
ENROLL_NUM_JITTERS = 5              # more jitters = better encodings, slower (one-time cost)

# ===== Detection =====
YOLO_CONFIDENCE = 0.4
# For tall (full-body) boxes the face is in the top part, so only that part is
# searched. This is faster and avoids false faces on clothing/background.
UPPER_BODY_FRACTION = 0.6
UPPER_BODY_ASPECT = 1.6             # height/width ratio above which a box is "tall"

# ===== Performance =====
PROCESS_EVERY_N_FRAMES = 2          # run the heavy models on every Nth frame

# ===== Logging / analytics =====
COOLDOWN_SECONDS = 15               # minimum gap before the same person is logged again
SESSION_GAP_MINUTES = 2             # a longer gap between detections starts a new visit
