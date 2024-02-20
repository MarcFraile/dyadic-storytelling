import re
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from local import util


PAIR_REGEX = re.compile(pattern="[PN][23]\d{2}")


@dataclass
class DefaultSettings:
    pair_ids   : Optional[list[str]]  = None
    video_dirs : Optional[list[Path]] = None


def check_one_pair_id(arg_value: str) -> str:
    """
    `argparse` type-checker for arguments consisting of a single pair ID.
    """
    if not PAIR_REGEX.match(arg_value):
        raise argparse.ArgumentTypeError(f"Pair codes should follow the pattern /{PAIR_REGEX.pattern}/. Found non-matching argument: '{arg_value}'.")
    return arg_value


def check_list(arg_value: str) -> list[str]:
    """
    `argparse` type-checker for arguments consisting of a comma-separated list.
    * Returns a sorted list of unique entries after validation.
    """

    # NOTE: First we make it into a set to remove duplicates, then into a sorted list to ensure a canonical ordering.
    items = sorted({ item.strip() for item in arg_value.strip().split(",") if len(item.strip()) > 0 })

    if len(items) == 0:
        raise argparse.ArgumentTypeError(f"After cleanup, the list was empty: {arg_value}")

    return items


def check_pair_id_list(arg_value: str) -> list[str]:
    """
    `argparse` type-checker for arguments consisting of a comma-separated list of pair IDs.
    * Returns a sorted list of unique IDs after cleanup and validation.
    """

    pair_ids = [ pair_id.upper() for pair_id in check_list(arg_value) ]

    for id in pair_ids:
        if not PAIR_REGEX.match(id):
            raise argparse.ArgumentTypeError(f"Pair codes should follow the pattern /{PAIR_REGEX.pattern}/. Found non-matching argument: {id}")

    return pair_ids


def check_path(arg_value: str) -> Path:
    """
    `argparse` type-checker for arguments consisting of a single path.
    * Returns a `Path`s after validation.
    """
    path = Path(arg_value)

    if not path.exists():
        raise argparse.ArgumentTypeError(f"Paths should correspond to existing files or dirs. Found non-existing path: {path}")

    return path

def check_dir_list(arg_value: str) -> list[Path]:
    """
    `argparse` type-checker for arguments consisting of a comma-separated list of paths.
    * Returns a sorted list of `Path`s after cleanup and validation.
    """
    paths = [ check_path(path) for path in check_list(arg_value) ]
    return paths


def check_vid_dirs(arg_value: str) -> list[Path]:
    paths = check_dir_list(arg_value)

    for path in paths:
        if path not in util.VIDEO_DIRS:
            raise argparse.ArgumentTypeError(f"Video dirs should be one of {[str(dir) for dir in util.VIDEO_DIRS]}; found: {path}")

    return paths


def get_default_parser(description: str) -> argparse.ArgumentParser:
    """
    Returns a default parser with options for only processing a list of pairs, or only processing a list of video dirs.
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("--only_pairs", type=check_pair_id_list, help="Comma-separated list (no spaces) of pairs to process. If supplied, only processes those pairs.")
    parser.add_argument("--only_dirs", type=check_vid_dirs, help="Comma-separated list (no spaces) of video dirs to process. If supplied, only processes those videos.")

    return parser


def get_default_settings(raw_args: argparse.Namespace) -> DefaultSettings:
    """
    Processes the default options (see `get_default_parser()`) and returns an initialized `DefaultSettings` object.
    """
    return DefaultSettings(
        pair_ids   = raw_args.only_pairs,
        video_dirs = raw_args.only_dirs,
    )


def parse_default_args(description: str) -> DefaultSettings:
    """
    Parses the default arguments.
    """

    parser = get_default_parser(description)
    raw_args = parser.parse_args()
    return get_default_settings(raw_args)


def process_paths(settings: DefaultSettings, file_end: str) -> dict[Path, list[tuple[str, int, Path]]]:
    """
    Returns a dict with the following structure:
    * The keys are the video dirs we should iterate over.
    * The values are sorted lists of `(pair_id, round, file)` tuples, where `file` are `Path`s in the corresponding dir.
      Files are selected based on `file_end`.

    To select which files to include, the following regex is applied to the file name:

    `[a-z]+-[a-z]+-([PN][23]\d{2})-planning-(\d)[file_end]`

    `settings` is used to conditionally filter which dirs and/or pair IDs we select:
    * If `settings.video_dirs` is not `None`, keeps only the listed dirs.
    * If `settings.pair_ids` is not `None`, keeps only the listed pair IDs.
    """
    regex = re.compile(f"[a-z]+-[a-z]+-([PN][23]\d{{2}})-planning-(\d){file_end}")

    output: dict[Path, list[tuple[str, int, Path]]] = {}

    video_dirs = util.VIDEO_DIRS
    if settings.video_dirs is not None:
        video_dirs = settings.video_dirs

    for dir in video_dirs:
        assert dir.is_dir()
        dir = dir.resolve() # Make into absolute path

        data_files = []

        for file in dir.iterdir():
            match = regex.match(file.name)
            if not match:
                continue

            pair_id = match[1]
            round = int(match[2])

            data_files.append((pair_id, round, file))

        if settings.pair_ids is not None:
            # Keep only entries with pair IDs in the list.
            data_files = sorted(
                (pair_id, round, file)
                for (pair_id, round, file) in data_files
                if pair_id in settings.pair_ids
            )
        else:
            data_files.sort()

        output[dir] = data_files

    return output
