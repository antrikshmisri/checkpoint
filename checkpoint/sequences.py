import json
import os
from collections import OrderedDict
from itertools import count
from multiprocessing import cpu_count
from tempfile import TemporaryDirectory as InTemporaryDirectory
from types import MethodType

from joblib import Parallel, delayed

from checkpoint import __version__ as version
from checkpoint.crypt import Crypt, generate_key
from checkpoint.io import IO
from checkpoint.readers import get_all_readers
from checkpoint.utils import LogColors, Logger, get_reader_by_extension


class Sequence:
    """Class to represent a sequence of operations."""

    def __init__(self, sequence_name, order_dict=None, logger=None):
        """Initialize the sequence class.

        Parameters
        ----------
        sequence_name: str
            Name of the sequence.
        order_dict: dict, optional
            Dictionary of function names and their order in the sequence.
        logger: `checkpoint.utils.Logger`, optional
            Logger for the sequence class
        """
        self.logger = logger or Logger()
        self.sequence_name = sequence_name
        self.sequence_dict = OrderedDict()
        self.order_dict = order_dict or {}

        self._sequence_functions = self.sequence_dict.items()
        self.sequence_functions = []

        self.get_sequence_functions()

        # User hook that is triggered when the sequence has finished
        self.on_sequence_end = lambda seq: None

    def __repr__(self):
        """Return the string representation of the Sequence."""
        _member_functions = [
            _func.__name__ for _func in self.sequence_dict.values()]
        return f'Name: {self.name}, Member Function: {_member_functions}'

    def add_sequence_function(self, func, order=0):
        """Add a member function to the sequence.

        Parameters
        ----------
        func: method
            Function that is to be added to the sequence.
        order: int, optional
            The order of the function in the sequence
        """
        if not func.__name__.startswith('seq'):
            raise ValueError('Function name must start with "seq"')

        if order in self.sequence_dict:
            _msg = f'Warning: overriting {self.sequence_dict[order].__name__} with {func.__name__}'
            self.logger.log(
                _msg, LogColors.WARNING, timestamp=True, log_caller=True)

        self.sequence_dict[order] = func

    def add_sub_sequence(self, sequence, order=0):
        """Add a sub sequence to the current sequence.

        Parameter
        ---------
        sequence: :class: `Sequence`
            The sub sequence that is to be added
        order: int, optional
            The order of the sub sequence in the sequence
        """
        if not isinstance(sequence, Sequence):
            raise TypeError('Sub sequence must be of type Sequence')

        _iterator = (count(start=order, step=1))
        for func_obj in sequence.sequence_dict.items():
            self.add_sequence_function(func_obj[1], order=next(_iterator))

    def execute_sequence(self, execution_policy='decreasing_order', pass_args=False):
        """Execute all functions in the current sequence.

        Parameters
        ----------
        execution_policy: str
            The policy to be followed while executing the functions.
            Possible values are 'increasing_order' or 'decreasing_order'.
        pass_args: bool
            If True, the arguments of the executed function will be passed to the next function.
        """
        self.update_order()
        _return_values = []

        if execution_policy == 'decreasing_order':
            _sorted_sequence = sorted(self.sequence_dict.items(), reverse=True)
            for func_obj in _sorted_sequence:
                context_text = func_obj[1].__name__.split(
                    'seq_')[-1].replace('_', ' ').title()

                try:
                    if pass_args:
                        if len(_return_values) > 0:
                            _return_value = func_obj[1](_return_values[-1])
                        else:
                            _return_value = func_obj[1]()
                    else:
                        _return_value = func_obj[1]()
                except Exception as e:
                    _msg = f'{context_text} ❌'
                    self.logger.log(
                        _msg, [LogColors.ERROR, LogColors.UNDERLINE], timestamp=True)
                    raise type(e)(f'{context_text} failed with error: {e}')

                _msg = f'{context_text} ✔️'
                self.logger.log(
                    _msg, [LogColors.SUCCESS, LogColors.UNDERLINE], timestamp=True)
                _return_values.append(_return_value)
            self.on_sequence_end(self)

        elif execution_policy == 'increasing_order':
            for _, func in self.sequence_dict.items():
                if pass_args:
                    _return_value = func(_return_values[-1])
                else:
                    _return_value = func()

                _return_values.append(_return_value)

            self.on_sequence_end(self)
        else:
            raise ValueError(
                f'{execution_policy} is an invalid execution policy')
        return _return_values

    def update_order(self):
        """Update the order of sequence functions in sequence dict."""
        self.sequence_dict = OrderedDict(sorted(self.sequence_dict.items()))

    def flush_sequence(self):
        """Flush the sequence."""
        self.sequence_dict.clear()

    def get_sequence_functions(self):
        """Get all the sequence functions."""
        self.sequence_functions.clear()

        for name in dir(self):
            if name.startswith('seq') and isinstance(getattr(self, name), MethodType):
                _func = getattr(self, name)
                if name not in self.order_dict:
                    self.order_dict[name] = len(self.sequence_functions)

                self.sequence_functions.append(_func)

        self.generate_sequence()

    def generate_sequence(self):
        """Generate a sequence from all memeber functions."""
        for func in self.sequence_functions:
            _name = func.__name__
            _order = self.order_dict[_name]
            self.add_sequence_function(func, _order)

    @property
    def name(self):
        return self.sequence_name

    @property
    def sequence_functions(self):
        return self._sequence_functions

    @sequence_functions.setter
    def sequence_functions(self, functions):
        """Set the value of sequence functions to a list.

        Parameters
        ----------
        functions: list of methods
            List of methods that are to be assigned
        """
        self._sequence_functions = functions[:]


