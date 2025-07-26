import random
import time
from object import Thing, Gold, Wall, Pit, Arrow, Stench, Breeze, Glitter, Bump, Scream
from agent import Explorer, Wumpus
from direction import Direction

class WumpusEnvironment:
    def __init__(self, N=8, K_wumpuses=2, pit_probability=0.2):
        self.height = N
        self.width = N
        self.k_wumpuses = K_wumpuses
        self.pit_probability = pit_probability
        self.board = [[[] for _ in range(self.width + 2)] for _ in range(self.height + 2)]
        self.game_over = False
        self.status = "ongoing"

        self.pit_pos = []

        self.add_wall()

        # add pits
        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                if (y, x) == (1, 1):  # Avoid bottom-left corner
                    continue
                if random.random() < self.pit_probability:
                    self.board[y][x].append(Pit())
                    self.pit_pos.append((y, x))
                    if x > 1 and not any(isinstance(e, Breeze) for e in self.board[y][x - 1]):
                        self.board[y][x - 1].append(Breeze())
                    if x < self.width and not any(isinstance(e, Breeze) for e in self.board[y][x + 1]):
                        self.board[y][x + 1].append(Breeze())
                    if y > 1 and not any(isinstance(e, Breeze) for e in self.board[y - 1][x]):
                        self.board[y - 1][x].append(Breeze())
                    if y < self.height and not any(isinstance(e, Breeze) for e in self.board[y + 1][x]):
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
            if x > 1 and not any(isinstance(e, Stench) for e in self.board[y][x - 1]):
                self.board[y][x - 1].append(Stench())
            if x < self.width and not any(isinstance(e, Stench) for e in self.board[y][x + 1]):
                self.board[y][x + 1].append(Stench())
            if y > 1 and not any(isinstance(e, Stench) for e in self.board[y - 1][x]):
                self.board[y - 1][x].append(Stench())
            if y < self.height and not any(isinstance(e, Stench) for e in self.board[y + 1][x]):
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
        for y in range(self.height + 2):
            self.board[y][0].append(Wall())
            self.board[y][self.width + 1].append(Wall())

        for x in range(self.width + 2):
            self.board[0][x].append(Wall())
            self.board[self.height + 1][x].append(Wall())

    def print_board(self):
        for y in range(self.height + 1, -1, -1):
            for x in range(self.width + 2):
                if y == 0 or x == 0 or y == self.height + 1 or x == self.width + 1:
                    print("[#########]", end=" ")
                    continue
                cell = self.board[y][x]
                if not cell:
                    print("[    .    ]", end=" ")
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
                            symbols.append("Go")
                        elif isinstance(t, Stench):
                            symbols.append("St")
                        elif isinstance(t, Breeze):
                            symbols.append("Br")
                        elif isinstance(t, Glitter):
                            symbols.append("Gl")
                    print(f"[{' '.join(symbols):<9}]", end=" ")
            print()

    
    def percept(self, pos):
        #TODO: handle empty perceptions
        y, x = pos[:2]
        percepts = set(e for e in self.board[y][x] if isinstance(e, (Breeze, Stench, Glitter, Scream, Bump)))
        return list(percepts)
    
    def in_danger(self, agent):
        """Check if Explorer is in danger (Pit or Wumpus), if he is, kill him"""
        y, x = agent.current_pos[:2]
        for thing in self.board[y][x]:
            if isinstance(thing, Pit) or (isinstance(thing, Wumpus) and thing.alive):
                agent.alive = False
                agent.performance -= 1000
                agent.killed_by = thing.__class__.__name__
                return True
        return False

    def kill_wumpus(self, agent):
        killed = False
        new_wumpus_pos = self.wumpus_pos.copy()
        current_pos = agent.current_pos
        while self.is_inbounds(current_pos):
            y, x = current_pos
            if any(isinstance(thing, Wumpus) for thing in self.board[y][x]):
                killed = True
                self.k_wumpuses -= 1
                self.board[y][x] = [t for t in self.board[y][x] if not isinstance(t, Wumpus)]
                new_wumpus_pos.remove((y, x))
                agent.has_arrow = False
                self.board[y][x].append(Scream())
                # Remove Stench only if no other Wumpus contributes
                adjacent_cells = []
                if x > 0:
                    adjacent_cells.append((x - 1, y))
                if x < self.width:
                    adjacent_cells.append((x + 1, y))
                if y > 0:
                    adjacent_cells.append((y, x - 1))
                if y < self.height:
                    adjacent_cells.append((y, x + 1))
                for ax, ay in adjacent_cells:
                    keep_stench = any((wx, wy) != (y, x) and
                                      ((wx == ax and abs(wy - ay) <= 1) or (wy == ay and abs(wx - ax) <= 1))
                                      for wx, wy in self.wumpus_pos)
                    if not keep_stench and any(isinstance(e, Stench) for e in self.board[ay][ax]):
                        self.board[ay][ax] = [e for e in self.board[ay][ax] if not isinstance(e, Stench)]
            current_pos = agent.direction.move_forward(current_pos)
        self.wumpus_pos = new_wumpus_pos
        return killed

    def is_inbounds(self, pos):
        y, x = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def in_danger(self, agent):
        y, x = agent.current_pos
        if any(isinstance(t, Wumpus) for t in self.board[y][x]):
            agent.killed_by = "Wumpus"
            return True
        if any(isinstance(t, Pit) for t in self.board[y][x]):
            agent.killed_by = "Pit"
            return True
        return False

    def execute_action(self, agent: Explorer, action: str):
        # Clear temporary percepts
        y, x = agent.current_pos
        self.board[y][x] = [t for t in self.board[y][x] if not isinstance(t, (Bump, Scream))]
        # Check for danger
        if self.in_danger(agent):
            self.game_over = True
            return ([], True, "dead")
        percepts = []
        game_over = False
        status = "ongoing"
        if action == "MoveForward":
            new_pos = agent.direction.move_forward(agent.current_pos)
            if not self.is_inbounds(new_pos):
                percepts.append(Bump())
                agent.performance -= 1
            else:
                self.board[agent.current_pos[1]][agent.current_pos[0]] = [t for t in self.board[agent.current_pos[1]][agent.current_pos[0]] if not isinstance(t, Explorer)]
                agent.current_pos = new_pos
                self.board[new_pos[1]][new_pos[0]].append(agent)
                agent.performance -= 1
                if self.in_danger(agent):
                    self.game_over = True
                    return ([], True, "dead")
        elif action == "TurnLeft":
            agent.direction = agent.direction + "left"
            agent.performance -= 1
        elif action == "TurnRight":
            agent.direction = agent.direction + "right"
            agent.performance -= 1
        elif action == "Grab":
            if any(isinstance(t, Gold) for t in self.board[agent.current_pos[1]][agent.current_pos[0]]):
                agent.holding.append(Gold())
                self.board[agent.current_pos[1]][agent.current_pos[0]] = [t for t in self.board[agent.current_pos[1]][agent.current_pos[0]] if not isinstance(t, (Gold, Glitter))]
                agent.performance += 1000
            agent.performance -= 1
        elif action == "Shoot":
            agent.performance -= 1
            if agent.has_arrow:
                agent.performance -= 10
                self.kill_wumpus(agent)
        elif action == "ClimbOut":
            if agent.current_pos == (0,0) and any(isinstance(t, Gold) for t in agent.holding):
                agent.performance += 1000
                self.board[agent.current_pos[1]][agent.current_pos[0]] = [t for t in self.board[agent.current_pos[1]][agent.current_pos[0]] if not isinstance(t, Explorer)]
                game_over = True
                status = "climbed_out"
            agent.performance -= 1
        percepts.extend(self.percept(agent.current_pos))
        return (percepts, game_over, status)
