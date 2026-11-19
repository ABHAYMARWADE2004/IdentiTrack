"""IdentiTrack dashboard: analytics, visit/dwell analysis, records and video upload.

    streamlit run dashboard.py
"""

import os
import tempfile
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

import analytics
import config
from database import clear_detections, fetch_detections, init_db

st.set_page_config(page_title="IdentiTrack", page_icon="🎯", layout="wide")

st.markdown(
    """
    <style>
        [data-testid="stMetric"] {
            background-color: #1A1D29; border: 1px solid #2D3142;
            padding: 15px; border-radius: 10px;
        }
        h2, h3 { color: #FF4B8B; }
        .stButton>button { border-radius: 8px; border: 1px solid #FF4B8B; }
    </style>
    <div style="text-align:center; padding: 6px 0 24px 0;">
        <h1 style="font-size: 40px; margin-bottom: 0;">🎯 IdentiTrack</h1>
        <p style="font-size: 16px; color: #999;">
            Person Detection &amp; Face Recognition Analytics
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- data access
@st.cache_data(ttl=10, show_spinner=False)
def load_records():
    return fetch_detections()


@st.cache_resource(show_spinner="Loading detection and recognition models...")
def get_recognizer():
    from recognizer import PersonRecognizer   # heavy import, only when needed
    return PersonRecognizer()


def refresh():
    load_records.clear()


try:
    raw = load_records()
except Exception as exc:  # noqa: BLE001
    st.error(f"Could not read from MySQL: {exc}")
    st.write("Check your `.env` (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME) and that MySQL is running. "
             "If this is a fresh install, create the database and table first:")
    if st.button("Initialize database"):
        try:
            init_db()
            refresh()
            st.success("Database initialised. Reload the page.")
        except Exception as inner:  # noqa: BLE001
            st.error(f"Initialisation failed: {inner}")
    st.stop()

df_all = analytics.prepare(raw) if not raw.empty else raw

# -------------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("🔍 Filters")
    df = df_all

    if not df_all.empty:
        source_choice = st.radio("Data source", ["All", "Live camera", "Uploaded video"])
        if source_choice == "Live camera":
            df = df[df["source"] == "live"]
        elif source_choice == "Uploaded video":
            df = df[df["source"] == "video"]

        names = sorted(df["source_name"].dropna().unique())
        if names:
            chosen_sources = st.multiselect("Camera / video", names, default=names)
            df = df[df["source_name"].isin(chosen_sources) | df["source_name"].isna()]

        people = sorted(df["person_name"].unique())
        chosen_people = st.multiselect("People", people, default=people)
        df = df[df["person_name"].isin(chosen_people)]

        if not df.empty:
            lo, hi = df["date"].min(), df["date"].max()
            picked = st.date_input("Date range", value=(lo, hi), min_value=lo, max_value=hi)
            if isinstance(picked, (tuple, list)) and len(picked) == 2:
                df = df[(df["date"] >= picked[0]) & (df["date"] <= picked[1])]

    st.header("⏱️ Visit settings")
    gap_minutes = st.slider("New visit after a gap of (minutes)", 1, 30,
                            config.SESSION_GAP_MINUTES)

    st.header("⚙️ Data")
    if st.button("🔄 Refresh"):
        refresh()
        st.rerun()
    with st.expander("Danger zone"):
        scope = st.selectbox("Delete", ["All records", "Live only", "Video only"])
        confirm = st.checkbox("I understand this cannot be undone")
        if st.button("🗑️ Delete records", disabled=not confirm):
            deleted = clear_detections({"All records": None, "Live only": "live",
                                        "Video only": "video"}[scope])
            refresh()
            st.success(f"Deleted {deleted} record(s).")
            st.rerun()

tab_analytics, tab_visits, tab_records, tab_video = st.tabs(
    ["📊 Analytics", "⏱️ Visits & Dwell Time", "📋 Records", "🎥 Process Video"]
)

# ------------------------------------------------------------------ analytics
with tab_analytics:
    if df.empty:
        st.info("No detection records match the current filters. "
                "Run `python tracker.py`, or process a video in the last tab.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total detections", f"{len(df):,}")
        c2.metric("Unique people", df["person_name"].nunique())
        c3.metric("Latest detection", df["detected_at"].max().strftime("%d %b %H:%M"))
        c4.metric("Peak hour", f"{analytics.peak_hour(df):02d}:00")
        st.divider()

        left, right = st.columns(2)
        with left:
            per_person = df["person_name"].value_counts().rename_axis("Person").reset_index(name="Detections")
            st.plotly_chart(px.bar(per_person, x="Person", y="Detections",
                                   title="Detections per person"))
        with right:
            st.plotly_chart(px.bar(analytics.hourly_counts(df), x="hour", y="detections",
                                   title="Activity by hour of day",
                                   labels={"hour": "Hour", "detections": "Detections"}))

        st.plotly_chart(px.line(analytics.daily_counts(df), x="date", y="detections",
                                markers=True, title="Daily detections"))

        matrix = analytics.weekday_hour_matrix(df)
        st.plotly_chart(px.imshow(matrix, aspect="auto", color_continuous_scale="Magma",
                                  labels=dict(x="Hour", y="Weekday", color="Detections"),
                                  title="When is activity highest? (weekday × hour)"))

# --------------------------------------------------------------------- visits
with tab_visits:
    st.caption(
        "A *visit* is a run of detections for one person with no gap longer than the "
        "setting in the sidebar. Detections are logged at most once per "
        f"{config.COOLDOWN_SECONDS}s, so each one is treated as ~{config.COOLDOWN_SECONDS}s of "
        "presence. Durations are **estimates**, not exact measurements."
    )
    if df.empty:
        st.info("No data for the current filters.")
    else:
        sessions = analytics.sessionize(df, gap_minutes=gap_minutes)
        st.dataframe(analytics.visit_summary(sessions), hide_index=True)

        timeline = sessions.assign(
            end_padded=sessions["start"] + pd.to_timedelta(sessions["duration_sec"], unit="s")
        )
        st.plotly_chart(px.timeline(timeline, x_start="start", x_end="end_padded",
                                    y="person_name", color="person_name",
                                    title="Visit timeline",
                                    labels={"person_name": "Person"}))

# -------------------------------------------------------------------- records
with tab_records:
    if df.empty:
        st.info("No records to show.")
    else:
        show = df[["person_name", "detected_at", "match_distance", "source",
                   "source_name", "video_offset_sec"]].rename(columns={
            "person_name": "Person", "detected_at": "Detected at",
            "match_distance": "Match distance", "source": "Source",
            "source_name": "Camera / video", "video_offset_sec": "Video offset (s)"})
        st.dataframe(show, hide_index=True)
        st.download_button("📥 Download as CSV", show.to_csv(index=False),
                           file_name="identitrack_detections.csv", mime="text/csv")
        st.caption("Match distance: lower means the face was closer to the enrolled photo "
                   f"(a match is accepted at ≤ {config.FACE_MATCH_TOLERANCE}).")

# ---------------------------------------------------------------------- video
with tab_video:
    st.write("Upload a recording. People are detected, identified and logged using their "
             "position in the video, so the analytics stay meaningful however fast it is processed.")

    if not os.path.exists(config.ENCODINGS_FILE):
        st.warning("No enrolled faces yet. Add photos to `gallery/<PersonName>/` and run "
                   "`python enrollment.py` first.")

    upload = st.file_uploader("Choose a video", type=["mp4", "avi", "mov"])
    c1, c2, c3 = st.columns(3)
    start_date = c1.date_input("Recording date", value=datetime.now().date())
    start_clock = c2.time_input("Recording start time", value=datetime.now().replace(
        second=0, microsecond=0).time())
    save_rows = c3.checkbox("Save detections to database", value=True)

    if upload is not None and st.button("🚀 Process video"):
        from video_processor import process_video

        suffix = os.path.splitext(upload.name)[1] or ".mp4"
        with tempfile.TemporaryDirectory() as tmp:
            in_path = os.path.join(tmp, f"input{suffix}")
            out_path = os.path.join(tmp, "processed.mp4")
            with open(in_path, "wb") as f:
                f.write(upload.getbuffer())

            bar = st.progress(0.0, text="Processing...")

            def on_progress(done, total):
                frac = min(done / total, 1.0) if total else 0.0
                bar.progress(frac, text=f"Processing... {done}/{total or '?'} frames")

            try:
                result = process_video(
                    in_path, out_path, source_name=upload.name,
                    start_time=datetime.combine(start_date, start_clock),
                    save_to_db=save_rows, recognizer=get_recognizer(),
                    progress_callback=on_progress,
                )
            except Exception as exc:  # noqa: BLE001
                st.error(f"Processing failed: {exc}")
                st.stop()

            bar.empty()
            refresh()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Frames", f"{result.frames:,}")
            m2.metric("Video length", f"{result.video_seconds:.0f}s")
            m3.metric("Speed", f"{result.effective_fps:.1f} FPS")
            m4.metric("Detections logged", result.logged)
            if result.people:
                st.write("**Recognised:** " + ", ".join(f"{k} ({v})" for k, v in result.people.items()))
            else:
                st.info("No enrolled person was recognised in this video.")
            if result.unknown_faces:
                st.caption(f"{result.unknown_faces} unknown-face sighting(s) were not logged.")

            with open(result.output_path, "rb") as f:
                video_bytes = f.read()
            st.video(video_bytes)
            st.download_button("📥 Download processed video", video_bytes,
                               file_name="identitrack_processed.mp4", mime="video/mp4")
