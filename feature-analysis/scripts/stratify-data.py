#!/bin/env -S python3 -u


import math
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from tqdm import trange, tqdm

from pretty_cli import PrettyCli


OUT_ROOT = Path("output")
SOURCES = [ "left-cam", "right-cam" ]

REPETITIONS : int = 1_000_000
NUM_FOLDS   : int = 5

cli = PrettyCli()


def json_handler(obj: Any):
    """
    Set this as the default() callback when calling json.dump() to ensure NumPy arrays are handled properly.
    """
    if type(obj).__module__ == np.__name__:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj.item()

    return str(obj)


def rel_se(observed: float, expected: float) -> float:
    """Return the relative squared error between `observed` and `expected` (normalized using `expected`)"""
    return ((observed - expected) / expected) ** 2


def get_pair_info() -> pd.DataFrame:
    pair_regex = re.compile("(P|N)\d{3}")
    pair_info = pd.DataFrame()

    face_files = sorted(file for file in Path("dataset/left-cam").iterdir() if file.name.endswith("consolidated-face.csv"))

    for file in face_files:
        if not file.name.endswith("planning-1-consolidated-face.csv"):
            continue # Only consider the first instance per pair.

        pair_id = pair_regex.search(file.name).group(0)
        [child_1, child_2] = sorted(pd.read_csv(file, nrows=5)["child_id"].unique())

        if pair_id == "P240":
            continue # Bad pair!

        pair_info.loc[pair_id, "condition"] = (pair_id[0] == "P")
        pair_info.loc[pair_id, "year"     ] = int(pair_id[1])
        pair_info.loc[pair_id, "child_1"  ] = child_1
        pair_info.loc[pair_id, "child_2"  ] = child_2
        pair_info.loc[pair_id, "rounds"   ] = len([ file for file in face_files if pair_id in file.name ])

    pair_info = pair_info.astype(int)
    pair_info.sort_index(inplace=True)
    pair_info.index.name = "pair_id"

    return pair_info


