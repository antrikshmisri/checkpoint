from os.path import join as pjoin
from tempfile import TemporaryDirectory as InTemporaryDirectory

import numpy as np
import numpy.testing as npt
from checkpoint import readers
from checkpoint.io import IO
from PIL import Image


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

        npt.assert_equal(core_reader.read(valid_file), ['test'])

        extensions = ['txt', 'log']
        npt.assert_equal(core_reader.validate_extensions(extensions), [])


def test_text_reader():
    simple_text_reader = readers.TextReader()

    with InTemporaryDirectory() as tdir:
        invalid_file = pjoin(tdir, 'invalid.extension')
        io = IO(tdir)
        io.write(invalid_file, 'w+', 'Test Content')

        with npt.assert_raises(ValueError):
            simple_text_reader.read(invalid_file)

        valid_file = pjoin(tdir, 'valid.txt')
        io.write(valid_file, 'w+', 'Test Content')

        npt.assert_equal(simple_text_reader.read(valid_file),
                         [{valid_file: 'Test Content'}])

        valid_extensions = ['txt', 'log']
        simple_text_reader.validate_extensions(valid_extensions)

        npt.assert_equal(valid_extensions, ['txt', 'log'])


def test_image_reader():
    image_reader = readers.ImageReader()

    with InTemporaryDirectory() as tdir:
        invalid_file = pjoin(tdir, 'invalid.ext')
        io = IO(tdir)
        io.write(invalid_file, 'w+', 'Invalid image data')

        with npt.assert_raises(ValueError):
            image_reader.read(invalid_file)
        
        test_size = (300, 300)
        img_data = np.zeros((*test_size, 3), dtype=np.uint8)
        valid_file = pjoin(tdir, 'valid.png')

        Image.fromarray(img_data).save(valid_file)
        npt.assert_equal(image_reader.read(valid_file)[0],
                        {valid_file: img_data.tobytes()})

        extensions = ['png', 'jpg', 'invalid']
        image_reader.validate_extensions(extensions)

        npt.assert_equal(extensions, ['png', 'jpg'])


def test_get_all_readers():
    all_readers = readers.get_all_readers()
    npt.assert_array_equal(set(all_readers), set(
        [readers.TextReader, readers.ImageReader]))
