#!/usr/bin/env python3

import numpy as np

class TimeSeries():
    ''' A series of data points indexed by time.'''

    def __init__(self, times, seq):
        '''Creates a TimeSeries using the data points in `seq`.

        Args:
            seq (:obj:`sequence` of `numeric`): A sequence of data points indexed by time.
                Time intervals are assumed to be uniform.

        Example:
            >>> ts = TimeSeries([1, 2, 3, 4])
            >>> ts
            TimeSeries([1,...])
        '''
        # raise an exception if `seq` is not iterable
        try:
            iter(seq)
        except:
            raise TypeError('`seq` must be a sequence')

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
        return iter(self._times[:self._length])

    def iteritems(self):
        '''Returns a tuple (time, value) for each item in the TimeSeries.'''
        return iter(zip(self._times[:self._length], self._data[:self._length]))

    def interpolate(self, interpts):
        times = []
        seq = []
        for i in interpts:
            times = sorted(enumerate(self._times), key=lambda x:abs(x[1]-i))[:2]
            vals = [self._data[times[0][0]], self._data[times[1][0]]]
            new_val = vals[0] + (i-times[0][1])*(vals[1]-vals[0])/(times[1][1]-times[0][1])
            times.append(i)
            seq.append(new_val)
        return TimeSeries(times,seq)

    ##DEFINE __EQ__


class ArrayTimeSeries(TimeSeries):

    def __init__(self, times, seq):
        '''Creates a TimeSeries using the data points in `seq`.
        Internally, this subclass uses a numpy array for storage
        instead of a Python list.

        Args:
            times (:obj:`sequence` of `numeric): A sequence of times,
            each associated with a value of `seq` at same index.

            seq (:obj:`sequence` of `numeric`): A sequence of data
            points associated with corresponding index in `times`.

        Example:
            >>> ts = TimeSeries([1, 2, 3, 4])
            >>> ts
            TimeSeries([1,...])
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

        # _length (int): The TimeSeries length / first empty index in the array
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
            raise IndexError('TimeSeries index out of range.')
        return self._data[key]

    def __setitem__(self, key, value):
        if key >= self._length:
            raise IndexError('TimeSeries index out of range.')
        self._data[key] = value

    def __iter__(self):
        return iter(self._data[:self._length])

    def itertimes(self):
        '''Returns an iterator over the time indices for the TimeSeries.'''
        return iter(self._times[:self._length])

    def iteritems(self):
        '''Returns an iterator over the tuples (time, value) for each item in the TimeSeries.'''
        return iter(zip(self._times[:self._length], self._data[:self._length]))
