# Base class for objects in the Wumpus World

import sys
import datetime

class Logger:
    def __init__(self, filename):
        self.console = sys.stdout
        self.file = open(filename, 'a', encoding='utf-8')
    
    def write(self, message):
        # Write to console
        self.console.write(message)
        # Write to file with timestamp
        # timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.file.write(f'{message}')
        self.file.flush()
    
    def flush(self):
        self.console.flush()
        self.file.flush()
    
    def __del__(self):
        self.file.close()


class Thing:
    position = tuple()

# Percepts
class Stench(Thing): pass
class Breeze(Thing): pass
class Glitter(Thing): pass
class Bump(Thing): pass
class Scream(Thing): pass

# Objects
class Gold(Thing):
    def __eq__(self, rhs):
        return rhs.__class__ == Gold
class Wall(Thing): pass
class Pit(Thing): pass
class Arrow(Thing): pass
class Wumpus(Thing): pass

# Actions
class MoveForward(Thing): pass
class TurnLeft(Thing): pass
class TurnRight(Thing): pass
class Grab(Thing): pass
class Shoot(Thing): pass