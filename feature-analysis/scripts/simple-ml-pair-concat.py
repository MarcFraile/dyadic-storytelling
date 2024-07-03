#!/bin/env -S python3 -u


# ================================================================ #
# SIMPLE ML ON THE NEW CLEAN DATA
# ================================================================ #
# ---------------------------------------------------------------- #
# LEFT CAM Significant Stats After P-Val Adjustment
# ---------------------------------------------------------------- #
#                        p-val   cohen-d
# variable
# AU10_presence_std   0.017746  0.541243
# AU10_presence_q95   0.000410  0.680781
# AU12_presence_std   0.010718  0.558874
# AU12_presence_q95   0.003284  0.604881
# AU25_presence_std   0.043035  0.509586
# AU10_intensity_q95  0.012776  0.552074
# AU12_intensity_std  0.008032  0.563946
# AU12_intensity_q95  0.011002  0.554482
# AU25_intensity_std  0.031784  0.516944
# ---------------------------------------------------------------- #
# The common ground is that AU10 and AU12 have strong reactions
# in the Q95 and in their STD. Since Q95 is used in some of the
# literature I have read, that is an easy to justify choice.
# ---------------------------------------------------------------- #
# RIGHT CAM Significant Stats After P-Val Adjustment
# ---------------------------------------------------------------- #
#                        p-val   cohen-d
# variable
# AU12_presence_std   0.018679  0.544083
# AU12_presence_q95   0.020896   0.55114
# AU26_presence_mean  0.026767  0.523637
# AU26_presence_std   0.003549  0.612068
# AU12_intensity_std    0.0124  0.550851
# AU12_intensity_q95  0.009536  0.560579
# ---------------------------------------------------------------- #
# AU12 shows same response as LEFT CAM, but we get AU26 instead of
# AU10 and AU25. We also get one mean for a change.
# ================================================================ #


import warnings
import itertools
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

import sklearn.base
from sklearn import model_selection
from sklearn.metrics import confusion_matrix, get_scorer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from pretty_cli import PrettyCli


OUT = Path("output")
K_FOLDS_JSON = OUT / "k_folds.json"

SOURCES = [ "left-cam", "right-cam" ]
FEATURE_FILES = { source: OUT / f"{source}-summary-au-data.csv" for source in SOURCES }

FEATURE_COMBINATIONS = [
    # Purely based on what has the most statistically significant difference between conditions:
    # We choose au in [ AU10, AU12 ]; mode in [ intensity, presence ]; stat=q95; either one AU or both.
    [ "AU10_presence_q95" , "AU12_presence_q95"  ],
    [ "AU10_intensity_q95", "AU12_intensity_q95" ],

    [ "AU10_presence_q95" ,                      ],
    [ "AU10_intensity_q95",                      ],

    [                       "AU12_presence_q95"  ],
    [                       "AU12_intensity_q95" ],

    # Still choosing AU10 and AU12 based on stats, but using mean and STD based on prior work:
    [ "AU10_presence_mean", "AU10_presence_std", "AU12_presence_mean", "AU12_presence_std" ],
    [ "AU10_presence_mean", "AU10_presence_std",                                           ],
    [                                            "AU12_presence_mean", "AU12_presence_std" ],

    # Now substituting AU10 => AU25.
    [ "AU25_presence_q95" , "AU12_presence_q95"  ],
    [ "AU25_intensity_q95", "AU12_intensity_q95" ],

    [ "AU25_presence_q95" ,                      ],
    [ "AU25_intensity_q95",                      ],

    [ "AU25_presence_mean", "AU25_presence_std", "AU12_presence_mean", "AU12_presence_std" ],
    [ "AU25_presence_mean", "AU25_presence_std",                                           ],

    # Now substituting AU10 => AU26.
    [ "AU26_presence_q95" , "AU12_presence_q95"  ],
    [ "AU26_intensity_q95", "AU12_intensity_q95" ],

    [ "AU26_presence_q95" ,                      ],
    [ "AU26_intensity_q95",                      ],

    [ "AU26_presence_mean", "AU26_presence_std", "AU12_presence_mean", "AU12_presence_std" ],
    [ "AU26_presence_mean", "AU26_presence_std",                                           ],

    # Theory-based: happiness
    [ "AU06_presence_q95" , "AU12_presence_q95"  ],
    [ "AU06_intensity_q95", "AU12_intensity_q95" ],

    [ "AU06_presence_mean" , "AU06_presence_std" , "AU12_presence_mean" , "AU12_presence_std"  ],
    [ "AU06_intensity_mean", "AU06_intensity_std", "AU12_intensity_mean", "AU12_intensity_std" ],
]

