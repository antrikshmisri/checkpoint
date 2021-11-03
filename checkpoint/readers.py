"""Module that provides readers for different file extensions."""
import abc
import os
import sys
from inspect import getmembers
from multiprocessing import cpu_count
from tempfile import TemporaryDirectory as InTemporaryDirectory

import numpy as np
from PIL import Image

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

    def read(self, files, validate=True):
        """Read the content of the file.

        Parameters
        ----------
        files: list
            List of files to be read
        validate: bool
            Flag to validate the extensions

        Returns
        -------
        content: list
            Content of the file/files
        """
        # TODO: Add parallelization
        contents = []
        exts = []
        if not isinstance(files, list):
            files = [files]

        for file in files:
            ext = self._io.get_file_extension(file)
            exts.append(ext)

        invalid_idxs = self.validate_extensions(exts) or []

        for idx in invalid_idxs:
            files.pop(idx)

        for file in files:
            _ext = self._io.get_file_extension(file)
            if validate:
                if _ext not in self.valid_extensions:
                    raise ValueError(
                        f"Invalid file extension: {_ext} for reader {self.__class__.__name__}")

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

    def __init__(self):
        """Initilaize the TextReader class."""
        super(TextReader, self).__init__(['txt', 'md', 'rst', 'py',
                                          'html', 'css', 'js', 'json',
                                          'txt'])

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
                    try:
                        f.write('test')
                        self._read(temp_file)
                    except UnicodeDecodeError:
                        invalid_idxs.append(extensions.index(ext))

        return invalid_idxs


class ImageReader(Reader):
    """Class to read image files."""

    def __init__(self):
        """Initialize the `ImageReader` class"""
        super(ImageReader, self).__init__(['png', 'jpg', 'jpeg', 'gif',
                                           'bmp', 'tiff', 'tif'])

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
        img_arr = np.asarray(Image.open(file_path))
        return {file_path: img_arr.tostring()}

    def _validate_extensions(self, extensions):
        """Validate if the extensions work with the current reader.

        Parameters
        ----------
        extensions: list
            List of extensions to be validated
        """
        invalid_idxs = []
        test_dimensions = (300, 300)
        with InTemporaryDirectory() as tdir:
            for ext in extensions:
                img_arr = np.zeros((*test_dimensions, 3), dtype=np.uint8)
                temp_file = os.path.join(tdir, f'test.{ext}')
                try:
                    Image.fromarray(img_arr).save(temp_file)
                except ValueError:
                    invalid_idxs.append(extensions.index(ext))

        for idx in invalid_idxs:
            extensions.pop(idx)
