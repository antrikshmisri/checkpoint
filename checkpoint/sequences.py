from collections import OrderedDict
from types import MethodType


class Sequence:
    """Class to represent a sequence of operations."""
    def __init__(self, sequence_name):
        """Initialize the sequence class.

        Parameters
        ----------
        sequence_name: str
            Name of the sequence.
        """
        self.sequence_name = sequence_name
        self.sequence_dict = OrderedDict()
        self._sequence_functions = self.sequence_dict.items()

        # User hook that is triggered when the sequence has finished
        self.on_sequence_end = lambda seq: None

    def add_sequence_function(self, func, order=0):
        """Add a member function to the sequence.

        Parameters
        ----------
        func: method
            Function that is to be added to the sequence.
        order: int, optional
            The order of the function in the sequence
        """
        if not func.__name__.startswith('seq'):
            raise ValueError('Function name must start with "seq"')

        if order in self.sequence_dict:
            print(f'Warning: overriting {self.sequence_dict[order].__name__} with {func.__name__}')

        self.sequence_dict[order] = func
        self.update_order()

    def execute_sequence(self, execution_policy='decreasing_order'):
        """Execute all functions in the current sequence.

        Parameters
        ----------
        execution_policy: str
            The policy to be followed while executing the functions.
            Possible values are 'increasing_order' or 'decreasing_order'.
        """
        if execution_policy == 'decreasing_order':
            _sorted_sequence = sorted(self.sequence_dict.items(), reverse=True)
            for func_obj in _sorted_sequence:
                func_obj[1]()
            self.on_sequence_end(self) 
        elif execution_policy == 'increasing_order':
            for _, func in self.sequence_dict.items():
                func()
            self.on_sequence_end(self)
        else:
            raise ValueError(f'{execution_policy} is an invalid execution policy')

    def update_order(self):
        """Update the order of sequence functions in sequence dict."""
        self.sequence_dict = OrderedDict(sorted(self.sequence_dict.items()))

    @property
    def name(self):
        return self.sequence_name

    @property
    def sequence_functions(self):
        return self._sequence_functions

    @sequence_functions.setter
    def sequence_functions(self, functions):
        """Set the value of sequence functions to a list.

        Parameters
        ----------
        functions: list of methods
            List of methods that are to be assigned
        """
        self._sequence_functions = functions[:]


class CLISequence(Sequence):
    """Sequence for the CLI environment."""
    def __init__(self, sequence_name='CLI_Sequence', order_dict=None):
        """Initialize the CLISequence class.

        Parameters
        ----------
        sequence_name: str
            Name of the sequence.
        order_dict: dict
            Dictionary of the order of the functions in the sequence.
        """
        super(CLISequence, self).__init__(sequence_name=sequence_name)

        self.sequence_functions = []
        self.order_dict = order_dict or {}

        self.get_sequence_functions()

    def get_sequence_functions(self):
        """Get all the sequence functions."""
        for name in dir(self):
            if name.startswith('seq') and isinstance(getattr(self, name), MethodType):
                _func = getattr(self, name)
                if name not in self.order_dict:
                    self.order_dict[name] = len(self.sequence_functions)

                self.sequence_functions.append(_func)

        self.generate_sequence()

    def generate_sequence(self):
        """Generate a sequence from all memeber functions."""
        for func in self.sequence_functions:
            _name = func.__name__
            _order = self.order_dict[_name]
            self.add_sequence_function(func, _order)
