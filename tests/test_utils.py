import math

from utils import CooldownGate, safe_fps


def test_first_event_always_logged_even_at_time_zero():
    gate = CooldownGate(15)
    assert gate.should_log("A", 0.0)          # regression: old code dropped this


def test_cooldown_blocks_then_allows():
    gate = CooldownGate(15)
    assert gate.should_log("A", 0)
    assert not gate.should_log("A", 14.9)
    assert gate.should_log("A", 15)
    assert not gate.should_log("A", 20)


def test_keys_are_independent():
    gate = CooldownGate(15)
    assert gate.should_log("A", 0) and gate.should_log("B", 1)


def test_safe_fps():
    assert safe_fps(30) == 30
    assert safe_fps(0) == 25 and safe_fps(float("nan")) == 25 and safe_fps(None) == 25
