import os, sys
curr_dir = os.getcwd().split('/')
sys.path.append('/'.join(curr_dir[:-1]))
ts_dir = curr_dir[:-1]
ts_dir.append('timeseries')
sys.path.append('/'.join(ts_dir))
#sys.path.append('/Users/mxy/Downloads/Milestone2-part7')

import json

from timeseries.timeseries import TimeSeries
import numpy as np
import random
from  tsbtreedb.correlation import kernel_corr_dist
from tsbtreedb import lab10

'''
This file is a script to generate 20 Databases
from 20 different timeseries vantage points
How to run:
python generateDB_A.py
Requires folders:
tsdb
'''

def generateDB(numTS = 1000, numVP = 20):
    num_ts = numTS
    num_vp = numVP
    vantage_point_index_list = np.random.choice(num_ts, num_vp, replace = False)
    file_name = 'vp_origin_idx.dat'
    f = open(file_name, 'w')
    for i in range(len(vantage_point_index_list)-1):
        f.write(str(vantage_point_index_list[i]))
        f.write(',')
    f.write(str(vantage_point_index_list[len(vantage_point_index_list)-1]))
    f.close()
    vantage_point_list  = []
    #print (vantage_point_index_list)
    directory = "tsdb"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for i in range(num_vp):
        file_name = 'tsfiles/ts_' + str(vantage_point_index_list[i]) + '.dat'  # get the 20 vp files
        x = np.loadtxt(file_name, delimiter = ',')  #####
        vantage_point = TimeSeries(x[:, 0], x[:, 1])
        vantage_point_list.append(vantage_point)

    my_dict = {}

    for i in range(num_vp):
        dbName = "tsdb/db_" + str(i) + ".dbdb"
        if os.path.exists(dbName):
            os.remove(dbName)
        db = lab10.connect(dbName)

        my_dict[i] = {}
        # create a new directory called tsdb
        for j in range(num_ts):
            tree_name = 'ts_' + str(j)
            file_name = 'tsfiles/' + tree_name + '.dat'
            x = np.loadtxt(file_name, delimiter=',')
            compare_ts_point = TimeSeries(x[:, 0], x[:, 1])

            dist = kernel_corr_dist(vantage_point_list[i], compare_ts_point)
            #print(dist, tree_name)
            db.set(dist, tree_name)
            db.commit()
            my_dict[i][j]=dist
        db.close()
    #db.close()
    f = open("mytest.dat", "w")
    f.write(json.dumps(my_dict))
    f.close()


if __name__ == "__main__":
    num_ts = int(sys.argv[1])
    num_vp = int(sys.argv[2])
    generateDB(num_ts, num_vp)
