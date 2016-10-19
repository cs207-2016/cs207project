#!/usr/bin/env python3

import numpy as np

class TimeSeries():
    ''' A series of data points indexed by time.'''
    
    def __init__(self, seq):
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

        self._data = np.array(seq)

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
        times = range(len(self._data))
        return iter(times)
    
    def iteritems(self):
        '''Returns a tuple (time, value) for each item in the TimeSeries.'''
        times = range(len(self._data))
        return iter(zip(times, self._data))

class ArrayTimeSeries(TimeSeries):
    
    def __init__(self, seq):
        '''Creates a TimeSeries using the data points in `seq`.
        Internally, this subclass uses a numpy array for storage
        instead of a Python list.

        Args:
            seq (:obj:`sequence` of `numeric`): A sequence of data 
            points indexed by time. Time intervals are assumed to be uniform.

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
            
        # _length (int): The TimeSeries length / first empty index in the array
        self._length = len(seq)

        # Initialize array to twice the length of the sequence
        self._data = np.empty(len(seq) * 2)
        self._data[:self._length] = seq
       
    def __len__(self):
        return self._length

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
        return iter(range(self._length))
    
    def iteritems(self):
        '''Returns an iterator over the tuples (time, value) for each item in the TimeSeries.'''
        times = range(self._length)
        return iter(zip(times, self._data[:self._length]))        
