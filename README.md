# 🎯 IdentiTrack

### AI-Powered Person Re-Identification & Real-Time Tracking System

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)](https://opencv.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple.svg)](https://ultralytics.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)
[![MySQL](https://img.shields.io/badge/MySQL-Database-orange.svg)](https://www.mysql.com/)

IdentiTrack Is an End-To-End Computer Vision System That Enrolls Individuals From Reference Photos And Automatically Detects And Identifies Them in Real Time — Via Live Webcam Or Uploaded Video — While Logging Every Detection To a Database And Surfacing Insights Through An Interactive Analytics Dashboard.

Built As a Hands-On Deep Dive Into Computer Vision, Real-Time Systems And Data Analytics — Combining A Two-stage AI Detection Pipeline With a Full Data Logging And Visualization Layer.

---

## 🔑 Highlights

- **Two-Stage Detection Pipeline** — YOLOv8 For Person Detection + Face Recognition For Identity Matching, So Presence Is Detected Even When a Face isn't Visible
- **Dual Input Modes** — Real-Time webcam tracking *and* Uploaded video File Processing
- **Full Data Pipeline** — From Raw Video Frames → Structured MySQL Records → Interactive Analytics Dashboard
- **Production-Conscious Design** — Cooldown-Based Deduplication, Secure Credential Handling Via `.env`, And a Clean Modular Codebase

---

## 🚀 Features

| Feature | Description |
|---|---|
| 👤 **Face Enrollment** | Register Individuals From Reference Photos Organized By Name |
| 🎯 **Two-Stage Detection** | YOLOv8 Detects *presence*, face Recognition Confirms *identity* |
| 📹 **Live Webcam Tracking** | Real-time Detection And recognition with on-screen Bounding Boxes |
| 🎬 **Video File Processing** | Upload any Video And Run The Full Detection Pipeline On It |
| 🗄️ **Database Logging** | Every Detection Logged To MySQL With Cooldown-Based Deduplication |
| 📊 **Analytics Dashboard** | Peak-Hour Trends, Per-person counts, Date-Wise Activity, CSV Export |
| 🔍 **Filtering** | Filter Detection Records By Person And By Date |
| 🔒 **Secure Config** | Credentials Managed Via `.env`, Excluded From Version Control |

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


1. **Enrollment**: Reference Photos in `gallery/<PersonName>/` Are Converted Into 128-Dimension Facial Embeddings Via `enrollment.py` And Stored In `encodings.pkl`.
2. **Detection**: Each Frame (from webcam or video) is Passed Through YOLOv8, Which Locates Every Person Present — Regardless Of Whether Their Face Is Visible.
3. **Recognition**: The Cropped Region For Each Detected Person Is Checked For a Face; If Found, It's Matched Against Stored Encodings Using Distance-Based Comparison.
4. **Logging**: Matched Detections Are Inserted Into MySQL, With Cooldown Logic Preventing Duplicate Entries For a Continuously Visible Person.
5. **Visualization**: The Streamlit Dashboard Reads Live From The Database To Surface Detection Counts, Peak Activity Hours, Trends And Exportable Records.


## 📁 Project Structure

```
IdentiTrack/
├── gallery/                  # photos of people to enroll, one folder per person
├── config.py                 # all the settings in one place (DB creds come from .env)
├── enrollment.py              # reads gallery photos, saves face encodings
├── tracker.py                  # live webcam tracking - the main detection loop
├── video_processor.py           # same detection logic, but for uploaded videos
├── database.py                   # all the MySQL stuff - save, fetch, clear
├── dashboard.py                   # the Streamlit app - charts, filters, everything
├── requirements.txt                # pip install -r this and you're set
└── README.md
```

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

There's a lot of Advanced stuff I intentionally didn't build into this version — things like 
handling cases where two people cross paths and the system has to figure out who's who, which 
is honestly a whole research area on its own. For this project, I focused on getting a complete, 
understandable pipeline working end-to-end rather than a half-built complex one. A few things 
I'd like to add going forward:

- Support for multiple camera feeds running at once
- Real-time alerts when a specific person is detected
- Docker-based deployment for a more production-ready setup
- Better handling of crowded scenes using segmentation-based detection
- Automated daily/weekly summary reports

## 👨‍💻 Author

**Abhay Marwade**

Aspiring Data Analyst | Data Science & AI Enthusiast

🔗 GitHub: [ABHAYMARWADE2004](https://github.com/ABHAYMARWADE2004)
