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
        '''Raises an exception if either parameter is not a sequence
        or if `time_points` and `data_points` are not the same length'''

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
        '''Returns the data point from the TimeSeries with index = key'''
        return self._data[key]

    def __setitem__(self, key, value):
        '''Sets the data point from the TimeSeries with index = key to value'''

        # Raise exception if a value is not a real number
        if not isinstance(value, numbers.Real):
            raise ValueError('`value` must be a real number')
        else:
            self._data[key] = value

    def __repr__(self):
        return str(self)

    def __str__(self):
        '''Prints a more user-friendly interpretation of the SizedContainerTimeSeriesInterface'''

        format_str = '{}([{}])'
        row_str = '[{}\t{}]'
        add_str = ''

        for pts in self.iteritems():
            add_str += row_str.format(pts[0], pts[1])
        class_name = type(self).__name__
        return format_str.format(class_name, add_str)

    def interpolate(self, pts):
        '''Generates new interpolated values for a TimeSeries given unseen times.
        Uses stationary boundary conditions: if a new time point is smaller than the
        first existing time point, returns the first value; likewise for larger time points.
        Args:
            pts: a list of time values to create interpolated points for

        Returns:
            A new TimeSeries with the provided times and their interpolated values.'''
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
        '''Returns the two-norm of the value vector of the TimeSeries'''
        return math.sqrt(sum(x**2 for x in self))

    def __bool__(self):
        '''Checks if the value vector is of length zero. If so, returns false.
        Otherwise returns true.'''
        return bool(abs(self))

    def _check_time_values(function):
        '''A Decorator to check if the rhs is either a TimeSeries with the same
        time values or a real number. If neither, raises an appropriate error'''
        def _check_time_values_helper(self , rhs):
            if isinstance(rhs, numbers.Real):
                return function(self, rhs)
            elif not isinstance(rhs, SizedContainerTimeSeriesInterface):
                raise NotImplementedError
            elif len(self) != len(rhs) or not all(t1 == t2 for t1, t2 in zip(self.itertimes(), rhs.itertimes())):
                raise ValueError('Both time series must have the same time points.')
            return function(self, rhs)
        return _check_time_values_helper

    def __neg__(self):
        # TODO: Create instance of calling class instead of TimeSeries
        return TimeSeries(list(self.itertimes()), [-x for x in iter(self)])

    def __pos__(self):
        # TODO: Create instance of calling class instead of TimeSeries
        return TimeSeries(list(self.itertimes()), list(iter(self)))

    @_check_time_values
    def __eq__(self, other):
        '''Determines if two TimeSeries are equal or if all values of a TimeSeries are
        equal to a real number.
        Args:
            other: either a real number or another TimeSeries. If using another TimeSeries,
            it must have the same time values

        Returns:
            True if all (time,value) tuples of the two TimeSeries are the same, or if all
            values of the TimeSeries are equal to the real number.
            False otherwise.'''

        if isinstance(other, numbers.Real):
            return (all(x == numbers.Real for x in iter(self)))
        else:
            return (all(x == y for x, y in zip(iter(self), iter(other))))

    @_check_time_values
    def __add__(self, other):
        '''Adds either a real number or another TimeSeries to the TimeSeries.
        Args:
            other: either a real number or another TimeSeries. If using another TimeSeries,
            it must have the same time values

        Returns:
            A new TimeSeries with the same times and either an elementwise addition
            with the real number or elementwise addition with the values of the other TimeSeries'''

        if isinstance(other, numbers.Real):
            return TimeSeries(list(self.itertimes()), [x + other for x in iter(self)])
        else:
            return TimeSeries(list(self.itertimes()), [x + y for x, y in zip(iter(self), iter(other))])

    @_check_time_values
    def __sub__(self, other):
        '''Subtracts either a real number or another TimeSeries from the TimeSeries.
        Args:
            other: either a real number or another TimeSeries. If using another TimeSeries,
            it must have the same time values

        Returns:
            A new TimeSeries with the same times and either an elementwise subtraction
            of the real number or elementwise subtraction of the values of the other TimeSeries'''

        if isinstance(other, numbers.Real):
            return TimeSeries(list(self.itertimes()), [x - other for x in iter(self)])
        else:
            return TimeSeries(list(self.itertimes()), [x - y for x, y in zip(iter(self), iter(other))])

    @_check_time_values
    def __mul__(self, other):
        '''Multiplies either a real number or another TimeSeries by the TimeSeries.
        Args:
            other: either a real number or another TimeSeries. If using another TimeSeries,
            it must have the same time values

        Returns:
            A new TimeSeries with the same times and either an elementwise multiplication
            by the real number or elementwise multiplication by the values of the other TimeSeries'''

        if isinstance(other, numbers.Real):
            return TimeSeries(list(self.itertimes()), [x * other for x in iter(self)])
        else:
            return TimeSeries(list(self.itertimes()), [x * y for x, y in zip(iter(self), iter(other))])

    def mean(self):
        return sum(self.itertimes())/len(self)

    def iteritems(self):
        '''Returns an iterator over the TimeSeries times'''
        return iter(zip(self.itertimes(), iter(self)))

    @property
    def lazy(self):
        '''Returns a new LazyOperation instance using an identity function
        and self as the only argument. This wraps up the TimeSeries instance
        and a function which does nothing and saves them both for later.'''
        return LazyOperation(lambda x: x, self)

    def std(self):
        '''Returns the standard deviation of the TimeSeries

        Returns:
            The standard deviation as a float'''
        s = 0
        mean = np.mean(list(iter(self)))
        for i in iter(self):
            s += (mean - i)**2
        return math.sqrt(s / len(self))

