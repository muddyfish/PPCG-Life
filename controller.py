import json
import threading
from itertools import combinations
from client_bot import ClientBot
from game import Game
import time

class Controller(object):
    max_threads = 16
    def __init__(self):
        self.logfile = open("log_main.log", "a")
        self.logfile.write("\n\nNEW RUN\n\n")
        
        f = open("answers.json")
        self.bots = list(map(ClientBot, json.load(f)))
        f.close()
        for bot in self.bots:
            bot.add_log(self.logfile)
        print("Starting the games...")
        threads = []
        stop_events = []
        for bot_1, bot_2 in combinations(self.bots, 2):
            print(time.strftime("%H:%M:%S"), bot_1, bot_2)
            new_event = threading.Event()
            stop_events.append(new_event)
            
            thread = threading.Thread(target=Game, args=(bot_1, bot_2, new_event, True))
            thread.daemon = False
            thread.start()
            threads.append(thread)
            total_running = 10
            while total_running >= Controller.max_threads:
                total_running = [event.is_set() for event in stop_events]
                total_running = len(total_running)-sum(total_running)
        print("All games started! Final push!")
        
if __name__ == '__main__':
    Controller()