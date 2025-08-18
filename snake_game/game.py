#!/usr/bin/env python3
"""
Enhanced Snake Game for Terminal
===============================

A modern, cross-platform terminal-based snake game with advanced features:
- Dynamic board sizing with 4:5 visual ratio
- Wall collision explosion effects  
- Cross-platform input handling
- Progressive difficulty system
- Persistent high score tracking

Author: kit_lee
Version: 3.0.1
"""

import sys
import time
import random
import os
import json
import shutil
import platform
import re
from enum import Enum
from datetime import datetime
from typing import Tuple, List, Optional, Dict, Any

# ================================
# PLATFORM DETECTION & IMPORTS
# ================================

# Unix terminal support
try:
    import termios
    import tty
    UNIX_TERMINAL = True
except ImportError:
    UNIX_TERMINAL = False

# Windows terminal support
if platform.system() == 'Windows':
    try:
        import msvcrt
        WINDOWS_TERMINAL = True
    except ImportError:
        WINDOWS_TERMINAL = False
else:
    WINDOWS_TERMINAL = False


# ================================
# CONSTANTS & ENUMS
# ================================

class Direction(Enum):
    """Snake movement directions"""
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


class GameConfig:
    """Game configuration constants"""
    
    # Default terminal dimensions
    DEFAULT_TERM_WIDTH = 80
    DEFAULT_TERM_HEIGHT = 24
    
    # Visual ratio settings
    VISUAL_RATIO_WIDTH = 4
    VISUAL_RATIO_HEIGHT = 5
    
    # Board size constraints
    MIN_BOARD_WIDTH = 20
    MIN_BOARD_HEIGHT = 15
    BOARD_MARGIN_WIDTH = 10
    BOARD_MARGIN_HEIGHT = 8
    
    # Difficulty settings
    DIFFICULTY_SETTINGS = {
        'easy': {'size_modifier': 0.8, 'speed': 0.15},
        'medium': {'size_modifier': 1.0, 'speed': 0.1},
        'hard': {'size_modifier': 1.2, 'speed': 0.05}
    }
    
    # Food generation settings
    WALL_MARGIN = 2
    VERTICAL_MARGIN = 1
    MAX_FOOD_ATTEMPTS = 100
    
    # Scoring system
    BASE_SCORE_PER_FOOD = 10
    LEVEL_BONUS_MULTIPLIER = 2
    FOODS_PER_LEVEL = 5
    
    # Animation settings
    EXPLOSION_FRAMES = 5
    EXPLOSION_FRAME_DURATION = 0.2


class Colors:
    """Terminal color codes and utilities"""
    
    # Basic colors
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_WHITE = '\033[47m'
    
    # Special effects
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    @classmethod
    def color(cls, text: str, color_code: str) -> str:
        """Apply color to text"""
        return f"{color_code}{text}{cls.RESET}"
    
    @classmethod
    def rainbow_text(cls, text: str) -> str:
        """Create rainbow colored text"""
        colors = [cls.RED, cls.YELLOW, cls.GREEN, cls.CYAN, cls.BLUE, cls.MAGENTA]
        result = ""
        for i, char in enumerate(text):
            if char != ' ':
                color = colors[i % len(colors)]
                result += cls.color(char, color + cls.BOLD)
            else:
                result += char
        return result


# ================================
# UTILITY CLASSES
# ================================

