from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_REUSEADDR
from concurrent.futures import ThreadPoolExecutor
import threading
import json
import enum
import socketserver

from timeseries.storagemanager import FileStorageManager
from timeseries.util import *
from timeseries import TimeSeries

from .tsdb_ops import *
from .tsdb_deserialize import *
from .tsdb_error import *

import pdb

LENGTH_FIELD_LENGTH = 4
DBSERVER_HOME = '/var/dbserver/'
DIR_TS_DATA = DBSERVER_HOME + 'tsdata'
DIR_TS_DB = DBSERVER_HOME + 'tsdb'

class TSDB_Server(socketserver.BaseServer):
    '''Class for TimeSeries Database Socket Server'''

    def __init__(self, addr=15001):
        '''Initializes Socket Server with given port, storage manager, and
        Deserializer for reading from bytestream'''
        self.addr = addr
        self.deserializer = Deserializer()
        self.sm = FileStorageManager(DIR_TS_DATA)

    def handle_client(self, sock, client_addr):
        '''Manages client request and sends back response as serialized json'''
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
        '''Start TSDBServer and listen for client connections. Manage incoming connections
        with threads.'''
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
        '''Waits until the entire message has been received into the Deserializer, then Deserializes
        a byte message from the socket back to its JSON representation.'''
        self.deserializer.append(data)
        if self.deserializer.ready():
            msg = self.deserializer.deserialize()
            status = TSDBStatus.OK  # until proven otherwise.
            response = TSDBOp_Return(status, None)  # until proven otherwise.
            try:
                tsdbop = TSDBOp.from_json(msg)
            except TypeError as e:
                response = TSDBOp_Return(TSDBStatus.INVALID_OPERATION, None)
                status = TSDBStatus.INVALID_OPERATION

            if status is TSDBStatus.OK:

                if isinstance(tsdbop, TSDBOp_withTS):
                    response = self._with_ts(tsdbop)
                elif isinstance(tsdbop, TSDBOp_withID):
                    response = self._with_id(tsdbop)
                elif isinstance(tsdbop, TSDBOp_putTS):
                    response = self._put_ts(tsdbop)
                else:
                    response = TSDBOp_Return(TSDBStatus.UNKNOWN_ERROR, tsdbop['op'])

            return serialize(response.to_json())

    def _with_ts(self, TSDBOp):
        '''Gets 6 TimeSeries representations (including the original queried TS) from StorageManager
        from a TimeSeries representation sent over the socket. Returns them as the payload of a TSDBOp_Return'''
        if not isinstance(TSDBOp['ts'], TimeSeries):
            return TSDBOp_Return(TSDBStatus.INVALID_COMPONENT, None)
        ids = get_similar_ts(TSDBOp['ts'], 5, DIR_TS_DATA, DIR_TS_DB)
        tslist = [self.get_ts_from_id(idee).to_json() for idee in ids]
        return TSDBOp_Return(TSDBStatus.OK, TSDBOp, json.dumps(tslist))

    def _with_id(self, TSDBOp):
        '''Gets 6 TimeSeries representations (including the original queried TS) from StorageManager
        from a TimeSeries ID sent over the socket. Returns them as the payload of a TSDBOp_Return'''
        try:
            ids = get_similar_ts_by_id(TSDBOp['id'], 5, DIR_TS_DATA, DIR_TS_DB)
        except KeyError:
            return TSDBOp_Return(TSDBStatus.INVALID_KEY, None)

        tslist = [self.get_ts_from_id(idee).to_json() for idee in ids]
        return TSDBOp_Return(TSDBStatus.OK, TSDBOp, json.dumps(tslist))

    def _put_ts(self, TSDBOp):
        if not isinstance(TSDBOp['ts'], TimeSeries):
            return TSDBOp_Return(TSDBStatus.INVALID_COMPONENT, None)
        ts = SMTimeSeries(time_points=TSDBOp['ts']._times, data_points=TSDBOp['ts']._data, sm=self.sm)
        tsid = ts._ident
        db_files = os.listdir(DIR_TS_DB)
        for db_filename in db_files:
            db = connect(DIR_TS_DB + '/' + db_filename)
            vantage_pt_id = db.get(0)
            vantage_pt = SMTimeSeries.from_db(vantage_pt_id, self.sm)
            dist = 2*(1-kernel_corr(vantage_pt, TSDBOp['ts']))
            db.set(dist, str(tsid))
            db.commit()
            db.close()
        return TSDBOp_Return(TSDBStatus.OK, TSDBOp)

    def get_ts_from_id(self, idee):
        '''Gets the TimeSeries data for a TimeSeries from the corresponding ID'''
        ts = SMTimeSeries.from_db(idee, self.sm)
        return ts

if __name__ == '__main__':
    server = TSDB_Server()
    server.run()
