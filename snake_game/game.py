#!/usr/bin/env python3
"""
Simple Snake Game for Terminal
Simplified version with all core features intact
"""
import sys
import termios
import tty
import time
import random
import os
import json
import shutil
from enum import Enum
from datetime import datetime

class Colors:
    """Terminal colors"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Background colors for special effects
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    
    @classmethod
    def color(cls, text, color):
        return f"{color}{text}{cls.RESET}"
    
    @classmethod
    def rainbow_text(cls, text):
        """Create rainbow effect for special occasions"""
        colors = [cls.RED, cls.YELLOW, cls.GREEN, cls.CYAN, cls.BLUE, cls.MAGENTA]
        result = ""
        for i, char in enumerate(text):
            if char != ' ':
                result += colors[i % len(colors)] + char + cls.RESET
            else:
                result += char
        return result

class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

class TerminalUtils:
    @staticmethod
    def get_terminal_size():
        """Get terminal dimensions"""
        try:
            size = shutil.get_terminal_size()
            return size.columns, size.lines
        except:
            return 80, 24
    
    @staticmethod
    def center_text(text, width=None):
        """Center text in terminal, properly handling ANSI color codes"""
        if width is None:
            width, _ = TerminalUtils.get_terminal_size()
        lines = text.split('\n')
        centered_lines = []
        for line in lines:
            # Remove ANSI color codes for accurate length calculation
            import re
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            padding = max(0, (width - len(clean_line)) // 2)
            # Add padding only to the left, preserving the original line structure
            centered_lines.append(' ' * padding + line)
        return '\n'.join(centered_lines)
    
    @staticmethod
    def center_block(lines, width=None):
        """Center a block of text lines"""
        if width is None:
            width, _ = TerminalUtils.get_terminal_size()
        centered_lines = []
        for line in lines:
            # Remove ANSI color codes for length calculation
            import re
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            padding = max(0, (width - len(clean_line)) // 2)
            centered_lines.append(' ' * padding + line)
        return centered_lines

class SnakeGame:
    def __init__(self, difficulty='medium'):
        # Get terminal dimensions
        self.term_width, self.term_height = TerminalUtils.get_terminal_size()
        
        # Difficulty settings with dynamic sizing
        base_difficulties = {
            'easy': {'base_size': (15, 30), 'speed': 0.15},
            'medium': {'base_size': (20, 40), 'speed': 0.1},
            'hard': {'base_size': (25, 50), 'speed': 0.05}
        }
        
        # Adjust board size to fit terminal
        base_height, base_width = base_difficulties[difficulty]['base_size']
        
        # Calculate maximum board size that fits in terminal
        max_width = min(self.term_width - 10, base_width)  # Leave margin for borders
        max_height = min(self.term_height - 15, base_height)  # Leave space for UI
        
        # Ensure minimum size
        self.width = max(20, max_width)
        self.height = max(10, max_height)
        
        self.base_speed = base_difficulties[difficulty]['speed']
        self.score = 0
        self.running = True
        self.foods_eaten = 0
        self.level = 1
        self.last_score_milestone = 0
        
        # Detect terminal type for better speed compensation
        self.terminal_type = self.detect_terminal_type()
        
        # Universal speed compensation for cross-platform compatibility
        # Most terminals have character aspect ratio between 1.6:1 to 2.2:1 (height:width)
        # Use conservative ratio that works well across different systems
        horizontal_ratio = 0.7  # Make horizontal movement faster
        
        self.speed_ratios = {
            Direction.UP: 1.0,              # Vertical movement (normal speed)
            Direction.DOWN: 1.0,            # Vertical movement (normal speed)
            Direction.LEFT: horizontal_ratio,   # Horizontal movement (compensated)
            Direction.RIGHT: horizontal_ratio   # Horizontal movement (compensated)
        }
        
        # Snake starts in center
        center_y, center_x = self.height // 2, self.width // 2
        self.snake = [(center_y, center_x), (center_y, center_x - 1), (center_y, center_x - 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Generate first food
        self.food = self.generate_food()
        
        # Terminal setup (only if in actual terminal)
        try:
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
            self.terminal_mode = True
        except (termios.error, OSError):
            self.old_settings = None
            self.terminal_mode = False

    def detect_terminal_type(self):
        """Detect terminal type for cross-platform compatibility"""
        term_program = os.environ.get('TERM_PROGRAM', '').lower()
        term = os.environ.get('TERM', '').lower()
        
        if 'iterm' in term_program:
            return 'iterm2'
        elif 'apple_terminal' in term_program:
            return 'terminal'
        elif 'vscode' in term_program:
            return 'vscode'
        elif 'screen' in term or 'tmux' in os.environ.get('TMUX', ''):
            return 'generic'
        else:
            return 'generic'

    def generate_food(self):
        """Generate food with improved positioning - avoid walls and snake body"""
        attempts = 0
        max_attempts = 100
        
        # Define safe zone boundaries (avoid too close to walls)
        wall_margin = 2
        safe_top = wall_margin
        safe_bottom = self.height - wall_margin - 1
        safe_left = wall_margin  
        safe_right = self.width - wall_margin - 1
        
        while attempts < max_attempts:
            # Try to place food in safe zone first
            if attempts < max_attempts // 2:
                food_y = random.randint(safe_top, safe_bottom)
                food_x = random.randint(safe_left, safe_right)
            else:
                # Fallback to original method if safe zone fails
                food_y = random.randint(1, self.height - 2)
                food_x = random.randint(1, self.width - 2)
            
            food_pos = (food_y, food_x)
            
            # Check if position is valid (not in snake and not too close to snake head)
            if food_pos not in self.snake:
                # Additional check: not too close to snake head for better gameplay
                head_y, head_x = self.snake[0]
                distance = abs(food_y - head_y) + abs(food_x - head_x)
                if distance >= 3:  # Manhattan distance of at least 3
                    return food_pos
            
            attempts += 1
        
        # Emergency fallback - just avoid snake body
        while True:
            food_pos = (random.randint(1, self.height - 2), random.randint(1, self.width - 2))
            if food_pos not in self.snake:
                return food_pos

    def get_key_press(self):
        """Non-blocking key input"""
        import select
        if select.select([sys.stdin], [], [], 0.0)[0]:
            return sys.stdin.read(1)
        return None

    def handle_input(self):
        key = self.get_key_press()
        if key:
            if key == '\x1b':  # ESC sequence
                key2 = sys.stdin.read(1)
                if key2 == '[':
                    key3 = sys.stdin.read(1)
                    if key3 == 'A' and self.direction != Direction.DOWN:
                        self.next_direction = Direction.UP
                    elif key3 == 'B' and self.direction != Direction.UP:
                        self.next_direction = Direction.DOWN
                    elif key3 == 'C' and self.direction != Direction.LEFT:
                        self.next_direction = Direction.RIGHT
                    elif key3 == 'D' and self.direction != Direction.RIGHT:
                        self.next_direction = Direction.LEFT
            elif key.lower() == 'q':
                self.running = False

    def move_snake(self):
        self.direction = self.next_direction
        head = self.snake[0]
        dy, dx = self.direction.value
        new_head = (head[0] + dy, head[1] + dx)
        
        # Check wall collision
        if (new_head[0] <= 0 or new_head[0] >= self.height - 1 or 
            new_head[1] <= 0 or new_head[1] >= self.width - 1):
            return False
        
        # Check self collision
        if new_head in self.snake:
            return False
        
        self.snake.insert(0, new_head)
        
        # Check food
        if new_head == self.food:
            self.foods_eaten += 1
            self.score += 10 + (self.level - 1) * 2  # Bonus points for higher levels
            
            # Level up every 5 foods
            if self.foods_eaten % 5 == 0:
                self.level += 1
            
            self.food = self.generate_food()
        else:
            self.snake.pop()
        
        return True

    def get_adjusted_speed(self):
        """Get speed adjusted for current direction to compensate for terminal character ratio"""
        return self.base_speed * self.speed_ratios[self.direction]

    def draw_board(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Create game board lines
        board_lines = []
        
        # Enhanced header with more game info
        score_text = Colors.color(f"Score: {self.score}", Colors.YELLOW + Colors.BOLD)
        level_text = Colors.color(f"Level: {self.level}", Colors.CYAN + Colors.BOLD)
        foods_text = Colors.color(f"Foods: {self.foods_eaten}", Colors.GREEN)
        length_text = Colors.color(f"Length: {len(self.snake)}", Colors.MAGENTA)
        quit_text = Colors.color("Q: Quit", Colors.RED + Colors.DIM)
        
        # Create multi-line header
        header1 = f"| {score_text} | {level_text} | {foods_text} |"
        header2 = f"| {length_text} | {quit_text} |"
        
        board_lines.append(header1)
        board_lines.append(header2)
        board_lines.append("+" + "=" * self.width + "+")
        
        # Game board with enhanced visuals
        for y in range(self.height):
            row = "|"
            for x in range(self.width):
                if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1:
                    # Enhanced wall design
                    if (y == 0 or y == self.height - 1) and (x == 0 or x == self.width - 1):
                        row += Colors.color("+", Colors.WHITE + Colors.BOLD)  # Corners
                    else:
                        row += Colors.color("#", Colors.GRAY)  # Walls
                elif (y, x) == self.snake[0]:  # Enhanced snake head
                    if self.level >= 5:
                        row += Colors.color("@", Colors.GREEN + Colors.BG_GREEN + Colors.BOLD)
                    else:
                        row += Colors.color("@", Colors.GREEN + Colors.BOLD)
                elif (y, x) in self.snake:  # Enhanced snake body
                    snake_index = self.snake.index((y, x))
                    if snake_index < 3:  # First few segments are brighter
                        row += Colors.color("o", Colors.GREEN + Colors.BOLD)
                    else:
                        row += Colors.color("o", Colors.GREEN)
                elif (y, x) == self.food:  # Enhanced food with level-based effects
                    if self.level >= 3:
                        row += Colors.rainbow_text("*")  # Rainbow food at higher levels
                    else:
                        row += Colors.color("*", Colors.RED + Colors.BOLD)
                else:
                    row += " "
            row += "|"
            board_lines.append(row)
        
        # Enhanced footer with tips
        board_lines.append("+" + "=" * self.width + "+")
        
        # Dynamic tips based on game state
        if self.level == 1 and self.foods_eaten == 0:
            tip_text = "TIP: Eat food (*) to grow and score points!"
            tip = Colors.color(tip_text, Colors.CYAN + Colors.DIM)
        elif self.level >= 3:
            tip_text = "AWESOME: Rainbow food gives bonus points!"
            tip = Colors.color(tip_text, Colors.MAGENTA + Colors.DIM)
        elif len(self.snake) > 10:
            tip_text = "CAREFUL: Don't hit your own tail!"
            tip = Colors.color(tip_text, Colors.YELLOW + Colors.DIM)
        else:
            tip_text = "Arrow keys: Move | Q: Quit"
            tip = Colors.color(tip_text, Colors.WHITE + Colors.DIM)
        
        # Center the footer text properly
        tip_padding = max(0, (self.width - 2 - len(tip_text)) // 2)  # -2 for the border characters
        footer = "|" + " " * tip_padding + tip + " " * (self.width - 2 - len(tip_text) - tip_padding) + "|"
        board_lines.append(footer)
        
        # Add vertical centering
        vertical_padding = max(0, (self.term_height - len(board_lines)) // 2 - 2)
        for _ in range(vertical_padding):
            print()
        
        # Center and print each line
        for line in board_lines:
            centered_line = TerminalUtils.center_text(line, self.term_width)
            print(centered_line)

    def game_over(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Enhanced game over screen with stats
        box_width = 50
        
        # Create game over title with effects
        if self.score >= 100:
            title_text = "GAME OVER!"
            title = Colors.rainbow_text(title_text)
        else:
            title_text = "GAME OVER!"
            title = Colors.color(title_text, Colors.RED + Colors.BOLD)
        
        # Performance evaluation
        if self.score >= 200:
            perf_text = "INCREDIBLE SCORE!"
            performance = Colors.color(perf_text, Colors.YELLOW + Colors.BOLD)
        elif self.score >= 100:
            perf_text = "Great job!"
            performance = Colors.color(perf_text, Colors.GREEN + Colors.BOLD)
        elif self.score >= 50:
            perf_text = "Not bad!"
            performance = Colors.color(perf_text, Colors.CYAN)
        else:
            perf_text = "Keep practicing!"
            performance = Colors.color(perf_text, Colors.BLUE)
        
        # Create all text lines first
        stats = [
            f"Final Score: {self.score} points",
            f"Level Reached: {self.level}",
            f"Foods Eaten: {self.foods_eaten}",
            f"Snake Length: {len(self.snake)}"
        ]
        
        restart_text = "Press 'y' to play again, 'n' to quit"
        
        # Build the box with proper centering
        game_over_lines = []
        
        # Top border
        game_over_lines.append("+" + "=" * box_width + "+")
        
        # Title line with proper centering
        title_padding = (box_width - len(title_text)) // 2
        title_line = "|" + " " * title_padding + title + " " * (box_width - len(title_text) - title_padding) + "|"
        game_over_lines.append(title_line)
        
        # Separator
        game_over_lines.append("+" + "-" * box_width + "+")
        
        # Empty line
        game_over_lines.append("|" + " " * box_width + "|")
        
        # Stats lines
        for stat in stats:
            game_over_lines.append("|" + stat.center(box_width) + "|")
        
        # Empty line
        game_over_lines.append("|" + " " * box_width + "|")
        
        # Performance line with proper centering
        perf_padding = (box_width - len(perf_text)) // 2
        perf_line = "|" + " " * perf_padding + performance + " " * (box_width - len(perf_text) - perf_padding) + "|"
        game_over_lines.append(perf_line)
        
        # Empty line
        game_over_lines.append("|" + " " * box_width + "|")
        
        # Restart instruction
        game_over_lines.append("|" + restart_text.center(box_width) + "|")
        
        # Bottom border
        game_over_lines.append("+" + "=" * box_width + "+")
        
        # Add vertical centering
        vertical_padding = max(0, (self.term_height - len(game_over_lines)) // 2)
        for _ in range(vertical_padding):
            print()
        
        # Center and print each line
        for line in game_over_lines:
            centered_line = TerminalUtils.center_text(line, self.term_width)
            print(centered_line)

    def cleanup(self):
        if self.old_settings is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def run(self):
        try:
            while self.running:
                self.draw_board()
                self.handle_input()
                
                if not self.move_snake():
                    break
                
                # Use direction-adjusted speed
                adjusted_speed = self.get_adjusted_speed()
                time.sleep(adjusted_speed)
            
            self.game_over()
            
        finally:
            self.cleanup()

def show_logo():
    term_width, term_height = TerminalUtils.get_terminal_size()
    
    logo_text = """
