# 🐍 Snake Game CLI

A classic snake game that runs in your terminal! Experience the nostalgic arcade game with modern features and beautiful ASCII art interface.

## ✨ Features

- 🎮 **Classic Gameplay**: Navigate your snake to eat food and grow longer
- 🎯 **Multiple Difficulty Levels**: Choose from Easy, Medium, or Hard
- 🖼️ **Beautiful ASCII Interface**: Retro-style graphics with Unicode characters
- 🏆 **Score Tracking**: Keep track of your high scores
- ⌨️ **Intuitive Controls**: Simple arrow key navigation
- 📱 **Cross-platform**: Works on macOS, Linux, and Windows

## 🚀 Installation

### Via Homebrew (macOS/Linux)

```bash
# Add the tap (if available)
brew tap movin-gun/snake

# Install the game
brew install snake-game-cli
```

### Via pip

```bash
pip install snake-game-cli
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/movin-gun/snake.git
cd snake

# Install using pip
pip install .
```

## 🎮 How to Play

### Starting the Game

```bash
# Run the game
snake-game

# Or use the short command
snake

# Or run directly from source
python -m snake_game.game
```

### Game Controls

- **Arrow Keys**: Move the snake (↑ ↓ ← →)
- **Q**: Quit the current game
- **Menu Navigation**: Use number keys (1-5) to navigate menus

### Game Rules

1. **Objective**: Eat food (◆) to grow your snake and increase your score
2. **Movement**: Your snake moves continuously in the direction you choose
3. **Growth**: Each food item eaten adds one segment to your snake
4. **Scoring**: Earn 10 points for each food item consumed
5. **Game Over**: The game ends if you hit the walls or your own body

### Difficulty Levels

| Difficulty | Board Size | Speed | Recommended For |
|------------|------------|-------|-----------------|
| 🟢 Easy | 15 x 30 | Slow | Beginners |
| 🟡 Medium | 20 x 40 | Normal | Regular players |
| 🔴 Hard | 25 x 50 | Fast | Advanced players |

## 🎯 Tips for High Scores

- 💡 **Stay in Open Areas**: Avoid getting trapped near walls
- 💡 **Plan Your Route**: Think ahead about where the food will appear
- 💡 **Control Your Speed**: Don't rush, especially in tight spaces
- 💡 **Use the Edges**: Sometimes hugging walls can help create space

## 🛠️ Development

### Requirements

- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

### Running from Source

```bash
# Clone the repository
git clone https://github.com/movin-gun/snake.git
cd snake

# Run directly
python -m snake_game.game

# Or install in development mode
pip install -e .
snake-game
```

### Project Structure

```
snake/
├── snake_game/
│   ├── __init__.py
│   └── game.py
├── Formula/
│   └── snake-game-cli.rb
├── setup.py
├── README.md
├── LICENSE
└── MANIFEST.in
```

## 🐛 Troubleshooting

### Common Issues

1. **Arrow keys not working**: Ensure your terminal supports ANSI escape sequences
2. **Display issues**: Try adjusting your terminal font size or window size
3. **Performance**: If the game runs too slowly/quickly, try a different difficulty level

### System Requirements

- **macOS**: Terminal.app, iTerm2, or any ANSI-compatible terminal
- **Linux**: Most modern terminal emulators
- **Windows**: Windows Terminal, PowerShell, or WSL

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🎉 Enjoy Playing!

Have fun playing this classic game! Try to beat your high score and challenge your friends.

---

Made with ❤️ by Claude Code
