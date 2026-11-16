#!/usr/bin/env python3
"""
Snake for the terminal: menus, rendering and the main loop.
Game rules live in engine.py; terminal plumbing lives in terminal.py.
"""
import argparse
import re
import sys
import time

if __package__ in (None, ""):  # allow `python3 snake_game/game.py`
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "snake_game"

from snake_game import __version__, scores
from snake_game.engine import DIFFICULTIES, Direction, SnakeEngine
from snake_game.terminal import Terminal, colors_supported

MAX_BOARD = (28, 18)   # cells (width, height)
MIN_BOARD = (12, 8)
DIFFICULTY_NAMES = list(DIFFICULTIES)

KEY_TO_DIRECTION = {
    "UP": Direction.UP, "DOWN": Direction.DOWN,
    "LEFT": Direction.LEFT, "RIGHT": Direction.RIGHT,
    "w": Direction.UP, "s": Direction.DOWN, "a": Direction.LEFT, "d": Direction.RIGHT,
    "k": Direction.UP, "j": Direction.DOWN, "h": Direction.LEFT, "l": Direction.RIGHT,
}

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def visible_len(text):
    return len(_ANSI_RE.sub("", text))


def center(text, width):
    return " " * max(0, (width - visible_len(text)) // 2) + text


# ----------------------------------------------------------------------- look
class Style:
    def __init__(self, color=True, unicode_ok=True):
        self.color = color
        self.box = ("╭", "╮", "╰", "╯", "─", "│") if unicode_ok else ("+", "+", "+", "+", "-", "|")
        self.dot = "·" if unicode_ok else "-"

    def __call__(self, text, *codes):
        if not self.color or not codes:
            return text
        return "\x1b[%sm%s\x1b[0m" % (";".join(str(c) for c in codes), text)

    # cells are two characters wide so the board looks square
    def cell(self, kind, tick=0):
        if not self.color:
            return {"head": "@@", "body": "oo", "food": "<>", "dead": "XX",
                    "dead_body": "xx"}.get(kind, "  ")
        if kind == "head":
            return "\x1b[102m  \x1b[0m"
        if kind == "body":
            return "\x1b[42m  \x1b[0m"
        if kind == "food":
            return "\x1b[101m  \x1b[0m"
        if kind == "food_rainbow":
            return "\x1b[%dm  \x1b[0m" % (101, 103, 105, 106)[tick % 4]
        if kind == "dead":
            return "\x1b[41;97;1mXX\x1b[0m"
        if kind == "dead_body":
            return "\x1b[41m  \x1b[0m" if tick % 2 == 0 else "\x1b[100m  \x1b[0m"
        return "  "


def _unicode_ok():
    enc = (getattr(sys.stdout, "encoding", None) or "").lower()
    try:
        "╭─│·←".encode(enc or "ascii")
        return True
    except (LookupError, UnicodeEncodeError):
        return False


# ------------------------------------------------------------------- screens
class App:
    def __init__(self, term, style, difficulty=None):
        self.term = term
        self.st = style
        self.preset_difficulty = difficulty

    # -- generic menu -------------------------------------------------------
    def menu(self, title_lines, options, selected=0, footer=None, hotkeys=None):
        """Arrow-key menu. Returns the selected index, or None for quit."""
        hotkeys = hotkeys or {}
        last_size = None
        dirty = True
        while True:
            size = self.term.size()
            if size != last_size or dirty:
                self._draw_menu(title_lines, options, selected, footer, clear=size != last_size)
                last_size, dirty = size, False
            for key in self.term.read_keys(0.25):
                dirty = True
                if key in ("UP", "k", "w"):
                    selected = (selected - 1) % len(options)
                elif key in ("DOWN", "j", "s"):
                    selected = (selected + 1) % len(options)
                elif key in ("ENTER", "SPACE"):
                    return selected
                elif key in ("ESC", "q"):
                    return None
                elif key in hotkeys:
                    return hotkeys[key]

    def _draw_menu(self, title_lines, options, selected, footer, clear):
        st = self.st
        tw, th = self.term.size()
        pointer = "▶ " if st.dot == "·" else "> "
        opt_width = max(visible_len(o) for o in options) + 2
        option_lines = []
        for i, opt in enumerate(options):
            if i == selected:
                option_lines.append(st(pointer, 92, 1) + st(opt, 1))
            else:
                option_lines.append("  " + st(opt, 2))
        footer_line = st(footer or "↑↓ select   Enter confirm   Q quit", 90)

        # Title and footer are centred; options share one left edge.
        total = len(title_lines) + len(option_lines) + 3
        out = [""] * max(0, (th - total) // 2)
        out.extend(center(l, tw) for l in title_lines)
        out.append("")
        indent = " " * max(0, (tw - opt_width) // 2)
        out.extend(indent + l for l in option_lines)
        out.append("")
        out.append(center(footer_line, tw))
        self.term.draw(out, clear=clear)

    def logo(self):
        st = self.st
        art = [
            ("  ____              _        ", (92, 1)),
            (" / ___| _ __   __ _| | _____ ", (92, 1)),
            (" \\___ \\| '_ \\ / _` | |/ / _ \\", (32, 1)),
            ("  ___) | | | | (_| |   <  __/", (32, 1)),
            (" |____/|_| |_|\\__,_|_|\\_\\___|", (32,)),
        ]
        width = max(len(t) for t, _ in art)
        lines = [st(t.ljust(width), *codes) for t, codes in art]
        lines.append(st(("terminal edition v%s" % __version__).center(width), 90))
        return lines

    def choose_difficulty(self, current="medium"):
        best = scores.load()
        labels = []
        for name in DIFFICULTY_NAMES:
            b = best.get(name)
            labels.append("%-7s %s" % (name.capitalize(), ("best %d" % b) if b else ""))
        labels.append("Quit")
        hotkeys = {str(i + 1): i for i in range(len(DIFFICULTY_NAMES))}
        idx = self.menu(self.logo(), labels, DIFFICULTY_NAMES.index(current),
                        footer="↑↓/1-3 select   Enter play   Q quit", hotkeys=hotkeys)
        if idx is None or idx == len(DIFFICULTY_NAMES):
            return None
        return DIFFICULTY_NAMES[idx]

    # -- the game -----------------------------------------------------------
    def board_size(self):
        tw, th = self.term.size()
        w = min(MAX_BOARD[0], (tw - 2) // 2)
        h = min(MAX_BOARD[1], th - 4)
        return w, h

    def wait_for_space(self):
        """Block until the terminal can hold the minimum board. False = quit."""
        while True:
            w, h = self.board_size()
            if w >= MIN_BOARD[0] and h >= MIN_BOARD[1]:
                return True
            tw, th = self.term.size()
            need = (MIN_BOARD[0] * 2 + 2, MIN_BOARD[1] + 4)
            self.term.draw([
                self.st("Terminal too small (%dx%d)." % (tw, th), 93, 1),
                "Resize to at least %dx%d," % need,
                "or press Q to quit.",
            ], clear=True)
            if any(k in ("q", "ESC") for k in self.term.read_keys(0.3)):
                return False

    def play(self, difficulty):
        """Run one round. Returns the finished engine, or None if aborted early."""
        if not self.wait_for_space():
            return None
        w, h = self.board_size()
        game = SnakeEngine(w, h, difficulty)
        best = scores.load().get(difficulty, 0)

        paused = False
        too_small = False
        banner_until = 0.0
        tick = 0
        last_size = self.term.size()
        self.render(game, best, tick, status="", clear=True)
        next_tick = time.monotonic() + game.interval

        while game.alive:
            timeout = 0.25 if (paused or too_small) else next_tick - time.monotonic()
            keys = self.term.read_keys(timeout)
            redraw = False
            for key in keys:
                if key in ("q", "ESC"):
                    game.alive = False
                    break
                if key in ("p", "SPACE"):
                    paused = not paused
                    redraw = True
                elif key in KEY_TO_DIRECTION and not paused:
                    game.queue_direction(KEY_TO_DIRECTION[key])
            if not game.alive:
                break

            size = self.term.size()
            clear = size != last_size
            if clear:
                last_size = size
                bw, bh = self.board_size()
                too_small = bw < game.width or bh < game.height
                redraw = True

            now = time.monotonic()
            if paused or too_small:
                next_tick = now + game.interval
            elif now >= next_tick:
                game.step()
                tick += 1
                if game.leveled_up:
                    banner_until = now + 1.5
                # schedule from the previous deadline to avoid drift, but never
                # try to "catch up" after a stall
                next_tick = max(next_tick + game.interval, now + game.interval * 0.5)
                redraw = True

            if redraw and game.alive:
                if too_small:
                    status = "too_small"
                elif paused:
                    status = "paused"
                elif now < banner_until:
                    status = "level_up"
                else:
                    status = ""
                self.render(game, best, tick, status, clear=clear)

        if game.death_cell is not None:
            self.death_animation(game, best)
        return game

    def death_animation(self, game, best):
        for frame in range(6):
            self.render(game, best, frame, status="crash", dead=True)
            time.sleep(0.09)
        # swallow keys mashed during the crash so they don't skip the summary
        self.term.read_keys(0.25)

    def render(self, game, best, tick, status="", clear=False, dead=False):
        st = self.st
        tw, th = self.term.size()
        if status == "too_small":
            msg = [st("Window too small", 93, 1), "enlarge it to continue", st("(Q quits)", 90)]
            pad = [""] * max(0, (th - len(msg)) // 2)
            self.term.draw(pad + [center(m, tw) for m in msg], clear=True)
            return
        tl, tr, bl, br, hz, vt = st.box

        board_w = game.width * 2 + 2
        left = " " * max(0, (tw - board_w) // 2)
        top = max(0, (th - (game.height + 4)) // 2)

        sep = st("  %s  " % st.dot, 90)
        header = sep.join([
            st("Score ", 90) + st(str(game.score), 93, 1),
            st("Best ", 90) + st(str(max(best, game.score)), 33),
            st("Lv ", 90) + st(str(game.level), 96, 1),
            st("Len ", 90) + st(str(len(game.body)), 95),
        ])

        lines = [""] * top
        lines.append(" " * max(0, (tw - visible_len(header)) // 2) + header)
        lines.append(left + st(tl + hz * (board_w - 2) + tr, 90))

        head = game.head
        food_kind = "food_rainbow" if game.level >= 3 else "food"
        wall = st(vt, 90)
        for r in range(game.height):
            row = [left, wall]
            for c in range(game.width):
                cell = (r, c)
                if dead and cell == head:
                    row.append(st.cell("dead"))
                elif cell == head:
                    row.append(st.cell("head"))
                elif cell in game.occupied:
                    row.append(st.cell("dead_body" if dead else "body", tick))
                elif cell == game.food:
                    row.append(st.cell(food_kind, tick))
                else:
                    row.append("  ")
            row.append(wall)
            lines.append("".join(row))
        lines.append(left + st(bl + hz * (board_w - 2) + br, 90))

        messages = {
            "paused": st("PAUSED", 93, 1) + st("  P/Space resume  Q quit", 90),
            "level_up": st("LEVEL UP!", 96, 1) + st("  speed increased", 90),
            "crash": st("CRASH!", 91, 1),
            "too_small": st("Window too small - enlarge to continue", 93, 1),
        }
        footer = messages.get(status) or st("←↑↓→/WASD move   P pause   Q quit", 90)
        lines.append(center(footer, tw))
        self.term.draw(lines, clear=clear)

    def game_over(self, game, difficulty):
        st = self.st
        new_best = scores.record(difficulty, game.score)
        if game.won:
            title = st("YOU WIN!", 92, 1)
        else:
            title = st("GAME OVER", 91, 1)
        if new_best and game.score > 0:
            verdict = st("NEW BEST SCORE!", 93, 1)
        elif game.score >= 200:
            verdict = st("Incredible!", 93)
        elif game.score >= 100:
            verdict = st("Great job!", 92)
        elif game.score >= 50:
            verdict = st("Not bad!", 96)
        else:
            verdict = st("Keep practicing!", 94)
        info = [
            title, "",
            "Score  " + st("%8d" % game.score, 93, 1),
            "Level  %8d" % game.level,
            "Length %8d" % len(game.body),
            "Mode   %8s" % difficulty.capitalize(),
            "", verdict,
        ]
        return self.menu(info, ["Play again", "Change difficulty", "Quit"],
                         footer="↑↓ select   Enter confirm   R retry   Q quit",
                         hotkeys={"r": 0, "y": 0, "n": 2})

    def run(self):
        difficulty = self.preset_difficulty or self.choose_difficulty()
        while difficulty:
            game = self.play(difficulty)
            if game is None:
                return
            choice = self.game_over(game, difficulty)
            if choice == 0:
                continue
            if choice == 1:
                difficulty = self.choose_difficulty(difficulty)
            else:
                return


# ----------------------------------------------------------------------- CLI
def parse_args(argv):
    p = argparse.ArgumentParser(prog="snakegame", description="Classic Snake in your terminal.")
    p.add_argument("-v", "--version", action="version", version="snakegame %s" % __version__)
    p.add_argument("-d", "--difficulty", choices=DIFFICULTY_NAMES,
                   help="skip the menu and start at this difficulty")
    p.add_argument("--no-color", action="store_true", help="plain ASCII rendering")
    p.add_argument("--scores", action="store_true", help="print best scores and exit")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.scores:
        best = scores.load()
        for name in DIFFICULTY_NAMES:
            print("%-7s %d" % (name, best.get(name, 0)))
        print("(%s)" % scores.scores_path())
        return 0

    style = Style(color=colors_supported() and not args.no_color, unicode_ok=_unicode_ok())
    try:
        with Terminal() as term:
            App(term, style, args.difficulty).run()
    except KeyboardInterrupt:
        pass
    print("Thanks for playing!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
