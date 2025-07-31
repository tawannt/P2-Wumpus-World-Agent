class Direction:
    """A direction class for agents that want to move in a 2D plane
        Usage:
            d = Direction("down")
            To change directions:
            d = d + "right" or d = d + Direction.R #Both do the same thing
            Note that the argument to __add__ must be a string and not a Direction object.
            Also, it (the argument) can only be right or left."""

    R = "right"
    L = "left"
    U = "up"
    D = "down"

    def __init__(self, direction):
        self.direction = direction

    def __add__(self, heading):
        """
        >>> d = Direction('right')
        >>> l1 = d.__add__(Direction.L)
        >>> l2 = d.__add__(Direction.R)
        >>> l1.direction
        'up'
        >>> l2.direction
        'down'
        >>> d = Direction('down')
        >>> l1 = d.__add__('right')
        >>> l2 = d.__add__('left')
        >>> l1.direction == Direction.L
        True
        >>> l2.direction == Direction.R
        True
        """
        if self.direction == self.R:
            return {
                self.R: Direction(self.D),
                self.L: Direction(self.U),
            }.get(heading, None)
        elif self.direction == self.L:
            return {
                self.R: Direction(self.U),
                self.L: Direction(self.D),
            }.get(heading, None)
        elif self.direction == self.U:
            return {
                self.R: Direction(self.R),
                self.L: Direction(self.L),
            }.get(heading, None)
        elif self.direction == self.D:
            return {
                self.R: Direction(self.L),
                self.L: Direction(self.R),
            }.get(heading, None)

    def __iadd__(self, heading):
        new_dir = self + heading
        if new_dir:
            self.direction = new_dir.direction
        return self

    def move_forward(self, from_location):
        """
        >>> d = Direction('up')
        >>> l1 = d.move_forward((1, 1))
        >>> l1
        (2, 1)
        >>> d = Direction(Direction.R)
        >>> l1 = d.move_forward((1, 1))
        >>> l1
        (1, 2)
        >>> d = Direction(Direction.D)
        >>> l1 = d.move_forward((2, 1))
        >>> l1
        (1, 1)
        """
        # get the iterable class to return
        # e.g, input is tuple -> use iclass to get tuple, then output is also tuple
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


