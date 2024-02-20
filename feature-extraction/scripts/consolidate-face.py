#!/bin/env -S python3


import shutil
import re
import itertools
import warnings
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from tqdm import trange
from pretty_cli import PrettyCli

from local import util, pose, face, arg_parsing


POSE_HEAD_POINTS = [ "nose", "right_eye", "left_eye", "right_ear", "left_ear" ]

FAILED_VIDEOS_CSV = Path("./failed-videos-consolidate-face.csv")

cli = PrettyCli()


def get_skelly_facepos(skeleton_data: pd.DataFrame, frame: int, skeleton_id: int) -> pose.Keypoint:
    """
    Calculates an anchor point for the face based on available skeleton data.
    * `x` and `y` are averaged over all `POSE_HEAD_POINTS` that have confidence above the `pose.MIN_CONFIDENCE`.
    * `confidence` takes into account how many points were ignored.
    """
    keypoints: list[pose.Keypoint] = []
    for joint in POSE_HEAD_POINTS:
        keypoint = pose.get_keypoint(skeleton_data, frame, skeleton_id, joint)
        if keypoint.confidence > pose.MIN_CONFIDENCE:
            keypoints.append(keypoint)

    if len(keypoints) == 0:
        return pose.Keypoint(x=0.0, y=0.0, confidence=0.0)

    x = sum(kp.x for kp in keypoints) / len(keypoints)
    y = sum(kp.y for kp in keypoints) / len(keypoints)
    confidence = sum(kp.confidence for kp in keypoints) / len(POSE_HEAD_POINTS)

    return pose.Keypoint(x, y, confidence)


