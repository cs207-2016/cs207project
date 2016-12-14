# CS207 Team 3 Red-Black Tree Library

# Todo: Implementation details and examples
# CS207 Team 3 Red Black Tree Library

# TODO: Someone write this

A library for building a Red Black Tree database

 ```python
 import os
 from rbtree import *

 dbName = "/tmp/test2.dbdb"
 if os.path.exists(dbName):
      os.remove(dbName)
 db = connect(dbName)
 db.set(4.4, "ts484.dat")
 db.set(0.0, "ts3.dat")
 db.commit()
 db.close()
 db = connect(dbName)
 db.get(0.0)
 >>>'ts3.dat'



```
