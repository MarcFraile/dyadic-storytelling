#!/bin/env -S python3 -u


from pathlib import Path
import json
import math
from datetime import datetime
import itertools
from typing import List, Literal, Tuple

import pandas as pd
from pandas.api.types import CategoricalDtype
import pingouin as pg

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns

from pretty_cli import PrettyCli


# Disable SettingWithCopyWarning.
pd.options.mode.chained_assignment = None

# Activate the default Seaborn theme.
sns.set_theme()

# Set the default PyPlot DPI to a higher value
plt.rcParams["figure.dpi"] = 200


CONDITIONS         = CategoricalDtype([ "negative", "positive" ], ordered=True)
MOMENT_OF_DELIVERY = CategoricalDtype([ "pre-interaction", "post-interaction" ], ordered=True)
SAM_VARS           = CategoricalDtype([ "valence", "arousal", "dominance" ], ordered=True)

IOS_CUTE_VARS = ["Bad Guy", "Partner", "Best Friend"]

BASE_SAM_COLS = [ "sam_valence", "sam_arousal", "sam_dominance" ]
PRE_SAM_COLS  = [ f"pre_{col}"  for col in BASE_SAM_COLS ]
POST_SAM_COLS = [ f"post_{col}" for col in BASE_SAM_COLS ]

IOS_COLS = [ "ios_best_friend", "ios_bad_guy", "ios_partner" ]

PRE_COLS               = PRE_SAM_COLS
POST_COLS              = [ *POST_SAM_COLS, *IOS_COLS ]
ALL_SAM_COLS           = [ *PRE_SAM_COLS, *POST_SAM_COLS ]
ALL_QUESTIONNAIRE_COLS = [ *PRE_COLS, *POST_COLS ]
ALL_INT_COLS           = [ "distance", *ALL_QUESTIONNAIRE_COLS ]


DATA_DIR           = Path("data/")
RAW_DIR            = DATA_DIR / "raw"
PROCESSED_DIR      = DATA_DIR / "processed"
QUESTIONNAIRE_FILE = RAW_DIR / "Student Data - Anonymized Questionnaires.csv"
PLOT_DIR           = Path("plots/")


cli = PrettyCli()


