"""
Pure game logic for Snake.

Nothing in this module touches the terminal, the clock or global state, so it
can be unit-tested directly and reused by any front end.
"""
import random
from collections import deque
from enum import Enum


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

    @property
    def opposite(self):
        dy, dx = self.value
        return Direction((-dy, -dx))


# Seconds per tick at level 1, and the fastest tick allowed.
DIFFICULTIES = {
    "easy":   {"interval": 0.16, "min_interval": 0.08, "accel": 0.95},
    "medium": {"interval": 0.12, "min_interval": 0.06, "accel": 0.93},
    "hard":   {"interval": 0.09, "min_interval": 0.045, "accel": 0.92},
}

FOODS_PER_LEVEL = 5
BASE_POINTS = 10
LEVEL_BONUS = 2
MAX_QUEUED_TURNS = 3


class SnakeEngine:
    """
    Board coordinates are (row, col) with 0 <= row < height, 0 <= col < width.
    Walls lie just outside that range.
    """

    def __init__(self, width, height, difficulty="medium", rng=None):
        if width < 5 or height < 3:
            raise ValueError("board must be at least 5x3")
        if difficulty not in DIFFICULTIES:
            raise ValueError("unknown difficulty: %r" % (difficulty,))

        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.rng = rng or random.Random()

        self.score = 0
        self.level = 1
        self.foods_eaten = 0
        self.alive = True
        self.won = False
        self.death_cell = None
        self.leveled_up = False  # True only on the tick a level was gained

        row, col = height // 2, width // 2
        self.body = deque([(row, col), (row, col - 1), (row, col - 2)])
        self.occupied = set(self.body)
        self.direction = Direction.RIGHT
        self._turns = deque()

        self.food = self._spawn_food()

    # ------------------------------------------------------------------ input
    def queue_direction(self, direction):
        """
        Buffer a turn. Each turn is validated against the *last queued*
        direction, so fast "up, left" while moving right is two legal turns
        instead of an instant 180-degree suicide.
        """
        last = self._turns[-1] if self._turns else self.direction
        if direction == last or direction == last.opposite:
            return False
        if len(self._turns) >= MAX_QUEUED_TURNS:
            return False
        self._turns.append(direction)
        return True

    # ------------------------------------------------------------------- tick
    @property
    def head(self):
        return self.body[0]

    @property
    def next_direction(self):
        """Direction the next step will take (first queued turn, if any)."""
        return self._turns[0] if self._turns else self.direction

    @property
    def interval(self):
        cfg = DIFFICULTIES[self.difficulty]
        value = cfg["interval"] * (cfg["accel"] ** (self.level - 1))
        return max(cfg["min_interval"], value)

    def step(self):
        """Advance one tick. Returns False once the game has ended."""
        if not self.alive:
            return False
        self.leveled_up = False

        if self._turns:
            self.direction = self._turns.popleft()

        dy, dx = self.direction.value
        new_head = (self.head[0] + dy, self.head[1] + dx)
        eating = new_head == self.food

        if not (0 <= new_head[0] < self.height and 0 <= new_head[1] < self.width):
            return self._die(new_head)

        # The tail moves out of the way this tick unless we are growing,
        # so chasing your own tail is legal.
        tail = self.body[-1]
        if new_head in self.occupied and not (new_head == tail and not eating):
            return self._die(new_head)

        if not eating:
            self.body.pop()
            self.occupied.discard(tail)
        self.body.appendleft(new_head)
        self.occupied.add(new_head)

        if eating:
            self.foods_eaten += 1
            self.score += BASE_POINTS + (self.level - 1) * LEVEL_BONUS
            if self.foods_eaten % FOODS_PER_LEVEL == 0:
                self.level += 1
                self.leveled_up = True
            self.food = self._spawn_food()
            if self.food is None:
                self.won = True
                self.alive = False
                return False
        return True

    # ---------------------------------------------------------------- helpers
    def _die(self, cell):
        self.alive = False
        self.death_cell = cell
        return False

    def _spawn_food(self):
        free = self.width * self.height - len(self.occupied)
        if free <= 0:
            return None
        # Random probing is fast while the board is mostly empty …
        if free > (self.width * self.height) // 4:
            for _ in range(64):
                cell = (self.rng.randrange(self.height), self.rng.randrange(self.width))
                if cell not in self.occupied:
                    return cell
        # … and an exact scan guarantees termination when it is nearly full.
        cells = [
            (r, c)
            for r in range(self.height)
            for c in range(self.width)
            if (r, c) not in self.occupied
        ]
        return self.rng.choice(cells)
