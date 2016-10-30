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


#!/usr/bin/env python3

import numpy as np
import math
import numbers
from lazy import *
import abc

class TimeSeriesInterface(abc.ABC):

    @abc.abstractmethod
    def __iter__(self):
       '''Iterate over data in TimeSeries'''

    @abc.abstractmethod
    def iteritems(self):
        '''Iterate over (time, data)'''

    @abc.abstractmethod
    def itertimes(self):
        '''Iterate over times'''

class TimeSeries():
    ''' A series of data points indexed by time.'''

    def __init__(self, times, seq):
        '''Creates a TimeSeries using the data points in `seq` and time points time.

        Args:
            seq (:obj:`sequence` of `numeric`): A sequence of data points indexed by time.
            time (:obj:`sequence` of `numeric`): A sequence of time points
                

        Example:
            >>> ts = TimeSeries([1, 2, 3, 4],[100,101,102,103])
            >>> ts
            TimeSeries([100,...])
        '''
        # raise an exception if `seq` is not iterable
        try:
            iter(seq)
        except:
            raise TypeError('`seq` must be a sequence')

        # raise an exception if `times` and `seq` are not of equal length
        if len(list(times)) != len(list(seq)):
            raise ValueError('Both constructor parameters must have the same length.')
        

        self._data = list(seq)
        self._times = list(times)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __repr__(self):
        class_name = type(self).__name__
        if len(self)==0:
            components=""
        else:
            components = self._data[0]
        return '{}([{},...])'.format(class_name, components)

    def __str__(self):
        '''Returns the sequence of data points contained in the TimeSeries.'''
        return(str(self._data))

    def __iter__(self):
        return iter(self._data)

    def itertimes(self):
        '''Returns the time indices for the TimeSeries data points'''

        return iter(self._times[:len(self)])

    def iteritems(self):
        '''Returns a tuple (time, value) for each item in the TimeSeries.'''
        return iter(zip(self._times[:len(self)], self._data[:len(self)]))

    def interpolate(self, interpts):
        
        #Anthony Amended this
        #times = []
        
        seq = []
        timeRecord = []
        for i in interpts:
            times = sorted(enumerate(self._times), key=lambda x:abs(x[1]-i))[:2]
            vals = [self._data[times[0][0]], self._data[times[1][0]]]
            new_val = vals[0] + (i-times[0][1])*(vals[1]-vals[0])/(times[1][1]-times[0][1])
            
            #Anthony removed this
            #times.append(i)
            
            seq.append(new_val)
            timeRecord.append(i)

        #Anthony amended this
        #return TimeSeries(interpts,seq)

        return TimeSeries(timeRecord,seq)



    def __abs__(self):
        return math.sqrt(sum(x * x for x in self))

    def __bool__(self):
        return bool(abs(self))

    def _check_time_values(function):
        def _check_time_values_helper(self , rhs):
            try:
                if not all(t1 == t2 for t1, t2 in zip(self._times, rhs._times)):
                    raise ValueError(str(self)+' and '+str(rhs)+' must have the same points')
                return function(self,rhs)
            except AttributeError:
                raise NotImplemented
        return _check_time_values_helper

    def __neg__(self):
        return TimeSeries(self._times, [-x for x in self._data])

    def __pos__(self):
        return TimeSeries(self._times, self._data)

    @_check_time_values
    def __eq__(self, other):
        if isinstance(other, numbers.Real):
            return (all(val1 == numbers.Real for val1 in self._data))
        else:
            return (all(val1 == val2 for val1, val2 in zip(self._data, other._data)))

    @_check_time_values
    def __add__(self, other):
        if isinstance(other, numbers.Real):
            return TimeSeries(self._times, [x + other for x in self._data])
        else:
            return TimeSeries(self._times, [x+y for x, y in zip(self._data, other._data)])

    # Implements lhs - rhs
    @_check_time_values
    def __sub__(self, other):
        if isinstance(other, numbers.Real):
            return TimeSeries(self._times, [x-other for x in self._data])
        else:
            return TimeSeries(self._times, [x-y for x, y in zip(self._data, other._data)])

    @_check_time_values
    def __mul__(self, other):
        if isinstance(other, numbers.Real):
            return TimeSeries(self._times, [x*other for x in self._data])
        else:
            return TimeSeries(self._times, [x*y for x, y in zip(self._data, other._data)])



    ##DEFINE __EQ__

    @property
    def lazy(self):
        return LazyOperation(lambda x: x, self)




