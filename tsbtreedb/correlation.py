import os, sys
curr_dir = os.getcwd().split('/')
sys.path.append('/'.join(curr_dir[:-1]))
ts_dir = curr_dir[:-1]
ts_dir.append('timeseries')
sys.path.append('/'.join(ts_dir))

import numpy.fft as nfft
import numpy as np
from timeseries.timeseries import TimeSeries
from scipy.stats import norm


def tsmaker(m, s, j):
    '''
    Generate a time series with 100 time-value points. The time of the time series
    are 100 equally spaced values between 0 and 1. The values of the time series
    are 100 values generated from a normal distribution with mean s and standard
    deviation s and random noises from 0 and j.
    Param:
      m : float, the time series values' mean
      s : float, the time series values' standard deviation
      j : float, the multiplicative constant to generate noises
    Return:
      TimeSeries, a time series with 100 time-value points
    '''
    t = np.arange(0.0, 1.0, 0.01)
    v = norm.pdf(t, m, s) + j*np.random.randn(100)
    #return meta, ts.TimeSeries(t, v)
    return TimeSeries(t, v)


def random_ts(a):
    '''
    Randomly generate a time series with 100 time-value points. The time of the time series
    are 100 equally spaced values between 0 and 1. The values of the time series
    are 100 randomly generated values between 0 and a.
    Param:
      a: int, a multiplicative constant to generate 100 values for the time series
    Return:
      A time series with 100 time-value points
    '''
    t = np.arange(0.0, 1.0, 0.01)
    v = a*np.random.random(100)
    #return ts.TimeSeries(t, v)
    return TimeSeries(t, v)


def stand(x, m, s):
    '''
    Standardize a variable x, using its mean m and its standard deviation s.
    Param:
      x : TimeSeries, the time series variable to standardize
      m : float, the time series values' mean
      s : float, the time series values' standard deviation
    Return:
      The standardized time series.
    '''
    time = x._times
    value = x._data
    for i in range(len(value)):
        value[i] = (value[i]-m)/float(s)
    return TimeSeries(time, value)
    #return (x-m)/s


def ccor(ts1, ts2):
    '''
    Given two standardized time series, compute their cross-correlation using
    fast fourier transform. Assume that the two time series have the same length"
    Param:
      ts1 : TimeSeries, the first standardized time series
      ts2 : TimeSeries, the second standardized time series
    Returns:
      float, the two time series' cross-correlation.
    '''
    #your code here
    result = nfft.fft(nfft.ifft(ts1._data) * np.conj(nfft.ifft(ts2._data)))
    return np.real(result)


def max_corr_at_phase(ts1, ts2):
    '''
    Given two standardized time series, find the time at which the two time series'
    cross-correlation is maximized, as well as the cross-correlation itself
    at that point.
    Param:
      ts1 : TimeSeries, the first standardized time series
      ts2 : TimeSeries, the second standardized time series
    Returns:
      idx, maxcorr : int, float
      Tuple of the time at which cross-correlation is maximized, and the
      cross-correlation at that point.
    '''
    ccorts = ccor(ts1, ts2)
    idx = np.argmax(ccorts)
    maxcorr = ccorts[idx]
    return idx, maxcorr

#The equation for the kernelized cross correlation is given at
#http://www.cs.tufts.edu/~roni/PUB/ecml09-tskernels.pdf
#normalize the kernel there by np.sqrt(K(x,x)K(y,y)) so that the correlation
#of a time series with itself is 1.


def kernel_corr(ts1, ts2, mult = 1):
    '''
    Given two standardized time series, compute a kernelized correlation so that
    we can get a real distance. The kernel is normalized so that
    the cross-correlation of a time series with itself is 1.
    Reference: http://www.cs.tufts.edu/~roni/PUB/ecml09-tskernels.pdf
    Param:
    ts1 : TimeSeries: the first standardized time series
    ts2 : TimeSeries: the second standardized time series
    mult : int, multiplicative constant in the kernel correlation
    Returns: float: kernel correlation between two time series.
    '''
    #your code here.
    k_11 = np.sum(np.exp(mult * ccor(ts1,ts1)))
    k_22 = np.sum(np.exp(mult * ccor(ts2,ts2)))
    return np.sum(np.exp(mult * ccor(ts1,ts2))) / np.sqrt(k_11*k_22)

def kernel_corr_dist(ts1, ts2, mult = 1):
    '''
    Given two standardized time series, compute a distance between the two time
    series. If the kernel correlation of the two time series is one, then the distance
    between them is zero. If the kernel correlation of the two time series is
    negative one, then the distance between them is maximized.
    Param:
    ts1 : TimeSeries: the first standardized time series
    ts2 : TimeSeries: the second standardized time series
    mult : int, multiplicative constant in the kernel correlation
    Returns: float, distance between two time series.
    '''
    return 2 * (1 - kernel_corr(ts1, ts2, mult))

#this is for a quick and dirty test of these functions
#you might need to add procs to pythonpath for this to work
if __name__ == "__main__":
    print("HI")
    t1 = tsmaker(0.5, 0.1, 0.01)
    t2 = tsmaker(0.5, 0.1, 0.01)
    print(t1.mean(), t1.std(), t2.mean(), t2.std())
    import matplotlib.pyplot as plt
    plt.plot(t1)
    plt.plot(t2)
    plt.show()
    standts1 = stand(t1, t1.mean(), t1.std())
    standts2 = stand(t2, t2.mean(), t2.std())

    idx, mcorr = max_corr_at_phase(standts1, standts2)
    print(idx, mcorr)
    sumcorr = kernel_corr(standts1, standts2, mult=10)
    print(sumcorr)
    t3 = random_ts(2)
    t4 = random_ts(3)
    plt.plot(t3)
    plt.plot(t4)
    plt.show()
    standts3 = stand(t3, t3.mean(), t3.std())
    standts4 = stand(t4, t4.mean(), t4.std())
    idx, mcorr = max_corr_at_phase(standts3, standts4)
    print(idx, mcorr)
    sumcorr = kernel_corr(standts3, standts4, mult=10)
    print(sumcorr)
