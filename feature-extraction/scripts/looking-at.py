#!/bin/env -S python3


import shutil
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import trange
from pretty_cli import PrettyCli

from local import util, geometry


DATA_PATH = Path("data-backup/20231009T104102")
OUTPUT_ROOT = Path("look-at")
CAMERAS = [ "left-cam", "right-cam", "frontal-cam" ]

cli = PrettyCli()


def look_at(data: pd.DataFrame, screen_plane: np.ndarray) -> pd.DataFrame:
    output = pd.DataFrame()

    max_frame = data.index.get_level_values("frame").max()
    faces = [0, 1]

    for frame in trange(1, max_frame + 1):
        if not frame in data.index:
            row = pd.DataFrame({ "frame": [ frame ], **{ f"child_{face}": [ "unknown" ] for face in faces } })
            output = pd.concat([ output, row ], ignore_index=True)
            continue

        states = { face: "unknown" for face in faces }
        for (f1, f2) in itertools.permutations(faces):
            if f1 in data.loc[frame].index:
                states[f1] = "none"

                left_eye_ray  = geometry.get_face_ray(data, frame, f1, eye="left")
                right_eye_ray = geometry.get_face_ray(data, frame, f1, eye="right")

                if f2 in data.loc[frame].index:
                    face_sphere = geometry.get_face_sphere(data, frame, f2)
                    if geometry.looks_at_face(left_eye_ray, right_eye_ray, face_sphere):
                        states[f1] = "face"

                if states[f1] == "none": # No other face detected, or not looking at other face.
                    if geometry.looks_at_screen(left_eye_ray, right_eye_ray, screen_plane, max_magnitude=4_000):
                        states[f1] = "screen"

        row = pd.DataFrame({ "frame": [ frame ], **{ f"child_{face}": state for (face, state) in states.items() } })
        output = pd.concat([ output, row ], ignore_index=True)

    output = output.set_index("frame")
    return output


def main() -> None:
    cli.main_title("LOOKING AT")

    assert DATA_PATH.is_dir()
    for camera in CAMERAS:
        assert (DATA_PATH / camera).is_dir()

    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)

    OUTPUT_ROOT.mkdir(parents=False, exist_ok=False)

    for camera in CAMERAS:
        cli.chapter(camera)

        root = DATA_PATH / camera
        screen_plane = geometry.SCREEN_PLANES[camera]

        out_dir = OUTPUT_ROOT / camera
        out_dir.mkdir(parents=False, exist_ok=False)

        face_data_paths = sorted(file for file in root.iterdir() if file.is_file() and file.suffix == ".csv" and file.stem.endswith("-face-data"))

        for data_path in face_data_paths:
            parts = data_path.stem.split("-")

            if len(parts) < 7:
                cli.print(f"Non compliant file found (stem too short): {data_path}")
                continue

            pair_id = parts[2]

            if not util.PAIR_REGEX.match(pair_id):
                cli.print(f"Non compliant file found (stem does not contain a valid pair ID at the expected location): {data_path}")
                continue

            round = int(parts[4])

            cli.subchapter(f"Pair {pair_id}; Round {round}")

            data = pd.read_csv(data_path, index_col=["frame", "face_id"])
            data = data[data["success"] == 1] # Remove failed registration attempts.
            data = data.loc[pd.IndexSlice[:, :1], :] # HACK: enforce no more than 2 entries per frame by always keeping IDs 0 and 1.

            lookat = look_at(data, screen_plane)
            lookat.to_csv(out_dir / data_path.name.replace("-face-data.csv", "-look-at.csv"))


if __name__ == "__main__":
    main()
