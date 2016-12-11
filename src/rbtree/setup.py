#!/usr/bin/env python3

from setuptools import setup

with open('README.md') as f:
    readme = f.read()
with open('LICENSE') as f:
    license = f.read()

setup(
    name='rbtree',
    version='0.1',
    scripts=['rbtree.py'],
    author='Sophie Hilgard;Ryan Lapcevic;Anthony Soroka;Yamini Bansal; Ariel Herbet-Voss',
    author_email='rlapcevic@g.harvard.edu',
    url='',
    license=license,
    description='A library implementing a red-black tree',
    long_description=readme
)

