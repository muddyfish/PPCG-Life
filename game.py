#!/usr/bin/env python
import traceback
import time
import Queue
import json
import random

#from PIL import Image

import client_bot
import training_bot

class Board(object):
    EMPTY = 0
    P_1 = 1
    P_2 = 2
    def __init__(self, x_size, y_size):
        self.x_size, self.y_size = x_size, y_size
        self.locations = {}
    
    def __repr__(self):
        return str(self.locations)
    
    def __getitem__(self, pos):
        if pos in self.locations:
            return self.locations[pos]
        return Board.EMPTY

    def __setitem__(self, pos, val):
        if val == Board.EMPTY:
            if pos in self.locations:
                del self.locations[pos]
        elif 0<=pos[0]<self.y_size:
            if 0<=pos[1]<self.x_size:
                self.locations[pos] = val
                
    def save(self, filename = "board.png"):
        im = Image.new("L", (200, 200))
        for i in xrange(200):
            for j in xrange(200):
                im.putpixel((i,j), self[i,j]*127)
        print("saving")
        im.save(filename)
        im.close()

    def get_neighbours(self, x, y):
        return self[x+1,y], self[x-1,y], self[x,y+1], self[x,y-1], \
               self[x+1,y+1], self[x-1,y-1], self[x-1,y+1], self[x+1,y-1],
    
    def get_neighbour_locs(self, x, y):
        return (x+1,y), (x-1,y), (x,y+1), (x,y-1), \
               (x+1,y+1), (x-1,y-1), (x+1,y+1), (x-1,y-1)

    def tick(self):
        updated = {}
        for loc in self.locations:
            player = self.locations[loc]
            neighbours = self.get_neighbours(*loc)
            friendly_count = neighbours.count(player)
            if friendly_count < 2:
                #Starve
                updated[loc] = Board.EMPTY
            if friendly_count > 3:
                #Overpoputation
                updated[loc] = Board.EMPTY
            for loc in self.get_neighbour_locs(*loc):
                if self[loc] == Board.EMPTY:
                    #Up for reclaiming
                    neighbours = self.get_neighbours(*loc)
                    set_neighbours = set(neighbours) - {Board.EMPTY}
                    if len(set_neighbours) == 1 and neighbours.count(list(set_neighbours)[0])==3:
                        updated[loc] = list(set_neighbours)[0]

        for loc in updated:
            self[loc] = updated[loc]
        
    def update(self, positions, player_id):
        for loc in positions:
            loc = tuple(loc)
            if self[loc] == Board.EMPTY:
                self[loc] = player_id
        

class Game(object):
    x_size = 2000
    y_size = 2000
    game_length = 60
    round_time = 0.1
    def __init__(self, client_bots, bot_1, bot_2):
        bot_1.send_data({"state":"in_game"})
        bot_2.send_data({"state":"in_game"})
        self.client_bots = client_bots
        bots = [bot_1, bot_2]
        random.shuffle(bots)
        self.bot_1,self.bot_2 = bots
        self.ended = False
        try:
            self.setup()
        except Exception, e:
            print "--- Start game setup exception ---"
            traceback.print_exc()
            print "--- End game setup exception ---"
            self.end_disconnect()
        while not self.ended:
            try:
                self.tick()
            except Exception, e:
                print "--- Start game exception ---"
                traceback.print_exc()
                print "--- End game exception ---"
                self.end_disconnect()
            if self.start_time + Game.game_length < time.time():
                self.end_time()
        print "Finished!"

    def setup(self):
        print("SETUP GAME", self.bot_1.name, self.bot_2.name)
        setup_data = {"x_size":Game.x_size,
                      "y_size":Game.y_size,
                      "game_time":Game.game_length,
                      "response_time":Game.round_time}
        self.bot_1.send_data({"setup_game":setup_data})
        self.bot_2.send_data({"setup_game":setup_data})
        self.setup_board()
        self.bot_1.state = self.bot_1.IN_GAME
        self.bot_2.state = self.bot_2.IN_GAME
        self.tick_id = 0
        self.start_time = time.time()

    def setup_board(self):
        self.board = Board(self.x_size, self.y_size)         

    def tick(self):
        self.bot_2.move_data(self.get_move(self.bot_1,1))
        self.bot_1.move_data(self.get_move(self.bot_2,2))
        self.bot_1.tick_board()
        self.bot_2.tick_board()
        #self.board.save("board_%s.png"%(self.tick_id))
        self.board.tick()
        self.tick_id += 1
    
    def get_move(self, bot, bid):
        bot.get_move()
        start_time = time.time()
        while not bot.updated and time.time()<start_time+Game.round_time:pass
        if time.time()>=start_time+Game.round_time and not bot.updated:
            print"Timeout"
            return []
        self.board.update(bot.move, bid)
        return bot.move
        
    def end_disconnect(self):
        self.ended = True
        self.kill_trainer()
        if self.bot_1.state == self.bot_1.DISCONNECTED:
            self.bot_2.inc_wins(self.bot_1)
            self.bot_1.disconnect()
            self.bot_2.goto_lobby()
        if self.bot_2.state == self.bot_1.DISCONNECTED:
            self.bot_1.inc_wins(self.bot_2)
            self.bot_2.disconnect()
            self.bot_1.goto_lobby()
    
    def end_time(self):
        self.ended = True
        locs = [0, 0]
        for loc in self.board.locations:
            locs[self.board[loc]-1]+=1
        if locs[0] >= locs[1]:
            self.bot_1.inc_wins(self.bot_2)
        if locs[0] <= locs[1]:
            self.bot_2.inc_wins(self.bot_1)
        self.kill_trainer()
        self.bot_1.goto_lobby()
        self.bot_2.goto_lobby()
        
    def kill_trainer(self):
        for bot in (self.bot_1, self.bot_2):
            if isinstance(bot, training_bot.TrainingBot):
                self.client_bots.remove(bot)