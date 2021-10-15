import os
from argparse import ArgumentParser

from checkpoint.sequences import IOSequence, CLISequence
from checkpoint.utils import LogColors, Logger


if __name__ == "__main__":
    checkpoint_arg_parser = ArgumentParser(
        description="Checkpoint - Create restore points in your projects.",
        prog="checkpoint",
    )

    checkpoint_arg_parser.add_argument(
        "--init",
        "-I",
        action="store_true",
        help="Initialize a new project.",
    )
    checkpoint_arg_parser.add_argument(
        "--name",
        "-n",
        type=str,
        help="Name of the restore point.",
    )

    checkpoint_arg_parser.add_argument(
        "--path",
        "-p",
        type=str,
        help="Path to the project.",
    )

    checkpoint_arg_parser.add_argument(
        "--action",
        "-a",
        type=str,
        help="Action to perform.",
    )

    checkpoint_arg_parser.add_argument(
        "--ignore-dirs",
        "-i",
        action="store_true",
        help="Ignore directories."
    )
    checkpoint_arg_parser.print_help()
    cli_sequence = CLISequence(arg_parser=checkpoint_arg_parser)
    cli_sequence.execute_sequence(pass_args=True)
