"""
Cross-platform terminal handling: raw key input, ANSI output, sizing.
"""
import os
import re
import shutil
import struct
import sys
import time

if os.name == "nt":  # pragma: no cover - exercised on Windows CI only
    import msvcrt
    termios = tty = select = None
else:
    import fcntl
    import select
    import termios
    import tty
    msvcrt = None


# ---------------------------------------------------------------- key parsing
_ESCAPE_KEYS = {
    "\x1b[A": "UP", "\x1b[B": "DOWN", "\x1b[C": "RIGHT", "\x1b[D": "LEFT",
    "\x1bOA": "UP", "\x1bOB": "DOWN", "\x1bOC": "RIGHT", "\x1bOD": "LEFT",
}
_WINDOWS_KEYS = {"H": "UP", "P": "DOWN", "K": "LEFT", "M": "RIGHT"}


def parse_keys(data):
    """
    Turn a chunk of raw terminal bytes (decoded to str) into key tokens:
    'UP' 'DOWN' 'LEFT' 'RIGHT' 'ENTER' 'ESC' 'SPACE' or a lowercase char.
    Unknown escape sequences are swallowed instead of leaking as letters.
    """
    keys = []
    i = 0
    n = len(data)
    while i < n:
        ch = data[i]
        if ch == "\x1b":
            if i + 1 < n and data[i + 1] in "[O":
                # CSI / SS3: ESC [ params final-byte
                j = i + 2
                while j < n and not ("@" <= data[j] <= "~"):
                    j += 1
                seq = data[i:j + 1]
                if seq in _ESCAPE_KEYS:
                    keys.append(_ESCAPE_KEYS[seq])
                elif j >= n:
                    pass  # truncated sequence: drop it
                i = j + 1
                continue
            keys.append("ESC")
        elif ch in "\r\n":
            keys.append("ENTER")
        elif ch == " ":
            keys.append("SPACE")
        elif ch == "\x03":
            raise KeyboardInterrupt
        elif ch.isprintable():
            keys.append(ch.lower())
        i += 1
    return keys


def parse_pixel_reports(text, rows=0, cols=0):
    """
    Extract (char_width_px, char_height_px) from XTWINOPS replies:
      ESC [ 6 ; height ; width t   (cell size)
      ESC [ 4 ; height ; width t   (text area size, divided by rows/cols)
    """
    m = re.search(r"\x1b\[6;(\d+);(\d+)t", text)
    if m and int(m.group(1)) > 0 and int(m.group(2)) > 0:
        return int(m.group(2)), int(m.group(1))
    m = re.search(r"\x1b\[4;(\d+);(\d+)t", text)
    if m and rows and cols and int(m.group(1)) > 0 and int(m.group(2)) > 0:
        return int(m.group(2)) / float(cols), int(m.group(1)) / float(rows)
    return None


# ------------------------------------------------------------------- ANSI out
CSI = "\x1b["
ALT_SCREEN_ON = CSI + "?1049h"
ALT_SCREEN_OFF = CSI + "?1049l"
CURSOR_HIDE = CSI + "?25l"
CURSOR_SHOW = CSI + "?25h"
HOME = CSI + "H"
CLEAR = CSI + "2J"
CLEAR_EOL = CSI + "K"
CLEAR_BELOW = CSI + "J"


def _enable_windows_vt():  # pragma: no cover - Windows only
    """Turn on ANSI escape processing for the classic Windows console."""
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
            return True
    except Exception:
        pass
    os.system("")  # side effect: enables VT mode on Windows 10+
    return True


def colors_supported():
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return sys.stdout.isatty()


