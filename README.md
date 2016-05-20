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

This is is a contest in the spirit of *Battlebots* and *Core Wars*. However, unlike those two, you are supposed to run your implementation on your own machine. You fight the other contestants on a central arena server.

## Protocol

The arena server speaks a simple, JSON protocol over TCP. Messages have the following format:

    llllvvvvvvv...
    ^ Length (4 byte, unsigned int)
        ^ Values (Exactly length bytes long)

Where Values is a JSON encoded string

Potential keys you will recieve in Values:

 - "state"
  - Recieved when your bot changes state
  - Possible states are:
    - connecting
    - config
    - lobby
    - in_game
 - "get_move"
   - Null value
   - Recieved when the game wants to know what move you will make
 - "move_data"
   - Update the cells to the opponents colour but only if empty
   - Nested coords list format
     - [[0,0], [0,1], [100,22]...]
 - "tick_board" 
   - Tick the board by one (Apply rules)
 - "rtn_state"
   - Internal state of your bot
   - Only sent in reply to "get_state" command
   - Contains:
     - "state"
     - "allow_training"
     - "force_training"
     - "author"
     - "bot_name"
     
Keys you may send to the server
  - "identity"
    - Only in the "connecting" state
      - "author": "CodeGolf Username",
      - "name": "Awesome bot name!"
  - "configure"
    - Only in the "config" state
      - allow_training: Boolean, will your bot go into training matches?
      - force_training: Boolean, is your bot only going into training matches? (only if allow_training)
      - training_timeout: Integer, How many seconds will your bot wait until going into a training match (only if allow_training and not force_training)
  - "get_state"
    - Ask the server about your internal state, server will reply with "rtn_state"
  - "disconnect"
    - Politely disconnect
  - "update_state": update_state
    - Send the server a list of square to turn to your colour.
    - Only those that are empty will be changed
    - Nested coords list format
      - [[0,0], [0,1], [100,22]...]


You're probably going to want to write a client. Here's how:

1. Connect to the central arena server.
  - Host `pyke.catbus.co.uk`
  - Port `9999`
2. Wait until server responds with `{'state': 'connecting'}`
3. Send identification `{"author": "PPCG Username", "name": "Awesome Bot!"}`
4. Wait until server responds with `{'state': 'config'}`
5. Send configuration `{'allow_training': true, 'force_training': true}`
6. Wait until server responds with `{'state': 'lobby'}`
7. Wait until server responds with `{'state': 'in_game'}`
8. Wait until server responds with `{'setup_game': {'y_size': 2000, 'x_size': 2000, 'game_time': 60}}`
9. Create a (x_size, y_size) sized array filled with 0s
10. Play!


Note that the server will *not* send you the entire state of the board at any time for bandwidth reasons. You'll have to keep track of the evolving yourself. ([Here](http://rosettacode.org/wiki/Conway%27s_Game_of_Life#C) are implementations of normal *Life* in many languages. You could probably base your implementation on one of those.)

## Competition rules

* If your implementation fails to follow the protocol, you'll be disconnected - and the game will be forfeited.
* You are not allowed to willfully take advantage of a fault in the arena server.
* Have your AI decide on moves in a sane time. Calculate strategies in advance if at all possible so you'll be able to send your next move as  fast as reasonably possible.
* Finally, please be nice to the server. It's there for your enjoyment.
* Not following these rules can lead to disqualification.

## Scoring

The bot with the largest KD spread, that is, the largest positive difference between the amount of wins and the amount of losses, wins.
