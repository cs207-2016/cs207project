from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_REUSEADDR
from concurrent.futures import ThreadPoolExecutor
import threading
from .tsdb_ops import *
from .tsdb_deserialize import *
from .tsdb_error import *
import json
import enum

LENGTH_FIELD_LENGTH = 4

class TSDB_Server(socketserver.BaseServer):

    def __init__(self, db, addr=15000):
        self.db = db
        self.addr = port
        self.deserializer = Deserializer()

    def run(self):
        pool = ThreadPoolExecutor(50)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind(addr)
        sock.listen(15)

        while True:
            print('connection')
            client_sock, client_addr = sock.accept()
            pool.submit(handle_client, client_sock, client_addr, self.db)

    def handle_client(sock, client_addr):
        print('Got connection from', client_addr)
        while True:
            msg = sock.recv(65536)
            if not msg:
                break
            json_response = data_received(msg)
            sock.sendall(self.deserializer.serialize(json_response))
        print('Client closed connection')
        sock.close()

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
                if isinstance(op, TSDBOp_withTS):
                    response = self._with_ts(tsdbop)
                elif isinstance(op, TSDBOp_withID):
                    response = self._with_id(tsdbop)
                else:
                    response = TSDBOp_Return(TSDBStatus.UNKNOWN_ERROR, tsdbop['op'])

            return serialize(response.to_json())

    def _with_ts(self, TSDBOp):

        return None

    def _with_id(self, TSDBOp):

        return None
