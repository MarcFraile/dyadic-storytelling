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


def add_display(data: pd.DataFrame, old_col_prefix: str, new_col: str) -> None:
    mean = (100 * data[old_col_prefix + "_mean"]).map("{:5.02f}\%".format)
    std  = (100 * data[old_col_prefix + "_std" ]).map("{:5.02f}\%".format)
    data[new_col] = "$" + mean + " \pm " + std + "$"


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
                usecols   = [ "model", "features", "train_accuracy_mean", "train_accuracy_std", "best_mean_val_accuracy_mean", "best_mean_val_accuracy_std", "test_accuracy_mean", "test_accuracy_std" ],
                index_col = [ "model", "features" ],
            )

            data.rename(columns=lambda col: col.replace("accuracy", "acc"), inplace=True)

            add_display(data, old_col_prefix="train_acc", new_col="train_display")
            add_display(data, old_col_prefix="best_mean_val_acc", new_col="val_display")
            add_display(data, old_col_prefix="test_acc", new_col="test_display")

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

        for side in ["left", "right"]:
            other = "left" if side == "right" else "right"

            # ================================================== #
            cli.subchapter(f"{side} cam")

            # ---------------- #
            cli.section("Stats")
            data = source_data[f"{side}-cam"]
            cli.print({
                "Beat Random": {
                    "Train": f"{(data['train_acc_mean'] > ACCURACY_BASELINE).sum()} / {len(data)}",
                    "Test" : f"{(data['test_acc_mean' ] > ACCURACY_BASELINE).sum()} / {len(data)}",
                }
            })


            # ---------------- #
            cli.section("Top Model")

            best = joint_data.sort_values(
                by        = [ f"test_acc_mean_{side}", f"test_acc_std_{side}", f"test_acc_mean_{other}", f"test_acc_std_{other}" ],
                ascending = [                   False,                   True,                    False,                    True ],
            )

            top = best.iloc[0][[f"train_acc_mean_{side}", f"train_acc_std_{side}", f"test_acc_mean_{side}", f"test_acc_std_{side}"]]
            top = top.map(lambda x: f"{100*x:5.02f}%")
            cli.print(top)

            # ---------------- #
            cli.section("Top 10 -- Latex Dislpay")
            cli.print(f"Sorted by (test mean {side}, test std {side}, test mean {other}, test std {other}).")
            cli.blank()

            top10_latex = (best
                [[ "model", "AUs", "statistic", "type", f"test_display_{side}", f"test_display_{other}" ]]
                .rename(columns=lambda col: col.replace("test_display", "camera"))
                .head(10)
                .reset_index(drop=True)
            )
            cli.print(top10_latex)

            # ---------------- #
            cli.section("Top 10 -- Test Single Source")
            cli.print(f"Sorted by (test mean {side}, val mean {side}, train mean {side}, test std {side}, val std {side}, train std {side}).")
            cli.blank()

            top10_test = (joint_data
                .sort_values(
                    by        = [ f"test_acc_mean_{side}", f"best_mean_val_acc_mean_{side}", f"train_acc_mean_{side}", f"test_acc_std_{side}", f"best_mean_val_acc_std_{side}", f"train_acc_std_{side}" ],
                    ascending = [                   False,                            False,                    False,                   True,                            True,                    True ],
                )
                [[ "model", "AUs", "statistic", "type", f"train_display_{side}", f"val_display_{side}", f"test_display_{side}" ]]
                .head(n=10)
                .reset_index(drop=True)
            )
            cli.print(top10_test)

            # ---------------- #
            cli.section("Top 10 -- Val Single Source")
            cli.print(f"Sorted by (val mean {side}, test mean {side}, train mean {side}, val std {side}, test std {side}, train std {side}).")
            cli.blank()

            top10_val = (joint_data
                .sort_values(
                    by        = [ f"best_mean_val_acc_mean_{side}", f"test_acc_mean_{side}", f"train_acc_mean_{side}", f"best_mean_val_acc_std_{side}", f"test_acc_std_{side}", f"train_acc_std_{side}" ],
                    ascending = [                            False,                   False,                    False,                            True,                   True,                    True ],
                )
                [[ "model", "AUs", "statistic", "type", f"train_display_{side}", f"val_display_{side}", f"test_display_{side}" ]]
                .head(n=10)
                .reset_index(drop=True)
            )
            cli.print(top10_val)


if __name__ == "__main__":
    main()
