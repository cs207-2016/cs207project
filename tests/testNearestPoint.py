import os, sys
curr_dir = os.getcwd().split('/')
print(curr_dir)
sys.path.append('/'.join(curr_dir))
ts_dir = curr_dir
ts_dir.append('timeseries')
sys.path.append('/'.join(ts_dir))

import numpy as np
from timeseries.timeseries import TimeSeries
from tsbtreedb.correlation import correlation
from tsbtreedb.generateTS import generate_ts
from tsbtreedb.generateDB import generateDB
from tsbtreedb.similarity import vp_similarity_search
from pytest import raises

'''
run 'py.test' to run this test file.
'''
def test_random_ts():
    ts1 = correlation.random_ts(2)
    ts2 = correlation.random_ts(3)
    standts1 = correlation.stand(ts1, ts1.mean(), ts1.std())
    standts2 = correlation.stand(ts2, ts2.mean(), ts2.std())
    idx, mcorr = correlation.max_corr_at_phase(standts1, standts2)
    assert idx<100 and idx>-1

def test_similarity():
    num_ts = 50
    num_vp = 20
    generate_ts(num_ts)
    #with raises(Exception):
    generateDB(num_ts, num_vp)
    #curr_dir = os.getcwd().split('/')
    #print(curr_dir)

    file_name = 'vp_origin_idx.dat'
    vantage_point_index_list = np.loadtxt(file_name, delimiter = ',')
    x = np.loadtxt('tsfiles/ts_1.dat', delimiter = ',')  #####
    query_ts = TimeSeries(x[:, 0], x[:, 1])

    nearest_ts = vp_similarity_search(query_ts, list(vantage_point_index_list))
    #print(nearest_ts)
    assert len(nearest_ts) == 10 and nearest_ts[0] == 'ts_1'

#if __name__ == "__main__":
#    test_similarity()
