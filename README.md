# 🐍 Snake Game CLI

A modern terminal-based snake game with enhanced visuals and gameplay features!

## ✨ Features

- 🎮 **Enhanced Gameplay**: Level system with progressive difficulty
- 🌈 **Visual Effects**: Rainbow food, glowing snake, dynamic colors
- 📊 **Smart UI**: Auto-centering, adaptive board sizing, real-time stats
- 🎯 **Improved Food Generation**: Smart positioning away from walls
- ⚡ **Optimized Controls**: Direction-compensated movement speed
- 📱 **Cross-platform**: Works perfectly on any terminal

## 🚀 Quick Start

### 🏠 Homebrew-style installation (Recommended):

**macOS/Linux:**
```bash
# Install permanently
curl -s https://raw.githubusercontent.com/movin-gun/snake/main/quick_start.sh | bash -s install

# Then run anytime with:
snakegame
```

**Windows PowerShell:**
```powershell
# Install permanently
iwr "https://raw.githubusercontent.com/movin-gun/snake/main/install.ps1" | iex -install

# Then run anytime with:
snakegame
```

### ⚡ Quick play (no installation):

**macOS/Linux:**
```bash
curl -s https://raw.githubusercontent.com/movin-gun/snake/main/quick_start.sh | bash
```

**Windows PowerShell:**
```powershell
iwr "https://raw.githubusercontent.com/movin-gun/snake/main/install.ps1" | iex
```

### 📥 Manual download:
```bash
curl -L https://github.com/movin-gun/snake/archive/main.zip -o snake.zip && unzip snake.zip && cd snake-main && python3 snake_game/game.py
```

### 🐍 Install with pip:
```bash
pip install git+https://github.com/movin-gun/snake.git
snakegame
```

## 🎮 How to Play

### Controls
- **Arrow Keys**: Move snake (↑ ↓ ← →)
- **Q**: Quit game
- **1-3**: Select difficulty

### Gameplay Features
- 🍎 **Smart Food**: Spawns away from walls for better gameplay
- 📊 **Level System**: Level up every 5 foods eaten
- 🌈 **Visual Progression**: Rainbow food at level 3+, glowing snake at level 5+
- ⚡ **Adaptive Speed**: Movement speed compensated for terminal character ratios
- 📏 **Dynamic Sizing**: Game board automatically fits your terminal

### Scoring
- **Base Points**: 10 points per food
- **Level Bonus**: +2 points per level above 1
- **Progressive Challenge**: Speed and visual effects increase with level

## 🛠️ Requirements

- Python 3.7+
- **Windows**: Command Prompt, PowerShell, or Windows Terminal
- **macOS/Linux**: Any terminal with ANSI color support
- No external dependencies needed!

## 🖥️ Platform Support

✅ **Windows 10/11**: Full support with native CMD/PowerShell  
✅ **macOS**: Perfect compatibility with Terminal.app and iTerm2  
✅ **Linux**: Works on all major distributions  
✅ **WSL**: Windows Subsystem for Linux supported

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🎉 Enjoy Playing!

Have fun playing this classic game! Try to beat your high score and challenge your friends.

---

Made with ❤️ by Claude Code
