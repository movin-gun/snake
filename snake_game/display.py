"""
Screen geometry: how tall a character cell is relative to its width, how many
characters make one (roughly square) board cell, and how long each move should
take so the snake covers the same on-screen distance per second in every
direction.

Terminal characters are not square. With a typical font a character is about
twice as tall as it is wide, but this ranges from ~1.8 to ~2.7 depending on the
font and line spacing (D2Coding, for example, is narrow and tall). A fixed
"two characters per cell" layout therefore draws tall cells and makes vertical
moves visibly faster than horizontal ones on many setups.
"""
import math

DEFAULT_CHAR_ASPECT = 2.0          # char height / char width when unknown
MIN_CHAR_ASPECT = 1.2
MAX_CHAR_ASPECT = 3.5
CELL_WIDTHS = (1, 2, 3)            # characters per board cell we may use


def clamp_aspect(value):
    return max(MIN_CHAR_ASPECT, min(MAX_CHAR_ASPECT, float(value)))


class Geometry:
    """
    char_aspect: height / width of one terminal character, in pixels.
    cell_chars:  characters per board cell (chosen to make cells most square).
    """

    def __init__(self, char_aspect=DEFAULT_CHAR_ASPECT, source="default"):
        self.char_aspect = clamp_aspect(char_aspect)
        self.source = source
        # pick the width whose cell is closest to square (in log space)
        self.cell_chars = min(CELL_WIDTHS, key=lambda n: abs(math.log(self.char_aspect / n)))

    @property
    def cell_aspect(self):
        """Board cell height / width on screen (1.0 = perfect square)."""
        return self.char_aspect / self.cell_chars

    def move_factors(self):
        """
        Multipliers for the tick interval of (horizontal, vertical) moves.

        Each move's duration is made proportional to the on-screen distance it
        covers, so speed in pixels/second is identical in all directions. The
        factors are normalised so their geometric mean is 1, keeping overall
        pace close to the difficulty's nominal speed.
        """
        h = float(self.cell_chars)      # horizontal step, in char widths
        v = self.char_aspect            # vertical step, in char widths
        mean = math.sqrt(h * v)
        return h / mean, v / mean

    def describe(self):
        return "char %.2f:1 (%s), cell %d char%s wide, cell shape %.2f" % (
            self.char_aspect, self.source, self.cell_chars,
            "" if self.cell_chars == 1 else "s", self.cell_aspect)


def aspect_from_pixels(width_px, height_px):
    if width_px and height_px and width_px > 0 and height_px > 0:
        return float(height_px) / float(width_px)
    return None


def resolve(detected=None, saved=None, override=None):
    """Priority: command-line override > saved calibration > detected > default."""
    if override:
        return Geometry(override, "command line")
    if saved:
        return Geometry(saved, "calibrated")
    if detected:
        return Geometry(detected, "auto-detected")
    return Geometry(DEFAULT_CHAR_ASPECT, "default")
