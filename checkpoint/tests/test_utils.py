import json
from os.path import join as pjoin
from sys import version
from tempfile import TemporaryDirectory as InTemporaryDirectory

import numpy.testing as npt
import pytest
from checkpoint import utils
from checkpoint.io import IO


@pytest.fixture
def file_path(request):
    return str(request.node.fspath)


def test_logger(capsys, file_path):
    file_path = file_path.replace("/", "\\")
    with InTemporaryDirectory() as tdir:
        log_file_path = pjoin(tdir, 'logs.log')
        log_message = 'This is a test message'
        log_color = utils.LogColors.SUCCESS

        terminal_loger = utils.Logger(log_mode='t')
        file_logger = utils.Logger(file_path=log_file_path, log_mode='f')

        terminal_loger.log(msg=log_message, colors=log_color)
        captured_stdout = capsys.readouterr()
        npt.assert_equal(log_message in captured_stdout.out, True)

        io = IO(path=tdir, mode='s')

        file_logger.log(msg=log_message, log_caller=True)
        message = f'[{file_path}, ]: {log_message} - INFO\n'
        logged_message = io.read(pjoin(tdir, log_file_path))
        npt.assert_equal(logged_message, message)

        io.mode = 'a'
        io.open(pjoin(tdir, log_file_path), 'w').close()

        file_logger.log(msg=log_message, as_obj=True, log_caller=True)
        message = json.dumps({file_path: log_message})
        message += '\n'
        logged_message = io.read(pjoin(tdir, log_file_path))
        npt.assert_equal(logged_message, message)


def test_get_reader_by_extension():
    extension = 'txt'
    invalid_extension = 'invalid'

    reader = utils.get_reader_by_extension(extension)
    invalid_reader = utils.get_reader_by_extension(invalid_extension)

    npt.assert_equal(reader.__class__.__name__, 'TextReader')
    npt.assert_equal(invalid_reader, None)


def test_execute_command():
    command = "python --version"
    for line in utils.execute_command(command):
        npt.assert_equal(line.startswith('Python'), True)
        python_version = line.split('Python ')[-1].split('\n')[0]
        npt.assert_equal(python_version, version.split(" ")[0].strip())
