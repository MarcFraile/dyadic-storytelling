#!/bin/env -S python3


# CHECK CHILD SPLITS
# ==================
# This script analyses the "who-played-with-whom" network implied by child-order.csv.
#
# Our primary interest is to analyse if a partition scheme where each child only appears
# in one fold is feasible. The conclusion is "not really". In particular, enforcing no
# child overlap precludes us from having several balanced folds with good stratification.
#
# Note that all the analysis in this article is done taking a playing *pair* as the
# statistical unit, that is to say, we always ensure the data from one pair is in one
# data split. Here we investigated if we can tighten the requirement to the child level.


import numpy as np
import pandas as pd
import networkx as nx

from pretty_cli import PrettyCli


def main():
    cli = PrettyCli()
    cli.main_title("CHECK CHILD SPLITS")

    cli.chapter("Loading")

    data = pd.read_csv("child-order.csv")

    pairs = data.groupby("pair_id")[["left_child", "right_child"]].apply(lambda x: list(np.unique(x)))
    pairs.drop("P240", inplace=True)

    cli.section("Pairs")
    cli.print(pairs)
    cli.print(f"Count: {len(pairs)}")

    year_lookup = pd.Series()
    for pair in pairs.index:
        year = int(pair[1])

        [first, second ] = pairs.loc[pair]

        year_lookup.loc[first ] = year
        year_lookup.loc[second] = year

    year_lookup = year_lookup.astype(int)

    cli.section("Year Lookup")
    cli.print(year_lookup)

    graph = nx.Graph()
    for (first, second) in pairs:
        graph.add_edge(first, second)

    cli.section("Graph Nodes")
    cli.print(sorted(graph.nodes))

    cli.section("Graph Edges")
    cli.print(sorted(graph.edges))

    cli.section("Connected Components")
    connected_components = list(nx.connected_components(graph))
    cli.print(connected_components)

    cli.blank()
    cli.print(f"Count: {len(connected_components)}")

    cli.chapter("Analysis")

    for (idx, component) in enumerate(connected_components):
        cli.subchapter(f"Component {idx}")
        component = sorted(component)

        cli.section("Component")
        cli.print(component)

        cli.blank()
        cli.print(f"Count: {len(component)}")

        cli.section("Year")
        years = [ year_lookup[child] for child in component ]
        year = years[0]
        for y in years[1:]:
            assert(year == y)
        cli.print(year)


if __name__ == "__main__":
    main()
