import os, sys
curr_dir = os.getcwd().split('/')
print(curr_dir)
sys.path.append('/'.join(curr_dir))
ts_dir = curr_dir
ts_dir.append('timeseries')
sys.path.append('/'.join(ts_dir))

import numpy as np
from timeseries.timeseries import TimeSeries
from tsbtreedb.correlation import stand, kernel_corr_dist
from tsbtreedb.generateTS import generate_ts
from tsbtreedb.generateDB import generateDB
from tsbtreedb import lab10
#from tsbtreedb.similarity import similarity
from pytest import raises


def test_similarity():
    num_ts = 50
    num_vp = 20
    generateDB(num_ts, num_vp)
    curr_dir = os.getcwd().split('/')
    print(curr_dir)
    file_name = 'vp_origin_idx.dat'
    vantage_point_index_list = np.loadtxt(file_name, delimiter = ',')

if __name__ == "__main__":
    test_similarity()
