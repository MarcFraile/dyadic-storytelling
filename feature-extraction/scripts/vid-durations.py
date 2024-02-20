#!/bin/env -S python3


# Video Duations
# ==============
#
# Basic video duration extractor (based on file metadata).


import warnings
import pandas as pd
import imageio.v3 as iio
from tqdm import tqdm
from pretty_cli import PrettyCli
from local import arg_parsing


cli = PrettyCli()


def main() -> None:
    settings = arg_parsing.parse_default_args(description="Process the videos using Py-Feat.")

    cli.main_title("VID DURATIONS")

    paths = arg_parsing.process_paths(settings, ".mp4")

    for vid_dir, entries in paths.items():
        cli.chapter(vid_dir.stem)

        data = pd.DataFrame()

        for (pair_id, round, vid_file) in tqdm(entries):

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                meta = iio.immeta(vid_file)
            assert "duration" in meta

            row = pd.DataFrame(data={ "pair_id": pair_id, "round": round, "duration_s": meta["duration"] }, index=[0])
            data = pd.concat([data, row], ignore_index=True)

        data.set_index(["pair_id", "round"], inplace=True)
        cli.print(data)
        data.to_csv(f"{vid_dir}-durations.csv")


if __name__ == "__main__":
    main()
