from os import path, listdir

from setuptools import setup

from checkpoint import __version__ as version

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


def get_requirements():
    _requirements_dir = path.join(this_directory, 'requirements')
    _requirements = []

    for _requirement_file in listdir(_requirements_dir):
        if _requirement_file.endswith('.txt'):
            with open(path.join(_requirements_dir, _requirement_file), 'r') as f:
                for _req in *f.read().splitlines(), :
                    _requirements.append(_req)

    return _requirements


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
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'checkpoint=checkpoint.__main__:run',
        ],
    },
)
