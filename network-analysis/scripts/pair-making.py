#!/bin/env -S python3 -u


import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Literal, Set, Tuple

import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
import networkx as nx
from networkx.algorithms import matching

from pretty_cli import PrettyCli


DATA_DIR = Path("data/")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
NOMINATION_FILE = RAW_DIR / "Student Data - Anonymized Nominations.csv"
CLASS_FILE = RAW_DIR / "class.csv"
PLOT_DIR = Path("plots/")

cli = PrettyCli()


def directed_graph_layout(G: nx.DiGraph):
    layout = dict()

    undirected = G.to_undirected()
    connected_components = [ c for c in nx.connected_components(undirected) ]

    for i, component in enumerate(connected_components):
        subgraph = G.subgraph(component)

        scale = np.sqrt(len(subgraph))
        angle = 2 * np.pi * i / len(connected_components)
        center = scale * 2.5 * np.array([ np.cos(angle), np.sin(angle) ])

        sub_layout = nx.shell_layout(subgraph, center=center, scale=scale)

        layout.update(sub_layout)

    return layout


def main():
    cli.main_title("FRIENDSHIP NETWORK ANALYSIS")

    # ================================================================ #
    cli.section("File Checks")

    assert NOMINATION_FILE.is_file()
    assert CLASS_FILE.is_file()
    assert PROCESSED_DIR.is_dir()

    if not PLOT_DIR.is_dir():
        PLOT_DIR.mkdir(parents=False, exist_ok=False)

    cli.print("OK")

    # ================================================================ #
    cli.section("Load Data")

    raw = pd.read_csv(NOMINATION_FILE)
    raw = raw.dropna(how="all").set_index([ "Grade", "ID" ]).sort_index()

    assert raw.index.has_duplicates == False

    cli.print(f"Total number of participants: {len(raw)}.")

    # ---------------- #

    clazz = pd.read_csv(CLASS_FILE, index_col=[ "Grade", "ID" ]).sort_index().fillna("Unknown")

    clazz_list = clazz["Class"].unique().tolist()
    clazz_color = [ tuple(mpl.colors.hsv_to_rgb(((n + 0.5) / (len(clazz_list) + 1), 0.5, 0.9))) for n in range(len(clazz_list)) ]
    clazz_to_color = { cla: col for (cla, col) in zip(clazz_list, clazz_color) }
    clazz["Color"] = clazz["Class"].map(clazz_to_color)

    cli.print("Students per class:")
    cli.print(clazz["Class"].value_counts())
    cli.blank()

    # ---------------- #
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "total_participants": len(raw),
    }

    # ================================================================ #
    cli.section("Cross-Grade Nominations")

    grade_lookup = raw.index.to_frame().reset_index(drop=True).set_index("ID", drop=True).sort_index()
    cross_nominations = []

    for (grade_1, idx_1) in raw.index:
        for idx_2 in raw.loc[(grade_1, idx_1)].squeeze():
            if idx_2.is_integer():
                idx_2 = int(idx_2)
                if not (idx_2 in grade_lookup.index):
                    continue # We never managed to schedule [Child 22] to fill the friendship nomination form. Causes issues (missing from index).
                grade_2 = grade_lookup.loc[idx_2].item()
                if grade_1 != grade_2:
                    cross_nominations.append((idx_1, idx_2))

    metadata["cross_grade_nominations"] = cross_nominations

    # ================================================================ #
    # ================================================================ #
    for grade in [ 2, 3 ]:
        cli.chapter(f"Grade {grade}")

        meta_key = f"grade_{grade}"
        metadata[meta_key] = dict()

        # ================================================================ #
        cli.section("Prepare Directed Graph")

        directed_graph = get_directed_graph(raw, grade)

        node_list = list(directed_graph.nodes)
        node_count = len(directed_graph.nodes)

        cli.print(f"IDs (count: {node_count}): {node_list}")
        metadata[meta_key]["ids"] = node_list
        metadata[meta_key]["count"] = node_count

        fig, ax = plt.subplots(dpi=200)
        fig, ax = plt.subplots(figsize=(8,6), dpi=200)

        node_color = clazz.loc[pd.IndexSlice[grade, directed_graph.nodes], "Color"]
        colors_in_graph = node_color.unique().tolist()
        node_color = node_color.tolist()
        classes_in_graph = clazz.loc[pd.IndexSlice[grade, directed_graph.nodes], "Class"].unique().tolist()
        clazz_legend_elements = [ mpl.lines.Line2D([0], [0], marker="o", color=color, linestyle="") for color in colors_in_graph ]

        edge_color = []
        edge_type = set()
        for (source, target) in directed_graph.edges:
            if source == target:
                edge_color.append("lightgray")
                edge_type.add(("self", "lightgray"))
            elif directed_graph.has_edge(target, source):
                edge_color.append("black")
                edge_type.add(("mutual", "black"))
            else:
                edge_color.append("gray")
                edge_type.add(("one-way", "gray"))

        class ArrowHandler(mpl.legend_handler.HandlerPatch):
            def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
                (r,g,b,a) = orig_handle.get_edgecolor()
                if r > 0:
                    return [orig_handle]
                else:
                    copy = mpl.patches.FancyArrow(14, 3, -12, 0, width=0.75, length_includes_head=True, head_width=3.5, color="black")
                    return [orig_handle, copy]

        edge_type = sorted(edge_type)
        edge_elements = [ mpl.patches.FancyArrow(5, 3, 14, 0, width=0.75, length_includes_head=True, head_width=3.5, color=color) for (name, color) in edge_type ]
        edge_type = [ name for (name, color) in edge_type ]

        legend_labels = [ *classes_in_graph, *edge_type ]
        legend_elements = [ *clazz_legend_elements, *edge_elements ]

        nx.draw_networkx(directed_graph, node_color=node_color, edge_color=edge_color, pos=directed_graph_layout(directed_graph))
        plt.legend(labels=legend_labels, handles=legend_elements, handler_map={mpl.patches.FancyArrow: ArrowHandler()})
        ax.axis("off")
        ax.set_aspect("equal")
        fig.tight_layout()

        og_path = PLOT_DIR / f"grade_{grade}_directed_graph.png"
        trimmed_path = PLOT_DIR / f"year_{grade}_nominations.png"

        fig.savefig(og_path)
        plt.close()
        cli.print(f"Saved visualization at {og_path}")

        result = subprocess.run([ "magick", "convert", og_path, "-trim", trimmed_path ])
        if result.returncode == 0:
            cli.print(f"Saved trimmed version at {trimmed_path}")
        else:
            cli.print("Failed to trim!")

        # ================================================================ #
        cli.section("Calculate Symmetric Distances")

        theoretical_max_dist = 2 * node_count

        symmetric_distances = get_symmetric_distances(directed_graph)

        path = PROCESSED_DIR / f"grade_{grade}_symmetric_distances.csv"
        symmetric_distances.to_csv(path)
        cli.print(f"Saved data at {path}")

        path = PLOT_DIR / f"grade_{grade}_symmetric_distances.png"
        plt.matshow(symmetric_distances, vmin=2, vmax=theoretical_max_dist)
        plt.colorbar()
        plt.xticks(ticks=range(len(symmetric_distances)), labels=symmetric_distances.columns)
        plt.yticks(ticks=range(len(symmetric_distances)), labels=symmetric_distances.columns)
        # plt.title(f"Grade {grade} Symmetric Distances")
        plt.savefig(path)
        plt.close()
        cli.print(f"Saved visualization at {path}")

        path = PLOT_DIR / f"grade_{grade}_symmetric_graph.png"
        fig, ax = plt.subplots(dpi=200, figsize=(8,6))
        draw_symmetric_graph(symmetric_distances, clazz, max_dist=theoretical_max_dist)
        # plt.title(f"Grade {grade} Symmetric Distance Graph")
        ax.set_aspect("equal")
        fig.savefig(path)
        plt.close()

        # ================================================================ #
        cli.section("Calculate Optimal Matchings")

        for kind in [ "minimum", "maximum" ]:
            partition, missing = get_partition(symmetric_distances, kind)

            cli.print(f"{kind.capitalize()} weight parition score: {partition.sum()}")
            cli.print(f"Missing indices: {missing}")
            cli.print(partition)

            meta_kind_key = f"{kind[:3]}_matching"
            metadata[meta_key][meta_kind_key] = {
                "total_score": partition.sum().item(),
                "min_distance": partition.min().item(),
                "max_distance": partition.max().item(),
                "missing_indices": list(missing),
            }

            path = PROCESSED_DIR / f"grade_{grade}_{kind[:3]}_partition.csv"
            partition.to_csv(path)
            cli.print(f"Saved data at {path}")

            path = PLOT_DIR / f"grade_{grade}_{kind[:3]}_partition_graph.png"
            fig, ax = plt.subplots(dpi=200, figsize=(8,6))
            draw_partition(symmetric_distances, clazz, partition, max_dist=theoretical_max_dist)
            # plt.title(f"Grade {grade} {kind.title()} Partition")
            ax.set_aspect("equal")
            fig.savefig(path)
            plt.close()

    # ================================================================ #
    cli.section("Save Metadata")

    cli.print(metadata)

    path = PROCESSED_DIR / "metadata.json"
    with open(path, "w") as file:
        json.dump(metadata, file, indent=4)
    cli.print(f"Saved metadata at {path}")


