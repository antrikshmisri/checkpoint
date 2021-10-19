from setuptools import setup
# read the contents of your README file
from os import path

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
    }
)
