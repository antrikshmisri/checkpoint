from argparse import ArgumentParser

from checkpoint import __version__ as version
from checkpoint.sequences import CLISequence
from checkpoint.utils import Logger


def run(args=None):
    logger = Logger()
    checkpoint_arg_parser = ArgumentParser(
        description=f"Create restore points in your projects. Version: {version}",
        prog="checkpoint",
    )

    checkpoint_arg_parser.add_argument(
        "-n",
        "--name",
        type=str,
        help="Name of the restore point.",
    )

    checkpoint_arg_parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="Path to the project.",
    )

    checkpoint_arg_parser.add_argument(
        "-a",
        "--action",
        type=str,
        help="Action to perform.",
        choices=["create", "restore", "version", "delete", "init"],
    )

    checkpoint_arg_parser.add_argument(
        "--ignore-dirs",
        "-i",
        nargs="+",
        default=[".git", ".idea", ".vscode",
                 ".venv", "node_modules", "__pycache__"],
        help="Ignore directories."
    )

    cli_sequence = CLISequence(arg_parser=checkpoint_arg_parser, args=args, logger=logger)
    cli_sequence.execute_sequence(pass_args=True)


if __name__ == "__main__":
    run()
