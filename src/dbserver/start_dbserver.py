#!/usr/bin/env python3

from dbserver.server import TSDB_Server
from timeseries.util import *
import os.path, os

def main():
        db = TSDB_Server()
        db.run()

if __name__ == '__main__':
        main()




