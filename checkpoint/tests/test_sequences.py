from argparse import ArgumentParser
from os.path import isdir, isfile
from os.path import join as pjoin
from shutil import rmtree
from tempfile import TemporaryDirectory as InTemporaryDirectory

import numpy.testing as npt
from checkpoint import __version__ as version
from checkpoint.crypt import Crypt
from checkpoint.io import IO
from checkpoint.sequences import (CheckpointSequence, CLISequence, IOSequence,
                                  Sequence)


def test_sequence():
    simple_sequence = Sequence(sequence_name='simple_sequence')
    npt.assert_equal(simple_sequence.name, 'simple_sequence')
    npt.assert_equal(repr(simple_sequence),
                     f'Name: {simple_sequence.name}, Member Function: {[]}')

    def invalid_sequence_function():
        return "Invalid function, doesn't start with 'seq'"

    with npt.assert_raises(ValueError):
        simple_sequence.add_sequence_function(invalid_sequence_function)

    def seq_test_sequence_function():
        return f"Memeber function of {simple_sequence.name}"

    simple_sequence.add_sequence_function(seq_test_sequence_function, order=0)
    npt.assert_equal(
        simple_sequence.sequence_dict[0], seq_test_sequence_function)

    with npt.assert_raises(ValueError):
        simple_sequence.execute_sequence(execution_policy="invalid")

    simple_sub_sequence = Sequence(sequence_name='simple_sub_sequence')

    def seq_test_sub_sequence_function():
        return f"Memeber function of {simple_sub_sequence.name}"

    simple_sub_sequence.add_sequence_function(seq_test_sub_sequence_function)
    simple_sequence.add_sub_sequence(simple_sub_sequence, order=1)

    with npt.assert_raises(TypeError):
        simple_sequence.add_sub_sequence(IO())

    npt.assert_equal(
        simple_sequence.sequence_dict[1], simple_sub_sequence.sequence_dict[0])

    return_vals = simple_sequence.execute_sequence(
        execution_policy="increasing_order")
    npt.assert_equal(return_vals, [f"Memeber function of {simple_sequence.name}",
                                   f"Memeber function of {simple_sub_sequence.name}"])

    return_vals = simple_sequence.execute_sequence()
    npt.assert_equal(return_vals, [f"Memeber function of {simple_sub_sequence.name}",
                                   f"Memeber function of {simple_sequence.name}"])

    simple_sequence.flush_sequence()
    npt.assert_equal(simple_sequence.sequence_dict, {})

    simple_sequence.sequence_functions = [seq_test_sequence_function]
    npt.assert_equal(simple_sequence.sequence_functions[0],
                     seq_test_sequence_function)

    order_dict = {'seq_test_method': 100}

    class SequenceMemeberMethods(Sequence):
        def __init__(self, sequence_name="Sequence_With_Member_Methods",
                     order_dict=order_dict):
            super(SequenceMemeberMethods, self).__init__(
                sequence_name, order_dict)

        def seq_test_method(self):
            return f"Memeber function of {self.name}"

    sequence_with_member_methods = SequenceMemeberMethods()
    npt.assert_equal(sequence_with_member_methods.sequence_dict[100],
                     sequence_with_member_methods.seq_test_method)


