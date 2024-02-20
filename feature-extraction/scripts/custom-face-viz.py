#!/bin/env -S python3


# Custom Face Viz
# ===============
#
# Custom visualization of the data produced by OpenFace, in order to understand what we need and the fine details.
#
#
# NOTE: This should be run from the dataset top-level (i.e. the folder containing left-cam/ and right-cam/).


import shutil
from pathlib import Path

import pandas as pd
from pretty_cli import PrettyCli

from local import face


VIDEO_DIRS = [ Path("./left-cam"), Path("./right-cam"), Path("./frontal-cam") ]

# Left and right from the point of view of the individual, as in medicine.
# Eye landmarks taken from the "Landmarks locations in 2D" list from the OpenFace Output Format docs:
# https://github.com/TadasBaltrusaitis/OpenFace/wiki/Output-Format

cli = PrettyCli()


def main() -> None:
    cli.main_title("CUSTOM FACE VIZ")
    for video_dir in VIDEO_DIRS:
        assert video_dir.is_dir(), f"Video dir not found: {video_dir}"

    video_dirs_absolute = [ vid_dir.resolve() for vid_dir in VIDEO_DIRS ]

    for video_dir in video_dirs_absolute:
        cli.chapter(video_dir.stem)

        viz_dir = video_dir / "custom_face_viz"

        if viz_dir.exists():
            shutil.rmtree(viz_dir)
        viz_dir.mkdir(parents=False, exist_ok=False)

        vids = [ file for file in video_dir.iterdir() if file.suffix.lower() == ".mp4"]
        vids.sort()

        for vid in vids:
            cli.subchapter(vid.stem)

            face_csv = vid.with_name(f"{vid.stem}-face-data.csv")
            if not face_csv.is_file():
                cli.print(f"CSV missing: {face_csv}")
                continue

            face_data = pd.read_csv(face_csv, index_col=["frame", "face_id"])
            face.visualize(vid, viz_dir, face_data)

if __name__ == "__main__":
    main()
