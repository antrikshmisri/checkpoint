import os
from os.path import join as pjoin
import numpy.testing as npt
from tempfile import TemporaryDirectory as InTemporaryDirectory

from checkpoint import readers
from checkpoint.io import IO


def test_reader():
    class SimpleReader(readers.Reader):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def _read(self, *args, **kwargs):
            return 'test'

        def _validate_extensions(self, *args, **kwargs):
            return []

    core_reader = SimpleReader(valid_extensions=['txt'])

    with InTemporaryDirectory() as tdir:
        io = IO(tdir)
        invalid_file = pjoin(tdir, 'invalid.extension')
        io.write(invalid_file, 'w+', 'Test Content')

        with npt.assert_raises(ValueError):
            core_reader.read(invalid_file)

        valid_file = pjoin(tdir, 'valid.txt')
        io.write(valid_file, 'w+', 'Test Content')

        npt.assert_equal(core_reader.read(valid_file), 'test')

        extensions = ['txt', 'log']
        npt.assert_equal(core_reader.validate_extensions(extensions), [])


def test_text_reader():
    simple_text_reader = readers.TextReader(additional_extensions=['json'])

    with InTemporaryDirectory() as tdir:
        invalid_file = pjoin(tdir, 'invalid.extension')
        io = IO(tdir)
        io.write(invalid_file, 'w+', 'Test Content')

        with npt.assert_raises(ValueError):
            simple_text_reader.read(invalid_file)

        valid_file = pjoin(tdir, 'valid.txt')
        io.write(valid_file, 'w+', 'Test Content')

        npt.assert_equal(simple_text_reader.read(valid_file), 'Test Content')

        valid_extensions = ['txt', 'log']
        simple_text_reader.validate_extensions(valid_extensions)

        npt.assert_equal(valid_extensions, ['txt', 'log'])