+===============================================+
|                 SNAKE GAME                    |
|              Terminal Edition                 |
+===============================================+
|                                               |
|  [@] Snake Head    [o] Snake Body             |
|  [*] Food          [#] Wall                   |
|                                               |
|  Arrow Keys: Move  |  Q: Quit                 |
+===============================================+
"""
    
    # Center the logo
    centered_logo = TerminalUtils.center_text(logo_text, term_width)
    
    # Add vertical centering
    logo_lines = logo_text.strip().split('\n')
    vertical_padding = max(0, (term_height - len(logo_lines)) // 2 - 3)
    
    os.system('clear' if os.name == 'posix' else 'cls')
    for _ in range(vertical_padding):
        print()
    
    print(centered_logo)

def select_difficulty():
    while True:
        term_width, term_height = TerminalUtils.get_terminal_size()
        os.system('clear' if os.name == 'posix' else 'cls')
        show_logo()
        
        # Create difficulty menu
        menu_lines = [
            "",
            "Select Difficulty:",
            "1. Easy   (Dynamic size, Slow)",
            "2. Medium (Dynamic size, Normal)",  
            "3. Hard   (Dynamic size, Fast)",
            "4. Quit",
            "",
            "Choice (1-4): "
        ]
        
        # Center the menu
        for line in menu_lines[:-1]:  # All except the input prompt
            centered_line = TerminalUtils.center_text(line, term_width)
            print(centered_line)
        
        # Center the input prompt
        prompt_line = menu_lines[-1]
        prompt_padding = (term_width - len(prompt_line)) // 2
        choice = input(' ' * prompt_padding + prompt_line).strip()
        
        if choice == '1':
            return 'easy'
        elif choice == '2':
            return 'medium'
        elif choice == '3':
            return 'hard'
        elif choice == '4':
            return None
        else:
            error_msg = "Invalid choice! Press Enter to try again..."
            centered_error = TerminalUtils.center_text(error_msg, term_width)
            print(centered_error)
            input()

def main():
    """Main game loop"""
    try:
        while True:
            difficulty = select_difficulty()
            if not difficulty:
                break
                
            game = SnakeGame(difficulty)
            game.run()
            
            # Ask for restart with centered text
            term_width, _ = TerminalUtils.get_terminal_size()
            while True:
                prompt = "Play again? (y/n): "
                prompt_padding = (term_width - len(prompt)) // 2
                restart = input(' ' * prompt_padding + prompt).strip().lower()
                if restart in ['y', 'yes']:
                    break
                elif restart in ['n', 'no']:
                    thanks_msg = "Thanks for playing!"
                    centered_thanks = TerminalUtils.center_text(thanks_msg, term_width)
                    print(centered_thanks)
                    return
                else:
                    error_msg = "Please enter 'y' or 'n'"
                    centered_error = TerminalUtils.center_text(error_msg, term_width)
                    print(centered_error)
                    
    except KeyboardInterrupt:
        term_width, _ = TerminalUtils.get_terminal_size()
        thanks_msg = "\nThanks for playing!"
        centered_thanks = TerminalUtils.center_text(thanks_msg, term_width)
        print(centered_thanks)
    except Exception as e:
        term_width, _ = TerminalUtils.get_terminal_size()
        error_msg = f"An error occurred: {e}"
        centered_error = TerminalUtils.center_text(error_msg, term_width)
        print(centered_error)

if __name__ == "__main__":
    main()