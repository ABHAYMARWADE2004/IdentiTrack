# 🎯 IdentiTrack

### AI-Powered Person Re-Identification & Real-Time Tracking System

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)](https://opencv.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple.svg)](https://ultralytics.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)
[![MySQL](https://img.shields.io/badge/MySQL-Database-orange.svg)](https://www.mysql.com/)

IdentiTrack Is an End-To-End Computer Vision System That Enrolls Individuals From Reference Photos And Automatically Detects And Identifies Them in Real Time — Via Live Webcam or Uploaded Video — While Logging Every Detection To a Database and surfacing Insights Through An Interactive Analytics Dashboard.

Built As a Hands-On Deep Dive Into Computer Vision, Real-Time Systems And Data Analytics — Combining a Two-stage AI Detection Pipeline With a Full data Logging And Visualization Layer.

---

## 🔑 Highlights

- **Two-stage detection pipeline** — YOLOv8 for Person Detection + Face Recognition for Identity Matching, So Presence Is Detected Even When a Face isn't Visible
- **Dual input modes** — Real-Time webcam tracking *and* Uploaded video File Processing
- **Full data pipeline** — From Raw Video Frames → Structured MySQL Records → Interactive Analytics Dashboard
- **Production-conscious design** — Cooldown-Based Deduplication, Secure Credential handling via `.env`, And a clean Modular Codebase

---

## 🚀 Features

| Feature | Description |
|---|---|
| 👤 **Face Enrollment** | Register individuals from reference photos organized by name |
| 🎯 **Two-Stage Detection** | YOLOv8 detects *presence*, face recognition confirms *identity* |
| 📹 **Live Webcam Tracking** | Real-time detection and recognition with on-screen bounding boxes |
| 🎬 **Video File Processing** | Upload any video and run the full detection pipeline on it |
| 🗄️ **Database Logging** | Every detection logged to MySQL with cooldown-based deduplication |
| 📊 **Analytics Dashboard** | Peak-hour trends, per-person counts, date-wise activity, CSV export |
| 🔍 **Filtering** | Filter detection records by person and by date |
| 🔒 **Secure Config** | Credentials managed via `.env`, excluded from version control |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| Person Detection | YOLOv8 (Ultralytics) |
| Face Recognition | `face_recognition` (dlib-based, 128-d facial embeddings) |
| Video Processing | OpenCV, imageio (H.264 encoding) |
| Database | MySQL |
| Dashboard | Streamlit |
| Data Analysis | Pandas |
| Configuration | python-dotenv |

---

## 🧠 How It Works

┌──────────────┐ ┌──────────────────┐ ┌────────────────────┐
│ Gallery │ --> │ Enrollment │ --> │ Face Encodings │
│ Photos │ │ (enrollment.py) │ │ (encodings.pkl) │
└──────────────┘ └──────────────────┘ └────────────────────┘
│
┌──────────────┐ ┌──────────────────┐ │
│ Webcam / │ --> │ YOLOv8 Person │ <─────────────┘
│ Video File │ │ Detection │
└──────────────┘ └──────────────────┘
│
▼
┌──────────────────┐
│ Face Match │
│ Against Encodings│
└──────────────────┘
│
▼
┌──────────────────┐ ┌────────────────────┐
│ MySQL Logging │ --> │ Streamlit │
│ (with cooldown) │ │ Analytics Dashboard│
└──────────────────┘ └────────────────────┘


1. **Enrollment**: Reference photos in `gallery/<PersonName>/` are converted into 128-dimension facial embeddings via `enrollment.py` and stored in `encodings.pkl`.
2. **Detection**: Each frame (from webcam or video) is passed through YOLOv8, which locates every person present — regardless of whether their face is visible.
3. **Recognition**: The cropped region for each detected person is checked for a face; if found, it's matched against stored encodings using distance-based comparison.
4. **Logging**: Matched detections are inserted into MySQL, with cooldown logic preventing duplicate entries for a continuously visible person.
5. **Visualization**: The Streamlit dashboard reads live from the database to surface detection counts, peak activity hours, trends, and exportable records.

---

## 📁 Project Structure

IdentiTrack/
├── gallery/ # Reference photos for Enrollment, Organized by person name
│ └── PersonName/
│ ├── photo1.jpg
│ └── photo2.jpg
├── config.py # Central Configuration (loads secrets from .env)
├── enrollment.py # Extracts face encodings from gallery photos
├── tracker.py # Real-time webcam-based detection and recognition
├── video_processor.py # Processes uploaded video files
├── database.py # MySQL connection, logging, and record management
├── dashboard.py # Streamlit dashboard — Analytics, Filters, video upload
├── requirements.txt # Python Dependencies
└── README.md


---

## ⚙️ Getting Started

```bash
# 1. Navigate into the project folder
cd IdentiTrack

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your database credentials
# Create a .env file in the root folder:
echo DB_PASSWORD=your_mysql_password > .env

# 5. Create the MySQL database and table
```
```sql
CREATE DATABASE identitrack_db;
USE identitrack_db;

CREATE TABLE detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_name VARCHAR(100),
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
```bash
# 6. Add reference photos to gallery/<PersonName>/, then enroll
python enrollment.py

# 7. Run live tracking
python tracker.py

# 8. Launch the analytics dashboard
streamlit run dashboard.py
```

---

## 📊 Future Scope

- Multi-Camera Support for Simultaneous Feeds.
- Real-Time Alerting for Specific Individuals.
- Docker-based Deployment For Production Environments.
- Segmentation-Based Detection For Improved Accuracy in Crowded Scenes.
- Scheduled Automated Reporting (Daily/Weekly summaries).

---

## 👨‍💻 Author

**Abhay Marwade**
Aspiring Data Analyst | Data Science & AI Enthusiast

🔗 GitHub: [ABHAYMARWADE2004](https://github.com/ABHAYMARWADE2004)
