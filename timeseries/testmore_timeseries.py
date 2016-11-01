
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
Functions Being Tested: interpolate ATS
Summary: Basic interpolate test
'''
def test_interpolateA_ats():
    a = ArrayTimeSeries([0,5,10], [1,2,3])
    assert a.interpolate([1]) == ArrayTimeSeries([1],[1.2])


