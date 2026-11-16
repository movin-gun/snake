"""Small persistent settings (display calibration), stored next to scores."""
import json
import os

from .scores import scores_path


def settings_path():
    return os.path.join(os.path.dirname(scores_path()), "settings.json")


def load():
    try:
        with open(settings_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save(data):
    path = settings_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        os.replace(tmp, path)
        return True
    except OSError:
        return False


def saved_char_aspect():
    value = load().get("char_aspect")
    return float(value) if isinstance(value, (int, float)) and value > 0 else None


def set_char_aspect(value):
    data = load()
    if value is None:
        data.pop("char_aspect", None)
    else:
        data["char_aspect"] = round(float(value), 3)
    return save(data)
