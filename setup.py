import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='plend',
    version='0.1.4',
    author='Brennen Herbruck',
    author_email='brennen.hrbruck@gmail.com',
    description='Least Cost Formulation with Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bherbruck/plend',
    packages=['plend', 'plend.presets'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