def get_directed_graph(df: pd.DataFrame, grade: int) -> nx.DiGraph:
    """
    Extracts the friendship nominations from `df` for a given grade as an `nx.DiGraph` directed graph.
    """

    graph = nx.DiGraph()
    nodes = set(df.loc[grade].index)

    for id1 in nodes:
        id1 = int(id1)
        graph.add_node(id1)

        for id2 in df.loc[(grade, id1)].squeeze():
            if id2.is_integer() and (id2 in nodes):
                id2 = int(id2)
                graph.add_edge(id1, id2)

    return graph


def get_symmetric_distances(graph: nx.DiGraph) -> pd.DataFrame:
    """
    Finds the shortest path from A to B and then back to A.
    Returns the output as a square `DataFrame` indexed by node ID.
    """

    num_nodes = len(graph.nodes)
    path_length = pd.DataFrame(
        { x: [ num_nodes ] * num_nodes for x in graph.nodes },
        index=graph.nodes,
    )

    for (first, distances) in nx.shortest_path_length(graph):
        for (second, dist) in distances.items():
            path_length.loc[first, second] = dist

    np_path_length = path_length.to_numpy()
    np_distances = np_path_length + np_path_length.T
    distances = pd.DataFrame(np_distances, columns=graph.nodes, index=graph.nodes)

    return distances


