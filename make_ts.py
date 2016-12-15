#!/usr/bin/env python3

import os, os.path
from timeseries.util import *

tsdata = '/var/dbserver/tsdata'
tsdb = '/var/dbserver/tsdb'

if not os.path.exists(tsdata):
	os.makedirs(tsdata)
	generate_timeseries(1000, tsdata)
if not os.path.exists(tsdb):
	os.makedirs(tsdb)
	generate_vantage_points(20, tsdata, tsdb)
