import os

import eel
import eel.browsers

from .utils import fetch_npm_package, get_electron_bin


def init_ui():
    """Initialize the UI."""
    _electron_path = get_electron_bin()

    if not os.path.isfile(_electron_path):
        print('Warning: Electron not found in global packages\n'
              'Trying to install through npm....')

        npm_out = fetch_npm_package('electron')
        if not len(npm_out):
            raise Exception(
                "Something went wrong, couldn't install electron.")
        else:
            print(npm_out[:100] + '...')

    eel.init('src')
    eel.browsers.set_path('electron', _electron_path)
    eel.start('',
              options={
                  'port': 8888,
                  'host': 'localhost',
                  'args': [_electron_path, '.'],
              }, suppress_error=True, size=(1000, 600), mode="electron")


if __name__ == '__main__':
    init_ui()
