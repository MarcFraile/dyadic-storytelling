#!/bin/env -S python3 -u


# ================================================================ #
# CROSS-SOURCE COMPARISON OF TEST ACCURACIES
# ================================================================ #


import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import seaborn as sns

from pretty_cli import PrettyCli


TYPES = [ "single-child", "pair-concat" ]
SOURCES = [ "left-cam", "right-cam" ]

DATA_ROOT = Path("dataset")
OUT = Path("output")
PLOT_DIR = Path("plots")

cli = PrettyCli()


def load_source(type: str, source: str) -> tuple[float, pd.DataFrame]:
    feature_csv = OUT / f"{source}-summary-au-data.csv"
    results_csv = OUT / f"{source}-simple-ml-{'data' if type == 'single-child' else 'pair-concat'}-run-summary.csv"

    assert feature_csv.is_file()
    assert results_csv.is_file()

    features = pd.read_csv(feature_csv)
    positive_probability = (features["condition"] == "positive").mean()
    random_chance = max(positive_probability, 1 - positive_probability)

    ml_results = pd.read_csv(results_csv)
    ml_results["feature_type"] = ml_results["features"].map(lambda s: "presence" if ("presence" in s) else "intensity")
    ml_results = ml_results.sort_values([ "feature_type", "model" ])
    ml_results = ml_results[[ "feature_type", "model", "features", "test_accuracy" ]]
    ml_results = ml_results.set_index(["model", "features"])

    return random_chance, ml_results


def main() -> None:
    cli.main_title("CROSS-SOURCE COMPARISON")

    assert DATA_ROOT.is_dir()
    assert OUT.is_dir()

    sns.set_theme()

    for type in TYPES:
        cli.chapter(type.replace("-", " "))

        for (sx, sy) in itertools.combinations(SOURCES, 2):
            cli.subchapter(f"[{sx} x {sy}]")

            random_x, ml_x = load_source(type, sx)
            random_y, ml_y = load_source(type, sy)

            ml_x = ml_x.rename({ "test_accuracy": "acc_x"}, axis=1)
            ml_y = ml_y.rename({ "test_accuracy": "acc_y"}, axis=1)

            ml = ml_x.join(ml_y.drop("feature_type", axis=1))
            ml["acc_min"] = np.minimum(ml["acc_x"], ml["acc_y"])

            ml = (
                ml.reset_index()
                .replace({ "DecisionTreeClassifier": "decision tree", "LogisticRegression": "linear", "SVC": "SVM" })
                .set_index(["model", "features"])
            )
            ml = ml.rename({ "feature_type": "feature type" }, axis=1)

            ml_sorted = ml.sort_values(by="acc_min", ascending=False)
            cli.print(ml_sorted)
            ml_sorted.to_csv(OUT / f"{type}-{sx}-vs-{sy}-simple-ml-test-acc.csv")

            fig, ax = plt.subplots(dpi=300, figsize=(8,8))

            sns.scatterplot(data=ml, x="acc_x", y="acc_y", hue="model", style="feature type", legend="brief")

            x0 = min(random_x, ml["acc_x"].min())
            y0 = min(random_y, ml["acc_y"].min())
            x1 = max(random_x, ml["acc_x"].max())
            y1 = max(random_y, ml["acc_y"].max())

            plt.plot([random_x, random_x], [y0, y1], "--", color="gray")
            plt.plot([x0, x1], [random_y, random_y], "--", color="gray")

            loc = plticker.MultipleLocator(base=0.05)
            ax.xaxis.set_major_locator(loc)
            ax.yaxis.set_major_locator(loc)

            ax.set_xticklabels(f"{100*x:.0f}%" for x in ax.get_xticks())
            ax.set_yticklabels(f"{100*y:.0f}%" for y in ax.get_yticks())

            sx_fancy = " ".join(sx.split("-")).replace("cam", "camera")
            sy_fancy = " ".join(sy.split("-")).replace("cam", "camera")

            # plt.title(f"{sx_fancy} Test Accuracy vs. {sy_fancy} Test Accuracy")
            plt.xlabel(sx_fancy)
            plt.ylabel(sy_fancy)

            ax.set_aspect("equal")
            plt.tight_layout()

            fig.savefig(PLOT_DIR / f"{type}-{sx}-vs-{sy}-simple-ml-test-acc.png")
            plt.close()


if __name__ == "__main__":
    main()
