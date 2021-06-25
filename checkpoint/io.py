from os.path import join as pjoin
from os.path import isdir
import os


class IO:
    """Class to perform Input/Output opreations.

    Provides methods to perform various IO operations
    in the target directory.

    Attributes
    ----------
    path: str
        Path to the target directory
    mode: str
        Mode of operations, valid values are
        `a`: IO has all permissions (R/W/X/A)
        `m`: IO has moderate permissions (R/W/A)
        `s`: IO has limited permissions (R/A)
    """

    def __init__(self, path=os.getcwd(), mode="a", ignore_dirs=[]):
        """Initialize the IO class.

        Parameters
        ----------
        path: str, optional
            Path to perform operations on
        mode: str, optional
            Mode of operations, valid values are
            `a`: IO has all permissions (R/W/X/A)
            `m`: IO has moderate permissions (R/W/A)
            `s`: IO has limited permissions (R/A)
        ignore_dirs: list
            List of directories to ignore
        """
        self._path = str()
        self._mode = str()
        self.ignore_dirs = ignore_dirs
        self.files = []
        self.sub_dirs = []

        self.path = path
        self.mode = mode

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

        self.update_paths(self._path)

    def update_paths(self, path):
        """Update the paths of files, sub_dirs w.r.t the path.

        Parameters
        ----------
        path: str
            Path to the target directory
        """
        self.files.clear()
        self.sub_dirs.clear()

        for path, subdirs, files in os.walk(path):
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
        """Write some content into a file.

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

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        """Set the value of the current path.

        Parameters
        ----------
        path: str
            New path
        """
        self._path = path
        self.update_paths(self._path)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Set the value of the IO mode.

        Parameters
        ----------
        mode: str
            Mode of operations, valid values are
            `a`: IO has all permissions (R/W/X/A)
            `m`: IO has moderate permissions (R/W/A)
            `s`: IO has limited permissions (R/A)
        """
        self._mode = mode

        if self._mode not in [*'ams']:
            raise ValueError(
                f'{self._mode} is not a valid IO operation mode'
            )
