from setuptools import setup, find_packages
 # read the contents of your README file
from os import path

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
  name='checkpoint',
  version='0.0.1',
  description='Create safe verions for your projects',
  long_description=f"{long_description} \n\n {open('CHANGELOG.txt').read()}",
  long_description_content_type='text/markdown',
  url='https://github.com/antrikshmisri/checkpoint',  
  author='Antriksh Misri',
  author_email='antrikshmisri@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='checkpoint', 
  packages=find_packages(),
  install_requires=[''] 
)