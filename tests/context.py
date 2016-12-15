import sys
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
path = os.path.join(path, 'src')
sys.path.insert(0, path)

from timeseries.timeseries import *
from rbtree.rbtree import *
from timeseries.util import *
from website import website

# Alias for group 5 tests
import group5code as tsbtreedb
