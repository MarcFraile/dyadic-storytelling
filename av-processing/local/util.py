import subprocess
import random
import colorsys
from typing import Tuple

from pretty_cli import PrettyCli


CLI_YELLOW = "\u001b[33m"
CLI_RED    = "\u001b[31m"
CLI_RESET  = "\u001b[0m"

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
    MAX_UID = 0xFF_FF_FF_FF

    def __init__(self):
        self.uids = []

    def get_uid(self) -> int:
        while True:
            id = random.randint(0, UidProvider.MAX_UID) # Max 32-bit unsigned int. No good reason.
            if id not in self.uids:
                self.uids.append(id)
                return id


# Linear Congruential Generator with numbers taken from GLIBC.
# https://sourceware.org/git/?p=glibc.git;a=blob;f=stdlib/random_r.c
# https://en.wikipedia.org/wiki/Linear_congruential_generator
LCG_MODULO = 0x80_00_00_00
def glibc_lcg(seed: int) -> int:
    """
    Uses a Linear Congruential Generator (LCG) to return a hash of `seed`.
    * Hash in range `[0, LCG_MODULO - 1)`.
    * Numbers based on GLIBC implementation of `rand()`.
    """
    return (seed * 1103515245 + 12345) % LCG_MODULO


def fraction_to_uint8(channel: float) -> int:
    """
    Convert a float in range `[0, 1]` to a uint8 in range `[0, 255]`.
    """
    return min(255, int(256 * channel))


def get_rgb_from_id(id: int) -> Tuple[int, int, int]:
    """
    Returns a pseudo-random color based on `id`.
    * Color returned as an RGB uint8 tuple `(red, green, blue)` in range `[0, 255]`.
    * Color guaranteed to have maximum saturation and value in HSV space.
    """
    hue = glibc_lcg(glibc_lcg(id)) / LCG_MODULO # Double trip through the LCG for good measure.
    rgb_01 = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    return tuple( fraction_to_uint8(channel) for channel in rgb_01 )
