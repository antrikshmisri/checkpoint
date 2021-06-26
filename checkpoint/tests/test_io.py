from checkpoint import io
from tempfile import TemporaryDirectory as InTemporaryDirectory
from os.path import join as pjoin
import os
import numpy.testing as npt
from shutil import rmtree

def test_io():

    with InTemporaryDirectory() as tdir:
        os.mkdir(pjoin(tdir, 'temp'))

        simple_io = io.IO(path=pjoin(tdir, 'temp'), mode='a')
        simple_io.path = tdir
        simple_io.mode = 's'

        npt.assert_equal(simple_io.path, tdir)
        npt.assert_equal(simple_io.mode, 's')
        rmtree(pjoin(tdir, 'temp'))  # Remove the temporary directory

        a_io = io.IO(path=tdir, mode='a')
        a_io.write(file=pjoin(tdir, 'temp.txt'), mode='x', content='Temporary File')
        content = a_io.read(file=pjoin(tdir, 'temp.txt'))

        npt.assert_equal(content, 'Temporary File')

        s_io = io.IO(path=tdir, mode='s')
        with npt.assert_raises(IOError):
            s_io.write(file=pjoin(tdir, 'temp.txt'), mode='w', content="Invalid Permission")

        with npt.assert_raises(IOError):
            _ = io.IO(path='invalid_path', mode='a')

        with npt.assert_raises(ValueError):
            _ = io.IO(path=tdir, mode='invalid_mode')
        
        with npt.assert_raises(ValueError):
            simple_io.mode_mapping = ['s', 'wb+', 'third_invalid_value']

        npt.assert_equal(simple_io.mode_mappings, simple_io.mode_mapping)

        simple_io.mode_mapping = ['s', 'wb+']
        npt.assert_equal('wb+' in simple_io.mode_mappings['s'], True)
