#!/usr/bin/env python
import traceback
import time
import Queue
import threading

import client_bot
import training_bot
import game

class Lobby(object):
    def __init__(self, client_bots):
        self.client_bots = client_bots
        while 1:
            try:
                self.tick()
            except Exception, e:
                print "--- Start lobby exception ---"
                traceback.print_exc()
                print "--- End lobby exception ---"

    def tick(self):
        bots = [bot for bot in self.client_bots if\
                bot.state == client_bot.ClientBot.WAITING]
        for bot in bots:
            if bot.allow_training and bot.force_training:
                self.train_bot(bot)
        if len(bots) > 1:
            self.pit_bots(bots[0], bots[1])
        elif len(bots) == 1:
            self.check_single(bots[0])
    
    def check_single(self, bot):
        if bot.allow_training and time.time() > bot.lobby_start_time + bot.train_timeout:
            self.train_bot(bot)

    def train_bot(self, bot):
        in_queue = Queue.Queue()
        out_queue = Queue.Queue()
        training = training_bot.TrainingBot(in_queue, out_queue)
        self.client_bots.append(training)
        self.pit_bots(bot, training)
        
    def pit_bots(self, bot, bot_2):
        bot.state = bot.SETTING_UP_GAME
        bot_2.state = bot.SETTING_UP_GAME
        game_thread = threading.Thread(target=game.Game,
                                        args = (self.client_bots,bot,bot_2))
        game_thread.daemon = True
        game_thread.start()