#!/bin/env -S python3 -u


import json
from pathlib import Path
from typing import Tuple, Dict, Any

import numpy as np
import pandas as pd
import networkx as nx
import pingouin as pg

import matplotlib.pyplot as plt
import seaborn as sns

from pretty_cli import PrettyCli


DATA_DIR = Path("data/")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
PLOT_DIR = Path("plots/")

CATEGORY_NAMES = [ "separate", "one-way", "two-way" ]

LengthMap = Dict[int, Dict[int, int]] # source ID => target ID => shortest path length


cli = PrettyCli()


def json_default(obj: Any) -> Any:
    """
    Used by json.dump() to process NumPy objects.
    """

    if isinstance(obj, np.int32) or isinstance(obj, np.int64):
        return int(obj)
    elif isinstance(obj, np.float32) or isinstance(obj, np.float64):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()

    return str(obj)


def get_path_lengths() -> Tuple[LengthMap, LengthMap]:
    """
    Returns two maps (one per year), mapping:
    `(source ID) => (target ID) => (length of the shortest directed path connecting source to target)`

    If two vertices are not connected, there is no entry in the map.
    """

    def _get_one_year(data: pd.DataFrame, year: int) -> LengthMap:
        data = data.loc[year,:]
        graph = nx.DiGraph()

        for id in data.index:
            graph.add_node(id)

        for id1 in data.index:
            for id2 in data[id1]:
                graph.add_edge(id1, id2)

        return { source_id: distance_dict for (source_id, distance_dict) in nx.shortest_path_length(graph) }

    nominations = pd.read_csv(RAW_DIR / "Student Data - Anonymized Nominations.csv", index_col=[ "Grade", "ID" ]).dropna(how="all").sort_index()
    nominations = nominations.aggregate(lambda x: x.dropna().astype(int).tolist(), axis=1)

    year_2 = _get_one_year(nominations, 2)
    year_3 = _get_one_year(nominations, 3)

    return year_2, year_3


def main():
    cli.main_title("PARTITION STATS")

    assert RAW_DIR.is_dir()
    assert PROCESSED_DIR.is_dir()

    if not PLOT_DIR.is_dir():
        PLOT_DIR.mkdir(exist_ok=False, parents=False)

    year_2, year_3 = get_path_lengths()
    lengths = { 2: year_2, 3: year_3 }

    display_dict = dict()

    for year in [ 2, 3 ]:

        grade_entry = dict()
        condition_data = dict()

        for condition in [ "min", "max" ]:

            pairing_data = pd.read_csv(PROCESSED_DIR / f"grade_{year}_{condition}_partition.csv")
            pairing_data["condition"] = condition
            condition_data[condition] = pairing_data

            top = 4 * len(pairing_data)
            if "Num Children" not in grade_entry:
                grade_entry["Num Children"] = 2 * len(pairing_data)

            category_counts = { category: 0 for category in CATEGORY_NAMES }
            for (id1, id2) in pairing_data.set_index(["first", "second"]).index:
                exists_12 = id2 in lengths[year][id1]
                exists_21 = id1 in lengths[year][id2]
                category = int(exists_12) + int(exists_21)
                category_counts[CATEGORY_NAMES[category]] += 1

            distance_dict = pairing_data["distance"].describe()[[ "mean", "std", "min", "max" ]].to_dict()
            distance_dict["twos"] = (pairing_data["distance"] == 2).sum()
            distance_dict["tops"] = (pairing_data["distance"] == top).sum()
            distance_dict["category counts"] = category_counts

            cli.big_divisor()
            cli.section(f"Year {year}; Condition {condition}")
            cli.print(pairing_data[pairing_data["distance"] == top])
            cli.big_divisor()

            grade_entry[condition.title()] = distance_dict

        test = pg.ttest(condition_data["min"]["distance"], condition_data["max"]["distance"])
        test = test.loc["T-test", [ "T", "p-val", "cohen-d", "CI95%" ]].to_dict()
        grade_entry["T-Test"] = test

        display_dict[f"Year {year}"] = grade_entry

        joint_data = pd.concat(condition_data, ignore_index=True)

        sns.countplot(joint_data, x="distance", hue="condition", width=1)
        plt.xlabel("social distance heuristic")
        plt.tight_layout()
        plt.savefig(PLOT_DIR / f"partition-stats-year-{year}.png")
        plt.close()

    cli.print(display_dict)

    with open(PROCESSED_DIR / "partition-stats.json", "w") as file:
        json.dump(display_dict, file, ensure_ascii=False, indent=4, default=json_default)


if __name__ == "__main__":
    main()
