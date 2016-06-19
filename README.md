# It's Life, Jim, but not as we know it

You probably know *Conway's Game of Life*, the famous cellular automaton invented by mathematician John Conway. *Life* is a set of rules that, together, allow you to simulate a two-dimensional board of cells. The rules decide which cells on the board live and  which ones die. With some imagination, you could say that *Life* is a zero-player game: a game with the objective to find patterns with interesting behavior, like the famous glider.

![Glider](http://upload.wikimedia.org/wikipedia/commons/f/f2/Game_of_life_animated_glider.gif)

A zero-player game... Until today. You are to write a program that plays the Game of Life - and plays it to win, King of the Hill-style. Your opponent (singular) of course tries to do the same. The winner is either the last bot with any live cells, or the player with the most live cells after 5 minutes of clock time.

## Game rules

The rules are *almost* the same as normal (B3/S23) Life:

* A live cell with fewer than two friendly neighbors dies from starvation.
* A live cell with two or three friendly neighbors survives.
* A live cell with more than three friendly neighbors dies from overpopulation.
* A dead cell with exactly three neighbors of the same player comes alive to fight for that player *provided there are no enemy neighbors*.

...but after each generation, both you and your opponent get the opportunity to intervene. You can awake up to a maximum of 30 cells to fight for you. (Who goes first is decided by the server.)

The board is a (x,y) cells square. All squares are initially dead. The borders do not wrap around (this is not a torus-shaped world) and are permanently dead.

This is is a contest in the spirit of *Battlebots* and *Core Wars*. There is a central server that will run bots and it can be found ![here](https://github.com/muddyfish/PPCG-Life)

## Protocol

The arena server speaks a simple JSON protocol communicated through argv


Where Values is a JSON encoded string

  - y_size: the maximum y coords of tiles before they vanish        
  - x_size: the maximum x coords of tiles before they vanish
  - board: a dictionary with keys in the form '(y,x)' and values in the form bot_id (int)
  - bot_id: tiles in the board with this id are yours

Example
    {"y_size":2000,"x_size":2000,"board":{},"bot_id":1}
     
Telling the server your choice:
    - Send the server a list of tiles to turn to your colour.
    - Only those that are empty will be changed
    - Nested coords list format
      - [[0,0], [0,1], [100,22]...]

NOTE: Your bot doesn't have to update the tiles at all - the server does the updating itself

## Competition rules

* If your implementation fails to follow the protocol, the turn it does will be forfeited; The server will assume no change in state
* You are not allowed to willfully take advantage of a fault in the arena server.
* Have your AI decide on moves in a sane time. Please send your next move as  fast as reasonably possible.
* Finally, please be nice to the server. It's there for your enjoyment.
* Not following these rules can lead to disqualification.

## Scoring

The bot with the most wins starting from <DATE HERE> wins