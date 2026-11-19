"""Smoke test: the dashboard renders with data and with an empty database."""

import os
import sys
import types

import pandas as pd
from streamlit.testing.v1 import AppTest

DASHBOARD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard.py")
COLUMNS = ["id", "person_name", "detected_at", "match_distance",
           "source", "source_name", "video_offset_sec"]


def _install_fake_database(monkeypatch, frame):
    fake = types.ModuleType("database")
    fake.fetch_detections = lambda: frame
    fake.init_db = lambda: None
    fake.clear_detections = lambda source=None: 0
    monkeypatch.setitem(sys.modules, "database", fake)


def _sample():
    rows = []
    for i, t in enumerate(["2026-11-17 09:00:00", "2026-11-17 09:00:15", "2026-11-18 14:30:00",
                           "2026-11-18 14:30:20", "2026-11-19 09:10:00"]):
        rows.append((i, "Asha" if i % 2 == 0 else "Ravi", t, 0.31, "live", "webcam", None))
    rows.append((9, "Asha", "2026-11-19 10:00:00", 0.4, "video", "clip.mp4", 12.0))
    return pd.DataFrame(rows, columns=COLUMNS)


def test_dashboard_renders_with_data(monkeypatch):
    _install_fake_database(monkeypatch, _sample())
    at = AppTest.from_file(DASHBOARD, default_timeout=60).run()
    assert not at.exception, [e.value for e in at.exception]
    assert any(m.label == "Total detections" and m.value == "6" for m in at.metric)


def test_dashboard_renders_when_empty(monkeypatch):
    _install_fake_database(monkeypatch, pd.DataFrame(columns=COLUMNS))
    at = AppTest.from_file(DASHBOARD, default_timeout=60).run()
    assert not at.exception, [e.value for e in at.exception]
