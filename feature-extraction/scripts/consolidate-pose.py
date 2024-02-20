#!/bin/env -S python3


import shutil
from pathlib import Path

import pandas as pd
from tqdm import tqdm
from pretty_cli import PrettyCli

from local import util, pose, arg_parsing


FAILED_VIDEOS_CSV = Path("./failed-videos-consolidate-pose.csv")
CHILD_ORDER_CSV = Path("child-order.csv")

cli = PrettyCli()


def process_file(left_child: int, right_child: int, data: pd.DataFrame) -> pd.DataFrame:
    cli.section("Processing File")

    # ---------------- Initialization ---------------- #

    frames = data.index.get_level_values("frame").unique().sort_values()
    max_frame = frames[-1]

    # Create a zero-initialized DataFrame that already contains all the entries.
    # It includes rows for every frame, even in the rare occasion that a frame is not listed in the original data.
    # It also enforces the assumption that we only have two known IDs in the output, and orders them left-to-right.
    output = pd.DataFrame(
        data=0.0,
        columns=[ "x", "y", "confidence" ],
        index=pd.MultiIndex.from_product(
            iterables=[ range(max_frame), (left_child, right_child), pose.JOINTS ],
            names = [ "frame", "child_id", "joint" ],
        )
    )

    leftmost_id, rightmost_id = pose.get_first_ordered_pair(data)

    # ---------------- Main Loop ---------------- #

    # Lookup table used to map (external ID) => (set of known automatic IDs)
    id_map : dict[int, set[int]] = {
        left_child  : { leftmost_id  },
        right_child : { rightmost_id },
    }

    for frame in tqdm(frames):
        frame_data : pd.DataFrame = data.loc[frame]
        automatic_ids = frame_data.index.get_level_values("person_id").unique()
        assert 0 <= len(automatic_ids) <= 2

        pending_child_ids = set(key for key in id_map)
        pending_auto_ids = set(automatic_ids)

        def update_skeleton(child_id: int, auto_id: int) -> None:
            pending_child_ids.remove(child_id)
            pending_auto_ids.remove(auto_id)
            id_map[child_id].add(auto_id)
            for joint in pose.JOINTS:
                output.loc[(frame, child_id, joint), :] = frame_data.loc[(auto_id, joint), :]

        # Attempt to propagate Child IDs forward based on known Automatic IDs.
        for auto_id in automatic_ids:
            for (child_id, known_ids) in id_map.items():
                if auto_id in known_ids:
                    update_skeleton(child_id, auto_id)
                    break

        # If all Child IDs have been assigned, we should be done.
        if len(pending_child_ids) == 0:
            assert len(pending_auto_ids) == 0
            continue

        # If only one is left in each set, just match them (the other child has already been assigned).
        if len(pending_child_ids) == 1 and len(pending_auto_ids) == 1:
            update_skeleton(next(pending_child_ids), next(pending_auto_ids))
            continue

        # TODO: Figure out the matching.

    return output


def visualize(viz_dir: Path, vid: Path, processed: pd.DataFrame) -> None:
    cli.section("Visualizing")

    frames = processed.index.get_level_values("frame").unique()
    skeletons = [
        [
            pose.get_skeleton(processed, frame, id)
            for id in processed.loc[frame].index.get_level_values("child_id").unique()
        ]
        for frame in frames
    ]

    pose.visualize_skeletons(viz_dir, vid, skeletons, id_style="dec", create_overlay=True, create_feature=False)


def main() -> None:
    settings = arg_parsing.parse_default_args(description="Post-process the pose data produced by extract-pose, to consolidate it into two named skeletons")

    cli.main_title("CONSOLIDATE POSE")

    for video_dir in util.VIDEO_DIRS:
        assert video_dir.is_dir(), f"Video dir not found: {video_dir}"

    assert CHILD_ORDER_CSV.is_file()

    if FAILED_VIDEOS_CSV.exists():
        FAILED_VIDEOS_CSV.unlink()

    paths = arg_parsing.process_paths(settings, file_end="-skeleton-data.csv")
    video_logger = util.FailedVidLogger(cli, csv_path=FAILED_VIDEOS_CSV)
    child_order = pd.read_csv(CHILD_ORDER_CSV, index_col=["pair_id", "round"])

    for video_dir, entries in paths.items():
        cli.chapter(video_dir.stem)

        viz_dir = video_dir / "consolidate-pose-viz"
        if viz_dir.exists():
            shutil.rmtree(viz_dir)
        viz_dir.mkdir(parents=False, exist_ok=False)

        for (pair_id, round, skeleton_file) in entries:
            cli.subchapter(f"Pair ID: {pair_id}; Round: {round}")

            try:
                (left_child, right_child) = child_order.loc[(pair_id, round), ["left_child", "right_child"]]

                out_csv = video_dir / f"{video_dir.name}-{pair_id}-planning-{round}-consolidated-skeleton.csv"
                vid = video_dir / f"{video_dir.name}-{pair_id}-planning-{round}.mp4"

                data = pd.read_csv(skeleton_file, index_col=["frame", "person_id", "joint"])

                processed = process_file(left_child, right_child, data)
                processed.to_csv(out_csv)

                visualize(viz_dir, vid, processed)
            except Exception as e:
                video_logger.add_failed(skeleton_file, repr(e))
                continue

    cli.big_divisor()
    cli.section("Failed Videos")
    cli.print(video_logger.failed_vids)


if __name__ == "__main__":
    main()
