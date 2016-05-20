#!/usr/bin/env python

import socket
import SocketServer
import struct
import json

json_identity = json.dumps({"identity":dict(
    author = "muddyfish",
    name = "demo_bot"
)})
json_configure = json.dumps({"configure":dict(
    allow_training = True,
    force_training = True
)})

class Disconnect(Exception):pass

def encode(message):
    return struct.pack("I", len(message))+message    

first = True

def handle(key, value):
    global first
    if key == "disconnect":
        raise Disconnect(value)
    print {key:value}
    if key == "get_move":
        if first:
            first = False
            return {"update_state": [[101,102],[102,101],[100,100],[100,101],[100,102]]}
        else:
            return {"update_state": []}
    if key == "state" and value == "lobby":
        first = True
    return {}

def handle_multiple(data):
    rtn = {}
    for key, value in data.iteritems():
        rtn.update(handle(key, value))
    return rtn

def client(ip, port):
    #Setup socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    print "Connected!"
    try:
        sock.sendall(encode(json_identity))
        sock.sendall(encode(json_configure))
        while 1:
            data = sock.recv(4)
            length = struct.unpack("I", data)[0]
            data = sock.recv(length)
            out = handle_multiple(json.loads(data))
            sock.sendall(encode(json.dumps(out)))
    finally:
        sock.close()

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "dustbunny.catbus.co.uk", 7777
    client(HOST, PORT)