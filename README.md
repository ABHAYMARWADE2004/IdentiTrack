🎯 IdentiTrack
Intelligent Person Detection, Recognition & Analytics System
PythonOpenCVYOLOv8StreamlitMySQL

About The Project
I built IdentiTrack to understand how a complete computer vision system works in practice.

Most projects stop after detecting or recognizing a person. I wanted to go a step further and build a system that could identify people, store detection records in a database, and show useful insights through a dashboard.

With IdentiTrack, a person can be enrolled using a few photos. Once enrolled, the system can recognize them from a live webcam feed or a recorded video. Every detection is stored in MySQL, and the dashboard helps visualize patterns such as activity trends, peak hours, and detection history.

This project helped me combine Computer Vision, Database Management, and Data Analytics into a single workflow.

🚀 What It Can Do
Detect people using YOLOv8
Recognize enrolled faces
Work with live webcam feeds
Process recorded video files
Store detection records in MySQL
Avoid duplicate logging using cooldown logic
View analytics in a Streamlit dashboard
Filter records by person or date
Export data as CSV
🛠️ Tech Stack
Python 3.10
YOLOv8
OpenCV
face_recognition (dlib)
MySQL
Streamlit
Pandas
python-dotenv
⚙️ How It Works
Step 1: Enroll Faces
Add a few images inside:

gallery/PersonName/
Run:

python enrollment.py
The system extracts facial features and stores them as encodings.

Step 2: Detect People
When a webcam feed or video is processed, YOLOv8 looks for people in every frame.

Step 3: Recognize Faces
If a face is visible, the system compares it with enrolled faces and identifies the person.

Step 4: Save Records
Each successful detection is stored in MySQL.

A cooldown mechanism prevents the same person from being logged repeatedly.

Step 5: Analyze Data
The Streamlit dashboard reads data from the database and shows:

Detection history
Peak activity hours
Person-wise statistics
Daily trends
Exportable reports
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
Working on this project helped me gain hands-on experience with:

Computer Vision
Face Recognition
YOLOv8
Database Integration
Data Analytics
Real-Time Video Processing
Streamlit Dashboard Development
More importantly, it taught me how different technologies can work together to build a complete solution instead of just an isolated model.

🔮 Future Improvements
Some improvements I would like to add in the future:

Multiple camera support
Email alerts for detections
Docker deployment
Cloud hosting
Better tracking in crowded scenes
Automated reports
👨‍💻 Author
Abhay Marwade
Aspiring Data Analyst | Data Science & AI Enthusiast

GitHub: https://github.com/ABHAYMARWADE2004
LinkedIn: https://www.linkedin.com/in/abhay-marwade-681108295
⭐ If you found this project interesting, feel free to give it a star.