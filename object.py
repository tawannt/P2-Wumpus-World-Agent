# Base class for objects in the Wumpus World
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