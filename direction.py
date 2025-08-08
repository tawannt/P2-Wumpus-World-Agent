

class Direction:
    R = "right"
    L = "left"
    U = "up"
    D = "down"

    def __init__(self, direction):
        self.direction = direction

    def __add__(self, heading):
        if self.direction == self.R:
            return {self.R: Direction(self.D), self.L: Direction(self.U)}.get(heading, None)
        elif self.direction == self.L:
            return {self.R: Direction(self.U), self.L: Direction(self.D)}.get(heading, None)
        elif self.direction == self.U:
            return {self.R: Direction(self.R), self.L: Direction(self.L)}.get(heading, None)
        elif self.direction == self.D:
            return {self.R: Direction(self.L), self.L: Direction(self.R)}.get(heading, None)

    def __iadd__(self, heading):
        new_dir = self + heading
        if new_dir:
            self.direction = new_dir.direction
        return self

    def move_forward(self, from_location):
        iclass = from_location.__class__
        y, x = from_location
        if self.direction == self.R:
            return iclass((y, x + 1))
        elif self.direction == self.L:
            return iclass((y, x - 1))
        elif self.direction == self.U:
            return iclass((y + 1, x))
        elif self.direction == self.D:
            return iclass((y - 1, x))
        
