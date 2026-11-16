# 🐍 Snake Game CLI

Classic Snake for your terminal. Pure Python standard library — no dependencies.

- Flicker-free rendering with square cells (each cell is two characters wide)
- Responsive controls: every key press is buffered, so quick turns never get lost
- Gets faster every level; best score saved per difficulty
- Pause, terminal-resize handling, plain-ASCII mode
- macOS, Linux, WSL and Windows (Windows Terminal / PowerShell / cmd)

## 🚀 Quick start

**Play once (macOS / Linux / WSL)**
```bash
curl -fsSL https://raw.githubusercontent.com/movin-gun/snake/main/play.sh | sh
```

**Play once (Windows PowerShell)**
```powershell
irm https://raw.githubusercontent.com/movin-gun/snake/main/install.ps1 | iex
```

**Install with pip** (recommended)
```bash
pip install git+https://github.com/movin-gun/snake.git
snakegame
```

**Install without pip (macOS / Linux / WSL)**
```bash
curl -fsSL https://raw.githubusercontent.com/movin-gun/snake/main/quick_start.sh | sh -s install
# remove again with: ... | sh -s uninstall
```

**Install without pip (Windows PowerShell)**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/movin-gun/snake/main/install.ps1))) -Mode install
```

**From a clone**
```bash
python3 -m snake_game
```

## 🎮 Controls

| Key | Action |
| --- | --- |
| `← ↑ ↓ →` / `W A S D` / `H J K L` | Move |
| `P` or `Space` | Pause / resume |
| `Q` or `Esc` | End the round |
| `1` `2` `3` | Pick difficulty in the menu |
| `R` | Retry on the game-over screen |

## 📏 Rules

- Every food: **10 points + 2 × (level − 1)**
- Level up every **5 foods**; each level makes the snake faster (down to a per-difficulty cap)
- Hitting a wall or your body ends the round. Moving into the cell your tail is leaving is allowed.
- Fill the whole board to win
- Food turns rainbow from level 3

| Difficulty | Start speed | Fastest |
| --- | --- | --- |
| Easy | 0.16 s/move | 0.08 s |
| Medium | 0.12 s/move | 0.06 s |
| Hard | 0.09 s/move | 0.045 s |

## ⚙️ Options

```
snakegame [-d {easy,medium,hard}] [--no-color] [--scores] [--version]
```

- `-d hard` — skip the menu
- `--no-color` — ASCII-only board (also honoured via the `NO_COLOR` environment variable)
- `--scores` — print best scores and where they are stored

Best scores live in `~/.local/share/snake-game/scores.json`
(`%APPDATA%\snake-game\scores.json` on Windows; override with `SNAKE_GAME_HOME`).

## 🧑‍💻 Development

```
snake_game/
  engine.py    game rules only (no I/O) — unit-tested
  terminal.py  raw keyboard input, ANSI output, terminal sizing
  scores.py    best-score storage
  game.py      menus, rendering, main loop, CLI
tests/         python -m unittest discover -s tests
```

Requires Python 3.7+.

## 📝 License

MIT — see [LICENSE](LICENSE).

Made with ❤️ by Kit Lee
