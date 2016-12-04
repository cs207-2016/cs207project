"""'

Authors:
Sophie Hilgard
Ryan Lapcevic
Anthony Soroka
Ariel Herbert-Voss
Yamini Bansal

Date: 28 Oct 2016
Course: Project CS 207
Document: test_cs207rbtree.py
Summary: Testing RBTree Class

Example:
    Example how to run this test
        $ source activate py35
        $ py.test test_storagemanager.py
"""

from pytest import raises
from random import *
from os.path import isfile
from sys import getsizeof
from operator import neg, sub, add
from itertools import combinations as combos

from storage_manager import *
from timeseries import *

'''
Functions being tested: store
Summary: Test FileStorageManager storage functionality
'''


def test_store():
    fsm = FileStorageManager()
    for i in range(10):
        ts = list(range(0, randint(0, 10000)))
        vs = [randint(0, 1000000) for t in ts]
        ats = ArrayTimeSeries(ts, vs)
        fsm.store(i, ats)
        assert isfile('{}/{}.npy'.format(fsm._storage, str(i)))


'''
Functions being tested: get
Summary: Test whether FileStorageManager returns by id
'''


def test_get():
    tseries = []
    fsm = FileStorageManager()
    for i in range(10):
        ts = list(range(0, randint(0, 10000)))
        vs = [randint(0, 1000000) for t in ts]
        ats = ArrayTimeSeries(ts, vs)
        fsm.store(i, ats)
        tseries.append(ats)
    for i in range(10):
        assert tseries[i] == fsm.get(str(i))


'''
Functions being tested: FileStorageManager caching
Summary: Tests whether newly stored time series are cached
and whether cache trimming works
'''


def test_cache():
    size = 0
    sizelim = randint(4, 10) * 1024
    fsm = FileStorageManager(max_cache_size=sizelim)
    i = 0

    # Test whether caching is working
    while size < sizelim:
        ts = list(range(0, randint(0, 10000)))
        vs = [randint(0, 1000000) for t in ts]
        ats = ArrayTimeSeries(ts, vs)
        size += getsizeof(ats)
        if size < sizelim:
            fsm.store(i, ats)
            i += 1
    for j in range(i):
        assert str(j) in fsm._cache.keys()

    # Test whether cache trimming is working
    while size <= sizelim:
        ts = list(range(0, randint(0, 10000)))
        vs = [randint(0, 1000000) for t in ts]
        ats = ArrayTimeSeries(ts, vs)
        size += getsizeof(ats)
        fsm.store(i, ats)
        i += 1

    assert '0' not in fsm._cache.keys()


'''
Functions being tested: size
Summary: Tests whether FileStorageManager returns time series sizes properly
'''


def test_size():
    tseries = []
    fsm = FileStorageManager()
    for i in range(10):
        ts = list(range(0, randint(0, 10000)))
        vs = [randint(0, 1000000) for t in ts]
        ats = ArrayTimeSeries(ts, vs)
        fsm.store(i, ats)
        tseries.append(ats)

    for i in range(10):
        assert len(tseries[i]) == fsm.size(str(i))


'''
Functions being tested: from_db
Summary: Tests whether SMTimeSeries creates time series from storage
'''


def test_SMTimeSeries():
    tseries = []
    fsm = FileStorageManager()
    for i in range(10):
        ts = list(range(0, randint(0, 10000)))
        vs = [randint(0, 1000000) for t in ts]
        ats = ArrayTimeSeries(ts, vs)
        fsm.store(i, ats)
        tseries.append(ats)

    for i in range(10):
        assert SMTimeSeries.from_db(i) == fsm.get(i)


'''
Functions being tested: caching of time series operations
Summary: Tests whether the FileStorageManager is caching the results of operations on SMTimeSeries
'''


def test_cache_ops():
    fsm = FileStorageManager()
    ops = [sub, add]
    tseries = []
    size_tot = 0

    ts = list(range(0, randint(0, 10000)))
    for i in range(5):
        vs = [randint(0, 1000000) for t in ts]
        ats = ArrayTimeSeries(ts, vs)
        fsm.store(i, ats)
        tseries.append(ats)
        size_tot += getsizeof(ats)

    fsm = FileStorageManager(max_cache_size=10 * size_tot)
    for o in ops:
        for i, j in combos(range(5), 2):
            t1 = SMTimeSeries.from_db(i, fsm)
            t2 = SMTimeSeries.from_db(j, fsm)
            t3 = o(t1, t2)
            assert o(t1, t2) == fsm._cache[t3._ident]

    t = -SMTimeSeries.from_db(0)
    assert -tseries[0] == fsm._cache[t._ident]
