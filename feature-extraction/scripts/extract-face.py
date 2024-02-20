#!/bin/env -S python3


# Extract Face
# ============
#
# Extract face data from each video, using OpenFace.
# NOTE: This should be run from the dataset top-level (i.e. the folder containing left-cam/ and right-cam/).


import os, shutil
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from pretty_cli import PrettyCli

from local import util, face, arg_parsing


FAILED_VIDEOS_CSV = Path("./failed-videos-extract-face.csv")

cli = PrettyCli()


@dataclass
class Settings(arg_parsing.DefaultSettings):
    openface_bin: Path = Path("/dev/null")


def parse_args() -> Settings:
    parser = arg_parsing.get_default_parser(description="Extract face features from each video, using OpenFace.")
    parser.add_argument("openface_bin", type=arg_parsing.check_path, help="Path to a local installation of the OpenFace binary FaceLandmarkVidMulti.")

    raw_args = parser.parse_args()

    default_settings = arg_parsing.get_default_settings(raw_args)
    openface_bin: Path = raw_args.openface_bin.resolve()
    assert openface_bin.is_file()

    settings = Settings(default_settings.pair_ids, default_settings.video_dirs, openface_bin)
    return settings


def main() -> None:
    settings = parse_args()

    cli.main_title("EXTRACT FACE")

    failed_videos_csv = FAILED_VIDEOS_CSV.resolve()
    if failed_videos_csv.exists():
        failed_videos_csv.unlink()

    paths = arg_parsing.process_paths(settings, file_end=".mp4")
    video_logger = util.FailedVidLogger(cli, failed_videos_csv)

    for video_dir, entries in paths.items():
        cli.chapter(video_dir.stem)
        os.chdir(video_dir)

        openface_viz_dir = video_dir / "face_viz"
        if openface_viz_dir.exists():
            shutil.rmtree(openface_viz_dir)
        openface_viz_dir.mkdir(parents=False, exist_ok=False)

        custom_viz_dir = video_dir / "custom_face_viz"
        if custom_viz_dir.exists():
            shutil.rmtree(custom_viz_dir)
        custom_viz_dir.mkdir(parents=False, exist_ok=False)

        processed_dir = video_dir / "processed"

        for (pair_id, round, vid) in entries:
            cli.subchapter(f"Pair: {pair_id}; Round: {round}")

            # Keep processed dir from growing large by nuking it continuously.
            if processed_dir.exists():
                shutil.rmtree(processed_dir)

            cli.section("OpenFace Feature Extraction")
            # See https://github.com/TadasBaltrusaitis/OpenFace/wiki/Command-line-arguments
            if not util.run_command(cli, command=f"{settings.openface_bin} -2Dfp -3Dfp -pose -aus -gaze -tracked -f {vid}"):
                video_logger.add_failed(vid, reason="OpenFace returned error status")
                continue

            cli.section("Post-Processing Data")
            openface_csv = processed_dir / f"{vid.stem}.csv"
            final_csv = video_dir / f"{vid.stem}-face-data.csv"
            if not openface_csv.is_file():
                video_logger.add_failed(vid, reason="OpenFace did not generate expected CSV feature file.")
                continue # For some reason, OpenFace did not create a CSV file.
            # TODO: Consider filtering only fields we want instead of copying the whole file.
            shutil.move(src=openface_csv, dst=final_csv)

            openface_raw_viz = processed_dir / f"{vid.stem}.avi"
            openface_processed_viz = openface_viz_dir / f"{vid.stem}-face-viz.mp4"
            if not openface_raw_viz.is_file():
                video_logger.add_failed(vid, reason="OpenFace did not generate expected AVI video file.")
                continue
            if not util.run_command(cli, command=f"ffmpeg -i {openface_raw_viz} -preset slow -crf 25 {openface_processed_viz}"):
                video_logger.add_failed(vid, reason="FFMPEG returned error status") # FFMPEG errored.
                continue

            cli.section("Custom Face Viz")
            face_data = pd.read_csv(final_csv, index_col=["frame", "face_id"])
            face.visualize(vid, custom_viz_dir, face_data, create_overlay=True, create_anonymized=False, create_feature=False)

        # Nuke the final one.
        if processed_dir.exists():
            shutil.rmtree(processed_dir)

    cli.big_divisor()
    cli.section("Failed Videos")
    cli.print(video_logger.failed_vids)


if __name__ == "__main__":
    main()