class IOSequence(Sequence):
    """Class to represent a sequence of IO operations."""

    def __init__(self, sequence_name='IO_Sequence', order_dict=None,
                 root_dir=None, ignore_dirs=None, num_cores=None):
        """Initialize the IO sequence class.

        Default execution sequence is:
        1. Walk through the root directory
        2. Group files by extension
        3. Map readers based on extension
        4. Read files
        5. Encrypt the files

        Parameters
        ----------
        sequence_name: str
            Name of the sequence.
        order_dict: dict, optional
            Dictionary of function names and their order in the sequence.
        root_dir: str, optional
            The root directory.
        ignore_dirs: list of str, optional
            List of directories to be ignored.
        num_cores: int, optional
            Number of cores to be used for parallel processing.
        """
        self.default_order_dict = {
            'seq_walk_directories': 4,
            'seq_group_files': 3,
            'seq_map_readers': 2,
            'seq_read_files': 1,
            'seq_encrypt_files': 0,
        }

        super(IOSequence, self).__init__(sequence_name,
                                         order_dict or self.default_order_dict)

        self.root_dir = root_dir or os.getcwd()
        self.ignore_dirs = ignore_dirs or []
        self.ignore_dirs.append('.checkpoint')
        self.io = IO(self.root_dir, ignore_dirs=self.ignore_dirs)
        self.num_cores = num_cores or cpu_count()

    def seq_walk_directories(self):
        """Walk through all directories in the root directory.

        Parameters
        ----------
        root_directory: str
            The root directory to be walked through.
        """
        directory2files = {}
        for root, file in self.io.walk_directory():
            if root in directory2files:
                directory2files[root].append(os.path.join(root, file))
            else:
                directory2files[root] = [os.path.join(root, file)]

        return directory2files

    def seq_group_files(self, directory2files):
        """Group files in the same directory.

        Parameters
        ----------
        directory2files: dict
            Dictionary of directory names and their files.
        """
        extensions_dict = {}

        for files in directory2files.items():
            for file in files[1]:
                base_file = os.path.basename(file)
                extension = base_file.split('.')[-1].lower()

                if extension not in extensions_dict:
                    extensions_dict[extension] = [file]
                else:
                    extensions_dict[extension].append(file)

        return extensions_dict

    def seq_map_readers(self, extensions_dict):
        """Map the extensions to their respective Readers.

        Parameters
        ----------
        extensions_dict: dict
            Dictionary of extensions and their files.

        Returns
        -------
        dict
            Dictionary of extensions and their Readers.
        """
        _readers = {}
        unavailabe_extensions = []
        for extension, _ in extensions_dict.items():
            _readers[extension] = get_reader_by_extension(extension)
            if not _readers[extension]:
                all_readers = get_all_readers()
                with InTemporaryDirectory() as temp_dir:
                    temp_file = os.path.join(temp_dir, f'temp.{extension}')
                    self.io.write(temp_file, 'w+', 'test content')
                    selected_reader = None
                    for reader in all_readers:
                        try:
                            _msg = f'Trying {reader.__name__} for extension {extension}'
                            self.logger.log(
                                _msg, colors=LogColors.BOLD, log_caller=True)
                            reader = reader()
                            reader.read(temp_file, validate=False)
                            selected_reader = reader
                        except Exception:
                            selected_reader = None
                            continue

                    if selected_reader:
                        _msg = f'{selected_reader.__class__.__name__} selected'
                        self.logger.log(
                            _msg, colors=LogColors.SUCCESS, timestamp=True)
                        _readers[extension] = selected_reader
                    else:
                        unavailabe_extensions.append(extension)
                        del _readers[extension]
                        self.logger.log(
                            f'No reader found for extension {extension}, skipping',
                            colors=LogColors.ERROR, log_caller=True)

        for extension in unavailabe_extensions:
            del extensions_dict[extension]

        return [_readers, extensions_dict]

    def seq_read_files(self, readers_extension):
        """Read the gathered files using their respective reader.

        Parameters
        ----------
        readers_extension: list
            Readers dict and extensions dict packed in a list.

        Returns
        -------
        dict
            Dictionary of files and their content.
        """
        readers_dict, extension_dict = readers_extension

        contents = \
            Parallel(self.num_cores)(delayed(readers_dict[ext].read)(files,
                                     validate=False) for (ext, files) in
                                     extension_dict.items())
        return contents

    def seq_encrypt_files(self, contents):
        """Encrypt the read files.

        Parameters
        ----------
        contents: dict
            Dictionary of file paths and their content.

        Returns
        -------
        dict
            Dictionary of file paths and their encrypted content.
        """
        # TODO: Parallelize this
        path2content = {}
        crypt_obj = Crypt(key='crypt.key', key_path=os.path.join(
            self.root_dir, '.checkpoint'))

        for content in contents:
            for obj in content:
                path = list(obj.keys())[0]
                path2content[path] = crypt_obj.encrypt(path)

        return path2content


