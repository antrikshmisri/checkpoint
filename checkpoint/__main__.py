from argparse import ArgumentParser

from checkpoint.sequences import CLISequence


if __name__ == "__main__":
    checkpoint_arg_parser = ArgumentParser(
        description="Checkpoint - Create restore points in your projects.",
        prog="checkpoint",
    )

    checkpoint_arg_parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize a new project.",
    )
    checkpoint_arg_parser.add_argument(
        "-n",
        "--name",
        type=str,
        help="Name of the restore point.",
        required=True
    )

    checkpoint_arg_parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="Path to the project.",
        required=True
    )

    checkpoint_arg_parser.add_argument(
        "-a",
        "--action",
        type=str,
        help="Action to perform.",
        required=True
    )

    checkpoint_arg_parser.add_argument(
        "--ignore-dirs",
        "-i",
        type=list,
        help="Ignore directories."
    )

    cli_sequence = CLISequence(arg_parser=checkpoint_arg_parser)
    cli_sequence.execute_sequence(pass_args=True)
