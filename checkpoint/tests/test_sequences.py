import numpy.testing as npt

from checkpoint.sequences import Sequence


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

    class SequenceMemeberMethods(Sequence):
        def __init__(self, sequence_name="Sequence_With_Member_Methods",
                     order_dict={'seq_test_method': 100}):
            super(SequenceMemeberMethods, self).__init__(sequence_name, order_dict)
        
        def seq_test_method(self):
            return f"Memeber function of {self.name}"
    
    sequence_with_member_methods = SequenceMemeberMethods()
    npt.assert_equal(sequence_with_member_methods.sequence_dict[100],
                     sequence_with_member_methods.seq_test_method)