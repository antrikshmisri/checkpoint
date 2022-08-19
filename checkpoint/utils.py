"""Module that provides utility functions/classes."""
import json
from datetime import datetime
from inspect import getmodule, stack
from os import getcwd
from os.path import dirname, isfile
from subprocess import PIPE, CalledProcessError, Popen

from checkpoint.io import IO
from checkpoint.readers import get_all_readers


class LogColors:
    """Provides colors for terminal logs."""
    HEADER = '[underline][bold]'
    BLUE = '[blue]'
    CYAN = '[cyan]'
    SUCCESS = '[green]'
    WARNING = '[yellow]'
    ERROR = '[red]'
    ENDC = '[/]'
    BOLD = '[bold]'
    UNDERLINE = '[underline]'


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
            log_caller=False, log_type="INFO"):
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
        log_type : str
            Type of log, can take values `INFO`, `WARNING`, `ERROR`, `SUCCESS`, etc.
        """

        _caller = stack()[1]
        _file = getmodule(_caller[0]).__file__.replace("/", "\\") * log_caller
        _timestamp = datetime.now().strftime('%H:%M:%S') * timestamp

        colors = colors or [self.log_colors.BOLD]
        if not isinstance(colors, list):
            colors = [colors]

        if as_obj:
            msg = {(_file, _timestamp): msg}
        else:
            msg = f'[{_file}, {_timestamp}]: {msg} - {log_type}'

        if self.log_mode == 't':
            print(f"{''.join(colors)}{msg}{self.log_colors.ENDC}")
        elif self.log_mode == 'f':
            if not as_obj:
                self._io.write(self._file_path, 'a', msg + '\n')
            else:
                with self._io.open(self._file_path, 'a') as f:
                    _msg_key = list(msg.keys())[0][0]
                    _msg_val = list(msg.values())[0]
                    _msg = {_msg_key: _msg_val}

                    json.dump(_msg, f)
                    f.write('\n')

    @property
    def log_mode(self):
        return self._log_mode

    @log_mode.setter
    def log_mode(self, log_mode):
        """Set the log mode.

        Parameters
        ----------
        log_mode: str
            Log mode, can take values `t` or `f`.
            `t`: log in terminal
            `f`: log in file
        """
        if log_mode not in ['t', 'f']:
            raise ValueError(f'Invalid log mode: {log_mode}')

        self._log_mode = log_mode


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
    print(f'{LogColors.ERROR}No default reader found for {extension}{LogColors.ENDC}')


def execute_command(command):
    """Execute a command and get continuous output.

    Parameters
    ----------
    command : str
        Command to execute.

    Yields
    ------
    line: str
        Output line.
    """
    popen = Popen(command, stdout=PIPE, stderr=PIPE,
                  shell=True, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line

    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise CalledProcessError(return_code, command)
