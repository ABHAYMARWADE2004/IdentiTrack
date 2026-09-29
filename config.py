# config.py
# Central configuration file - loads sensitive values from .env

from dotenv import load_dotenv
import os

load_dotenv()

# ===== MySQL Database Settings =====
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = "identitrack_db"

# ===== Folder Paths =====
GALLERY_FOLDER = "gallery"

# ===== Face Recognition Settings =====
FACE_MATCH_TOLERANCE = 0.6  # Lower = stricter matching