class CheckpointSequence(Sequence):
    """Sequence to perform checkpoint operations."""

    def __init__(self, sequence_name, order_dict, root_dir, ignore_dirs):
        """Initialize the CheckpointSequence class.

        Parameters
        ----------
        sequence_name: str
            Name of the sequence.
        order_dict: dict
            Dictionary of function names and their order in the sequence.
        root_dir: str
            The root directory.
        ignore_dirs: list of str
            List of directories to be ignored.
        """
        self.sequence_name = sequence_name
        self.order_dict = order_dict
        self.root_dir = root_dir
        self.ignore_dirs = ignore_dirs
        super(CheckpointSequence, self).__init__(sequence_name, order_dict)

    def seq_init_checkpoint(self):
        """Initialize the checkpoint directory."""
        self._io = IO(path=self.root_dir, mode="a",
                      ignore_dirs=self.ignore_dirs)
        path = self._io.make_dir('.checkpoint')
        generate_key('crypt.key', path)

    def seq_create_checkpoint(self):
        """Create a new checkpoint for the target directory."""
        if self.sequence_name in os.listdir(os.path.join(self.root_dir, '.checkpoint')):
            raise ValueError(
                f'Checkpoint with name {self.sequence_name} already exists')
        self._io = IO(path=self.root_dir, mode="a",
                      ignore_dirs=self.ignore_dirs)

        _io_sequence = IOSequence(root_dir=self.root_dir,
                                  ignore_dirs=self.ignore_dirs)

        enc_files = _io_sequence.execute_sequence(pass_args=True)[-1]

        checkpoint_path = os.path.join(
            self.root_dir, '.checkpoint', self.sequence_name)
        checkpoint_path = self._io.make_dir(checkpoint_path)
        checkpoint_file_path = os.path.join(
            checkpoint_path, f'{self.sequence_name}.json')

        with open(checkpoint_file_path, 'w+') as checkpoint_file:
            json.dump(enc_files, checkpoint_file, indent=4)

        root2file = {}
        for root, file in self._io.walk_directory():
            if root in root2file:
                root2file[root].append(os.path.join(root, file))
            else:
                root2file[root] = [os.path.join(root, file)]

        with open(os.path.join(checkpoint_path, '.metadata'), 'w+') as metadata_file:
            json.dump(root2file, metadata_file, indent=4)

    def seq_delete_checkpoint(self):
        """Delete the checkpoint for the target directory."""
        self._io = IO(path=self.root_dir, mode="a",
                      ignore_dirs=self.ignore_dirs)
        checkpoint_path = os.path.join(
            self.root_dir, '.checkpoint', self.sequence_name)
        self._io.delete_dir(checkpoint_path)

    def seq_restore_checkpoint(self):
        """Restore back to a specific checkpoint."""
        self._io = IO(path=self.root_dir, mode="a",
                      ignore_dirs=self.ignore_dirs)
        _key = os.path.join(self.root_dir, '.checkpoint')
        crypt = Crypt(key='crypt.key', key_path=_key)

        checkpoint_path = os.path.join(self.root_dir, '.checkpoint',
                                       self.sequence_name, f'{self.sequence_name}.json')

        with open(checkpoint_path, 'r') as checkpoint_file:
            checkpoint_dict = json.load(checkpoint_file)

        for file, content in checkpoint_dict.items():
            content = crypt.decrypt(content)
            self._io.write(file, 'wb+', content)

    def seq_version(self):
        """Print the version of the sequence."""
        _msg = f'Running version {version}'
        self.logger.log(_msg, timestamp=True)


