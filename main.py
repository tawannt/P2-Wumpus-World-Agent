import random
import time
from environment import WumpusEnvironment
from agent import Explorer
from logic import Sentence, Symbol, Not, And, Or, Implication, model_check
from knowledgeBase import build_init_kb



def main():
    random.seed(time.time())
    N = 4
    world= WumpusEnvironment(N=N, K_wumpuses=1, pit_probability=0.2)
    kb = build_init_kb(N, world)
    explorer = Explorer(kb=kb)
    world.board[1][1].append(explorer)
    print("Initial Wumpus World:")
    world.print_board()
    print(explorer.current_pos)
    print()
    

    for thing in world.board[1][1]:
        if isinstance(thing, Explorer):
            print(thing.kb.clauses.formula())
            if ('Pit', 2, 1) in thing.kb.symbols:
                print(thing.kb.ask(Not(thing.kb.symbols[('Pit', 2, 1)])))
            else:
                print(f'{('Breeze', 1, 1)} not in KB, that maybe means that Agent didn\'t percept Breeze or ERROR ')
    
    

if __name__ == "__main__":
    main()