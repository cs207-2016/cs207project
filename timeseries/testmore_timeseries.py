
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

##### ArrayTimeSeries Tests ####

'''
Functions Being Tested: mult
Summary: mult integer TypeError 
'''
def test_mult3():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    myList = [1,2,3,4]
    with raises(TypeError):
        ts * myList


'''
Functions Being Tested: sub
Summary: sub integer TypeError 
'''
def test_sub3():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    myList = [1,2,3,4]
    with raises(TypeError):
        ts - myList

'''
Functions Being Tested: add
Summary: add integer TypeError 
'''
def test_add3():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    myList = [1,2,3,4]
    with raises(TypeError):
        ts + myList

