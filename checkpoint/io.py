from os.path import join as pjoin
from os.path import isdir, isfile
import os


class IO:
    """ Class to perform Input/Output opreations
    """

    def __init__(self, path=os.getcwd(), mode="a", ignore_dirs=[]):
        """Initialize the IO class

        Parameters
        ----------
        path: str, optional
            Path to perform operations on
        mode: str, optional
            Mode of operations, valid values are
            `a`: IO has all permissions (R/W/D/A)
            `m`: IO has moderate permissions (R/W/A)
            `s`: IO has limited permissions (R/A)
        ignore_dirs: list
            List of directories to ignore
        """
        self.path = path
        self.mode = mode
        self.ignore_dirs = ignore_dirs
        self.files = []
        self.sub_dirs = []

        if not isdir(self.path):
            raise IOError(
                f'{self.path} is not a valid directory'
            )

        if self.mode not in ['a', 'm', 's']:
            raise ValueError(
                f'{self.mode} is not a valid IO operation mode'
            )

        self.setup()

    def setup(self):
        """Setup the IO class
        """
        self.mode_mappings = {'a': [*'rwxa', 'wb+', 'w+', 'rb+'],
                              'm': [*'rwa', 'wb', 'rb'],
                              's': [*'ra']}

        for path, subdirs, files in os.walk(self.path):
            if all(dir not in path for dir in self.ignore_dirs):

                for file, dir in zip(files, subdirs):
                    self.files.append(pjoin(path, file))
                    self.sub_dirs.append(pjoin(path, dir))

    def read(self, file, mode='r'):
        """Read the content of a file

        Parameters
        ----------
        file: str
            Name of the file
        mode: str, optional
            Mode of operation
        """
        with open(file, mode) as f:
            content = f.read()

        return content

    def write(self, file, mode, content):
        """ Write some content into a file

        Parameters
        ----------
        file: str
            Name of the file
        mode: str
            Mode of operation
        content: str
            Content to write in the file
        """
        if mode not in self.mode_mappings[self.mode]:
            raise IOError(
                f'Mode {mode} not allowed with IO mode {self.mode}'
            )

        with open(file, mode) as f:
            f.write(content)
