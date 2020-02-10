from setuptools import setup, find_packages


version_dict = {}
exec(open('constants.py').read(), version_dict)
VERSION = version_dict['VERSION']

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='plend',
      version=VERSION,
      desctiption='Python Feed Formulation',
      auhor='Brennen Herbruck',
      author_email='brennen.herbruck@gmail.com',
      license='MIT',
      url='https://github.com/bherbruck/plend',
      install_requires=requirements,
      packages=['plend', 'plend.presets'],
      python_requires='>=3.6')
