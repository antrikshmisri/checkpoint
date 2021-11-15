import os
from os.path import join as pjoin
from shutil import rmtree
from tempfile import TemporaryDirectory as InTemporaryDirectory

import numpy.testing as npt
from checkpoint import io


def test_io():

    with InTemporaryDirectory() as tdir:
        os.mkdir(pjoin(tdir, 'temp'))
        with npt.assert_raises(ValueError):
            _ = io.IO(path=pjoin(tdir, 'temp'), mode='invalid_mode')

        simple_io = io.IO(path=pjoin(tdir, 'temp'), mode='a')
        simple_io.path = tdir
        simple_io.mode = 's'
        npt.assert_equal(simple_io.files, [])
        npt.assert_equal(simple_io.sub_dirs, [])

        root_file = []
        for root, file in simple_io.walk_directory():
            root_file.append([root, file])

        npt.assert_equal(root_file, [])
        npt.assert_equal(simple_io.path, tdir)
        npt.assert_equal(simple_io.mode, 's')
        rmtree(pjoin(tdir, 'temp'))  # Remove the temporary directory

        a_io = io.IO(path=tdir, mode='a')
        a_io.write(file=pjoin(tdir, 'temp.txt'),
                   mode='x', content='Temporary File')

        a_io.update_paths(tdir)
        npt.assert_equal(a_io.files, [os.path.join(tdir, 'temp.txt')])
        npt.assert_equal(a_io.sub_dirs, [])

        ext = a_io.get_file_extension(pjoin(tdir, 'temp.txt'))
        npt.assert_equal(ext, 'txt')

        content = a_io.read(file=pjoin(tdir, 'temp.txt'))
        npt.assert_equal(content, 'Temporary File')
        file_path = pjoin(tdir, 'temp.txt')

        with npt.assert_raises(IOError):
            _ = a_io.open(file_path, mode='invalid mode')

        content = a_io.open(file_path, mode='r').read()
        npt.assert_equal(content, 'Temporary File')

        s_io = io.IO(path=tdir, mode='s')
        with npt.assert_raises(IOError):
            s_io.write(file=pjoin(tdir, 'temp.txt'),
                       mode='w', content="Invalid Permission")

        with npt.assert_raises(IOError):
            s_io.read(file=pjoin(tdir, 'temp.txt'), mode='w')

        with npt.assert_raises(IOError):
            _ = io.IO(path='invalid_path', mode='a')

        with npt.assert_raises(ValueError):
            _ = io.IO(path=tdir, mode='invalid_mode')

        with npt.assert_raises(ValueError):
            simple_io.mode_mapping = ['s', 'wb+', 'third_invalid_value']

        npt.assert_equal(simple_io.mode_mappings, simple_io.mode_mapping)

        simple_io.mode_mapping = ['s', 'wb+']
        npt.assert_equal('wb+' in simple_io.mode_mappings['s'], True)

        new_dir = simple_io.make_dir('test_dir')
        npt.assert_equal(os.path.isdir(new_dir), True)

        simple_io.delete_dir(new_dir)
        npt.assert_equal(os.path.isdir(new_dir), False)

        non_lazy_io = io.IO(path=tdir, mode='a', lazy=False)
        non_lazy_io.make_dir('test_dir')
        non_lazy_io.update_paths(tdir)

        npt.assert_equal(non_lazy_io.files, [os.path.join(tdir, 'temp.txt')])
        npt.assert_equal(non_lazy_io.sub_dirs, [
                         os.path.join(tdir, 'test_dir')])

        with npt.assert_raises(IOError):
            _ = non_lazy_io.make_dir('test_dir')

        _ = non_lazy_io.make_dir('test_dir_two')
        new_dir = non_lazy_io.make_dir('test_dir_two')

        npt.assert_equal(os.path.isdir(new_dir), True)
        npt.assert_equal(new_dir, pjoin(tdir, 'test_dir_two'))

        non_lazy_io.delete_dir(new_dir)

        with npt.assert_raises(IOError):
            non_lazy_io.delete_dir(new_dir)
