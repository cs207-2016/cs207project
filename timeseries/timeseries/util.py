import os, sys
import numpy.fft as nfft
import numpy as np
#below is your module. Use your ListTimeSeries or ArrayTimeSeries..
from scipy.stats import norm
from .timeseries import *
from ..rbtree import *


'''

Util Functions for Similarity Search Between Timeseries

'''


def genTS(nTS = 1000):
    '''
    Script1: Generate 1000 TS in website/tsdata folder
    '''
    for i in range(nTS):
        file_path = 'website/tsdata/ts'+str(i)+'.dat'
        fp = open(file_path,'w+')
        m = np.random.random()
        s = np.random.random()
        t1 = tsmaker(m, s, 0.01)
        np.savetxt(file_path,np.transpose(np.array([list(t1.itertimes()),list(t1)])), delimiter=' ')

def genDB(nTS = 1000, nDB = 20):
    '''
    Script2: Generate 20 databases in website/tsdb
    '''
    indexes = np.random.choice(nTS,nDB, replace = False)
    print("### Vantage Indx Pts ###")
    print(indexes)
    vantagePtList= []
    dbList = []

    #Create TS Referencing
    #The nDB randomally selected vantagePtFiles
    for j in range(nDB):
    	fileName = 'website/tsdata/ts'+str(indexes[j])+'.dat'
    	dbName = "website/tsdb/db"+str(j)+".dbdb"
    	x = np.loadtxt(fileName, delimiter=' ')
    	vantagePt = TimeSeries(x[:,0],x[:,1])
    	vantagePtList.append(vantagePt)
    	##Remove DB if it has previously been created
    	if os.path.exists(dbName):
    			 os.remove(dbName)

    	# Connect to Databses
    	db = connect(dbName)
    	dbList.append(db)

    #For all nDB Databases
    #Loop through nTS TimeSeries
    #Add Key = Distance(vantagePt, comparePt)
    #Value = comparePT's fileName
    for i in range(nTS):
    	fileName = 'website/tsdata/ts'+str(i)+'.dat'
    	x = np.loadtxt(fileName, delimiter=' ')
    	comparePt = TimeSeries(x[:,0],x[:,1])

    	# Add Key,Value for ComparePt for all nDB Databases
    	for j in range(nDB):
    		dist = 2*(1-kernel_corr(vantagePtList[j],comparePt))
    		dbList[j].set(dist, fileName)

    #Commit and Close Databases
    for j in range(nDB):
    	dbList[j].commit()
    	dbList[j].close()

def genSIM(filename, nDB = 20):
    '''
    Script3a: Find Nearest TS to TS passed in filename
    '''
    # Load in the TS to Evaluate
    x = np.loadtxt(filename, delimiter=' ')
    origTs = TimeSeries(x[:,0],x[:,1])
    time = np.arange(0.0, 1.0, 0.01)
    testTs = origTs.interpolate(time)

    # Find the Nearest vantagePt
    minDist = float('inf')
    for j in range(nDB):
        dbName = "website/tsdb/db"+str(j)+".dbdb"
        db = connect(dbName)
        vantagePtFile = db.get(0)
        x = np.loadtxt(vantagePtFile, delimiter=' ')
        comparePt = TimeSeries(x[:,0],x[:,1])
        dist = 2*(1-kernel_corr(comparePt,testTs))
        if dist < minDist:
            minDist = dist
            minDbName = dbName
            minVantagePtFile = vantagePtFile
        db.close()

    #Connect to DB Referencing the Nearest vantagePT
    db = connect(minDbName)
    keys, filenames = db.get_All_LTE(float(2)*minDist)
    nFiles = len(filenames)
    print("### Number of TS to Review ###")
    print(nFiles)

    #Dictionary Key File, Val = Distance to testTs
    distDict = {}

    #Get dist between testTs and all TS within key below 2*minDist
    for i in range(nFiles):
        x = np.loadtxt(filenames[i], delimiter=' ')
        comparePt = TimeSeries(x[:,0],x[:,1])
        dist = 2*(1-kernel_corr(comparePt,testTs))
        #dist = random.random()
        distDict[filenames[i]] = dist

    ## Commented out these prints that return up to 10 of the nearest TS
    ## Print 10 Nearest Distances (Assuming you have reviewed at least 10 TS)
    ## print(sorted(distDict.values())[:10])
    ## Print 10 nearest TS FIles (Assuming you have reviewed at least 10 TS)
    ## print(sorted(distDict, key=distDict.__getitem__)[:10])

    db.close()
    ## Return Nearest Timeseries
    nearest = sorted(distDict, key=distDict.__getitem__)[0]
    print("#### Nearest Timeseries ####")
    print(nearest)
    file_path = 'website/results/results.txt'
    text_file = open(file_path, "w")
    text_file.write(nearest)
    text_file.close()