MODELS = {
    "linear": {
            "estimator": LogisticRegression(),
            "grid":  [
                {
                    "solver": [ "lbfgs" ], # Saga is the only one that supports all losses
                    "penalty": [ "l2" ],
                    "C": 10 ** np.linspace(-2, +2, 13),
                },
                {
                    "solver": [ "saga" ], # Saga is the only one that supports all losses
                    "penalty": [ "l1", "l2", "elasticnet" ],
                    "C": 10 ** np.linspace(-2, +2, 13),
                },
                {
                    "solver": [ "lbfgs", "saga" ],
                    "penalty": [ None ],
                },
            ],
        },
    "svm": {
        "estimator": SVC(),
        "grid": [
            {
                "C": 10 ** np.linspace(-2, +2, 13),
                "kernel": [ "linear" ],
            },
            {
                "C": 10 ** np.linspace(-2, +2, 13),
                "kernel": [ "rbf" ],
                "gamma": [ "scale", "auto" ],
            },
        ],
    },
    "tree": {
        "estimator": DecisionTreeClassifier(),
        "grid": {
            "criterion": [ "gini", "entropy" ],
            "max_depth": [ 2, 3, 4, 5 ],
        },
    },
}

SCORES = [ "accuracy", "balanced_accuracy", "matthews_corrcoef" ]
MAIN_SCORE = "accuracy"

SEED = 380775725


@dataclass
class TrainValSplit:
    train_pairs : list[str]
    val_pairs   : list[str]


@dataclass
class TestSplit:
    test_pairs            : list[str]
    train_val_joint_pairs : list[str]
    train_val_splits      : list[TrainValSplit]


Grid = dict[str, Any] | list[dict[str, Any]]


def get_param_names(grid: Grid) -> list[str]:
    """Returns a sorted list of parameter names."""
    if isinstance(grid, dict):
        grid = [ grid ]

    params = set()
    for g in grid:
        params.update(g.keys())

    return sorted(params)


def _get_sklearn_grid_inner(grid: dict[str, Any]) -> dict[str, Any]:
    """Internal function. Called by `get_sklearn_grid()`."""
    return { "clf__" + key: value for (key, value) in grid.items() }


def get_sklearn_grid(grid: Grid) -> Grid:
    """Appends 'clf__' to each parameter name."""
    if isinstance(grid, dict):
        return _get_sklearn_grid_inner(grid)
    else:
        return [ _get_sklearn_grid_inner(g) for g in grid ]


def get_splits() -> list[TestSplit]:
    with open(K_FOLDS_JSON, "r") as handle:
        k_folds = json.load(handle)

    # fold => pair ID set.
    pair_ids: list[set[str]] = [ set(fold["pair_ids"]) for fold in k_folds["folds"] ]

    # Sanity checks: we have 5 folds, and they're nonempty.
    assert len(pair_ids) == 5
    for ids in pair_ids:
        assert len(ids) > 0

    all_pairs = set()
    for fold_pairs in pair_ids:
        all_pairs.update(fold_pairs)

    test_splits = []
    for test_fold, test_pairs in enumerate(pair_ids):

        train_val_splits = []
        for val_fold in range(len(pair_ids)):
            if val_fold == test_fold:
                continue

            val_pairs = pair_ids[val_fold]
            train_pairs = all_pairs - test_pairs - val_pairs

            train_val_splits.append(TrainValSplit(train_pairs=train_pairs, val_pairs=val_pairs))

        test_splits.append(TestSplit(test_pairs=test_pairs, train_val_joint_pairs=(all_pairs - test_pairs), train_val_splits=train_val_splits))

    return test_splits


