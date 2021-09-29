"""Module that provides readers for different file extensions."""
import os
import abc
from tempfile import TemporaryDirectory as InTemporaryDirectory
from checkpoint.io import IO


class Reader(abc.ABC):
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
        is_valid: bool
            True if the extensions are valid, False otherwise
        """
        msg = "This method must be implemented by the child class."
        raise NotImplementedError(msg)

    def read(self, file_path):
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
        _ext = self._io.get_file_extension(file_path)

        if _ext not in self.valid_extensions:
            raise ValueError(f"Invalid file extension: {_ext}")
        else:
            return self._read(file_path)

    def validate_extensions(self, extensions):
        """Validate if the additional extensions are valid.

        Parameters
        ----------
        extensions: list
            List of extensions to be validated

        Returns
        -------
        is_valid: bool
            True if the extensions are valid, False otherwise
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
        self.valid_extensions = ['txt', 'md', 'rst', 'py',
                                 'html', 'css', 'js', 'json']

        self.additional_extensions = additional_extensions or []
        if self.validate_extensions(self.additional_extensions):
            self.valid_extensions.extend(self.additional_extensions)

        super(TextReader, self).__init__(self.valid_extensions)

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
        with open(file_path, 'r') as f:
            content = f.read()

        return content

    def _validate_extensions(self, extensions):
        """Validate if the extensions work with the current reader.

        Parameters
        ----------
        extensions: list
            List of extensions to be validated

        Returns
        -------
        valid: bool
            True if the extensions are valid, False otherwise
        """
        with InTemporaryDirectory() as tdir:
            for extension in extensions:
                file_name = f"file.{extension}"
                file_path = os.path.join(tdir, file_name)
                with open(file_path, 'w+') as f:
                    f.write("")

                try:
                    self._read(file_path)
                except Exception as e:
                    return False

        return True
