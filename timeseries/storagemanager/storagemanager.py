import abc
import numpy as np
import os, os.path
import sys

from ..timeseries.interfaces import SizedContainerTimeSeriesInterface
from ..timeseries.timeseries import ArrayTimeSeries

class StorageManagerInterface(abc.ABC):
    '''An interface for managing persistent storage of time series under an identifier.'''
    
    @abc.abstractmethod
    def store(ident, ts) -> SizedContainerTimeSeriesInterface:
        '''Store time series `ts` associated with id `ident.`'''

    @abc.abstractmethod
    def size(ident) -> int:
        '''Return size of time series associated with id `ident`.'''

    @abc.abstractmethod
    def get(ident) -> SizedContainerTimeSeriesInterface:
        '''Return time series associated with id `ident`.'''

class FileStorageManager(StorageManagerInterface):
    '''Manages time series storage. 
    Underlying on-disk representation for a time series is a single npy file containing an array containing two arrays, one for data, the other for time points. 
    The user executing the script must have r/w permissions for the storage directory.'''
    
    def __init__(self, path='/tmp/smdata', max_cache_size=4.0):
        '''Create a new FileStorageManager.
        Args:
            `path` (string): The path to the file storage directory. Must have r/w permissions.        This constructor will attempt to create the directory if it does not exist.
            `cache_size` (float): The size in MB of the time series cache.'''

        # Create storage directory if it does not exist
        # TODO: Handle exception? Test.
        if not os.path.exists(path):
            os.makedirs(path)
        self._storage = path

        # Cache time series within a dict.
        self._cache = {}
        # Set maximum cache size
        self._cache_size_max = max_cache_size * 1024
        # Time series order of use for cache trimming. Ordered by decreasing staleness.
        self._cache_order = []
        # Proportion of cache to trim when max size is exceeded.
        self._cache_trim = 0.2
        # Current size of cache
        self._cache_size = 0
        
    def store(self, ident, ts):
        '''Store a time series under an identifier. 
           If the identifier is currently in use, the existing time series will be overwritten.

        Args:
             `ident`(string): The identifier for the time series.
             `ts`(SizedContainerTimeSeriesInterface): The time series to store.'''
        
        fname = '{}/{}.npy'.format(self._storage, str(ident))
        times = np.array(list(ts.itertimes()))
        data = np.array(list(iter(ts)))
        dstore = np.array([times, data])
        np.save(fname, dstore)
        self._cache_store(ident, ts)

    def size(self, ident):
        '''Returns the length of the time series stored under the identifier `ident.`

        Args:
           `ident` (string): The identifier for the time series.

        Raises:
            KeyError: No time series is stored under identifier `ident`.'''
        
        return len(self.get(ident))

    def get(self, ident):
        '''Returns the time series stored under the identifier `ident`.
        
        Args: 
             `ident` (string): The identifier for the time series to retrieve.

        Raises: 
             KeyError: No time series was found under identifier `ident`.'''

        # First try to retrieve from cache
        try:
            ats = self._cache_get(ident)
        # Retrieve from storage if not in cache
        except:
            try:
                fname = '{}/{}.npy'.format(self._storage, ident)
                dstore = np.load(fname)
                ats = ArrayTimeSeries(dstore[0], dstore[1])
                self._cache_store(ident, ats)
            # Raise an exception if identifier not recognized
            except:
                raise KeyError('No time series was found associated with id `{}`'.format(ident))
        
        return ats
      
    def _cache_store(self, ident, ts):
        '''Stores the given time series under the given identifier in the cache.
        This function will clear 'stale' time series from the cache if the cache grows larger than the FileStorageManager's maximum cache size.
        Any existing time series will be overwritten.

        Args:
            `ident` (string): The identifier for the time series.
            `ts` (SizedContainerTimeSeriesInterface): The time series to store.'''
        
        # Add size of time series to the total size of cache
        self._cache_size += sys.getsizeof(ts)

        # If the new size is too large, remove stale time series from cache
        if self._cache_size > self._cache_size_max:
            trimsize = self._cache_trim * self._cache_size_max
            trimmed = 0
            i = 0
            while trimmed < trimsize and i < len(self._cache_order):
                trimmed += sys.getsizeof(self._cache[self._cache_order[i]])
                del self._cache[self._cache_order[0]]
                del self._cache_order[0]
                i += 1
            self._cache_size -= trimmed

        # Store the ts in the cache under the identifier
        self._cache[ident] = ts

        # Delete identifier from cache id list if present
        try:
            del self._cache_order[self._cache_order.index(ident)]
        except:
            pass

        # Add identifier to end of cache id list
        self._cache_order.append(ident)
        
  
    def _cache_get(self, ident):
        '''Returns the time series stored under the given identifier in the cache.

        Args:
            `ident`(string): The identifier for the time series.

        Raises:
             KeyError: No time series was stored in the cache under the identifier `ident`.'''
        
        try:
            ts = self._cache[ident]
        except:
            raise KeyError('No time series was found associated with id `{}`'.format(ident))

        # Move the ts identifier to end of cache order list (it is now 'fresh')
        del self._cache_order[self._cache_order.index(ident)]
        self._cache_order.append(ident)
        
        return ts
