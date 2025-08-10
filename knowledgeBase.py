from logic import Sentence, Symbol, Not, And, Or, Implication, Biconditional, move_forward, shoot, grab, turn_left, turn_right, ok_to_move, to_cnf, pl_resolution
from object import Thing, Gold, Wall, Pit, Arrow, Stench, Breeze, Glitter, Bump, Scream, MoveForward, TurnLeft, TurnRight, Grab, Shoot

class KnowledgeBase:
    def __init__(self, knowledge=None, symbols=None, visited=None, N=8):
        self.width = N
        self.height = N
        if visited is None:
            visited = [(1, 1)]
        self.visited = visited
        if symbols is None:
            symbols = {}
        self.symbols = symbols
        if knowledge is None:
            self.clauses = And()
        elif isinstance(knowledge, KnowledgeBase):
            self.clauses = knowledge.clauses
        elif isinstance(knowledge, Sentence):
            self.clauses = And(to_cnf(knowledge))

        # Initialize symbols for all cells
        for x in range(1, self.width + 1):
            for y in range(1, self.height + 1):
                self.symbols[('Wumpus', y, x)] = Symbol(f'Wumpus_{y}_{x}')
                self.symbols[('Pit', y, x)] = Symbol(f'Pit_{y}_{x}')
                self.symbols[('Stench', y, x)] = Symbol(f'Stench_{y}_{x}')
                self.symbols[('Breeze', y, x)] = Symbol(f'Breeze_{y}_{x}')
                self.symbols[('Glitter', y, x)] = Symbol(f'Glitter_{y}_{x}')
                self.symbols[('Bump', y, x)] = Symbol(f'Bump_{y}_{x}')
                self.symbols[('Scream', y, x)] = Symbol(f'Scream_{y}_{x}')

        # Add initial knowledge: (1,1) is safe
        self.clauses.add(to_cnf(Not(self.symbols[('Wumpus', 1, 1)])))
        self.clauses.add(to_cnf(Not(self.symbols[('Pit', 1, 1)])))

        # Add temporal sentences for logical relationships
        self.add_temporal_sentence()


    def __iadd__(self, sentence):
        if Sentence.validate(sentence) and to_cnf(sentence) not in self.clauses.conjuncts:
            self.clauses.add(to_cnf(sentence))
        return self

    def add_temporal_sentence(self):
        for x in range(1, self.width + 1):
            for y in range(1, self.height + 1):
                wumpus_consequents = Or()
                pit_consequents = Or()
                if y > 1:
                    wumpus_consequents.add(self.symbols[('Wumpus', y - 1, x)])
                    pit_consequents.add(self.symbols[('Pit', y - 1, x)])
                if y < self.height:
                    wumpus_consequents.add(self.symbols[('Wumpus', y + 1, x)])
                    pit_consequents.add(self.symbols[('Pit', y + 1, x)])
                if x > 1:
                    wumpus_consequents.add(self.symbols[('Wumpus', y, x - 1)])
                    pit_consequents.add(self.symbols[('Pit', y, x - 1)])
                if x < self.width:
                    wumpus_consequents.add(self.symbols[('Wumpus', y, x + 1)])
                    pit_consequents.add(self.symbols[('Pit', y, x + 1)])
                if wumpus_consequents.disjuncts:
                    self.clauses.add(to_cnf(Biconditional(self.symbols[('Stench', y, x)], wumpus_consequents)))
                if pit_consequents.disjuncts:
                    self.clauses.add(to_cnf(Biconditional(self.symbols[('Breeze', y, x)], pit_consequents)))

    def update_action_sentence(self, agent, action, step):
        actions = [
            move_forward(step),
            turn_left(step),
            turn_right(step),
            grab(agent.location, step),
            shoot(agent.location, agent.direction.direction, step)
        ]
        for a in actions:
            self.symbols[a.name] = a
            if action == a.name:
                self.clauses.add(to_cnf(self.symbols[a.name]))

    def update_percept_sentence(self, pos, percepts):
        y, x = pos[:2]
        if pos not in self.visited and pos != (1, 1):
            self.clauses.add(to_cnf(Not(self.symbols[('Pit', y, x)])))
            self.clauses.add(to_cnf(Not(self.symbols[('Wumpus', y, x)])))
            self.visited.append(pos)
        for percept_type in [Glitter, Bump, Stench, Breeze, Scream]:
            symbol_key = (percept_type.__name__, y, x)
            if any(isinstance(percept, percept_type) for percept in percepts):
                self.clauses.add(to_cnf(self.symbols[symbol_key]))
            else:
                self.clauses.add(to_cnf(Not(self.symbols[symbol_key])))

    # def list_clauses_with_premise(self, p):
    #     list_rules = []
    #     for k in self.clauses.conjuncts:
    #         if isinstance(k, Implication) and p.name in k.antecedent.symbols():
    #             list_rules.append(k)
    #         elif isinstance(k, Biconditional) and p.name in k.left.symbols():
    #             list_rules.append(k)
    #     return list_rules

    def ask(self, query):
        return pl_resolution(self, query)


def build_init_kb(N, environment):
    kb = KnowledgeBase(N=N)  # Set single_wumpus=True for exactly one Wumpus
    percepts = environment.percept((1, 1))
    kb.update_percept_sentence((1, 1), percepts)
    return kb