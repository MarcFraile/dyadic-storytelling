#!/bin/env -S python3


# Extract Pose
# ============
#
# Extract skeleton keypoints from each video, using OpenPose.
# NOTE: This should be run from the dataset top-level (i.e. the folder containing left-cam/ and right-cam/).


import os, shutil
import json
import math
import itertools
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd
from tqdm import tqdm

from pretty_cli import PrettyCli
from local import util, pose, arg_parsing
from local.pose import JOINTS, JOINTS_CATEGORICAL, Keypoint, Skeleton


FAILED_VIDEOS_CSV = Path("./failed-videos-extract-pose.csv")

cli = PrettyCli()
uid_provider = util.UidProvider()


@dataclass
class Settings(arg_parsing.DefaultSettings):
    openpose_root: Path = Path("/dev/null")


def parse_args() -> Settings:
    parser = arg_parsing.get_default_parser(description="Extract OpenPose features from all videos. For each video, clean and aggregate the data, giving a continuous identity over time to the skeletons.")
    parser.add_argument("openpose_root", type=arg_parsing.check_path, help="Path to the root of the local OpenPose installation.")

    raw_args = parser.parse_args()

    default_settings = arg_parsing.get_default_settings(raw_args)
    openpose_root = raw_args.openpose_root.resolve()
    assert openpose_root.is_dir()

    settings = Settings(default_settings.pair_ids, default_settings.video_dirs, openpose_root)
    return settings


def consume_person_data(raw_person: Any) -> Skeleton:
    """
    Takes in a dict corresponding to the JSON data produced by OpenPose for one person in one frame, and produces a skeleton.

    Extensive validation is done with asserts.
    """

    assert isinstance(raw_person, dict), f"Expected `raw_person` argument to be a `dict`, but found: {type(raw_person)}"
    assert "pose_keypoints_2d" in raw_person, f"Expected dict `raw_person` to contain the field `'pose_keypoints_2d'`, but missing. Found keys: {raw_person.keys()}"

    raw_points = raw_person["pose_keypoints_2d"]

    assert isinstance(raw_points, list), f"Expected `raw_person['pose_keypoints_2d']` to be a `list`, but found: {type(raw_points)}"
    assert len(raw_points) == 3 * len(JOINTS), f"Expected {3 * len(JOINTS)} entries in 'pose_keypoints_2d'; found: {len(raw_points)}"

    joint_data = {
        joint: Keypoint(
            x          = raw_points[3 * idx + 0],
            y          = raw_points[3 * idx + 1],
            confidence = raw_points[3 * idx + 2],
        )
        for (idx, joint) in enumerate(JOINTS)
    }

    return Skeleton(joints=joint_data)


def consume_file(file_path: Path) -> list[Skeleton]:
    """
    Takes in the path to a JSON file containing the OpenPose output for one frame, and returns a list of skeletons detected in that frame.

    Extensive validation is done with asserts.
    """

    with open(file_path, "r") as file_handle:
        file_contents = json.load(file_handle)

    assert isinstance(file_contents, dict), f"Expected loaded JSON to be a dict, but found: {type(file_contents)}"
    assert "people" in file_contents, f"Expected loaded JSON to contain the field `'people'`, but missing. Found keys: {file_contents.keys()}"
    raw_people = file_contents["people"]

    assert isinstance(raw_people, list), f"Expected `'people'` field to be a list, but found: {type(raw_people)}"
    skeletons = [ consume_person_data(person) for person in raw_people ]

    return skeletons


