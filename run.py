"""Script to run `python -m checkpoint` when `python run.py` is executed."""

from checkpoint import __main__ as checkpoint_main

checkpoint_main.__name__ = '__main__'
checkpoint_main.run()
