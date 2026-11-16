import random
import unittest

from snake_game.engine import Direction, SnakeEngine


def make(width=10, height=7, seed=0):
    return SnakeEngine(width, height, "medium", rng=random.Random(seed))


class MovementTests(unittest.TestCase):
    def test_starts_moving_right(self):
        g = make()
        head = g.head
        g.food = (0, 0)
        self.assertTrue(g.step())
        self.assertEqual(g.head, (head[0], head[1] + 1))
        self.assertEqual(len(g.body), 3)

    def test_reverse_is_ignored(self):
        g = make()
        self.assertFalse(g.queue_direction(Direction.LEFT))
        self.assertFalse(g.queue_direction(Direction.RIGHT))

    def test_two_fast_turns_do_not_reverse_into_self(self):
        # Moving right, press UP then LEFT before the next tick:
        # both turns must be applied on successive ticks, not collapsed.
        g = make()
        g.food = (0, 0)
        self.assertTrue(g.queue_direction(Direction.UP))
        self.assertTrue(g.queue_direction(Direction.LEFT))
        row, col = g.head
        self.assertTrue(g.step())
        self.assertEqual(g.head, (row - 1, col))
        self.assertTrue(g.step())
        self.assertEqual(g.head, (row - 1, col - 1))
        self.assertTrue(g.alive)

    def test_turn_queue_is_bounded(self):
        g = make()
        for d in (Direction.UP, Direction.LEFT, Direction.DOWN):
            self.assertTrue(g.queue_direction(d))
        self.assertFalse(g.queue_direction(Direction.RIGHT))


class CollisionTests(unittest.TestCase):
    def test_wall_kills(self):
        g = make(width=6, height=3)
        g.food = (0, 0)
        steps = 0
        while g.step():
            steps += 1
            self.assertLess(steps, 10)
        self.assertFalse(g.alive)
        self.assertEqual(g.death_cell[1], g.width)

    def test_moving_into_tail_cell_is_allowed(self):
        # 2x2 loop: head chases the tail which vacates the cell the same tick.
        g = make()
        g.body.clear()
        g.body.extend([(1, 1), (1, 0), (2, 0), (2, 1)])  # head (1,1), tail (2,1)
        g.occupied = set(g.body)
        g.direction = Direction.RIGHT
        g.food = (5, 5)
        g.queue_direction(Direction.DOWN)
        self.assertTrue(g.step(), "head may enter the cell the tail is leaving")
        self.assertEqual(g.head, (2, 1))

    def test_moving_into_body_kills(self):
        g = make()
        g.body.clear()
        g.body.extend([(2, 2), (2, 1), (3, 1), (3, 2), (3, 3)])
        g.occupied = set(g.body)
        g.direction = Direction.RIGHT
        g.food = (0, 0)
        g.queue_direction(Direction.DOWN)
        self.assertFalse(g.step())
        self.assertEqual(g.death_cell, (3, 2))


class FoodTests(unittest.TestCase):
    def test_eating_grows_and_scores(self):
        g = make()
        row, col = g.head
        g.food = (row, col + 1)
        g.step()
        self.assertEqual(len(g.body), 4)
        self.assertEqual(g.score, 10)
        self.assertNotIn(g.food, g.occupied)

    def test_level_up_every_five_and_speeds_up(self):
        g = make(width=20)
        start_interval = g.interval
        for _ in range(5):
            row, col = g.head
            g.food = (row, col + 1)
            g.step()
        self.assertEqual(g.level, 2)
        self.assertTrue(g.leveled_up)
        self.assertLess(g.interval, start_interval)
        # level 1 foods = 10 each
        self.assertEqual(g.score, 50)

    def test_food_never_spawns_on_snake(self):
        for seed in range(50):
            g = make(width=5, height=3, seed=seed)
            self.assertNotIn(g.food, g.occupied)

    def test_filling_the_board_wins(self):
        g = make(width=5, height=3)
        # Occupy everything except one cell, then eat into it.
        cells = [(r, c) for r in range(3) for c in range(5)]
        target = (0, 4)
        rest = [c for c in cells if c != target]
        # snake path ending with head next to target
        path = [(0, 3), (0, 2), (0, 1), (0, 0), (1, 0), (1, 1), (1, 2), (1, 3),
                (1, 4), (2, 4), (2, 3), (2, 2), (2, 1), (2, 0)]
        self.assertEqual(sorted(path), sorted(rest))
        g.body.clear()
        g.body.extend(path)
        g.occupied = set(path)
        g.direction = Direction.RIGHT
        g.food = target
        self.assertFalse(g.step())
        self.assertTrue(g.won)
        self.assertIsNone(g.death_cell)


if __name__ == "__main__":
    unittest.main()
