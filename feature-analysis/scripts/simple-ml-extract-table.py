#!/bin/env -S python3 -u


import re
from pathlib import Path

import pandas as pd
from pretty_cli import PrettyCli


OUT = Path("output")

TYPES = [ "single-child", "pair-concat" ]
SOURCES = [ "left-cam", "right-cam" ]

ACCURACY_BASELINE = 54 / 103

FEATURE_FILES : list[Path] = { source: OUT / f"{source}-summary-au-data.csv" for source in SOURCES }


def get_test_acc_display(source_data: pd.DataFrame) -> pd.Series:
    test_acc = source_data.groupby(["features", "model"])["test_accuracy"]

    test_acc_mean    = (100 * test_acc.mean()).map("{:,.2f}\%".format)
    test_acc_std     = (100 * test_acc.std() ).map("{:,.2f}\%".format)
    test_acc_display = "$" + test_acc_mean + " \pm " + test_acc_std + "$"

    return test_acc_display


def main() -> None:
    cli = PrettyCli()
    cli.main_title("SIMPLE ML - EXTRACT TABLE")

    assert OUT.is_dir()

    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.max_columns", None)
    pd.set_option('display.width', 2000)

    for type in TYPES:
        cli.chapter(type)

        source_data = {
            src: pd.read_csv(
                OUT / f"{src}-simple-ml-{'data' if type == 'single-child' else 'pair-concat'}-run-summary.csv",
                index_col=["model", "features"],
            )
            for src in SOURCES
        }

        source_detailed = {
            src: pd.read_csv(
                OUT / f"{src}-simple-ml-{'data' if type == 'single-child' else 'pair-concat'}-detailed-runs.csv",
                index_col=["model", "features"],
            )
            for src in SOURCES
        }

        left_accs  = get_test_acc_display(source_detailed["left-cam" ]).rename("left_camera")
        right_accs = get_test_acc_display(source_detailed["right-cam"]).rename("right_camera")
        test_accs  = pd.concat([left_accs, right_accs], axis=1).reset_index()

        test_accs["AUs"] = test_accs["features"].map(lambda features: sorted(set(re.findall("AU\d{2}", features))))
        test_accs["statistic"] = test_accs["features"].map(lambda features: sorted(set(re.findall("mean|std|q95", features))))
        test_accs["type"] = test_accs["features"].map(lambda features: re.search("presence|intensity", features).group(0))

        test_accs = test_accs[["model", "AUs", "statistic", "type", "left_camera", "right_camera"]]

        test_accs["model"] = test_accs["model"].map({ "DecisionTreeClassifier": "decision tree", "LogisticRegression": "linear", "SVC": "SVM" })
        test_accs["statistic"] = test_accs["statistic"].map(lambda l: [ ("95% quantile" if x == "q95" else x) for x in l ])

        cli.subchapter("left cam")

        cli.section("Stats")
        data = source_data["left-cam"]
        cli.print({
            "Beat Random": {
                "Train": f"{(data['train_accuracy'] > ACCURACY_BASELINE).sum()} / {len(data)}",
                "Test" : f"{(data['test_accuracy' ] > ACCURACY_BASELINE).sum()} / {len(data)}",
            }
        })

        cli.section("Top Results")
        left_best = test_accs.sort_values("left_camera", ascending=False).head(10).reset_index(drop=True)
        cli.print(left_best)

        cli.subchapter("right cam")

        cli.section("Stats")
        data = source_data["right-cam"]
        cli.print({
            "Beat Random": {
                "Train": f"{(data['train_accuracy'] > ACCURACY_BASELINE).sum()} / {len(data)}",
                "Test" : f"{(data['test_accuracy' ] > ACCURACY_BASELINE).sum()} / {len(data)}",
            }
        })

        cli.section("Top Results")
        left_best = test_accs.sort_values("right_camera", ascending=False).head(10).reset_index(drop=True)
        cli.print(left_best)


if __name__ == "__main__":
    main()
