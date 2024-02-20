#!/bin/env -S python3 -u


from typing import List, Optional, Callable, Dict
import sys
from dataclasses import dataclass, asdict

import pandas as pd
from pretty_cli import PrettyCli


# ================ Types ================ #


@dataclass
class ChildIdentity:
    name : str
    id   : int


@dataclass
class ChildInfo:
    identity : ChildIdentity
    grade    : int
    min_pair : Optional[ChildIdentity]
    max_pair : Optional[ChildIdentity]


@dataclass
class GradeData:
    max_partition       : pd.DataFrame
    min_partition       : pd.DataFrame
    symmetric_distances : pd.DataFrame


@dataclass
class Data:
    id_mappings : pd.DataFrame
    grade_2     : GradeData
    grade_3     : GradeData

    def get_grade(self, grade: int) -> GradeData:
        if grade == 2:
            return self.grade_2
        if grade == 3:
            return self.grade_3
        raise ValueError(f"Invalid grade: {grade} (should be 2 or 3).")


Command = Callable[[List[str]], None]


# ================ Functions and Static Data ================ #


def get_grade_data(grade: int) -> GradeData:
    max_partition       = pd.read_csv(f"data/processed/grade_{grade}_max_partition.csv")
    min_partition       = pd.read_csv(f"data/processed/grade_{grade}_min_partition.csv")
    symmetric_distances = pd.read_csv(f"data/processed/grade_{grade}_symmetric_distances.csv", index_col="Unnamed: 0")

    symmetric_distances.columns = symmetric_distances.columns.astype("int64")

    return GradeData(max_partition, min_partition, symmetric_distances)


def load_data() -> Data:
    return Data(
        id_mappings = pd.read_csv("data/raw/id_mappings.csv"),
        grade_2     = get_grade_data(grade=2),
        grade_3     = get_grade_data(grade=3),
    )


DATA = load_data()
cli = PrettyCli()


def get_child_base(key: str) -> ChildIdentity:
    key = key.strip()
    if key.isnumeric():
        id   = int(key)
        name = DATA.id_mappings.set_index("id").loc[id, "name"]
    else:
        name = key.title()
        id   = DATA.id_mappings.set_index("name").loc[name, "id"]

    return ChildIdentity(name, id)


def find_pair(id: int, partition: pd.DataFrame) -> Optional[ChildIdentity]:
    if id in partition["first"].values:
        second_id = partition.loc[partition["first"] == id, "second"].item()
    elif id in partition["second"].values:
        second_id = partition.loc[partition["second"] == id, "first"].item()
    else:
        return None

    return get_child_base(str(second_id))


def get_child_info(key: str) -> ChildInfo:
    base = get_child_base(key)
    entry = DATA.id_mappings.set_index("id").loc[base.id]

    grade = int(entry["grade"])

    grade_data = DATA.get_grade(grade)
    min_pair = find_pair(base.id, grade_data.min_partition)
    max_pair = find_pair(base.id, grade_data.max_partition)

    return ChildInfo(base, grade, min_pair, max_pair)


# ================ Commands ================ #


def cmd_info(args: List[str]) -> None:
    """Get information about the given children."""
    assert len(args) >= 1, "At least one ID or name required; none received."

    output = { key: asdict(get_child_info(key)) for key in args }
    cli.print(output)


def cmd_dist(args: List[str]) -> None:
    """Get the symmetric network distance between the two given children."""
    assert len(args) == 2, f"Exactly 2 IDs / names required; received {len(args)}."

    [ key_1, key_2 ] = args
    info_1 = get_child_info(key_1)
    info_2 = get_child_info(key_2)

    assert info_1.grade == info_2.grade, f"Children are in different grades! ({info_1.identity.name}: {info_1.grade}; {info_2.identity.name}: {info_2.grade})."
    distances = DATA.get_grade(info_1.grade).symmetric_distances

    d = distances.loc[info_1.identity.id, info_2.identity.id]
    output = { "distance": d }
    cli.print(output)


def cmd_shell(args: List[str]) -> None:
    """Start an interactive shell."""
    assert len(args) == 0

    should_quit = False
    def cmd_quit(args: List[str]) -> None:
        """Quit the interactive shell."""
        nonlocal should_quit
        should_quit = True

    COMMANDS["quit"] = cmd_quit
    COMMANDS["list"] = cmd_list
    COMMANDS["help"] = cmd_help
    del COMMANDS["shell"]

    while not should_quit:
        try:
            in_args = input("> ").split()
        except EOFError: # Ctrl + D => Quit
            break

        if len(in_args) < 1:
            continue

        try:
            func = COMMANDS[in_args[0]]
            func(in_args[1:])
        except Exception as e:
            cli.print(f"\u001b[31m{type(e).__name__}: {e}\u001b[0m")

    cli.blank()
    sys.exit(0)

def get_command_list() -> List[str]:
    output = []

    name_len = max(len(name) for name in COMMANDS.keys())
    name_fmt = f"<{name_len}"

    for (name, func) in COMMANDS.items():
        output.append(f"{name:{name_fmt}} - {func.__doc__}")

    return output


def cmd_list(args: List[str]) -> None:
    """List all available commands."""
    assert len(args) == 0

    command_list = get_command_list()
    for command_description in command_list:
        cli.print(command_description)


def cmd_help(args: List[str]) -> None:
    """Alias for 'list'."""
    cmd_list(args)


COMMANDS: Dict[str, Command] = {
    "info"  : cmd_info,
    "dist"  : cmd_dist,
    "shell" : cmd_shell,

}


# ================ Kickstart ================ #


def usage() -> None:
    """Prints the usage string, including all known commands and their descriptions."""

    cli.print(f"Usage: {sys.argv[0]} <command> [options...]\n\nCommands:")

    command_list = get_command_list()
    for command_description in command_list:
        cli.print(f"    {command_description}")


def main() -> None:
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    func = COMMANDS[sys.argv[1]]
    func(sys.argv[2:])


if __name__ == "__main__":
    main()
