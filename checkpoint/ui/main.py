import os
import sys
import json
from argparse import ArgumentParser
from subprocess import PIPE, Popen

import eel
import eel.browsers


@eel.expose
def run_cli_sequence(args=None):
    currentdir = os.path.dirname(os.path.abspath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0, os.path.dirname(parentdir))

    from checkpoint.sequences import CLISequence

    status = False
    checkpoint_arg_parser = ArgumentParser(
        description=f"Create restore points in your projects.",
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
        choices=["create", "restore", "delete", "init"],
    )

    checkpoint_arg_parser.add_argument(
        "--ignore-dirs",
        "-i",
        nargs="+",
        default=[".git", ".idea", ".vscode",
                 ".venv", "node_modules", "__pycache__"],
        help="Ignore directories."
    )

    cli_sequence = CLISequence(arg_parser=checkpoint_arg_parser, args=args)
    try:
        cli_sequence.execute_sequence(pass_args=True)
        status = True
    except Exception as e:
        status = False
        cli_sequence.logger.log(e, log_type="ERROR")

    return status


@eel.expose
def read_logs():
    """Read and parse the logs."""
    currentdir = os.path.dirname(os.path.abspath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0, os.path.dirname(parentdir))

    from checkpoint.io import IO

    io = IO()
    logs = io.read('logs.log')
    logs = logs.split('\n')
    parsed_logs = []
    for log in logs:
        log = log.split(':')[-1]
        parsed_logs.append(log)

    io.write('logs.log', 'w', '')  # Clear logs
    return parsed_logs


@eel.expose
def get_all_checkpoints(target_dir):
    """Get all checkpoints present inside athe target directory.
    
    Parameters
    ----------
    target_dir: str
        Path to the directory
    
    Returns
    -------
    list of str
        List containing names of all checkpoints
    """
    checkpoint_path = os.path.join(target_dir, '.checkpoint')
    checkpoints = []
    if not os.path.isdir(checkpoint_path):
        return []

    for dir in os.listdir(checkpoint_path):
        if os.path.isdir(os.path.join(checkpoint_path, dir)):
            checkpoints.append(dir)

    return checkpoints


def fetch_npm_package(package_name):
    """Fetch a package using node package manager.
    
    Parameters
    ----------
    package_name: str
        Name of the package.
    """
    npm_out = Popen(f'npm install --global {package_name}',
                    stdout=PIPE, shell=True).stdout.read().decode('utf-8')

    if 'npm ERR!' in npm_out:
        print(f'Error installing {package_name}')
        return ""

    return npm_out


def get_electron_bin():
    """Get the binaries for electron using npm.
    
    Returns
    -------
    path
        The path to the electron binaries.
    """
    os_name = os.name
    if os_name == 'nt':
        user_path = os.path.expanduser('~')
        node_modules_path = os.path.join(
            user_path, 'AppData', 'Roaming', 'npm', 'node_modules')
        electron_path = os.path.join(
            node_modules_path, 'electron', 'dist', 'electron.exe')
        return electron_path
    elif os_name == 'posix':
        user_path = 'root'
        node_modules_path = os.path.join(
            user_path, 'local', 'lib', 'node_modules')
        electron_path = os.path.join(
            node_modules_path, 'electron', 'dist', 'electron')
        return electron_path
    else:
        raise ValueError(f'{os_name} currently not supported.')


def init_ui():
    """Initialize the UI."""
    _electron_path = os.path.join(
        os.getcwd(), "node_modules/electron/dist/electron.exe")
    if not os.path.isfile(_electron_path):
        raise Exception(
            f'Electron not found in path {_electron_path}.\nPlease install using npm i electron')

    eel.init("./src")
    eel.browsers.set_path('electron', _electron_path)
    eel.start({
        'port': 3000,
    }, options={
        'port': 8888,
        'host': 'localhost',
        'args': [_electron_path, '.'],
    }, suppress_error=True, size=(1000, 600), mode="electron")


if __name__ == '__main__':
    init_ui()
