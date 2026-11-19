# 🎯 IdentiTrack

Person detection and face recognition with an analytics layer: **YOLOv8** finds people,
**dlib face recognition** identifies enrolled faces, every sighting is logged to **MySQL**,
and a **Streamlit** dashboard turns the log into visit, dwell-time and peak-hour analytics.

> Built to learn how a computer-vision model becomes a complete system: capture → recognise →
> store → analyse → evaluate.

---

## How it works

```text
 webcam / video file
        │
        ▼
  YOLOv8 (person boxes)  ──►  face search in the head region of each box
                                   │
                                   ▼
                       128-d face encoding ──► nearest enrolled face
                                   │              (distance ≤ tolerance ?)
                       ┌───────────┴───────────┐
                    known                   unknown / no face
                       │                  (drawn, never stored)
                       ▼
        cooldown gate (one log per person per 15 s)
                       │
                       ▼
                 MySQL `detections`
                       │
                       ▼
     Streamlit dashboard: analytics · visits & dwell time · records · video upload
```

## Features

- Real-time recognition from a webcam (`tracker.py`) or recorded video (`video_processor.py`)
- One shared pipeline (`recognizer.py`) used by the tracker, video processor and dashboard
- **Cooldown logging** so a person standing in view isn't logged every frame
- **Video-time timestamps**: uploaded videos are logged by their position in the video, so
  analytics stay correct however fast the file is processed
- Frame skipping and head-region search to keep the live feed responsive; live FPS shown on screen
- Pooled MySQL connections, bulk inserts for video, and automatic schema upgrade
- Dashboard: filters (source, camera/video, person, date), daily trend, hour-of-day chart,
  weekday × hour heatmap, visit timeline, per-person visit and dwell-time summary, CSV export
- **`evaluate.py`**: measures recognition accuracy and false-accept rate on your own photos and
  recommends a match tolerance (see *Evaluation*)
- Unit and smoke tests (`pytest`)

## Setup

```bash
git clone https://github.com/ABHAYMARWADE2004/IdentiTrack.git
cd IdentiTrack
python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
pip install face_recognition --no-deps
```

Copy `.env.example` to `.env` and set your MySQL password. Then create the database/table
(either `schema.sql`, or):

```bash
python database.py
```

## Usage

```bash
# 1. Enrol people: put 5+ clear, varied, single-person photos in gallery/<PersonName>/
python enrollment.py

# 2a. Live camera (press q to quit)
python tracker.py --camera 0 --name Entrance

# 2b. ...or process a recording
python video_processor.py clip.mp4 --start "2026-11-19 09:00:00"

# 3. Dashboard (also lets you upload and process videos)
streamlit run dashboard.py
```

## Evaluation

A recognition system is only as good as its measured error rates, so the project includes a
script that measures them from photos:

```bash
python evaluate.py --unknown-dir eval/strangers --max-far 0.01
```

- **Leave-one-out on the gallery** – each photo is matched against all *other* enrolled photos
  → accuracy, false-reject rate, misidentification rate.
- **Strangers** (`--unknown-dir`, photos of people who are *not* enrolled) → **false-accept
  rate**, i.e. how often a stranger is given an enrolled person's name.
- Sweeps tolerances 0.40–0.65 and recommends the most accurate one that keeps the
  false-accept rate under your cap. Results are saved to `eval_results.csv`.

### My results

> Run `evaluate.py` on your own photos and record the numbers here (with N).

| Tolerance | Test photos (N) | Accuracy | False-reject | Strangers (N) | False-accept |
|---:|---:|---:|---:|---:|---:|
| _fill in_ | | | | | |

## Design decisions

| Decision | Why |
|---|---|
| Match tolerance 0.5 (library default is 0.6) | 0.6 is lenient and raises false matches; the value is configurable and chosen with `evaluate.py` |
| Timestamp video rows with `frame / fps` | Using processing time compresses a long video into seconds and ruins dwell/peak analytics |
| Search only the top 60 % of tall person boxes | The face is in the head area; faster and fewer false faces on clothing |
| Largest face per person box | Avoids matching background faces |
| Skip enrollment photos with several faces | Can't know which face belongs to the person |
| Unknown faces are drawn but never stored | Avoids accumulating biometric-adjacent data about unenrolled people |
| Visit duration = (last − first) + one cooldown window | Logs are ≥15 s apart, so a single sighting would otherwise have zero duration |

## Limitations

- Face recognition needs a reasonably frontal, well-lit face; people turned away are detected
  but shown as "Person" (not identified). Not a replacement for true person re-identification
  across cameras.
- Dwell time is an **estimate** from sampled logs, not a measurement.
- Accuracy depends heavily on gallery quality and lighting; report your own measured numbers.
- CPU-only dlib is slow on large frames; throughput is shown live and in the video summary.

## Privacy and ethics

Face data is biometric. Only enrol people who have given consent, keep `gallery/` and
`encodings.pkl` out of version control (they are git-ignored), and don't deploy this to track
people without a legal basis and clear notice. This project is for learning and demonstration.

## Project structure

```text
IdentiTrack/
├── config.py            # all settings (secrets via .env)
├── recognizer.py        # shared YOLO + face-recognition pipeline
├── tracker.py           # live webcam tracking
├── video_processor.py   # recorded-video processing
├── enrollment.py        # build face encodings from gallery/
├── evaluate.py          # accuracy / false-accept evaluation + tolerance recommendation
├── database.py          # pooled MySQL access, schema init/upgrade
├── analytics.py         # sessionization and aggregates (pure pandas)
├── dashboard.py         # Streamlit app
├── utils.py             # cooldown gate, fps helper
├── schema.sql
├── tests/               # pytest: analytics, cooldown, evaluation, video pipeline, dashboard
└── requirements.txt
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The video-pipeline test uses lightweight stand-ins for YOLO and dlib, so it runs anywhere
without a GPU, camera or database.

## Roadmap

- Multi-camera support and cross-camera person re-identification
- Email/webhook alerts, Docker deployment, cloud hosting
- Optional face-embedding index for large galleries

---

**Author:** Abhay Marwade · [GitHub](https://github.com/ABHAYMARWADE2004) ·
[LinkedIn](https://www.linkedin.com/in/abhay-marwade-681108295)
