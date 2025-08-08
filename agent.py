from direction import Direction

from logic import Sentence, Symbol, Not, And, Or, Implication
from object import Thing, Gold, Wall, Pit, Arrow, Stench, Breeze, Glitter, Bump, Scream


class Agent(Thing):
    alive = True
    location = tuple()

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
        self.location = pos

    def mark_safe_location(self, pos):
        '''Check the input location is safe or not'''
        y, x = pos[:2]
        # TODO: if "add_temporal_sentence" => remove this
        # if ('Pit', y, x) not in self.kb.symbols and ('Wumpus', y, x) not in self.kb.symbols:
        #     return True
        if self.kb.ask(Not((self.kb.symbols[('Pit', y, x)]))):
            self.kb += Not((self.kb.symbols[('Pit', y, x)]))
            if self.kb.ask(Not(self.kb.symbols[('Wumpus', y, x)])):
                self.kb += Not((self.kb.symbols[('Wumpus', y, x)]))
                return True
        return False

    def can_grab(self, thing):
        return thing.__class__ == Gold

class Wumpus(Agent):
    screamed = False
    pass
