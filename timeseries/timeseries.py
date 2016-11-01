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

class SizedContainerTimeSeriesInterface(TimeSeriesInterface):
    
    def __init__(self, time_points, data_points):

        # Raise an exception if any parameter is not a sequence
        params = {'time_points': time_points,
                  'data_points': data_points}
        for p in params:
            try:
                iter(params[p])
            except:
                raise TypeError('`%s` must be a sequence.' % p)
                
                
        # Raise an exception if `time_points` and `data_points` are not the same length
        if len(list(time_points)) != len(list(data_points)):
            raise ValueError('`time_points` and `data_points` must have the same length.')

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __repr__(self):
        return str(self)

    def __str__(self):
        format_str = '{}([{}])'
        row_str = '[{}\t{}]'
        add_str = ''
        
        for pts in self.iteritems():
            add_str += row_str.format(pts[0], pts[1])
        class_name = type(self).__name__
        return format_str.format(class_name, add_str)

    def interpolate(self, pts):
        inter_pts = []
        ts = list(pts)
        for pt in ts:
            # Get the two time points bounding `pts`
            times = sorted(enumerate(self._times), key = lambda x: abs(x[1] - pt))[:2]
            vals = [self._data[times[0][0]], self._data[times[1][0]]]
            x = vals[0] + (pt - times[0][1]) * (vals[1] - vals[0]) / (times[1][1] - times[0][1])
            inter_pts.append(x)
        return TimeSeries(ts, inter_pts)

    def __abs__(self):
        return math.sqrt(sum(x**2 for x in self))

    def __bool__(self):
        return bool(abs(self))

    def _check_time_values(function):
        def _check_time_values_helper(self , rhs):
            print(rhs)
            try:
                if isinstance(rhs, numbers.Real): 
                    return function(self, rhs)
                elif len(self) != len(rhs) or not all(t1 == t2 for t1, t2 in zip(self.itertimes(), rhs.itertimes())):
                    raise ValueError('Both time series must have the same time points.')
                return function(self, rhs)
            except AttributeError:
                raise NotImplemented
        return _check_time_values_helper

    def __neg__(self):
        # TODO: Create instance of calling class instead of TimeSeries
        return TimeSeries(list(self.itertimes()), [-x for x in iter(self)])

    def __pos__(self):
        # TODO: Create instance of calling class instead of TimeSeries
        return TimeSeries(list(self.itertimes()), list(iter(self)))

    @_check_time_values
    def __eq__(self, other):
        if isinstance(other, numbers.Real):
            return (all(x == numbers.Real for x in iter(self)))
        else:
            return (all(x == y for x, y in zip(iter(self), iter(other))))

    @_check_time_values
    def __add__(self, other):
        if isinstance(other, numbers.Real):
            return TimeSeries(list(self.itertimes()), [x + other for x in iter(self)])
        else:
            return TimeSeries(list(self.itertimes()), [x + y for x, y in zip(iter(self), iter(other))])

    @_check_time_values
    def __sub__(self, other):
        if isinstance(other, numbers.Real):
            return TimeSeries(list(self.itertimes()), [x - other for x in iter(self)])
        else:
            return TimeSeries(list(self.itertimes()), [x - y for x, y in zip(iter(self), iter(other))])

    @_check_time_values
    def __mul__(self, other):
        if isinstance(other, numbers.Real):
            return TimeSeries(list(self.itertimes()), [x * other for x in iter(self)])
        else:
            return TimeSeries(list(self.itertimes()), [x * y for x, y in zip(iter(self), iter(other))])

    def mean(self):
        return sum(self.itertimes())/len(self)
    
    def iteritems(self):
        return iter(zip(self.itertimes(), iter(self)))        
        
    @property
    def lazy(self):
        return LazyOperation(lambda x: x, self)
        
class TimeSeries(SizedContainerTimeSeriesInterface):
    def __init__(self, time_points, data_points):
               
        super().__init__(time_points, data_points)
        self._times = list(time_points)
        self._data = list(data_points)

    def __len__(self):
        return len(self._times)       
                                                 
    def __iter__(self):
        return iter(self._data)

    def itertimes(self):
        return iter(self._times)           
                                                 
class ArrayTimeSeries(TimeSeries):

    def __init__(self, time_points, data_points):

        super().__init__(time_points, data_points)
        
        self._length = len(time_points)
        self._times = np.empty(self._length * 2)
        self._data = np.empty(self._length * 2)
        self._times[:self._length] = time_points
        self._data[:self._length] = data_points

    def __len__(self):
        return self._length

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


def online_mean(self, chunk=1):
    def gen():
        n = 0
        mean = 0
        for x in self.iteritems():
            n += 1
            mean = ((n - 1) * mean + x) / n
            yield mean

    return SimulatedTimeSeries(gen)


class SimulatedTimeSeries(StreamTimeSeriesInterface):

    def __init__(self, generator):
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
