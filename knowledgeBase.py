from logic import Sentence, Symbol, Not, And, Or, Implication, Biconditional, model_check, forward_chaining, move_forward, shoot, grab, turn_left, turn_right, ok_to_move, to_cnf, pl_resolution
from object import Thing, Gold, Wall, Pit, Arrow, Stench, Breeze, Glitter, Bump, Scream, MoveFoward, TurnLeft, TurnRight, Grab, Shoot


class KnowledgeBase:
    '''
    Contain the KB of the problem.
    It has attribute:
        - clauses: Logic connective And(sentence1, sentence2,..., sentenceK)
    '''

    def __init__(self, knowledge=None, symbols=None, visited=[], N=8):
        self.width = N
        self.height = N
        if symbols is None:
            symbols = dict()
        self.symbols = symbols
        if knowledge is None:
            self.clauses = And()
        elif isinstance(knowledge, KnowledgeBase):
            self.clauses = knowledge.clauses
        elif isinstance(knowledge, Sentence):
            self.clauses = And(knowledge)
        # Initialize symbols for (1,1)
        self.symbols[('Wumpus', 1, 1)] = Symbol('Wumpus_1_1')
        self.symbols[('Pit', 1, 1)] = Symbol('Pit_1_1')
        self.clauses.add(Not(self.symbols[('Wumpus', 1, 1)]))
        self.clauses.add(Not(self.symbols[('Pit', 1, 1)]))
        self.visited = visited

        for x in range(1, self.width + 1):
            for y in range(1, self.height + 1):
                # Stench, Breeze -> Wumpus, Pit
                if ('Stench', y, x) not in self.symbols:
                    self.symbols[('Stench', y, x)] = Symbol(f'Stench_{y}_{x}')
                if ('Breeze', y, x) not in self.symbols:
                    self.symbols[('Breeze', y, x)] = Symbol(f'Breeze_{y}_{x}')
                if ('Pit', y, x) not in self.symbols:
                    self.symbols[('Pit', y, x)] = Symbol(f'Pit_{y}_{x}')
                if ('Wumpus', y, x) not in self.symbols:
                    self.symbols[('Wumpus', y, x)] = Symbol(f'Wumpus_{y}_{x}')
        
        

        # self.add_temporal_sentence()

    def __iadd__(self, sentence):
        if Sentence.validate(sentence) and sentence not in self.clauses:
            self.clauses.add(sentence)
        return self

    def update_action_sentence(self, agent, action, step):
        '''
        Input:
            agent: The agent do the action.
            action: An action that agent do.
            step: The step that agent do.
        '''
        actions = [move_forward(step), turn_left(step), turn_right(step), grab(agent.location, step), shoot(agent.location, agent.direction.direction, step)]
        for a in actions:
            self.symbols[a.name] = a
            if action == a:
                self.clauses.add(self.symbols[a.name])
            # else:
            #     if 'Grab' not in a.name and 'Shoot' not in a.name:
            #         self.clauses.add(Not(self.symbols[a.name]))

    def update_percept_sentence(self, pos, percepts):
        y, x = pos[:2]
        # Mark current position as safe
        # self.symbols[('SafePosition', y, x)] = Symbol(f'SafePosition_{y}_{x}')
        # self.clauses.add(self.symbols[('SafePosition', y, x)])
        if ('Pit', y, x) not in self.symbols:
            self.symbols[('Pit', y, x)] = Symbol(f'Pit_{y}_{x}')
        if ('Wumpus', y, x) not in self.symbols:
            self.symbols[('Wumpus', y, x)] = Symbol(f'Wumpus_{y}_{x}')

        # just update Not Pit or Wumpus when the pos is not in visited positions' list
        # in advanced setting (Wumpus Move) => should fix this
        if pos not in self.visited and pos != (1, 1):
            self.clauses.add(Not(self.symbols[('Pit', y, x)]))
            self.clauses.add(Not(self.symbols[('Wumpus', y, x)]))
            self.visited.append(pos)
        flags = [0, 0, 0, 0, 0]

        for percept in percepts:
            # Things perceived
            # Glitter, Bump, Stench, Breeze, Scream
            if isinstance(percept, Glitter):
                flags[0] = 1
                if ('Glitter', y, x) not in self.symbols:
                    self.symbols[('Glitter', y, x)] = Symbol(f'Glitter_{y}_{x}')
                self.clauses.add(self.symbols[('Glitter', y, x)])
            if isinstance(percept, Bump):
                flags[1] = 1
                if ('Bump', y, x) not in self.symbols:
                    self.symbols[('Bump', y, x)] = Symbol(f'Bump_{y}_{x}')
                self.clauses.add(self.symbols[('Bump', y, x)])
            if isinstance(percept, Stench):
                flags[2] = 1
                if ('Stench', y, x) not in self.symbols:
                    self.symbols[('Stench', y, x)] = Symbol(f'Stench_{y}_{x}')
                self.clauses.add(self.symbols[('Stench', y, x)])

            if isinstance(percept, Breeze):
                flags[3] = 1
                if ('Breeze', y, x) not in self.symbols:
                    self.symbols[('Breeze', y, x)] = Symbol(f'Breeze_{y}_{x}')
                self.clauses.add(self.symbols[('Breeze', y, x)])

            if isinstance(percept, Scream):
                flags[4] = 1
                if ('Scream', y, x) not in self.symbols:
                    self.symbols[('Scream', y, x)] = Symbol(f'Scream_{y}_{x}')
                self.clauses.add(self.symbols[('Scream', y, x)])

        # Things not perceived
        for i in range(len(flags)):
            if flags[i] == 0:
                if i == 0:
                    pass
                    # if ('Glitter', y, x) not in self.symbols:
                    #     self.symbols[('Glitter', y, x)] = Symbol(f'Glitter_{y}_{x}')
                    # self.clauses.add(Not(self.symbols[('Glitter', y, x)]))
                # elif i == 1:
                #     if ('Bump', y, x) not in self.symbols:
                #         self.symbols[('Bump', y, x)] = Symbol(f'Bump_{y}_{x}')
                #     self.clauses.add(Not(self.symbols[('Bump', y, x)]))
                elif i == 2:
                    if ('Stench', y, x) not in self.symbols:
                        self.symbols[('Stench', y, x)] = Symbol(f'Stench_{y}_{x}')
                    self.clauses.add(Not(self.symbols[('Stench', y, x)]))
                elif i == 3:
                    if ('Breeze', y, x) not in self.symbols:
                        self.symbols[('Breeze', y, x)] = Symbol(f'Breeze_{y}_{x}')
                    self.clauses.add(Not(self.symbols[('Breeze', y, x)]))
                # elif i == 4:
                #     if ('Scream', y, x) not in self.symbols:
                #         self.symbols[('Scream', y, x)] = Symbol(f'Scream_{y}_{x}')
                #     self.clauses.add(Not(self.symbols[('Scream', y, x)]))
            # else:
            #     if i == 1:
            #         pass
            #     elif i == 2:  # Stench
            #         consequents = Or()
            #         if y > 1:
            #             if ('Wumpus', y - 1, x) not in self.symbols:
            #                 self.symbols[('Wumpus', y - 1, x)] = Symbol(f'Wumpus_{y-1}_{x}')
            #             consequents.add(self.symbols[('Wumpus', y-1, x)])

            #         if y < self.height:
            #             if ('Wumpus', y + 1, x) not in self.symbols:
            #                 self.symbols[('Wumpus', y + 1, x)] = Symbol(f'Wumpus_{y+1}_{x}')
            #             consequents.add(self.symbols[('Wumpus', y + 1, x)])

            #         if x > 1:
            #             if ('Wumpus', y, x - 1) not in self.symbols:
            #                 self.symbols[('Wumpus', y, x - 1)] = Symbol(f'Wumpus_{y}_{x-1}')
            #             consequents.add(self.symbols[('Wumpus', y, x-1)])

            #         if x < self.width:
            #             if ('Wumpus', y, x + 1) not in self.symbols:
            #                 self.symbols[('Wumpus', y, x + 1)] = Symbol(f'Wumpus_{y}_{x+1}')
            #             consequents.add(self.symbols[('Wumpus', y, x+1)])

            #         if consequents.disjuncts:
            #             self.clauses.add(Implication(self.symbols[('Stench', y, x)], consequents))
            #     elif i == 3:  # Breeze
            #         consequents = Or()
            #         if y > 1:
            #             if ('Pit', y - 1, x) not in self.symbols:
            #                 self.symbols[('Pit', y-1, x)] = Symbol(f'Pit_{y-1}_{x}')
            #             consequents.add(self.symbols[('Pit', y-1, x)])

            #         if y < self.height:
            #             if ('Pit', y + 1, x) not in self.symbols:
            #                 self.symbols[('Pit', y+1, x)] = Symbol(f'Pit_{y+1}_{x}')
            #             consequents.add(self.symbols[('Pit', y+1, x)])

            #         if x > 1:
            #             if ('Pit', y, x - 1) not in self.symbols:
            #                 self.symbols[('Pit', y, x-1)] = Symbol(f'Pit_{y}_{x-1}')
            #             consequents.add(self.symbols[('Pit', y, x-1)])

            #         if x < self.width:
            #             if ('Pit', y, x + 1) not in self.symbols:
            #                 self.symbols[('Pit', y, x+1)] = Symbol(f'Pit_{y}_{x+1}')
            #             consequents.add(self.symbols[('Pit', y, x+1)])

            #         if consequents.disjuncts:
            #             self.clauses.add(Implication(self.symbols[('Breeze', y, x)], consequents))
            #     elif i == 4:
            #         pass
                
        consequents = Or()
        if y > 1:
            if ('Wumpus', y - 1, x) not in self.symbols:
                self.symbols[('Wumpus', y - 1, x)] = Symbol(f'Wumpus_{y-1}_{x}')
            consequents.add(self.symbols[('Wumpus', y-1, x)])

        if y < self.height:
            if ('Wumpus', y + 1, x) not in self.symbols:
                self.symbols[('Wumpus', y + 1, x)] = Symbol(f'Wumpus_{y+1}_{x}')
            consequents.add(self.symbols[('Wumpus', y + 1, x)])

        if x > 1:
            if ('Wumpus', y, x - 1) not in self.symbols:
                self.symbols[('Wumpus', y, x - 1)] = Symbol(f'Wumpus_{y}_{x-1}')
            consequents.add(self.symbols[('Wumpus', y, x-1)])

        if x < self.width:
            if ('Wumpus', y, x + 1) not in self.symbols:
                self.symbols[('Wumpus', y, x + 1)] = Symbol(f'Wumpus_{y}_{x+1}')
            consequents.add(self.symbols[('Wumpus', y, x+1)])

        if consequents.disjuncts:
            self.clauses.add(Or(Not(self.symbols[('Stench', y, x)]), consequents))
            self.clauses.add(Implication(consequents, self.symbols[('Stench', y, x)]))
            
        consequents = Or()
        if y > 1:
            if ('Pit', y - 1, x) not in self.symbols:
                self.symbols[('Pit', y-1, x)] = Symbol(f'Pit_{y-1}_{x}')
            consequents.add(self.symbols[('Pit', y-1, x)])

        if y < self.height:
            if ('Pit', y + 1, x) not in self.symbols:
                self.symbols[('Pit', y+1, x)] = Symbol(f'Pit_{y+1}_{x}')
            consequents.add(self.symbols[('Pit', y+1, x)])

        if x > 1:
            if ('Pit', y, x - 1) not in self.symbols:
                self.symbols[('Pit', y, x-1)] = Symbol(f'Pit_{y}_{x-1}')
            consequents.add(self.symbols[('Pit', y, x-1)])

        if x < self.width:
            if ('Pit', y, x + 1) not in self.symbols:
                self.symbols[('Pit', y, x+1)] = Symbol(f'Pit_{y}_{x+1}')
            consequents.add(self.symbols[('Pit', y, x+1)])

        if consequents.disjuncts:
            self.clauses.add(Or(Not(self.symbols[('Breeze', y, x)]), consequents))
            self.clauses.add(Implication(consequents, self.symbols[('Breeze', y, x)]))

    def add_temporal_sentence(self):
        for x in range(1, self.width + 1):
            for y in range(1, self.height + 1):
                # Stench, Breeze -> Wumpus, Pit
                if ('Stench', y, x) not in self.symbols:
                    self.symbols[('Stench', y, x)] = Symbol(f'Stench_{y}_{x}')

                if ('Breeze', y, x) not in self.symbols:
                    self.symbols[('Breeze', y, x)] = Symbol(f'Breeze_{y}_{x}')

                wumpus_consequents = Or()
                pit_consequents = Or()
                if y > 1:
                    if ('Wumpus', y - 1, x) not in self.symbols:
                        self.symbols[('Wumpus', y - 1, x)] = Symbol(f'Wumpus_{y-1}_{x}')
                    wumpus_consequents.add(self.symbols[('Wumpus', y-1, x)])
                    # self.clauses.add(Implication(self.symbols[('Stench', y, x)], self.symbols[('Wumpus', y-1, x)]))

                    if ('Pit', y - 1, x) not in self.symbols:
                        self.symbols[('Pit', y-1, x)] = Symbol(f'Pit_{y-1}_{x}')
                    pit_consequents.add(self.symbols[('Pit', y-1, x)])
                    # self.clauses.add(Implication(self.symbols[('Breeze', y, x)], self.symbols[('Pit', y-1, x)]))


                if y < self.height:
                    if ('Wumpus', y + 1, x) not in self.symbols:
                        self.symbols[('Wumpus', y + 1, x)] = Symbol(f'Wumpus_{y+1}_{x}')
                    wumpus_consequents.add(self.symbols[('Wumpus', y+1, x)])
                    # self.clauses.add(Implication(self.symbols[('Stench', y, x)], self.symbols[('Wumpus', y+1, x)]))

                    if ('Pit', y + 1, x) not in self.symbols:
                        self.symbols[('Pit', y+1, x)] = Symbol(f'Pit_{y+1}_{x}')
                    pit_consequents.add(self.symbols[('Pit', y+1, x)])
                    # self.clauses.add(Implication(self.symbols[('Breeze', y, x)], self.symbols[('Pit', y+1, x)]))


                if x > 1:
                    if ('Wumpus', y, x - 1) not in self.symbols:
                        self.symbols[('Wumpus', y, x - 1)] = Symbol(f'Wumpus_{y}_{x-1}')
                    wumpus_consequents.add(self.symbols[('Wumpus', y, x-1)])
                    # self.clauses.add(Implication(self.symbols[('Stench', y, x)], self.symbols[('Wumpus', y, x-1)]))
                    

                    if ('Pit', y, x - 1) not in self.symbols:
                        self.symbols[('Pit', y, x-1)] = Symbol(f'Pit_{y}_{x-1}')
                    pit_consequents.add(self.symbols[('Pit', y, x-1)])
                    # self.clauses.add(Implication(self.symbols[('Breeze', y, x)], self.symbols[('Pit', y, x-1)]))

                if x < self.width:
                    if ('Wumpus', y, x + 1) not in self.symbols:
                        self.symbols[('Wumpus', y, x + 1)] = Symbol(f'Wumpus_{y}_{x+1}')
                    wumpus_consequents.add(self.symbols[('Wumpus', y, x+1)])
                    # self.clauses.add(Implication(self.symbols[('Stench', y, x)], self.symbols[('Wumpus', y, x+1)]))

                    if ('Pit', y, x + 1) not in self.symbols:
                        self.symbols[('Pit', y, x+1)] = Symbol(f'Pit_{y}_{x+1}')
                    pit_consequents.add(self.symbols[('Pit', y, x+1)])
                    # self.clauses.add(Implication(self.symbols[('Breeze', y, x)], self.symbols[('Pit', y, x+1)]))

                if wumpus_consequents.disjuncts:
                    self.clauses.add(Biconditional(self.symbols[('Stench', y, x)], wumpus_consequents))
                
                if pit_consequents.disjuncts:
                    self.clauses.add(Biconditional(self.symbols[('Breeze', y, x)], pit_consequents))
                    
                
    def list_clauses_with_premise(self, p):
        # rules (not including facts) that having p in the premise
        # print(f'p: {p}')
        list_rules = []
        for k in self.clauses.conjuncts:
            # print(f'k: {k}')
            # # print({k.symbols}
            # if isinstance(k, Implication):
            #     print(f'k.antecedent.symbols(): {k.antecedent.symbols()}')
            #     if p.name in k.antecedent.symbols():
            #         print('p in')
            if isinstance(k, Implication) and p.name in k.antecedent.symbols():
                list_rules.append(k)
        return list_rules



    # Inference with the query
    def ask(self, query: Sentence) -> bool:
        # return model_check(self, query)
        # return forward_chaining(self, query)
        return pl_resolution(self, query)


def build_init_kb(N, environment):
    kb = KnowledgeBase(N=N)
    percepts = environment.percept((1, 1))
    kb.update_percept_sentence((1, 1), percepts)
    return kb

