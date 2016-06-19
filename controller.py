import json
import threading
from itertools import combinations
from client_bot import ClientBot
from game import Game
import time

class Controller(object):
    no_games = 4
    def __init__(self):
        self.logfile = open("log.log", "a")
        self.logfile.write("\n\nNEW RUN\n\n")
        
        f = open("answers.json")
        self.bots = list(map(ClientBot, json.load(f)))
        f.close()
        for bot in self.bots:
            bot.add_log(self.logfile)
        print("Starting the games...")
        threads = []
        for bot_1, bot_2 in combinations(self.bots, 2):
            print bot_1, bot_2
            thread = threading.Thread(target=Game, args=(self.logfile, bot_1, bot_2))
            thread.daemon = False
            thread.start()
            threads.append(thread)
            time.sleep(Game.game_length//Controller.no_games)
        print("Ran all games!")
        
if __name__ == '__main__':
    Controller()