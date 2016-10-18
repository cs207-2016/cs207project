#!/usr/bin/env python3

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

        self._data = list(seq)

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
