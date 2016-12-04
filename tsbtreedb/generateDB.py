import os, sys

curr_dir = os.getcwd().split('/')
sys.path.append('/'.join(curr_dir[:-1]))
ts_dir = curr_dir[:-1]
ts_dir.append('timeseries')
sys.path.append('/'.join(ts_dir))
# sys.path.append('/Users/mxy/Downloads/Milestone2-part7')

import json

from timeseries.timeseries import TimeSeries
import numpy as np
import random
from  tsbtreedb.correlation import correlation
from tsbtreedb import lab10

'''
This file includes a function called generateDB to generate some databases from
20 different timeseries vantage points.

How to run:
first import this file
then call 'generateDB(numTS, numVP)' to generate numVP(an integer) databases

Requires folders:
tsfiles

Requires files:
There should be at least numTS(an integer) time series files in the folder 'tsfiles'.
Each file should have 'tsfiles/ts_i.dat' formate where i is an integer.

All databases will be saved in a folder called 'tsdb'
A file called 'vp_origin_idx.dat' is also genenrated when this function is called.
It saves the index of each vantage point in the set of time series.
'''


def generateDB(numTS=1000, numVP=20):
    '''
    Generate some Databases from different timeseries vantage points. Each database
    is generated from each vantage point.
    Run 'python generate_ts.py 1000' to generate 1000 time series in the directory
    '/tsfile', with each time series stored in a dat file.
    Param:
      numTS: int, the number of time series that the vantage points are generated from
      numVP: int, the number of vantage points that should be generated
    '''
    num_ts = numTS
    num_vp = numVP
    vantage_point_index_list = np.random.choice(num_ts, num_vp, replace=False)
    file_name = 'vp_origin_idx.dat'
    try:
        f = open(file_name, 'w')
    except IOError:
        print('cannot open', file_name)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    for i in range(len(vantage_point_index_list) - 1):
        f.write(str(vantage_point_index_list[i]))
        f.write(',')
    f.write(str(vantage_point_index_list[len(vantage_point_index_list) - 1]))
    f.close()
    vantage_point_list = []
    # print (vantage_point_index_list)
    directory = "tsdb"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for i in range(num_vp):
        file_name = 'tsfiles/ts_' + str(vantage_point_index_list[i]) + '.dat'  # get the 20 vp files
        x = np.loadtxt(file_name, delimiter=',')  #####
        vantage_point = TimeSeries(x[:, 0], x[:, 1])
        vantage_point_list.append(vantage_point)

    # my_dict = {}

    for i in range(num_vp):
        dbName = "tsdb/db_" + str(i) + ".dbdb"
        if os.path.exists(dbName):
            os.remove(dbName)
        db = lab10.connect(dbName)

        # my_dict[i] = {}
        # create a new directory called tsdb
        for j in range(num_ts):
            tree_name = 'ts_' + str(j)
            file_name = 'tsfiles/' + tree_name + '.dat'
            x = np.loadtxt(file_name, delimiter=',')
            compare_ts_point = TimeSeries(x[:, 0], x[:, 1])

            dist = correlation.kernel_corr_dist(vantage_point_list[i], compare_ts_point)
            # print(dist, tree_name)
            db.set(dist, tree_name)
            db.commit()
            # my_dict[i][j]=dist
        db.close()
        # db.close()
        # f = open("mytest.dat", "w")
        # f.write(json.dumps(my_dict))
        # f.close()

# if __name__ == "__main__":
#    num_ts = int(sys.argv[1])
#    num_vp = int(sys.argv[2])
#    generateDB(num_ts, num_vp)
