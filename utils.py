"""Small, dependency-free helpers (safe to import and unit-test anywhere)."""

import math


class CooldownGate:
    """Decides whether an event for a given key (e.g. a person) should be logged.

    The caller supplies the clock value, so the same logic works for live
    cameras (wall-clock seconds) and for recorded videos (video seconds).

    The first event for a key is always allowed. (The earlier implementation
    compared against a default of 0, which silently dropped the first
    detection of any video whose timestamps started near zero.)
    """

    def __init__(self, seconds):
        self.seconds = seconds
        self._last = {}

    def should_log(self, key, now):
        last = self._last.get(key)
        if last is None or (now - last) >= self.seconds:
            self._last[key] = now
            return True
        return False

    def reset(self):
        self._last.clear()


def safe_fps(value, default=25.0):
    """Return a usable FPS value; cameras and some files report 0 or NaN."""
    try:
        fps = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(fps) or fps <= 0 or fps > 240:
        return default
    return fps
