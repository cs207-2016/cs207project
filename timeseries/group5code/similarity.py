import os, sys

curr_dir = os.getcwd().split('/')
sys.path.append('/'.join(curr_dir[:-1]))
ts_dir = curr_dir[:-1]
ts_dir.append('timeseries')
sys.path.append('/'.join(ts_dir))

import numpy as np
from tsbtreedb.generateTS import generate_ts
from tsbtreedb.correlation import correlation
from tsbtreedb import lab10
from timeseries.timeseries import TimeSeries

'''
This file includes a function called vp_similarity_search to find 10 nearest time
series to the query time series.

How to run:
first import this file
then call 'vp_similarity_search(query_ts, vantage_point_index_list)' to return a
list of 10 nearest time series names.

Requires folders:
tsfiles, tsdb

Requires files:
vp_origin_idx.dat
'''


def vp_similarity_search(query_ts, vantage_point_index_list):  # vantage_point_list should be a file
    # def _vp_similarity_search(query_ts_key, ts_dict, vp_dict):
    '''
    Find a list of 10 nearest time series to the query time series.
    1. get distances from query time series to all vantage points
    2. define the circle radius to be 2 times the distance between the query time series
    and each vantage point
    3. find relative index of time series within each radius distance
    4. calculate distance to all time series within the radius
    5. find 10 closest time series and return the index of the time series
    Param:
      query_ts : TimeSeries, the query time series that we want to find the 10
      nearest time series to it
      vantage_point_index_list : list, a list of indices of the 20 vantage points
    Return:
      list, a list of 10 time series names that are the nearest 10 time series
      to the query time series.
    '''
    # step 1: get distances from query time series to all vantage points
    query_vp_dist = []
    for i in range(len(vantage_point_index_list)):
        file_name = 'tsfiles/ts_' + str(int(vantage_point_index_list[i])) + '.dat'  # get the 20 vp files
        x = np.loadtxt(file_name, delimiter=',')  #####
        vantage_point = TimeSeries(x[:, 0], x[:, 1])
        query_vp_dist.append(correlation.kernel_corr_dist(query_ts, vantage_point, 10))

    # step 2: define circle radius as 2 times the distance to each vantage point
    radius = [2 * i for i in query_vp_dist]
    # print (radius)

    # step 3: find relative index of time series within each radius distance
    vp_less_dict = {}
    for i in range(20):
        dbName = "tsdb/db_" + str(i) + ".dbdb"
        db = lab10.connect(dbName)
        # keys, values = db.getAll_LTE(radius)
        keys = db.find_all_smaller(radius[i])
        vp_less_dict[i] = keys
    # print('keys',vp_less_dict)

    # step 4: calculate distance to all time series within the radius
    distance = {}
    for ts_list in list(vp_less_dict.values()):
        for tree_name in ts_list:
            # print(tree_name)
            file_name = 'tsfiles/' + tree_name + '.dat'
            x = np.loadtxt(file_name, delimiter=',')
            compare_ts_point = TimeSeries(x[:, 0], x[:, 1])
            dist = correlation.kernel_corr_dist(query_ts, compare_ts_point, 10)
            distance[tree_name] = dist

    # step 5: find 10 closest time series and return the index of the time series
    # find 10 nearest timeseries
    dist_list = list(distance.items())
    # print(dist_list)
    nearest_ts_tuple = sorted(distance.items(), key=lambda dist: dist[1])[:10]
    # print(nearest_ts_tuple)
    # nearest_ts_tuple = [(tree_name, dist),...]
    return [item[0] for item in nearest_ts_tuple]


if __name__ == "__main__":
    file_name = 'vp_origin_idx.dat'
    vantage_point_index_list = np.loadtxt(file_name, delimiter=',')
    # print(vantage_point_index_list)
    # vantage_point_index_list = [3,33,21,5,11,8,28,13,46,34,23,32,0,49,19,27,37,24,44,2]
    x = np.loadtxt('tsfiles/ts_1.dat', delimiter=',')  #####
    query_ts = TimeSeries(x[:, 0], x[:, 1])

    nearest_ts = vp_similarity_search(query_ts, list(vantage_point_index_list))
    print('10 nearest time series:', nearest_ts)
