
''''

Authors:
Sophie Hilgard
Ryan Lapcevic
Anthony Soroka
Ariel Herbert-Voss
Yamini Bansal

Date: 15 Oct 2016
Course: Project CS 207
Document: testmore_timeseries.py
Summary: Testing Timeseries Class

Example:
    Example how to run this test
        $ source activate py35
        $ py.test testmore_timeseries.py

'''



from pytest import raises
from timeseries import *
import numpy as np
import random


'''
Functions Being Tested: add
Summary: Value Error on Add
'''
def test_add_valueError():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4,5],[200,202,204,206,207])
    with raises(ValueError):
        ts + ts2

'''
Functions Being Tested: sub
Summary: Value Error on Sub
'''
def test_sub_valueError():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4,5],[200,202,204,206,207])
    with raises(ValueError):
        ts - ts2

'''
Functions Being Tested: mult
Summary: Value Error on Mult
'''
def test_mult_valueError():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4,5],[200,202,204,206,207])
    with raises(ValueError):
        ts * ts2

