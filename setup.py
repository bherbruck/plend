from setuptools import setup, find_packages
from plend import constants


setup(name='plend',
      version=constants.VERSION,
      desctiption='Least Cost Formulation with Python',
      auhor=constants.AUTHOR,
      author_email=constants.EMAIL,
      license='MIT',
      url='https://github.com/bherbruck/plend',
      install_requires=['PuLP==2.0'],
      packages=['plend', 'plend.presets'],
      python_requires='>=3.6')
