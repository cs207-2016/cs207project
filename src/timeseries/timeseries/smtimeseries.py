#!/usr/bin/env python3

from .helpers import *
from .interfaces import *
from .storagemanager import *

class SMTimeSeries(SizedContainerTimeSeriesInterface):
    
    _fsm = None

    def __init__(self, time_points=None, data_points=None, ident=None, sm=None):
        '''Implements the SizedContainerTimeSeriesInterface using a StorageManager for storage.
           If no `ident` is supplied, identical time series will receive the same identifier.

            Args:
                `time_points` (sequence): A sequence of time points. Must have length equal to `data_points.`
                `data_points` (sequence): A sequence of data points. Must have length equal to `time_points.`
                `ident` (int or string): An identifier for the time series. 
                                         If it is already in use by the FileStorageManager, the existing SMTimeSeries will be overwritten. 
                                         If not supplied, an identifier will be generated from the hash of the data.
                `sm` (StorageManager): A storage manager to use for underlying storage. 
                                       If not supplied, the class storage manager will be used be default.
                     
            Returns:
                SMTimeSeries: A time series containing time and data points.'''                
        
        if ident is None:
            ident = abs(hash((tuple(time_points), tuple(data_points))))
        else:
            ident = str(ident)
        self._ident = ident
             
        if sm is None:            
            if SMTimeSeries._fsm is None:
                SMTimeSeries._fsm = FileStorageManager()
            self._sm = SMTimeSeries._fsm
        else:
            self._sm = sm
            
        # Only store if we aren't initializing an empty object
        if time_points is not None and data_points is not None:
            self._sm.store(ident, ArrayTimeSeries(time_points, data_points))

    
    @classmethod
    def from_db(cls, ident, fsm=None):
        if fsm is not None:
            SMTimeSeries._fsm = fsm
        if SMTimeSeries._fsm is None:
            SMTimeSeries._fsm = FileStorageManager()
        try:
            ts = SMTimeSeries._fsm.get(ident)
            obj = cls(ident=ident)
        except:
            raise KeyError('No time series found corresponding to {}'.format(ident))
        return obj

    def __len__(self):
        '''The length of the time series.
        Returns:
           int: The number of elements in the time series.'''

        return self._sm.size(self._ident)
    
    def __iter__(self):
        '''An iterable over the data points of the time series.
        Returns:
            iterable: An iterable over the data points of the time series.'''

        return iter(self._sm.get(self._ident))

    def itertimes(self):
        '''Returns an iterator over the TimeSeries times'''
        return self._sm.get(self._ident).itertimes()

    def __sizeof__(self):
        '''Returns the size in bytes of the time series storage.'''
        return sys.getsizeof(self._sm.get(self._ident))