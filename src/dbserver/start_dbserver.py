#!/usr/bin/env python3

from dbserver.server import TSDB_Server
from timeseries.util import *
import os.path, os

DIR_TS_DATA = '/var/dbserver/tsdata'
DIR_TS_DB = '/var/dbserver/tsdb'

def main():
        db = TSDB_Server()
        db.run()

if __name__ == '__main__':

        # If the random time series haven't yet been generated, generate them
        if not os.path.exists(DIR_TS_DATA):
                os.makedirs(DIR_TS_DATA)
		generate_timeseries(1000, DIR_TS_DATA)
        if not os.path.exists(DIR_TS_DB):
                os.makedirs(DIR_TS_DB)
		generate_vantage_points(20, DIR_TS_DATA, DIR_TS_DB)                
        main()




