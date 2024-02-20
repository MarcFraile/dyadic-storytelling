#!/bin/env -S python3


# Extract Py-Feat
# =============
#
# This is an atempt to follow the steps shown in the Py-Feat "Running a full analysis" tutorial:
# https://py-feat.org/basic_tutorials/05_fex_analysis.html


import shutil
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import imageio.v3 as iio
from tqdm import tqdm
from feat import Detector
from pretty_cli import PrettyCli

from local import arg_parsing, face, util

OPENFACE_BIN = Path("/media/chagan/openface/build/bin/FaceLandmarkVidMulti")
FAILED_VIDEOS_CSV = Path("./failed-videos-using-pyfeat.csv")

cli = PrettyCli()


def extract_pyfeat_data(detector: Detector, vid_file: Path) -> pd.DataFrame:
    data = pd.DataFrame()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        meta = iio.immeta(vid_file)
    assert "fps" in meta
    assert "duration" in meta

    approx_frames = int(meta["fps"] * meta["duration"])

    for frame_idx, frame in enumerate(tqdm(iio.imiter(vid_file), desc="frame", total=approx_frames)):
        # Extract using Py-Feat. We catch warnings to avoid spam from a deprecated function.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            faces = detector.detect_faces(frame) # Returns a list-of-lists mapping frame/img => face => [x0, y0, x1, y1, p]
            landmarks = detector.detect_landmarks(frame, faces) # Returns a list-of-lists mapping frame/img => face => array(68, 2); array maps keypoint => (x, y).
            poses = detector.detect_facepose(frame, landmarks) # Returns a dict with entries "faces" (same format as above; what's this??) and "poses". Poses is list-of-lists mapping frame => face => [pitch, roll, yaw]
            aus = detector.detect_aus(frame, landmarks) # Returns a list mapping frame/img => array(faces, 20); array maps face => au (presence?).
            emotions = detector.detect_emotions(frame, faces, landmarks) # Returns a list mapping frame/img => array(faces, 7); array maps face => (anger, disgust, fear, happiness, sadness, surprise, neutral)

        # We only have one image here, so we can unwrap the first layer.
        faces     = faces[0]
        landmarks = np.asarray(landmarks[0]).reshape(-1, 68 * 2, order="F")
        poses     = poses["poses"][0]
        aus       = aus[0]
        emotions  = emotions[0]

        # For some reason, Py-Feat decides to change formats halfway through processing and returns width and height instead.
        # I also don't like their CamelCase naming scheme (which they don't adhere to consistently either).
        face_rect_columns = ["bounds_x0", "bounds_y0", "bounds_x1", "bounds_y1", "bounds_p"]
        landmark_columns = detector.info["face_landmark_columns"]
        pose_columns = [ col.lower() for col in detector.info["facepose_model_columns"]]
        au_columns = detector.info["au_presence_columns"] # Based on name, I assume this means we're returning AU**_c and not AU**_r?
        emotion_columns = detector.info["emotion_model_columns"]

        # It's easier to convert to individual DataFrames and append.
        faces     = pd.DataFrame(data=faces    , columns=face_rect_columns)
        landmarks = pd.DataFrame(data=landmarks, columns=landmark_columns )
        poses     = pd.DataFrame(data=poses    , columns=pose_columns     )
        aus       = pd.DataFrame(data=aus      , columns=au_columns       )
        emotions  = pd.DataFrame(data=emotions , columns=emotion_columns  )

        frame_data = pd.concat([faces, landmarks, poses, aus, emotions], axis=1)

        frame_data.index.name = "face"
        frame_data["frame"] = frame_idx
        frame_data = frame_data.reset_index().dropna(axis=0, how="any").set_index(["frame", "face"]) # For some reason, Py-Feat seems to produce NaN rows *sometimes*. Not sure it's deterministic.

        data = pd.concat([data, frame_data])

    return data


def main() -> None:
    settings = arg_parsing.parse_default_args(description="Process the videos using Py-Feat.")

    cli.main_title("EXTRACT PY-FEAT")

    failed_videos_csv = FAILED_VIDEOS_CSV.resolve()
    if failed_videos_csv.exists():
        failed_videos_csv.unlink()

    cli.section("Load Detector")
    detector = Detector(device="cuda")

    paths = arg_parsing.process_paths(settings, ".mp4")
    video_logger = util.FailedVidLogger(cli, failed_videos_csv)

    for video_dir, entries in paths.items():
        cli.chapter(video_dir.stem)

        viz_dir = video_dir / "pyfeat-viz"
        if viz_dir.exists():
            shutil.rmtree(viz_dir)
        viz_dir.mkdir(parents=False, exist_ok=False)

        for (pair_id, round, video_file) in entries:
            cli.subchapter(f"Pair: {pair_id}; Round: {round}")

            try:
                cli.section("Extracting Data")
                csv_file = video_file.with_name(video_file.stem + "-pyfeat.csv")
                data = extract_pyfeat_data(detector, video_file)
                cli.print(data)
                data.to_csv(csv_file)

                cli.section("Creating Visualization")
                data.rename({ "bounds_p": "confidence"}, axis=1, inplace=True)
                face.visualize(video_file, viz_dir, data, create_overlay=True, create_anonymized=False, create_feature=False)
            except Exception as e:
                video_logger.add_failed(video_file, repr(e))
                continue

    cli.big_divisor()
    cli.section("Failed Videos")
    cli.print(video_logger.failed_vids)


if __name__ == "__main__":
    main()