def process_one_source(cli: PrettyCli, source: str) -> None:
    # ================================================================ #
    cli.section("Loading Data")

    score_funcs = { score: get_scorer(score) for score in SCORES }

    feature_file = FEATURE_FILES[source]
    assert feature_file.is_file()

    all_features = pd.read_csv(feature_file, index_col=["pair_id", "round", "child_id"]).sort_index()

    splits = get_splits()

    detailed_runs = pd.DataFrame()
    run_summary = pd.DataFrame()

    for (feature_set, model_name) in itertools.product(FEATURE_COMBINATIONS, MODELS):
        # ================================================================ #
        cli.subchapter(f"Features: {feature_set}; Model: {model_name}")

        # Stack features from both children in the same video.
        features = all_features[feature_set].reset_index()
        features["child_id"] = features.reset_index().groupby(["pair_id", "round"]).cumcount()
        features = features.set_index(["pair_id", "round", "child_id"])
        features = features.unstack(level="child_id")

        labels = features.index.get_level_values("pair_id").str.startswith("P").astype(int)

        # ================================================================ #
        cli.section("Features")
        cli.print(features)

        # ================================================================ #
        cli.section("Labels")
        cli.print(labels)

        base_model = MODELS[model_name]["estimator"]
        param_grid = MODELS[model_name]["grid"]
        param_names = get_param_names(param_grid)

        pipeline = Pipeline([ ("scale", StandardScaler()), ("clf", base_model) ])

        test_scores = dict()
        for score_name in SCORES:
            test_scores["best_mean_val_" + score_name] = []
            test_scores["train_"         + score_name] = []
            test_scores["test_"          + score_name] = []

        best_params = { param: [] for param in param_names }
        test_conf = [] # Confusion matrices

        for split_idx, split in enumerate(splits):
            cli.small_divisor()
            cli.section(f"Split {split_idx}")

            def get_indices(pairs: list[str]) -> np.ndarray:
                return features.index.get_level_values("pair_id").isin(pairs)

            test_indices = get_indices(split.test_pairs)
            X_test = features[test_indices]
            Y_test = labels  [test_indices]

            train_val_joint_indices = get_indices(split.train_val_joint_pairs)
            X_tv = features[train_val_joint_indices]
            Y_tv = labels  [train_val_joint_indices]

            cv = [ (get_indices(tvs.train_pairs), get_indices(tvs.val_pairs)) for tvs in split.train_val_splits ]
            param_grid_sklearn = get_sklearn_grid(param_grid)

            search_results = model_selection.GridSearchCV(estimator=pipeline, param_grid=param_grid_sklearn, cv=cv, scoring=SCORES, refit=MAIN_SCORE)

            with warnings.catch_warnings():
                warnings.simplefilter(action="ignore")
                search_results.fit(features, labels)

            # I suspect the trained classifier returned by GridSearchCV uses ALL the data available in (features, labels) for training, which is wrong.
            # Therefore, we roll our own fitting here.
            clf = sklearn.base.clone(pipeline)
            clf.set_params(**search_results.best_params_)
            clf.fit(X_tv, Y_tv)

            pred_tv   = clf.predict(X_tv)
            pred_test = clf.predict(X_test)

            for score_name in SCORES:
                # Best score in the grid search. Averaged over the validation folds. Used to choose the hyper-parameters.
                best_val_score = search_results.cv_results_["mean_test_" + score_name][search_results.best_index_]
                test_scores["best_mean_val_" + score_name].append(best_val_score)

                # Score over the data used to train the final model (the union of all the train and/or validation data).
                # Equivalent to GridSearchCV's out-of-the-box training scores, if we didn't have to worry about the nested cross-validation scheme.
                tv_score = score_funcs[score_name]._score_func(y_true=Y_tv, y_pred=pred_tv)
                test_scores["train_" + score_name].append(tv_score)

                # Good old test score for this fold.
                test_score = score_funcs[score_name]._score_func(y_true=Y_test, y_pred=pred_test)
                test_scores["test_" + score_name].append(test_score)

            test_conf.append(confusion_matrix(y_true=Y_test, y_pred=pred_test))

            for param in param_names:
                key = "clf__" + param
                value = search_results.best_params_.get(key, None)
                best_params[param].append(value)

        one_run = pd.DataFrame({ **test_scores, **best_params, "test_conf": test_conf })
        one_run["features"] = str(feature_set).replace(" ", "")
        one_run["model"] = type(base_model).__name__

        one_summary_means = one_run[test_scores.keys()].mean()
        one_summary_means.index += "_mean"

        one_summary_stds = one_run[test_scores.keys()].std()
        one_summary_stds.index += "_std"

        one_summary = pd.concat([one_summary_means, one_summary_stds]).sort_index()

        one_summary["test_conf"] = one_run["test_conf"].sum().tolist()
        one_summary["features" ] = one_run["features" ].iloc[0]
        one_summary["model"    ] = one_run["model"    ].iloc[0]
        one_summary = one_summary.to_frame().T

        detailed_runs = pd.concat([ detailed_runs, one_run ])
        run_summary = pd.concat([ run_summary, one_summary ], ignore_index=True)

    detailed_runs.index.name = "test_split"
    detailed_runs["test_conf"] = detailed_runs["test_conf"].map(lambda conf: conf.tolist())
    detailed_runs.reset_index(inplace=True, drop=False)
    detailed_runs.set_index([ "features", "model", "test_split" ], inplace=True)
    detailed_runs.sort_index(inplace=True)

    # ================================================================ #
    cli.chapter("Results")

    cli.subchapter("Detailed Runs")
    cli.print(detailed_runs)
    detailed_runs.to_csv(OUT / f"{source}-simple-ml-pair-concat-detailed-runs.csv")

    cli.subchapter("Run Summary")
    run_summary = run_summary.set_index([ "features", "model" ], drop=True).sort_index()
    cli.print(run_summary)
    run_summary.to_csv(OUT / f"{source}-simple-ml-pair-concat-run-summary.csv")


def main() -> None:
    cli = PrettyCli()
    cli.main_title("SIMPLE ML - JOINT PAIR")

    assert OUT.is_dir()


    np.random.seed(SEED)

    for source in SOURCES:
        cli.chapter(source)
        process_one_source(cli, source)


if __name__ == "__main__":
    main()
