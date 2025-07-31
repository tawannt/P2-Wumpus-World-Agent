# marker Interface class
class Thing():
    position = tuple()

class Gold(Thing):

    def __eq__(self, rhs):
        """All Gold are equal"""
        return rhs.__class__ == Gold

    pass


class Wall(Thing): pass
class Pit(Thing): pass
class Arrow(Thing): pass

# Percepts
class Stench(Thing): pass
class Breeze(Thing): pass
class Glitter(Thing): pass
class Bump(Thing): pass
class Scream(Thing): pass

# Action
class MoveFoward(Thing): pass
class TurnLeft(Thing): pass
class TurnRight(Thing): pass
class Grab(Thing): pass
class Shoot(Thing): pass
class ClimbOut(Thing): pass

# Inference
class SafePosition(Thing): pass

