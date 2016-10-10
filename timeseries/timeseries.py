#!/usr/bin/env python3

# Stores a single, ordered set of numerical data
class TimeSeries():

    def __init__(self, seq):

        # raise an exception if `seq` is not a sequence
        try:
            iter(seq)
        except:
            raise TypeError('`seq` must be a sequence')

        self._data = sorted(seq)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        
