#!/usr/bin/env python

"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup

setup(name='graphlib',
      version='1.2.0',
      description='Graph Processing Library',
      author='David Minor',
      author_email='dahvid.minor@gmail.com',
      url='https://www.python.org/sigs/distutils-sig/',
      packages=['graphlib'],
      python_requires='>=2.7',
      )
