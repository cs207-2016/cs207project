
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
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    assert len(ts) == 4

'''
Functions Being Tested: getitem
Summary: Basic Get Item Test
'''
def test_getItem():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    assert ts[3] == 103

'''
Functions Being Tested: setitem
Summary: Basic Set Item test
'''
def test_setItem():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts[2] = 5
    assert ts[2] == 5

'''
Functions Being Tested: str
Summary: Basic str test
'''
def test_str():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    assert str(ts) == '[100, 101, 102, 103]'

'''
Functions Being Tested: interpolate
Summary: Basic interpolate test
'''
def test_interpolateA():
    a = TimeSeries([0,5,10], [1,2,3])
    assert a.interpolate([1]) == TimeSeries([1],[1.2])

'''
Functions Being Tested: interpolate and itertimes
Summary: Interpolate and Itertimes Test
'''
def test_interpolate_itertimes():
     
    a = TimeSeries([0,5,10], [1,2,3])
    b = TimeSeries([2.5,7.5], [100, -100])
    assert a.interpolate(b.itertimes()) == TimeSeries([2.5,7.5], [1.5, 2.5])


'''
Functions Being Tested: interpolate
Summary: Interpolate Boundary Scenario
'''
def test_interpolate_boundary():
    a = TimeSeries([0,5,10], [1,2,3])
    a.interpolate([-100,100]) == TimeSeries([-100,100],[1,3])
