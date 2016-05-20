#!/usr/bin/env python
import struct
import json
import time
import os

class ClientBot(object):
    CONNECTING = 0
    CONFIG = 1
    WAITING = 2
    SETTING_UP_GAME = 3
    IN_GAME = 4
    DISCONNECTED = 5
    
    train_timeout = 5
    
    def __init__(self, server, in_queue, out_queue):
        self.state = ClientBot.CONNECTING
        self.server = server
        self.in_queue = in_queue
        self.out_queue = out_queue
    
    def __repr__(self):
        return ".".join((self.author, self.name))
    
    def get_move(self):
        assert(self.state == ClientBot.IN_GAME)
        self.updated = False
        self.send_data({"get_move":None})
        
    def move_data(self, move_data):
        assert(self.state == ClientBot.IN_GAME)
        self.send_data({"move_data":move_data})
    
    def tick_board(self):
        assert(self.state == ClientBot.IN_GAME)
        self.send_data({"tick_board":None})
    
    def send_data(self, data):
        for key, value in data.iteritems():
            self.in_queue.put((key, value))
    
    def update_state(self, message):
        assert(self.state == ClientBot.IN_GAME)
        self.move = message[:30]
        self.updated = True
    
    def on_data(self):
        key, value = self.out_queue.get()
        assert(key in ClientBot.types)
        ClientBot.types[key](self, value)
        
    def identify(self, message):
        assert(self.state == ClientBot.CONNECTING)
        self.author = message["author"]
        self.name = message["name"]
        print "%s (%s) has connected!" %(self.name, self.author)
        self.in_queue.put(("state", "config"))
        self.state = ClientBot.CONFIG
    
    def configure(self, message):
        assert(self.state == ClientBot.CONFIG)
        self.allow_training = message["allow_training"]
        if self.allow_training:
            self.force_training = message["force_training"]
            if not self.force_training:
                self.train_timeout = message["training_timeout"]
        self.goto_lobby()
                
    def goto_lobby(self):
        self.lobby_start_time = time.time()
        self.in_queue.put(("state", "lobby"))
        self.state = ClientBot.WAITING
    
    def inc_wins(self, other_bot):
        score_file = os.path.join("bot_score", str(self)+".json")
        try:
            f = open(score_file, "r")
        except IOError:
            scores = {}
        else:
            scores = json.load(f)
            f.close()
        other_name = str(other_bot)
        if other_name not in scores:
            scores[other_name] = 0
        scores[other_name] += 1
        self.in_queue.put(("scores", scores))
        f = open(score_file, "w")
        scores = json.dump(scores, f)
        f.close()
    
    def get_state(self, message):
        assert(self.state not in [ClientBot.CONNECTING,
                                  ClientBot.CONFIG,
                                  ClientBot.DISCONNECTED])
        state = {"state":self.state,
                 "allow_training":self.allow_training,
                 "force_training":self.force_training,
                 "author":self.author,
                 "bot_name":self.name}
        self.in_queue.put(("rtn_state", state))
    
    def disconnect(self, message = ""):
        if self.state != ClientBot.CONNECTING:
            print "%s (%s) disconnected"%(self.name, self.author)
        self.in_queue.put(("disconnect",message))
        self.state = ClientBot.DISCONNECTED
    
    types = {"identity": identify,
             "configure": configure,
             "get_state": get_state,
             "disconnect": disconnect,
             "update_state": update_state}