class Terminal:
    """
    Context manager that puts the terminal into game mode (cbreak, alternate
    screen, hidden cursor) and *always* restores it on exit.
    """

    def __init__(self):
        self._fd = None
        self._tty_file = None
        self._saved = None
        self.out = sys.stdout

    # -- lifecycle
    def __enter__(self):
        if msvcrt is not None:
            _enable_windows_vt()
        else:
            fd = sys.stdin.fileno() if sys.stdin and sys.stdin.isatty() else None
            if fd is None:
                # e.g. launched by `curl ... | sh` where stdin is the pipe
                try:
                    self._tty_file = open("/dev/tty", "rb", buffering=0)
                    fd = self._tty_file.fileno()
                except OSError:
                    raise SystemExit("snake: no interactive terminal available")
            self._fd = fd
            self._saved = termios.tcgetattr(fd)
            tty.setcbreak(fd)
        self.write(ALT_SCREEN_ON + CURSOR_HIDE + CLEAR + HOME)
        return self

    def __exit__(self, *exc):
        try:
            self.write(CSI + "0m" + CURSOR_SHOW + ALT_SCREEN_OFF)
        finally:
            if self._saved is not None:
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._saved)
            if self._tty_file is not None:
                self._tty_file.close()
        return False

    # -- output
    def write(self, text):
        self.out.write(text)
        self.out.flush()

    def draw(self, lines, clear=False):
        """Repaint the whole screen in one write, without flicker."""
        buf = [CLEAR if clear else "", HOME]
        for line in lines:
            buf.append(line)
            buf.append(CLEAR_EOL + "\r\n")
        buf.append(CLEAR_BELOW)
        self.write("".join(buf))

    @staticmethod
    def size():
        s = shutil.get_terminal_size((80, 24))
        return s.columns, s.lines

    # -- geometry
    def char_pixel_size(self, query=True):
        """
        (width, height) in pixels of one character cell, or None if the
        terminal does not tell us. Tries the kernel window size first (free),
        then asks the terminal with XTWINOPS escape queries.
        """
        if msvcrt is not None or self._fd is None:  # pragma: no cover
            return None
        try:
            raw = fcntl.ioctl(self._fd, termios.TIOCGWINSZ, b"\0" * 8)
            rows, cols, xpix, ypix = struct.unpack("HHHH", raw)
            if rows and cols and xpix > 0 and ypix > 0:
                return xpix / float(cols), ypix / float(rows)
        except OSError:
            rows = cols = 0
        if not query:
            return None
        return self._query_pixel_size(rows, cols)

    def _query_pixel_size(self, rows, cols, timeout=0.3):
        # CSI 16 t -> cell size, CSI 14 t -> window size, CSI c (DA1) is
        # answered by virtually every terminal and tells us when to stop waiting.
        self.write("\x1b[16t\x1b[14t\x1b[c")
        data = b""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            ready, _, _ = select.select([self._fd], [], [], deadline - time.monotonic())
            if not ready:
                break
            data += os.read(self._fd, 1024)
            if re.search(rb"\x1b\[\?[\d;]*c", data):
                break
        return parse_pixel_reports(data.decode("ascii", "ignore"), rows, cols)

    # -- input
    def read_keys(self, timeout):
        """Wait up to `timeout` seconds; return every key pressed meanwhile."""
        if msvcrt is not None:  # pragma: no cover
            return self._read_keys_windows(timeout)
        ready, _, _ = select.select([self._fd], [], [], max(0.0, timeout))
        if not ready:
            return []
        data = os.read(self._fd, 1024)
        # A lone ESC may be the start of a sequence split across reads.
        if data.endswith(b"\x1b") or data.endswith(b"\x1b["):
            more, _, _ = select.select([self._fd], [], [], 0.02)
            if more:
                data += os.read(self._fd, 1024)
        return parse_keys(data.decode("utf-8", errors="ignore"))

    def _read_keys_windows(self, timeout):  # pragma: no cover
        deadline = time.monotonic() + max(0.0, timeout)
        keys = []
        while True:
            while msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ("\x00", "\xe0"):
                    code = msvcrt.getwch()
                    if code in _WINDOWS_KEYS:
                        keys.append(_WINDOWS_KEYS[code])
                else:
                    keys.extend(parse_keys(ch))
            if keys or time.monotonic() >= deadline:
                return keys
            time.sleep(0.01)
