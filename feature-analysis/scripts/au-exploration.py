#!/bin/env -S python3


import colorsys
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Any

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from pretty_cli import PrettyCli


DATA_ROOT = Path("dataset")
PLOT_DIR = Path("plots")

FPS = 25.0
cli = PrettyCli()


def get_common_aus(data: pd.DataFrame) -> list[str]:
    au_c_cols = [ col for col in data.columns if col.endswith("_c") ] # AUXX_c
    au_r_cols = [ col for col in data.columns if col.endswith("_r") ] # AUXX_r

    au_c_set = set(col[:-2] for col in au_c_cols) # AUXX
    au_r_set = set(col[:-2] for col in au_r_cols) # AUXX

    au_common    = sorted(au_c_set.intersection(au_r_set)) # Contained in both sets.
    au_different = sorted(au_c_set.symmetric_difference(au_r_set)) # Contained in one set, but not the other.

    cli.print({ "Common": au_common, "Different": au_different })
    return au_common


def hue_iterator(base_hue: float, steps: int, hue_spread: float = 0.24):#, saturation_spread: float = 0.05, value_spread: float = 0.05):
    for hue in np.linspace(start=base_hue - 0.5 * hue_spread, stop=base_hue + 0.5 * hue_spread, num=steps):
        hue = hue % 1
        yield colorsys.hsv_to_rgb(h=hue, s=1.0, v=1.0)


@dataclass
class Settings:
    source     : str
    pair_id    : str
    game_round : int


def parse_args() -> Settings:
    parser = argparse.ArgumentParser(description="Study the AU distributions in one video.")
    parser.add_argument("source", type=str, help="Video source to consult (left-cam, right-cam, front-cam).")
    parser.add_argument("pair_id", type=str, help="Pair ID for the session under consideration.")
    parser.add_argument("game_round", type=int, help="Round number under consideration.")
    args = parser.parse_args()
    return Settings(args.source, args.pair_id, args.game_round)


def expand_limits(low: float, high: float, padding_fraction: float) -> tuple[float, float]:
    delta = high - low
    return (low - padding_fraction * delta, high + padding_fraction * delta)


def main() -> None:
    settings = parse_args()

    cli.main_title("AU EXPLORATION")

    plt.rcParams["figure.figsize"] = (12, 9)

    cli.section("Selected Session")
    cli.print(asdict(settings))

    cli.section("Basic Stats")

    assert DATA_ROOT.is_dir()

    if not PLOT_DIR.is_dir():
        PLOT_DIR.mkdir(parents=False, exist_ok=False)

    data = pd.read_csv(DATA_ROOT / settings.source / f"{settings.source}-{settings.pair_id}-planning-{settings.game_round}-face-data.csv", index_col=[ "frame", "face_id" ])
    ids = sorted(data.index.get_level_values("face_id").unique())
    max_frame = data.index.get_level_values("frame").max()
    cli.print({ "entries": len(data), "max_frame": max_frame, "ids": data.index.get_level_values("face_id").value_counts().sort_index().to_dict() })

    cli.section("Plot General Values")

    x = np.linspace(start=0, stop=max_frame / FPS, num=max_frame)
    xlim = expand_limits(low=0, high=max_frame / FPS, padding_fraction=0.01)
    binary_ylim = expand_limits(low=0, high=1, padding_fraction=0.05)
    au_ylim = expand_limits(low=0, high=5, padding_fraction=0.05)


    def get_series(column: str, fill_value: Any) -> dict[int, np.ndarray]:
        series = dict()

        for id in ids:
            entry = data.loc[pd.IndexSlice[:, id], column]
            entry = entry.droplevel("face_id", axis=0)
            entry = entry.reindex(range(1, max_frame + 1), fill_value=fill_value).to_numpy()
            series[id] = entry

        return series


    def plot_series(series: dict[int, np.ndarray], ylim: tuple[float, float], base_hue: float) -> None:
        pos = 0
        hue_iter = hue_iterator(base_hue, len(series))

        plt.clf()
        for id, y in series.items():
            pos += 1
            color = next(hue_iter)

            plt.subplot(len(series), 1, pos)

            plt.title(f"Face ID: {id:02}")
            plt.plot(x, y, c=color)
            plt.xlim(xlim)
            plt.ylim(ylim)
            plt.ylabel("value")
            plt.xlabel("seconds")
            plt.tight_layout()

        plt.tight_layout()


    plt.title("Detection Confidence")
    confidence = get_series(column="confidence", fill_value=0)
    plot_series(confidence, ylim=binary_ylim, base_hue=0.50)
    plt.savefig(PLOT_DIR / f"{settings.source}-pair-{settings.pair_id}-round-{settings.game_round}-confidence.png")
    plt.close()

    plt.title("Detection Success")
    success = get_series(column="success", fill_value=0)
    plot_series(success, ylim=binary_ylim, base_hue=0.75)
    plt.savefig(PLOT_DIR / f"{settings.source}-pair-{settings.pair_id}-round-{settings.game_round}-success.png")
    plt.close()

    cli.section("Plot AUs")

    au_common = get_common_aus(data)

    for au_name in au_common:
        cli.subchapter(au_name)

        cli.section("Raw AU Intensity")
        au_intensity = get_series(column=f"{au_name}_r", fill_value=np.nan)

        plt.title(f"Raw {au_name} Intensity")
        plot_series(au_intensity, ylim=au_ylim, base_hue=0.00)
        plt.savefig(PLOT_DIR / f"{settings.source}-pair-{settings.pair_id}-round-{settings.game_round}-raw-{au_name}-intensity.png")
        plt.close()

        cli.section("Raw AU Activation")
        au_activation = get_series(column=f"{au_name}_c", fill_value=np.nan)

        plt.title(f"Raw {au_name} Activation")
        plot_series(au_activation, ylim=binary_ylim, base_hue=0.25)
        plt.savefig(PLOT_DIR / f"{settings.source}-pair-{settings.pair_id}-round-{settings.game_round}-raw-{au_name}-activation.png")
        plt.close()

        # ================================================================ #

        cli.section("Filtered AU Intensity")

        filtered_au_intensity = dict()
        for (id, series) in au_intensity.items():
            filtered_au_intensity[id] = series.copy()
            filtered_au_intensity[id][success[id] == 0] = np.nan

        plt.title(f"Filtered {au_name} Intensity")
        plot_series(filtered_au_intensity, ylim=au_ylim, base_hue=0.00)
        plt.savefig(PLOT_DIR / f"{settings.source}-pair-{settings.pair_id}-round-{settings.game_round}-filtered-{au_name}-intensity.png")
        plt.close()

        cli.section("Filtered AU Activation")

        filtered_au_activation = dict()
        for (id, series) in au_activation.items():
            filtered_au_activation[id] = series.copy()
            filtered_au_activation[id][success[id] == 0] = np.nan

        plt.title(f"Filtered {au_name} Activation")
        plot_series(filtered_au_activation, ylim=binary_ylim, base_hue=0.25)
        plt.savefig(PLOT_DIR / f"{settings.source}-pair-{settings.pair_id}-round-{settings.game_round}-filtered-{au_name}-activation.png")
        plt.close()


if __name__ == "__main__":
    main()