def test_io_sequence():
    with InTemporaryDirectory() as tdir:
        io = IO(path=tdir, mode='a')
        _checkpoint_sequernce = CheckpointSequence(sequence_name='checkpoint_sequence',
                                                   order_dict={
                                                       'seq_init_checkpoint': 0},
                                                   root_dir=tdir, ignore_dirs=list())

        _checkpoint_sequernce.seq_init_checkpoint()
        io.make_dir('text_files')
        io.make_dir('binary_files')
        # Writing into test files
        io.write(pjoin(io.path, 'text_files', 'test.txt'), 'w+', 'test')
        io.write(pjoin(io.path, 'text_files', 'test1.txt'), 'w+', 'test1')
        io.write(pjoin(io.path, 'binary_files', 'test.bin'), 'wb+', b'test')

        io_sequence = IOSequence(sequence_name='test_io_sequence',
                                 root_dir=io.path, ignore_dirs=['binary_files'])

        with npt.assert_raises(TypeError):
            io_sequence.execute_sequence()

        return_vals = io_sequence.execute_sequence(pass_args=True)
        text_path = pjoin(io.path, 'text_files')

        # Testing Walk Directory phase of sequence
        npt.assert_equal(return_vals[0], {pjoin(tdir, 'text_files'): [
                         pjoin(text_path, 'test.txt'), pjoin(text_path, 'test1.txt')]})

        # Testing Group files by extension phase of sequence
        npt.assert_equal(return_vals[1], {'txt': [pjoin(
            text_path, 'test.txt'), pjoin(text_path, 'test1.txt')]})

        # Testing Map Readers phase of sequence
        npt.assert_equal(return_vals[2][0]
                         ['txt'].__class__.__name__, 'TextReader')

        for obj in return_vals[2]:
            npt.assert_equal('bin' not in obj, True)

        npt.assert_equal(return_vals[2][1], return_vals[1])

        # Testing Read files phase of sequence
        npt.assert_equal(return_vals[3], [[{pjoin(text_path, 'test.txt'): 'test'}, {
                         pjoin(text_path, 'test1.txt'): 'test1'}]])

        # Testing Encryption phase of sequence
        crypt_obj = Crypt('crypt.key', pjoin(io.path, '.checkpoint'))
        dec_content = crypt_obj.decrypt(
            return_vals[4][pjoin(io.path, 'text_files', 'test.txt')])
        npt.assert_equal(dec_content.decode('utf-8'), 'test')


def test_checkpoint_sequence():
    order_dict = {
        'seq_init_checkpoint': 4,
        'seq_create_checkpoint': 3,
        'seq_delete_checkpoint': 2,
        'seq_restore_checkpoint': 1,
        'seq_version': 0,
    }
    with InTemporaryDirectory() as tdir:
        io = IO(path=tdir, mode='a')
        checkpoint_sequence = CheckpointSequence(sequence_name='checkpoint_sequence',
                                                 order_dict=order_dict,
                                                 root_dir=tdir, ignore_dirs=list(),)

        # Testing checkpoint initialization phase of sequence
        checkpoint_sequence.seq_init_checkpoint()
        npt.assert_equal(isdir(pjoin(tdir, '.checkpoint')), True)
        npt.assert_equal(isfile(pjoin(tdir, '.checkpoint', 'crypt.key')), True)

        io.write(pjoin(tdir, 'test.txt'), 'w+', 'test')
        io.write(pjoin(tdir, 'test1.txt'), 'w+', 'test1')

        # Testing checkpoint creation phase of sequence
        checkpoint_sequence.seq_create_checkpoint()
        checkpoint_path = pjoin(tdir, '.checkpoint',
                                checkpoint_sequence.sequence_name)

        npt.assert_equal(isdir(checkpoint_path), True)
        io.path = pjoin(tdir, '.checkpoint', checkpoint_sequence.sequence_name)

        checkpoint_files = [file for _, file in io.walk_directory()]
        npt.assert_equal(sorted(checkpoint_files), sorted([
                         '.metadata', f'{checkpoint_sequence.sequence_name}.json']))

        checkpoint_sequence_two = CheckpointSequence(sequence_name='checkpoint_sequence_two',
                                                     order_dict=order_dict,
                                                     root_dir=tdir, ignore_dirs=list())
        io.path = tdir
        io.write(pjoin(tdir, 'test.txt'), 'a', 'added text')
        io.write(pjoin(tdir, 'test1.txt'), 'a', 'added text')
        checkpoint_sequence_two.seq_create_checkpoint()

        # Testing checkpoint restoration phase of sequence
        checkpoint_sequence.seq_restore_checkpoint()
        contents = [io.read(pjoin(root, file), 'r') for root,
                    file in io.walk_directory() if '.checkpoint' not in root]

        npt.assert_equal(contents, ['test', 'test1'])

        checkpoint_sequence.seq_delete_checkpoint()
        npt.assert_equal(isdir(checkpoint_path), False)

        checkpoint_sequence.seq_version()
        with open('logs.log', 'r') as f:
            logs = f.read()
            npt.assert_equal(version in logs, True)

        checkpoint_duplicate = CheckpointSequence(sequence_name='checkpoint_sequence_two',
                                                  order_dict=order_dict,
                                                  root_dir=tdir, ignore_dirs=list())

        with npt.assert_raises(ValueError):
            checkpoint_duplicate.seq_create_checkpoint()

        io.write('logs.log', 'w', '')


