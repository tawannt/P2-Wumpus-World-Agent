import sys
import time
from environment import WumpusEnvironment
from knowledgeBase import build_init_kb
from agent import Explorer
from object import Gold, Glitter


def get_bool_input(prompt):
    while True:
        val = input(prompt + ' (y/n): ').strip().lower()
        if val in ['y', 'yes']:
            return True
        elif val in ['n', 'no']:
            return False
        else:
            print('Please enter y or n.')

def get_int_input(prompt, min_val, max_val):
    while True:
        try:
            val = int(input(f'{prompt} [{min_val}-{max_val}]: '))
            if min_val <= val <= max_val:
                return val
            else:
                print(f'Please enter a value between {min_val} and {max_val}.')
        except ValueError:
            print('Please enter a valid integer.')

def get_float_input(prompt, min_val, max_val):
    while True:
        try:
            val = float(input(f'{prompt} [{min_val}-{max_val}]: '))
            if min_val <= val <= max_val:
                return val
            else:
                print(f'Please enter a value between {min_val} and {max_val}.')
        except ValueError:
            print('Please enter a valid number.')

def choose_agent():
    while True:
        val = input('Choose agent: (1) Random Agent, (2) A* Agent: ').strip()
        if val == '1':
            return 'random'
        elif val == '2':
            return 'astar'
        else:
            print('Please enter 1 or 2.')

def run_agent_solution(env, agent, kb, planner_class):
    print("="*60)
    print(f"COMPLETE {'ADVANCED ' if env.is_advanced else ''}A* WUMPUS WORLD SOLUTION")
    print("="*60)
    print(f"Environment: {env.height}x{env.width} grid, {env.k_wumpuses} wumpus, {len(env.pit_pos)} pits")
    print("Initial board:")
    env.print_board()
    planner = planner_class(env, kb)
    step = 0
    max_steps = 100
    while not env.is_end() and step < max_steps:
        print(f"\n--- STEP {step + 1} ---")
        print(f"Agent at {agent.location}, facing {agent.direction.direction}")
        print(f"Performance: {agent.performance}")
        percepts = env.percept(agent.location)
        planner.update_world_knowledge(agent.location, percepts)
        print(f"Percepts: {[type(p).__name__ for p in percepts]}")
        if any(isinstance(p, Glitter) for p in percepts):
            print("🏆 GOLD DETECTED! Grabbing...")
            env.exe_action(agent, agent.location, 'Grab')
            gold_status = any(isinstance(item, Gold) for item in agent.holding)
            print(f"Gold acquired: {gold_status}")
        action = planner.get_next_action(agent)
        if action:
            print(f"🎯 Planned action: {action}")
            action_percepts = env.exe_action(agent, agent.location, action)
            kb.update_action_sentence(agent, action, step)
            if not agent.alive:
                print(f"💀 AGENT KILLED BY: {agent.killed_by}")
                break
            if action_percepts:
                for percept in action_percepts:
                    print(f"Action result: {type(percept).__name__}")
        else:
            print("❌ No valid action available!")
            break
        print("Board state:")
        env.print_board()
        if agent not in env.agents:
            print("🚀 Agent successfully climbed out!")
            break
        step += 1
        time.sleep(0.3)
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"Steps taken: {step}")
    print(f"Final performance: {agent.performance}")
    print(f"Positions visited: {len(planner.visited_positions)}")
    print(f"Visited: {sorted(list(planner.visited_positions))}")
    if not agent.alive:
        print(f"❌ OUTCOME: FAILURE - Agent killed by {agent.killed_by}")
        success = False
    elif env.gold_taken:
        print("✅ OUTCOME: SUCCESS - Gold found and agent escaped!")
        success = True
    else:
        print("⚠️  OUTCOME: PARTIAL - Agent escaped but no gold found")
        success = False
    print(f"Performance score: {agent.performance}")
    return success, agent.performance, step

def main():
    print('--- Wumpus World Setup ---')
    adv = get_bool_input('Enable advanced setting (moving wumpus)?')
    N = get_int_input('Map size (N x N)', 4, 12)
    K = get_int_input('Number of wumpus', 1, max(1, N//2))
    pit_prob = get_float_input('Pit probability', 0.0, 0.5)

    env = WumpusEnvironment(N=N, K_wumpuses=K, pit_probability=pit_prob, advanced_setting=adv)
    print('\nGenerated board:')
    env.print_board()

    agent_type = choose_agent()
    kb = build_init_kb(N, env, env.is_advanced)
    if agent_type == 'random':
        from random_agent import RandomAgent
        agent = RandomAgent(kb, pos=(1, 1))
        env.agents.append(agent)
        env.board[1][1].append(agent)
        print("=== RANDOM AGENT RUN ===")
        step = 0
        while not env.is_end() and step < 1000:
            step += 1
            percepts = env.percept(agent.location)
            action = agent.choose_action(env, percepts)
            print(f"Step {step}: Agent at {agent.location}, facing {agent.direction.direction}")
            print(f"Percepts: {[type(p).__name__ for p in percepts]}")
            print(f"Action: {action}")
            result_percepts = env.exe_action(agent, agent.location, action)
            print(f"Performance: {agent.performance}")
            if not agent.alive:
                print(f"Agent died! Killed by: {agent.killed_by}")
                break
            if action == 'Climb' and agent.location == (1, 1):
                print("Agent climbed out!")
                break
            print("Board state:")
            env.print_board()
        print(f"Final performance: {agent.performance}")
        print(f"Agent alive: {agent.alive}")
        print(f"Found gold: {agent.found_gold}")
    else:
        agent = Explorer(kb, pos=(1, 1))
        env.agents.append(agent)
        env.board[1][1].append(agent)
        if adv:
            from astar_advanced import WumpusWorldAStarAdvanced
            run_agent_solution(env, agent, kb, WumpusWorldAStarAdvanced)
        else:
            from astar import WumpusWorldAStar
            run_agent_solution(env, agent, kb, WumpusWorldAStar)

if __name__ == '__main__':
    main()
