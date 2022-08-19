import imp
from rich import print as rich_print

from checkpoint.utils import Logger

__logger__ = Logger()
__builtins__['print'] = rich_print
__version__ = '1.3'
