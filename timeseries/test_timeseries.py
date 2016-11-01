
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
Functions Being Tested: Len
Summary: Basic Len Test
'''
def test_len():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    assert len(ts) == 4

'''
Functions Being Tested: Repr
Summary: Basic Repr Test
'''
def test_repr():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    assert repr(ts) == 'TimeSeries([[1\t100][2\t101][3\t102][4\t103]])'

'''
Functions Being Tested: Init
Summary: Value error if Time and Data Length don't match
'''
def test_init_valueError():
    with raises(ValueError):
        ts = TimeSeries([1,2,3,4,5],[100,101,102,103])

'''
Functions Being Tested: Init
Summary: Value error if time value is not a real number
'''
def test_init_valueError_time():
    with raises(ValueError):
        ts = TimeSeries([1,2,"hello",4],[100,101,102,103])

'''
Functions Being Tested: Init
Summary: Value error if data value is not a real number
'''
def test_init_valueError_data():
    with raises(ValueError):
        ts = TimeSeries([1,2,3,4],[100,"hello",102,103])

'''
Functions Being Tested: Init
Summary: Value error if time value is duplicated
'''
def test_init_valueError_dupTime():
    with raises(ValueError):
        ts = TimeSeries([1,2,2,4],[100,100,102,103])

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
Functions Being Tested: getitem
Summary: TypeError Get Item for String
'''
def test_getItem_TypeError():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    with raises(TypeError):
        ts["hello"]

'''
Functions Being Tested: getitem
Summary: TypeError Get Item for Float
'''
def test_getItem_TypeError3():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    with raises(TypeError):
        ts[52.222]

'''
Functions Being Tested: getitem
Summary: TypeError Get Item for Float
'''
def test_getItem_IndexError():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    with raises(IndexError):
        ts[33]

'''
Functions Being Tested: setitem
Summary: Basic Set Item test
'''
def test_setItem():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts[2] = 5
    assert ts[2] == 5

'''
Functions Being Tested: setitem
Summary: ValueError if setting a value that's not a real number
'''
def test_setItem_ValueError():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    with raises(ValueError):
        ts[0] = "hello"

'''
Functions Being Tested: str
Summary: Basic str test
'''
#def test_str():
#    ts = TimeSeries([1,2,3,4],[100,101,102,103])
#    assert str(ts) == '[100, 101, 102, 103]'

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
Functions Being Tested: add
Summary: add integer
'''
def test_add2():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4],[105,106,107,108])
    assert ts2 == (ts+5)


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
Summary: sub integer
'''
def test_sub2():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4],[105,106,107,108])
    assert ts == (ts2 - 5)

'''
Functions Being Tested: sub
Summary: Basic sub test
'''
def test_mult():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4],[2,2,2,2])
    ts3 = TimeSeries([1,2,3,4],[200,202,204,206])
    assert ts3 == (ts*ts2)

'''
Functions Being Tested: mult
Summary: mult integer
'''
def test_mult2():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    ts2 = TimeSeries([1,2,3,4],[500,505,510,515])
    assert ts2 == (ts * 5)

'''
Functions Being Tested: abs
Summary: Basic abs test
'''
def test_abs():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    testAbs =  (100**2+101**2+102**2+103**2)**.5
    assert testAbs == abs(ts)


'''
Functions Being Tested: bool
Summary: Basic Bools Test (True)
'''
def test_bool():
    ts = TimeSeries([1,2,3,4],[100,101,102,103])
    assert bool(ts) == True

'''
Functions Being Tested: bool2
Summary: Basic Bools Test (False)
'''
def test_bool_false():
    ts = TimeSeries([1,2,3,4],[0,0,0,0])
    assert bool(ts) == False


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
def test_init_typeError_ats():
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
Functions Being Tested: getitem
Summary: getItem Index Error
'''
def test_getItem_ats_IndexError():
    ats = ArrayTimeSeries([1,2,3,4],[100,101,102,103])
    with raises(IndexError):
        ats[5]


'''
Functions Being Tested: setitem
Summary: Basic Set Item test
'''
def test_setItem_ats():
    ats = ArrayTimeSeries([1,2,3,4],[100,101,102,103])
    ats[2] = 5
    assert ats[2] == 5

'''
Functions Being Tested: add
Summary: add list NotImplemented
'''
def test_add_notImplemented():
   ts = TimeSeries([1,2,3,4],[100,101,102,103])
   myList = [1,2,3,4]
   with raises(NotImplementedError):
       ts + myList

'''
Functions Being Tested: mult
Summary: mult list NotImplemented
'''
def test_mult_notImplemented():
   ts = TimeSeries([1,2,3,4],[100,101,102,103])
   myList = [1,2,3,4]
   with raises(NotImplementedError):
       ts*myList

'''
Functions Being Tested: sub
Summary: sub list NotImplemented
'''
def test_sub_notImplemented():
   ts = TimeSeries([1,2,3,4],[100,101,102,103])
   myList = [1,2,3,4]
   with raises(NotImplementedError):
       ts-myList

'''       
Functions Being Tested: setitem
Summary: setItem Index Error
'''
def test_setItem_ats_IndexError():
    ats = ArrayTimeSeries([1,2,3,4],[100,101,102,103])
    with raises(IndexError):
        ats[5] = 105

'''
Functions Being Tested: std
Summary: standard deviation
'''

def test_std():
    ts = TimeSeries([1,2,3,4], [10, 11, 12, 13])
    assert ts.std() == np.std([10, 11, 12, 13])

'''Functions Being Tested: interpolate and itertimes ATS
Summary: Interpolate and Itertimes Test
'''
def test_interpolate_itertimes_ats():
     
    a = ArrayTimeSeries([0,5,10], [1,2,3])
    b = ArrayTimeSeries([2.5,7.5], [100, -100])
    assert a.interpolate(b.itertimes()) == ArrayTimeSeries([2.5,7.5], [1.5, 2.5])


'''
Functions Being Tested: interpolate ATS
Summary: Interpolate Boundary Scenario
'''
def test_interpolate_boundary_ats():
    a = ArrayTimeSeries([0,5,10], [1,2,3])
    a.interpolate([-100,100]) == ArrayTimeSeries([-100,100],[1,3])


