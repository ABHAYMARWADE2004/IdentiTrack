import pandas as pd
import pytest

import analytics


def make(rows):
    return analytics.prepare(pd.DataFrame(rows, columns=["person_name", "detected_at"]))


def test_sessionize_splits_on_gap_and_pads_duration():
    df = make([
        ("Asha", "2026-11-19 09:00:00"),
        ("Asha", "2026-11-19 09:00:15"),
        ("Asha", "2026-11-19 09:00:30"),
        ("Asha", "2026-11-19 09:10:00"),   # > 2 min later -> second visit
        ("Ravi", "2026-11-19 09:05:00"),
    ])
    s = analytics.sessionize(df, gap_minutes=2, presence_pad_seconds=15)
    asha = s[s.person_name == "Asha"].sort_values("start")
    assert len(asha) == 2
    assert asha.iloc[0]["detections"] == 3
    assert asha.iloc[0]["duration_sec"] == 30 + 15
    assert asha.iloc[1]["duration_sec"] == 15            # single sighting, not 0
    assert len(s[s.person_name == "Ravi"]) == 1


def test_sessionize_empty():
    s = analytics.sessionize(make([]))
    assert s.empty and "duration_sec" in s.columns


def test_visit_summary_totals():
    df = make([("A", "2026-11-19 09:00:00"), ("A", "2026-11-19 09:01:00")])
    summary = analytics.visit_summary(analytics.sessionize(df, 2, 0))
    row = summary.iloc[0]
    assert row["Visits"] == 1 and row["Total minutes"] == 1.0


def test_hourly_counts_fills_missing_hours():
    df = make([("A", "2026-11-19 09:00:00"), ("A", "2026-11-19 09:30:00")])
    h = analytics.hourly_counts(df)
    assert len(h) == 24 and h.loc[h.hour == 9, "detections"].iloc[0] == 2
    assert analytics.peak_hour(df) == 9


def test_weekday_matrix_shape():
    df = make([("A", "2026-11-19 09:00:00")])   # a Thursday
    m = analytics.weekday_hour_matrix(df)
    assert m.shape == (7, 24) and m.loc["Thu", 9] == 1
