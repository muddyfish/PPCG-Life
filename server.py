import socket
import threading
import SocketServer
import Queue
import traceback
import struct
import time
import json

import client_bot
import lobby

class ClientRequestHandler(SocketServer.BaseRequestHandler):
    """ThreadedTCPRequestHandler"""
    timeout = 0.1
    def setup(self):
        self.in_queue, self.out_queue = self.server.add_queue()
        self.request.settimeout(ClientRequestHandler.timeout)
    
    def encode(self, message):
        return struct.pack("I", len(message))+message    
    
    def handle(self):
        cur_thread = threading.current_thread()
        self.in_queue.put(("state", "connecting"))
        while 1:
            try:
                data = self.request.recv(4)
                length = struct.unpack("I", data)[0]
                data = self.request.recv(length)
            except socket.timeout:pass
            except:
                break
            else:
                for key, value in json.loads(data).iteritems():
                    self.out_queue.put((key, value))
            if not self.in_queue.empty():
                key, value = self.in_queue.get()
                self.request.sendall(self.encode(json.dumps({key:value})))
                if key == "disconnect":
                    break
        self.request.shutdown(socket.SHUT_RDWR)
        self.request.close()
    
    def finish(self):
        self.out_queue.put(("disconnect", ""))

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    daemon_threads = True
    def __init__(self, server_address, client_bots):
        SocketServer.TCPServer.__init__(self, server_address, ClientRequestHandler)
        self.client_bots = client_bots
        
    def add_queue(self):
        in_queue = Queue.Queue()
        out_queue = Queue.Queue()
        new_bot = client_bot.ClientBot(self, in_queue, out_queue)
        self.client_bots.append(new_bot)
        return in_queue, out_queue
    
    def send_all_bots(self, data):
        for bot in self.client_bots:
            bot.in_queue.put(data)

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 7777

    client_bots = []
    server = ThreadedTCPServer((HOST, PORT), client_bots)
    ip, port = server.server_address
    #Start server thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    #Start lobby thread
    lobby_thread = threading.Thread(target=lobby.Lobby,
                                    args = (client_bots,))
    lobby_thread.daemon = True
    lobby_thread.start()
    print "Initialised server!"
    try:
        while True:
            for bot in client_bots:
                if not bot.out_queue.empty():
                    try:
                        bot.on_data()
                    except Exception, e:
                        print "--- Start bot exception ---"
                        traceback.print_exc()
                        print "--- End bot exception ---"
                        bot.disconnect()
                        client_bots.remove(bot)
    finally:
        print("Stopping")
        server.shutdown()
        server.server_close()