class ArrayTimeSeries(TimeSeries):
    ''' A series of data points indexed by time developed using Numpy.'''

    def __init__(self, times, seq):
        '''Creates a TimeSeries using the data points in `seq` and time points time.

        Args:
            seq (:obj:`sequence` of `numeric`): A sequence of data points indexed by time.
            time (:obj:`sequence` of `numeric`): A sequence of time points
                

        Example:
            >>> ats = ArrayTimeSeries([1, 2, 3, 4],[100,101,102,103])
            >>> ats
            ArrayTimeSeries([[1.0   100.0]
            [2.0    101.0]
            [3.0    102.0]
            [4.0    103.0]])
        '''
        # raise an exception if parameters are not iterable
        for s in [times, seq]:
            try:
                iter(s)
            except:
                raise TypeError('Both constructor parameters must be sequences.')

        # raise an exception if `times` and `seq` are not of equal length
        if len(times) != len(seq):
            raise ValueError('Both constructor parameters must have the same length.')

        # _length (int): The ArrayTimeSeries length / first empty index in the array
        self._length = len(seq)

        # Initialize array to twice the length of the sequence (room for future data)
        self._data = np.empty(len(seq) * 2)
        self._times = np.empty(len(seq) * 2)
        self._data[:self._length] = seq
        self._times[:self._length] = times

    def __len__(self):
        return self._length

    def __repr__(self):
        format_str = '{}([{}])'
        row_str = '[{}\t{}]'
        add_str = ''

        for i in range(self._length):
            add_str += row_str.format(self._times[i], self._data[i])
            if i != self._length - 1: add_str += '\n'

        class_name = type(self).__name__
        return format_str.format(class_name, add_str)

    def __getitem__(self, key):
        if key >= self._length:
            raise IndexError('ArrayTimeSeries index out of range.')
        return self._data[key]

    def __setitem__(self, key, value):
        if key >= self._length:
            raise IndexError('ArrayTimeSeries index out of range.')
        self._data[key] = value

    def __iter__(self):
        return iter(self._data[:self._length])

    def itertimes(self):
        '''Returns an iterator over the time indices for the ArrayTimeSeries.'''
        return iter(self._times[:self._length])

    def iteritems(self):
        '''Returns an iterator over the tuples (time, value) for each item in the ArrayTimeSeries.'''
        return iter(zip(self._times[:self._length], self._data[:self._length]))

class StreamTimeSeriesInterface(TimeSeriesInterface):
    '''Creates an interface for a Timeseries with no internal storage that
    yields data based on a generator '''

    @abc.abstractmethod
    def produce(self)->list:
        "intersection with another set"

class SimulatedTimeSeries(StreamTimeSeriesInterface):

    def __init__(self, generator):
        '''Creates a TimeSeries using a generator that creates tuples of (time, value)
        Internally, this subclass has no storage.

        Args:
            generator (:obj:`sequence` of `numeric): A sequence of (time, value) tuples.

        Example:
            >>> ts = TimeSeries(generator)
            >>> ts
            SimulatedTimeSeries([<generator object make_data at 0x1091183b8>])
        '''

        self._gen = generator

    def __iter__(self):
        return self

    def __next__(self):
        return self.produce()

    def iteritems(self):
        return self.produce()[1]

    def itertimes(self):
        return self.produce()[0]

    def __repr__(self):
        format_str = '{}([{}])'

        class_name = type(self).__name__
        return format_str.format(class_name, str(self._gen))

    def produce(self, chunk=1):
        for i in range(chunk):
            value = next(self._gen)
            if type(value) == tuple:
                return value
            else:
                return (datetime.datetime.now(), value)
