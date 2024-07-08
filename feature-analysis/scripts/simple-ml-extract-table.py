#!/bin/env -S python3 -u


import re
import json
from pathlib import Path

import pandas as pd
from pretty_cli import PrettyCli


OUT = Path("output")
K_FOLDS_JSON = OUT / "k_folds.json"

TYPES = [ "single-child", "pair-concat" ]
SOURCES = [ "left-cam", "right-cam" ]

ACCURACY_BASELINE = 57 / 106

FEATURE_FILES : list[Path] = { source: OUT / f"{source}-summary-au-data.csv" for source in SOURCES }


def main() -> None:
    cli = PrettyCli()
    cli.main_title("SIMPLE ML - EXTRACT TABLE")

    assert OUT.is_dir()

    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.max_columns", None)
    pd.set_option('display.width', 2000)

    cli.chapter("Baselines")

    with open(K_FOLDS_JSON, "r") as handle:
        k_folds = json.load(handle)

    emp_probs = [ fold["rounds"]["positive_fraction"] for fold in k_folds["folds"] ]
    baseline_accs = pd.Series([ max(p, 1-p) for p in emp_probs ])

    cli.section("Random Chance Accuracy per Fold")
    cli.print(baseline_accs)

    cli.section("LaTeX-Ready Summary")
    cli.print(f"${100*baseline_accs.mean():.02f}\% \pm {100*baseline_accs.std():.02f}\%$")

    for type in TYPES:
        cli.chapter(type)

        source_data: dict[str, pd.DataFrame] = {}
        for src in SOURCES:
            data = pd.read_csv(
                OUT / f"{src}-simple-ml-{'data' if type == 'single-child' else 'pair-concat'}-run-summary.csv",
                usecols   = [ "model", "features", "train_accuracy_mean", "train_accuracy_std", "test_accuracy_mean", "test_accuracy_std" ],
                index_col = [ "model", "features" ],
            )

            data.rename(columns=lambda col: col.replace("accuracy", "acc"), inplace=True)

            test_acc_mean = (100 * data["test_acc_mean"]).map("{:5.02f}\%".format)
            test_acc_std  = (100 * data["test_acc_std" ]).map("{:5.02f}\%".format)
            data["display"] = "$" + test_acc_mean + " \pm " + test_acc_std + "$"

            source_data[src] = data

        joint_data = source_data["left-cam"].join(source_data["right-cam"], lsuffix="_left", rsuffix="_right").reset_index()

        joint_data["AUs"      ] = joint_data["features"].map(lambda features: sorted(set(re.findall("AU\d{2}", features))))
        joint_data["statistic"] = joint_data["features"].map(lambda features: sorted(set(re.findall("mean|std|q95", features))))
        joint_data["type"     ] = joint_data["features"].map(lambda features: re.search("presence|intensity", features).group(0))

        joint_data.drop("features", axis=1, inplace=True)

        joint_data["model"] = joint_data["model"].map({ "DecisionTreeClassifier": "decision tree", "LogisticRegression": "linear", "SVC": "SVM" })

        cli.section("Generalization Gap")
        gap_lr = (
            (joint_data["test_acc_mean_left"] - joint_data["test_acc_mean_right"])
            .abs()
            .describe(percentiles=[])
            .drop(["count", "50%"])
            .map(lambda x: round(100 * x, 2))
        )
        cli.print(gap_lr)

        cli.subchapter("left cam")

        cli.section("Stats")
        data = source_data["left-cam"]
        cli.print({
            "Beat Random": {
                "Train": f"{(data['train_acc_mean'] > ACCURACY_BASELINE).sum()} / {len(data)}",
                "Test" : f"{(data['test_acc_mean' ] > ACCURACY_BASELINE).sum()} / {len(data)}",
            }
        })

        # =========================

        cli.section("Top Model")

        left_best = (joint_data
            .sort_values(
                by        = [ "test_acc_mean_left", "test_acc_std_left", "test_acc_mean_right", "test_acc_std_right" ],
                ascending = [                False,                True,                 False,                 True ],
            )
            .head(10)
        )

        top_left = left_best.iloc[0][["train_acc_mean_left", "train_acc_std_left", "test_acc_mean_left", "test_acc_std_left"]]
        top_left = top_left.map(lambda x: f"{100*x:5.02f}%")
        cli.print(top_left)

        cli.section("Top 10 -- Latex Dislpay")

        left_best_display = (left_best
            [[ "model", "AUs", "statistic", "type", "display_left", "display_right" ]]
            .rename(columns=lambda col: col.replace("display", "camera"))
            .reset_index(drop=True)
        )
        cli.print(left_best_display)

        cli.subchapter("right cam")

        cli.section("Stats")
        data = source_data["right-cam"]
        cli.print({
            "Beat Random": {
                "Train": f"{(data['train_acc_mean'] > ACCURACY_BASELINE).sum()} / {len(data)}",
                "Test" : f"{(data['test_acc_mean' ] > ACCURACY_BASELINE).sum()} / {len(data)}",
            }
        })

        # =========================

        cli.section("Top Model")

        right_best = (joint_data
            .sort_values(
                by        = [ "test_acc_mean_right", "test_acc_std_right", "test_acc_mean_left", "test_acc_std_left" ],
                ascending = [                 False,                 True,                False,                True ],
            )
            .head(10)
        )

        top_right = right_best.iloc[0][["train_acc_mean_right", "train_acc_std_right", "test_acc_mean_right", "test_acc_std_right"]]
        top_right = top_right.map(lambda x: f"{100*x:5.02f}%")
        cli.print(top_right)

        cli.section("Top 10 -- Latex Dislpay")

        right_best_display = (right_best
            [[ "model", "AUs", "statistic", "type", "display_left", "display_right" ]]
            .rename(columns=lambda col: col.replace("display", "camera"))
            .reset_index(drop=True)
        )
        cli.print(right_best_display)


if __name__ == "__main__":
    main()
