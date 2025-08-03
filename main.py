import random
import time
from environment import WumpusEnvironment
from agent import Explorer
from logic import Sentence, Symbol, Not, And, Or, Implication, Biconditional, model_check, forward_chaining, move_forward, shoot, grab, turn_left, turn_right, ok_to_move, to_cnf, pl_resolution
from knowledgeBase import build_init_kb, KnowledgeBase
from direction import Direction

def test_forward_chaining():
    # Define some symbols
    A = Symbol("A")
    B = Symbol("B")
    C = Symbol("C")
    D = Symbol("D")
    E = Symbol("E")

    # Knowledge base: A, A ∧ B => C, C => D, D ∧ E => B
    kb = KnowledgeBase()
    kb.clauses = And(
        A,
        B,
        Implication(And(A, B), C),
        Implication(C, D),
        Implication(And(D, E), B)  # This should not fire because E is not a fact
    )

    # Test entailments
    print("Query C:", forward_chaining(kb, C))  # Expect True (A ∧ B => C)
    print("Query D:", forward_chaining(kb, D))  # Expect True (via C)
    print("Query E:", forward_chaining(kb, E))  # Expect False (never inferred)
    print("Query B:", forward_chaining(kb, B))  # Expect True (initial fact)

# def main():
#     test_forward_chaining()
def main():
    random.seed(time.time())
    N = 6
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
            # print(thing.kb.clauses.formula())
            if ('Breeze', 1, 1) in thing.kb.symbols:
                if thing.kb.symbols[('Breeze', 1, 1)] in thing.kb.clauses.conjuncts:
                    print('yes')
                print(thing.kb.ask(thing.kb.symbols[('Breeze', 1, 1)]))
                
            else:
                print(f'{('Pit', 2, 1)} not in KB, that maybe means that Agent didn\'t percept Breeze or ERROR ')
    


    

if __name__ == "__main__":
    main()
# import random
# import time
# import ast

# def main():
#     random.seed(time.time())
#     N = 6
#     world = WumpusEnvironment(N=N, K_wumpuses=2, pit_probability=0.2)
#     kb = build_init_kb(N, world)
#     explorer = Explorer(kb=kb)
#     world.board[1][1].append(explorer)
#     world.agents.append(explorer)

#     print("Initial Wumpus World:")
#     world.print_board()
#     print()
#     print(explorer.kb.clauses.formula())

#     # kb = KnowledgeBase(N=3)
#     # kb.clauses.add(Symbol('Breeze_1_1'))
#     # kb.clauses.add(Not(Symbol('Pit_1_1')))
#     # kb.clauses.add(Implication(Symbol('Breeze_1_1'), Or(Symbol('Pit_2_1'), Symbol('Pit_1_2'))))
#     # print(kb.clauses.formula())
#     # print(kb.ask(Symbol('Pit_2_1')))  # Should be False
#     # kb.clauses.add(Not(Symbol('Pit_1_2')))
#     # print()
#     # print()
#     # print()
#     # print()
#     # print(kb.clauses.formula())
#     # print(kb.ask(Symbol('Pit_2_1')))  # Should be True
#     while True:
#         print("\n--- QUERY PHASE ---")
#         try:
#             query_input = input("Enter a query tuple (e.g., ('Pit', 2, 1)): ")
#             parsed = ast.literal_eval(query_input)
#             if not (isinstance(parsed, tuple) and len(parsed) == 3):
#                 print("Invalid format. Must be a tuple like ('Pit', 2, 1).")
#                 continue

#             name, y, x = parsed
#             if parsed not in explorer.kb.symbols:
#                 print(f"Symbol {parsed} not in KB symbols.")
#                 continue

#             symbol = explorer.kb.symbols[parsed]
#             print("Checking with forward chaining...")
#             # result = forward_chaining(explorer.kb, symbol)
#             result = explorer.kb.ask(symbol)
#             print("Entailed (forward chaining):", result)

#             # print("Checking with model checking...")
#             # result = model_check(explorer.kb, symbol)
#             # print("Entailed (model checking):", result)

#         except Exception as e:
#             print("Error:", e)
#             continue

#         print("\n--- ACTION PHASE ---")
#         try:
#             action_input = input("Enter action (e.g., TurnLeft 0, Shoot 2 1 right 3): ")
#             parts = action_input.strip().split()

