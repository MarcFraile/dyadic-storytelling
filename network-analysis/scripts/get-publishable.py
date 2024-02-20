#!/bin/env -S python3 -u


import warnings
from pathlib import Path

import pandas as pd
from pandas.errors import SettingWithCopyWarning

from pretty_cli import PrettyCli


DATA_ROOT = Path("data")
RAW = DATA_ROOT / "raw"
PROCESSED = DATA_ROOT / "processed"

CHILD_PUBLISHABLE_FILE = RAW / "publishable.csv"
QUESTIONNAIRE_FILE = RAW / "Student Data - Anonymized Questionnaires.csv"
OUT_FILE = PROCESSED / "publishable_pairs.csv"

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

cli = PrettyCli()


def main() -> None:
    cli.main_title("GET PUBLISHABLE PAIRS")

    assert DATA_ROOT.is_dir()

    assert QUESTIONNAIRE_FILE.is_file()
    assert CHILD_PUBLISHABLE_FILE.is_file()

    if not PROCESSED.is_dir():
        PROCESSED.mkdir(parents=False, exist_ok=False)

    child_publishable = pd.read_csv(CHILD_PUBLISHABLE_FILE, index_col="id")
    questionnaire_data = pd.read_csv(QUESTIONNAIRE_FILE)

    wide = questionnaire_data[["child_id", "pair_id"]]
    wide["child"] = wide.groupby("pair_id").cumcount()
    wide = wide.pivot(index="pair_id", columns="child", values="child_id")
    wide.columns = [ "c1", "c2" ]

    wide = wide.join(child_publishable, on="c1")
    wide = wide.rename({ "publishable": "c1_pub" }, axis=1)

    wide = wide.join(child_publishable, on="c2")
    wide = wide.rename({ "publishable": "c2_pub" }, axis=1)

    wide["pub"] = (wide["c1_pub"] == "Yes") & (wide["c2_pub"] == "Yes")
    wide["pub"] = wide["pub"].replace({ True: "Yes", False: "No" })

    cli.section("Overall Table")
    cli.print(wide)
    wide.to_csv(OUT_FILE)

    cli.section("Publishable Pairs")
    cli.print(wide[wide["pub"] == "Yes"].index.tolist())


if __name__ == "__main__":
    main()
