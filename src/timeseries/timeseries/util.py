import os, sys
import numpy.fft as nfft
import numpy as np
import re
from scipy.stats import norm

from .storagemanager import FileStorageManager
from .smtimeseries import SMTimeSeries

from rbtree import *

def stand(x, m, s):
    '''Standardize timeseries x by mean m and std deviation s

    Args:
    x: Timeseries that is beign standardized
    m: Mean of the timeseries after standardization
    s: Standard deviation of the timeseries after standardization

    Output:
    A timeseries with mean 0 and standard deviation 1
    '''
    vals = np.array(list(iter(x)))
    vals = (vals - m)/s
    return TimeSeries(list(x.itertimes()),vals)

def ccor(ts1, ts2):
    '''Given two standardized time series, compute their cross-correlation using FFT.

    Args:
        ts1, ts2: Time series whose correlation has to be checked

    Returns: 
        float: The dot product of the timeseries for different shift of `ts2`'''

    f1 = nfft.fft(list(iter(ts1)))
    f2 = nfft.fft(np.flipud(list(iter(ts2))))
    cc = np.real(nfft.ifft(f1 * f2))/(abs(ts1)*abs(ts2))
    return cc

def max_corr_at_phase(ts1, ts2):
    '''Calculates the maximum value of the correlation for different shifts

    Args:
        ts1, ts2: Time series whose correlation is to be calculated

    Returns:
        int: Index of maximum correlation
        float: Value of maximum correlation'''

    ccorts = ccor(ts1, ts2)
    idx = np.argmax(ccorts)
    maxcorr = ccorts[idx]
    return idx, maxcorr

def kernel_corr(ts1, ts2, mult=1):
    '''Kernelized correlation calculated with an exponential kernel. 
    
       The correlation value may be slightly greater than 1 due to precision issues in the calculation

    Args:
        ts1, ts2: Timeseries whose correlation is to be caluclated
        mult: Kernel constant

    Returns:
        float: the correlation'''

    ccorts = ccor(ts1, ts2)
    cc1 = ccor(ts1, ts1)
    cc2 = ccor(ts2, ts2)
    exp_ccorts = np.exp(mult*ccorts)
    exp_ts1 = np.exp(mult*cc1)
    exp_ts2 = np.exp(mult*cc2)
    return sum(exp_ccorts)/np.sqrt(sum(exp_ts1)*sum(exp_ts2))

def generate_timeseries(count, path):
    '''Generates `count` random time series in `path`.'''
    fsm = FileStorageManager(path=path)
    for i in range(count):
        m = np.random.random()
        s = np.random.random()
        times = np.arange(0.0, 1.0, 0.01)
        vals = norm.pdf(times, m, s) + 0.01*np.random.randn(100)
        # This will store the time series data as an .npy file in `path`
        ts = SMTimeSeries(time_points=times, data_points=vals, sm=fsm)

def generate_vantage_points(db_count, timeseries_path, db_path):
    '''Generates `db_count` databases in `db_path` from the time series files in `timeseries_path`.'''

    # Get list of time series files, ensure there are enough
    ts_files = os.listdir(timeseries_path)
    num_ts = len(ts_files)
    if num_ts < db_count: 
        raise Exception('Insufficient number of time series {} to generate {} vantage points'.format(num_ts, db_count))
    
    # Create vantage points from FileStorageManager using `timeseries_path`
    fsm = FileStorageManager(path=timeseries_path)
    vpt_indices = np.random.choice(num_ts, db_count, replace = False)
    vpt_ids = [ts_files[i].strip('.npy') for i in vpt_indices]
    vantage_pts = [SMTimeSeries.from_db(i, fsm) for i in vpt_ids]

    # List of databases
    dbs = [] 
    db_filepath = '{}/db{}.dbdb'

    # Create database files for vantage points
    for i in range(db_count):
        db_filename = db_filepath.format(db_path, str(i))
        # Delete DB file if already exists
        if os.path.exists(db_filename):
            os.remove(db_filename)

    # Connect to database and store
        db = connect(db_filename)
        dbs.append(db)

    # For each db, add distance to each time series in `timeseries_path`
    for i in range(num_ts):
        tsid = ts_files[i].strip('.npy')
        ts = SMTimeSeries.from_db(tsid, fsm)
        for j in range(db_count):
            dist = 2*(1-kernel_corr(vantage_pts[j], ts))
            dbs[j].set(dist, tsid)

    # Commit and close Databases
    for i in range(db_count):
        dbs[i].commit()
        dbs[i].close()

def get_similar_ts(ts, count, timeseries_path, db_path):
    '''Returns the `count` most similar time series to ts.'''

    db_files = os.listdir(db_path)

    # Load in the TS to Evaluate
    if count > len(db_files):
        raise KeyError('There must be more vantage points than similar time series.')
    
    fsm = FileStorageManager(path=timeseries_path)

    # Interpolate time series
    time = np.arange(0.0, 1.0, 0.01)
    ts = ts.interpolate(time)

    closest_dist = None
    closest_vp_db = None # The db with the closest vantage point

    # Find the Nearest vantagePt
    for i in range(len(db_files)):
        db_file = '{}/{}'.format(db_path, db_files[i]) 
        db = connect(db_file)
        vpt_id = db.get(0)
        vpt_ts = SMTimeSeries.from_db(vpt_id, fsm)
        dist = 2*(1-kernel_corr(vpt_ts, ts))
        if closest_dist is None or dist < closest_dist:
            closest_dist = dist
            closest_vp_db = db_file
        db.close()

    # Connect to DB with closest vantage point
    db = connect(closest_vp_db)
    dists, ids = db.get_All_LTE(float(2)*closest_dist)

    #Dictionary Key File, Val = Distance to testTs
    distDict = {}

    #Get dist between testTs and all TS within key below 2*minDist
    for i in range(len(ids)):
        compare_ts = SMTimeSeries.from_db(ids[i], fsm)
        dist = 2*(1-kernel_corr(compare_ts, ts))
        distDict[ids[i]] = dist
    db.close()

    # Get `count` nearest ids and return
    nearest = sorted(distDict, key=distDict.__getitem__)[:count]
    return nearest

def get_similar_ts_by_id(tsid, count, timeseries_path, db_path):
    fsm = FileStorageManager(path=timeseries_path)
    ts = SMTimeSeries.from_db(tsid, fsm)
    return get_similar_ts(ts, count, timeseries_path, db_path)