class CLISequence(Sequence):
    """Sequence for the CLI environment."""

    def __init__(self, sequence_name='CLI_Sequence', order_dict=None,
                 arg_parser=None, args=None):
        """Initialize the CLISequence class.

        Default execution sequence is:

        1. Parse the arguments.
        2. Determine the action to perform from the arguments.
        3. Perform the action.

        Parameters
        ----------
        sequence_name: str
            Name of the sequence.
        order_dict: dict
            Dictionary of the order of the functions in the sequence.
        arg_parser: ArgumentParser
            Argument parser for the CLI.
        """
        self.default_order_dict = {
            'seq_parse_args': 2,
            'seq_determine_action': 1,
            'seq_perform_action': 0,
        }
        self.args = args
        self.arg_parser = arg_parser
        super(CLISequence, self).__init__(sequence_name=sequence_name,
                                          order_dict=order_dict or self.default_order_dict)

    def seq_parse_args(self):
        """Parse the arguments from the CLI."""
        if self.args is None:
            args = self.arg_parser.parse_args()
        else:
            args = self.arg_parser.parse_args(self.args)
        return args

    def seq_determine_action(self, args):
        """Determine the action to be performed.

        Parameters
        ----------
        args: ArgumentParser
            Parsed arguments from the CLI.
        """
        if args.action == 'create':
            action = 'seq_create_checkpoint'
        elif args.action == 'restore':
            action = 'seq_restore_checkpoint'
        elif args.action == 'delete':
            action = 'seq_delete_checkpoint'
        elif args.action == 'init':
            action = 'seq_init_checkpoint'
        elif args.action == 'version':
            action = 'seq_version'
        else:
            raise ValueError('Invalid action.')

        return [action, args]

    def seq_perform_action(self, action_args):
        """Perform the action.

        Parameters
        ----------
        action_args: list
            List containing action and args NameSpace.
        """
        action, args = action_args
        _name = args.name
        _path = args.path
        _ignore_dirs = args.ignore_dirs or []
        _helper_actions = ['seq_init_checkpoint', 'seq_version']

        if not (_name and _path) and action not in _helper_actions:
            raise ValueError(f'{args.action} requires a valid name and a path')

        order_dict = {action: 0}
        _checkpoint_sequence = CheckpointSequence(
            _name, order_dict, _path, _ignore_dirs)
        action_function = getattr(_checkpoint_sequence, action)
        action_function()