def main() -> None:
    cli.main_title("STRATIFY DATA")

    start_time = datetime.now()
    rng = np.random.default_rng(seed=1168824132)

    # ================================================================ #
    cli.chapter("Pair Info")

    pair_info = get_pair_info()
    stratification_lookup = pair_info.reset_index().set_index(["condition", "year"]).sort_index()
    cli.print(pair_info)

    # ================================================================ #
    cli.chapter("Stratified Counts")

    counts = pair_info.reset_index().groupby(["condition", "year"]).count()["pair_id"]
    cli.print(counts)

    # ================================================================ #
    cli.chapter("Round Durations")

    cli.subchapter("Left Cam Data")
    left_cam_durations = pd.read_csv("dataset/left-cam-durations.csv", index_col=[ "pair_id", "round" ]).sort_index()
    cli.print(left_cam_durations)

    # (source, pair_id, round) => duration
    video_lookup: dict[str, dict[str, dict[int, np.ndarray]]] = dict()

    for source in SOURCES:
        video_lookup[source] = dict()
        for pair_id in tqdm(pair_info.index, desc="pair", leave=False):
            video_lookup[source][pair_id] = dict()
            rounds = pair_info.loc[pair_id, "rounds"]
            for round in range(1, rounds+1):
                video_lookup[source][pair_id][round] = left_cam_durations.loc[(pair_id, round)]


    # ================================================================ #
    cli.chapter("Stratifying")

    total_rounds = pair_info["rounds"].sum()
    target_total_rounds = total_rounds / NUM_FOLDS

    positive_rounds = stratification_lookup.loc[1, "rounds"].sum()
    target_rel_pos_rounds = positive_rounds / total_rounds

    total_ids = len(pair_info)
    target_ids = total_ids / NUM_FOLDS

    # ASSUMPTION: all sources have the same duration.
    total_duration    = 0
    positive_duration = 0
    for (pair_id, round_data) in video_lookup[SOURCES[0]].items():
        for (round, duration) in round_data.items():
            duration = duration.item()
            total_duration += duration
            if pair_id[0] == "P":
                positive_duration += duration
    target_total_duration = total_duration / NUM_FOLDS
    target_rel_pos_duration = positive_duration / total_duration

    cli.section("Targets")
    cli.print({
        "Pairs per Fold"                  : target_ids,
        "Rounds per Fold"                 : target_total_rounds,
        "Proportion of Positive Rounds"   : f"{100*target_rel_pos_rounds:.02f}%",
        "Duration per Fold"               : timedelta(seconds=target_total_duration),
        "Proportion of Positive Duration" : f"{100*target_rel_pos_duration:.02f}%",
    })

    runs: list[tuple[float, list[dict[str, Any]]]] = []

    for _ in trange(REPETITIONS):

        folds = [
            {
                "k"        : k,
                "pairs"    : { "positive": 0, "negative": 0, "total": 0 },
                "rounds"   : { "positive": 0, "negative": 0, "total": 0 },
                "duration" : { "positive": 0, "negative": 0, "total": 0 },
                "pair_ids" : [],
            }
            for k in range(NUM_FOLDS)
        ]

        for condition in pair_info["condition"].unique():
            for year in pair_info["year"].unique():
                pair_ids = stratification_lookup.loc[(condition, year), "pair_id"].values
                assert len(pair_ids) > 0

                for n in range(math.ceil(len(pair_ids) / NUM_FOLDS)):
                    start_idx = n * NUM_FOLDS
                    end_idx = (n + 1) * NUM_FOLDS
                    id_batch = pair_ids[start_idx:end_idx]

                    indices = [n for n in range(NUM_FOLDS)]
                    rng.shuffle(indices)

                    for (pair_id, fold_idx) in zip(id_batch, indices):
                        folds[fold_idx]["pair_ids"].append(pair_id)

                        type_key = "positive" if (pair_id[0] == "P") else "negative"

                        folds[fold_idx]["pairs"][type_key] += 1
                        folds[fold_idx]["pairs"]["total" ] += 1

                        folds[fold_idx]["rounds"][type_key] += pair_info.loc[pair_id, "rounds"]
                        folds[fold_idx]["rounds"]["total" ] += pair_info.loc[pair_id, "rounds"]

                        for (round, duration) in video_lookup[SOURCES[0]][pair_id].items():
                            duration = duration.item()
                            folds[fold_idx]["duration"][type_key] += duration
                            folds[fold_idx]["duration"]["total" ] += duration

        total_error = 0
        for k in range(NUM_FOLDS):
            fold = folds[k]

            for field in [ "pairs", "rounds", "duration" ]:
                fold[field]["positive_fraction"] = fold[field]["positive"] / fold[field]["total"]

            id_count_error          = rel_se(observed=fold["pairs"   ]["total"            ], expected=target_ids             ) # Do we have the same # of pairs per fold?
            total_round_error       = rel_se(observed=fold["rounds"  ]["total"            ], expected=target_total_rounds    ) # Do we have the same total number of rounds per fold?
            total_duration_error    = rel_se(observed=fold["duration"]["total"            ], expected=target_total_duration  ) # Do we have the same total number of seconds per fold?
            positive_round_error    = rel_se(observed=fold["rounds"  ]["positive_fraction"], expected=target_rel_pos_rounds  ) # Do we have the same proportion of positive rounds per fold?
            positive_duration_error = rel_se(observed=fold["duration"]["positive_fraction"], expected=target_rel_pos_duration) # Do we have the same proportion of positive seconds per fold?

            fold_error = 2.0 * id_count_error + 1.25 * total_round_error + 1.5 * positive_round_error + 0.5 * total_duration_error + 0.75 * positive_duration_error
            total_error += fold_error

        runs.append((total_error, folds))

    error_series = pd.Series([ error for (error, folds) in runs ])
    best_idx = error_series.argmin()
    best_error, best_folds = runs[best_idx]

    cli.subchapter("Error Distribution")
    cli.print(error_series.describe())

    cli.subchapter("Best Fold")

    cli.section("Error")
    cli.print(best_error)

    for k in range(NUM_FOLDS):
        cli.section(f"Fold {k}")
        cli.print(best_folds[k])

    # ================================================================ #
    cli.chapter("Saving to Disk")

    end_time = datetime.now()

    cli.section("Saving...")

    path = OUT_ROOT / "k_folds.json"
    saved_data = {
        "metadata": {
            "start_time" : start_time.strftime("%Y%m%dT%H%M%S"), # ISO-8601 compact style.
            "end_time"   : end_time  .strftime("%Y%m%dT%H%M%S"), # ISO-8601 compact style.
            "duration"   : end_time - start_time,
            "error"      : best_error,
            "num_folds"  : NUM_FOLDS,
        },
        "folds"      : best_folds,
    }

    with open(path, "w") as handle:
        json.dump(saved_data, handle, ensure_ascii=False, indent=4, default=json_handler)

    cli.print(f"Saved to: {path}")

    cli.section("Saved Data")

    def prettify(d: dict[str, Any]) -> dict[str, Any]:
        return { key.replace("_", " ").title(): value for (key, value) in saved_data.items() }

    cli.print({
        "Metadata": prettify(saved_data["metadata"]),
        "Folds": { fold["k"]: prettify(fold) for fold in saved_data["folds"] },
     })



if __name__ == "__main__":
    main()
