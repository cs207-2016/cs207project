#!/usr/bin/env python3

from setuptools import setup

# Todo: fix
#with open('README.md') as f:
#    readme = f.read()
readme=''
#with open('LICENSE') as f:
#    license = f.read()
license=''

setup(
    name='rbtree',
    version='0.1',
    packages=['timeseries.rbtree'],
    author='Sophie Hilgard;Ryan Lapcevic;Anthony Soroka;Yamini Bansal; Ariel Herbet-Voss',
    author_email='rlapcevic@g.harvard.edu',
    url='',
    license=license,
    description='A library implementing a red-black tree',
    long_description=readme
)

setup(
    name='timeseries',
    version='0.1',
    packages=['timeseries.timeseries'],
    author='Sophie Hilgard;Ryan Lapcevic;Anthony Soroka;Yamini Bansal; Ariel Herbert-Voss',
    author_email='rlapcevic@g.harvard.edu',
    url='',  
    license=license,
    description='A library for manipulating time series.',
    long_description=readme
)

setup(
    name='storagemanager',
    version='0.1',
    packages=['timeseries.storagemanager'],
    author='Sophie Hilgard;Ryan Lapcevic;Anthony Soroka;Yamini Bansal; Ariel Herbet-Voss',
    author_email='rlapcevic@g.harvard.edu',
    url='',  
    license=license,
    description='A library for managing time series on disk',
    long_description=readme
)

