# dashboard.py
# IdentiTrack ka main dashboard - analytics, filters, video upload, sab kuch yahin hai

import streamlit as st
import pandas as pd
from database import get_all_detections, clear_all_detections

st.set_page_config(page_title="IdentiTrack Dashboard", page_icon="🎯", layout="wide")

# ===== Custom Styling (Dashboard ko professional look dene ke liye) =====
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background-color: #1A1D29;
        border: 1px solid #2D3142;
        padding: 15px;
        border-radius: 10px;
    }
    h2, h3 {
        color: #FF4B8B;
    }
    .stButton>button {
        border-radius: 8px;
        border: 1px solid #FF4B8B;
    }
</style>
""", unsafe_allow_html=True)

# ===== Title Section =====
st.markdown("""
<div style="text-align: center; padding: 10px 0 30px 0;">
    <h1 style="font-size: 42px; margin-bottom: 0;">🎯 IdentiTrack</h1>
    <p style="font-size: 16px; color: #999;">AI-Powered Person Re-Identification & Real-Time Analytics</p>
</div>
""", unsafe_allow_html=True)

# ===== Sidebar: Clear Records Option =====
with st.sidebar:
    st.header("⚙️ Settings")
    st.write("Saare records delete karke fresh start karo")
    if st.button("🗑️ Clear All Records", type="secondary"):
        clear_all_detections()
        st.success("Saare records delete ho gaye!")
        st.rerun()

records = get_all_detections()

if len(records) == 0:
    st.warning("Abhi tak koi detection record nahi hai. Pehle tracker.py chalao.")
else:
    df = pd.DataFrame(records, columns=["Name", "Detected At"])
    df["Detected At"] = pd.to_datetime(df["Detected At"])
    df["Date"] = df["Detected At"].dt.date
    df["Hour"] = df["Detected At"].dt.hour

    # ===== Top Stats =====
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Detections", len(df))

    with col2:
        unique_people = df["Name"].nunique()
        st.metric("Unique People", unique_people)

    with col3:
        latest_detection = df["Detected At"].iloc[0]
        st.metric("Latest Detection", str(latest_detection))

    with col4:
        busiest_hour = df["Hour"].mode()[0]
        st.metric("Peak Hour", f"{busiest_hour}:00")

    st.divider()

    # ===== Filters (Name + Date) =====
    st.subheader("🔍 Filter Karo")

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        all_names = ["Sabhi"] + list(df["Name"].unique())
        selected_name = st.selectbox("Naam se filter karo:", all_names)

    with filter_col2:
        all_dates = ["Sabhi Dates"] + sorted([str(d) for d in df["Date"].unique()], reverse=True)
        selected_date = st.selectbox("Date se filter karo:", all_dates)

    filtered_df = df.copy()

    if selected_name != "Sabhi":
        filtered_df = filtered_df[filtered_df["Name"] == selected_name]

    if selected_date != "Sabhi Dates":
        filtered_df = filtered_df[filtered_df["Date"].astype(str) == selected_date]

    # ===== Table =====
    st.subheader("📋 Detection Records")
    st.dataframe(filtered_df[["Name", "Detected At"]], use_container_width=True)

    # ===== CSV Download =====
    csv_data = filtered_df[["Name", "Detected At"]].to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv_data,
        file_name="identitrack_detections.csv",
        mime="text/csv"
    )

    st.divider()

    # ===== Analytics Section =====
    st.subheader("📊 Analytics")

    col_a, col_b = st.columns(2)

    with col_a:
        st.write("**Person-wise Detection Count**")
        chart_data = filtered_df["Name"].value_counts()
        st.bar_chart(chart_data)

    with col_b:
        st.write("**Hour-wise Activity (Peak Hours)**")
        hourly_data = filtered_df.groupby("Hour").size().reset_index(name="Detections")
        hourly_data = hourly_data.set_index("Hour")
        st.bar_chart(hourly_data)

    st.write("**Date-wise Detection Trend**")
    daily_data = filtered_df.groupby("Date").size().reset_index(name="Detections")
    daily_data["Date"] = daily_data["Date"].astype(str)
    daily_data = daily_data.set_index("Date")
    st.bar_chart(daily_data)

    # ===== Duration & Visit Tracking =====
    st.divider()
    st.subheader("⏱️ Duration & Visit Analysis")
    st.write("Har banda kitni baar 'visit' kiya, aur kitni der screen pe raha (session-based calculation)")

    SESSION_GAP_MINUTES = 2

    df_sorted = df.sort_values(["Name", "Detected At"]).copy()
    df_sorted["Time Gap"] = df_sorted.groupby("Name")["Detected At"].diff().dt.total_seconds()
    df_sorted["New Session"] = (df_sorted["Time Gap"].isna()) | (df_sorted["Time Gap"] > SESSION_GAP_MINUTES * 60)
    df_sorted["Session ID"] = df_sorted.groupby("Name")["New Session"].cumsum()

    sessions = df_sorted.groupby(["Name", "Session ID"]).agg(
        Start=("Detected At", "min"),
        End=("Detected At", "max")
    ).reset_index()

    sessions["Duration (sec)"] = (sessions["End"] - sessions["Start"]).dt.total_seconds()

    summary = sessions.groupby("Name").agg(
        Total_Visits=("Session ID", "count"),
        Total_Duration_Sec=("Duration (sec)", "sum")
    ).reset_index()

    summary["Total Duration (min)"] = (summary["Total_Duration_Sec"] / 60).round(2)
    summary = summary.rename(columns={"Name": "Person", "Total_Visits": "Total Visits"})

    st.dataframe(summary[["Person", "Total Visits", "Total Duration (min)"]], use_container_width=True)

    # ===== Video Upload Section =====
    st.divider()
    st.subheader("🎥 Video Upload & Processing")
    st.write("Koi bhi video file upload karo, system usme se logo ko detect aur pehchanega")

    uploaded_file = st.file_uploader("Video choose karo", type=["mp4", "avi", "mov"])

    if uploaded_file is not None:
        temp_input_path = "temp_input_video.mp4"
        with open(temp_input_path, "wb") as f:
            f.write(uploaded_file.read())

        if st.button("🚀 Process Video"):
            with st.spinner("Video process ho rahi hai... thoda time lagega"):
                from video_processor import process_video
                output_path, frame_count = process_video(temp_input_path)

            st.success(f"Video process ho gayi! Total {frame_count} frames process hue.")

            with open(output_path, "rb") as f:
                video_bytes = f.read()

            st.video(video_bytes)

            st.download_button(
                label="📥 Download Processed Video",
                data=video_bytes,
                file_name="identitrack_processed.mp4",
                mime="video/mp4"
            )