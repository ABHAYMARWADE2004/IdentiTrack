"""End-to-end test of the video pipeline using stand-in detectors.

YOLO and face_recognition are replaced with tiny fakes so the test runs
anywhere (no GPU, no dlib, no MySQL). It verifies the logic that is ours:
video-time timestamps, cooldown, bulk logging, annotation and output writing.
"""

import importlib
import pickle
import sys
import types
from datetime import datetime, timedelta

import cv2
import numpy as np
import pytest


class _Box:
    def __init__(self, xyxy):
        self.xyxy = [xyxy]


class _FakeYOLO:
    def __init__(self, *_a, **_k):
        pass

    def __call__(self, frame, **_k):
        return [types.SimpleNamespace(boxes=[_Box([4, 2, 60, 46])])]   # one wide box


def _fake_face_recognition():
    fr = types.ModuleType("face_recognition")
    fr.face_locations = lambda rgb, *a, **k: [(5, 40, 35, 10)]
    fr.face_encodings = lambda rgb, locs=None, *a, **k: [np.full(128, 0.1)]
    fr.face_distance = lambda known, enc: np.linalg.norm(np.asarray(known) - enc, axis=1)
    return fr


@pytest.fixture
def pipeline(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "face_recognition", _fake_face_recognition())
    monkeypatch.setitem(sys.modules, "ultralytics", types.SimpleNamespace(YOLO=_FakeYOLO))
    for name in ("recognizer", "video_processor"):
        sys.modules.pop(name, None)
    recognizer = importlib.import_module("recognizer")
    video_processor = importlib.import_module("video_processor")

    saved = []
    monkeypatch.setattr(video_processor, "init_db", lambda: None)
    monkeypatch.setattr(video_processor, "save_detections_bulk",
                        lambda rows: saved.extend(rows) or len(rows))

    enc_path = tmp_path / "enc.pkl"
    with open(enc_path, "wb") as f:
        pickle.dump({"encodings": [np.full(128, 0.1), np.full(128, 0.9)],
                     "names": ["Asha", "Ravi"]}, f)

    yield recognizer, video_processor, saved, str(enc_path)
    for name in ("recognizer", "video_processor"):
        sys.modules.pop(name, None)


def _make_video(path, seconds=40, fps=5, size=(64, 48)):
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
    for i in range(seconds * fps):
        writer.write(np.full((size[1], size[0], 3), i % 255, dtype=np.uint8))
    writer.release()


def test_video_uses_video_time_and_cooldown(pipeline, tmp_path):
    recognizer_mod, vp, saved, enc_path = pipeline
    video = tmp_path / "clip.mp4"
    _make_video(video, seconds=40, fps=5)

    rec = recognizer_mod.PersonRecognizer(encodings_path=enc_path, tolerance=0.5)
    start = datetime(2026, 11, 19, 9, 0, 0)
    result = vp.process_video(str(video), str(tmp_path / "out.mp4"),
                              start_time=start, recognizer=rec)

    assert result.frames == 200
    assert result.people == {"Asha": 3}                 # t≈0, ≈15, ≈30 within 40 s
    assert len(saved) == 3
    offsets = [row[5] for row in saved]
    assert offsets[0] == 0.0 and offsets == sorted(offsets)
    assert all(b - a >= 15 for a, b in zip(offsets, offsets[1:]))
    for row in saved:                                   # timestamps follow the VIDEO clock
        assert row[1] == start + timedelta(seconds=row[5])
        assert row[3] == "video" and row[4] == "clip.mp4"
    assert (tmp_path / "out.mp4").stat().st_size > 0


def test_unknown_face_is_not_logged(pipeline, tmp_path):
    recognizer_mod, vp, saved, enc_path = pipeline
    video = tmp_path / "clip.mp4"
    _make_video(video, seconds=3, fps=5)

    # Strict tolerance + stand-in face that is nowhere near either enrolled face.
    rec = recognizer_mod.PersonRecognizer(encodings_path=enc_path, tolerance=0.0001)
    sys.modules["face_recognition"].face_encodings = lambda rgb, locs=None, *a, **k: [np.full(128, 5.0)]
    result = vp.process_video(str(video), str(tmp_path / "o.mp4"), recognizer=rec)

    assert saved == [] and result.people == {} and result.unknown_faces > 0


def test_tall_box_searches_only_upper_body(pipeline):
    recognizer_mod, *_ = pipeline
    tall = np.zeros((200, 50, 3), dtype=np.uint8)      # ratio 4 -> full-body
    wide = np.zeros((60, 50, 3), dtype=np.uint8)       # ratio 1.2 -> close-up
    assert recognizer_mod.PersonRecognizer._face_region(tall).shape[0] == 120
    assert recognizer_mod.PersonRecognizer._face_region(wide).shape[0] == 60
