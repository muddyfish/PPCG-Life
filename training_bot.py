#!/usr/bin/env python
import random, copy
import client_bot

class TrainingBot(client_bot.ClientBot):
    glider = [[1,2],[2,1],[0,0],[0,1],[0,2]]
    size = 1900
    def __init__(self, in_queue, out_queue):
        self.state = client_bot.ClientBot.WAITING
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.author = "muddyfish"
        self.name = "training_bot"
    
    def get_move(self):
        ##AI stuff here
        x_add = random.randrange(TrainingBot.size)
        y_add = random.randrange(TrainingBot.size)
        new_glider = copy.deepcopy(TrainingBot.glider)
        for coord in new_glider:
            coord[0]+=y_add
            coord[1]+=x_add
        self.move = new_glider
        print self.move
        self.updated = True
    
    def disconnect(self, message = ""):
        self.state = client_bot.ClientBot.DISCONNECTED