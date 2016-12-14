# CS207 Team 3 DB Server

This module is a socket-server for querying the proximity between time series.

It is installed as a python library and executed as a background systemd service. The service is configured in dbserver.service and runs the executable start_dbserver.py.

References directory of TimeSeries Databases.  Uses file storage manager to access directory of TimeSeries Databases.
Unless otherwise specified, uses port 15001.

Expects to receive a Serialized  TSDBOp.  If not returns INVALID_OPERATION.  If TSDBOp_withTS, returns a serialized TSDBOp_Return with a payload of 6 JSON timeseries retrieved from the timeseries.  If TSDBOp_withID, returns a serialized TSDBOp_Return with a payload of 6 JSON timeseries retrieved from the ID.  Accepts up to 15 clients at once.

To start the server run:
 ```python
main.py
```

To connect to the server you'll need to:
 ```python
from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_REUSEADDR
from dbserver.tsdb_deserialize import *
from dbserver.tsdb_ops import *
s= socket(AF_INET, SOCK_STREAM)
s.connect(('',15001))
op = TSDBOp_withID('99329482398429305458')
op = op.to_json()
s.send(serialize(op))
msg = s.recv(65536)
```
What is received back from the server is a TSDBOp_Return with a payload equal to the 6 JSON timeseries.
