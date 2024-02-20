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

SOURCES = [ "left-cam", "right-cam" ]
# SOURCES = [ "left-cam", "right-cam", "frontal-cam" ]

FEATURE_FILES : list[Path] = { source: OUT / f"{source}-summary-au-data.csv" for source in SOURCES }

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
    "linear":
        {
            "estimator": LogisticRegression(),
            "grid":  [
                {
                    "solver": [ "lbfgs" ], # Saga is the only one that supports all losses
                    "penalty": [ None, "l2" ],
                    "C": 10 ** np.linspace(-2, +2, 13),
                },
                {
                    "solver": [ "saga" ], # Saga is the only one that supports all losses
                    "penalty": [ None, "l1", "l2", "elasticnet" ],
                    "C": 10 ** np.linspace(-2, +2, 13),
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

cli = PrettyCli()


@dataclass
class TrainValSplit:
    train_indices: np.ndarray
    val_indices: np.ndarray


@dataclass
class TestSplit:
    test_indices: np.ndarray
    train_val_joint_indices: np.ndarray
    train_val_splits: list[TrainValSplit]


Grid = dict[str, Any] | list[dict[str, Any]]

def get_param_names(grid: Grid) -> list[str]:
    if isinstance(grid, dict):
        grid = [ grid ]

    params = set()
    for g in grid:
        params.update(g.keys())

    return sorted(params)


def _get_sklearn_grid_inner(grid: dict[str, Any]) -> dict[str, Any]:
    return { "clf__" + key: value for (key, value) in grid.items() }


def get_sklearn_grid(grid: Grid) -> Grid:
    if isinstance(grid, dict):
        return _get_sklearn_grid_inner(grid)
    else:
        return [ _get_sklearn_grid_inner(g) for g in grid ]


def get_splits(data: pd.DataFrame) -> list[TestSplit]:
    """
    Returns a list of `TestSplit` entries used for nested leave-one-out cross-validation.

    Each `TestSplit` gives a list of sample indices to be used for testing, and a list of `TrainValSplit` entries.
    Each `TrainVal` split gives a list of training indices, and a list of validation indices.

    Leave-one-out is done by choosing a child to exclude, and excluding any entries corresponding to a session the child participated in.
    This means some entries corresponding to other children (who palyed with the out-child) are also excluded.
    """

    index = data.index.to_frame().reset_index(drop=True)
    children = data.index.get_level_values("child_id").unique()

    test_splits = []

    for test_child in children:

        test_sessions = set(index.loc[index["child_id"] == test_child, "pair_id"])
        test_mask = index["pair_id"].isin(test_sessions)

        test_indices = index[test_mask].index.to_numpy()
        train_val_joint_indices = index[~test_mask].index.to_numpy()

        train_val_splits = []

        for val_child in children:
            if val_child == test_child:
                continue

            val_sessions = set(index.loc[index["child_id"] == val_child, "pair_id"])
            val_sessions = val_sessions - test_sessions
            val_mask = index["pair_id"].isin(val_sessions)
            val_indices = index[val_mask].index.to_numpy()

            train_mask = ~(test_mask | val_mask)
            train_indices = index[train_mask].index.to_numpy()

            train_val_splits.append(TrainValSplit(train_indices, val_indices))

        test_splits.append(TestSplit(test_indices, train_val_joint_indices, train_val_splits))

    return test_splits


def main() -> None:
    cli.main_title("SIMPLE ML - NEW EDITION")

    assert OUT.is_dir()

    score_funcs = { score: get_scorer(score) for score in SCORES }

    np.random.seed(SEED)

    for source in SOURCES:
        cli.chapter(source)

        cli.section("Loading Data")

        feature_file = FEATURE_FILES[source]
        assert feature_file.is_file()

        all_features = pd.read_csv(feature_file, index_col=["pair_id", "round", "child_id"])
        splits = get_splits(all_features)

        detailed_runs = pd.DataFrame()
        run_summary = pd.DataFrame()

        for (feature_set, model_name) in itertools.product(FEATURE_COMBINATIONS, MODELS):
            cli.subchapter(f"Features: {feature_set}; Model: {model_name}")

            features = all_features[feature_set].to_numpy()
            labels = (all_features["condition"] == "positive").astype(int).to_numpy()

            base_model = MODELS[model_name]["estimator"]
            param_grid = MODELS[model_name]["grid"]
            param_names = get_param_names(param_grid)

            pipeline = Pipeline([ ("scale", StandardScaler()), ("clf", base_model) ])

            test_scores = dict()
            for score_name in SCORES:
                test_scores["best_mean_val_" + score_name] = []
                test_scores["train_" + score_name] = []
                test_scores["test_" + score_name] = []

            best_params = { param: [] for param in param_names }
            test_conf = [] # Confusion matrices

            for split in splits:
                X_test = features[split.test_indices]
                Y_test = labels[split.test_indices]

                X_tv = features[split.train_val_joint_indices]
                Y_tv = labels[split.train_val_joint_indices]

                cv = [ (tvs.train_indices, tvs.val_indices) for tvs in split.train_val_splits ]
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

                pred_tv = clf.predict(X_tv)
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

            one_summary = one_run[test_scores.keys()].mean()
            one_summary["test_conf"] = one_run["test_conf"].sum().tolist()
            one_summary["features"] = one_run["features"].iloc[0]
            one_summary["model"] = one_run["model"].iloc[0]
            one_summary = one_summary.to_frame().T

            detailed_runs = pd.concat([ detailed_runs, one_run ])
            run_summary = pd.concat([ run_summary, one_summary ], ignore_index=True)

        detailed_runs.index.name = "test_split"
        detailed_runs.reset_index(inplace=True, drop=False)
        detailed_runs.set_index([ "features", "model", "test_split" ], inplace=True)
        detailed_runs.sort_index(inplace=True)

        cli.print(run_summary)
        run_summary = run_summary.set_index([ "features", "model" ], drop=True).sort_index()

        cli.chapter("Results")

        cli.subchapter("Detailed Runs")
        cli.print(detailed_runs)
        detailed_runs.to_csv(OUT / f"{source}-simple-ml-data-detailed-runs.csv")

        cli.subchapter("Run Summary")
        cli.print(run_summary)
        run_summary.to_csv(OUT / f"{source}-simple-ml-data-run-summary.csv")


if __name__ == "__main__":
    main()
