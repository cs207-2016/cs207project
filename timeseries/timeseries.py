#!/usr/bin/env python3

import numpy as np
import math
import numbers
from lazy import *
import abc
import datetime

class TimeSeriesInterface(abc.ABC):
    '''A series of data points associated with time points.'''

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
    '''A TimeSeriesInterface that stores time and data points internally.

    The interface preserves information but not type: ints may be converted to floats.'''

    def __init__(self, time_points, data_points):
        '''Constructor for SizedContainerTimeSeriesInterface.

        Args:
            `time_points` (`sequence` of `numbers.Real`): 
                A nondecreasing sequence of time points. Must have same length as `data_points`.
            `data_points` (`sequence` of `numbers.Real`): 
                A sequence of data points. Must have same length as `time_points`.'''

        # Raise an exception if any parameter is not a sequence.
        params = {'time_points': time_points,
                  'data_points': data_points}
        for p in params:
            try:
                iter(params[p])
            except:
                raise TypeError('Parameter `%s` must be a sequence type.' % p)

        # Raise an exception if `time_points` and `data_points` are not the same length
        if len(list(time_points)) != len(list(data_points)):
            raise ValueError('Parameters `time_points` and `data_points` must have the same length.')

        # Raise Exception if a time value is not a real number
        for time in iter(time_points):
            if not isinstance(time, numbers.Real):
                raise ValueError('`time_points` must be real numbers')

        # Raise Exception if a data value is not a real number
        for data in iter(data_points):
            if not isinstance(data, numbers.Real):
                raise ValueError('`data_points` must be real numbers')

        # Raise exception if there is a duplicate time value
        if len(np.unique(list(time_points))) !=len(list(time_points)):
            raise ValueError('No Duplicate Time Values')


    def __getitem__(self, key):
        '''Returns the data point from the time series with index = key.
         
        Args:
            `key`(int): The index of the desired data point.
        Returns: 
            numbers.Real: The value stored at the index `key`.'''
        
        return self._data[key]

    def __setitem__(self, key, value):
        '''Sets the data point from the TimeSeries with index = key to value'''

        # Raise exception if a value is not a real number
        if not isinstance(value, numbers.Real):
            raise ValueError('`value` must be a real number')
        else:
            self._data[key] = value

    def __repr__(self):
        '''Returns a string containing all information about the instance relevant to a technical user.

        Returns:
            str: The representation of the object.'''

        fmt_str = '<{}.{} object at {}>{}'
        return fmt_str.format(
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self)),
            str(self))

    def __str__(self):
        '''Returns a succint interpretation of the SizedContainerTimeSeriesInterface.

        Returns:
            str: An informal description of the object.'''

        format_str = '{}([{}])'
        row_str = '[{},{}]'
        add_str = ''
        for pts in self.iteritems():
            add_str += row_str.format(pts[0], pts[1]) + '\n'
        class_name = type(self).__name__
        return format_str.format(class_name, add_str)

    def interpolate(self, pts):
        '''Generates new interpolated values for a TimeSeries given unseen times.
        Uses stationary boundary conditions: if a new time point is smaller than the
        first existing time point, returns the first value; likewise for larger time points.

        Args:
            pts: a list of time values to create interpolated points for

        Returns:
            A new SizedContainerTimeSeriesInterface (of the same type) with the provided times and their interpolated values.'''

        inter_pts = []
        ts = list(pts)
        for t in ts:
            # Get the two time points bounding `pts`
            times = sorted(enumerate(self.itertimes()), key = lambda x: abs(x[1] - t))[:2]
            i1, t1 = times[0]
            i2, t2 = times[1]
            if t <= t1: 
                inter_pts.append(self._data[i1])
            elif t >= t2:
                inter_pts.append(self._data[i2])
            else:
                dt = t2 - t1
                dy = self._data[i2] - self._data[i1]
                m = dy / dt
                y = m * (t - t1) + self._data[i1]
                inter_pts.append(y)
        return type(self)(ts, inter_pts)

    def __abs__(self):
        '''Calculates the two-norm of the value vector of the time series.

        Returns:
            float: The two-norm of the value vector of the time series.'''

        return math.sqrt(sum(x**2 for x in self))

    def __bool__(self):
        '''Determines whether the value vector is of length zero.
    
        Returns:
            bool: True if abs(self) != 0, False otherwise.'''

        return bool(abs(self))

    def _check_time_values(function):
        '''Verifies that the RHS of an instance function is either a numbers.Real or
           a SizedContainerTimeSeriesInterface with identical time values.

           Returns:
                function: The function verifying that the RHS is compatible.

           Raises:
                ValueError: The RHS is a time series whose time points are not equivalent.
                NotImplementedError: The RHS is a noncompatible type.'''

        def _check_time_values_helper(self , rhs):
            # An internal method for verifying that the other argument in an binary function is valid.
            if isinstance(rhs, numbers.Real):
                return function(self, rhs)
            elif not isinstance(rhs, SizedContainerTimeSeriesInterface):
                raise NotImplementedError
            elif len(self) != len(rhs) or not all(t1 == t2 for t1, t2 in zip(self.itertimes(), rhs.itertimes())):
                raise ValueError('Both time series must have the same time points.')
            return function(self, rhs)
        return _check_time_values_helper

    def __neg__(self):
        '''Returns a new time series of the same class with the negation of each data point.
          
           Returns:
               SizedContainerTimeSeriesInterface: A new instance whose data points are the negation of `self`'s.'''

        return type(self)(list(self.itertimes()), [-x for x in iter(self)])

    def __pos__(self):
        '''Returns a new time series with identical data points.
           
           Returns:
               SizedContainerTimeSeriesInterface: A copy of the instance.'''
        return type(self)(list(self.itertimes()), list(iter(self)))

    @_check_time_values
    def __eq__(self, other):
        '''Verifies that either the RHS is an equal SizedContainerTimeSeriesInterface
           or all data points are equal to a real number.

        Args:
            `other` (numbers.Real or SizedContainerTimeSeriesInterface): 
                Either a real number or another SizedContainerTimeSeriesInterface. 
                If using another TimeSeries, it must have the same time and data values.

        Returns:
            bool: True if all (time,value) tuples of the two TimeSeries are the same, or if all
            values of the TimeSeries are equal to the real number. False otherwise.'''

        if isinstance(other, numbers.Real):
            return (all(x == numbers.Real for x in iter(self)))
        else:
            return (all(x == y for x, y in zip(iter(self), iter(other))))

    @_check_time_values
    def __add__(self, other):
        '''Adds either a real number to each data point or elementwise addition with another time series.

        Args:
            `other` (numbers.Real or SizedContainerTimeSeriesInterface): 
                Either a real number or another TimeSeries. 
                If using another TimeSeries, it must have the same time values.

        Returns:
            SizedContainerTimeSeriesInterface: 
                A new time series with the same times and either an elementwise addition
                with the real number or elementwise addition between the values of the other time series.'''

        if isinstance(other, numbers.Real):
            return type(self)(list(self.itertimes()), [x + other for x in iter(self)])
        else:
            return type(self)(list(self.itertimes()), [x + y for x, y in zip(iter(self), iter(other))])

    @_check_time_values
    def __sub__(self, other):
        '''Subtracts either a real number from each data point or elementwise subtraction with another time series.

        Args:
            `other` (numbers.Real or SizedContainerTimeSeriesInterface): 
                Either a real number or another time series. 
                If using another time series, it must have the same time values.

        Returns:
            SizedContainerTimeSeriesInterface subclass: 
                A new time series with the same times and either an elementwise addition
                with the real number or elementwise addition between the values of the other time series.'''

        if isinstance(other, numbers.Real):
            return type(self)(list(self.itertimes()), [x - other for x in iter(self)])
        else:
            return type(self)(list(self.itertimes()), [x - y for x, y in zip(iter(self), iter(other))])

    @_check_time_values
    def __mul__(self, other):
        '''Either multiplies another time series elementwise, or multiples each data point value by a real number.

        Args:
            `other` (numbers.Real or SizedContainerTimeSeriesInterface): 
                Either a real number or another time series. 
                If using another time series, it must have the same time values.

        Returns:
            SizedContainerTimeSeriesInterface subclass: 
                A new time series with the same times and either an elementwise multiplication
                with the real number or elementwise multiplication between the values of the other time series.'''

        if isinstance(other, numbers.Real):
            return type(self)(list(self.itertimes()), [x * other for x in iter(self)])
        else:
            return type(self)(list(self.itertimes()), [x * y for x, y in zip(iter(self), iter(other))])

    def mean(self):
        '''Returns the mean of all data points in the time series.

        Returns:
            float: the mean of all data points in the time series.'''

        return np.mean(list(iter(self)))

    def iteritems(self):
        '''Returns an iterator over tuples of the time series' time and data points.

        Returns:
            iterable: an iterator over tuples (time, data) of the time series.'''

        return iter(zip(self.itertimes(), iter(self)))

    @property
    def lazy(self):
        '''Returns a new instance of LazyOperation.

        Returns:
            LazyOperation: a wrapper around a function not evaluated until called.'''

        return LazyOperation(lambda x: x, self)

    def std(self):
        '''Computes the standard deviation of the time series.

        Returns:
            float: The standard deviation of the time series.'''

        s = 0
        mean = self.mean()
        for i in iter(self):
            s += (mean - i)**2
        return math.sqrt(s / (len(self) - 1))

