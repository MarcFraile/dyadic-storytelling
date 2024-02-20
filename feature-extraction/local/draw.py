import colorsys
from typing import TypeAlias

from local import util


RGB  : TypeAlias = tuple[int, int, int]
RGBA : TypeAlias = tuple[int, int, int, int]


def fraction_to_uint8(channel: float) -> int:
    """
    Convert a float in range `[0, 1]` to a uint8 in range `[0, 255]`.
    """
    return min(255, int(256 * channel))


def get_rgb_from_id(id: int) -> RGB:
    """
    Returns a pseudo-random color based on `id`.
    * Color returned as an RGB uint8 tuple `(red, green, blue)` in range `[0, 255]`.
    * Color guaranteed to have maximum saturation and value in HSV space.
    """
    hue = util.glibc_lcg(util.glibc_lcg(id)) / (util.LCG_MODULO - 1) # Double trip through the LCG for good measure.
    rgb_01 = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    return tuple( fraction_to_uint8(channel) for channel in rgb_01 )