class TerminalUtils:
    """Terminal utility functions"""
    
    @staticmethod
    def clear_screen() -> None:
        """Clear terminal screen (cross-platform)"""
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')
    
    @staticmethod
    def get_terminal_size() -> Tuple[int, int]:
        """Get terminal dimensions (width, height)"""
        try:
            size = shutil.get_terminal_size()
            return size.columns, size.lines
        except Exception:
            return GameConfig.DEFAULT_TERM_WIDTH, GameConfig.DEFAULT_TERM_HEIGHT
    
    @staticmethod
    def get_terminal_character_ratio() -> float:
        """Simple character aspect ratio (width:height)"""
        # Use a simple, universal ratio that works well across terminals
        return 0.5
    
    @staticmethod
    def calculate_optimal_board_size(
        term_width: int, 
        term_height: int, 
        target_ratio_w: int = GameConfig.VISUAL_RATIO_WIDTH,
        target_ratio_h: int = GameConfig.VISUAL_RATIO_HEIGHT
    ) -> Tuple[int, int]:
        """Calculate simple board size with good proportions"""
        
        # Calculate available space with margins
        available_width = term_width - GameConfig.BOARD_MARGIN_WIDTH
        available_height = term_height - GameConfig.BOARD_MARGIN_HEIGHT
        
        # Use simple fixed proportions that work well
        board_width = min(available_width, 50)  # Max width 50
        board_height = min(available_height, int(board_width * 1.2))  # Height slightly larger
        
        # Apply constraints
        board_width = max(GameConfig.MIN_BOARD_WIDTH, board_width)
        board_height = max(GameConfig.MIN_BOARD_HEIGHT, board_height)
        
        return board_width, board_height
    
    @staticmethod
    def remove_ansi_codes(text: str) -> str:
        """Remove ANSI color codes from text"""
        return re.sub(r'\x1b\[[0-9;]*m', '', text)
    
    @staticmethod
    def center_text(text: str, width: Optional[int] = None) -> str:
        """Simple text centering without complex calculations"""
        if width is None:
            width, _ = TerminalUtils.get_terminal_size()
        
        # Simple centering - just add some spaces
        clean_text = TerminalUtils.remove_ansi_codes(text)
        padding = max(0, (width - len(clean_text)) // 2)
        return ' ' * padding + text
    
    @staticmethod
    def center_block(lines: List[str], width: Optional[int] = None) -> List[str]:
        """Simple block centering"""
        if width is None:
            width, _ = TerminalUtils.get_terminal_size()
        
        centered_lines = []
        for line in lines:
            clean_line = TerminalUtils.remove_ansi_codes(line)
            padding = max(0, (width - len(clean_line)) // 2)
            centered_lines.append(' ' * padding + line)
        
        return centered_lines


class ScoreManager:
    """Handle score persistence and high score tracking"""
    
    def __init__(self):
        self.score_file = os.path.expanduser("~/.snake_game_scores.json")
        self.scores = self._load_scores()
    
    def _load_scores(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load scores from file"""
        try:
            if os.path.exists(self.score_file):
                with open(self.score_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {'easy': [], 'medium': [], 'hard': []}
    
    def save_score(self, difficulty: str, score: int, level: int, foods_eaten: int) -> bool:
        """Save a new score and return True if it's a high score"""
        score_entry = {
            'score': score,
            'level': level,
            'foods_eaten': foods_eaten,
            'date': datetime.now().isoformat()
        }
        
        if difficulty not in self.scores:
            self.scores[difficulty] = []
        
        self.scores[difficulty].append(score_entry)
        self.scores[difficulty].sort(key=lambda x: x['score'], reverse=True)
        self.scores[difficulty] = self.scores[difficulty][:10]  # Keep top 10
        
        try:
            with open(self.score_file, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except Exception:
            pass
        
        return len(self.scores[difficulty]) == 1 or score >= self.scores[difficulty][0]['score']
    
    def get_high_score(self, difficulty: str) -> int:
        """Get the highest score for a difficulty"""
        if difficulty in self.scores and self.scores[difficulty]:
            return self.scores[difficulty][0]['score']
        return 0
    
    def get_top_scores(self, difficulty: str, count: int = 5) -> List[Dict[str, Any]]:
        """Get top scores for a difficulty"""
        if difficulty in self.scores:
            return self.scores[difficulty][:count]
        return []


# ================================
# MAIN GAME CLASS
# ================================

class SnakeGame:
    """Main Snake Game class with enhanced features"""
    
    def __init__(self, difficulty: str = 'medium'):
        """Initialize the game with specified difficulty"""
        self.difficulty = difficulty
        self.score_manager = ScoreManager()
        
        # Terminal setup
        self.term_width, self.term_height = TerminalUtils.get_terminal_size()
        
        # Calculate optimal board size
        self._setup_board_dimensions()
        
        # Game state initialization
        self._initialize_game_state()
        
        # Input handling setup
        self._setup_input_handling()
    
    def _setup_board_dimensions(self) -> None:
        """Calculate and set optimal board dimensions"""
        optimal_width, optimal_height = TerminalUtils.calculate_optimal_board_size(
            self.term_width, self.term_height
        )
        
        # Apply difficulty modifier
        config = GameConfig.DIFFICULTY_SETTINGS[self.difficulty]
        modifier = config['size_modifier']
        
        self.width = max(GameConfig.MIN_BOARD_WIDTH, int(optimal_width * modifier))
        self.height = max(GameConfig.MIN_BOARD_HEIGHT, int(optimal_height * modifier))
        
        # Ensure terminal bounds
        self.width = min(self.width, self.term_width - GameConfig.BOARD_MARGIN_WIDTH)
        self.height = min(self.height, self.term_height - GameConfig.BOARD_MARGIN_HEIGHT)
        
        # Set game speed
        self.base_speed = config['speed']
    
    def _initialize_game_state(self) -> None:
        """Initialize game state variables"""
        # Score and level tracking
        self.score = 0
        self.foods_eaten = 0
        self.level = 1
        self.last_score_milestone = 0
        
        # Game status
        self.running = True
        
        # Snake initialization (center of board)
        center_y, center_x = self.height // 2, self.width // 2
        self.snake = [
            (center_y, center_x),
            (center_y, center_x - 1),
            (center_y, center_x - 2)
        ]
        
        # Movement setup
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Speed compensation for different movement directions
        self._setup_speed_compensation()
        
        # Generate initial food
        self.food = self._generate_food()
    
    def _setup_speed_compensation(self) -> None:
        """Setup speed compensation for terminal character ratios"""
        self.terminal_type = self._detect_terminal_type()
        
        # Universal speed compensation for cross-platform compatibility
        horizontal_ratio = 0.7  # Make horizontal movement faster
        
        self.speed_ratios = {
            Direction.UP: 1.0,
            Direction.DOWN: 1.0,
            Direction.LEFT: horizontal_ratio,
            Direction.RIGHT: horizontal_ratio
        }
    
    def _setup_input_handling(self) -> None:
        """Setup terminal input handling"""
        self.old_settings = None
        self.terminal_mode = False
        
        if UNIX_TERMINAL:
            try:
                self.old_settings = termios.tcgetattr(sys.stdin)
                tty.setraw(sys.stdin.fileno())
                self.terminal_mode = True
            except Exception:
                pass
    
    def _detect_terminal_type(self) -> str:
        """Detect terminal type for optimizations"""
        term = os.environ.get('TERM', '').lower()
        term_program = os.environ.get('TERM_PROGRAM', '').lower()
        
        if 'iterm' in term_program:
            return 'iterm2'
        elif 'terminal' in term_program:
            return 'macos_terminal'
        elif 'xterm' in term:
            return 'xterm'
        elif platform.system() == 'Windows':
            return 'windows_terminal'
        else:
            return 'generic'
    
    def _generate_food(self) -> Tuple[int, int]:
        """Generate food with improved positioning"""
        attempts = 0
        max_attempts = GameConfig.MAX_FOOD_ATTEMPTS
        
        # Define safe zones
        wall_margin = GameConfig.WALL_MARGIN
        vertical_margin = GameConfig.VERTICAL_MARGIN
        
        safe_top = vertical_margin
        safe_bottom = self.height - vertical_margin - 1
        safe_left = wall_margin
        safe_right = self.width - wall_margin - 1
        
        while attempts < max_attempts:
            # Try safe zone first
            if attempts < max_attempts // 2:
                food_y = random.randint(safe_top, safe_bottom)
                food_x = random.randint(safe_left, safe_right)
            else:
                # Fallback to any valid position
                food_y = random.randint(1, self.height - 2)
                food_x = random.randint(1, self.width - 2)
            
            food_pos = (food_y, food_x)
            
            # Check if position is valid (not on snake)
            if food_pos not in self.snake:
                return food_pos
            
            attempts += 1
        
        # Emergency fallback
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if (y, x) not in self.snake:
                    return (y, x)
        
        # Last resort
        return (1, 1)
    
    def get_key_press(self) -> Optional[str]:
        """Cross-platform non-blocking key input"""
        if WINDOWS_TERMINAL:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if isinstance(key, bytes):
                    key = key.decode('utf-8', errors='ignore')
                # Handle Windows arrow keys
                if ord(key) == 224:  # Special key prefix
                    key2 = msvcrt.getch()
                    if isinstance(key2, bytes):
                        key2 = key2.decode('utf-8', errors='ignore')
                    arrow_map = {'H': 'UP', 'P': 'DOWN', 'K': 'LEFT', 'M': 'RIGHT'}
                    return arrow_map.get(key2, key2)
                return key
            return None
        
        elif UNIX_TERMINAL:
            try:
                import select
                if select.select([sys.stdin], [], [], 0.0)[0]:
                    key = sys.stdin.read(1)
                    # Handle escape sequences for arrow keys
                    if key == '\x1b':  # ESC
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            key += sys.stdin.read(1)  # [
                            if key == '\x1b[' and select.select([sys.stdin], [], [], 0.1)[0]:
                                key += sys.stdin.read(1)  # A/B/C/D
                                arrow_map = {'\x1b[A': 'UP', '\x1b[B': 'DOWN', '\x1b[C': 'RIGHT', '\x1b[D': 'LEFT'}
                                return arrow_map.get(key, key)
                    return key
            except (ImportError, OSError):
                pass
            return None
        
        else:
            return None
    
    def handle_input(self) -> None:
        """Process keyboard input"""
        key = self.get_key_press()
        if not key:
            return
        
        # Simple key mappings
        key_mappings = {
            # Arrow keys (converted by get_key_press)
            'UP': Direction.UP,
            'DOWN': Direction.DOWN,
            'LEFT': Direction.LEFT,
            'RIGHT': Direction.RIGHT,
            # WASD keys
            'w': Direction.UP,
            'W': Direction.UP,
            's': Direction.DOWN,
            'S': Direction.DOWN,
            'a': Direction.LEFT,
            'A': Direction.LEFT,
            'd': Direction.RIGHT,
            'D': Direction.RIGHT,
        }
        
        if key in key_mappings:
            new_direction = key_mappings[key]
            if self._is_valid_direction_change(new_direction):
                self.next_direction = new_direction
        elif key.lower() == 'q':
            self.running = False
    
    def _is_valid_direction_change(self, new_direction: Direction) -> bool:
        """Check if direction change is valid (not opposite)"""
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        return new_direction != opposite_directions.get(self.direction)
    
    def update(self) -> bool:
        """Update game state, return False if game over"""
        # Update direction
        self.direction = self.next_direction
        
        # Calculate new head position
        head = self.snake[0]
        dy, dx = self.direction.value
        new_head = (head[0] + dy, head[1] + dx)
        
        # Check wall collision
        if (new_head[0] < 1 or new_head[0] >= self.height - 1 or 
            new_head[1] < 1 or new_head[1] >= self.width - 1):
            self._show_wall_collision_effect(new_head)
            return False
        
        # Check self collision
        if new_head in self.snake:
            return False
        
        # Move snake
        self.snake.insert(0, new_head)
        
        # Check food consumption
        if new_head == self.food:
            self._handle_food_consumption()
        else:
            self.snake.pop()  # Remove tail if no food eaten
        
        return True
    
    def _handle_food_consumption(self) -> None:
        """Handle when snake eats food"""
        self.foods_eaten += 1
        self.score += GameConfig.BASE_SCORE_PER_FOOD + (self.level - 1) * GameConfig.LEVEL_BONUS_MULTIPLIER
        
        # Level progression
        if self.foods_eaten % GameConfig.FOODS_PER_LEVEL == 0:
            self.level += 1
        
        # Generate new food
        self.food = self._generate_food()
    
    def _show_wall_collision_effect(self, collision_pos: Tuple[int, int]) -> None:
        """Show explosion effect when hitting wall"""
        explosion_chars = ["*", "+"]
        explosion_colors = [Colors.RED, Colors.YELLOW, Colors.WHITE, Colors.YELLOW, Colors.RED]
        
        for frame_idx in range(GameConfig.EXPLOSION_FRAMES):
            TerminalUtils.clear_screen()
            
            board_lines = []
            
            # Header with crash message
            header1 = "+" + "=" * self.width + "+"
            crash_msg = "CRASH!!!"
            header2_padding = (self.width - len(crash_msg)) // 2
            header2 = "|" + " " * header2_padding + crash_msg + " " * (self.width - len(crash_msg) - header2_padding) + "|"
            
            board_lines.extend([header1, header2, header1])
            
            # Game board with explosion effect
            for y in range(self.height):
                row = "|"
                for x in range(self.width):
                    if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1:
                        # Flashing walls
                        wall_char = "#"
                        if frame_idx % 2 == 0:
                            row += Colors.color(wall_char, Colors.BG_RED + Colors.WHITE + Colors.BOLD)
                        else:
                            row += Colors.color(wall_char, Colors.RED + Colors.BOLD)
                    elif (y, x) in self.snake:
                        # Damaged snake
                        if (y, x) == self.snake[0]:
                            row += Colors.color("X", Colors.RED + Colors.BOLD)
                        else:
                            row += Colors.color("~", Colors.RED + Colors.DIM)
                    elif abs(y - collision_pos[0]) <= 1 and abs(x - collision_pos[1]) <= 1:
                        # Explosion effect
                        explosion_char = explosion_chars[frame_idx % len(explosion_chars)]
                        color = explosion_colors[frame_idx] + Colors.BOLD
                        if frame_idx < 3:  # Add blink for first few frames
                            color += Colors.BLINK
                        row += Colors.color(explosion_char, color)
                    else:
                        row += " "
                row += "|"
                board_lines.append(row)
            
            board_lines.append("+" + "=" * self.width + "+")
            
            # Center and display
            self._display_centered_board(board_lines)
            time.sleep(GameConfig.EXPLOSION_FRAME_DURATION)
    
    def _display_centered_board(self, board_lines: List[str]) -> None:
        """Display board lines centered in terminal"""
        vertical_padding = max(0, (self.term_height - len(board_lines)) // 2 - 2)
        for _ in range(vertical_padding):
            print()
        
        for line in board_lines:
            centered_line = TerminalUtils.center_text(line, self.term_width)
            print(centered_line)
    
    def render(self) -> None:
        """Render the game board"""
        TerminalUtils.clear_screen()
        
        # Calculate center padding
        center_padding = max(0, (self.term_width - self.width) // 2)
        
        # Header with centering
        header = f"Score: {self.score} | Level: {self.level} | Foods: {self.foods_eaten}"
        header_padding = max(0, (self.term_width - len(header)) // 2)
        print(' ' * header_padding + header)
        
        border = "=" * self.width
        print(' ' * center_padding + border)
        
        # Game board with centering
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1:
                    row += "#"  # Safe ASCII walls
                elif (y, x) == self.snake[0]:
                    row += "@"  # Snake head
                elif (y, x) in self.snake:
                    row += "o"  # Snake body
                elif (y, x) == self.food:
                    row += "*"  # Food
                else:
                    row += " "
            print(' ' * center_padding + row)
        
        # Footer with centering
        print(' ' * center_padding + border)
        footer = "Arrow keys: Move | Q: Quit"
        footer_padding = max(0, (self.term_width - len(footer)) // 2)
        print(' ' * footer_padding + footer)
    
    def _get_current_tip(self) -> str:
        """Get contextual tip based on game state"""
        if self.level == 1 and self.foods_eaten == 0:
            return "TIP: Eat food (*) to grow and score points!"
        elif self.level >= 3:
            return "AWESOME: Rainbow food gives bonus points!"
        elif len(self.snake) > 10:
            return "CAREFUL: Don't hit your own tail!"
        else:
            return "Arrow keys: Move | Q: Quit"
    
    def game_over(self) -> None:
        """Display game over screen with enhanced stats"""
        TerminalUtils.clear_screen()
        
        # Save score and check for high score
        is_high_score = self.score_manager.save_score(
            self.difficulty, self.score, self.level, self.foods_eaten
        )
        
        box_width = 50
        
        # Enhanced game over title
        if self.score >= 100:
            title_text = "GAME OVER!"
            title = Colors.rainbow_text(title_text)
        else:
            title_text = "GAME OVER!"
            title = Colors.color(title_text, Colors.RED + Colors.BOLD)
        
        # Performance evaluation
        performance_messages = [
            (200, "INCREDIBLE SCORE!", Colors.YELLOW + Colors.BOLD),
            (100, "EXCELLENT PERFORMANCE!", Colors.GREEN + Colors.BOLD),
            (50, "GREAT JOB!", Colors.CYAN + Colors.BOLD),
            (0, "KEEP TRYING!", Colors.WHITE)
        ]
        
        perf_text = "KEEP TRYING!"
        perf_color = Colors.WHITE
        for threshold, message, color in performance_messages:
            if self.score >= threshold:
                perf_text = message
                perf_color = color
                break
        
        performance = Colors.color(perf_text, perf_color)
        
        # High score notification
        high_score_msg = ""
        if is_high_score:
            high_score_msg = Colors.color("🎉 NEW HIGH SCORE! 🎉", Colors.YELLOW + Colors.BOLD + Colors.BLINK)
        
        # Create game over box
        game_over_lines = [
            "+" + "=" * box_width + "+",
            "|" + " " * ((box_width - len(title_text)) // 2) + title + " " * (box_width - len(title_text) - (box_width - len(title_text)) // 2) + "|",
            "|" + " " * box_width + "|",
            "|" + " " * ((box_width - len(perf_text)) // 2) + performance + " " * (box_width - len(perf_text) - (box_width - len(perf_text)) // 2) + "|",
        ]
        
        if high_score_msg:
            hs_text = "🎉 NEW HIGH SCORE! 🎉"
            game_over_lines.extend([
                "|" + " " * box_width + "|",
                "|" + " " * ((box_width - len(hs_text)) // 2) + high_score_msg + " " * (box_width - len(hs_text) - (box_width - len(hs_text)) // 2) + "|"
            ])
        
        # Game statistics
        stats = [
            f"Final Score: {self.score}",
            f"Level Reached: {self.level}",
            f"Foods Eaten: {self.foods_eaten}",
            f"Snake Length: {len(self.snake)}",
            f"Difficulty: {self.difficulty.upper()}"
        ]
        
        game_over_lines.append("|" + " " * box_width + "|")
        game_over_lines.append("|" + " " * ((box_width - 10) // 2) + Colors.color("STATISTICS", Colors.CYAN + Colors.BOLD) + " " * (box_width - 10 - (box_width - 10) // 2) + "|")
        game_over_lines.append("|" + " " * box_width + "|")
        
        for stat in stats:
            stat_colored = Colors.color(stat, Colors.WHITE)
            padding = (box_width - len(stat)) // 2
            game_over_lines.append("|" + " " * padding + stat_colored + " " * (box_width - len(stat) - padding) + "|")
        
        game_over_lines.extend([
            "|" + " " * box_width + "|",
            "|" + " " * ((box_width - 26) // 2) + Colors.color("Press Enter to continue...", Colors.GRAY) + " " * (box_width - 26 - (box_width - 26) // 2) + "|",
            "+" + "=" * box_width + "+"
        ])
        
        # Center and display
        centered_lines = TerminalUtils.center_block(game_over_lines, self.term_width)
        
        vertical_padding = max(0, (self.term_height - len(centered_lines)) // 2 - 2)
        for _ in range(vertical_padding):
            print()
        
        for line in centered_lines:
            print(line)
    
    def cleanup(self) -> None:
        """Cleanup terminal settings"""
        if self.terminal_mode and self.old_settings and UNIX_TERMINAL:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            except Exception:
                pass
    
    def run(self) -> None:
        """Main game loop"""
        try:
            while self.running:
                self.render()
                self.handle_input()
                
                if not self.update():
                    break
                
                # Dynamic speed based on level and direction
                current_speed = self.base_speed * (0.95 ** (self.level - 1))  # Faster each level
                direction_speed = current_speed * self.speed_ratios[self.direction]
                time.sleep(direction_speed)
            
            self.game_over()
            input()  # Wait for user input
            
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()


# ================================
# MENU AND GAME LAUNCHER
# ================================

def select_difficulty() -> Optional[str]:
    """Display simple difficulty selection menu"""
    while True:
        TerminalUtils.clear_screen()
        term_width, term_height = TerminalUtils.get_terminal_size()
        
        # Center the menu
        menu_lines = [
            "",
            "=" * 40,
            "        SNAKE GAME v3.0.1",
            "=" * 40,
            "",
            "SELECT DIFFICULTY:",
            "",
            "1. EASY   - Relaxed pace",
            "2. MEDIUM - Balanced challenge", 
            "3. HARD   - Fast and furious!",
            "4. QUIT   - Exit game",
            "",
            "=" * 40,
            ""
        ]
        
        # Add vertical padding
        vertical_padding = max(0, (term_height - len(menu_lines)) // 2 - 2)
        for _ in range(vertical_padding):
            print()
        
        # Print centered menu
        for line in menu_lines:
            if line.strip():  # Only center non-empty lines
                padding = max(0, (term_width - len(line)) // 2)
                print(' ' * padding + line)
            else:
                print()
        
        try:
            prompt_text = "Enter your choice (1-4): "
            prompt_padding = max(0, (term_width - len(prompt_text)) // 2)
            choice = input(' ' * prompt_padding + prompt_text).strip()
            
            difficulty_map = {
                '1': 'easy',
                '2': 'medium', 
                '3': 'hard',
                '4': None
            }
            
            if choice in difficulty_map:
                return difficulty_map[choice]
            else:
                print("Invalid choice! Press Enter to try again...")
                input()
                
        except (EOFError, KeyboardInterrupt):
            return None


def main() -> None:
    """Main game entry point"""
    try:
        while True:
            difficulty = select_difficulty()
            if difficulty is None:
                break
            
            game = SnakeGame(difficulty)
            game.run()
            
            # Ask to play again
            TerminalUtils.clear_screen()
            term_width, _ = TerminalUtils.get_terminal_size()
            
            restart_lines = [
                "",
                Colors.color("🎮 PLAY AGAIN? 🎮", Colors.CYAN + Colors.BOLD),
                "",
                Colors.color("Press Enter to play again, or 'q' to quit...", Colors.WHITE)
            ]
            
            for line in restart_lines:
                print(TerminalUtils.center_text(line, term_width))
            
            prompt_line = "Your choice: "
            prompt_padding = (term_width - len(prompt_line)) // 2
            
            try:
                restart = input(' ' * prompt_padding + prompt_line).strip().lower()
                if restart == 'q':
                    break
            except (EOFError, KeyboardInterrupt):
                break
                
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        TerminalUtils.clear_screen()
        print(Colors.color("Thanks for playing Snake Game! 🐍", Colors.GREEN + Colors.BOLD))


def cli() -> None:
    """CLI entry point for package installation"""
    main()


if __name__ == "__main__":
    main()