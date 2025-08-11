import random
from object import Thing, Gold, Wall, Pit, Arrow, Stench, Breeze, Glitter, Bump, Scream
from agent import Explorer, Wumpus
from direction import Direction


class WumpusEnvironment:
    def __init__(self, N=8, K_wumpuses=2, pit_probability=0.2, advanced_setting = False):
        self.height = N
        self.width = N
        self.k_wumpuses = K_wumpuses
        self.pit_probability = pit_probability
        self.board = [[[] for _ in range(self.width + 2)] for _ in range(self.height + 2)]
        self.agents = []
        self.game_over = False
        self.status = "ongoing"
        self.gold_taken = False
        self.pit_pos = []
        self.action_counts = 0
        self.is_advanced = advanced_setting

        self.add_wall()

        # add pits
        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                if (y, x) == (1, 1):  # Avoid bottom-left corner
                    continue
                if random.random() < self.pit_probability:
                    self.board[y][x].append(Pit())
                    self.pit_pos.append((y, x))
                    if x > 1 and not any(isinstance(e, Breeze) or isinstance(e, Pit) for e in self.board[y][x - 1]):
                        self.board[y][x - 1].append(Breeze())
                    if x < self.width and not any(isinstance(e, Breeze) or isinstance(e, Pit) for e in self.board[y][x + 1]):
                        self.board[y][x + 1].append(Breeze())
                    if y > 1 and not any(isinstance(e, Breeze) or isinstance(e, Pit) for e in self.board[y - 1][x]):
                        self.board[y - 1][x].append(Breeze())
                    if y < self.height and not any(isinstance(e, Breeze) or isinstance(e, Pit) for e in self.board[y + 1][x]):
                        self.board[y + 1][x].append(Breeze())

        self.wumpus_pos = []
        for _ in range(K_wumpuses):
            while True:
                x = random.randint(1, self.width)
                y = random.randint(1, self.height)
                if (y, x) == (1, 1) or (y, x) in self.pit_pos or (y, x) in self.wumpus_pos:
                    continue
                break
            self.board[y][x].append(Wumpus())
            self.wumpus_pos.append((y, x))
            if x > 1 and not any(isinstance(e, Stench) or isinstance(e, Wumpus) or isinstance(e, Pit) for e in self.board[y][x - 1]):
            # if x > 1:
                self.board[y][x - 1].append(Stench())
            if x < self.width and not any(isinstance(e, Stench) or isinstance(e, Wumpus) or isinstance(e, Pit) for e in self.board[y][x + 1]):
            # if x < self.width:
                self.board[y][x + 1].append(Stench())
            if y > 1 and not any(isinstance(e, Stench) or isinstance(e, Wumpus) or isinstance(e, Pit) for e in self.board[y - 1][x]):
            # if y > 1:
                self.board[y - 1][x].append(Stench())
            if y < self.height and not any(isinstance(e, Stench) or isinstance(e, Wumpus) or isinstance(e, Pit) for e in self.board[y + 1][x]):
            # if y < self.height:
                self.board[y + 1][x].append(Stench())

        used_pos = self.wumpus_pos + self.pit_pos
        while True:
            x = random.randint(1, self.width)
            y = random.randint(1, self.height)
            if (y, x) == (1, 1) or (y, x) in used_pos:
                continue
            break
        self.board[y][x].append(Gold())
        self.board[y][x].append(Glitter())

        

    def add_wall(self):
        for i in range(1, self.height + 1):
            self.board[i][0].append(Wall())
            self.board[i][self.width + 1].append(Wall())

            self.board[0][i].append(Wall())
            self.board[self.height + 1][i].append(Wall())

        self.board[0][0].append(Wall())
        self.board[0][self.width + 1].append(Wall())
        self.board[self.height + 1][0].append(Wall())
        self.board[self.height + 1][self.width + 1].append(Wall())

    def print_board(self):
        for y in range(self.height + 1, -1, -1):
            for x in range(self.width + 2):
                # if y == 0 or x == 0 or y == self.height + 1 or x == self.width + 1:
                #     print("[#########]", end=" ")
                #     continue
                cell = self.board[y][x]
                if not cell:
                    print("[..........]", end=" ")
                else:
                    symbols = []
                    
                    for t in cell:
                        if isinstance(t, Explorer):
                            d = t.direction.direction
                            symbols.append("A" + {Direction.R: ">", Direction.L: "<", Direction.U: "^", Direction.D: "v"}[d])
                        elif isinstance(t, Wumpus):
                            symbols.append("Wu")
                        elif isinstance(t, Pit):
                            symbols.append("Pi")
                        elif isinstance(t, Gold):
                            symbols.append("G")
                        elif isinstance(t, Stench):
                            symbols.append("St")
                        elif isinstance(t, Breeze):
                            symbols.append("Br")
                        elif isinstance(t, Glitter):
                            symbols.append("Gl")
                        elif isinstance(t, Wall):
                            symbols.append("##########")
                    print(f"[{','.join(symbols):<10}]", end=" ")
            print()

    def is_in_map(self, pos):
        y, x = pos[:2]
        return True if y > 0 and y <= self.height and x > 0 and x <= self.width else False

    def update_stench(self):
        # Clear all Stench
        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                self.board[y][x] = [t for t in self.board[y][x] if not isinstance(t, Stench)]

        # Add Stench for each Wumpus
        for y, x in self.wumpus_pos:  # Fixed from (x, y) to (y, x)
            if x > 1 and not any(isinstance(e, Stench) or isinstance(e, Pit) for e in self.board[y][x - 1]) and (y, x - 1) not in self.wumpus_pos:
                self.board[y][x - 1].append(Stench())
            if x < self.width and not any(isinstance(e, Stench) or isinstance(e, Pit) for e in self.board[y][x + 1]) and (y, x + 1) not in self.wumpus_pos:
                self.board[y][x + 1].append(Stench())
            if y > 1 and not any(isinstance(e, Stench) or isinstance(e, Pit) for e in self.board[y - 1][x]) and (y - 1, x) not in self.wumpus_pos:
                self.board[y - 1][x].append(Stench())
            if y < self.height and not any(isinstance(e, Stench) or isinstance(e, Pit) for e in self.board[y + 1][x]) and (y + 1, x) not in self.wumpus_pos:
                self.board[y + 1][x].append(Stench())
    
    
    def exe_action(self, agent, pos, action): #execute action 
        y, x = pos[:2]
        arrow_direction = Direction(agent.direction.direction)
        percepts = []
        
        if(self.is_advanced == True and self.action_counts % 5 == 0):
            self.wumpus_move()

        if isinstance(agent, Explorer) and self.in_danger(agent):
            return percepts  # Return empty percepts if agent is killed 
        agent.bump = False
        if action == 'TurnRight':
            agent.direction += Direction.R
            agent.performance -= 1
        elif action == 'TurnLeft':
            agent.direction += Direction.L
            agent.performance -= 1
        elif action == 'MoveForward':
            location = agent.direction.move_forward(agent.location)
            agent.bump = not self.is_in_map(location)
            if not agent.bump:
                self.board[agent.location[0]][agent.location[1]].remove(agent)
                agent.location = location
                self.board[agent.location[0]][agent.location[1]].append(agent)
            else:
                percepts.append(Bump())
            agent.performance -= 1
        elif action == 'Grab':
            grabbing = False
            for thing in self.board[y][x]:
                if isinstance(thing, Gold):
                    agent.holding.append(thing)
                    print("Grabbing ", thing.__class__.__name__)
                    self.board[y][x].remove(thing)
                    self.gold_taken = True  # Update gold_taken
                    agent.performance += 10
                    grabbing = True
            if not grabbing:
                print("There is no Gold in this position to Grab.")
        elif action == 'Climb':
            if agent.location == (1, 1):  # Agent can only climb out of (1,1)
                agent.performance += 1000 if Gold() in agent.holding else 0
                self.board[y][x].remove(agent)
                self.agents.remove(agent)  # Remove agent from environment
        elif action == 'Shoot':
            """The arrow travels straight down the path the agent is facing"""
            if agent.has_arrow:
                agent.performance -= 10
                arrow_travel = arrow_direction.move_forward(agent.location)
                while self.is_in_map(arrow_travel):
                    arrow_y, arrow_x = arrow_travel[:2]
                    wumpuses = [thing for thing in self.board[arrow_y][arrow_x]
                                if isinstance(thing, Wumpus)]
                    if len(wumpuses):
                        wumpuses[0].alive = False
                        self.k_wumpuses -= 1
                        self.wumpus_pos.remove((arrow_y, arrow_x))
                        self.board[arrow_y][arrow_x].remove(wumpuses[0])
                        percepts.append(Scream())
                        self.update_stench()  # Update stench after Wumpus death
                        break
                    arrow_travel = arrow_direction.move_forward(arrow_travel)
                agent.has_arrow = False
        self.action_counts += 1
        return percepts


    def percept(self, pos):
        #TODO: handle empty perceptions -> done
        y, x = pos[:2]
        percepts = set(e for e in self.board[y][x] if isinstance(e, (Breeze, Stench, Glitter, Scream, Bump)))
        return list(percepts)
    
    def in_danger(self, agent):
        """Check if Explorer is in danger (Pit or Wumpus), if he is, kill him"""
        y, x = agent.location[:2]
        for thing in self.board[y][x]:
            if isinstance(thing, Pit) or (isinstance(thing, Wumpus) and thing.alive):
                agent.alive = False
                agent.performance -= 1000
                agent.killed_by = thing.__class__.__name__
                return True
        return False
    
    def is_end(self):
        """The game is over when the Explorer is killed
        or if he climbs out of the cave only at (1,1)."""
        explorer = [agent for agent in self.agents if isinstance(agent, Explorer)]
        if len(explorer):
            if explorer[0].alive:
                print("Exporer is alive.")
                return False
            else:
                print(f"Death by {explorer[0].killed_by} [-1000].")
        else:
            #TODO ADD ACTION OUT -> remove agent from world
            print("Explorer climbed out {}."
                  .format("with Gold [+1000]!" if self.gold_taken else "without Gold [+0]"))
        return True

    def wumpus_move(self):
        move = ["left", "right", "up", "down"]
        for y, x in self.wumpus_pos:
            #random in range [0, 3]
            direction = random.randint(0, 3)
            if direction == 0:  # Move left
                new_pos = (y, x - 1)
            elif direction == 1:  # Move right
                new_pos = (y, x + 1)
            elif direction == 2:  # Move up
                new_pos = (y + 1, x)
            else:  # Move down
                new_pos = (y - 1, x)

            if self.is_in_map(new_pos) and not any(isinstance(e, Wall) for e in self.board[new_pos[0]][new_pos[1]]) and not any(isinstance(e, Wumpus) for e in self.board[new_pos[0]][new_pos[1]]) and not any(isinstance(e, Pit) for e in self.board[new_pos[0]][new_pos[1]]):
                self.board[y][x] = [t for t in self.board[y][x] if not isinstance(t, Wumpus)]
                self.board[new_pos[0]][new_pos[1]].append(Wumpus())
                self.wumpus_pos.remove((y, x))
                self.wumpus_pos.append(new_pos)
        self.update_stench()  # Update stench after Wumpus moves
        
                
