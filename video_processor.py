"""Process a recorded video through the same pipeline as the live tracker.

Detections are timestamped with the position inside the video
(``frame_index / fps``), NOT with the time the file happens to be processed.
That keeps the cooldown and the visit/duration analytics meaningful no matter
how fast the machine chews through the file.

    python video_processor.py clip.mp4 --start "2026-11-19 09:00:00"
"""

import argparse
import os
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import cv2
import imageio

import config
from database import init_db, save_detections_bulk
from recognizer import KNOWN, UNKNOWN, PersonRecognizer
from utils import CooldownGate, safe_fps


@dataclass
class VideoResult:
    output_path: str
    frames: int
    fps: float
    video_seconds: float
    processing_seconds: float
    effective_fps: float
    logged: int
    people: dict = field(default_factory=dict)   # name -> rows logged
    unknown_faces: int = 0                       # frames-with-unknown-face count


def process_video(input_path, output_path="output_video.mp4", source_name=None,
                  start_time=None, save_to_db=True, recognizer=None,
                  progress_callback=None):
    """Annotate a video and log recognised people to MySQL.

    start_time        real-world time the recording started (default: now). Row
                      timestamps are start_time + position in the video.
    recognizer        pass an existing PersonRecognizer to avoid reloading models.
    progress_callback called as callback(done_frames, total_frames).
    """
    recognizer = recognizer or PersonRecognizer()
    source_name = source_name or os.path.basename(input_path)
    start_time = start_time or datetime.now()

    capture = cv2.VideoCapture(input_path)
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {input_path}")

    fps = safe_fps(capture.get(cv2.CAP_PROP_FPS))
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    writer = imageio.get_writer(output_path, fps=fps, codec="libx264",
                                quality=7, macro_block_size=1)

    gate = CooldownGate(config.COOLDOWN_SECONDS)
    rows, people, detections = [], Counter(), []
    unknown_faces = 0
    frame_index = 0
    started = time.perf_counter()

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break

            video_second = frame_index / fps
            if frame_index % config.PROCESS_EVERY_N_FRAMES == 0:
                detections = recognizer.process_frame(frame)
                for d in detections:
                    if d.status == UNKNOWN:
                        unknown_faces += 1
                    elif d.status == KNOWN and gate.should_log(d.name, video_second):
                        rows.append((
                            d.name,
                            start_time + timedelta(seconds=video_second),
                            d.distance, "video", source_name, round(video_second, 2),
                        ))
                        people[d.name] += 1

            recognizer.annotate(frame, detections)

            # libx264 needs even dimensions.
            h, w = frame.shape[:2]
            frame = frame[: h - h % 2, : w - w % 2]
            writer.append_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            frame_index += 1
            if progress_callback and (frame_index % 10 == 0 or frame_index == total_frames):
                progress_callback(frame_index, total_frames)
    finally:
        capture.release()
        writer.close()

    elapsed = time.perf_counter() - started
    logged = 0
    if save_to_db and rows:
        init_db()
        logged = save_detections_bulk(rows)

    return VideoResult(
        output_path=output_path,
        frames=frame_index,
        fps=fps,
        video_seconds=frame_index / fps,
        processing_seconds=elapsed,
        effective_fps=frame_index / elapsed if elapsed else 0.0,
        logged=logged if save_to_db else len(rows),
        people=dict(people),
        unknown_faces=unknown_faces,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a video with IdentiTrack")
    parser.add_argument("video")
    parser.add_argument("--out", default="output_video.mp4")
    parser.add_argument("--start", help='recording start, e.g. "2026-11-19 09:00:00"')
    parser.add_argument("--no-db", action="store_true", help="do not write to MySQL")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d %H:%M:%S") if args.start else None
    result = process_video(args.video, args.out, start_time=start, save_to_db=not args.no_db,
                           progress_callback=lambda d, t: print(f"\r{d}/{t} frames", end=""))
    print(f"\nDone: {result.frames} frames in {result.processing_seconds:.1f}s "
          f"({result.effective_fps:.1f} FPS). Logged {result.logged} detection(s): {result.people}")
