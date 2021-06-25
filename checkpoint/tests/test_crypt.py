from genericpath import isfile
from checkpoint import crypt, io
from os.path import join as pjoin
import os
import numpy.testing as npt
from tempfile import TemporaryDirectory as InTemporaryDirectory


def test_generate_key():
    
    with InTemporaryDirectory() as tdir:
        key_name = 'secret_key'
        key = crypt.generate_key(key_name, tdir)

        npt.assert_equal(isfile(pjoin(tdir, f'{key_name}.key')), True)
        
        with open(pjoin(tdir, f'{key_name}.key'), 'rb') as k:
            key_value = k.read()
            npt.assert_equal(key, key_value)
            k.close()


def test_crypt():
    
    with InTemporaryDirectory() as tdir:
        IO = io.IO(tdir)
        key_name = 'secret_key'
        key = crypt.generate_key(key_name, tdir)

        _crypt = crypt.Crypt(key, iterations=3)

        # Creating a temporary file and writing into it
        content = 'This is a random string for testing purposes'
        with open(pjoin(tdir, 'temp.txt'), 'w+') as f:
            f.write(content)
            f.close()
        
        temp_path = pjoin(tdir, 'temp.txt')
        encrypted = _crypt.encrypt(temp_path)
        IO.write(temp_path, 'wb+', encrypted)
        decrypted = _crypt.decrypt(temp_path)

        npt.assert_equal(decrypted, bytes(content, 'utf-8'))