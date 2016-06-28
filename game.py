#!/usr/bin/env python
import traceback
import time
import json
import random
import time

#from PIL import Image

import client_bot

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
    no_generations = 10000
    
    def __init__(self, bot_1, bot_2, stop_event):
        cur_time = str(time.time())
        self.log = open("log_%s.log"%cur_time, "w")
        self.stop_event = stop_event
        bots = [bot_1, bot_2]
        random.shuffle(bots)
        self.bot_1,self.bot_2 = bots
        self.ended = False
        try:
            self.setup()
        except Exception as e:
            self.log.write("--- Start game setup exception ---\n")
            traceback.print_exc()
            self.log.write("--- End game setup exception ---\n")
        while not self.ended:
            try:
                self.tick()
            except Exception as e:
                self.log.write("--- Start game exception ---\n")
                traceback.print_exc()
                self.log.write("--- End game exception ---\n")
            if self.tick_id == Game.no_generations:
                self.end_time()
        self.log.write("Finished!\n")
        self.stop_event.set()

    def setup(self):
        self.log.write("SETUP GAME %s %s\n"%(self.bot_1, self.bot_2))
        self.setup_board()
        self.tick_id = 0
        self.start_time = time.time()

    def setup_board(self):
        self.board = Board(self.x_size, self.y_size)         

    def tick(self):
        self.log.write("TICK\n")
        self.log.flush()
        #self.board.save("board_%s.png"%(self.tick_id))
        self.get_move(self.bot_1, 1)
        self.get_move(self.bot_2, 2)
        self.board.tick()
        self.tick_id += 1
    
    def get_move(self, bot, bid):
        self.board.update(bot.get_move(bid, self.board), bid)
    
    def end_time(self):
        self.ended = True
        locs = [0, 0]
        for loc in self.board.locations:
            locs[self.board[loc]-1]+=1
        if locs[0] >= locs[1]:
            self.bot_1.inc_wins(self.bot_2)
        if locs[0] <= locs[1]:
            self.bot_2.inc_wins(self.bot_1)