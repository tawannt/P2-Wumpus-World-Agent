import random
from object import Stench, Breeze
from agent import Explorer, Stench, Breeze
from direction import Direction
from environment import WumpusEnvironment
from knowledgeBase import KnowledgeBase, build_init_kb
from logic import Symbol, Not, And, Biconditional, Implication, Or

def main():
    kb = KnowledgeBase(N=3)
    if ('Stench', 1, 1) not in kb.symbols:
        kb.symbols[('Stench', 1, 1)] = Symbol(f'Stench_{1}_{1}')
    kb.clauses.add(kb.symbols[('Stench', 1, 1)])
    kb.clauses.add(Biconditional(kb.symbols[('Stench', 1, 1)], Or(Symbol('Pit_1_2'), Symbol('Pit_2_1'))))
    
    print(kb.clauses.formula())
    print()
    if ('Stench', 1, 3) not in kb.symbols:
        kb.symbols[('Stench', 1, 3)] = Symbol(f'Stench_{1}_{3}')
    kb.clauses.add(Biconditional(kb.symbols[('Stench', 1, 3)], Or(Symbol('Pit_1_2'), Symbol('Pit_2_3'))))
    kb.clauses.add(Not(kb.symbols[('Stench', 1, 3)]))
    print(kb.clauses.formula())
    print()

    print(kb.ask(Symbol('Pit_1_2')))
    # print(kb.ask(Symbol('Pit_2_1')))

if __name__ == "__main__":
    main()