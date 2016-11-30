import os, sys
curr_dir = os.getcwd().split('/')
sys.path.append('/'.join(curr_dir[:-1]))
ts_dir = curr_dir[:-1]
ts_dir.append('timeseries')
sys.path.append('/'.join(ts_dir))

import numpy as np
from tsbtreedb.generateTS import generate_ts
from tsbtreedb.correlation import stand, kernel_corr_dist
from tsbtreedb import lab10
from timeseries.timeseries import TimeSeries

def vp_similarity_search(query_ts, vantage_point_index_list):#vantage_point_list should be a file
#def _vp_similarity_search(query_ts_key, ts_dict, vp_dict):
    '''
    Find a list of 10 nearest time series to the query time series.
    1. get distances from query time series to all vantage points
    2. pick the closest vantage point
    3. define the circle radius to be 2 x distance between the query time series
    and the closest vantage point
    4. find relative index of time series within the radius distance
    5. calculate distance to all time series within the radius
    6. find the closest time series and return the index of the time series
    Param:
      query_ts : TimeSeries, the query time series that we find the 10 nearest time
      series to it
      vantage_point_index_list : list, a list of names of the 20 vantage points
    Return:
      list, a list of 10 time series indices that are the nearest 10 time series
      to the query time series.
    '''
    # step 1: get distances from query time series to all vantage points
    query_vp_dist = []
    for i in range(len(vantage_point_index_list)):
        file_name = 'tsfiles/ts_' + str(int(vantage_point_index_list[i])) + '.dat'  # get the 20 vp files
        x = np.loadtxt(file_name, delimiter = ',')  #####
        vantage_point = TimeSeries(x[:, 0], x[:, 1])
        query_vp_dist.append(kernel_corr_dist(query_ts, vantage_point, 10))

    # step 2: pick the closest vantage point
    nearest_vp = np.argmin(np.array(query_vp_dist))
    print (nearest_vp)

    # step 3: define circle radius as 2 x distance to closest vantage point
    radius = 2 * query_vp_dist[nearest_vp]
    print (radius)

    # step 4: find relative index of time series within the radius distance
    dbName = "tsdb/db_" + str(nearest_vp) + ".dbdb"
    db = lab10.connect(dbName)
    #keys, values = db.getAll_LTE(radius)
    keys = db.find_all_smaller(radius)
    print('keys',keys)

    # step 5: calculate distance to all time series within the radius
    distance = []
    for tree_name in keys:
        #print(tree_name)
        file_name = 'tsfiles/' + tree_name + '.dat'
        x = np.loadtxt(file_name, delimiter=',')
        compare_ts_point = TimeSeries(x[:, 0], x[:, 1])
        distance.append((tree_name, kernel_corr_dist(query_ts, compare_ts_point, 10)))
    #print(distance)

    # step 6: find the closest time series and return the index of the time series
    # find 10 nearest timeseries
    nearest_ts_tuple = sorted(distance, key=lambda dist: dist[1])[:10]
    #print(nearest_ts_tuple)
    #nearest_ts_tuple = [(tree_name, dist),...]
    return [item[0] for item in nearest_ts_tuple]


if __name__ == "__main__":
    file_name = 'vp_origin_idx.dat'
    vantage_point_index_list = np.loadtxt(file_name, delimiter = ',')
    print(vantage_point_index_list)
    #vantage_point_index_list = [3,33,21,5,11,8,28,13,46,34,23,32,0,49,19,27,37,24,44,2]
    x = np.loadtxt('tsfiles/ts_1.dat', delimiter = ',')  #####
    query_ts = TimeSeries(x[:, 0], x[:, 1])

    nearest_ts = vp_similarity_search(query_ts, list(vantage_point_index_list))
    print(nearest_ts)
