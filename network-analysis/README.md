# Using Real-World Data

## Network Analysis

* `scripts/pair-making` consumes anonymized friendship nominations from `data/raw/Student Data - Anonymized Nominations.csv`. For each grade (2 and 3), it creates:
    * `data/processed/grade_*_directed_graph.png` visualises the directed graph described by the nominations. The plotting algorithm is imperfect, but it tries to separate connected components.
    * `data/processed/grade_*_symmetric_distances.(csv|png)` describe (`.csv`) and visualise (`.png`) the symmetric distance between participants.
        * First, we can define a *directed distance* as
          ```
          d'(A,B):
            if paths exists from A to B:
                return shortest path A -> B
            else:
                return number of nodes in graph
          ```
          (note that the number of nodes in the graph is strictly bigger than the greatest simple path).
        * Then, we can define the *symmetric distance* as `d(A,B) = d'(A,B) + d'(B,A)`.
            * Shortest possible distance: `2` (both children nominated each other).
            * Longest possible distance: `2 * (number of nodes in graph)` (children are in separate subgraphs).
* `scripts/query.py` is a CLI tool (including interactive mode) to query information about children and distances between children.
    * Can take both child name or pseudonymous ID as identifier.

## Questionnaire Statistical Analysis

* `scripts/statistical-analysis.py` performs statistical testing of the questionnaire results, as read from `data/raw/Student Data - Anonymized Questionnaires.csv`.
