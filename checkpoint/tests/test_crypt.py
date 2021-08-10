from genericpath import isfile
from checkpoint import crypt, io
from os.path import join as pjoin
import numpy.testing as npt
from tempfile import TemporaryDirectory as InTemporaryDirectory


def test_generate_key():

    with InTemporaryDirectory() as tdir:
        key_name = 'secret_key.key'
        invalid_key = 'secret_key.txt'
        key = crypt.generate_key(key_name, tdir)

        with npt.assert_raises(ValueError):
            _ = crypt.generate_key(invalid_key, tdir)

        npt.assert_equal(isfile(pjoin(tdir, key_name)), True)

        with open(pjoin(tdir, key_name), 'rb') as k:
            key_value = k.read()
            npt.assert_equal(key, key_value)
            k.close()


def test_crypt():

    with InTemporaryDirectory() as tdir:
        key_name = 'secret_key.key'
        _ = crypt.generate_key(key_name, tdir)

        _crypt = crypt.Crypt(key_name, tdir, iterations=3)

        # Creating a temporary file and writing into it
        content = 'This is a random string for testing purposes'
        with open(pjoin(tdir, 'temp.txt'), 'w+') as f:
            f.write(content)
            f.close()

        temp_path = pjoin(tdir, 'temp.txt')
        _ = _crypt.encrypt(temp_path)
        decrypted = _crypt.decrypt(temp_path)

        npt.assert_equal(decrypted, bytes(content, 'utf-8'))