def match_keypoints(previous: list[Skeleton], current: list[Skeleton]) -> float:
    """
    Uses weighted Root Mean Square Error (RMSE) matching to find the best combination of 'this old skeleton corresponds to this new skeleton'.

    * The matching minimizing the overall sum of the RMSE is chosen.
    * The RMSE is weighted according to each joint's confidence score (see `get_rmse()`).
    * Returns the salience score (second best RMSE) / (best RMSE). Since lower RMSE is better, a higher score is better.
    * If `len(current) > len(previous)`, new IDs are assigned as needed.
    * If either list is empty, the score is set to NaN.
    """

    if len(current) == 0: # No new skeletons, nothing to match.
        return math.nan

    elif len(previous) == 0: # No old skeletons to match to. Set score to NaN and skip main processing (there is some processing needed at the end).
        score = math.nan

    else: # There are both old and new skeletons. We need to run the proper matching algorithm.
        lookup : list[list[float]] = [] # old_idx => new_idx => RMSE.
        for old_idx, old_skelly in enumerate(previous):
            lookup.append([])
            for new_idx, new_skelly in enumerate(current):
                lookup[old_idx].append(pose.get_rmse(old_skelly, new_skelly))

        best_permutation = None
        best_rmse = np.inf
        second_rmse = np.inf

        # We want an iterator that gives us all possible ways to match the old skeletons to the new ones.
        # We can do this with itertools.permutations(iterator, r). It returns all possible tuples made of unique elements in `iterator`, such that `len(tuple) = r`.
        # We then interpret each tuple as a mapping `tuple[old_idx] = new_idx`.

        new_indices = [ idx for idx in range(len(current)) ]

        # If there were more old skeletons than there are new, we need to add dummies.
        while len(new_indices) < len(previous):
            new_indices.append(-1)

        matching_permutations = itertools.permutations(new_indices, r=len(previous))

        for permutation in matching_permutations:

            rmse = 0.0
            for (old_idx, new_idx) in enumerate(permutation):
                if new_idx >= 0: # Unmatched old skeletons indicated by new_idx = -1.
                    rmse += lookup[old_idx][new_idx]

            if rmse < best_rmse:
                best_permutation = permutation
                second_rmse = best_rmse
                best_rmse = rmse
            elif rmse < second_rmse:
                second_rmse = rmse

        score = second_rmse / best_rmse

        # assert best_permutation is not None, "Expected `best_permutation` to be != None"
        if best_permutation is None: # DEBUG: Let the default "new skeleton" code below reset the skeletons for now. Should at least let us see what's happening.
            cli.print("BEST PERMUTATION IS NONE")
        else:
            for (old_idx, new_idx) in enumerate(best_permutation):
                if new_idx >= 0:
                    current[new_idx].id = previous[old_idx].id

    # If len(previous) < len(current), or if the matching procedure failed, there are unmatched skeletons that need new IDs.
    for new_skelly in current:
        if new_skelly.id is None:
            new_skelly.id = uid_provider.get_uid()

    return score


class IdBuffer:
    def __init__(self):
        self.buffer : set[int] = set()

    def update(self, skeletons: Iterable[Skeleton]) -> None:
        assert all(skelly.id is not None for skelly in skeletons) # Assumption: all IDs are non-null.

        new_ids = set(skelly.id for skelly in skeletons)
        lost = self.buffer.difference(new_ids)
        gained = new_ids.difference(self.buffer)

        if len(gained) == 0: # All new IDs were already in buffer
            return # Do nothing
        # NOTE: The next bit kind of assumes there are exactly 2 skeletons at most at any point, and kind of doesn't.
        #       This half-half pattern is repeated all over the place, and it's suboptimal.
        elif len(self.buffer) > 1 and len(lost) == 1 and len(gained) == 1: # There is more than one skeleton, and there is exactly one mismatch in each set.
            lost_id = lost.pop()
            gained_id = gained.pop()

            skelly = next(skelly for skelly in skeletons if skelly.id == gained_id) # Recover the skeleton that is mismatched.
            skelly.id = lost_id # Update the skeleton's ID to the missing ID.
            return # No update on the buffer, since we updated the skeleton.
        else:
            self.buffer = new_ids # It's not an easily solved, so we stick it.
            return


