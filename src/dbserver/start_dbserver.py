#!/usr/bin/env python3

from dbserver.server import TSDB_Server
from dbserver.util import getTS, genDB
import os.path, os

DIR_TS_DATA = '/var/dbserver/tsdata'
DIR_TS_DB - '/var/dbserver/tsdb'

def main():
	db = TSDB_Server()
	db.run

if __name__ == '__main__':

	# If the random time series haven't yet been generated, generate them
	if not os.path.exists(DIR_TS_DATA):
		os.makdirs(DIR_TS_DATA)
		genTS(nTS = 1000, file_dir=DIR_TS_DATA)
	if not os.path.exists(DIR_TS_DB):
		os.makedirs(DIR_TS_DB):
		genDB(tsdata_dir=DIR_TS_DATA, db_dir=DIR_TS_DB)
		
	main()
