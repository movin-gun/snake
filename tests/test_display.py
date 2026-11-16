import math
import unittest

from snake_game import display
from snake_game.engine import Direction, SnakeEngine
from snake_game.terminal import parse_pixel_reports


class GeometryTests(unittest.TestCase):
    def test_standard_font_uses_two_chars(self):
        g = display.Geometry(2.0)
        self.assertEqual(g.cell_chars, 2)
        self.assertAlmostEqual(g.cell_aspect, 1.0)
        fh, fv = g.move_factors()
        self.assertAlmostEqual(fh, 1.0)
        self.assertAlmostEqual(fv, 1.0)

    def test_narrow_tall_font_uses_three_chars(self):
        # e.g. D2Coding: ~8 x 21 px
        g = display.Geometry(21 / 8.0)
        self.assertEqual(g.cell_chars, 3)
        self.assertLess(abs(math.log(g.cell_aspect)), abs(math.log(g.char_aspect / 2)))

    def test_move_time_proportional_to_screen_distance(self):
        for aspect in (1.8, 2.0, 2.2, 2.4, 2.7, 3.0):
            g = display.Geometry(aspect)
            fh, fv = g.move_factors()
            # pixels per second, in units of char width
            speed_h = g.cell_chars / fh
            speed_v = g.char_aspect / fv
            self.assertAlmostEqual(speed_h, speed_v, places=9)
            self.assertAlmostEqual(fh * fv, 1.0, places=9)

    def test_clamped(self):
        self.assertEqual(display.Geometry(10).char_aspect, display.MAX_CHAR_ASPECT)
        self.assertEqual(display.Geometry(0.1).char_aspect, display.MIN_CHAR_ASPECT)

    def test_resolve_priority(self):
        self.assertEqual(display.resolve(2.1, 2.3, 2.5).source, "command line")
        self.assertEqual(display.resolve(2.1, 2.3).char_aspect, 2.3)
        self.assertEqual(display.resolve(2.1).source, "auto-detected")
        self.assertEqual(display.resolve().char_aspect, display.DEFAULT_CHAR_ASPECT)


class PixelReportTests(unittest.TestCase):
    def test_cell_size_report(self):
        self.assertEqual(parse_pixel_reports("\x1b[6;17;8t\x1b[?62;22c"), (8, 17))

    def test_window_size_report_fallback(self):
        self.assertEqual(parse_pixel_reports("\x1b[4;480;800t", rows=24, cols=100), (8.0, 20.0))

    def test_no_report(self):
        self.assertIsNone(parse_pixel_reports("\x1b[?1;2c"))
        self.assertIsNone(parse_pixel_reports("\x1b[6;0;0t"))


class NextDirectionTests(unittest.TestCase):
    def test_peeks_queued_turn(self):
        g = SnakeEngine(10, 7)
        self.assertEqual(g.next_direction, Direction.RIGHT)
        g.queue_direction(Direction.UP)
        self.assertEqual(g.next_direction, Direction.UP)
        self.assertEqual(g.direction, Direction.RIGHT)


if __name__ == "__main__":
    unittest.main()