# TODO: This is pretty coupled with the code in main(). Would be nice to decouple it more.
def process_vid_json(video_dir: Path, json_dir: Path, vid: Path) -> tuple[ list[list[Skeleton]], list[float] ]:
    """
    Process the OpenPose output of one video, save it to CSV, and return the skeleton data and scores.
    * This should be run after OpenPose has been called on `vid`, and the frame-by-frame JSON files saved to `json_folder`.
    * Output 0 (skeletons) maps frame idx => list of found skeletons in that frame.
    * Output 1 (scores) maps frame idx => score of the matching in that frame.
    """

    # NOTE: Each frame gets its own JSON file. The top-level object has a "people" field that's an array. Each entry in the array is the data for one person in one frame.
    #       Based on cursory exploration of the OpenPose output, the only field we care about is "pose_keypoints_2d".
    #       This is a long list of numbers that's secretly made of triplets (x, y, confidence), with (x, y) either in range [-1,+1] or pixel-range, and confidence in range [0,1].
    #       It uses the BODY_25 model by default, which has the keypoints specified in JOINTS (encoded in that order).
    #       We parse each frame into a dict with proper names, and aggregate accross all frames into a single file per video.
    #       It will be humongous, but such is life.

    assert video_dir.is_dir(), f"Expected `video_dir` path to be a (pre-existing) dir: {video_dir}"
    assert json_dir.is_dir(), f"Expected `json_dir` path to be a dir (created by OpenPose): {json_dir}"
    assert vid.is_file(), f"Expected `vid` path to be a file: {vid}"

    json_files = [ file for file in json_dir.iterdir() if file.suffix.lower() == ".json" ]
    json_files.sort()

    # Sanity check: there is a multitude of frames.
    assert len(json_files) > 10, f"Expected to find at least 10 files, found: {len(json_files)}"

    data = pd.DataFrame()
    scores : list[float] = []

    skeletons : list[list[Skeleton]] = [] # frame idx => list of found skeletons.
    id_buffer = IdBuffer() # Used to patch situations where one skeleton is recovered after a few frames out, and the other was always visible.

    for file_idx, file_path in tqdm(enumerate(json_files), desc="frame", total=len(json_files)):

        expected_stem = f"{vid.stem}_{file_idx:012}_keypoints"
        assert file_path.stem == expected_stem, f"Expected file stem '{expected_stem}'; found '{file_path.stem}'."

        old_skeletons = [] if (file_idx == 0) else skeletons[file_idx - 1] # Skeletons from previous frame.
        new_skeletons = consume_file(file_path)
        skeletons.append(new_skeletons)

        score = match_keypoints(old_skeletons, new_skeletons)
        id_buffer.update(new_skeletons)
        scores.append(score)

        for skelly in new_skeletons:
            for joint in JOINTS:
                entry = pd.DataFrame({
                    "frame"      : [ file_idx ],
                    "person_id"  : [ skelly.id ],
                    "joint"      : [ joint ],
                    "x"          : [ skelly.joints[joint].x ],
                    "y"          : [ skelly.joints[joint].y ],
                    "confidence" : [ skelly.joints[joint].confidence ],
                })
                data = pd.concat([ data, entry ], ignore_index=True)

    data["joint"] = data["joint"].astype(JOINTS_CATEGORICAL)
    data = data.set_index([ "frame", "person_id", "joint" ], drop = True).sort_index()
    data.to_csv(video_dir / f"{vid.stem}-skeleton-data.csv")

    score_series = pd.Series(scores, name="score")
    score_series.index.name = "frame"
    score_series.to_csv(video_dir / f"{vid.stem}-skeleton-scores.csv", na_rep="nan")

    cli.print({
        "Detected Individuals"     : len(data.reset_index()["person_id"].unique()),
        "Score (higher is better)" : score_series.describe().to_dict(),
    })

    return skeletons, scores


def main() -> None:
    settings = parse_args()

    cli.main_title("EXTRACT POSE")

    # `resolve()` returns the absolute path.
    failed_videos_csv = FAILED_VIDEOS_CSV.resolve()
    if failed_videos_csv.exists():
        failed_videos_csv.unlink()

    paths = arg_parsing.process_paths(settings, file_end=".mp4")
    video_logger = util.FailedVidLogger(cli, csv_path=failed_videos_csv)

    # OpenPose is very finicky. We need to call it from its project root.
    os.chdir(settings.openpose_root)

    for video_dir, entries in paths.items():
        cli.chapter(video_dir.stem)

        json_dir = video_dir / "tmp_json"
        viz_dir = video_dir / "pose_viz"

        if viz_dir.exists():
            shutil.rmtree(viz_dir)
        viz_dir.mkdir(parents=False, exist_ok=False)

        for (pair_id, round, vid) in entries:
            cli.subchapter(f"Pair: {pair_id}; Round: {round}")

            cli.section("Calling OpenPose")

            if json_dir.is_dir():
                shutil.rmtree(json_dir)

            # NOTE: Relevant OpenPose flags:
            #         --video <file>          - Read input from the video at `file`, instead of the webcam.
            #         --number_people_max <n> - If more than `n` skeletons are detected, return the `n` most likely ones and skip the rest.
            #         --write_json <dir>      - Save the data for each frame as a JSON file in `dir`.
            #         --display 0             - Do not attempt to display a GUI.
            #         --render_pose 0         - Do not attempt to render the skeleton on any source. Incompatible with --write_images <dir>, --write_video <file>.
            #         --write_images <dir>    - Render the skeleton overlaid on each frame, and save it to image files in `dir`. Incompatible with --render_pose 0.
            #         --write_video <file>    - Render the skeleton overlaid on each frame, and save as a video in `file`. Incompatible with --render_pose 0.
            if not util.run_command(cli, f"build/examples/openpose/openpose.bin --video {vid} --write_json {json_dir} --number_people_max 2 --display 0 --render_pose 0"):
                video_logger.add_failed(vid, "OpenPose returned an error code")
                continue # OpenPose errored.

            try:
                cli.section("Processing JSON Data")
                skeletons, scores = process_vid_json(video_dir, json_dir, vid)

                cli.section("Creating Visualization")
                pose.visualize_skeletons(viz_dir, vid, skeletons, id_style="hex", scores=scores, show_joint_names=False, create_overlay=True, create_feature=False)
            except Exception as e:
                video_logger.add_failed(vid, repr(e))
                continue

        if json_dir.is_dir():
            shutil.rmtree(json_dir)

    cli.big_divisor()
    cli.section("Failed Videos")
    cli.print(video_logger.failed_vids)


if __name__ == "__main__":
    main()
