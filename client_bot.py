#!/usr/bin/env python
import subprocess
import json
import sys, os

class ClientBot(object):
    timeout = 1
    def __init__(self, cmd):
        self.cmd = cmd
        self.bot_name = self.get_botname()

    def __str__(self):
        return self.bot_name.encode(sys.stdout.encoding, errors='replace').decode()
    
    def get_botname(self): return self.cmd[3]
    
    def add_log(self, log):
        self.logfile = log

    def run(self, bot_id, board):
        loc = {str(key):value for key,value in board.locations.items()}
        json_args = json.dumps({"bot_id": bot_id,
                                "x_size": board.x_size,
                                "y_size": board.y_size,
                                "board": loc})
        try:
            args = " ".join(self.cmd + ["'"+json_args.replace(' ','')+"'"])
            output = str(subprocess.check_output(args, timeout=ClientBot.timeout), "ascii").strip()
            return json.loads(output)
        except subprocess.TimeoutExpired as e:
            print("Timeout in bot", self)
        except Exception as e:
            self.logfile.write("An Error occured running the bot: %s\nException:\n%s\n"%(self, e))
            return {}
    
    def get_move(self, bot_id, board_data):
        #print(self, bot_id, board_data)
        return self.run(bot_id, board_data)
    
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
        f = open(score_file, "w")
        scores = json.dump(scores, f)
        f.close()