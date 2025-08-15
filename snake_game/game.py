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
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    @classmethod
    def color(cls, text, color):
        return f"{color}{text}{cls.RESET}"

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
        """Center text in terminal"""
        if width is None:
            width, _ = TerminalUtils.get_terminal_size()
        lines = text.split('\n')
        centered_lines = []
        for line in lines:
            # Remove ANSI color codes for length calculation
            import re
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            padding = max(0, (width - len(clean_line)) // 2)
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
            self.score += 10
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
        
        # Header
        score_text = Colors.color(f"Score: {self.score}", Colors.YELLOW + Colors.BOLD)
        quit_text = Colors.color("Quit: Q", Colors.RED)
        header = f"| {score_text} | {quit_text} |"
        board_lines.append(header)
        board_lines.append("+" + "=" * self.width + "+")
        
        # Game board
        for y in range(self.height):
            row = "|"
            for x in range(self.width):
                if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1:
                    row += Colors.color("#", Colors.WHITE)
                elif (y, x) == self.snake[0]:  # head
                    row += Colors.color("@", Colors.GREEN + Colors.BOLD)
                elif (y, x) in self.snake:  # body
                    row += Colors.color("o", Colors.GREEN)
                elif (y, x) == self.food:  # food
                    row += Colors.color("*", Colors.RED + Colors.BOLD)
                else:
                    row += " "
            row += "|"
            board_lines.append(row)
        
        # Footer
        board_lines.append("+" + "=" * self.width + "+")
        footer = "| Arrow keys: Move | Q: Quit |"
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
        
        # Create game over screen
        game_over_lines = [
            "+" + "=" * 40 + "+",
            "|" + "GAME OVER!".center(40) + "|",
            "+" + "-" * 40 + "+",
            "|" + f"Final Score: {self.score} points".center(40) + "|",
            "|" + " " * 40 + "|",
            "|" + "Press 'y' to play again, 'n' to quit".center(40) + "|",
            "+" + "=" * 40 + "+"
        ]
        
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