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
        
        # Analyze danger signals
        has_breeze = any(isinstance(p, Breeze) for p in percepts)
        has_stench = any(isinstance(p, Stench) for p in percepts)
        
        if has_breeze or has_stench:
            # Mark adjacent unvisited positions as potentially unsafe
            for adj_pos in self.get_adjacent_positions(position):
                if adj_pos not in self.visited_positions:
                    # Don't mark as known_unsafe yet, but be cautious
                    pass
        else:
            # No danger signals - adjacent cells are much safer candidates
            for adj_pos in self.get_adjacent_positions(position):
                if adj_pos not in self.visited_positions and adj_pos not in self.known_unsafe:
                    # This is a good candidate for safe exploration
                    pass
    
    def is_position_safe(self, position: Tuple[int, int]) -> bool:
        """
        Determine if a position is safe using multiple approaches:
        1. Already visited positions are safe
        2. Logical inference (if KB available)
        3. Conservative heuristics - only safe if adjacent to visited area with NO danger signals
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
                # Create symbols for this position
                pit_symbol = f"Pit_{y}_{x}"
                wumpus_symbol = f"Wumpus_{y}_{x}"
                
                # Try to ask if position is safe (no pit and no wumpus)
                if pit_symbol in self.kb.symbols and wumpus_symbol in self.kb.symbols:
                    no_pit = self.kb.ask(Not(self.kb.symbols[pit_symbol]))
                    no_wumpus = self.kb.ask(Not(self.kb.symbols[wumpus_symbol]))
                    if no_pit and no_wumpus:
                        self.known_safe.add(position)
                        return True
                    elif no_pit is False or no_wumpus is False:
                        # Definitely unsafe
                        self.known_unsafe.add(position)
                        return False
            except Exception as e:
                print(f"KB inference error for {position}: {e}")
        
        # Conservative heuristic: ONLY safe if adjacent to visited position with NO danger
        for visited_pos in self.visited_positions:
            if self.manhattan_distance(position, visited_pos) == 1:
                percepts = self.percept_history.get(visited_pos, [])
                has_danger = any(isinstance(p, (Breeze, Stench)) for p in percepts)
                if not has_danger:
                    # Adjacent to safe area with no danger signals
                    self.known_safe.add(position)
                    return True
        
        # Default to unsafe if we can't prove it's safe
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
    
    def find_safe_unvisited_targets(self, current_pos: Tuple[int, int], agent: Explorer) -> List[Tuple[int, int]]:
        """Find unvisited positions that are confirmed safe, prioritize those that don't require a turn."""
        targets = []
        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                pos = (y, x)
                if pos not in self.visited_positions and self.is_position_safe(pos):
                    targets.append(pos)

        def needs_turn(from_pos, to_pos, current_direction):
            move_dir = self.get_direction_action(from_pos, to_pos)
            # Map move_dir to canonical direction string
            dir_map = {"up": Direction.U, "down": Direction.D, "left": Direction.L, "right": Direction.R}
            if move_dir not in dir_map:
                return 1  # Unknown, treat as needs turn
            return 0 if dir_map[move_dir] == current_direction else 1

        # Sort by (distance, needs_turn)
        current_direction = agent.direction.direction if hasattr(agent.direction, 'direction') else agent.direction
        targets.sort(key=lambda pos: (self.manhattan_distance(current_pos, pos), needs_turn(current_pos, pos, current_direction)))
        return targets
    
    def find_risky_exploration_targets(self, current_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find unvisited positions that are not confirmed unsafe (for risky exploration)"""
        targets = []
        
        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                pos = (y, x)
                if (pos not in self.visited_positions and 
                    pos not in self.known_unsafe and
                    not self.is_position_safe(pos)):  # Not confirmed safe, but not confirmed unsafe
                    targets.append(pos)
        
        # Sort by distance from current position
        targets.sort(key=lambda pos: self.manhattan_distance(current_pos, pos))
        return targets
    
    def plan_wumpus_shot(self, agent: Explorer) -> List[str]:
        """
        Plan a wumpus shot following HybridWumpusAgent pattern:
        1. Find possible wumpus locations (positions with stench but not confirmed safe)
        2. Find shooting positions that can target these locations
        3. Move to a shooting position and shoot
        """
        current_pos = agent.location
        possible_wumpus_locations = self.find_possible_wumpus_locations()
        
        if not possible_wumpus_locations:
            return []
        
        print(f"Possible wumpus locations: {possible_wumpus_locations}")
        
        # Find all valid shooting positions for these wumpus locations
        shooting_positions = self.find_shooting_positions(possible_wumpus_locations)
        
        if not shooting_positions:
            return []
        
        # Find the closest shooting position we can safely reach
        for shoot_pos, shoot_dir, target_pos in shooting_positions:
            if self.is_position_safe(shoot_pos):
                # Plan route to shooting position
                path_to_shoot = self.find_path_astar(current_pos, shoot_pos)
                if path_to_shoot:
                    actions = self.convert_path_to_actions(agent, path_to_shoot)
                    
                    # Add turning and shooting actions
                    # Calculate final direction after movement
                    final_direction = agent.direction.direction
                    if path_to_shoot:
                        direction_map = {"up": Direction.U, "down": Direction.D, 
                                       "left": Direction.L, "right": Direction.R}
                        final_direction = direction_map[path_to_shoot[-1]]
                    
                    # Turn to face shooting direction
                    turn_actions = self.calculate_turn_actions(final_direction, shoot_dir)
                    actions.extend(turn_actions)
                    actions.append("Shoot")
                    
                    print(f"Shot plan: move to {shoot_pos}, face {shoot_dir}, shoot at {target_pos}")
                    return actions
        
        return []
    
    def find_possible_wumpus_locations(self) -> List[Tuple[int, int]]:
        """Find locations where wumpus might be based on stench percepts"""
        possible_locations = []
        stench_positions = self.find_stench_positions()
        
        if not stench_positions:
            return []
        
        # Check adjacent positions to stench locations
        for stench_pos in stench_positions:
            for adj_pos in self.get_adjacent_positions(stench_pos):
                if (adj_pos not in self.visited_positions and 
                    adj_pos not in possible_locations):
                    # This could be a wumpus location
                    possible_locations.append(adj_pos)
        
        return possible_locations
    
    def find_shooting_positions(self, wumpus_locations: List[Tuple[int, int]]) -> List[Tuple[Tuple[int, int], str, Tuple[int, int]]]:
        """
        Find positions from which we can shoot at potential wumpus locations.
        Returns list of (shooting_position, shooting_direction, target_position)
        """
        shooting_positions = []
        
        for target_pos in wumpus_locations:
            target_y, target_x = target_pos
            
            # Check all positions in same row (for horizontal shots)
            for x in range(1, self.width + 1):
                if x != target_x:
                    shoot_pos = (target_y, x)
                    if x < target_x:
                        shoot_dir = Direction.R  # Shoot right towards target
                    else:
                        shoot_dir = Direction.L  # Shoot left towards target
                    
                    # Make sure shooting position is not a potential wumpus location
                    if shoot_pos not in wumpus_locations:
                        shooting_positions.append((shoot_pos, shoot_dir, target_pos))
            
            # Check all positions in same column (for vertical shots)
            for y in range(1, self.height + 1):
                if y != target_y:
                    shoot_pos = (y, target_x)
                    if y < target_y:
                        shoot_dir = Direction.U  # Shoot up towards target
                    else:
                        shoot_dir = Direction.D  # Shoot down towards target
                    
                    # Make sure shooting position is not a potential wumpus location
                    if shoot_pos not in wumpus_locations:
                        shooting_positions.append((shoot_pos, shoot_dir, target_pos))
        
        # Sort by distance to current position (prefer closer shooting positions)
        current_pos = list(self.visited_positions)[0] if self.visited_positions else (1, 1)
        shooting_positions.sort(key=lambda x: self.manhattan_distance(current_pos, x[0]))
        
        return shooting_positions
    
    def find_risky_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[str]:
        """Find path allowing movement to unvisited (potentially unsafe) positions"""
        if start == goal:
            return []
        
        # Simple direct path if adjacent
        if self.manhattan_distance(start, goal) == 1:
            direction = self.get_direction_action(start, goal)
            return [direction]
        
        # For longer paths, use A* but allow unvisited positions
        open_set = []
        closed_set = set()
        
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
            
            # Explore neighbors (including potentially unsafe ones)
            for neighbor_pos in self.get_adjacent_positions(current.position):
                if neighbor_pos in closed_set:
                    continue
                
                # Allow movement to unvisited positions (risky but necessary)
                # Still avoid known unsafe positions if possible
                if neighbor_pos in self.known_unsafe:
                    continue
                
                # Calculate costs with penalty for unvisited positions
                g_cost = current.g_cost + 1
                if neighbor_pos not in self.visited_positions:
                    g_cost += 2  # Penalty for risky moves
                
                h_cost = self.manhattan_distance(neighbor_pos, goal)
                
                # Check if this path is better
                if neighbor_pos not in node_map or g_cost < node_map[neighbor_pos].g_cost:
                    action = self.get_direction_action(current.position, neighbor_pos)
                    neighbor_node = WumpusWorldNode(neighbor_pos, g_cost, h_cost, current, action)
                    node_map[neighbor_pos] = neighbor_node
                    heapq.heappush(open_set, neighbor_node)
        
        return []
    
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
    
    def find_unvisited_adjacent_positions(self, current_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find unvisited positions adjacent to visited positions"""
        unvisited_adjacent = []
        
        # Check all positions adjacent to visited areas
        for visited_pos in self.visited_positions:
            for adj_pos in self.get_adjacent_positions(visited_pos):
                if adj_pos not in self.visited_positions and adj_pos not in unvisited_adjacent:
                    unvisited_adjacent.append(adj_pos)
        
        return unvisited_adjacent
    
    def find_stench_positions(self) -> List[Tuple[int, int]]:
        """Find visited positions that have stench percepts"""
        stench_positions = []
        
        for pos, percepts in self.percept_history.items():
            if any(isinstance(p, Stench) for p in percepts):
                stench_positions.append(pos)
        
        return stench_positions
    
    def get_direction_to_position(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> str:
        """Get the direction name to move from one position to another"""
        dy = to_pos[0] - from_pos[0]
        dx = to_pos[1] - from_pos[1]
        
        if dy == 1:
            return Direction.U
        elif dy == -1:
            return Direction.D
        elif dx == 1:
            return Direction.R
        elif dx == -1:
            return Direction.L
        return None
    
    def plan_risky_action(self, agent: Explorer) -> List[str]:
        """
        Plan a risky action when no safe zones are available:
        1. If there's stench in visited zone and agent has arrow, shoot towards unvisited adjacent zone
        2. Otherwise, move to a random unvisited zone adjacent to visited zones
        """
        import random
        
        current_pos = agent.location
        complete_plan = []
        
        # Find unvisited adjacent positions
        unvisited_adjacent = self.find_unvisited_adjacent_positions(current_pos)
        
        if not unvisited_adjacent:
            print("No unvisited adjacent positions available!")
            return []
        
        # Check if agent has arrow and there are stench positions
        if agent.has_arrow:
            stench_positions = self.find_stench_positions()
            
            if stench_positions:
                print(f"Found stench at positions: {stench_positions}")
                
                # Find unvisited positions adjacent to stench positions
                stench_adjacent_unvisited = []
                for stench_pos in stench_positions:
                    for adj_pos in self.get_adjacent_positions(stench_pos):
                        if adj_pos not in self.visited_positions and adj_pos not in stench_adjacent_unvisited:
                            stench_adjacent_unvisited.append(adj_pos)
                
                if stench_adjacent_unvisited:
                    # Choose a random target to shoot at
                    shoot_target = random.choice(stench_adjacent_unvisited)
                    print(f"Planning to shoot towards {shoot_target} (potential wumpus location)")
                    
                    # Calculate direction to shoot from current position
                    # Find the best position to shoot from (should be adjacent to current pos and in line with target)
                    best_shoot_plan = self.plan_shoot_sequence(current_pos, shoot_target, agent)
                    
                    if best_shoot_plan:
                        complete_plan.extend(best_shoot_plan)
                        print(f"Risky shoot plan: {best_shoot_plan}")
                        return complete_plan
        
        # Fallback: Move to a random unvisited adjacent position
        if unvisited_adjacent:
            target = random.choice(unvisited_adjacent)
            print(f"No arrow strategy available, taking calculated risk to move to {target}")
            
            # Try to find a path (even if risky)
            path = self.find_risky_path(current_pos, target)
            if path:
                actions = self.convert_path_to_actions(agent, path)
                complete_plan.extend(actions)
                print(f"Risky path to {target}: {path}")
        
        return complete_plan
    
    def find_risky_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[str]:
        """Find path allowing movement to unvisited (potentially unsafe) positions"""
        if start == goal:
            return []
        
        # Simple direct path if adjacent
        if self.manhattan_distance(start, goal) == 1:
            direction = self.get_direction_action(start, goal)
            return [direction]
        
        # For longer paths, use A* but allow unvisited positions
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
            
            # Explore neighbors (including potentially unsafe ones)
            for neighbor_pos in self.get_adjacent_positions(current.position):
                if neighbor_pos in closed_set:
                    continue
                
                # Allow movement to unvisited positions (risky but necessary)
                # Still avoid known unsafe positions if possible
                if neighbor_pos in self.known_unsafe:
                    continue
                
                # Calculate costs with penalty for unvisited positions
                g_cost = current.g_cost + 1
                if neighbor_pos not in self.visited_positions:
                    g_cost += 2  # Penalty for risky moves
                
                h_cost = self.manhattan_distance(neighbor_pos, goal)
                
                # Check if this path is better
                if neighbor_pos not in node_map or g_cost < node_map[neighbor_pos].g_cost:
                    action = self.get_direction_action(current.position, neighbor_pos)
                    neighbor_node = WumpusWorldNode(neighbor_pos, g_cost, h_cost, current, action)
                    node_map[neighbor_pos] = neighbor_node
                    heapq.heappush(open_set, neighbor_node)
        
        return []
    
    def plan_shoot_sequence(self, current_pos: Tuple[int, int], target_pos: Tuple[int, int], agent: Explorer) -> List[str]:
        """Plan a sequence to shoot towards a target and then move"""
        sequence = []
        
        # Check if we can shoot in a straight line towards the target
        # Find a position from which we can shoot towards the target
        
        # Try shooting from current position first
        if self.can_shoot_towards_target(current_pos, target_pos):
            shoot_direction = self.get_shooting_direction(current_pos, target_pos)
            if shoot_direction:
                # Turn to face the target direction
                turn_actions = self.calculate_turn_actions(agent.direction.direction, shoot_direction)
                sequence.extend(turn_actions)
                sequence.append("Shoot")
                sequence.append("MoveForward")  # Move into potentially cleared area
                return sequence
        
        # If we can't shoot directly, try to move to an adjacent position and then shoot
        for adj_pos in self.get_adjacent_positions(current_pos):
            if adj_pos in self.visited_positions and self.can_shoot_towards_target(adj_pos, target_pos):
                # Move to the adjacent position first
                move_direction = self.get_direction_action(current_pos, adj_pos)
                path_to_shoot_pos = [move_direction]
                move_actions = self.convert_path_to_actions(agent, path_to_shoot_pos)
                sequence.extend(move_actions)
                
                # Then shoot towards target
                shoot_direction = self.get_shooting_direction(adj_pos, target_pos)
                if shoot_direction:
                    # Calculate what direction we'll be facing after the move
                    direction_after_move = self.get_direction_to_position(current_pos, adj_pos)
                    turn_actions = self.calculate_turn_actions(direction_after_move, shoot_direction)
                    sequence.extend(turn_actions)
                    sequence.append("Shoot")
                    sequence.append("MoveForward")
                    return sequence
        
        return []
    
    def can_shoot_towards_target(self, shoot_from: Tuple[int, int], target: Tuple[int, int]) -> bool:
        """Check if we can shoot towards target from the given position"""
        dy = target[0] - shoot_from[0]
        dx = target[1] - shoot_from[1]
        
        # Can only shoot in straight lines (horizontal or vertical)
        if dy == 0 and dx != 0:  # Horizontal line
            return True
        elif dx == 0 and dy != 0:  # Vertical line
            return True
        
        return False
    
    def get_shooting_direction(self, shoot_from: Tuple[int, int], target: Tuple[int, int]) -> str:
        """Get the direction to shoot towards target"""
        dy = target[0] - shoot_from[0]
        dx = target[1] - shoot_from[1]
        
        if dy > 0:
            return Direction.U
        elif dy < 0:
            return Direction.D
        elif dx > 0:
            return Direction.R
        elif dx < 0:
            return Direction.L
        
        return None
    
    def solve_wumpus_world(self, agent: Explorer) -> List[str]:
        """
        Main solving function following HybridWumpusAgent behavior pattern:
        1. If glitter detected, grab gold and return home
        2. Explore unvisited safe areas
        3. If have arrow, plan shot at possible wumpus locations
        4. Try risky moves to unvisited areas
        5. Return home and climb out
        """
        complete_plan = []
        current_pos = agent.location
        has_gold = any(isinstance(item, Gold) for item in agent.holding)
        
        print(f"Starting solve from {current_pos}, has_gold={has_gold}")
        
        # Priority 1: If agent has gold, return to (1,1) and climb
        if has_gold:
            if current_pos == (1, 1):
                complete_plan.append("Climb")
                print("At home with gold - climbing out!")
            else:
                return_path = self.find_path_astar(current_pos, (1, 1))
                if return_path:
                    return_actions = self.convert_path_to_actions(agent, return_path)
                    complete_plan.extend(return_actions)
                    complete_plan.append("Climb")
                    print(f"Returning home with gold: {return_path}")
                else:
                    print("Cannot find safe return path to (1,1)!")
            return complete_plan
        
        # Priority 2: Explore unvisited safe areas
        safe_unvisited_targets = self.find_safe_unvisited_targets(current_pos, agent)
        if safe_unvisited_targets:
            target = safe_unvisited_targets[0]  # Closest safe unvisited, tie-broken by no-turn
            path = self.find_path_astar(current_pos, target)
            if path:
                actions = self.convert_path_to_actions(agent, path)
                complete_plan.extend(actions)
                print(f"Exploring safe unvisited area: {target}")
                return complete_plan
        
        # # Priority 3: If have arrow, plan shot at possible wumpus locations
        # if agent.has_arrow:
        #     shot_plan = self.plan_wumpus_shot(agent)
        #     if shot_plan:
        #         complete_plan.extend(shot_plan)
        #         print("Planning wumpus shot sequence")
        #         return complete_plan
        
        # Priority 4: Try risky moves to unvisited areas (not confirmed unsafe)
        risky_targets = self.find_risky_exploration_targets(current_pos)
        if risky_targets:
            target = risky_targets[0]
            path = self.find_risky_path(current_pos, target)
            if path:
                actions = self.convert_path_to_actions(agent, path)
                complete_plan.extend(actions)
                print(f"Taking calculated risk to explore: {target}")
                return complete_plan
        
        # Priority 5: Last resort - return home and climb out
        print("No more exploration options - returning home")
        if current_pos != (1, 1):
            return_path = self.find_path_astar(current_pos, (1, 1))
            if return_path:
                return_actions = self.convert_path_to_actions(agent, return_path)
                complete_plan.extend(return_actions)
        complete_plan.append("Climb")
        
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
    max_steps = 100
    
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
