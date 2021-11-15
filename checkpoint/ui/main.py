import json
import os
import sys
from argparse import ArgumentParser
from subprocess import PIPE, Popen
from webbrowser import open_new_tab

import eel
import eel.browsers

try:
    from checkpoint.io import IO
    from checkpoint.sequences import CLISequence
    IN_DEVELOPMENT = False
except ImportError:
    currentdir = os.path.dirname(os.path.abspath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0, os.path.dirname(parentdir))

    from checkpoint.io import IO
    from checkpoint.sequences import CLISequence
    IN_DEVELOPMENT = True


@eel.expose
def run_cli_sequence(args=None):
    args = args[0:2] + ['-i'] + args[3].split(" ") + args[4:]

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

    try:
        cli_sequence = CLISequence(arg_parser=checkpoint_arg_parser, args=args)
        cli_sequence.execute_sequence(pass_args=True)
        status = True
    except Exception as e:
        status = False
        cli_sequence.logger.log(e, log_type="ERROR")

    return status


@eel.expose
def read_logs():
    """Read and parse the logs."""

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

    if not os.path.isdir(checkpoint_path):
        return []

    config_path = os.path.join(checkpoint_path, '.config')
    if not os.path.isfile(config_path):
        checkpoints = []
    else:
        with open(config_path, 'r') as f:
            config = json.load(f)
            checkpoints = config['checkpoints']

    return checkpoints


@eel.expose
def get_ignore_dirs(target_dir):
    checkpoint_path = os.path.join(target_dir, '.checkpoint')

    config_path = os.path.join(checkpoint_path, '.config')
    if not os.path.isfile(config_path):
        return []
    with open(config_path, 'r') as f:
        config = json.load(f)
        ignore_dirs = config['ignore_dirs']

    return ignore_dirs


@eel.expose
def get_current_checkpoint(target_dir):
    checkpoint_path = os.path.join(target_dir, '.checkpoint')

    config_path = os.path.join(checkpoint_path, '.config')
    if not os.path.isfile(config_path):
        return None

    with open(config_path, 'r') as f:
        config = json.load(f)
        current_checkpoint = config['current_checkpoint']

    return current_checkpoint


@eel.expose
def generate_tree(checkpoint_name, target_directory):
    """Generate a Tree from the metadata of a certain checkpoint.

    Parameters
    ----------
    checkpoint_name: str
        Name of the checkpoint.
    target_directory: str
        Path to the target directory.
    """
    class Tree:
        def __init__(self, name, folders=None, files=None, parent=None):
            self.name = name
            self.folders = folders or []
            self.files = files or []
            self.parent = parent

        def add_folder(self, folder):
            self.folders.append(folder)
            folder.parent = self

    tree_dict = {}
    curr_folder_idx = 0

    io = IO(target_directory)
    checkpoint_path = os.path.join(
        target_directory, '.checkpoint', checkpoint_name)
    metadata = io.read(os.path.join(checkpoint_path, '.metadata'))
    metadata = json.loads(metadata)

    for folder, files in metadata.items():
        parent = None
        if curr_folder_idx:
            split_idx = -2
            while folder.split("\\")[split_idx] not in tree_dict:
                split_idx = split_idx - 1
            parent = tree_dict[folder.split("\\")[split_idx]]

        files = [file.split("\\")[-1] for file in files]
        folder = folder.split("\\")[-1]
        folder_tree = Tree(folder, files=files, parent=parent)

        if parent:
            parent.add_folder(folder_tree)

        tree_dict[folder] = folder_tree
        curr_folder_idx += 1

    serializable_tree = {}
    for folder_name, folder_tree in tree_dict.items():
        serializable_tree[folder_name] = {
            'name': folder_tree.name,
            'folders': [folder.name for folder in folder_tree.folders],
            'files': folder_tree.files
        }

    return serializable_tree


@eel.expose
def validate_path(path):
    """Validate a path.

    Parameters
    ----------
    path: str
        Path to validate
    """
    if not os.path.isdir(path):
        return False

    return True


@eel.expose
def open_browser(url):
    """Open a URL in browser.

    Parameters
    ----------
    url: str
        URL to open.
    """
    open_new_tab(url)


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
    if IN_DEVELOPMENT:
        _electron_path = os.path.join(
            os.getcwd(), "node_modules/electron/dist/electron.exe")
        if not os.path.isfile(_electron_path):
            raise Exception(
                f'Electron not found in path {_electron_path}.\n')

        eel.init("./src")
        eel.browsers.set_path('electron', _electron_path)
        eel.start({
            'port': 3000,
        }, options={
            'port': 8888,
            'host': 'localhost',
            'args': [_electron_path, '.'],
        }, suppress_error=True, size=(1000, 600), mode="electron")
    else:
        _electron_path = get_electron_bin()

        if not os.path.isfile(_electron_path):
            print('Warning: Electron not found in global packages\n'
                  'Trying to install through npm....')

            npm_out = fetch_npm_package('electron')
            if not len(npm_out):
                raise Exception(
                    "Something went wrong, couldn't install electron.")
            else:
                print(npm_out[:100] + '...')

        print(_electron_path)
        eel.init('build')
        eel.browsers.set_path('electron', _electron_path)
        eel.start('',
                  options={
                      'port': 8888,
                      'host': 'localhost',
                      'args': [_electron_path, '.'],
                  }, suppress_error=True, size=(1000, 600), mode="electron")


if __name__ == '__main__':
    init_ui()
