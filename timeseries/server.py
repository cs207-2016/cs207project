from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_REUSEADDR
from concurrent.futures import ThreadPoolExecutor
import threading
import json
import enum

LENGTH_FIELD_LENGTH = 4

class LockableDict:
    def __init__(self):
        self._d={}
        self._dlock={}

    def __getitem__(self, attr):
        return self._d[attr]

    def __setitem__(self, attr, val):
        if attr not in self._d:
            self._dlock[attr]=threading.Lock()
        print("LOCKING FOR", attr, val)
        with self._dlock[attr]:
            self._d[attr] = val
        print("UNLOCKED FOR", attr, val)

def db_client(sock, client_addr, ldict):
    print('Got connection from', client_addr)
    while True:
        msg = sock.recv(65536)
        print("msg", msg)
        if not msg:
            break
        key, value = msg.decode().split('=')
        print("k,v", key, value)
        ldict[key] = value
        sock.sendall(value.encode())
    print('Client closed connection')
    sock.close()

def db_server(addr):
    print("creating lockable dict and pool")
    ldict=LockableDict()
    pool = ThreadPoolExecutor(50)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(addr)
    sock.listen(15)
    while True:
        print('connection')
        client_sock, client_addr = sock.accept()
        pool.submit(db_client, client_sock, client_addr, ldict)

db_server(('',15000))
