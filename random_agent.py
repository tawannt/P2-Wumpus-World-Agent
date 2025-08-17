import random
from agent import Explorer
from direction import Direction
from object import Gold, Breeze, Stench, Glitter, Scream, Bump


class RandomAgent(Explorer):
    """
    A random agent baseline that takes random valid actions in the Wumpus World.
    This agent serves as a baseline for comparison with more intelligent agents.
    """
    
    def __init__(self, kb, visited=None, pos=(1, 1)):
        super().__init__(kb, visited, pos)
        self.action_count = 0
        self.max_actions = 1000  # Prevent infinite loops
        self.found_gold = False
        self.at_start = True
        
    def get_valid_actions(self, environment):
        """
        Get list of valid actions the agent can take.
        Returns a list of action strings.
        """
        actions = ['TurnLeft', 'TurnRight']
        
        # Check if we can move forward (not into a wall)
        next_location = self.direction.move_forward(self.location)
        if environment.is_in_map(next_location):
            actions.append('MoveForward')
        
        # Check if there's gold to grab
        for thing in environment.board[self.location[0]][self.location[1]]:
            if isinstance(thing, Gold):
                actions.append('Grab')
                break
        
        # Check if we can climb (only at starting position)
        if self.location == (1, 1):
            actions.append('Climb')
            
        # Check if we can shoot (if we still have arrow)
        if self.has_arrow:
            actions.append('Shoot')
            
        return actions
    
    def choose_action(self, environment, percepts=None):
        """
        Choose a random action from valid actions.
        Implements some basic preferences:
        1. Always grab gold if available
        2. Climb out if we have gold and are at start
        3. Otherwise choose randomly
        """
        self.action_count += 1
        
        # Safety check - prevent infinite loops
        if self.action_count > self.max_actions:
            if self.location == (1, 1):
                return 'Climb'
            else:
                # Try to get back to start
                actions = ['TurnLeft', 'TurnRight', 'MoveForward']
                return random.choice(actions)
        
        valid_actions = self.get_valid_actions(environment)
        
        # Priority 1: Grab gold if available
        if 'Grab' in valid_actions:
            self.found_gold = True
            return 'Grab'
        
        # Priority 2: Climb out if we have gold and are at start
        if self.found_gold and self.location == (1, 1) and 'Climb' in valid_actions:
            return 'Climb'
        
        # Priority 3: Random exploration with slight preference for movement
        # Give higher probability to movement to encourage exploration
        if 'MoveForward' in valid_actions:
            # 60% chance to move forward, 40% chance for other actions
            if random.random() < 0.6:
                return 'MoveForward'
        
        # Remove 'Climb' from random selection unless we have gold
        if not self.found_gold and 'Climb' in valid_actions:
            valid_actions.remove('Climb')
        
        # Choose randomly from remaining actions
        if valid_actions:
            return random.choice(valid_actions)
        else:
            # Fallback - just turn
            return 'TurnLeft'
    
    def run_episode(self, environment, max_steps=1000, verbose=False):
        """
        Run a complete episode with the random agent.
        Returns the final performance score.
        """
        step = 0
        
        if verbose:
            print("Starting Random Agent Episode")
            print("Initial state:")
            environment.print_board()
            print()
        
        while not environment.is_end() and step < max_steps:
            step += 1
            
            # Get current percepts
            percepts = environment.percept(self.location)
            
            if verbose:
                print(f"Step {step}: Agent at {self.location}, facing {self.direction.direction}")
                print(f"Percepts: {[type(p).__name__ for p in percepts]}")
            
            # Choose action
            action = self.choose_action(environment, percepts)
            
            if verbose:
                print(f"Action: {action}")
            
            # Execute action
            result_percepts = environment.exe_action(self, self.location, action)
            
            if verbose:
                print(f"Performance: {self.performance}")
                if not self.alive:
                    print(f"Agent died! Killed by: {self.killed_by}")
                print()
            
            # Check if agent died
            if not self.alive:
                break
                
            # Check if agent climbed out
            if action == 'Climb' and self.location == (1, 1):
                break
        
        if verbose:
            print(f"Episode ended after {step} steps")
            print(f"Final performance: {self.performance}")
            print(f"Agent alive: {self.alive}")
            print(f"Found gold: {self.found_gold}")
        
        return self.performance


def run_random_agent_experiment(num_episodes=100, world_size=8, num_wumpuses=2, pit_prob=0.2, verbose=False):
    """
    Run multiple episodes with the random agent and collect statistics.
    """
    from environment import WumpusEnvironment
    from knowledgeBase import build_init_kb
    
    scores = []
    survival_rate = 0
    gold_found_rate = 0
    
    print(f"Running {num_episodes} episodes with Random Agent...")
    print(f"World size: {world_size}x{world_size}, Wumpuses: {num_wumpuses}, Pit probability: {pit_prob}")
    print()
    
    for episode in range(num_episodes):
        # Create new environment for each episode
        world = WumpusEnvironment(N=world_size, K_wumpuses=num_wumpuses, pit_probability=pit_prob)
        kb = build_init_kb(world_size, world)
        
        # Create random agent
        agent = RandomAgent(kb=kb)
        world.board[1][1].append(agent)
        world.agents.append(agent)
        
        # Run episode
        score = agent.run_episode(world, verbose=verbose and episode < 3)  # Show first 3 episodes if verbose
        scores.append(score)
        
        # Track statistics
        if agent.alive:
            survival_rate += 1
        if agent.found_gold:
            gold_found_rate += 1
        
        if (episode + 1) % 10 == 0:
            print(f"Completed {episode + 1} episodes...")
    
    # Calculate statistics
    survival_rate = survival_rate / num_episodes
    gold_found_rate = gold_found_rate / num_episodes
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    print("\n=== Random Agent Results ===")
    print(f"Episodes: {num_episodes}")
    print(f"Average Score: {avg_score:.2f}")
    print(f"Best Score: {max_score}")
    print(f"Worst Score: {min_score}")
    print(f"Survival Rate: {survival_rate:.2%}")
    print(f"Gold Found Rate: {gold_found_rate:.2%}")
    print()
    
    return {
        'scores': scores,
        'avg_score': avg_score,
        'survival_rate': survival_rate,
        'gold_found_rate': gold_found_rate,
        'max_score': max_score,
        'min_score': min_score
    }


if __name__ == "__main__":
    # Test the random agent
    print("=== Random Agent Baseline Test ===")
    
    # Run a small experiment
    results = run_random_agent_experiment(num_episodes=50, verbose=True)
    
    print("Random Agent baseline implementation complete!")