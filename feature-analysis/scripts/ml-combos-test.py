#!/bin/env -S python3 -u


# ================================================================ #
# ML COMBOS TEST
# ================================================================ #
# ---------------------------------------------------------------- #
# LEFT CAM Significant Stats After P-Val Adjustment
# ---------------------------------------------------------------- #
#                        p-val   cohen-d
# variable
# AU10_presence_std   0.017746  0.541243
# AU10_presence_q95   0.000410  0.680781
# AU12_presence_std   0.010718  0.558874
# AU12_presence_q95   0.003284  0.604881
# AU25_presence_std   0.043035  0.509586
# AU10_intensity_q95  0.012776  0.552074
# AU12_intensity_std  0.008032  0.563946
# AU12_intensity_q95  0.011002  0.554482
# AU25_intensity_std  0.031784  0.516944
# ---------------------------------------------------------------- #
# The common ground is that AU10 and AU12 have strong reactions
# in the Q95 and in their STD. Since Q95 is used in some of the
# literature I have read, that is an easy to justify choice.
# ---------------------------------------------------------------- #
# RIGHT CAM Significant Stats After P-Val Adjustment
# ---------------------------------------------------------------- #
#                        p-val   cohen-d
# variable
# AU12_presence_std   0.018679  0.544083
# AU12_presence_q95   0.020896   0.55114
# AU26_presence_mean  0.026767  0.523637
# AU26_presence_std   0.003549  0.612068
# AU12_intensity_std    0.0124  0.550851
# AU12_intensity_q95  0.009536  0.560579
# ---------------------------------------------------------------- #
# AU12 shows same response as LEFT CAM, but we get AU26 instead of
# AU10 and AU25. We also get one mean for a change.
# ================================================================ #


import itertools
from typing import Iterable
from pretty_cli import PrettyCli


TYPE = [ "presence", "intensity" ]
AU = [ "AU06", "AU10", "AU12", "AU25", "AU26" ]
STATISTICS = [ [ "mean" ], [ "std" ], [ "q95" ], [ "mean", "std" ] ]

cli = PrettyCli()


def subsets(collection: Iterable, max_size: int) -> list:
    output = []
    for n in range(1, max_size + 1):
        output.extend(itertools.combinations(collection, n))
    return output


def main() -> None:
    cli.main_title("ML COMBOS TEST")

    cli.section("AU Combos")
    au_combos = subsets(AU, 2)
    cli.print(au_combos)

    cli.section("Feature Combos")
    feature_combos = [ [ f"{au}_{typ}_{stat}" for au in aus for stat in stats ] for (aus, typ, stats) in itertools.product(au_combos, TYPE, STATISTICS) ]

    for (n, combo) in enumerate(feature_combos):
        cli.print(f"[{n:3}] {combo}")


if __name__ == "__main__":
    main()
