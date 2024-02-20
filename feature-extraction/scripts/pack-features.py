#!/bin/env -S python3


import shutil
from pathlib import Path
from datetime import datetime

from tqdm import tqdm
from pretty_cli import PrettyCli


BACKUP_DIR = Path("./data-backup")
PACKED_DIR = Path("./packed")

cli = PrettyCli()


def main() -> None:
    cli.main_title("PACK FEATURES")

    assert BACKUP_DIR.is_dir()

    if PACKED_DIR.exists():
        shutil.rmtree(PACKED_DIR)
    PACKED_DIR.mkdir(parents=False, exist_ok=False)

    cli.chapter("Fetching Backup")

    # Assumption: backups are named such that lexicographical order matches time order.
    backups = sorted(subdir for subdir in BACKUP_DIR.iterdir() if subdir.is_dir())
    assert len(backups) > 0
    latest = backups[-1]

    cli.print(f"Latest backup: {latest.name}")

    cli.chapter("Staging Files")

    for source in [ "left-cam", "right-cam" ]:
        cli.section(source)

        in_dir = latest / source
        assert in_dir.is_dir()

        out_dir = PACKED_DIR / source.replace("cam", "camera")
        out_dir.mkdir(parents=False, exist_ok=False)

        files = [ file for file in in_dir.iterdir() if file.is_file() and (file.suffix == ".csv") and ("consolidated-" in file.stem) ]

        for in_file in tqdm(files):
            out_file = out_dir / in_file.name.replace("consolidated-", "").replace("cam", "camera").replace("skeleton", "pose")
            shutil.copy2(in_file, out_file)

    cli.chapter("Packing")

    tic = datetime.now()
    shutil.make_archive(PACKED_DIR, "zip", PACKED_DIR)
    toc = datetime.now()

    cli.print(f"Zip lasted for: {toc - tic}")


if __name__ == "__main__":
    main()
