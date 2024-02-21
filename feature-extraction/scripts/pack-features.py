#!/bin/env -S python3


import itertools
import shutil
from pathlib import Path
from datetime import datetime

import pandas as pd
from tqdm import tqdm
from pretty_cli import PrettyCli

from local.arg_parsing import PAIR_REGEX


BACKUP_DIR = Path("./data-backup")
PACKED_DIR = Path("./packed")
ORDER_CSV  = Path("./child-order.csv")
PAIRS_CSV  = Path("./pairs-with-distances.csv")

cli = PrettyCli()


def main() -> None:
    cli.main_title("PACK FEATURES")

    assert BACKUP_DIR.is_dir()
    assert ORDER_CSV.is_file()
    assert PAIRS_CSV.is_file()

    if PACKED_DIR.exists():
        shutil.rmtree(PACKED_DIR)
    PACKED_DIR.mkdir(parents=False, exist_ok=False)

    order = pd.read_csv(ORDER_CSV, index_col="pair_id")
    pairs_csv = pd.read_csv(PAIRS_CSV, index_col="pair_id")

    cli.chapter("Fetching Backup")

    # Assumption: backups are named such that lexicographical order matches time order.
    backups = sorted(subdir for subdir in BACKUP_DIR.iterdir() if subdir.is_dir())
    assert len(backups) > 0
    latest = backups[-1]

    cli.print(f"Latest backup: {latest.name}")

    cli.chapter("Staging Files")

    pairs_per_source = dict()

    for source in [ "left-cam", "right-cam" ]:
        cli.section(source)

        in_dir = latest / source
        assert in_dir.is_dir()

        out_dir = PACKED_DIR / source.replace("cam", "camera")
        out_dir.mkdir(parents=False, exist_ok=False)

        files = [ file for file in in_dir.iterdir() if file.is_file() and (file.suffix == ".csv") and ("consolidated-" in file.stem) ]
        pairs_per_source[source] = sorted(set(PAIR_REGEX.search(file.stem).group(0) for file in files))

        for in_file in tqdm(files):
            out_file = out_dir / in_file.name.replace("consolidated-", "").replace("cam", "camera").replace("skeleton", "pose")
            shutil.copy2(in_file, out_file)

    cli.chapter("Compiling Metadata")

    for (first, second) in itertools.combinations(pairs_per_source.keys(), 2):
        assert pairs_per_source[first] == pairs_per_source[second]
    pairs = pairs_per_source[next(iter(pairs_per_source.keys()))]

    pair_info = pd.DataFrame([
        {
            "pair_id"   : pid,
            "condition" : "high_rapport" if "P" in pid else "low_rapport",
            "distance"  : pairs_csv.loc[pid, "distance"],
            "year"      : int(pid[1]),
            "rounds"    : order.loc[pid, "round"].max(),
            "child_1"   : f"{pairs_csv.loc[pid, 'child_1']:02}",
            "child_2"   : f"{pairs_csv.loc[pid, 'child_2']:02}",
        } for pid in pairs
    ]).set_index("pair_id")

    cli.print(pair_info)
    pair_info.to_csv(PACKED_DIR / "pair_info.csv")

    cli.chapter("Packing")
    cli.print("This will take a long time...")

    tic = datetime.now()
    shutil.make_archive(PACKED_DIR, "zip", PACKED_DIR)
    toc = datetime.now()

    cli.print(f"Zip lasted for: {toc - tic}")


if __name__ == "__main__":
    main()
