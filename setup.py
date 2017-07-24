from setuptools import setup
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='splutter',
    packages=['splutter'],
    version='0.1.0',
    description='A modern curses UI framework for Python.',
    author='John Carlyle',
    url='https://github.com/elegantbadger/splutter',
    long_description=long_description,
    keywords=['curses', 'terminal'],
    license='MIT',
    classifiers=[],
)
