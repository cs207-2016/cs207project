#!/usr/bin/env python3

from setuptools import setup

with open('README.md') as f:
    readme = f.read()
with open('LICENSE') as f:
    license = f.read()

setup(
    name='timeseries',
    version='0.1',
    packages=['timeseries'],
    author='Sophie Hilgard;Ryan Lapcevic;Anthony Soroka;Yamini Bansal; Ariel Herbert-Voss',
    author_email='rlapcevic@g.harvard.edu',
    url='',  
    license=license,
    description='A library for manipulating time series.',
    long_description=readme
)

