import numpy as np

import evaluate


def cluster(center, n, rng, spread=0.02):
    return [center + rng.normal(0, spread, 128) for _ in range(n)]


def make_data():
    rng = np.random.default_rng(0)
    a, b = rng.normal(0, 1, 128), rng.normal(0, 1, 128)
    encs = cluster(a, 4, rng) + cluster(b, 4, rng)
    names = ["A"] * 4 + ["B"] * 4
    strangers = [rng.normal(0, 1, 128) for _ in range(5)]
    return np.array(encs), names, np.array(strangers)


def test_well_separated_people_are_recognised():
    encs, names, strangers = make_data()
    m = evaluate.compute_metrics(encs, names, 0.6, strangers)
    assert m["tested"] == 8 and m["accuracy"] == 1.0
    assert m["misidentification_rate"] == 0.0
    assert m["false_accept_rate"] == 0.0          # random strangers are far away


def test_very_strict_tolerance_rejects_everyone():
    encs, names, _ = make_data()
    m = evaluate.compute_metrics(encs, names, 0.0001)
    assert m["accuracy"] == 0.0 and m["false_reject_rate"] == 1.0


def test_single_photo_people_are_not_testable():
    encs, names, _ = make_data()
    m = evaluate.compute_metrics(encs[:5], names[:5], 0.6)   # B has only 1 photo left
    assert m["tested"] == 4


def test_recommend_respects_far_cap():
    encs, names, strangers = make_data()
    results = evaluate.sweep(encs, names, [0.4, 0.5, 0.6], strangers)
    assert evaluate.recommend(results, max_far=0.01) is not None
