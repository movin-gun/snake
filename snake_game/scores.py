"""Persistent best scores, one per difficulty."""
import json
import os
import sys


def scores_path():
    override = os.environ.get("SNAKE_GAME_HOME")
    if override:
        base = override
    elif sys.platform == "win32":
        base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "snake-game")
    else:
        data_home = os.environ.get("XDG_DATA_HOME") or os.path.join(
            os.path.expanduser("~"), ".local", "share")
        base = os.path.join(data_home, "snake-game")
    return os.path.join(base, "scores.json")


def load():
    try:
        with open(scores_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return {k: int(v) for k, v in data.items() if isinstance(v, (int, float))}
    except (OSError, ValueError, AttributeError):
        return {}


def record(difficulty, score):
    """Store `score` if it beats the current best. Returns True on a new best."""
    scores = load()
    if score <= scores.get(difficulty, 0):
        return False
    scores[difficulty] = score
    path = scores_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, sort_keys=True)
        os.replace(tmp, path)
    except OSError:
        pass  # a read-only home directory should never crash the game
    return True
