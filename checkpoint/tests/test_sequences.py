from os.path import join as pjoin
import numpy.testing as npt
from tempfile import TemporaryDirectory as InTemporaryDirectory

from checkpoint.sequences import CheckpointSequence, Sequence, IOSequence
from checkpoint.io import IO


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
    npt.assert_equal(simple_sequence.sequence_dict[0], seq_test_sequence_function)

    with npt.assert_raises(ValueError):
        simple_sequence.execute_sequence(execution_policy="invalid")

    simple_sub_sequence = Sequence(sequence_name='simple_sub_sequence')

    def seq_test_sub_sequence_function():
        return f"Memeber function of {simple_sub_sequence.name}"

    simple_sub_sequence.add_sequence_function(seq_test_sub_sequence_function)
    simple_sequence.add_sub_sequence(simple_sub_sequence, order=1)

    npt.assert_equal(simple_sequence.sequence_dict[1], simple_sub_sequence.sequence_dict[0])

    return_vals = simple_sequence.execute_sequence(execution_policy="increasing_order")
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
            super(SequenceMemeberMethods, self).__init__(sequence_name, order_dict)

        def seq_test_method(self):
            return f"Memeber function of {self.name}"

    sequence_with_member_methods = SequenceMemeberMethods()
    npt.assert_equal(sequence_with_member_methods.sequence_dict[100],
                     sequence_with_member_methods.seq_test_method)


def test_io_sequence():
    # TODO: Test the encryption phase of the IO sequence
    with InTemporaryDirectory() as tdir:
        io = IO(path=tdir, mode='a')
        _checkpoint_sequernce = CheckpointSequence(sequence_name='checkpoint_sequence',
                                                    order_dict={'seq_init_checkpoint': 0}, root_dir=tdir,
                                                    ignore_dirs=list())

        _checkpoint_sequernce.seq_init_checkpoint()
        io.make_dir('text_files')
        io.make_dir('binary_files')
        # Writing into test files
        io.write(pjoin(io.path, 'text_files', 'test.txt'), 'w+', 'test')
        io.write(pjoin(io.path, 'text_files', 'test1.txt'), 'w+', 'test1')
        io.write(pjoin(io.path, 'binary_files', 'test.bin'), 'wb+', b'test')

        io_sequence = IOSequence(sequence_name='test_io_sequence',
                                 root_dir=io.path, ignore_dirs=['binary_files'])

        return_vals = io_sequence.execute_sequence(pass_args=True)
        text_path = pjoin(io.path, 'text_files')
        npt.assert_equal(return_vals[0], {pjoin(tdir, 'text_files'): [
                         pjoin(text_path, 'test.txt'), pjoin(text_path, 'test1.txt')]})

        npt.assert_equal(return_vals[1], {'txt': [pjoin(
            text_path, 'test.txt'), pjoin(text_path, 'test1.txt')]})

        npt.assert_equal(return_vals[2][0]['txt'].__class__.__name__, 'TextReader')
        npt.assert_equal(return_vals[2][1], return_vals[1])

        npt.assert_equal(return_vals[3], [[{pjoin(text_path, 'test.txt'): 'test'}, {
                         pjoin(text_path, 'test1.txt'): 'test1'}]])
