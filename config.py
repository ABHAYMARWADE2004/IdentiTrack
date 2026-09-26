# config.py
# Yahan hum saari important settings rakhte hain
# Sensitive info (jaise password) .env file se aati hai, taaki GitHub pe expose na ho

from dotenv import load_dotenv
import os

load_dotenv()   # .env file se values load karo

# ===== MySQL Database Settings =====
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = os.getenv("DB_PASSWORD")   # .env file se password aayega
DB_NAME = "identitrack_db"

# ===== Folder Paths =====
GALLERY_FOLDER = "gallery"

# ===== Face Recognition Settings =====
FACE_MATCH_TOLERANCE = 0.6