from logic import Sentence, Symbol, Not, And, Or, Implication, Biconditional, move_forward, shoot, grab, turn_left, turn_right, ok_to_move, to_cnf, pl_resolution, flatten_and_clauses, normalize_clause
from object import Thing, Gold, Wall, Pit, Arrow, Stench, Breeze, Glitter, Bump, Scream, MoveForward, TurnLeft, TurnRight, Grab, Shoot
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KnowledgeBase:
    def __init__(self, knowledge=None, symbols=None, visited=None, N=8):
        self.width = N
        self.height = N
        self.visited = set(visited or [(1, 1)])
        self.symbols = symbols or {}
        self.clauses = And() if knowledge is None else (knowledge.clauses if isinstance(knowledge, KnowledgeBase) else And(to_cnf(knowledge)))
        self.clause_formulas = set()  # Track unique clause formulas

        # Initialize symbols
        for x in range(1, self.width + 1):
            for y in range(1, self.height + 1):
                for obj in ['Wumpus', 'Pit', 'Stench', 'Breeze', 'Glitter', 'Bump', 'Scream']:
                    self.symbols[(obj, y, x)] = Symbol(f'{obj}_{y}_{x}')

        # Add initial knowledge
        self.clauses.add(to_cnf(Not(self.symbols[('Wumpus', 1, 1)])))
        self.clauses.add(to_cnf(Not(self.symbols[('Pit', 1, 1)])))
        self.add_temporal_sentence()
        self.last_shot = None

    def __iadd__(self, sentence):
        sentence_cnf = to_cnf(sentence)
        formula = sentence_cnf.formula()
        if formula not in self.clause_formulas:
            logging.info(f"Adding clause: {formula}")
            self.clauses.add(sentence_cnf)
            self.clause_formulas.add(formula)
        return self
    
    def add_temporal_sentence(self):
        for x in range(1, self.width + 1):
            for y in range(1, self.height + 1):
                self.clauses.add(to_cnf(Not(And(self.symbols[('Wumpus', y, x)], self.symbols[('Pit', y, x)]))))
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
        # actions = [
        #     move_forward(step),
        #     turn_left(step),
        #     turn_right(step),
        # ]
        if action == 'Shoot':
            self.symbols[('Shoot', agent.location[0], agent.location[1], agent.direction.direction, step)] = shoot(agent.location, agent.direction.direction, step)
            self.clauses.add(to_cnf(self.symbols[('Shoot', agent.location[0], agent.location[1], agent.direction.direction, step)]))
            self.last_shot = (agent.location, agent.direction, step)
        # for a in actions:
        #     self.symbols[(a, )] = a
        #     if action == a:
        #         self.clauses.add(to_cnf(self.symbols[a.name]))

    def update_percept_sentence(self, pos, percepts):
        y, x = pos[:2]
        if pos not in self.visited and pos != (1, 1):
            self += Not(self.symbols[('Pit', y, x)])
            self += Not(self.symbols[('Wumpus', y, x)])
            self.visited.add(pos)

        if self.last_shot:
            pos, direction, step = self.last_shot
            if any(isinstance(p, Scream) for p in percepts):
                self.remove_clause(Not(self.symbols[('Scream', y, x)]))
                self += self.symbols[('Scream', y, x)]
                arrow_travel = direction.move_forward(pos)
                if (arrow_travel[0] > 0 and arrow_travel[0] <= self.height and 
                        arrow_travel[1] > 0 and arrow_travel[1] <= self.width):
                    arrow_y, arrow_x = arrow_travel[:2]
                    self += Or(Not(self.symbols[('Shoot', pos[0], pos[1], direction.direction, step)]), 
                              Not(self.symbols[('Wumpus', arrow_y, arrow_x)]))
            self.last_shot = None
        else:
            for percept_type in [Glitter, Stench, Breeze, Bump]:
                symbol_key = (percept_type.__name__, y, x)
                if any(isinstance(percept, percept_type) for percept in percepts):
                    if percept_type.__name__ == 'Stench' and f"¬({self.symbols[symbol_key].formula()})" in self.clause_formulas:
                        self.remove_clause(Not(self.symbols[symbol_key]))
                        self.clause_formulas.remove( f"¬({self.symbols[symbol_key].formula()})")
                    self += self.symbols[symbol_key]
                else:
                    if percept_type.__name__ not in ['Bump', 'Glitter']:
                        if f"{self.symbols[symbol_key].formula()}" in self.clause_formulas:
                            self.remove_clause(self.symbols[symbol_key])
                            self.clause_formulas.remove(f"{self.symbols[symbol_key].formula()}")
                        self += Not(self.symbols[symbol_key])

    def remove_clause(self, sentence):
        formula = to_cnf(sentence).formula()
        if formula in self.clause_formulas:
            logging.info(f"Remove clause: {formula}")
            self.clause_formulas.remove(formula)
            new_clauses = [c for c in self.clauses.conjuncts if c.formula() != formula]
            self.clauses = And(*new_clauses) if new_clauses else And()

    def ask(self, query):
        return pl_resolution(self, query)


def build_init_kb(N, environment):
    kb = KnowledgeBase(N=N)  # Set single_wumpus=True for exactly one Wumpus
    percepts = environment.percept((1, 1))
    kb.update_percept_sentence((1, 1), percepts)
    return kb