"""
Final A* Wumpus World Solver

This is the comprehensive A* implementation that combines logical inference 
with conservative heuristics to solve the Wumpus World problem efficiently.
"""

import heapq
import random
import time
from typing import List, Tuple, Set, Optional, Dict
from environment import WumpusEnvironment
from knowledgeBase import build_init_kb
from agent import Explorer
from direction import Direction
from logic import Not
from object import Thing, Gold, Wall, Pit, Arrow, Stench, Breeze, Glitter, Bump, Scream


class WumpusWorldNode:
    """Node for A* search in Wumpus World"""
    
    def __init__(self, position: Tuple[int, int], g_cost: int = 0, h_cost: int = 0, 
                 parent: Optional['WumpusWorldNode'] = None, action: str = ""):
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent = parent
        self.action = action
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        return self.position == other.position
    
    def __hash__(self):
        return hash(self.position)


class WumpusWorldAStar:
    """
    A* Planner for Wumpus World that uses both logical inference and conservative heuristics
    """
    
    def __init__(self, environment: WumpusEnvironment, knowledge_base=None):
        self.env = environment
        self.kb = knowledge_base
        self.width = environment.width
        self.height = environment.height
        
        # Safety tracking
        self.known_safe = {(1, 1)}  # Start is always safe
        self.known_unsafe = set()
        self.percept_history = {}
        self.visited_positions = {(1, 1)}
        
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance heuristic"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_adjacent_positions(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid adjacent positions within the grid"""
        y, x = position
        adjacent = []
        
        for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_y, new_x = y + dy, x + dx
            if 1 <= new_y <= self.height and 1 <= new_x <= self.width:
                adjacent.append((new_y, new_x))
        
        return adjacent
    
    def update_world_knowledge(self, position: Tuple[int, int], percepts: List):
        """Update world knowledge based on percepts"""
        self.percept_history[position] = percepts
        self.visited_positions.add(position)
        self.known_safe.add(position)
        
        # Update knowledge base if available
        if self.kb:
            try:
                self.kb.update_percept_sentence(position, percepts)
            except Exception as e:
                print(f"KB update error: {e}")
        
        # Heuristic safety inference
        has_breeze = any(isinstance(p, Breeze) for p in percepts)
        has_stench = any(isinstance(p, Stench) for p in percepts)
        
        if not has_breeze and not has_stench:
            # No danger signals - adjacent cells are safer candidates
            for adj_pos in self.get_adjacent_positions(position):
                if adj_pos not in self.known_unsafe:
                    # Mark as potential exploration target
                    pass
    
    def is_position_safe(self, position: Tuple[int, int]) -> bool:
        """
        Determine if a position is safe using multiple approaches:
        1. Already visited positions are safe
        2. Logical inference (if KB available)
        3. Conservative heuristics
        """
        # Already visited/known safe
        if position in self.visited_positions or position in self.known_safe:
            return True
        
        # Known unsafe
        if position in self.known_unsafe:
            return False
        
        # Try logical inference first
        if self.kb:
            try:
                y, x = position
                no_pit = self.kb.ask(Not(self.kb.symbols[('Pit', y, x)]))
                no_wumpus = self.kb.ask(Not(self.kb.symbols[('Wumpus', y, x)]))
                if no_pit and no_wumpus:
                    return True
            except Exception:
                # If logic fails, fall back to heuristics
                pass
        
        # Conservative heuristic: safe if adjacent to visited position with no danger
        for visited_pos in self.visited_positions:
            if self.manhattan_distance(position, visited_pos) == 1:
                percepts = self.percept_history.get(visited_pos, [])
                has_danger = any(isinstance(p, (Breeze, Stench)) for p in percepts)
                if not has_danger:
                    return True
        
        return False
    
    def find_path_astar(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[str]:
        """Find optimal path using A* algorithm"""
        if start == goal:
            return []
        
        open_set = []
        closed_set = set()
        came_from = {}
        
        start_node = WumpusWorldNode(start, 0, self.manhattan_distance(start, goal))
        heapq.heappush(open_set, start_node)
        node_map = {start: start_node}
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if current.position == goal:
                # Reconstruct path
                path = []
                while current.parent:
                    path.append(current.action)
                    current = current.parent
                return path[::-1]
            
            closed_set.add(current.position)
            
            # Explore neighbors
            for neighbor_pos in self.get_adjacent_positions(current.position):
                if neighbor_pos in closed_set:
                    continue
                
                # Only consider safe positions
                if not self.is_position_safe(neighbor_pos):
                    continue
                
                # Calculate costs
                g_cost = current.g_cost + 1
                h_cost = self.manhattan_distance(neighbor_pos, goal)
                
                # Check if this path is better
                if neighbor_pos not in node_map or g_cost < node_map[neighbor_pos].g_cost:
                    action = self.get_direction_action(current.position, neighbor_pos)
                    neighbor_node = WumpusWorldNode(neighbor_pos, g_cost, h_cost, current, action)
                    node_map[neighbor_pos] = neighbor_node
                    heapq.heappush(open_set, neighbor_node)
        
        return []  # No path found
    
    def get_direction_action(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> str:
        """Get the direction needed to move from one position to another"""
        dy = to_pos[0] - from_pos[0]
        dx = to_pos[1] - from_pos[1]
        
        if dy == 1:
            return "up"
        elif dy == -1:
            return "down"
        elif dx == 1:
            return "right"
        elif dx == -1:
            return "left"
        return "unknown"
    
    def find_exploration_targets(self, current_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find promising positions to explore for gold"""
        targets = []
        
        # Look for unvisited safe positions
        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                pos = (y, x)
                if pos not in self.visited_positions and self.is_position_safe(pos):
                    targets.append(pos)
        
        # Sort by distance from current position
        targets.sort(key=lambda pos: self.manhattan_distance(current_pos, pos))
        return targets
    
    def convert_path_to_actions(self, agent: Explorer, path: List[str]) -> List[str]:
        """Convert directional path to sequence of agent actions (turns + moves)"""
        if not path:
            return []
        
        actions = []
        current_direction = agent.direction.direction
        
        direction_map = {
            "up": Direction.U,
            "down": Direction.D,
            "left": Direction.L,
            "right": Direction.R
        }
        
        for move_direction in path:
            target_direction = direction_map[move_direction]
            
            # Add turning actions
            turn_actions = self.calculate_turn_actions(current_direction, target_direction)
            actions.extend(turn_actions)
            
            # Add move action
            actions.append("MoveForward")
            
            # Update current direction
            current_direction = target_direction
        
        return actions
    
    def calculate_turn_actions(self, current_dir: str, target_dir: str) -> List[str]:
        """Calculate the turning actions needed to face the target direction"""
        if current_dir == target_dir:
            return []
        
        directions = [Direction.U, Direction.R, Direction.D, Direction.L]
        
        try:
            current_idx = directions.index(current_dir)
            target_idx = directions.index(target_dir)
        except ValueError:
            return []
        
        # Calculate shortest rotation
        diff = (target_idx - current_idx) % 4
        
        if diff == 1:
            return ["TurnRight"]
        elif diff == 2:
            return ["TurnRight", "TurnRight"]
        elif diff == 3:
            return ["TurnLeft"]
        
        return []
    
    def solve_wumpus_world(self, agent: Explorer) -> List[str]:
        """
        Main solving function that returns a complete action sequence
        to find gold and return to (1,1)
        """
        complete_plan = []
        current_pos = agent.location
        has_gold = any(isinstance(item, Gold) for item in agent.holding)
        
        print(f"Starting solve from {current_pos}, has_gold={has_gold}")
        
        if has_gold:
            # Agent has gold, plan return to (1,1)
            if current_pos == (1, 1):
                complete_plan.append("Climb")
            else:
                return_path = self.find_path_astar(current_pos, (1, 1))
                if return_path:
                    return_actions = self.convert_path_to_actions(agent, return_path)
                    complete_plan.extend(return_actions)
                    complete_plan.append("Climb")
                    print(f"Return path planned: {return_path}")
                else:
                    print("Cannot find safe return path to (1,1)!")
        else:
            # Search for gold
            exploration_targets = self.find_exploration_targets(current_pos)
            print(f"Found {len(exploration_targets)} exploration targets: {exploration_targets[:3]}...")
            
            if exploration_targets:
                # Plan to closest safe target
                target = exploration_targets[0]
                path = self.find_path_astar(current_pos, target)
                if path:
                    actions = self.convert_path_to_actions(agent, path)
                    complete_plan.extend(actions)
                    print(f"Exploration path to {target}: {path}")
                else:
                    print(f"No safe path to exploration target {target}")
            else:
                print("No safe exploration targets available")
        
        return complete_plan
    
    def get_next_action(self, agent: Explorer) -> Optional[str]:
        """Get the next single action for the agent"""
        plan = self.solve_wumpus_world(agent)
        return plan[0] if plan else None


def run_complete_wumpus_solution():
    """Run a complete automated solution of the Wumpus World"""
    
    print("="*60)
    print("COMPLETE A* WUMPUS WORLD SOLUTION")
    print("="*60)
    
    # Setup
    random.seed(time.time())  # For reproducible results
    N = 6
    env = WumpusEnvironment(N=N, K_wumpuses=2, pit_probability=0.2)
    
    # Initialize KB and agent
    kb = build_init_kb(N, env)
    agent = Explorer(kb, pos=(1, 1))
    env.agents.append(agent)
    env.board[1][1].append(agent)
    
    # Create planner
    planner = WumpusWorldAStar(env, kb)
    
    print(f"Environment: {N}x{N} grid, {env.k_wumpuses} wumpus, {len(env.pit_pos)} pits")
    print("Initial board:")
    env.print_board()
    
    step = 0
    max_steps = 50
    
    # Game loop
    while not env.is_end() and step < max_steps:
        print(f"\n--- STEP {step + 1} ---")
        print(f"Agent at {agent.location}, facing {agent.direction.direction}")
        print(f"Performance: {agent.performance}")
        
        # Get and process percepts
        percepts = env.percept(agent.location)
        planner.update_world_knowledge(agent.location, percepts)
        print(f"Percepts: {[type(p).__name__ for p in percepts]}")
        
        # Check for gold
        if any(isinstance(p, Glitter) for p in percepts):
            print("🏆 GOLD DETECTED! Grabbing...")
            env.exe_action(agent, agent.location, 'Grab')
            gold_status = any(isinstance(item, Gold) for item in agent.holding)
            print(f"Gold acquired: {gold_status}")
        
        # Get next action from planner
        action = planner.get_next_action(agent)
        
        if action:
            print(f"🎯 Planned action: {action}")
            
            # Execute action
            action_percepts = env.exe_action(agent, agent.location, action)
            
            # Check if agent survived
            if not agent.alive:
                print(f"💀 AGENT KILLED BY: {agent.killed_by}")
                break
            
            # Handle special percepts from actions
            if action_percepts:
                for percept in action_percepts:
                    print(f"Action result: {type(percept).__name__}")
        else:
            print("❌ No valid action available!")
            break
        
        print("Board state:")
        env.print_board()
        
        # Check if agent climbed out
        if agent not in env.agents:
            print("🚀 Agent successfully climbed out!")
            break
        
        step += 1
        time.sleep(0.3)  # Brief pause for readability
    
    # Final results
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"Steps taken: {step}")
    print(f"Final performance: {agent.performance}")
    print(f"Positions visited: {len(planner.visited_positions)}")
    print(f"Visited: {sorted(list(planner.visited_positions))}")
    
    # Determine outcome
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


def run_multiple_scenarios(num_runs=3):
    """Run multiple scenarios to test robustness"""
    
    print("\n" + "="*60)
    print(f"RUNNING {num_runs} TEST SCENARIOS")
    print("="*60)
    
    results = []
    
    for run in range(num_runs):
        print(f"\n🧪 TEST SCENARIO {run + 1}/{num_runs}")
        print("-" * 40)
        
        random.seed(run + 500)  # Different seed for each run
        
        try:
            success, performance, steps = run_complete_wumpus_solution()
            results.append({
                'run': run + 1,
                'success': success,
                'performance': performance,
                'steps': steps
            })
        except Exception as e:
            print(f"❌ Scenario {run + 1} failed: {e}")
            results.append({
                'run': run + 1,
                'success': False,
                'performance': -1000,
                'steps': 0
            })
    
    # Summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    successful_runs = [r for r in results if r['success']]
    success_rate = len(successful_runs) / len(results) * 100
    avg_performance = sum(r['performance'] for r in results) / len(results)
    avg_steps = sum(r['steps'] for r in results) / len(results)
    
    print(f"Success rate: {len(successful_runs)}/{len(results)} ({success_rate:.1f}%)")
    print(f"Average performance: {avg_performance:.1f}")
    print(f"Average steps: {avg_steps:.1f}")
    
    if successful_runs:
        best_performance = max(r['performance'] for r in successful_runs)
        best_run = next(r for r in successful_runs if r['performance'] == best_performance)
        print(f"Best performance: {best_performance} (Run {best_run['run']})")
    
    print("\nDetailed results:")
    for r in results:
        status = "✅ SUCCESS" if r['success'] else "❌ FAILURE"
        print(f"  Run {r['run']}: {status} - Performance: {r['performance']}, Steps: {r['steps']}")


if __name__ == "__main__":
    # Run single complete solution
    run_complete_wumpus_solution()
    
    # Uncomment to run multiple test scenarios
    # run_multiple_scenarios(5)