def get_dense_graph(distances: pd.DataFrame) -> nx.Graph:
    """Returns an `nx.Graph` fully-connected undirected weighted graph, whose weights correspond to the symmetric distance between nodes."""
    cols = distances.columns
    dense_graph = nx.Graph()

    for i in range(len(cols) - 1):
        for j in range(i + 1, len(cols)):
            first = cols[i]
            second = cols[j]
            dense_graph.add_edge(first, second, weight=distances.loc[first, second])

    return dense_graph


def get_partition(distances: pd.DataFrame, kind: Literal["minimum", "maximum"]) -> Tuple[pd.DataFrame, Set[int]]:
    """
    Returns `(partition, missing)`, where:
        * `partition` is a `DataFrame` containing the desired pairings and their symmetric distance.
        * `missing` is a `set` containing any missing IDs that were not included in the pairings.
    """
    dense_graph = get_dense_graph(distances)

    if kind == "minimum":
        partition = matching.min_weight_matching(dense_graph)
    else:
        partition = matching.max_weight_matching(dense_graph)

    df = pd.DataFrame()
    found = set()

    for (x, y) in partition:
        entry = pd.DataFrame({ "first": [x], "second": [y], "distance": [distances.loc[x,y]] }, index=[0])
        df = pd.concat([ df, entry ], ignore_index=True)
        found.add(x)
        found.add(y)

    df = df.set_index([ "first", "second" ])
    missing = set(distances.columns).difference(found)

    return (df, missing)


def draw_weighted_graph(graph: nx.Graph, clazz: pd.DataFrame, max_dist: int) -> None:
    """
    Uses `networkx` to draw a PyPlot figure containing an undirected graph with weighted edges.

    * Should be followed by `plt.show()`, `plt.savefig()`, or similar commands.
    * Edge weights assumed to be in range `[2, max_dist]`. Colorbar automatically added to the plot.
    """
    weights = [ weight for (source, target, weight) in graph.edges.data("weight") ]

    position = nx.shell_layout(graph)

    node_color = clazz.loc[pd.IndexSlice[:, graph.nodes], "Color"]
    colors_in_graph = node_color.unique().tolist()
    node_color = node_color.tolist()

    legend_labels = clazz.loc[pd.IndexSlice[:, graph.nodes], "Class"].unique().tolist()
    legend_elements = [ mpl.lines.Line2D([0], [0], marker="o", color=color, linestyle="") for color in colors_in_graph ]
    plt.legend(labels=legend_labels, handles=legend_elements, bbox_to_anchor=(0.1, 1.0))
    plt.gca().axis("off")

    nx.draw_networkx_nodes(graph, pos=position, node_color=node_color)
    edge_plot_data = nx.draw_networkx_edges(graph, pos=position, edge_color=weights, edge_vmin=2, edge_vmax=max_dist)
    plt.colorbar(edge_plot_data)
    nx.draw_networkx_labels(graph, pos=position)


def draw_symmetric_graph(distances: pd.DataFrame, clazz: pd.DataFrame, max_dist: int) -> None:
    """
    Draws the fully connected graph showing all weighted edges between nodes in `distances`.

    * Should be followed by `plt.show()`, `plt.savefig()`, or similar commands.
    * `distances` expected to be indexed and "columned" by a full set of node IDs.
    * Edge weights assumed to be in range `[2, max_dist]`. Colorbar automatically added to the plot.
    """

    cols = distances.columns
    graph = nx.Graph()

    for i in range(len(cols) - 1):
        for j in range(i + 1, len(cols)):
            first = cols[i]
            second = cols[j]
            graph.add_edge(first, second, weight=distances.loc[first, second])

    draw_weighted_graph(graph, clazz, max_dist)


def draw_partition(distances: pd.DataFrame, clazz: pd.DataFrame, partition: pd.DataFrame, max_dist: int) -> None:
    """
    Draws the matching subgraph given by `distances` (contains all nodes and distances for the full graph) and `partition` (contains the valid pairings as `"first"` and `"second"`).

    * Should be followed by `plt.show()`, `plt.savefig()`, or similar commands.
    * Edge weights assumed to be in range `[2, max_dist]`. Colorbar automatically added to the plot.
    """

    graph = nx.Graph()

    for node in distances.columns:
        graph.add_node(node)

    for (_, row) in partition.reset_index().iterrows():
        graph.add_edge(row["first"], row["second"], weight=row["distance"])

    draw_weighted_graph(graph, clazz, max_dist)


if __name__ == "__main__":
    main()