class TimeSeries(SizedContainerTimeSeriesInterface):
    def __init__(self, time_points, data_points):
        '''Implements the SizedContainerTimeSeriesInterface using Python lists for storage.
            
            Args:
                `time_points` (sequence): A sequence of time points. Must have length equal to `data_points.`
                `data_points` (sequence): A sequence of data points. Must have length equal to `time_points.`
            
            Returns:
                TimeSeries: A time series containing time and data points.'''

        super().__init__(time_points, data_points)
        self._times = list(time_points)
        self._data = list(data_points)

    def __len__(self):
        '''The length of the time series.
        Returns:
           int: The number of elements in the time series.'''

        return len(self._times)

    def __iter__(self):
        '''An iterable over the data points of the time series.
        Returns:
            iterable: An iterable over the data points of the time series.'''

        return iter(self._data)

    def itertimes(self):
        '''Returns an iterator over the TimeSeries times'''
        return iter(self._times)

class ArrayTimeSeries(TimeSeries):

    def __init__(self, time_points, data_points):
        '''Implements the SizedContainerTimeSeriesInterface using NumPy arrays for storage.
            
            Args:
                `time_points` (sequence): A sequence of time points. Must have length equal to `data_points.`
                `data_points` (sequence): A sequence of data points. Must have length equal to `time_points.`
            
            Returns:
                ArrayTimeSeries: A time series containing time and data points.'''

        super().__init__(time_points, data_points)

        self._length = len(time_points)
        self._times = np.empty(self._length * 2)
        self._data = np.empty(self._length * 2)
        self._times[:self._length] = time_points
        self._data[:self._length] = data_points

    def __len__(self):
        return self._length

    def __getitem__(self, key):
        '''Returns the data point from the TimeSeries with index = key'''
        if key >= self._length:
            raise IndexError('ArrayTimeSeries index out of range.')
        return self._data[key]

    def __setitem__(self, key, value):
        '''Sets the data point from the TimeSeries with index = key to value'''
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
    def produce(self)->tuple:
        '''Generate (time, value) tuples'''

    def online_std(self, chunk=1):
        "Online standard deviation"
        def gen():
            n = 0
            mu = 0
            dev_accum = 0
            for i in range(chunk):
                tmp = next(self._gen)
                (time, value) = (tmp[0], tmp[1])
                n += 1
                delta = value - mu
                dev_accum=dev_accum+(value-mu)*(value-mu-delta/n)
                mu = mu + delta/n
                if n==1:
                    stddev = 0
                    yield (time, stddev)
                elif n > 1:
                    stddev = math.sqrt(dev_accum/(n-1))
                    yield (time, stddev)
        return SimulatedTimeSeries(gen())

    def online_mean(self, chunk=1):
        def gen():
            n = 0
            mean = 0
            for x in self.iteritems():
                n += 1
                mean = ((n - 1) * mean + x) / n
                yield mean
        return SimulatedTimeSeries(gen())


