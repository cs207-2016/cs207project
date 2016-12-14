#!/usr/bin/env python3

from dbserver.server import *
'''Initializes and runs the Server'''

if __name__ == '__main__':
	db = TSDB_Server()
	db.run()
