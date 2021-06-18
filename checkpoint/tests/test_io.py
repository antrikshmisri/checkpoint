from os import path
from checkpoint import io
from tempfile import TemporaryDirectory as InTemporaryDirectory
from os.path import join as pjoin
import os
import numpy.testing as npt


def test_io():

    with InTemporaryDirectory() as tdir:

        a_io = io.IO(path=tdir, mode='a')
        a_io.write(file=pjoin(tdir, 'temp.txt'), mode='x', content='Temporary File')
        content = a_io.read(file=pjoin(tdir, 'temp.txt'))

        npt.assert_equal(content, 'Temporary File')

        s_io = io.IO(path=tdir, mode='s')
        with npt.assert_raises(IOError):
            s_io.write(file=pjoin(tdir, 'temp.txt'), mode='w', content="Invalid Permission")

        with npt.assert_raises(IOError):
            invalid_io = io.IO(path='invalid_path', mode='a')

        with npt.assert_raises(ValueError):
            invalid_io = io.IO(path=tdir, mode='invalid_mode')