#             if not parts:
#                 continue

#             action_type = parts[0].lower()

#             if action_type == "turnleft" and len(parts) == 2:
#                 step = int(parts[1])
#                 action_symbol = turn_left(step)
#             elif action_type == "turnright" and len(parts) == 2:
#                 step = int(parts[1])
#                 action_symbol = turn_right(step)
#             elif action_type == "moveforward" and len(parts) == 2:
#                 step = int(parts[1])
#                 action_symbol = move_forward(step)
#             elif action_type == "grab" and len(parts) == 3:
#                 y, x = int(parts[1]), int(parts[2])
#                 step = int(input("Enter step: "))
#                 action_symbol = grab((y, x), step)
#             elif action_type == "shoot" and len(parts) == 5:
#                 y, x = int(parts[1]), int(parts[2])
#                 direction = parts[3]
#                 step = int(parts[4])
#                 action_symbol = shoot((y, x), direction, step)
#             else:
#                 print("Unknown or badly formatted action.")
#                 continue

#             # Update KB with action
#             explorer.kb.update_action_sentence(explorer, action_symbol, step)
#             percepts = world.exe_action(explorer, explorer.location, parts[0])  # this assumes exe_action supports the action string
#             explorer.kb.update_percept_sentence(explorer.location, percepts)
#             print(explorer.kb.clauses.formula())

#             print("Action executed. Updated board:")
#             world.print_board()


#         except Exception as e:
#             print("Error:", e)


# if __name__ == "__main__":
#     main()

# # def main():
# #     # Define symbols
# #     A = Symbol('A')
# #     B = Symbol('B')
# #     C = Symbol('C')
# #     D = Symbol('D')

# #     print("Testing CNF conversion:\n")

# #     # Test 1: Implication A => B
# #     print("1. Implication: A => B")
# #     sentence1 = Implication(A, B)
# #     cnf1 = to_cnf(sentence1)
# #     print(f"Original: {sentence1.formula()}")
# #     print(f"CNF: {cnf1.formula()}\n")

# #     # Test 2: Implication with And: (A ∧ B) => C
# #     print("2. Implication with And: (A ∧ B) => C")
# #     sentence2 = Implication(And(A, B), C)
# #     cnf2 = to_cnf(sentence2)
# #     print(f"Original: {sentence2.formula()}")
# #     print(f"CNF: {cnf2.formula()}\n")

# #     # Test 3: Or with And: A ∨ (B ∧ C)
# #     print("3. Or with And: A ∨ (B ∧ C)")
# #     sentence3 = Or(A, And(B, C))
# #     cnf3 = to_cnf(sentence3)
# #     print(f"Original: {sentence3.formula()}")
# #     print(f"CNF: {cnf3.formula()}\n")

# #     # Test 4: Not Or: ¬(A ∨ B)
# #     print("4. Not Or: ¬(A ∨ B)")
# #     sentence4 = Not(Or(A, B))
# #     cnf4 = to_cnf(sentence4)
# #     print(f"Original: {sentence4.formula()}")
# #     print(f"CNF: {cnf4.formula()}\n")

# #     # Test 5: Biconditional: A <=> B
# #     print("5. Biconditional: A <=> B")
# #     sentence5 = Biconditional(A, B)
# #     cnf5 = to_cnf(sentence5)
# #     print(f"Original: {sentence5.formula()}")
# #     print(f"CNF: {cnf5.formula()}\n")

# #     # Test 6: Complex case: (A ∨ B) ∧ (C ∨ D)
# #     print("6. Complex case: (A ∨ B) ∧ (C ∨ D)")
# #     sentence6 = And(Or(A, B), Or(C, D))
# #     cnf6 = to_cnf(sentence6)
# #     print(f"Original: {sentence6.formula()}")
# #     print(f"CNF: {cnf6.formula()}\n")

# #     # Test 7: Nested Or with And: (A ∨ (B ∧ C)) ∨ D
# #     print("7. Nested Or with And: (A ∨ (B ∧ C)) ∨ D")
# #     sentence7 = Or(Or(A, And(B, C)), D)
# #     cnf7 = to_cnf(sentence7)
# #     print(f"Original: {sentence7.formula()}")
# #     print(f"CNF: {cnf7.formula()}\n")
# #     print(cnf7)

# # if __name__ == "__main__":
# #     main()