def genSIM_N(filename, nSim = 5, nDB = 20):
    '''
    Script3b: Find N (nSim) Nearest TS to TS passed in filename
    '''
    # Load in the TS to Evaluate
    if nSim > nDB:
        raise KeyError('Must Hold: nSim <= nDB')

    x = np.loadtxt(filename, delimiter=' ')
    origTs = TimeSeries(x[:,0],x[:,1])
    time = np.arange(0.0, 1.0, 0.01)
    testTs = origTs.interpolate(time)

    #Dictionary Key DB, Val = Distance to testTs
    VPdistDict = {}

    # Find the Nearest vantagePt
    for j in range(nDB):
        dbName = "website/tsdb/db"+str(j)+".dbdb"
        db = connect(dbName)
        vantagePtFile = db.get(0)
        x = np.loadtxt(vantagePtFile, delimiter=' ')
        comparePt = TimeSeries(x[:,0],x[:,1])
        dist = 2*(1-kernel_corr(comparePt,testTs))
        VPdistDict[dbName] = dist
        db.close()

    # By Chosing the nSim closest VantagePt, we guarrantee to find nSim Closest TS
    dbName = sorted(VPdistDict, key=VPdistDict.__getitem__)[nSim - 1]
    dist = sorted(VPdistDict.values())[nSim - 1]

    #Connect to DB Referencing the Nearest vantagePT
    db = connect(dbName)
    keys, filenames = db.get_All_LTE(float(2)*dist)
    nFiles = len(filenames)
    print("### Number of TS to Review ###")
    print(nFiles)

    #Dictionary Key File, Val = Distance to testTs
    distDict = {}

    #Get dist between testTs and all TS within key below 2*minDist
    for i in range(nFiles):
        x = np.loadtxt(filenames[i], delimiter=' ')
        comparePt = TimeSeries(x[:,0],x[:,1])
        dist = 2*(1-kernel_corr(comparePt,testTs))
        #dist = random.random()
        distDict[filenames[i]] = dist

    db.close()
    ## Return nSim Nearest Timeseries
    nearest = sorted(distDict, key=distDict.__getitem__)[:nSim]
    print("#### Nearest Timeseries ####")
    print(nearest)
    file_path = 'website/results/results.txt'
    text_file = open(file_path, "w")
    for item in nearest:
        text_file.write("%s\n" % item)
    text_file.close()


def tsmaker(m, s, j):
    '''Generate TS from Normal PDF with mean m and stand s

    Args:
    m: Mean of Normal PDF
    s: Standard deviation of Normal PDF
    j: Random Mulitplier

    Output:
    A timeseries from Normal PDF with mean m and stand s
    '''
    t = np.arange(0.0, 1.0, 0.01)
    v = norm.pdf(t, m, s) + j*np.random.randn(100)
    return TimeSeries(t,v)

def random_ts(a):
    '''Generate TS from random uniform distribution

    Args:
    a: Random Mulitplier

    Output:
    A timeseries from 0,1 Uniform Distribution * a mulitplier
    '''
    t = np.arange(0.0, 1.0, 0.01)
    v = a*np.random.random(100)
    return TimeSeries(t,v)

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
    '''given two standardized time series, compute their cross-correlation using FFT

    Args:
    ts1, ts2: Timeseries whose correlation has to be checked

    Output: Value of dot product of the timeseries for different shifts of the second timeseries

    '''
    f1 = nfft.fft(list(iter(ts1)))
    f2 = nfft.fft(np.flipud(list(iter(ts2))))
    cc = np.real(nfft.ifft(f1 * f2))/(abs(ts1)*abs(ts2))
    return cc

# this is just for checking the max correlation with the
#kernelized cross-correlation
def max_corr_at_phase(ts1, ts2):
    '''Calculates the maximum value of the correlation for different shifts

    Args:
    ts1, ts2: Timeseries whose correlation is to be calculated

    Output:
    idx: Index of maximum correlation
    maxcorr: Value of maximum correlation'''
    ccorts = ccor(ts1, ts2)
    idx = np.argmax(ccorts)
    maxcorr = ccorts[idx]
    return idx, maxcorr

#The equation for the kernelized cross correlation is given at
#http://www.cs.tufts.edu/~roni/PUB/ecml09-tskernels.pdf
#normalize the kernel there by np.sqrt(K(x,x)K(y,y)) so that the correlation
#of a time series with itself is 1. We'll set the default multiplier to 1.
def kernel_corr(ts1, ts2, mult=1):
    '''Kernelized correlation calculated with an exponential kernel. The correlation value may be slightly greater than 1 due to precision issues in the calculation

    Args:
    ts1, ts2: Timeseries whose correlation is to be caluclated
    mult: Kernel constant

    Output:
    Value of the correlation as a float'''
    #your code here.
    ccorts = ccor(ts1, ts2)
    cc1 = ccor(ts1, ts1)
    cc2 = ccor(ts2, ts2)
    exp_ccorts = np.exp(mult*ccorts)
    exp_ts1 = np.exp(mult*cc1)
    exp_ts2 = np.exp(mult*cc2)
    return sum(exp_ccorts)/np.sqrt(sum(exp_ts1)*sum(exp_ts2))
