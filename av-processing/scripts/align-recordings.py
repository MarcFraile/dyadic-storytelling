#!/bin/env -S python3


# Align Recordings
# ================
#
# Align audio and video sources, based on audio content.
# Uses the BBC's audio-offset-finder package: https://github.com/bbc/audio-offset-finder
#
# NOTE: Front cam audio seems to be off by ~200ms. This means the cut will not be perfect, but it's probably good enough.
#       The rest of the sources should be synchronized to ~10ms.


from dataclasses import dataclass
import argparse
import subprocess
import itertools
import shutil
import json
import re
import random
from pathlib import Path
from datetime import timedelta
from typing import Optional

from audio_offset_finder.audio_offset_finder import find_offset_between_files

import librosa
import pandas as pd

from pretty_cli import PrettyCli


CLI_YELLOW = "\u001b[33m"
CLI_RED    = "\u001b[31m"
CLI_RESET = "\u001b[0m"

QUESTIONNAIRE_CSV = Path("Raw/Student Data - Anonymized Questionnaires.csv")

IN_DIR_ROOT  = Path("Clean")
OUT_DIR_ROOT = Path("Cut")

IN_DIRS = {
    "headset_audio_1" : IN_DIR_ROOT / "headset-audio",
    "headset_audio_2" : IN_DIR_ROOT / "headset-audio",
    "left_cam_video"  : IN_DIR_ROOT / "left-cam",
    "right_cam_video" : IN_DIR_ROOT / "right-cam",
    "front_cam_video" : IN_DIR_ROOT / "frontal-cam",
}

OUT_DIRS = {
    "headset_audio_1" : OUT_DIR_ROOT / "headset-audio",
    "headset_audio_2" : OUT_DIR_ROOT / "headset-audio",
    "left_cam_video"  : OUT_DIR_ROOT / "left-cam",
    "right_cam_video" : OUT_DIR_ROOT / "right-cam",
    "front_cam_video" : OUT_DIR_ROOT / "frontal-cam",
}

PAIR_REGEX = re.compile(pattern="[PN][23]\d{2}")

cli = PrettyCli()


@dataclass
class Settings:
    debug             : bool
    should_delete_old : bool
    should_convert    : bool
    pair_ids          : Optional[set[str]]


def parse_args() -> Settings:
    """Uses argparse to process CLI args, and post-processes them into a typed `Settings` object."""

    parser = argparse.ArgumentParser(description="Automatically align the files in 'Clean/' into 'Cut/', based on audio content.\n\nBy default, re-creates the output directory (deletes everything and starts from scratch).")

    parser.add_argument("--debug", action="store_true", help="Set debug behavior.")
    parser.add_argument("--no_convert", action="store_true", help="Skip converting the actual audio and video files.")
    parser.add_argument("--only_pairs", help="Comma-separated list (no spaces) of pairs to process. If list is nonempty, only processes those pairs, and avoids re-creating the output directory.")

    raw_args = parser.parse_args()

    debug             : bool               = raw_args.debug
    should_delete_old : bool               = True
    should_convert    : bool               = (not raw_args.no_convert) # Flip to a positive statement.
    pair_ids          : Optional[set[str]] = None

    if raw_args.only_pairs is not None:
        pair_ids = { pair.strip().upper() for pair in raw_args.only_pairs.strip().split(",") if len(pair.strip()) > 0 }

        if len(pair_ids) == 0:
            pair_ids = None
        else:
            for pair in pair_ids:
                assert PAIR_REGEX.match(pair), f"Pair codes should follow the pattern {PAIR_REGEX.pattern}. Found non-matching pair: '{pair}'."
            should_delete_old = False

    settings = Settings(debug, should_delete_old, should_convert, pair_ids)
    return settings


