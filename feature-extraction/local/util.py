import re
import subprocess
import random
import colorsys
from pathlib import Path
from typing import Tuple, Optional

import pandas as pd
from pretty_cli import PrettyCli


CLI_YELLOW = "\u001b[33m"
CLI_RED    = "\u001b[31m"
CLI_RESET  = "\u001b[0m"

VIDEO_DIRS = [ Path("left-cam"), Path("right-cam"), Path("frontal-cam") ]


def run_command(cli: PrettyCli, command: str) -> bool:
    """
    Pretty-prints the supplied command, executes it, and pretty-prints a message if it errors.

    Returns the success status (`True` if command ran successfully, `False` otherwise).
    """

    cli.print(f"{CLI_YELLOW}{command}{CLI_RESET}")
    completed_process = subprocess.run(command, shell=True)

    if completed_process.returncode != 0:
        cli.print(f"{CLI_RED}Command failed with error code: {completed_process.returncode}{CLI_RESET}")
        return False

    return True


class UidProvider:
    """Provides random 32-bit unsigned int IDs, and guarantees to never return the same ID twice."""

    MAX_UID = 0xFF_FF_FF_FF

    def __init__(self):
        self.uids = []

    def get_uid(self) -> int:
        while True:
            id = random.randint(0, UidProvider.MAX_UID) # Max 32-bit unsigned int. No good reason.
            if id not in self.uids:
                self.uids.append(id)
                return id


class FailedVidLogger:
    """Ingests videos into a Pandas DataFrame accessible as `self.failed_vids`; keeps an up-to-date record in disk at the given `csv_path`."""
    def __init__(self, cli: PrettyCli, csv_path: Path):
        # self.failed_vids = pd.DataFrame()
        self.csv_path = csv_path
        self.cli = cli

        # Create a fresh file at the location, so it will exist even if no failed videos were detected.
        header = pd.DataFrame({"video": [], "reason": []}).set_index("video")
        header.to_csv(csv_path)

        self.failed_vids = header

    def add_failed(self, vid: Path, reason: str) -> None:
        row = pd.DataFrame({ "video" : [ vid.stem ], "reason" : [ reason ] }).set_index("video")

        if self.csv_path.is_file():
            row.to_csv(self.csv_path, mode="a", header=False)
        else:
            row.to_csv(self.csv_path)

        self.failed_vids = pd.concat([ self.failed_vids, row ])
        self.cli.print(f"{CLI_RED}Video failed; skipping. Reason: {reason}{CLI_RESET}")


# Linear Congruential Generator with numbers taken from GLIBC.
# https://sourceware.org/git/?p=glibc.git;a=blob;f=stdlib/random_r.c
# https://en.wikipedia.org/wiki/Linear_congruential_generator
LCG_MODULO = 0x80_00_00_00
def glibc_lcg(seed: int) -> int:
    """
    Uses a Linear Congruential Generator (LCG) to return a hash of `seed`.
    * Hash in range `[0, LCG_MODULO - 1]`.
    * Numbers based on GLIBC implementation of `rand()`.
    """
    return (seed * 1103515245 + 12345) % LCG_MODULO