class SimulatedTimeSeries(StreamTimeSeriesInterface):
    '''A time series with no internal storage. 
    Yields data from a supplied generator, either with or without times provided.'''


    def __init__(self, generator):
        '''Inits SimulatedTimeSeries with a value or (time,value) generator'''
        try:
            self._gen = iter(generator)
            self._index = 0
        except:
            raise TypeError('Parameter `generator` must be a sequence type.')


    def __iter__(self):
        '''Returns an iterator that gets a new value from produce'''
        return self

    def __next__(self):
        '''An iterator that gets a new data point from produce'''
        return self.produce()[0][1]

    def iteritems(self):
        '''An iterator that gets a new (time,value) tuple from produce'''
        while True:
            yield self.produce()[0]

    def itertimes(self):
        '''An iterator that gets a new time from produce'''
        while True:
            yield self.produce()[0][0]

    def __repr__(self):
        format_str = '{}([{}])'
        class_name = type(self).__name__
        return format_str.format(class_name, str(self._gen))

    def produce(self, chunk = 1):
        '''Generates a list of up to chunk (time, value) tuples. If optional time is not
        provided, adds an integer timestamp (Unix time) to value

        Args:
            chunk (int): the number of tuples produce generates

        Returns:
            list: list of (time, value) tuples.'''

        values = []
        for i in range(chunk):
            value = next(self._gen)
            if type(value) == tuple:
                values.append(value)
            else:
                values.append((int(datetime.datetime.now().timestamp()), value))
        return values
