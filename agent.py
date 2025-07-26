from direction import Direction

from logic import Sentence, Symbol, Not, And, Or, Implication
from object import Thing, Gold, Wall, Pit, Arrow, Stench, Breeze, Glitter, Bump, Scream

class Agent(Thing):
    alive = True

# Fixed Explorer
class Explorer(Agent):
    holding = []
    has_arrow = True
    killed_by = ""
    direction = Direction("right")
    performance = 0
    safe_cells = set([(1,1)])

    def __init__(self, kb, visited=None, pos=(1, 1)):
        if visited is None:
            visited = set([(1, 1)])
        self.kb = kb
        self.visited = visited
        self.current_pos = pos

    def mark_safe_cell(self, pos):
        pass

    def can_grab(self, thing):
        return thing.__class__ == Gold

class Wumpus(Agent):
    screamed = False
    pass