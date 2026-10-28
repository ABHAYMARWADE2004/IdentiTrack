🎯 IdentiTrack
Intelligent Person Detection, Recognition & Analytics System
PythonOpenCVYOLOv8StreamlitMySQL

📌 About The Project
I built IdentiTrack to understand how a complete computer vision system works in practice.

Most projects stop after detecting or recognizing a person. I wanted to build something more practical that could identify people, store detection records in a database, and generate useful insights through a dashboard.

With IdentiTrack, a person can be enrolled using a few photos. Once enrolled, the system can recognize them from a live webcam feed or a recorded video. Every detection is stored in MySQL, and the dashboard helps visualize trends such as peak activity hours, detection history, and person-wise records.

This project helped me combine Computer Vision, Database Management, and Data Analytics into a single workflow.

🚀 Features

👤 Face Enrollment
🎯 YOLOv8 Person Detection
😀 Face Recognition
📹 Live Webcam Tracking
🎬 Video File Processing
🗄️ MySQL Logging
📊 Streamlit Analytics Dashboard
📅 Filter by Date or Person
📤 CSV Export
🔁 Duplicate Detection Prevention

🛠️ Tech Stack
Category	Technology
Language	Python 3.10
Detection	YOLOv8
Face Recognition	face_recognition (dlib)
Video Processing	OpenCV
Database	MySQL
Dashboard	Streamlit
Analytics	Pandas
Configuration	python-dotenv

⚙️ How It Works
Step 1: Enroll Faces
Add a few images inside:

gallery/PersonName/
Run:

python enrollment.py
The system extracts facial features and saves them as face encodings.

Step 2: Detect People
YOLOv8 scans each frame from a webcam or video and detects people.

Step 3: Recognize Faces
If a face is visible, the system matches it against enrolled faces and identifies the person.

Step 4: Save Records
Every successful detection is stored in MySQL.

A cooldown mechanism prevents duplicate entries from being logged repeatedly.

Step 5: Analyze Data
The Streamlit dashboard reads database records and shows:

Detection history
Peak activity hours
Person-wise statistics
Daily trends
Exportable reports

🔄 Workflow
Gallery Images
      │
      ▼
Face Enrollment
      │
      ▼
Face Encodings
      │
      ▼
Webcam / Video Input
      │
      ▼
YOLOv8 Detection
      │
      ▼
Face Recognition
      │
      ▼
MySQL Logging
      │
      ▼
Streamlit Dashboard
      │
      ▼
Analytics & Insights

📁 Project Structure
IdentiTrack/
│
├── gallery/
├── config.py
├── database.py
├── enrollment.py
├── tracker.py
├── video_processor.py
├── dashboard.py
├── requirements.txt
└── README.md

🔧 Setup
Clone the Repository
git clone https://github.com/ABHAYMARWADE2004/IdentiTrack.git

cd IdentiTrack
Create a Virtual Environment
python -m venv venv
Activate it:

venv\Scripts\activate
Install Dependencies
pip install -r requirements.txt

pip install face_recognition --no-deps
Create a .env File
DB_PASSWORD=your_mysql_password
Create the Database
CREATE DATABASE identitrack_db;

USE identitrack_db;

CREATE TABLE detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_name VARCHAR(100),
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
Generate Face Encodings
python enrollment.py
Start Live Tracking
python tracker.py
Launch Dashboard
streamlit run dashboard.py

📚 What I Learned
This project helped me gain hands-on experience with:

Computer Vision
Face Recognition
YOLOv8
Database Integration
Data Analytics
Real-Time Video Processing
Streamlit Dashboard Development
More importantly, it taught me how different technologies work together to create a complete solution instead of just a standalone model.

🔮 Future Improvements
Multiple camera support
Email alerts for detections
Docker deployment
Cloud deployment
Better tracking in crowded scenes
Automated reports

👨‍💻 Author
Abhay Marwade
Aspiring Data Analyst | Data Science & AI Enthusiast

🔗 GitHub: https://github.com/ABHAYMARWADE2004

🔗 LinkedIn: https://www.linkedin.com/in/abhay-marwade-681108295

⭐ If you found this project interesting, feel free to give it a star.