from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_REUSEADDR
from concurrent.futures import ThreadPoolExecutor
import threading
import json
import enum
import socketserver

from timeseries.storagemanager import FileStorageManager
from timeseries.util import *

from .tsdb_ops import *
from .tsdb_deserialize import *
from .tsdb_error import *

import pdb

LENGTH_FIELD_LENGTH = 4
DBSERVER_HOME = '/var/dbserver/'
DIR_TS_DATA = DBSERVER_HOME + 'tsdata'
DIR_TS_DB = DBSERVER_HOME + 'tsdb'

class TSDB_Server(socketserver.BaseServer):

    def __init__(self, addr=15001):
        self.addr = addr
        self.deserializer = Deserializer()
        self.sm = FileStorageManager(DIR_TS_DATA)

    def handle_client(self, sock, client_addr):
        print('Got connection from', client_addr)
        while True:
            msg = sock.recv(65536)
            if not msg:
                break
            json_response = self.data_received(msg)
            sock.sendall(json_response)
        print('Client closed connection')
        sock.close()

    def run(self):
        pool = ThreadPoolExecutor(50)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind(('',self.addr))
        sock.listen(15)

        while True:
            print('connection')
            client_sock, client_addr = sock.accept()
            pool.submit(self.handle_client, client_sock, client_addr)

    def data_received(self, data):
        self.deserializer.append(data)
        if self.deserializer.ready():
            msg = self.deserializer.deserialize()
            status = TSDBStatus.OK  # until proven otherwise.
            response = TSDBOp_Return(status, None)  # until proven otherwise.
            try:
                tsdbop = TSDBOp.from_json(msg)
            except TypeError as e:
                response = TSDBOp_Return(TSDBStatus.INVALID_OPERATION, None)

            if status is TSDBStatus.OK:
                if isinstance(tsdbop, TSDBOp_withTS):
                    response = self._with_ts(tsdbop)
                elif isinstance(tsdbop, TSDBOp_withID):
                    response = self._with_id(tsdbop)
                else:
                    response = TSDBOp_Return(TSDBStatus.UNKNOWN_ERROR, tsdbop['op'])

            return serialize(response.to_json())

    def _with_ts(self, TSDBOp):
        ids = get_similar_ts_by_id(TSDBOp['ts'], 5, DIR_TS_DATA, DIR_TS_DB)
        tslist = [self.get_ts_from_id(idee).to_json() for idee in ids]
        return TSDBOp_Return(TSDBStatus.OK, TSDBOp, json.dumps(tslist))

    def _with_id(self, TSDBOp):
        ids = get_similar_ts_by_id(TSDBOp['id'], 5, DIR_TS_DATA, DIR_TS_DB)
        tslist = [self.get_ts_from_id(idee).to_json() for idee in ids]
        return TSDBOp_Return(TSDBStatus.OK, TSDBOp, json.dumps(tslist))

    def get_ts_from_id(self, idee):
        ts = SMTimeSeries.from_db(idee, self.sm)
        return ts
