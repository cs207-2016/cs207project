
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
from timeseries import *
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
Functions Being Tested: Init
Summary: Value error if Time and Data Length don't match
'''
def test_init_valueError():
    with raises(ValueError):
        ts = TimeSeries([1,2,3,4,5],[100,101,102,103])

'''
Functions Being Tested: Init
Summary: Value error if time or data not a seq
'''
def test_init_typeError():
    with raises(TypeError):
        ts = TimeSeries(3,100)

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

'''
Functions Being Tested: eq
Summary: Basic eq Test (true)
'''
def test_eq():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4],[100,101,102,103])
    assert ts == ts2

'''
Functions Being Tested: eq
Summary: Basic eq Test 2 (false)
'''
def test_eq2():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4],[100,101,102,104])
    assert ts != ts2

'''
Functions Being Tested: neg
Summary: Basic neg test
'''
def test_neg():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4],[-100,-101,-102,-103])
    assert -ts == ts2


'''
Functions Being Tested: pos
Summary: Basic ps test
'''
def test_pos():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = +ts
    assert ts == ts2


'''
Functions Being Tested: add
Summary: Basic add test
'''
def test_add():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4],[200,202,204,206])
    assert ts2 == (ts+ts)

'''
Functions Being Tested: sub
Summary: Basic sub test
'''
def test_sub():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4],[0,0,0,0])
    assert ts2 == (ts-ts)

'''
Functions Being Tested: sub
Summary: Basic sub test
'''
def test_mult():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4],[2,2,2,2])
    ts3 = TimeSeries([1,2,3,4],[200,202,204,206])
    assert ts3 == (ts*ts2)


### Start of ArrayTimeSeries Tests###

'''
Functions Being Tested:
Summary: Basic Len Test
'''
def test_len_ats():
    ats = ArrayTimeSeries([1,2,3,4],[100,101,102,103])
    assert len(ats) == 4



'''
Functions Being Tested: Init
Summary: Value error if Time and Data Length don't match
'''
def test_init_valueError_ats():
    with raises(ValueError):
        ats = ArrayTimeSeries([1,2,3,4,5],[100,101,102,103])

'''
Functions Being Tested: Init
Summary: Value error if time or data not a seq
'''
def test_init_typeError_Ats():
    with raises(TypeError):
        ts = TimeSeries(3,100)


'''
Functions Being Tested: getitem
Summary: Basic Get Item Test
'''
def test_getItem_ats():
    ats = ArrayTimeSeries([1,2,3,4],[100,101,102,103])
    assert ats[3] == 103

'''
Functions Being Tested: setitem
Summary: Basic Set Item test
'''
def test_setItem_ats():
    ats = ArrayTimeSeries([1,2,3,4],[100,101,102,103])
    ats[2] = 5
    assert ats[2] == 5


