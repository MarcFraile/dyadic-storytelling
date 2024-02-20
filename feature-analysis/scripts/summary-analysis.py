#!/bin/env -S python3.11 -u


import itertools
from pathlib import Path
from datetime import timedelta

import pandas as pd
import pingouin as pg
import matplotlib.pyplot as plt
import seaborn as sns

from pretty_cli import PrettyCli


SOURCES = [ "left-cam", "right-cam", "frontal-cam" ]

DATA_ROOT = Path("dataset")
OUT = Path("output")
PLOT_DIR = Path("plots")

cli = PrettyCli()


def main() -> None:
    cli.main_title("SUMMARY ANALYSIS")

    assert DATA_ROOT.is_dir()
    assert OUT.is_dir()

    if not PLOT_DIR.is_dir():
        PLOT_DIR.mkdir(parents=False, exist_ok=False)

    for source in SOURCES:
        cli.chapter(source)

        cli.section("Loading Data")

        au_file = OUT / f"{source}-summary-au-data.csv"
        assert au_file.is_file()
        au_data = pd.read_csv(au_file, index_col=["pair_id", "round", "child_id"])

        duration_file = DATA_ROOT / f"{source}-durations.csv"
        assert duration_file.is_file()
        duration_data = pd.read_csv(duration_file, index_col=["pair_id", "round"])

        cli.print("OK")

        # ================================================================ #

        cli.chapter("Duration Data")

        duration_data.loc[duration_data.index.get_level_values("pair_id").str.startswith("P"), "condition"] = "positive"
        duration_data.loc[duration_data.index.get_level_values("pair_id").str.startswith("N"), "condition"] = "negative"

        duration_pos = duration_data[duration_data["condition"] == "positive"]
        duration_neg = duration_data[duration_data["condition"] == "negative"]

        assert len(duration_data) == len(duration_pos) + len(duration_neg)

        # -------------------------------- #

        cli.subchapter("Counts")

        cli.print({
            "Condition": {
                "Positive": {
                    "Pairs": len(duration_pos.index.get_level_values("pair_id").unique()),
                    "Rounds": len(duration_pos),
                },
                "Negative": {
                    "Pairs": len(duration_neg.index.get_level_values("pair_id").unique()),
                    "Rounds": len(duration_neg),
                },
            }
        })

        # -------------------------------- #

        cli.subchapter("Durations")

        duration_ttest = pg.ttest(duration_pos["duration_s"], duration_neg["duration_s"])
        duration_ttest.to_csv(OUT / f"{source}-summary-analysis-duration-ttest.csv")

        cli.print({ "Duration Statistics": {
            "Condition": {
                "Positive" : {
                    "Mean"  : timedelta(seconds=duration_pos["duration_s"].mean().item()),
                    "STD"   : timedelta(seconds=duration_pos["duration_s"].std().item()),
                    "Total" : timedelta(seconds=duration_pos["duration_s"].sum().item()),
                },
                "Negative" : {
                    "Mean"  : timedelta(seconds=duration_neg["duration_s"].mean().item()),
                    "STD"   : timedelta(seconds=duration_neg["duration_s"].std().item()),
                    "Total" : timedelta(seconds=duration_neg["duration_s"].sum().item()),
                },
            },
            "T-Test": {
                "Significant": (duration_ttest["p-val"].item() < 0.05),
                "P-Value": duration_ttest["p-val"].item(),
                "Cohen D": duration_ttest["cohen-d"].item(),
            },
         } })

        sns.boxplot(duration_data, x="condition", y="duration_s")
        plt.title("Duration per Condition")
        plt.xlabel("Condition")
        plt.ylabel("Duration (s)")
        plt.tight_layout()
        plt.savefig(PLOT_DIR / f"{source}-summary-analysis-duration-per-condition.png")
        plt.close()

        # -------------------------------- #

        cli.subchapter("Rounds")

        rounds_pos = duration_pos.reset_index().groupby("pair_id").count()["round"]
        rounds_neg = duration_neg.reset_index().groupby("pair_id").count()["round"]

        round_data = pd.concat([rounds_pos, rounds_neg])
        round_data = pd.DataFrame(round_data)
        round_data.loc[round_data.index.str.startswith("P"), "condition"] = "positive"
        round_data.loc[round_data.index.str.startswith("N"), "condition"] = "negative"

        rounds_ttest = pg.ttest(rounds_pos, rounds_neg)
        rounds_ttest.to_csv(OUT / f"{source}-summary-analysis-rounds-ttest.csv")

        cli.print({ "Round Statistics": {
            "Condition": {
                "Positive": {
                    "Mean": rounds_pos.mean().item(),
                    "STD" : rounds_pos.std().item(),
                },
                "Negative" : {
                    "Mean": rounds_neg.mean().item(),
                    "STD" : rounds_neg.std().item(),
                },
            },
            "T-Test": {
                "Significant": (rounds_ttest["p-val"].item() < 0.05),
                "P-Value": rounds_ttest["p-val"].item(),
                "Cohen D": rounds_ttest["cohen-d"].item(),
            },
         } })

        sns.countplot(round_data, x="round", hue="condition")
        plt.title("Number of Rounds per Condition")
        plt.tight_layout()
        plt.savefig(PLOT_DIR / f"{source}-summary-analysis-rounds-per-condition.png")
        plt.close()

        # ================================================================ #

        cli.chapter("AU Data")

        au_pos = au_data[au_data["condition"] == "positive"].drop("condition", axis=1)
        au_neg = au_data[au_data["condition"] == "negative"].drop("condition", axis=1)
        assert len(au_data) == len(au_pos) + len(au_neg)

        cli.section("Sample Distribution")
        cli.print({ "positive": len(au_pos), "negative": len(au_neg) })

        # -------------------------------- #

        cli.section("Basic Statistics")

        overall_distribution = (
            au_data.describe(percentiles=[])
            .reset_index()
            .melt(id_vars="index")
            .rename({ "index": "statistic" }, axis=1)
            .rename({ "value": "overall" }, axis=1)
            .set_index(["variable", "statistic"])
            .T
        )

        per_condition = au_data.groupby("condition").describe(percentiles=[])
        per_condition = pd.concat([overall_distribution, per_condition], axis=0)
        per_condition.drop(["count", "50%"], axis=1, level=1, inplace=True)

        per_condition = per_condition.stack()
        per_condition.index.set_names(["condition", "statistic"], inplace=True)

        cli.print(per_condition)
        per_condition.to_csv(OUT / f"{source}-summay-analysis-variable-distribution.csv")

        # -------------------------------- #

        cli.subchapter("Correlation")

        au_cols = [ col for col in au_data.columns if col.startswith("AU") ]
        aus = sorted(set(col[:4] for col in au_cols))

        corr = au_data[au_cols].corr(method="pearson")
        corr.index.name = "index"
        cli.print(corr)
        corr.to_csv(OUT / f"{source}-summary-analysis-correlation.csv")

        cli.small_divisor()

        corr_flat = corr.reset_index().melt(id_vars=["index"]).set_index(["index", "variable"])

        au_top_corrs = []
        for (au1, au2) in itertools.combinations(aus, 2):
            idx1 = corr_flat.index.get_level_values("index").str.startswith(au1)
            idx2 = corr_flat.index.get_level_values("variable").str.startswith(au2)
            subset = corr_flat[idx1 & idx2].dropna().reset_index().rename({"index": "first_var", "variable": "second_var", "value": "correlation" }, axis=1)
            subset["abs"] = subset["correlation"].abs()
            subset["first"] = au1
            subset["second"] = au2
            top_value = subset.sort_values("abs", ascending=False).head(n=1)
            au_top_corrs.append(top_value)

        au_top_corrs = pd.concat(au_top_corrs, ignore_index=True).set_index(["first", "second"]).sort_values("abs").drop("abs", axis=1)
        cli.print(au_top_corrs)
        au_top_corrs.to_csv(OUT / f"{source}-summary-analysis-top-correlations.csv")

        # -------------------------------- #

        cli.section("Normality")

        normality = pg.normality(au_data)
        cli.print(normality)
        normality.to_csv(OUT / f"{source}-summary-analysis-normality.csv")

        # -------------------------------- #

        cli.subchapter("T-Test")

        ttest_rows = []
        for col in au_pos.columns:
            row = pg.ttest(au_pos[col], au_neg[col])
            row["variable"] = col
            ttest_rows.append(row)
        ttest = pd.concat(ttest_rows, ignore_index=True).set_index("variable")

        cli.section("Raw T-Test")
        cli.print(ttest)
        ttest.to_csv(OUT / f"{source}-summary-analysis-raw-ttest.csv")

        cli.section("Raw Significant Fields")
        raw_significant = ttest[ttest["p-val"] < 0.05]
        cli.print(raw_significant[["p-val", "cohen-d"]])

        cli.section("Adjusted Significant Fields")
        adjusted_ttest = ttest.copy()
        adjusted_ttest["p-val"] *= len(au_pos.columns)
        adjusted_significant = adjusted_ttest[adjusted_ttest["p-val"] < 0.05]
        cli.print(adjusted_significant[["p-val", "cohen-d"]])


if __name__ == "__main__":
    main()
