
''''

Authors:
Sophie Hilgard
Ryan Lapcevic
Anthony Soroka
Ariel Herbert-Voss
Yamini Bansal

Date: 15 Oct 2016
Course: Project CS 207
Document: test_timeseries.py
Summary: Testing Timeseries Class

Example:
    Example how to run this test
        $ source activate py35
        $ py.test test_timeseries.py

'''



from pytest import raises
from timeseries import TimeSeries
import numpy as np
import random


'''
Functions Being Tested:
Summary: Basic Len Test
'''
def test_len():
    ts = TimeSeries([1,2,3,4])
    assert len(ts) == 4

'''
Functions Being Tested: getitem
Summary: Basic Get Item Test
'''
def test_getItem():
    ts = TimeSeries([1,2,3,4])
    assert ts[3] == 4

'''
Functions Being Tested: setitem
Summary: Basic Set Item test
'''
def test_setItem():
    ts = TimeSeries([1,2,3,4])
    ts[2] = 5
    assert ts[2] == 5

'''
Functions Being Tested: str
Summary: Basic str test
'''
def test_str():
    ts = TimeSeries([1,2,3,4])
    assert str(ts) == '[1, 2, 3, 4]'
