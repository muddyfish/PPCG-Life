import random, copy
import sys, json

args = json.loads(sys.argv[1])
bot_id = args["bot_id"]
x_size = args["x_size"]
y_size = args["y_size"]
board = args["board"]

glider = [[1,2],[2,1],[0,0],[0,1],[0,2]]

x_add = random.randrange(x_size)
y_add = random.randrange(y_size)
new_glider = copy.deepcopy(glider)
for coord in new_glider:
    coord[0]+=y_add
    coord[1]+=x_add
move = new_glider
print json.dumps(move)
