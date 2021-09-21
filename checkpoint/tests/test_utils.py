import pytest
import json
from os.path import join as pjoin
import numpy.testing as npt

from tempfile import TemporaryDirectory as InTemporaryDirectory

from checkpoint import utils
from checkpoint.io import IO


@pytest.fixture
def file_path(request):
    return str(request.node.fspath)


def test_logger(capsys, file_path):

    with InTemporaryDirectory() as tdir:
        log_file_path = pjoin(tdir, 'logs.log')
        log_message = 'This is a test message'
        log_color = '\033[92m'

        terminal_loger = utils.Logger(log_mode='t')
        file_logger = utils.Logger(file_path=log_file_path, log_mode='f')

        terminal_loger.log(msg=log_message, color=log_color)
        captured_stdout = capsys.readouterr()
        npt.assert_equal(log_message in captured_stdout.out, True)

        io = IO(path=tdir, mode='s')

        file_logger.log(msg=log_message, log_caller=True)
        message = f'[{file_path}, ]: {log_message} \n'
        logged_message = io.read(pjoin(tdir, log_file_path))
        npt.assert_equal(logged_message, message)

        io.mode = 'a'
        io.open(pjoin(tdir, log_file_path), 'w').close()

        file_logger.log(msg=log_message, as_obj=True, log_caller=True)
        message = json.dumps({file_path: log_message})
        message += '\n'
        logged_message = io.read(pjoin(tdir, log_file_path))
        npt.assert_equal(logged_message, message)