def main():
    cli.main_title("QUESTIONNAIRE ANALYSIS")

    # ================================================================ #
    cli.section("Metadata")

    metadata = {
        "timestamp": datetime.now().isoformat(),
    }

    cli.print(metadata)

    # ================================================================ #
    # ================================================================ #
    cli.chapter("Fecth Data")

    # ================================================================ #
    cli.section("File Checks")

    assert QUESTIONNAIRE_FILE.is_file()
    assert PROCESSED_DIR.is_dir()

    if not PLOT_DIR.is_dir():
        PLOT_DIR.mkdir(parents=False, exist_ok=False)

    cli.print("OK")

    # ================================================================ #
    cli.section("Load Data")

    raw = pd.read_csv(QUESTIONNAIRE_FILE, index_col=[ "pair_id", "child_id" ]).sort_index()
    assert raw.index.has_duplicates == False

    # ---- Ensure all integer-type columns are treated as numbers ---- #
    # If a column contains non-numbers (e.g., a dash '-' to indicate "not applicable"),
    # it is temporarily treated as a float, and non-numbers cast to NaN.
    raw = raw.drop("notes", axis=1)
    for col in ALL_INT_COLS:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")

    # Treat 'condition' as an ordered categorical variable.
    raw["condition"] = raw["condition"].astype(CONDITIONS)

    # Treat 'date' as... a date!
    raw["date"] = pd.to_datetime(raw["date"])

    # Harvest IDs *before* filtering out missing data.
    raw_child_ids = raw.index.get_level_values("child_id").to_series().sort_values().unique()
    raw_pair_ids  = raw.index.get_level_values("pair_id" ).to_series().sort_values().unique()

    raw_year_2_pair_ids = [ id for id in raw_pair_ids if int(id[1]) == 2 ]
    raw_year_3_pair_ids = [ id for id in raw_pair_ids if int(id[1]) == 3 ]

    raw_year_2_child_ids = raw[raw.index.get_level_values("pair_id").map(lambda id: int(id[1]) == 2)].index.get_level_values("child_id").to_series().sort_values().unique()
    raw_year_3_child_ids = raw[raw.index.get_level_values("pair_id").map(lambda id: int(id[1]) == 3)].index.get_level_values("child_id").to_series().sort_values().unique()

    metadata["raw_data"] = {
        "num_entries"  : len(raw),
        "children" : {
            "year_2" : len(raw_year_2_child_ids),
            "year_3" : len(raw_year_3_child_ids),
            "total"  : len(raw_child_ids),
        },
        "pairs" : {
            "year_2" : len(raw_year_2_pair_ids),
            "year_3" : len(raw_year_3_pair_ids),
            "total"  : len(raw_pair_ids),
        },
    }
    cli.print({ "Raw Data" : metadata["raw_data"] })

    # ================================================================ #
    cli.section("Drop Incomplete Entries")

    # Visualize which entries are missing which columns.
    raw_nan_idx = raw.isna().T.any()
    nan_entries = []
    for (pair, child) in raw.index[raw_nan_idx]:
        x = raw.loc[(pair, child)]
        x = x[x.isna()].index.to_list()
        entry = { "pair_id" : pair, "child_id": child, "nan_columns": x }
        nan_entries.append(entry)
        cli.print(f"[pair {pair:<5}; child {child:02}] NaN columns: {x}")
    cli.blank()
    metadata["nan_entries"] = nan_entries

    # Drop rows containing non-numbers, and ensure all columns are properly typed as integers.
    full = raw.dropna(how="any")
    for col in ALL_INT_COLS:
        full[col] = full[col].astype(int)

    cli.print(f"Number of entries after dropping NaN: {len(full)}.")

    # ---------------- #
    cli.small_divisor()

    # We want to compare each child's data accross conditions, so we need to drop children who only appear once.
    # Some of them are the  NaNs we just dropped; some of them are children who only participated once.
    partial_children = full.index.get_level_values("child_id").value_counts() < 2
    partial_children = partial_children[partial_children].index.sort_values()

    cli.print(f"Participants with a single entry: {partial_children.to_list()}")
    cli.blank()

    partial_child_index = full.index.map(lambda idx: idx[1] in partial_children)
    full = full[~partial_child_index]

    cli.print(f"Number of entries after dropping participants with a single entry: {len(full)}.")

    # ---------------- #
    cli.small_divisor()

    full_child_ids = full.index.get_level_values("child_id").to_series().sort_values().unique()
    full_pair_ids  = full.index.get_level_values("pair_id" ).to_series().sort_values().unique()

    full_year_2_pair_ids = [ id for id in full_pair_ids if int(id[1]) == 2 ]
    full_year_3_pair_ids = [ id for id in full_pair_ids if int(id[1]) == 3 ]

    full_year_2_child_ids = full[full.index.get_level_values("pair_id").map(lambda id: int(id[1]) == 2)].index.get_level_values("child_id").to_series().sort_values().unique()
    full_year_3_child_ids = full[full.index.get_level_values("pair_id").map(lambda id: int(id[1]) == 3)].index.get_level_values("child_id").to_series().sort_values().unique()

    metadata["full_data"] = {
        "num_entries"  : len(full),
        "children" : {
            "year_2" : len(full_year_2_child_ids),
            "year_3" : len(full_year_3_child_ids),
            "total"  : len(full_child_ids),
        },
        "pairs" : {
            "year_2" : len(full_year_2_pair_ids),
            "year_3" : len(full_year_3_pair_ids),
            "total"  : len(full_pair_ids),
        },
    }
    cli.print({ "Full Data" : metadata["full_data"] })

    # ================================================================ #
    cli.section("Data")

    cli.print(full)

    # ================================================================ #
    # ================================================================ #
    cli.chapter("Basic Statistics")

    # ================================================================ #
    cli.subchapter("Counter-Balancing")

    conditions = full.reset_index().set_index(["child_id", "date"]).sort_index()["condition"]
    did_negative_first = conditions.iloc[0::2].droplevel("date") < conditions.iloc[1::2].droplevel("date")
    negative_first_counts = did_negative_first.value_counts()

    metadata["condition_order"] = {
        "negative_first_count"    : negative_first_counts[True ].item(),
        "positive_first_count"    : negative_first_counts[False].item(),
        "negative_first_fraction" : negative_first_counts[True ].item() / negative_first_counts.sum()
    }

    cli.print(metadata["condition_order"])

    # ================================================================ #
    cli.subchapter("Questionnaire Stats")

    basic_stats = full[ALL_QUESTIONNAIRE_COLS].describe()
    cli.print(basic_stats)
    cli.blank()

    path = PROCESSED_DIR / "questionnaire_descriptive_stats.csv"
    basic_stats.to_csv(path)
    cli.print(f"Saved descriptive stats at: {path}")

    # ================================ #
    cli.section("Response Normality")

    all_sw = pg.normality(full[ALL_QUESTIONNAIRE_COLS])
    all_sw["condition"] = "all"

    negative_sw = pg.normality(full.loc[full["condition"] == "negative", ALL_QUESTIONNAIRE_COLS])
    negative_sw["condition"] = "negative"

    positive_sw = pg.normality(full.loc[full["condition"] == "positive", ALL_QUESTIONNAIRE_COLS])
    positive_sw["condition"] = "positive"

    sw = pd.concat([ all_sw, negative_sw, positive_sw ])
    sw.index.name = "item"
    sw = sw.reset_index().set_index([ "item", "condition" ]).sort_index()

    cli.print(sw)
    cli.blank()

    path = PROCESSED_DIR / "normality_test.csv"
    sw.to_csv(path)
    cli.print(f"Saved normality test results at: {path}")

    # ================================ #
    cli.section("SAM")

    # ---- Format the data in a useful way to compare pretest and posttest SAM data. ---- #

    sam = get_sam_data(full)
    melted_sam = sam.reset_index().melt(id_vars=["moment"], value_vars=["valence", "arousal", "dominance"])
    cli.print(sam)
    cli.blank()
    cli.print(melted_sam)
    cli.blank()

    # ---- One boxplot per SAM item, showing the overall distribution. ---- #

    ax = sns.boxplot(melted_sam, x="variable", y="value", hue="moment", palette="pastel", medianprops={"color": "r", "linewidth": 2.5}, legend=False)
    # plt.title("SAM Questionnaires")
    plt.xlabel("")
    plt.ylabel("SAM score")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.tight_layout()

    path = PLOT_DIR / "questionnaire_descriptive_stats_sam.png"
    plt.savefig(path)
    plt.close()
    cli.print(f"Saved overall SAM box plot at: {path}")

    repeated_measures_anova = pd.DataFrame()

    for variable in SAM_VARS.categories:

        # --- Boxplot per moment (pre-post test) and condition (positive or negative pair). ---- #

        sns.boxplot(sam.reset_index(), x="moment", y=variable, hue="condition", palette="pastel", medianprops={"color": "r", "linewidth": 2.5}, legend=False)
        plt.ylim((0.75, 5.25))
        # plt.title(f"SAM {variable.title()}")
        plt.ylabel("SAM score")
        plt.tight_layout()

        path = PLOT_DIR / f"questionnaire_descriptive_stats_sam_{variable}.png"
        plt.savefig(path)
        plt.close()
        cli.print(f"Saved SAM {variable.title()} box plot at: {path}")

        # ---- Population-pyramid-like plot per moment (pre-post test) and condition (positive or negative pair). ---- #

        draw_sam_counts(sam, variable)
        path = PLOT_DIR / f"questionnaire_descriptive_stats_sam_{variable}_pyramid.png"
        plt.savefig(path)
        plt.close()
        cli.print(f"Saved SAM {variable.title()} value count plot at: {path}")

        # --- Significance testing ---- #

        # It seems that for normal data, the correct analysis here would be a "two-way repeated measures ANOVA".
        # That is, we have two within-subjects categorical IVs, and one continuous DV.
        # Given that our data are nowhere near normal, it is unclear what we should do.
        # Also, based on our notebook experiments, a two-way repeated measures ANOVA seems to not return significance.

        rma_row = pg.rm_anova(data=sam.reset_index(), dv=variable, within=["moment", "condition"], subject="child_id")
        rma_row["variable"] = variable
        rma_row["variable"] = rma_row["variable"].astype(SAM_VARS)
        rma_row["under-5"] = (rma_row["p-unc"] < 0.05)
        repeated_measures_anova = pd.concat([repeated_measures_anova, rma_row])

    # ================================ #
    cli.section("SAM repeated measures ANOVA")

    repeated_measures_anova = repeated_measures_anova.set_index([ "variable", "Source" ]).sort_index()
    cli.print(repeated_measures_anova)
    cli.blank()
    path = PROCESSED_DIR / "sam_repeated_measures_anova.csv"
    repeated_measures_anova.to_csv(path)
    cli.print(f"Saved SAM repeated measures ANOVA at: {path}")

    # ================================================================ #
    # ================================================================ #
    cli.chapter("IOS")

    def name_mapper(og_name: str) -> str:
        words = og_name.split("_")
        words = words[1:]
        return " ".join(words).title()

    ios : pd.DataFrame = full[[ "condition", *IOS_COLS ]]
    ios = ios.reset_index().set_index([ "child_id", "condition" ]).sort_index()
    ios = ios.drop("pair_id", axis=1)
    ios.columns = ios.columns.map(name_mapper)

    cli.print(ios)

    # ================================================================ #
    cli.subchapter("Overall Analysis")

    # ---- Basic test: bad guy < partner < best friend ---- #

    # If the data were normal, the correct test here would be a paired t-test.
    #   * Paired: the responses come from the same child in the same interaction.
    # Originally, I thought a one-tailed test was appropriate, since we expect a certain direction of events.
    # However, Rebecca pointed out that one should use two-tailed tests whenever it's possible that the change could go the other way.
    # Here is a discussion on one- vs two-tailed tests from a UCLA source: https://stats.oarc.ucla.edu/other/mult-pkg/faq/general/faq-what-are-the-differences-between-one-tailed-and-two-tailed-tests/

    # Since the data are not normal, it seems like the correct alternative is the Wilcoxon signed-rank test
    # (not to be confused with the Wilcoxon rank-sum test, which is an alternative name for the Mann-Whitney U-test).

    ios_wilcoxon = pd.DataFrame()
    for (x, y) in itertools.combinations(IOS_CUTE_VARS, 2): # Iterate over all ordered pairs, in order.
        row = pg.wilcoxon(ios[x], ios[y])
        row["x"] = x
        row["y"] = y
        ios_wilcoxon = pd.concat([ios_wilcoxon, row])
    ios_wilcoxon = ios_wilcoxon.set_index(["x", "y"])

    cli.print(ios_wilcoxon)
    cli.blank()

    path = PROCESSED_DIR / "ios_wilcoxon_signed_rank.csv"
    ios_wilcoxon.to_csv(path)
    cli.print(f"Saved IOS Wilcoxon signed-rank test results at: {path}")

    # ---- Joint boxplot (one box per IOS item) ---- #

    significant = []
    for (idx, row) in ios_wilcoxon.iterrows():
        x1 = IOS_CUTE_VARS.index(idx[0])
        x2 = IOS_CUTE_VARS.index(idx[1])
        p = row["p-val"]
        if p < 0.05:
            significant.append((x1, x2, p))

    ax = sns.boxplot(ios, order=IOS_CUTE_VARS, palette="pastel", medianprops={"color": "r", "linewidth": 2.5})
    add_significance(ax, significant)
    # plt.title("IOS Questionnaire Answers (overall)")
    plt.ylabel("IOS score")
    plt.tight_layout()

    path = PLOT_DIR / "questionnaire_descriptive_stats_ios.png"
    plt.savefig(path)
    plt.close()
    cli.print(f"Saved joint IOS plot at: {path}")

    # ================================================================ #
    cli.subchapter("Condition Comparison")

    # ---- negative partner < positive partner ---- #

    # I originally analysed all variables for completeness, but Rebecca pointed out that this is just a badly done factorial analysis.
    #
    # So our options are:
    #     1) Do a full 6-condition analysis and risk losing significance for data that is not so interesting.
    #     2) Drop further analysis for "Bad Guy" and "Best Friend", since they achieved their "sanity check" goal, and focus only on "Partner".
    #
    #  In theory, we're going for (2). To keep it simple, for now I'm just adding the extra plot.

    ios_positive = ios[ios.index.get_level_values("condition") == "positive"]
    ios_positive = ios_positive.reset_index().set_index("child_id").sort_index()
    ios_positive = ios_positive.drop("condition", axis=1)

    ios_negative = ios[ios.index.get_level_values("condition") == "negative"]
    ios_negative = ios_negative.reset_index().set_index("child_id").sort_index()
    ios_negative = ios_negative.drop("condition", axis=1)

    ios_condition = pd.DataFrame()
    for var in IOS_CUTE_VARS:
        row = pg.wilcoxon(ios_negative[var], ios_positive[var], method="approx")
        row["variable"] = var
        ios_condition = pd.concat([ios_condition, row])
    ios_condition = ios_condition.set_index("variable")

    cli.print(ios_condition)
    cli.blank()

    path = PROCESSED_DIR / "ios_condition_wilcoxon_signed_rank.csv"
    ios_condition.to_csv(path)
    cli.print(f"Saved IOS condition Wilcoxon signed-rank test results at: {path}")

    # ---- Per-condition boxplot ---- #

    significant = []
    for (idx, row) in ios_condition.iterrows():
        p = row["p-val"]
        if p < 0.05:
            x = IOS_CUTE_VARS.index(idx)
            significant.append((x - 0.25, x + 0.25, p))

    ios_long = ios.reset_index().melt(id_vars=["child_id", "condition"], value_vars=["Best Friend", "Bad Guy", "Partner"])

    ax = sns.boxplot(ios_long, x="variable", y="value", hue="condition", order=IOS_CUTE_VARS, palette="pastel", medianprops={"color": "r", "linewidth": 2.5}, legend=False)
    ax.set(xlabel=None)
    add_significance(ax, significant)
    # plt.title("IOS Questionnaire Answers (per-condition)")
    plt.ylabel("IOS score")
    plt.tight_layout()

    path = PLOT_DIR / "questionnaire_descriptive_stats_ios_condition.png"
    plt.savefig(path)
    plt.close()
    cli.print(f"Saved per-condition IOS plot at: {path}")

    # ---- Partner boxplot ---- #

    ios_long_partner = ios.reset_index().melt(id_vars=["child_id", "condition"], value_vars=["Partner"])
    ios_long_partner["condition"].replace({"positive": "high-rapport", "negative": "low-rapport"}, inplace=True)

    ax = sns.boxplot(ios_long_partner, x="condition", y="value", palette="pastel", medianprops={"color": "r", "linewidth": 2.5}, legend=False)
    ax.set(xlabel=None)
    add_significance(ax, [(0, 1, ios_condition.loc["Partner", "p-val"])])
    # plt.title("IOS::Partner Questionnaire Answers (per-condition)")
    plt.ylabel("IOS score")
    plt.tight_layout()

    path = PLOT_DIR / "questionnaire_descriptive_stats_ios_partner_condition.png"
    plt.savefig(path)
    plt.close()
    cli.print(f"Saved per-condition IOS::Partner plot at: {path}")

    # ================================================================ #
    # ================================================================ #
    cli.chapter("SAM Deltas")

    pre_sam = full[PRE_SAM_COLS]
    pre_sam.columns = pre_sam.columns.map(lambda text: text.split("_")[-1])

    post_sam = full[POST_SAM_COLS]
    post_sam.columns = post_sam.columns.map(lambda text: text.split("_")[-1])

    sam_diff = post_sam - pre_sam
    cli.print(sam_diff.describe())

    # ================================================================ #
    # ================================================================ #
    cli.chapter("Save Metadata")

    cli.print(metadata)

    path = PROCESSED_DIR / "statistical_analysis_metadata.json"
    with open(path, "w") as file:
        json.dump(metadata, file, indent=4)
    cli.print(f"Saved metadata at {path}")


