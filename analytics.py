"""Analytics on detection records. Pure pandas: no database, no OpenCV.

Keeping this separate from the dashboard makes it unit-testable.
"""

import pandas as pd

import config

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def prepare(df):
    """Add Date / Hour / Weekday columns and make sure timestamps are datetimes."""
    out = df.copy()
    out["detected_at"] = pd.to_datetime(out["detected_at"])
    out["date"] = out["detected_at"].dt.date
    out["hour"] = out["detected_at"].dt.hour
    out["weekday"] = out["detected_at"].dt.dayofweek.map(dict(enumerate(WEEKDAYS)))
    return out


def sessionize(df, gap_minutes=config.SESSION_GAP_MINUTES,
               presence_pad_seconds=config.COOLDOWN_SECONDS):
    """Group each person's detections into visits.

    A new visit starts when the gap since that person's previous detection is
    larger than ``gap_minutes``.

    Because the logger only writes a row every COOLDOWN seconds, a person seen
    exactly once would otherwise get a duration of 0. Each detection therefore
    represents roughly one cooldown window of presence, so the estimated
    duration is ``(last - first) + presence_pad_seconds``. It is an estimate,
    not a measurement.
    """
    columns = ["person_name", "session", "start", "end", "detections", "duration_sec"]
    if df.empty:
        return pd.DataFrame(columns=columns)

    d = df.sort_values(["person_name", "detected_at"]).copy()
    gap = d.groupby("person_name")["detected_at"].diff().dt.total_seconds()
    d["new_session"] = gap.isna() | (gap > gap_minutes * 60)
    d["session"] = d.groupby("person_name")["new_session"].cumsum()

    sessions = (
        d.groupby(["person_name", "session"])
        .agg(start=("detected_at", "min"),
             end=("detected_at", "max"),
             detections=("detected_at", "size"))
        .reset_index()
    )
    sessions["duration_sec"] = (
        (sessions["end"] - sessions["start"]).dt.total_seconds() + presence_pad_seconds
    )
    return sessions[columns]


def visit_summary(sessions):
    """One row per person: visits, total / average duration, first and last seen."""
    if sessions.empty:
        return pd.DataFrame(columns=[
            "Person", "Visits", "Total minutes", "Avg visit (min)", "First seen", "Last seen",
        ])
    summary = (
        sessions.groupby("person_name")
        .agg(Visits=("session", "count"),
             total_sec=("duration_sec", "sum"),
             avg_sec=("duration_sec", "mean"),
             first=("start", "min"),
             last=("end", "max"))
        .reset_index()
    )
    summary["Total minutes"] = (summary["total_sec"] / 60).round(2)
    summary["Avg visit (min)"] = (summary["avg_sec"] / 60).round(2)
    summary = summary.rename(columns={
        "person_name": "Person", "first": "First seen", "last": "Last seen",
    })
    return summary[["Person", "Visits", "Total minutes", "Avg visit (min)",
                    "First seen", "Last seen"]].sort_values("Total minutes", ascending=False)


def peak_hour(df):
    """Most common hour of day, or None when there is no data."""
    if df.empty:
        return None
    return int(df["hour"].mode().iloc[0])


def hourly_counts(df):
    """Detections per hour of day, including hours with zero detections."""
    counts = df.groupby("hour").size().reindex(range(24), fill_value=0)
    return counts.rename("detections").reset_index()


def daily_counts(df):
    return df.groupby("date").size().rename("detections").reset_index()


def weekday_hour_matrix(df):
    """Weekday x hour matrix of detection counts (for a heatmap)."""
    matrix = (
        df.groupby(["weekday", "hour"]).size().unstack(fill_value=0)
        .reindex(index=WEEKDAYS, columns=range(24), fill_value=0)
    )
    return matrix
