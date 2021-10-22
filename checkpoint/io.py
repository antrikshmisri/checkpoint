import os
from os.path import isdir
from os.path import join as pjoin
from shutil import rmtree


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
        """Setup the IO class."""
        self.mode_mappings = {'a': [*'rwxa', 'wb+', 'w+', 'rb+'],
                              'm': [*'rwa', 'wb', 'rb'],
                              's': [*'ra', 'rb']}

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

    def walk_directory(self):
        """Walk through the root directory."""
        for root, _, files in os.walk(self.path):
            if all(dir not in root for dir in self.ignore_dirs):
                for file in files:
                    yield [root, file]

    def read(self, file, mode='r'):
        """Read the content of a file

        Parameters
        ----------
        file: str
            Name of the file
        mode: str, optional
            Mode of operation
        """
        if mode not in self.mode_mappings[self.mode]:
            raise IOError(
                f'Mode {mode} not allowed with IO mode {self.mode}'
            )
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

    def open(self, file, mode):
        """Open a file in a given mode.

        Parameters
        ----------
        file: str
            Name of the file
        mode: str
            Mode of operation
        """
        if mode not in self.mode_mappings[self.mode]:
            raise IOError(
                f'Mode {mode} not allowed with IO mode {self.mode}'
            )

        return open(file, mode)

    def get_file_extension(self, file_path):
        """Get the extension from the file.

        Parameters
        ----------
        file_path: str
            Path to the file
        """
        _file = os.path.basename(file_path)
        return _file.split('.')[-1].lower()

    def make_dir(self, dir_name):
        """Make a sub directory in the root directory.

        Parameters
        ----------
        dir_name: str
            Name of the sub directory
        """
        if dir_name in self.sub_dirs:
            raise IOError(
                f'{dir_name} already exists'
            )

        try:
            os.mkdir(pjoin(self.path, dir_name))
        except FileExistsError:
            rmtree(pjoin(self.path, dir_name))
            os.mkdir(pjoin(self.path, dir_name))

        return pjoin(self.path, dir_name)

    def delete_dir(self, dir_name):
        """Delete a sub directory in the root directory.

        Parameters
        ----------
        dir_name: str
            Name of the sub directory
        """

        if not os.path.isdir(pjoin(self.path, dir_name)):
            raise IOError(
                f'{dir_name} does not exist'
            )

        rmtree(pjoin(self.path, dir_name))

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

    @property
    def mode_mapping(self):
        return self.mode_mappings

    @mode_mapping.setter
    def mode_mapping(self, io_mode):
        """Add a IO permission to a specific mode

        Parameters
        ----------
        io_mode: Iterable
            Iterable that packs the mode, IO permission
            Valid values are
            `a`: IO has all permissions (R/W/X/A)
            `m`: IO has moderate permissions (R/W/A)
            `s`: IO has limited permissions (R/A)
        """
        if len(io_mode) != 2:
            raise ValueError(
                f'Iterable {io_mode} can have max two values packed'
            )

        mode, io_permission = io_mode
        self.mode_mappings[mode].append(io_permission)
