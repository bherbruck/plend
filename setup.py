from setuptools import setup, find_packages


setup(name='plend',
      version='0.1.3',
      desctiption='Python Feed Formulation',
      auhor='Brennen Herbruck',
      author_email='brennen.herbruck@gmail.com',
      license='MIT',
      url='https://github.com/bherbruck/plend',
      install_requires=['PuLP==2.0'],
      packages=['plend', 'plend.presets'],
      python_requires='>=3.6')
