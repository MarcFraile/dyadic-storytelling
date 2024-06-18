#!/bin/env -S python3


# ================================================================ #
# ANALYSIS OF THE SIMPLE ML RESULTS
# ================================================================ #


from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pretty_cli import PrettyCli


TYPES = [ "single-child", "pair-concat" ]
SOURCES = [ "left-cam", "right-cam" ]

DATA_ROOT = Path("dataset")
OUT = Path("output")
PLOT_DIR = Path("plots")

cli = PrettyCli()


def main() -> None:
    cli.main_title("SIMPLE ML ANALYSIS")

    assert DATA_ROOT.is_dir()
    assert OUT.is_dir()
    if not PLOT_DIR.exists():
        PLOT_DIR.mkdir(parents=False, exist_ok=False)

    for type in TYPES:
        cli.chapter(type.replace("-", " "))

        for source in SOURCES:
            cli.subchapter(source.replace("-", " "))

            feature_csv = OUT / f"{source}-summary-au-data.csv"
            results_csv = OUT / f"{source}-simple-ml-{'data' if type == 'single-child' else 'pair-concat'}-run-summary.csv"

            assert feature_csv.is_file()
            assert results_csv.is_file()

            features = pd.read_csv(feature_csv)
            positive_probability = (features["condition"] == "positive").mean()
            random_chance = max(positive_probability, 1 - positive_probability)

            ml = pd.read_csv(results_csv)
            ml["feature_type"] = ml["features"].map(lambda s: "presence" if ("presence" in s) else "intensity")
            ml = ml.sort_values([ "feature_type", "model" ])

            cli.section("Data")
            cli.print(ml)

            cli.section("Plot Stats")
            sns.set_theme()
            fig, ax = plt.subplots(dpi=200, figsize=(8,6))
            sns.scatterplot(data=ml, x="train_accuracy", y="test_accuracy", hue="model", style="feature_type", legend="brief")

            x0 = min(random_chance, ml["train_accuracy"].min())
            y0 = min(random_chance, ml["test_accuracy" ].min())
            x1 = max(random_chance, ml["train_accuracy"].max())
            y1 = max(random_chance, ml["test_accuracy" ].max())

            plt.plot([random_chance, random_chance], [y0, y1], "--", color="gray")
            plt.plot([x0, x1], [random_chance, random_chance], "--", color="gray")

            source_fancy = " ".join(source.split("-")).title()
            plt.title(f"Train vs. Test Accuracy ({source_fancy})")
            plt.xlabel("train accuracy")
            plt.ylabel("test accuracy")

            fig.savefig(PLOT_DIR / f"{source}-simple-ml-{type}-train-test-acc.png")
            plt.close()


if __name__ == "__main__":
    main()
