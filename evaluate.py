"""Measure how well face matching actually works, and pick a tolerance.

Two kinds of test, using only photos:

1. Leave-one-out on the gallery: each photo is treated as a "new" photo and
   matched against all OTHER enrolled photos. This measures how often enrolled
   people are recognised correctly, rejected, or mistaken for someone else.
2. Strangers (optional): photos of people who are NOT enrolled, in
   --unknown-dir. This measures the false-accept rate: how often a stranger is
   wrongly given an enrolled person's name. This is the number that matters
   most for an identity system.

    python evaluate.py
    python evaluate.py --unknown-dir eval/strangers --max-far 0.01 --out eval_results.csv

Use photos that were NOT chosen to look good: varied angles, lighting and
distance give honest numbers. Report N (number of test photos) with every
percentage.
"""

import argparse
import os

import numpy as np
import pandas as pd

import config

UNKNOWN = "Unknown"


def pairwise_distances(a, b):
    """Euclidean distance matrix between two sets of encodings (shape n x m)."""
    return np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)


def compute_metrics(encodings, names, tolerance, stranger_encodings=None):
    """Leave-one-out metrics at one tolerance. Pure numpy, unit-tested.

    A photo is only testable if its person has at least one other photo.
    """
    encodings = np.asarray(encodings, dtype=float)
    names = np.asarray(names)
    n = len(names)

    dist = pairwise_distances(encodings, encodings)
    np.fill_diagonal(dist, np.inf)            # never match a photo with itself

    counts = pd.Series(names).value_counts()
    testable = np.array([counts[name] >= 2 for name in names])

    correct = false_reject = misidentified = 0
    for i in np.where(testable)[0]:
        j = int(np.argmin(dist[i]))
        if dist[i, j] <= tolerance:
            if names[j] == names[i]:
                correct += 1
            else:
                misidentified += 1
        else:
            false_reject += 1

    tested = int(testable.sum())
    result = {
        "tolerance": tolerance,
        "tested": tested,
        "accuracy": correct / tested if tested else np.nan,
        "false_reject_rate": false_reject / tested if tested else np.nan,
        "misidentification_rate": misidentified / tested if tested else np.nan,
        "strangers_tested": 0,
        "false_accept_rate": np.nan,
    }

    if stranger_encodings is not None and len(stranger_encodings) > 0:
        s = np.asarray(stranger_encodings, dtype=float)
        nearest = pairwise_distances(s, encodings).min(axis=1)
        result["strangers_tested"] = len(s)
        result["false_accept_rate"] = float((nearest <= tolerance).mean())
    return result


def sweep(encodings, names, tolerances, stranger_encodings=None):
    rows = [compute_metrics(encodings, names, t, stranger_encodings) for t in tolerances]
    return pd.DataFrame(rows)


def recommend(results, max_far=0.01, max_misid=0.01):
    """Pick the tolerance with the best accuracy that keeps errors under the cap.

    With strangers available the cap is on the false-accept rate; otherwise it
    falls back to the misidentification rate on enrolled people.
    """
    if results["strangers_tested"].max() > 0:
        ok = results[results["false_accept_rate"] <= max_far]
    else:
        ok = results[results["misidentification_rate"] <= max_misid]
    if ok.empty:
        return None
    return float(ok.sort_values(["accuracy", "tolerance"], ascending=[False, True])
                 .iloc[0]["tolerance"])


def per_person_recall(encodings, names, tolerance):
    """Recall per enrolled person (leave-one-out)."""
    encodings = np.asarray(encodings, dtype=float)
    names = np.asarray(names)
    dist = pairwise_distances(encodings, encodings)
    np.fill_diagonal(dist, np.inf)
    rows = []
    for person in sorted(set(names)):
        idx = np.where(names == person)[0]
        if len(idx) < 2:
            continue
        hits = 0
        for i in idx:
            j = int(np.argmin(dist[i]))
            hits += int(dist[i, j] <= tolerance and names[j] == person)
        rows.append({"person": person, "photos_tested": len(idx), "recall": hits / len(idx)})
    return pd.DataFrame(rows)


# ---- image loading (needs face_recognition; kept out of the tested core) ----
def encode_folder_tree(root):
    """Return (encodings, names) for root/<Person>/*.jpg, single-face photos only."""
    import face_recognition

    encs, names = [], []
    for person in sorted(os.listdir(root)):
        folder = os.path.join(root, person)
        if not os.path.isdir(folder):
            continue
        for file in sorted(os.listdir(folder)):
            if not file.lower().endswith(config.IMAGE_EXTENSIONS):
                continue
            image = face_recognition.load_image_file(os.path.join(folder, file))
            locations = face_recognition.face_locations(image)
            if len(locations) != 1:
                continue
            encs.append(face_recognition.face_encodings(image, locations)[0])
            names.append(person)
    return np.array(encs), names


def encode_flat_folder(folder):
    """Return encodings for every single-face image directly inside `folder`."""
    import face_recognition

    encs = []
    for file in sorted(os.listdir(folder)):
        if not file.lower().endswith(config.IMAGE_EXTENSIONS):
            continue
        image = face_recognition.load_image_file(os.path.join(folder, file))
        locations = face_recognition.face_locations(image)
        if len(locations) == 1:
            encs.append(face_recognition.face_encodings(image, locations)[0])
    return np.array(encs)


def main():
    parser = argparse.ArgumentParser(description="IdentiTrack recognition evaluation")
    parser.add_argument("--gallery", default=config.GALLERY_FOLDER)
    parser.add_argument("--unknown-dir", help="folder of photos of people NOT enrolled")
    parser.add_argument("--max-far", type=float, default=0.01,
                        help="highest acceptable false-accept rate (default 0.01)")
    parser.add_argument("--out", default="eval_results.csv")
    args = parser.parse_args()

    print("Encoding gallery photos...")
    encs, names = encode_folder_tree(args.gallery)
    if len(names) == 0:
        raise SystemExit("No usable photos found in the gallery.")
    strangers = None
    if args.unknown_dir:
        print("Encoding stranger photos...")
        strangers = encode_flat_folder(args.unknown_dir)

    tolerances = [round(t, 2) for t in np.arange(0.40, 0.66, 0.05)]
    results = sweep(encs, names, tolerances, strangers)

    pd.options.display.float_format = "{:.3f}".format
    print("\n===== Results by tolerance =====")
    print(results.to_string(index=False))
    results.to_csv(args.out, index=False)

    best = recommend(results, max_far=args.max_far)
    if best is None:
        print("\nNo tolerance met the error cap. Add more/better photos or relax --max-far.")
    else:
        print(f"\nRecommended tolerance: {best}  (set FACE_MATCH_TOLERANCE={best} in .env)")
        print("\nPer-person recall at that tolerance:")
        print(per_person_recall(encs, names, best).to_string(index=False))
    print(f"\nSaved to {args.out}. Quote N (tested / strangers_tested) with any percentage.")


if __name__ == "__main__":
    main()
