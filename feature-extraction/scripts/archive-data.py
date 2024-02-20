#!/bin/env -S python3


import argparse
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from pretty_cli import PrettyCli


VIDEO_DIRS = [ Path("./left-cam"), Path("./right-cam"), Path("./frontal-cam") ]
VIZ_DIRS = [ "pose_viz", "face_viz", "custom_face_viz", "consolidate-pose-viz", "consolidate-face-viz" ]
FAILURE_REPORTS = [
    Path("./failed-videos-extract-pose.csv"),
    Path("./failed-videos-extract-face.csv"),
    Path("./failed-videos-consolidate-pose.csv"),
    Path("./failed-videos-consolidate-face.csv"),
]
BACKUP_ROOT = Path("./data-backup")


@dataclass
class Settings:
    copy: bool


cli = PrettyCli()


def parse_args() -> Settings:
    parser = argparse.ArgumentParser(description="Moves (default) or copies the generated CSV files and visualizations to a timestamped directory in data-backup/")
    parser.add_argument("--copy", action="store_true", help="Copy the original files instead of moving them.")
    raw_args = parser.parse_args()
    settings = Settings(copy=raw_args.copy)
    return settings


def move_or_copy(src: Path, dst: Path, settings: Settings) -> None:
    assert src.exists()

    if settings.copy:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)
    else:
        shutil.move(src, dst)


def move_if_exists(in_dir: Path, out_dir: Path, item: str, settings: Settings) -> None:
    in_path = in_dir / item
    out_path = out_dir / item

    if in_path.exists():
        cli.print(f"Moving '{item}'")
        move_or_copy(src=in_path, dst=out_path, settings=settings)


def main() -> None:
    settings = parse_args()

    cli.main_title("ARCHIVE DATA")

    for in_dir in VIDEO_DIRS:
        assert in_dir.is_dir()

    if not BACKUP_ROOT.is_dir():
        BACKUP_ROOT.mkdir(parents=False, exist_ok=False)

    now = datetime.now()
    time_string = now.strftime("%Y%m%dT%H%M%S")
    out_root = Path(BACKUP_ROOT / time_string)
    out_root.mkdir(parents=False, exist_ok=False)

    for in_dir in VIDEO_DIRS:
        cli.section(str(in_dir))

        out_dir = out_root / in_dir.name
        out_dir.mkdir(parents=False, exist_ok=False)

        for in_file in in_dir.iterdir():

            if not in_file.is_file():
                continue
            if not (in_file.suffix.lower() == ".csv"):
                continue

            out_file = out_dir / in_file.name
            move_or_copy(src=in_file, dst=out_file, settings=settings)

        for viz_dir in VIZ_DIRS:
            move_if_exists(in_dir, out_dir, item=viz_dir, settings=settings)

    for report in FAILURE_REPORTS:
        move_if_exists(in_dir=report.parent, out_dir=out_root, item=report.name, settings=settings)


if __name__ == "__main__":
    main()
