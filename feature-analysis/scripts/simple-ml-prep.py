#!/bin/env -S python3


import re
from pathlib import Path

import pandas as pd
from pretty_cli import PrettyCli
from tqdm import tqdm


SOURCES = [ "left-cam", "right-cam", "frontal-cam" ]

DATA_ROOT = Path("dataset")
DATA_DIRS : list[Path] = [ DATA_ROOT / source for source in SOURCES ]
OUTPUT_DIR = Path("output")

PAIR_REGEX : re.Pattern = re.compile(pattern="[PN][23]\d{2}")

AUS = [ 1, 2, 4, 5, 6, 7, 9, 10, 12, 14, 15, 17, 20, 23, 25, 26, 45 ]
OPENFACE_AU_PRESENCE = [ f"AU{au:02}_c" for au in AUS ]
OPENFACE_AU_INTENSITY = [ f"AU{au:02}_r" for au in AUS ]
AU_SHORT = [ f"AU{au:02}" for au in AUS ]

cli = PrettyCli()


def get_paths(data_dir: Path) -> list[tuple[str, int, Path]]:
    face_csv_regex = re.compile(f"{data_dir.name}-([NP][23]\d{{2}})-planning-(\d)-consolidated-face.csv")

    paths = []
    for file in data_dir.iterdir():
        match = face_csv_regex.match(file.name)
        if not match:
            continue
        pair_id: str = match[1]
        round: int = int(match[2])
        paths.append((pair_id, round, file))
    paths.sort()

    return paths


def process_child_data(data: pd.DataFrame, measure: str, columns: list[str]) -> pd.DataFrame:
    summary = (
        data.describe(percentiles=[ .95 ])
        .loc[[ "mean", "std", "95%" ], :]
        .rename({ "95%": "q95" }, axis=0)
        .rename({ openface: f"{short}_{measure}" for (openface, short) in zip(columns, AU_SHORT) }, axis=1)
        .reset_index()
        .melt(id_vars=["index"])
    )

    summary["variable"] = summary["variable"] + "_" + summary["index"]
    summary.drop("index", axis=1, inplace=True)
    summary.set_index("variable", inplace=True)

    return summary.T


def main() -> None:
    cli.main_title("SIMPLE ML PREP")

    assert DATA_ROOT.is_dir()

    if not OUTPUT_DIR.is_dir():
        OUTPUT_DIR.mkdir(parents=False, exist_ok=False)

    for data_dir in DATA_DIRS:
        cli.chapter(data_dir.name)

        paths = get_paths(data_dir)

        data = pd.DataFrame()

        for (pair_id, game_round, file) in tqdm(paths):
            condition = "positive" if pair_id[0] == "P" else "negative"

            face_data = pd.read_csv(file, index_col=["frame", "child_id"])

            child_ids_in_file = sorted(face_data.index.get_level_values("child_id").unique())
            success_idx = (face_data["success"] == 1)

            for child_id in child_ids_in_file:
                child_idx = (face_data.index.get_level_values("child_id") == child_id)

                all_child_rows = face_data.loc[child_idx]
                successful_child_rows = face_data.loc[child_idx & success_idx]

                detection_rate = len(successful_child_rows) / len(all_child_rows)

                au_presence  = face_data.loc[child_idx & success_idx, OPENFACE_AU_PRESENCE]
                au_intensity = face_data.loc[child_idx & success_idx, OPENFACE_AU_INTENSITY] / 5

                au_presence_summary  = process_child_data(au_presence , "presence", OPENFACE_AU_PRESENCE)
                au_intensity_summary = process_child_data(au_intensity, "intensity", OPENFACE_AU_INTENSITY)

                au_summary = pd.concat([au_presence_summary, au_intensity_summary], axis=1)

                au_summary["pair_id"] = pair_id
                au_summary["round"] = game_round
                au_summary["child_id"] = child_id
                au_summary["condition"] = condition
                au_summary["detection_rate"] = detection_rate

                data = pd.concat([data, au_summary], ignore_index=True)

        data.set_index(["pair_id", "round", "child_id"], inplace=True)

        # Move the condition and detection rate columns to the beginning (based on https://stackoverflow.com/questions/25122099/move-column-by-name-to-front-of-table-in-pandas )
        cond_col = data.pop(item="condition")
        data.insert(loc=0, column=cond_col.name, value=cond_col)

        detection_col = data.pop(item="detection_rate")
        data.insert(loc=1, column=detection_col.name, value=detection_col)

        cli.print(data)
        data.to_csv(OUTPUT_DIR / f"{data_dir.name}-summary-au-data.csv")


if __name__ == "__main__":
    main()