def maybe_skelly_facepos(skeleton_data: pd.DataFrame, frame: int, skeleton_id: int) -> Optional[pose.Keypoint]:
    """
    Checks if there is available skeleton data to return an anchor point for the face.
    In case of success, returns data as described in `get_skelly_facepos()`.
    Returns `None` otherwise.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if (frame, skeleton_id) in skeleton_data.index:
            face_pos = get_skelly_facepos(skeleton_data, frame, skeleton_id)
            if face_pos.confidence > pose.MIN_CONFIDENCE:
                return face_pos
        return None


def seek_first_face(skeleton_data: pd.DataFrame, skeleton_id: int) -> pose.Keypoint:
    """
    Seeks the first successful anchor point for the face based on skeleton data, as described in `maybe_skelly_facepos()`.
    """
    frames = skeleton_data.index.get_level_values("frame").unique().sort_values()
    for frame in frames:
        face_pos = maybe_skelly_facepos(skeleton_data, frame, skeleton_id)
        if face_pos is not None:
            return face_pos
    raise Exception(f"Face not located for skeleton_id = {skeleton_id}")


def get_face_facepos(face_data: pd.DataFrame, frame: int, face_id: int) -> pose.Keypoint:
    x = face_data.loc[(frame, face_id), face.FACE_2D_X_COLUMNS].mean()
    y = face_data.loc[(frame, face_id), face.FACE_2D_Y_COLUMNS].mean()
    confidence = face_data.loc[(frame, face_id), "confidence"]

    return pose.Keypoint(x, y, confidence)


# def maybe_face_facepos(face_data: pd.DataFrame, frame: int, face_id: int) -> pose.Keypoint:
#     if (frame, face_id) in face_data.index:
#         # In the case of the face, we already filtered out unsuccessful registrations,
#         # so we can skip the confidence check.
#         return get_face_facepos(face_data, frame, face_id)
#     else:
#         return None


def get_error(skeleton_anchor: pose.Keypoint, face_anchor: pose.Keypoint, uncertainty_weight: float) -> float:
    distance = np.sqrt((skeleton_anchor.x - face_anchor.x) ** 2 + (skeleton_anchor.y - face_anchor.y) ** 2)
    uncertainty = 1 - face_anchor.confidence

    return distance + uncertainty_weight * uncertainty


# NOTE: Based on extract-pose.match_keypoints()
def match_faces(
        skeleton_anchors: list[tuple[int, pose.Keypoint]],
        face_anchors: list[tuple[int, pose.Keypoint]],
        uncertainty_weight: float
) -> dict[int, int]:
    """
    Takes in two lists of `(id, anchor)` pairs, and matches them based on distance and face anchor uncertainty.
    Returns a `dict` mapping `skeleton ID => face ID` for the best permutation.
    """

    output = {}

    if (len(skeleton_anchors) == 0) or (len(face_anchors) == 0):
        return output

    lookup : list[list[float]] = [] # skelly => face => error
    for skelly_id, skelly_anchor in skeleton_anchors:
        lookup.append([])
        for face_id, face_anchor in face_anchors:
            lookup[-1].append(get_error(skelly_anchor, face_anchor, uncertainty_weight))

    face_indices = list(range(len(face_anchors)))
    while len(face_indices) < len(skeleton_anchors):
        face_indices.append(-1) # Padding elements (correspond to ignored indices in skeleton_anchors).
    matching_permutations = itertools.permutations(face_indices, r=len(skeleton_anchors))

    best_permutation = None
    best_error = np.inf

    for permutation in matching_permutations:
        error = 0.0
        for (skelly_idx, face_idx) in enumerate(permutation):
            if face_idx >= 0: # Skip dummy -1's added for padding.
                error += lookup[skelly_idx][face_idx]

        if error < best_error:
            best_error = error
            best_permutation = permutation

    if best_permutation is None:
        cli.print("BEST PERMUTATION IS NONE")
    else:
        for (skelly_idx, face_idx) in enumerate(best_permutation):
            if face_idx >= 0: # Skip dummies
                skelly_id, skelly_anchor = skeleton_anchors[skelly_idx]
                face_id, face_anchor = face_anchors[face_idx]
                output[skelly_id] = face_id

    # TODO: Do we need any more processing?

    return output


def process_faces(face_data: pd.DataFrame, skeleton_data: pd.DataFrame) -> pd.DataFrame:
    face_data = face_data[face_data["success"] == 1]

    face_frames = face_data.index.get_level_values("frame").unique().sort_values()
    skelly_frames = skeleton_data.index.get_level_values("frame").unique().sort_values()
    max_frame = max(face_frames[-1], skelly_frames[-1])

    face_std_x = face_data[face.FACE_2D_X_COLUMNS].to_numpy().flatten().std()
    face_std_y = face_data[face.FACE_2D_Y_COLUMNS].to_numpy().flatten().std()
    face_std = max(face_std_x, face_std_y)

    # NOTE: This assumes that the first successful detection of skeletons happens when the children are still in their beginning-of-video orientation.
    #       This is the same assumption done by consolidate-pose, but we could de-couple by reading the ground truth from child-order.csv
    left_child, right_child = pose.get_first_ordered_pair(skeleton_data, id_key="child_id")
    left_face_anchor = seek_first_face(skeleton_data, left_child)
    right_face_anchor = seek_first_face(skeleton_data, right_child)

    output = pd.DataFrame(
        data=0.0,
        columns=face_data.columns,
        index=pd.MultiIndex.from_product(
            iterables=[ range(max_frame), (left_child, right_child) ],
            names=[ "frame", "child_id" ],
        )
    )

    for frame in trange(max_frame):
        left_candidate = maybe_skelly_facepos(skeleton_data, frame, left_child)
        if left_candidate is not None:
            left_face_anchor = left_candidate

        right_candidate = maybe_skelly_facepos(skeleton_data, frame, right_child)
        if right_candidate is not None:
            right_face_anchor = right_candidate

        skeleton_anchors = [ (left_child, left_face_anchor), (right_child, right_face_anchor) ]

        if frame in face_frames:
            face_candidate_ids = face_data.loc[frame].index.get_level_values("face_id").unique().sort_values()
            face_anchors = [ (face_id, get_face_facepos(face_data, frame, face_id)) for face_id in face_candidate_ids ]

            matching = match_faces(skeleton_anchors, face_anchors, uncertainty_weight=face_std)

            if left_child in matching:
                face_left = matching[left_child]
                output.loc[(frame, left_child)] = face_data.loc[(frame, face_left)]

            if right_child in matching:
                face_right = matching[right_child]
                output.loc[(frame, right_child)] = face_data.loc[(frame, face_right)]

    return output


def main() -> None:
    settings = arg_parsing.parse_default_args(description="Post-process the pose data produced by extract-pose, to consolidate it into two named skeletons")

    cli.main_title("CONSOLIDATE FACE")

    if FAILED_VIDEOS_CSV.exists():
        FAILED_VIDEOS_CSV.unlink()

    paths = arg_parsing.process_paths(settings, file_end="-face-data.csv")
    vid_logger = util.FailedVidLogger(cli, csv_path=FAILED_VIDEOS_CSV)

    for video_dir, entries in paths.items():
        cli.chapter(video_dir.stem)

        viz_dir = video_dir / "consolidate-face-viz"
        if viz_dir.exists():
            shutil.rmtree(viz_dir)
        viz_dir.mkdir(exist_ok=False, parents=False)

        for (pair_id, round, face_file) in entries:
            cli.subchapter(f"Pair: {pair_id}; Round: {round}")

            try:
                out_csv = face_file.with_stem(face_file.stem.replace("face-data", "consolidated-face"))
                skeleton_file = face_file.with_stem(face_file.stem.replace("face-data", "consolidated-skeleton"))
                video_file = face_file.with_name(face_file.name.replace("-face-data.csv", ".mp4"))

                assert face_file.is_file()
                assert skeleton_file.is_file()
                assert video_file.is_file()

                face_data     = pd.read_csv(face_file    , index_col=["frame", "face_id"])
                skeleton_data = pd.read_csv(skeleton_file, index_col=["frame", "child_id", "joint"])

                cli.section("Processing")
                processed = process_faces(face_data, skeleton_data)
                processed.to_csv(out_csv)

                cli.section("Visualizing")
                face.visualize(video_file, viz_dir, processed, create_overlay=True, create_anonymized=False, create_feature=False)
            except Exception as e:
                vid_logger.add_failed(face_file, repr(e))
                continue

    cli.big_divisor()
    cli.section("Failed Videos")
    cli.print(vid_logger.failed_vids)


if __name__ == "__main__":
    main()
