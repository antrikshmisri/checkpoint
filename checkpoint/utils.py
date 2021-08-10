"""Module that provides utility functions/classes."""
from os.path import isfile, dirname
from checkpoint.io import IO
from inspect import stack, getmodule

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
    def __init__(self, handler='logs.log', log_mode='t'):
        """Initialize the logger.
        
        Parameters
        ----------
        handler : str
            Path to the log file.
        mode : str
            Log mode, can take values `t` or `f`.
            `t`: log in terminal
            `f`: log in file
        """
        if not isfile(handler):
            self._io_mode = 'a'
        else:
            self._io_mode = 'm'
        
        self._handler = handler
        self._io = IO(path=dirname(self._handler), mode=self._io_mode)
        self.log_mode = log_mode
        self.log_colors = LogColors()
    
    def _log(self, msg, color=None):
        """Log a message.
        
        Parameters
        ----------
        msg : str
            Message to log.
        color : str
            Escape sequence of the color.
        """
        _callee = stack()[1]
        _mod = getmodule(_callee[0])
        msg = f'[{_mod}]: {msg} \n'

        if self.log_mode == 't':
            if color is None:
                print(msg)
            else:
                print(color + msg + LogColors.ENDC)
        elif self.log_mode == 'f':
            self._io.write(self._handler, 'a', msg)

