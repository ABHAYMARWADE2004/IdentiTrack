# 🎯 IdentiTrack — AI-Based Person Re-Identification & Tracking System

IdentiTrack is a Real-Time Person Re-Identification System That Enrolls Individuals From a Photo Gallery And Automatically Recognizes Them Via Live Webcam Feed Or Uploaded Video, Logging Every Detection To a Database With a Live Analytics Dashboard.

## 🚀 Features

- **Face Enrollment** — Register People Using Reference Photos Stored In a Gallery Folder
- **Two-Stage Detection Pipeline** — YOLOv8 Detects The Presence of a Person in Each Frame, Then Face Recognition Identifies Who It Is — So a Person is Still Flagged as detected Even When Their Face Isn't Visible (Turned away, Partial angle)
- **Real-Time Face Recognition** — Detects and identifies enrolled individuals via webcam using deep learning face embeddings
- **Video File Processing** — Upload a recorded video and run the full detection pipeline on it, with a browser-playable, downloadable output video
- **Smart Deduplication** — Cooldown-based logic prevents redundant database entries for continuously visible individuals
- **MySQL Database Integration** — Every detection is logged with person name and timestamp
- **Live Analytics Dashboard** — Built with Streamlit, showing total detections, unique people, peak activity hours, and detection trends
- **Filtering & Export** — Filter records by person and date, and export results as CSV
- **Data Management** — Clear all detection records from the dashboard for a fresh start
- **Secure Configuration** — Database credentials stored in a `.env` file, excluded from version control

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10 |
| Person Detection | YOLOv8 (Ultralytics) |
| Face Recognition | `face_recognition` (dlib-based) |
| Video Processing | OpenCV, imageio (H.264 encoding) |
| Database | MySQL |
| Dashboard | Streamlit |
| Data Handling | Pandas |
| Configuration | python-dotenv |

## 📁 Project Structure

IdentiTrack/
├── gallery/ # Reference photos for enrollment, organized by person name
│ └── PersonName/
│ ├── photo1.jpg
│ └── photo2.jpg
├── config.py # Central Configuration (loads secrets from .env)
├── enrollment.py # Extracts face encodings from gallery photos
├── tracker.py # Real-time Webcam-based detection and recognition
├── video_processor.py # Processes Uploaded Video Files
├── database.py # MySQL Connection, logging, and Record Management
├── dashboard.py # Streamlit dashboard — analytics, filters, video upload
├── requirements.txt # Python dependencies
├── .env # Database Credentials (not committed to version control)
├── .gitignore # Excludes venv, .env, And Generated Files
└── README.md


## ⚙️ How It Works

1. **Enrollment**: Photos placed in `gallery/<PersonName>/` Are Processed by `enrollment.py`, which extracts a unique facial embedding (128-dimension vector) for each photo and stores it in `encodings.pkl`.
2. **Person Detection**: `tracker.py` (live) or `video_processor.py` (uploaded video) runs each frame through YOLOv8, which detects all people present, regardless of whether their face is visible.
3. **Face Matching**: For each detected person, the cropped region is Checked for a face; if found, it's compared against the stored encodings Using distance-based matching to Identify who it is.
4. **Logging**: When a known face is matched, `database.py` inserts a Record into MySQL — with cooldown logic to avoid duplicate entries within a short time window.
5. **Visualization**: `dashboard.py` reads from the database and Presents detection statistics, filterable records, time-based Analytics, and an interface to Upload and Process video files.

## 🔧 Setup Instructions

1. Navigate into the project folder
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up a MySQL database and create a `.env` file with:
DB_PASSWORD=your_mysql_password
6. Create the `detections` table:
```sql
   CREATE TABLE detections (
       id INT AUTO_INCREMENT PRIMARY KEY,
       person_name VARCHAR(100),
       detected_at DATETIME DEFAULT CURRENT_TIMESTAMP
   );
```
7. Add reference photos to `gallery/<PersonName>/`
8. Run enrollment: `python enrollment.py`
9. Start live tracking: `python tracker.py`
10. Launch dashboard: `streamlit run dashboard.py`

## 📊 Future Scope

- Multi-Camera Support
- Alert/Notification System For Specific Individuals
- Deployment Via Docker For Production Use
- Advanced ID-switch Handling for Crowded/Occluded Scenes Using Segmentation-Based Detection
- Automated Scheduled Reports (Daily/Weekly Summaries)

## 👤 Author

Built by Abhay as a Learning Project in computer vision and real-time data pipelines — applying data Analysis and Data science Thinking to Unstructured Data Sources Like Video and Images.