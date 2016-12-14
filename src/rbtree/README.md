# CS207 Team 3 Red-Black Tree Library

A key/value store that you'd use like BDB or SQLite.

Append-only Red-Black Tree-based data-store [Red-Black Tree is self-balancing binary search tree]. An update to a leaf updates the ancestor nodes. Common nodes are shared. Updates are flushed leaf-to-root to disk (so that disk addresses can be written to the parent nodes, and commit is an atomic update to a superblock, which just points at the new root node).

Concurrent (dirty) readers are supported. Serialized fully transactional updates are supported.



 ```python
 import os
 from rbtree import *

 '''
 Connect, Set, Get, Commit, Close
 '''
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

 '''
 Get all Less Than or Equal To
 '''
 def test_db_get_All_LTE():
   dbName = "/tmp/test2.dbdb"
   if os.path.exists(dbName):
        os.remove(dbName)
   db = connect(dbName)
   db.set(4.4, "ts484.dat")
   db.set(0.0, "ts3.dat") #vantagePT
   db.set(1.3, "ts82.dat")
   db.set(2.9, "ts84.dat")
   db.set(2.3, "ts382.dat")
   db.set(2.1, "ts52.dat")
   db.set(1.8, "ts49.dat")
   db.set(1.1, "ts77.dat")
   db.set(5.3, "ts583.dat")
   keys, vals = db.get_All_LTE(2.9)
   keys
   >>>[2.1, 2.9, 2.3, 1.3, 1.8, 0.0, 1.1]
   vals
   >>>['ts52.dat','ts84.dat','ts382.dat','ts82.dat','ts49.dat','ts3.dat','ts77.dat']
   db.commit()
   db.close()

```
