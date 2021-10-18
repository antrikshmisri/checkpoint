"""Module that provides readers for different file extensions."""
import os
import sys
from inspect import getmembers
import abc
from multiprocessing import cpu_count
from tempfile import TemporaryDirectory as InTemporaryDirectory
from checkpoint.io import IO


def get_all_readers():
    """Get all the readers from the module."""
    readers = []
    for _, name in getmembers(sys.modules[__name__]):
        if isinstance(name, abc.ABCMeta) and name.__name__ != 'Reader':
            readers.append(name)

    return readers


class Reader(metaclass=abc.ABCMeta):
    """Umbrella for all reader classes."""
    def __init__(self, valid_extensions=None):
        """Initialize the Reader class.

        Parameters
        ----------
        valid_extensions: list
            List of valid extensions for the reader
        """
        self._io = IO()
        self.valid_extensions = valid_extensions or []
        self.num_cores = cpu_count()

    @abc.abstractmethod
    def _read(self, file_path):
        """Read the content of the file.

        Parameters
        ----------
        file_path: str
            Path to the file that is to be read

        Returns
        -------
        content: str
            Content of the file
        """
        msg = "This method must be implemented by the child class."
        raise NotImplementedError(msg)

    @abc.abstractmethod
    def _validate_extensions(self, extensions):
        """Validate if the additional extensions are valid.

        Parameters
        ----------
        extensions: list
            List of extensions to be validated

        Returns
        -------
        invalid_idxs: list
            List of indices of invalid extensions
        """
        msg = "This method must be implemented by the child class."
        raise NotImplementedError(msg)

    def read(self, files):
        """Read the content of the file.

        Parameters
        ----------
        files: list
            List of files to be read

        Returns
        -------
        content: list
            Content of the file/files
        """
        # TODO: Add parallelization
        contents = []

        if not isinstance(files, list):
            files = [files]

        for file in files:
            _ext = self._io.get_file_extension(file)
            if _ext not in self.valid_extensions:
                raise ValueError(f"Invalid file extension: {_ext}")

        for file in files:
            contents.append(self._read(file))

        return contents

    def validate_extensions(self, extensions):
        """Validate if the additional extensions are valid.

        Parameters
        ----------
        extensions: list
            List of extensions to be validated

        Returns
        -------
        invalid_idxs: list
            List of indices of invalid extensions
        """
        return self._validate_extensions(extensions)


class TextReader(Reader):
    """Class to read text files."""
    def __init__(self, additional_extensions=None):
        """Initilaize the TextReader class.

        Parameters
        ----------
        additional_extensions: list
            List of additional extensions that are valid for the reader
        """
        self.additional_extensions = additional_extensions or []
        super(TextReader, self).__init__(['txt', 'md', 'rst', 'py',
                                          'html', 'css', 'js', 'json',
                                          'txt'])

        self.validate_extensions(self.additional_extensions)
        self.valid_extensions.extend(self.additional_extensions)

    def _read(self, file_path):
        """Read the content of the file.

        Parameters
        ----------
        file_path: str
            Path to the file that is to be read

        Returns
        -------
        content: dict
            Dictionary containing the content of the file
        """

        return {file_path: self._io.read(file_path, mode='r')}

    def _validate_extensions(self, extensions):
        """Validate if the extensions work with the current reader.

        Parameters
        ----------
        extensions: list
            List of extensions to be validated
        """
        invalid_idxs = []

        with InTemporaryDirectory() as tdir:
            for ext in extensions:
                temp_file = os.path.join(tdir, f'test.{ext}')
                with open(temp_file, 'w+') as f:
                    f.write('test')

                try:
                    self._read(temp_file)
                except UnicodeDecodeError:
                    invalid_idxs.append(extensions.index(ext))

        for idx in invalid_idxs:
            extensions.pop(idx)
