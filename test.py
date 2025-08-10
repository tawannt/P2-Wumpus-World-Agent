import random
import time
from collections import defaultdict
from environment import WumpusEnvironment
from knowledgeBase import build_init_kb
from agent import Explorer
from object import Thing, Gold, Wall, Pit, Arrow, Stench, Breeze, Glitter, Bump, Scream
from logic import Sentence, Symbol, Not, And, Or, Implication, Biconditional


def main():
    random.seed(time.time())  # For reproducibility
    # Initialize environment: 4x4 grid, 1 Wumpus, 20% pit probability
    N = 4
    env = WumpusEnvironment(N=N, K_wumpuses=0, pit_probability=0.2)
    
    # Initialize knowledge base with single_wumpus=False for multi-Wumpus compatibility
    kb = build_init_kb(N, env)
    
    # Initialize explorer at (1,1) with the KB
    agent = Explorer(kb, pos=(1, 1))
    env.agents.append(agent)
    env.board[1][1].append(agent)
    
    step = 0
    max_steps = 100  # Prevent infinite loops
    
    print("Initial Board:")
    env.print_board()
    print("\nAvailable actions: MoveForward, TurnLeft, TurnRight, Grab, Shoot, Climb")
    action = None
    percepts = []
    while not env.is_end() and step < max_steps:
        print(f"\nStep {step}: Agent at {agent.location}, Direction: {agent.direction.direction}")
        
        if action == 'MoveForward' or action == 'Shoot' or action == None:
            # Check if current position is safe
            y, x = agent.location
            is_current_safe = kb.ask(Not(kb.symbols[('Pit', y, x)])) and kb.ask(Not(kb.symbols[('Wumpus', y, x)]))
            if not is_current_safe and (y, x) not in agent.visited:
                print(f"Warning: Current position {agent.location} may be unsafe!")
                env.in_danger(agent)  # Check if agent is killed
                if not agent.alive:
                    break
        
        # Get percepts at current position
        if action == 'MoveForward' or action == 'Shoot' or action == None:
            percepts = env.percept(agent.location)
            print(f"Percepts: {[type(p).__name__ for p in percepts]}")
        
            # Update KB with percepts
            kb.update_percept_sentence(agent.location, percepts)
            
            # Check for glitter (gold) and suggest grabbing
            if any(isinstance(p, Glitter) for p in percepts):
                print("Gold detected! You can use 'Grab' to pick it up.")
        
            # Check adjacent cells for safety
            adjacent = [
                (y + 1, x) if y < N else None,  # Up
                (y - 1, x) if y > 1 else None,  # Down
                (y, x + 1) if x < N else None,  # Right
                (y, x - 1) if x > 1 else None   # Left
            ]
            safe_adjacent = []
            for pos in adjacent:
                if pos and env.is_in_map(pos):
                    if (kb.ask(Not(kb.symbols[('Pit', pos[0], pos[1])]))) and \
                    kb.ask(Not(kb.symbols[('Wumpus', pos[0], pos[1])])) or \
                    pos in agent.visited:
                        safe_adjacent.append(pos)
            print(f"Safe adjacent cells: {safe_adjacent}")
        
        # Prompt for user action
        valid_actions = ['MoveForward', 'TurnLeft', 'TurnRight', 'Grab', 'Shoot', 'Climb']
        if not agent.has_arrow:
            valid_actions.remove('Shoot')
        if not any(isinstance(p, Glitter) for p in percepts):
            valid_actions.remove('Grab')
        if agent.location != (1, 1):
            valid_actions.remove('Climb')
        
        print(f"Valid actions: {', '.join(valid_actions)}")
        while True:
            action = input("Enter action: ").strip()
            if action in valid_actions:
                break
            print(f"Invalid action! Choose from: {', '.join(valid_actions)}")
        
        # Execute action
        print(f"Action: {action}")
        percepts = env.exe_action(agent, agent.location, action)
        kb.update_action_sentence(agent, f"{action}_{agent.location[0]}_{agent.location[1]}_{step}", step)
        if action == 'MoveForward' or action == 'Shoot':
            for percept in percepts:  # Safe since exe_action returns a list
                kb.update_percept_sentence(agent.location, [percept])
        
        print("Board after action:")
        env.print_board()
        
        # Check if action caused death
        if not agent.alive:
            break
        
        step += 1
    
    print(f"\nGame ended after {step} steps.")
    print(f"Agent performance: {agent.performance}")
    if not agent.alive:
        print(f"Agent died: {agent.killed_by}")
    elif env.gold_taken:
        print("Agent won with gold!")
    else:
        print("Agent climbed out without gold.")

if __name__ == "__main__":
    
    main()