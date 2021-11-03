from distutils.dir_util import copy_tree
from functools import partial
from os import chdir as cd
from os import getcwd, path
from os.path import abspath, dirname, isfile, join
from shutil import rmtree
from threading import Thread

from setuptools import setup
from setuptools.command.install import install

from checkpoint import __version__ as version
from checkpoint.utils import execute_command

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]


def ui_build_wathcer(callback=None):
    """Watch for the UI build directory on a seperate thread.
    
    Parameters
    ----------
    callback : function
        Callback function to be called when the build directory is created.
    """
    print("UI build wathcer has started...")
    ui_executable = join(getcwd(), 'dist', 'ui.exe')
    is_built = isfile(ui_executable)

    if is_built:
        if callback:
            callback()
            return True

    while not is_built:
        is_built = isfile(ui_executable)
        if is_built:
            if callback:
                callback()
                return True


def merge_ui_build(main_package_path):
    """Merge the build/executable of UI with main package.

    Parameters
    ----------
    main_package_path : str
        Path to the main package.
    """
    print('Merging UI build with the main package...')
    build_dir = join(getcwd(), 'build')
    dist_dir = join(getcwd(), 'dist')
    executable_file_path = join(getcwd(), 'dist', 'ui.exe')
    copy_tree(build_dir, join(main_package_path, "build"))

    # copy(executable_file_path, dist_dir)
    print("Removing build artifacts...")
    rmtree(build_dir)
    rmtree(dist_dir)
    cd(main_package_path)
    print('UI built successfully.')


def custom_command():
    """Custom command to build `UI` after installation"""
    print('Building UI...')
    abs_path = abspath(dirname(__file__))
    ui_path = join(dirname(abspath(__file__)), 'checkpoint', 'ui')
    cd(ui_path)

    wathcer_thread = Thread(target=ui_build_wathcer, args=(
        partial(merge_ui_build, abs_path),))
    wathcer_thread.start()

    for line in execute_command('yarn build'):
        if 'python -m eel' in line:
            break

    wathcer_thread.join()


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        custom_command()


setup(
    name='pycheckpoint',
    version=version,
    description='Create restore points in your projects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/antrikshmisri/checkpoint',
    author='Antriksh Misri',
    author_email='antrikshmisri@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords=['checkpoint', 'cli', 'executable'],
    include_package_data=True,
    packages=['checkpoint'],
    install_requires=['cryptography==3.4.7',
                      'joblib==1.0.1',
                      'numpy==1.20.3',
                      'pytest==6.2.4'],
    entry_points={
        'console_scripts': [
            'checkpoint=checkpoint.__main__:run',
        ],
    },
    cmdclass={
        'install': CustomInstallCommand,
    },
)
