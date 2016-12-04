#!/usr/bin/env python3

import numpy as np
import math
import numbers
import datetime
import sys

from lazy import *
from interfaces import *


class TimeSeries(SizedContainerTimeSeriesInterface):
    def __init__(self, time_points, data_points):
        """Implements the SizedContainerTimeSeriesInterface using Python lists for storage.

            Args:
                `time_points` (sequence): A sequence of time points. Must have length equal to `data_points.`
                `data_points` (sequence): A sequence of data points. Must have length equal to `time_points.`

            Returns:
                TimeSeries: A time series containing time and data points."""

        super().__init__(time_points, data_points)
        self._times = list(time_points)
        self._data = list(data_points)

    def __len__(self):
        """The length of the time series.
        Returns:
           int: The number of elements in the time series."""

        return len(self._times)

    def __iter__(self):
        """An iterable over the data points of the time series.
        Returns:
            iterable: An iterable over the data points of the time series."""

        return iter(self._data)

    def itertimes(self):
        """Returns an iterator over the TimeSeries times"""
        return iter(self._times)

    def __sizeof__(self):
        """Returns the size in bytes of the time series storage."""
        return sys.getsizeof(self.time_points) + sys.getsizeof(self.data_points)


class ArrayTimeSeries(TimeSeries):
    def __init__(self, time_points, data_points):
        """Implements the SizedContainerTimeSeriesInterface using NumPy arrays for storage.

            Args:
                `time_points` (sequence): A sequence of time points. Must have length equal to `data_points.`
                `data_points` (sequence): A sequence of data points. Must have length equal to `time_points.`

            Returns:
                ArrayTimeSeries: A time series containing time and data points."""

        super().__init__(time_points, data_points)

        self._length = len(time_points)
        self._times = np.empty(self._length * 2)
        self._data = np.empty(self._length * 2)
        self._times[:self._length] = time_points
        self._data[:self._length] = data_points

    def __len__(self):
        return self._length

    def __getitem__(self, key):
        """Returns the data point from the TimeSeries with index = key"""
        if key >= self._length:
            raise IndexError('ArrayTimeSeries index out of range.')
        return self._data[key]

    def __setitem__(self, key, value):
        """Sets the data point from the TimeSeries with index = key to value"""
        if key >= self._length:
            raise IndexError('ArrayTimeSeries index out of range.')
        self._data[key] = value

    def __iter__(self):
        return iter(self._data[:self._length])

    def itertimes(self):
        """Returns an iterator over the time indices for the ArrayTimeSeries."""
        return iter(self._times[:self._length])

    def iteritems(self):
        """Returns an iterator over the tuples (time, value) for each item in the ArrayTimeSeries."""
        return iter(zip(self._times[:self._length], self._data[:self._length]))

    def __sizeof__(self):
        """Returns the size in bytes of the time series storage."""
        return sys.getsizeof(self._times) + sys.getsizeof(self._data)


class StreamTimeSeriesInterface(TimeSeriesInterface):
    """Creates an interface for a Timeseries with no internal storage that
    yields data based on a generator """

    @abc.abstractmethod
    def produce(self) -> tuple:
        """Generate (time, value) tuples"""

    def online_std(self, chunk=1):
        """Online standard deviation"""

        def gen():
            n = 0
            mu = 0
            dev_accum = 0
            for i in range(chunk):
                tmp = next(self._gen)
                (time, value) = (tmp[0], tmp[1])
                n += 1
                delta = value - mu
                dev_accum += (value - mu) * (value - mu - delta / n)
                mu += delta / n
                if n == 1:
                    stddev = 0
                    yield (time, stddev)
                elif n > 1:
                    stddev = math.sqrt(dev_accum / (n - 1))
                    yield (time, stddev)

        return SimulatedTimeSeries(gen())

    def online_mean(self, chunk=1):
        """Online mean"""

        def gen():
            n = 0
            mu = 0
            for i in range(chunk):
                tmp = next(self._gen)
                (time, value) = (tmp[0], tmp[1])
                n += 1
                delta = value - mu
                mu += delta / n
                yield (time, mu)

        return SimulatedTimeSeries(gen())


class SimulatedTimeSeries(StreamTimeSeriesInterface):
    """A time series with no internal storage.
    Yields data from a supplied generator, either with or without times provided."""

    def __init__(self, generator):
        """Inits SimulatedTimeSeries with a value or (time,value) generator"""
        try:
            self._gen = iter(generator)
            self._index = 0
        except:
            raise TypeError('Parameter `generator` must be a sequence type.')

    def __iter__(self):
        """Returns an iterator that gets a new value from produce"""
        return self

    def __next__(self):
        """An iterator that gets a new data point from produce"""
        return self.produce()[0][1]

    def iteritems(self):
        """An iterator that gets a new (time,value) tuple from produce"""
        while True:
            yield self.produce()[0]

    def itertimes(self):
        """An iterator that gets a new time from produce"""
        while True:
            yield self.produce()[0][0]

    def __repr__(self):
        format_str = '{}([{}])'
        class_name = type(self).__name__
        return format_str.format(class_name, str(self._gen))

    def produce(self, chunk=1):
        """Generates a list of up to chunk (time, value) tuples. If optional time is not
        provided, adds an integer timestamp (Unix time) to value

        Args:
            chunk (int): the number of tuples produce generates

        Returns:
            list: list of (time, value) tuples."""

        values = []
        for i in range(chunk):
            value = next(self._gen)
            if type(value) == tuple:
                values.append(value)
            else:
                values.append((int(datetime.datetime.now().timestamp()), value))
        return values
