import random, copy
import sys, json
args = json.loads(sys.argv[1])
bot_id = args["bot_id"]
x_size = args["x_size"]
y_size = args["y_size"]
board = args["board"]
occupied = [tuple(key) for key,value in iter(board.items())]
cellsleft=30
move=[]
choices = [[[1,2],[2,1],[0,0],[0,1],[0,2]],
           [[0,0],[0,1],[1,1],[1,0]],
           [[0,1],[1,0],[0,2],[0,3],[0,4],[1,4],[2,4],[3,4],[4,4],[5,3],[5,1]],
           [[0,0],[1,0],[0,1],[2,1],[2,2]]]
while cellsleft>0:
    x_add = random.randrange(x_size)
    y_add = random.randrange(y_size)
    new_glider = copy.deepcopy(random.choice(choices))
    randomdirection = random.choice([[1,1],[1,-1],[-1,1],[-1,-1]])
    maxy=max([y[0] for y in new_glider])
    maxx=max([x[1] for x in new_glider])
    for coord in new_glider:
        coord[0]=coord[0]*randomdirection[0]+y_add
        coord[1]=coord[1]*randomdirection[1]+x_add
        cellsleft-=1
    set([tuple(x) for x in new_glider]) 
    if not set([tuple(x) for x in new_glider]) & (set(occupied)|set([tuple(x) for x in move])) and cellsleft>0:
        if min(y[0] for y in new_glider)<0: new_glider = [[y[0]+maxy,y[1]] for y in new_glider]
        if min(y[1] for y in new_glider)<0: new_glider = [[y[0],y[1]+maxx] for y in new_glider]
        move += new_glider
    elif set([tuple(x) for x in new_glider]) & (set(occupied)|set([tuple(x) for x in move])):
        cellsleft+=len(new_glider)

print(json.dumps(move))
