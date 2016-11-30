import os, sys
curr_dir = os.getcwd().split('/')
sys.path.append('/'.join(curr_dir[:-1]))
ts_dir = curr_dir[:-1]
ts_dir.append('timeseries')
sys.path.append('/'.join(ts_dir))

from timeseries.timeseries import TimeSeries
import numpy as np
from tsbtreedb.correlation import tsmaker, stand, kernel_corr
import os
import shutil

def generate_ts(num_of_ts = 50):
    '''
    Generate a set of time series, and each time series has 100 time-value points.
    The mean of each time series values is a number uniformly chosen from 0 and 1.
    The standard deviation of each time series values is a number uniformly chosen
    form 0.05 and 0.4. The jitter of each time series is a number unifromly chosen
    from 0.05 and 0.2.
    Run 'python generate_ts.py 1000' to generate 1000 time series in the directory
    '/tsfile', with each time series stored in a dat file.
    Param:
      num_ts: int, the number of time series that shoule be generated
    Return:
      ts_dict: dict, a dictionary stores each generated time series as well as a
      self-generated index
    '''
    # generate sample time series
    num_ts = int(num_of_ts)
    print(type(num_ts))
    mus = np.random.uniform(low=0.0, high=1.0, size=num_ts)
    sigs = np.random.uniform(low=0.05, high=0.4, size=num_ts)
    jits = np.random.uniform(low=0.05, high=0.2, size=num_ts)

    # initialize dictionaries for time series and their metadata
    primary_keys = []
    ts_dict = {}
    #meta_dict = {}

    # fill dictionaries with randomly generated entries for database
    for i, m, s, j in zip(range(num_ts), mus, sigs, jits):
        tsrs = tsmaker(m, s, j)  # generate data
        pk = "ts_{}".format(i)  # generate primary key
        #print (pk)
        primary_keys.append(pk) # keep track of all primary keys
        ts_dict[pk] = tsrs  # store time series data
    #print ('tsdict', tsdict)

    i = 0
    directory = "tsfiles"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for key in sorted(ts_dict.keys()):
        #print (key)
        ts = ts_dict[key]
        time = ts._times
        value = ts._data

        file_name = "tsfiles/"+key+".dat"
        #print (file_name)
        try:
            f = open(file_name, 'w')
        except IOError, (errno, strerror):
            print "I/O error(%s): %s" % (errno, strerror)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        #    raise

        for j in range(len(time)):
            f.write(str(time[j]))
            f.write(',')
            f.write(str(value[j]))
            f.write('\n')
        f.close()
        i += 1

    return ts_dict


if __name__ == "__main__":
    num_ts = sys.argv[1]
    #print(num_ts)
    ts_dict = generate_ts(num_ts)
