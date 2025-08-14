# 🐍 Snake Game CLI

A classic snake game that runs in your terminal! Experience the nostalgic arcade game with modern features and beautiful ASCII art interface.

## ✨ Features

- 🎮 **Classic Gameplay**: Navigate your snake to eat food and grow longer
- 🎯 **Multiple Difficulty Levels**: Choose from Easy, Medium, or Hard
- 🖼️ **Beautiful ASCII Interface**: Retro-style graphics with Unicode characters
- 🏆 **Score Tracking**: Keep track of your high scores
- ⌨️ **Intuitive Controls**: Simple arrow key navigation
- 📱 **Cross-platform**: Works on macOS, Linux, and Windows

## 🚀 설치 방법 (Installation)

### 🐍 pip으로 설치 (추천 방법)

```bash
# 저장소에서 직접 설치
git clone https://github.com/movin-gun/snake.git
cd snake
pip install .

# 게임 실행
snakegame
```

### 🔧 소스에서 직접 실행 (설치 불필요)

```bash
# 저장소 복제
git clone https://github.com/movin-gun/snake.git
cd snake

# 바로 실행
python3 -m snake_game.game
```

### 📱 원클릭 실행 (macOS/Linux)

```bash
# 임시 디렉토리에서 바로 실행
curl -s https://raw.githubusercontent.com/movin-gun/snake/main/quick_start.sh | bash
```

### 🍺 홈브루로 설치 (향후 지원 예정)

```bash
# 현재는 지원되지 않습니다
# brew tap movin-gun/snake
# brew install snake-game-cli
# snakegame
```

## 🎮 게임 실행 방법 (How to Play)

### 게임 시작하기

```bash
# 홈브루 또는 pip 설치 후
snakegame

# 다른 명령어들
snake-game
snake

# 소스에서 직접 실행 (설치 없이)
python3 -m snake_game.game
```

### 게임 조작법 (Game Controls)

- **방향키 (Arrow Keys)**: 스네이크 이동 (↑ ↓ ← →)
- **Q키**: 현재 게임 종료
- **메뉴 탐색**: 숫자키 (1-5)로 메뉴 선택

### 게임 규칙 (Game Rules)

1. **목표**: 음식 (◆)을 먹어서 스네이크를 키우고 점수 획득
2. **이동**: 스네이크는 선택한 방향으로 계속 이동
3. **성장**: 음식을 먹을 때마다 스네이크가 한 칸씩 길어짐
4. **점수**: 음식 하나당 10점 획득
5. **게임 오버**: 벽이나 자신의 몸에 부딪히면 게임 종료

### 난이도 단계 (Difficulty Levels)

| 난이도 (Difficulty) | 게임판 크기 (Board Size) | 속도 (Speed) | 추천 대상 (Recommended For) |
|------------|------------|-------|-----------------|
| 🟢 쉬움 (Easy) | 15 x 25 | 느림 (Slow) | 초보자 (Beginners) |
| 🟡 보통 (Medium) | 20 x 35 | 보통 (Normal) | 일반 플레이어 (Regular players) |
| 🔴 어려움 (Hard) | 25 x 45 | 빠름 (Fast) | 고수 (Advanced players) |

## 🎯 고득점 팁 (Tips for High Scores)

- 💡 **넓은 공간 활용**: 벽 근처에서 갇히지 않도록 주의
- 💡 **경로 계획**: 음식이 나타날 위치를 미리 예측하여 이동
- 💡 **속도 조절**: 좁은 공간에서는 서두르지 말고 신중하게
- 💡 **벽 활용**: 때로는 벽을 따라 이동하여 공간 확보

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