class TimeSeries(SizedContainerTimeSeriesInterface):
    def __init__(self, time_points, data_points):
        '''Inits a TimeSeries with time_points and data_points.
        Stores these as lists.'''
        super().__init__(time_points, data_points)
        self._times = list(time_points)
        self._data = list(data_points)

    def __len__(self):
        return len(self._times)

    def __iter__(self):
        '''Returns an iterator over the TimeSeries values'''
        return iter(self._data)

    def itertimes(self):
        '''Returns an iterator over the TimeSeries times'''
        return iter(self._times)

class ArrayTimeSeries(TimeSeries):

    def __init__(self, time_points, data_points):
        '''Inits a TimeSeries with time_points and data_points.
        Stores these as numpy arrays with extra space in the length of
        the provided arrays.'''

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
        def gen():
            "Online standard deviation"
            n = 0
            mu = 0
            dev_accum = 0
            for i in range(chunk):
                value = next(self._gen)
                n += 1
                delta = value - mu
                dev_accum=dev_accum+(value-mu)*(value-mu-delta/n)
                mu = mu + delta/n
                if n > 1:
                    stddev = math.sqrt(dev_accum/(n-1))
                    yield stddev
            return SimulatedTimeSeries(gen)


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
    '''Creates a Simulated TimeSeries with no internal storage
    that yields data from a supplied generator, either with or
    without times provided'''


    def __init__(self, generator):
        '''Inits SimulatedTimeSeries with a value or (time,value) generator'''
        self._gen = generator

    def __iter__(self):
        '''Returns an iterator that gets a new value from produce'''
        return self

    def __next__(self):
        return next(self.produce())[1]

    def iteritems(self):
        '''Returns an iterator that gets a new (time,value) tuple from produce'''
        yield next(self.produce())

    def itertimes(self):
        '''Returns an iterator that gets a new time from produce'''
        yield next(self.produce())[0]

    def __repr__(self):
        format_str = '{}([{}])'

        class_name = type(self).__name__
        return format_str.format(class_name, str(self._gen))

    def produce(self, chunk=1):
        '''Generates up to chunk (time, value) tuples. If optional time is not
        provided, adds an integer timestamp to value

        Args:
            chunk: the number of tuples produce generates

        Returns:
            chunk # of (time, value) tuples'''

        for i in range(chunk):
            value = next(self._gen)
            if type(value) == tuple:
                yield value
            else:
                yield (int(datetime.datetime.now().timestamp()), value)
