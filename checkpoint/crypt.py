from cryptography.fernet import Fernet
import os
from os.path import join as pjoin
from checkpoint import io


def generate_key(name, path=os.getcwd()):
    """Generate a key to encrypt/decrypt files

    Parameters
    ----------
    name: str
        Name of the key
    path: str, optional
        Path where key isto be stored
    """
    if len(name.split('.')) > 1:
        name = name.split('.')[0]

    key = Fernet.generate_key()
    key_path = pjoin(path, f'{name}.key')
    IO = io.IO(path)
    IO.write(key_path, 'wb+', key)

    return key


class Crypt:
    """Class to perform cryptographical operations
    """
    def __init__(self, key, iterations=1):
        """Initialize the class

        Parameters
        ----------
        key: str
            Key to enctrypt/decrypt file
        iterations: int, optional
            Total iterations of encryption/decryption
        """
        self.key = key
        self.iterations = iterations
        self._fernet = Fernet(key)

    def encrypt(self, file):
        """Encrypt a specific file

        Parameters
        ----------
        file: str
            Path to the file that isto be encrypted
        """
        _io = io.IO()
        content = _io.read(file, mode='rb+')
        for _ in range(self.iterations):
            content = self._fernet.encrypt(content)

        return content

    def decrypt(self, file):
        """Decrypt a specific file

        Parameters
        ----------
        file: str
            Path to the file that isto be decrypted
        """
        _io = io.IO()
        content = _io.read(file, mode='rb+')
        for _ in range(self.iterations):
            content = self._fernet.decrypt(content)

        return content
