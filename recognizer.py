"""Shared detection + recognition core.

Used by the live tracker, the video processor and the dashboard so the
pipeline exists in exactly one place:

    frame -> YOLOv8 (person boxes) -> face search inside each box
          -> 128-d face encoding -> nearest enrolled face -> name / unknown
"""

import os
import pickle
from dataclasses import dataclass

import cv2
import face_recognition
import numpy as np
from ultralytics import YOLO

import config

KNOWN = "known"        # face found and matched an enrolled person
UNKNOWN = "unknown"    # face found but no enrolled person is close enough
NO_FACE = "no_face"    # a person was detected but no usable face was visible

_COLORS = {            # BGR
    KNOWN: (0, 200, 0),
    UNKNOWN: (0, 140, 255),
    NO_FACE: (160, 160, 160),
}


@dataclass(frozen=True)
class Detection:
    box: tuple          # (x1, y1, x2, y2)
    name: str
    status: str
    distance: float = None


def load_encodings(path=config.ENCODINGS_FILE):
    """Load enrolled face encodings written by enrollment.py."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"'{path}' not found. Add photos under '{config.GALLERY_FOLDER}/<PersonName>/' "
            "and run: python enrollment.py"
        )
    with open(path, "rb") as f:
        data = pickle.load(f)
    names = list(data["names"])
    if not names:
        raise ValueError("No enrolled faces found. Re-run enrollment.py with clear photos.")
    return np.array(data["encodings"]), names


class PersonRecognizer:
    def __init__(self, tolerance=config.FACE_MATCH_TOLERANCE,
                 encodings_path=config.ENCODINGS_FILE,
                 yolo_path=config.YOLO_MODEL,
                 yolo_conf=config.YOLO_CONFIDENCE):
        self.tolerance = tolerance
        self.yolo_conf = yolo_conf
        self.known_encodings, self.known_names = load_encodings(encodings_path)
        self.yolo = YOLO(yolo_path)

    # ---- matching ---------------------------------------------------------
    def match_face(self, encoding):
        """Return (name or None, distance) for the closest enrolled face."""
        distances = face_recognition.face_distance(self.known_encodings, encoding)
        best = int(np.argmin(distances))
        distance = float(distances[best])
        if distance <= self.tolerance:
            return self.known_names[best], distance
        return None, distance

    @staticmethod
    def _face_region(crop):
        """Restrict the face search to the head area of tall (full-body) boxes."""
        h, w = crop.shape[:2]
        if h / max(w, 1) >= config.UPPER_BODY_ASPECT:
            return crop[: max(int(h * config.UPPER_BODY_FRACTION), 1)]
        return crop

    # ---- per-frame pipeline ----------------------------------------------
    def process_frame(self, frame):
        """Detect people in a BGR frame and identify each one. Returns [Detection]."""
        results = self.yolo(frame, classes=[0], conf=self.yolo_conf, verbose=False)
        height, width = frame.shape[:2]
        detections = []

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            x1, y1 = max(x1, 0), max(y1, 0)
            x2, y2 = min(x2, width), min(y2, height)
            crop = frame[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            region = self._face_region(crop)
            rgb = np.ascontiguousarray(cv2.cvtColor(region, cv2.COLOR_BGR2RGB))
            locations = face_recognition.face_locations(rgb)
            if not locations:
                detections.append(Detection((x1, y1, x2, y2), "Person", NO_FACE))
                continue

            # Use the largest face in the box (most likely the box's owner).
            largest = max(locations, key=lambda l: (l[2] - l[0]) * (l[1] - l[3]))
            encodings = face_recognition.face_encodings(rgb, [largest])
            if not encodings:
                detections.append(Detection((x1, y1, x2, y2), "Person", NO_FACE))
                continue

            name, distance = self.match_face(encodings[0])
            if name is None:
                detections.append(Detection((x1, y1, x2, y2), "Unknown", UNKNOWN, distance))
            else:
                detections.append(Detection((x1, y1, x2, y2), name, KNOWN, distance))

        return detections

    # ---- drawing ----------------------------------------------------------
    @staticmethod
    def annotate(frame, detections):
        """Draw boxes and labels onto the frame (in place) and return it."""
        for d in detections:
            x1, y1, x2, y2 = d.box
            color = _COLORS[d.status]
            label = d.name if d.distance is None else f"{d.name} ({d.distance:.2f})"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            top = max(y2 - 28, 0)
            cv2.rectangle(frame, (x1, top), (x2, y2), color, cv2.FILLED)
            cv2.putText(frame, label, (x1 + 6, max(y2 - 8, 12)),
                        cv2.FONT_HERSHEY_DUPLEX, 0.55, (255, 255, 255), 1)
        return frame
