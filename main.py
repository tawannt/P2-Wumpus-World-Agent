import random
import time
from environment import WumpusEnvironment
from agent import Explorer
from logic import Sentence, Symbol, Not, And, Or, Implication, model_check, move_forward, shoot, grab, turn_left, turn_right, ok_to_move
from knowledgeBase import build_init_kb
from direction import Direction



def main():
    random.seed(time.time())
    N = 4
    world= WumpusEnvironment(N=N, K_wumpuses=2, pit_probability=0.2)
    kb = build_init_kb(N, world)
    explorer = Explorer(kb=kb)
    world.board[1][1].append(explorer)
    world.agents.append(explorer)
    print("Initial Wumpus World:")
    world.print_board()
    print()


    
    # percepts = world.exe_action(explorer, (1, 1), 'TurnLeft')
    # print('After Turning Left: ')
    # world.print_board()
    # explorer.kb.update_action_sentence(explorer, turn_left(0), 0)
    # print(explorer.kb.clauses.formula())
    # percepts = world.exe_action(explorer, (1, 1), 'Shoot')
    # explorer.kb.update_action_sentence(explorer, shoot(explorer.location, explorer.direction.direction, 1), 1)
    # explorer.kb.update_percept_sentence(explorer.location, percepts)

    # print('After Shooting: ')
    # world.print_board()
    # print(explorer.kb.clauses.formula())
    
    for thing in world.board[1][1]:
        if isinstance(thing, Explorer):
            print(thing.kb.clauses.formula())
            if ('Pit', 2, 1) in thing.kb.symbols:
                print(thing.kb.ask(thing.kb.symbols[('Pit', 2, 1)]))
            else:
                print(f'{('Pit', 2, 1)} not in KB, that maybe means that Agent didn\'t percept Breeze or ERROR ')
    
    
    

if __name__ == "__main__":
    main()