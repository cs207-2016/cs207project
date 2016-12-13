#!/usr/bin/env python3

from setuptools import setup

with open('README.md') as f:
    readme = f.read()
with open('LICENSE') as f:
    license = f.read()

setup(
    name='dbserver',
    version='1.0',
    packages=['dbserver'],
    author='Sophie Hilgard;Ryan Lapcevic;Anthony Soroka;Yamini Bansal; Ariel Herbert-Voss',
    author_email='rlapcevic@g.harvard.edu',
    url='',  
    license=license,
    description='A library for creating and communicating with 	a time series database over a socket.',
    long_description=readme
)

