import os
from collections import OrderedDict
from types import MethodType
from itertools import count

from multiprocessing import cpu_count
from joblib import Parallel, delayed

from checkpoint.utils import get_reader_by_extension
from checkpoint.io import IO
from checkpoint.crypt import Crypt


class Sequence:
    """Class to represent a sequence of operations."""
    def __init__(self, sequence_name, order_dict=None):
        """Initialize the sequence class.

        Parameters
        ----------
        sequence_name: str
            Name of the sequence.
        order_dict: dict, optional
            Dictionary of function names and their order in the sequence.
        """
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
        _member_functions = [_func.__name__ for _func in self.sequence_dict.values()]
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
            print(f'Warning: overriting {self.sequence_dict[order].__name__} with {func.__name__}')

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
                if pass_args:
                    if len(_return_values) > 0:
                        _return_value = func_obj[1](_return_values[-1])
                    else:
                        _return_value = func_obj[1]()
                else:
                    _return_value = func_obj[1]()

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
            raise ValueError(f'{execution_policy} is an invalid execution policy')

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
                directory2files[root] = []

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
                extension = base_file.split('.')[-1]

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
        for extension, _ in extensions_dict.items():
            _readers[extension] = get_reader_by_extension(extension)

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
            Parallel(self.num_cores)(delayed(readers_dict[ext].read)(files) for (ext, files) in
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
        _checkpoint_path = self.io.make_dir('.checkpoint')
        crypt_obj = Crypt(key='crypt.key', key_path=_checkpoint_path)

        for content in contents:
            path = list(content[0].items())[0][0]
            content[0][path] = crypt_obj.encrypt(path)
        
        return contents


class CLISequence(Sequence):
    """Sequence for the CLI environment."""
    def __init__(self, sequence_name='CLI_Sequence', order_dict=None):
        """Initialize the CLISequence class.

        Parameters
        ----------
        sequence_name: str
            Name of the sequence.
        order_dict: dict
            Dictionary of the order of the functions in the sequence.
        """
        super(CLISequence, self).__init__(sequence_name=sequence_name)
