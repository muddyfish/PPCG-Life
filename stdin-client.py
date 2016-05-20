#!/usr/bin/env python

import socket
import SocketServer
import threading
import Queue
import struct
import json

json_identity = json.dumps({"identity":dict(
    author = "muddyfish",
    name = "stdin_bot"
)})
json_configure = json.dumps({"configure":dict(
    allow_training = True,
    force_training = False,
    training_timeout = 1
)})

class Disconnect(Exception):pass

def stdin_handler(queue):
    while 1:
        queue.put(raw_input())

def encode(message):
    return struct.pack("I", len(message))+message    

def handle(key, value):
    if key == "disconnect":
        raise Disconnect(value)
    print {key:value}

def handle_multiple(data):
    for key, value in data.iteritems():
        handle(key, value)

def client(ip, port):
    stdin = Queue.Queue()
    stdin_thread = threading.Thread(target=stdin_handler,
                                    args = (stdin,))
    stdin_thread.daemon = True
    stdin_thread.start()
    #Setup socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.settimeout(0.1)
    try:
        sock.sendall(encode(json_identity))
        sock.sendall(encode(json_configure))
        while 1:
            try:
                data = sock.recv(4)
                length = struct.unpack("I", data)[0]
                data = sock.recv(length)
            except socket.timeout:pass
            else:
                handle_multiple(json.loads(data))
            if not stdin.empty():
                inp = stdin.get()
                sock.sendall(encode(inp))
    finally:
        sock.close()

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 9999
    client(HOST, PORT)