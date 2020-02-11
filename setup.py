import os
import sys

from setuptools import setup, find_packages
from plend import __version__, __author__, __email__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(name='plend',
      version=__version__,
      desctiption='Python Feed Formulation',
      auhor=__author__,
      author_email=__email__,
      license='MIT',
      url='https://github.com/bherbruck/plend',
      install_requires=['PuLP==2.0'],
      packages=['plend', 'plend.presets'],
      python_requires='>=3.6')
