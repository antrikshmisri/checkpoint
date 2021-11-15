import os
from argparse import ArgumentParser

from checkpoint import __version__ as version
from checkpoint.sequences import CLISequence
from checkpoint.utils import execute_command


def run(args=None):
    checkpoint_arg_parser = ArgumentParser(
        description=f"Create restore points in your projects. Version: {version}",
        prog="checkpoint",
    )

    checkpoint_arg_parser.add_argument(
        "--run-ui",
        action="store_true",
        help="Start checkpoint in UI environment",
        default=False,
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
    if args is not None:
        run_ui = args.run_ui
    else:
        run_ui = checkpoint_arg_parser.parse_args().run_ui

    if run_ui:
        _dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(os.path.join(_dir, "ui"))
        for line in execute_command('yarn start'):
            print(line, end='')
            if "exited" in line:
                exit(0)
    else:
        cli_sequence = CLISequence(
            arg_parser=checkpoint_arg_parser, args=args, terminal_log=True)
        cli_sequence.execute_sequence(pass_args=True)


if __name__ == "__main__":
    run()
