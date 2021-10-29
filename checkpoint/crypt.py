import os
from os.path import join as pjoin

from cryptography.fernet import Fernet

from checkpoint import io


def generate_key(name, path=os.getcwd()):
    """Generate a key to encrypt/decrypt files

    Parameters
    ----------
    name: str
        Name of the key, should end with .key extension
    path: str, optional
        Path where key isto be stored
    """
    if name.split('.')[-1] != 'key':
        raise ValueError('Key name should end with .key')

    key = Fernet.generate_key()
    key_path = pjoin(path, name)
    IO = io.IO(path)
    IO.write(key_path, 'wb+', key)

    return key


class Crypt:
    """Class to perform cryptographical operations"""

    def __init__(self, key, key_path=os.getcwd(), iterations=1):
        """Initialize the class

        Parameters
        ----------
        key: str
            Name of the key should end with .key extension
        key_path: str
            Path to the key
        iterations: int, optional
            Total iterations of encryption/decryption
        """
        self._io = io.IO(mode='m')
        self.key_path = key_path

        if not os.path.isfile(pjoin(key_path, key)):
            self.key = generate_key(key, self.key_path)
        else:
            self.key = self._io.read(pjoin(key_path, key), mode='rb')

        self.iterations = iterations
        self._fernet = Fernet(self.key)

    def encrypt(self, file, modify_file=False):
        """Encrypt a specific file

        Parameters
        ----------
        file: str
            Path to the file or content that isto be encrypted
        modify_file: bool, optional
            If True, the hash will be written in the target file
        """
        isfile = os.path.isfile(file)
        if isfile:
            content = self._io.read(file, mode='rb')
        else:
            content = file

        for _ in range(self.iterations):
            content = self._fernet.encrypt(content)

        if modify_file and isfile:
            self._io.write(file, 'wb', content)

        return content.decode('utf-8')

    def decrypt(self, file, modify_file=False):
        """Decrypt a specific file

        Parameters
        ----------
        file: str
            Path to the file or content that isto be decrypted
        modify_file: bool, optional
            If True, the hash will be written in the target file
        """
        isfile = os.path.isfile(file)
        if isfile:
            content = self._io.read(file, mode='rb')
        else:
            content = bytes(file, 'utf-8')

        for _ in range(self.iterations):
            content = self._fernet.decrypt(content)

        if modify_file and isfile:
            self._io.write(file, 'wb', content)

        return content
