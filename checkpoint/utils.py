"""Module that provides utility functions/classes."""
import json
from datetime import datetime
from inspect import getmodule, stack
from os import getcwd
from os.path import dirname, isfile

from checkpoint.io import IO
from checkpoint.readers import get_all_readers


class LogColors:
    """Provides colors for terminal logs."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Logger:
    """Provides logging utility functions."""

    def __init__(self, file_path='logs.log', log_mode='t'):
        """Initialize the logger.

        Parameters
        ----------
        file_path : str
            Path to the log file.
        log_mode : str
            Log mode, can take values `t` or `f`.
            `t`: log in terminal
            `f`: log in file
        """
        if not isfile(file_path):
            self._io_mode = 'a'
        else:
            self._io_mode = 'm'

        self._file_path = file_path
        self._log_dir_path = dirname(self._file_path)

        if not self._log_dir_path:
            self._log_dir_path = getcwd()

        self._io = IO(path=self._log_dir_path, mode=self._io_mode)
        self.log_mode = log_mode
        self.log_colors = LogColors()

    def log(self, msg, colors=None, as_obj=False, timestamp=False,
            log_caller=False):
        """Log a message.

        Parameters
        ----------
        msg : str
            Message to log.
        colors : list
            List of colors to use for the message.
        as_obj : bool
            If True, the message will be logged as an object.
        timestamp : bool
            If True, the current time will be added to the message.
        log_caller : bool
            If True, the current function name will be added to the message.
        """

        _caller = stack()[1]
        _file = getmodule(_caller[0]).__file__ * log_caller
        _timestamp = datetime.now().strftime('%H:%M:%S') * timestamp

        colors = colors or [self.log_colors.BOLD]
        if not isinstance(colors, list):
            colors = [colors]

        if as_obj:
            msg = {(_file, _timestamp): msg}
        else:
            msg = f'[{_file}, {_timestamp}]: {msg}'

        if self.log_mode == 't':
            print(f"{''.join(colors)}{msg}{self.log_colors.ENDC}")
        elif self.log_mode == 'f':
            if not as_obj:
                self._io.write(self._file_path, 'a', msg)
            else:
                with self._io.open(self._file_path, 'a') as f:
                    _msg_key = list(msg.keys())[0][0]
                    _msg_val = list(msg.values())[0]
                    _msg = {_msg_key: _msg_val}

                    json.dump(_msg, f)
                    f.write('\n')


def get_reader_by_extension(extension):
    """Get the reader by an extension.

    Parameters
    ----------
    extension : str
        Extension of the file.

    Returns
    -------
    reader: :class: `checkpoint.readers.Reader`
        Reader class.
    """
    readers = get_all_readers()

    for reader in readers:
        reader_obj = reader()
        if extension in reader_obj.valid_extensions:
            return reader_obj
    print(f'{LogColors.ERROR}No reader found for {extension}{LogColors.ENDC}')
