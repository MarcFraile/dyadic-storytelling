#!/bin/env -S python3


from dataclasses import asdict
from pretty_cli import PrettyCli
from local import arg_parsing


cli = PrettyCli()


def main():
    settings = arg_parsing.parse_default_args(description="Argument parsing test utility")
    cli.main_title("ARGUMENT PARSING TEST")
    cli.print(asdict(settings))


if __name__ == "__main__":
    main()