def test_CLI_sequence():
    # TODO: Add a recording option to test CLI sequence based on a recording file
    with InTemporaryDirectory() as tdir:
        io = IO(path=tdir, mode='a', ignore_dirs=['.checkpoint'])

        all_args = {'init': ['-p', tdir, '-a', 'init'],
                    'create': ['-n', 'restore_point', '-p', tdir, '-a', 'create'],
                    'restore': ['-n', 'restore_point', '-p', tdir, '-a', 'restore'],
                    'delete': ['-n', 'restore_point', '-p', tdir, '-a', 'delete'],
                    'invalid_action': ['-n', 'restore_point', '-p', tdir, '-a', 'invalid_action']}

        arg_parser = ArgumentParser(
            description='Test CLI sequence',
        )
        arg_parser.add_argument(
            "-n",
            "--name",
            type=str,
            help="Name of the restore point.",
            default='restore_point',
        )

        arg_parser.add_argument(
            "-p",
            "--path",
            type=str,
            help="Path to the project.",
            default=tdir,
        )

        arg_parser.add_argument(
            "-a",
            "--action",
            type=str,
            help="Action to perform.",
            default='init',
        )

        arg_parser.add_argument(
            "--ignore-dirs",
            "-i",
            nargs="+",
            default=[".git", ".idea", ".vscode",
                     ".venv", "node_modules", "__pycache__"],
            help="Ignore directories."
        )

        for action, args in all_args.items():
            print(action, args)
            if action == 'init':
                cli_sequence = CLISequence(
                    arg_parser=arg_parser, args=args, terminal_log=True)
                cli_sequence.execute_sequence(pass_args=True)

                npt.assert_equal(isdir(pjoin(tdir, '.checkpoint')), True)
                npt.assert_equal(
                    isfile(pjoin(tdir, '.checkpoint', 'crypt.key')), True)
            elif action == 'create':
                io.write(pjoin(tdir, 'test.txt'), 'w+', 'test')
                io.write(pjoin(tdir, 'test1.txt'), 'w+', 'test1')

                cli_sequence = CLISequence(arg_parser=arg_parser, args=args)
                cli_sequence.execute_sequence(pass_args=True)

                checkpoint_path = pjoin(tdir, '.checkpoint',
                                        args[1])

                npt.assert_equal(isdir(checkpoint_path), True)
            elif action == 'restore':
                io.write(pjoin(tdir, 'test.txt'), 'w+', 'test changed')
                io.write(pjoin(tdir, 'test1.txt'), 'w+', 'test1 changed')

                cli_sequence = CLISequence(arg_parser=arg_parser, args=args)
                cli_sequence.execute_sequence(pass_args=True)

                contents = [io.read(pjoin(root, file), 'r')
                            for root, file in io.walk_directory()]

                npt.assert_equal(contents, ['test', 'test1'])
            elif action == 'delete':
                cli_sequence = CLISequence(arg_parser=arg_parser, args=args)
                cli_sequence.execute_sequence(pass_args=True)

                checkpoint_path = pjoin(tdir, '.checkpoint', args[1])
                npt.assert_equal(isdir(checkpoint_path), False)
            elif action == 'invalid_action':
                cli_sequence = CLISequence(arg_parser=arg_parser, args=args)
                with npt.assert_raises(ValueError):
                    cli_sequence.execute_sequence(pass_args=True)
