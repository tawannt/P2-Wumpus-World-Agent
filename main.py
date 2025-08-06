import random
from object import Stench, Breeze
from agent import Explorer, Stench, Breeze
from direction import Direction
from environment import WumpusEnvironment
from logic import Sentence, Symbol, Not, And, Or, Implication, Biconditional, model_check, forward_chaining, move_forward, shoot, grab, turn_left, turn_right, ok_to_move, to_cnf, pl_resolution
from knowledgeBase import build_init_kb
# def main():
#     kb = KnowledgeBase(N=3)
#     if ('Stench', 1, 1) not in kb.symbols:
#         kb.symbols[('Stench', 1, 1)] = Symbol(f'Stench_{1}_{1}')
#     kb.clauses.add(kb.symbols[('Stench', 1, 1)])
#     kb.clauses.add(Biconditional(kb.symbols[('Stench', 1, 1)], Or(Symbol('Pit_1_2'), Symbol('Pit_2_1'))))
    
#     print(kb.clauses.formula())
#     print()
#     if ('Stench', 1, 3) not in kb.symbols:
#         kb.symbols[('Stench', 1, 3)] = Symbol(f'Stench_{1}_{3}')
#     kb.clauses.add(Biconditional(kb.symbols[('Stench', 1, 3)], Or(Symbol('Pit_1_2'), Symbol('Pit_2_3'))))
#     kb.clauses.add(Not(kb.symbols[('Stench', 1, 3)]))
#     print(kb.clauses.formula())
#     print()

#     print(kb.ask(Symbol('Pit_1_2')))
#     # print(kb.ask(Symbol('Pit_2_1')))

# if __name__ == "__main__":
#     main()


import random
import time
import ast

def main():
    random.seed(time.time())
    N = 6
    world = WumpusEnvironment(N=N, K_wumpuses=2, pit_probability=0.2)
    kb = build_init_kb(N, world)
    explorer = Explorer(kb=kb)
    world.board[1][1].append(explorer)
    world.agents.append(explorer)

    print("Initial Wumpus World:")
    world.print_board()
    print()
    print(explorer.kb.clauses.formula())

    # kb = KnowledgeBase(N=3)
    # kb.clauses.add(Symbol('Breeze_1_1'))
    # kb.clauses.add(Not(Symbol('Pit_1_1')))
    # kb.clauses.add(Implication(Symbol('Breeze_1_1'), Or(Symbol('Pit_2_1'), Symbol('Pit_1_2'))))
    # print(kb.clauses.formula())
    # print(kb.ask(Symbol('Pit_2_1')))  # Should be False
    # kb.clauses.add(Not(Symbol('Pit_1_2')))
    # print()
    # print()
    # print()
    # print()
    # print(kb.clauses.formula())
    # print(kb.ask(Symbol('Pit_2_1')))  # Should be True
    while True:
        print("\n--- QUERY PHASE ---")
        try:
            num_query = int(input("Num queries: "))
            for i in range(num_query):
                query_input = input("Enter a query tuple (e.g., ('Pit', 2, 1)): ")
                parsed = ast.literal_eval(query_input)
                if not (isinstance(parsed, tuple) and len(parsed) == 3):
                    print("Invalid format. Must be a tuple like ('Pit', 2, 1).")
                    continue
                name, y, x = parsed

                if parsed not in explorer.kb.symbols:
                    print(f"Symbol {parsed} not in KB symbols.")
                    continue

                symbol = explorer.kb.symbols[parsed]
                print("Checking with forward chaining...")
                # result = forward_chaining(explorer.kb, symbol)
                result = explorer.kb.ask(symbol)
                if result:
                    explorer.kb.clauses.add(symbol)
                print("Entailed (forward chaining):", result)

                # print("Checking with model checking...")
                # result = model_check(explorer.kb, symbol)
                # print("Entailed (model checking):", result)

        except Exception as e:
            print("Error:", e)
            continue

        print("\n--- ACTION PHASE ---")
        try:
            
            action_input = input("Enter action (e.g., TurnLeft 0, Shoot 2 1 right 3): ")
            parts = action_input.strip().split()

            if not parts:
                continue

            action_type = parts[0].lower()

            if action_type == "turnleft" and len(parts) == 2:
                step = int(parts[1])
                action_symbol = turn_left(step)
            elif action_type == "turnright" and len(parts) == 2:
                step = int(parts[1])
                action_symbol = turn_right(step)
            elif action_type == "moveforward" and len(parts) == 2:
                step = int(parts[1])
                action_symbol = move_forward(step)
            elif action_type == "grab" and len(parts) == 3:
                y, x = int(parts[1]), int(parts[2])
                step = int(input("Enter step: "))
                action_symbol = grab((y, x), step)
            elif action_type == "shoot" and len(parts) == 5:
                y, x = int(parts[1]), int(parts[2])
                direction = parts[3]
                step = int(parts[4])
                action_symbol = shoot((y, x), direction, step)
            else:
                print("Unknown or badly formatted action.")
                continue

            # Update KB with action
            # explorer.kb.update_action_sentence(explorer, action_symbol, step)
            print(explorer.location)
            percepts = world.exe_action(explorer, explorer.location, parts[0])  # this assumes exe_action supports the action string
            # explorer.kb.update_percept_sentence(explorer.location, percepts)
            percepts = world.percept(explorer.location)
            
            explorer.kb.update_percept_sentence(explorer.location, percepts)

            print("Action executed. Updated board:")
            print(explorer.kb.clauses.formula())
            world.print_board()


        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()