def main() -> None:
    settings = parse_args()

    cli.main_title("ALIGNING AUDIO")

    # ================ VERIFY FOLDER STRUCTURE ================ #

    assert QUESTIONNAIRE_CSV.is_file()

    assert IN_DIR_ROOT.is_dir()
    for dir in IN_DIRS.values():
        assert dir.is_dir()

    if OUT_DIR_ROOT.exists():
        assert OUT_DIR_ROOT.is_dir()
        if settings.should_delete_old:
            shutil.rmtree(OUT_DIR_ROOT)
    OUT_DIR_ROOT.mkdir(parents=False, exist_ok=True)

    for dir in OUT_DIRS.values():
        dir.mkdir(parents=False, exist_ok=True)

    # ================ LOAD PAIRS FROM SOURCE-OF-TRUTH ================ #

    data = pd.read_csv(QUESTIONNAIRE_CSV)
    pairs = set(data.loc[:, "pair_id"])

    if settings.pair_ids is not None: # Check that no wrong IDs were passed, and limit the IDs to the newly passed ones.
        assert settings.pair_ids.issubset(pairs), f"The following provided pair IDs were not found in the CSV: {settings.pair_ids - pairs}"
        pairs = settings.pair_ids

    if settings.debug: # Limit the population to 4 randomly selected pairs.
        pairs = set(random.sample(population=tuple(pairs), k=4))

    ordered_pairs = sorted(pairs) # Ensure consistent execution order (Python set is randomized).

    # ================ PROCESS RECORDINGS ================ #

    pairs_with_missing_data = []
    all_offsets = pd.DataFrame()

    for pair in ordered_pairs:
        cli.chapter(pair)

        # HACK: We have a wonky pair (P240*) that was supposed to be positive but was a bad pairing (error due to repeating names).
        #       The files are marked with its standard name P240, but the questionnaire data marks it as P240* (with the asterisk) to distinguish it.
        #       We should probably drop the sample, but for now we're just making sure the file names match the pair name.
        if pair == "P240*":
            pair = "P240"

        for round in itertools.count(start=1):
            paths = {
                "headset_audio_1" : IN_DIRS["headset_audio_1"] / f"headset-audio-{pair}-planning-{round}-child-1.mp3",
                "headset_audio_2" : IN_DIRS["headset_audio_2"] / f"headset-audio-{pair}-planning-{round}-child-2.mp3",
                "left_cam_video"  : IN_DIRS["left_cam_video" ] / f"left-cam-{pair}-planning-{round}.mp4",
                "right_cam_video" : IN_DIRS["right_cam_video"] / f"right-cam-{pair}-planning-{round}.mp4",
                "front_cam_video" : IN_DIRS["front_cam_video"] / f"frontal-cam-{pair}-planning-{round}.mp4",
            }
            reference_path = paths["headset_audio_1"]

            # ---------------- Check if Files Present for Round ---------------- #

            missing_files = []

            # Check if files for this round exist, and collect a list of missing ones.
            for (key, path) in paths.items():
                if not path.is_file():
                    missing_files.append(str(path))

            # If there are missing files, we either reached the last round or there is missing data for this pair.
            # Assumption: We will either run into trouble from the start or everything is fine.
            if len(missing_files) > 0:
                if round == 1: # No rounds processed yet: there is trouble
                    pairs_with_missing_data.append({ "pair": pair, "missing_files": missing_files })
                break

            # ---------------- Collect and Process Offsets ---------------- #

            cli.subchapter(f"Round {round}")

            offsets = dict()
            for (key, path) in paths.items():
                offset_data = find_offset_between_files(reference_path, path) # offset > 0 => path starts AFTER reference_path.
                offsets[key] = {
                    "offset_s"   : -offset_data["time_offset"], # offset > 0 => path starts BEFORE reference path (needs to be trimmed by that amount).
                    "score"      : offset_data["standard_score"], # Measure of success. I think I saw somewhere it should be > 10.
                    "duration_s" : librosa.get_duration(path=path), # We don't get it directly from the BBC code, sadly.
                }

            min_offset = min(data["offset_s"] for data in offsets.values())
            for data in offsets.values():
                data["adjusted_offset_s"] = data["offset_s"] - min_offset

            min_duration = min(data["duration_s"] - data["adjusted_offset_s"] for data in offsets.values())

            cli.print({ "Offsets" : offsets, "Min Duration" : min_duration })

            offset_df = pd.DataFrame(offsets).T.reset_index(names="source")
            offset_df["pair"] = pair
            offset_df["round"] = round
            all_offsets = pd.concat([ all_offsets, offset_df ], ignore_index=True)

            # ---------------- Call FFMPEG ---------------- #

            if settings.should_convert:
                for (key, in_path) in paths.items():
                    out_path = OUT_DIRS[key] / in_path.name
                    start_offset = timedelta(seconds=offsets[key]["adjusted_offset_s"])

                    is_audio = (in_path.suffix.lower() == ".mp3")
                    if is_audio: # No flags needed.
                        flags = ""
                    else: # Is video (.mp4)
                        if settings.debug: # Convert quick, within reason.
                            flags = "-preset faster -crf 27"
                        else: # Optimize for quality, within reason.
                            flags = "-preset slow -tune fastdecode -crf 20"

                    command = f"ffmpeg -hide_banner -y -i {in_path} -ss {start_offset} -t {min_duration} {flags} {out_path}"

                    cli.print(f"{CLI_YELLOW}{command}{CLI_RESET}")
                    completed_process = subprocess.run(command, shell=True)

                    if completed_process.returncode != 0:
                        cli.print(f"{CLI_RED}FFMPEG failed with error code: {completed_process.returncode}{CLI_RESET}")

    # ================ SAVE AND REPORT SUMMARY DATA ================ #

    cli.chapter("Summary")

    all_offsets = all_offsets.set_index([ "pair", "round", "source" ], drop=True).sort_index()
    all_offsets.to_csv(OUT_DIR_ROOT / "offsets.csv")

    with open(OUT_DIR_ROOT / "pairs_with_missing_data.json", "w") as file_handle:
        json.dump(pairs_with_missing_data, file_handle, indent=4)

    num_saved_pairs = len(all_offsets.reset_index()["pair"].unique())
    cli.print({
        "Num saved pairs": num_saved_pairs,
        "Num skipped pairs": len(pairs_with_missing_data),
        "Missing Data": { entry["pair"]: entry["missing_files"] for entry in pairs_with_missing_data },
    })


if __name__ == "__main__":
    main()