def get_sam_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts pretest and posttest SAM data from the main DataFrame into a better shape for pre-post comparison.

    * Output indexed by `(pair_id, child_id, moment)`; columns `[condition, valence, arousal, dominance]`.
    """
    def get_sam_subset(df: pd.DataFrame, moment: Literal["pre-interaction", "post-interaction"]) -> pd.DataFrame:
        cols = PRE_SAM_COLS if (moment == "pre-interaction") else POST_SAM_COLS
        cols = [ "condition", *cols ]
        subset = df[cols]
        subset.columns = subset.columns.map(lambda name: name.split("_")[-1])
        subset["moment"] = moment
        subset["moment"] = subset["moment"].astype(MOMENT_OF_DELIVERY)
        subset = subset.reset_index().set_index(["pair_id", "child_id", "moment"])
        return subset

    pre_sam = get_sam_subset(df=data, moment="pre-interaction")
    post_sam = get_sam_subset(df=data, moment="post-interaction")

    sam = pd.concat([pre_sam, post_sam]).sort_index()
    return sam


def draw_sam_counts(sam: pd.DataFrame, variable: Literal["valence", "arousal", "dominance"]) -> None:
    """
    Plot a population-pyramid-like histogram of SAM responses per condition and moment for the given target variable.
    """

    # ==== (1) Gather a "chunky histogram" with the known possible response values. ==== #

    counts = sam.reset_index().groupby(["moment", "condition"])[variable].value_counts()

    for moment in MOMENT_OF_DELIVERY.categories:
        for condition in CONDITIONS.categories:
            for value in range(1, 6): # { 1, ..., 5 }
                idx = (moment, condition, value)
                if idx in counts.index:
                    if condition == "negative":
                        counts[idx] = -counts[idx]
                else:
                    counts[idx] = 0

    counts = counts.sort_index()
    counts = counts.rename("count").reset_index()

    # ==== (2) Plot the "population pyramid". ==== #

    def plot_sam_subfig(counts: pd.DataFrame, variable: str, moment: str) -> None:
        # plt.title(moment.title())
        sns.barplot(
            counts[counts["moment"] == moment],
            orient="horizontal", x="count", y=variable,
            hue="condition", dodge=False,
            order=[5, 4, 3, 2, 1],
        )

        ticks, labels = plt.xticks()
        plt.xticks(ticks=ticks, labels=[str(int(abs(tick))) for tick in ticks])

    # Set common limits accross both subplots, for readability.
    max_count = counts["count"].max()
    lim = ( 1 + math.floor(max_count / 5)) * 5

    plt.figure(figsize=(10, 4))

    plt.subplot(1, 2, 1)
    plt.xlim((-lim, +lim))
    plot_sam_subfig(counts, variable, "pre-interaction")

    plt.subplot(1, 2, 2)
    plt.xlim((-lim, +lim))
    plot_sam_subfig(counts, variable, "post-interaction")

    plt.tight_layout()


def add_significance(ax: plt.Axes, comparisons: List[Tuple[float, float, float]]) -> None:
    """
    Add comparison bars to `ax`, based on `comparisons`.

    * Each entry in `comparisons` is expected to be a tuple `(x1, x2, p)` indicating first x pos, second x pos, probability.
    """

    bottom, top = ax.get_ylim()
    y_range = top - bottom

    for (i, (x1, x2, p)) in enumerate(comparisons):
        bar_height = top + (i * 0.08 + 0.02) * y_range
        bar_tips = bar_height - 0.02 * y_range
        plt.plot([x1, x1, x2, x2], [bar_tips, bar_height, bar_height, bar_tips], lw=1, c="k")

        if p < 0.001:
            sig_symbol = '***'
        elif p < 0.01:
            sig_symbol = '**'
        elif p < 0.05:
            sig_symbol = '*'

        text_height = bar_height - 0.015 * y_range
        plt.text((x1 + x2) / 2, text_height, sig_symbol, ha="center", va="bottom", c="k")


if __name__ == "__main__":
    main()
