#!/usr/bin/env python3
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

class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

class TerminalAdapter:
    """Class for detecting and automatically adjusting terminal environment"""
    
    def __init__(self):
        self.terminal_width, self.terminal_height = self.get_terminal_size()
        self.terminal_type = self.detect_terminal_type()
        self.char_ratio = self.detect_character_ratio()
    
    def get_terminal_size(self):
        """Detect terminal size"""
        try:
            size = shutil.get_terminal_size()
            return size.columns, size.lines
        except:
            return 80, 24  # Default value
    
    def detect_terminal_type(self):
        """Detect terminal type"""
        term_program = os.environ.get('TERM_PROGRAM', '')
        term = os.environ.get('TERM', '')
        
        if 'iTerm' in term_program:
            return 'iterm2'
        elif 'Apple_Terminal' in term_program:
            return 'terminal'
        elif 'vscode' in term_program.lower():
            return 'vscode'
        elif 'hyper' in term_program.lower():
            return 'hyper'
        elif term.startswith('screen'):
            return 'screen'
        elif 'tmux' in os.environ.get('TMUX', ''):
            return 'tmux'
        else:
            return 'generic'
    
    def detect_character_ratio(self):
        """Detect character ratio for each terminal type"""
        ratios = {
            'iterm2': 1.8,      # iTerm2 typically uses 1.8:1 ratio
            'terminal': 2.0,    # macOS Terminal uses 2:1 ratio
            'vscode': 1.6,      # VS Code integrated terminal
            'hyper': 1.7,       # Hyper terminal
            'screen': 2.0,      # Screen session
            'tmux': 2.0,        # Tmux session
            'generic': 1.8      # Default value
        }
        return ratios.get(self.terminal_type, 1.8)
    
    def get_optimal_board_size(self, base_height, base_width):
        """Calculate optimal board size for terminal"""
        # Adjust based on terminal size
        max_width = min(self.terminal_width - 4, base_width)  # Consider margins
        max_height = min(self.terminal_height - 10, base_height)  # Consider UI space
        
        # Adjust width based on character ratio
        adjusted_width = int(base_height * self.char_ratio * 0.8)  # 0.8 is correction factor
        
        # Determine final size
        final_width = min(max_width, adjusted_width)
        final_height = min(max_height, base_height)
        
        return (final_height, final_width)
    
    def get_speed_adjustment(self, direction):
        """Speed adjustment for each terminal type"""
        # Base adjustment values by terminal type
        base_adjustments = {
            'iterm2': {'vertical': 1.1, 'horizontal': 0.9},
            'terminal': {'vertical': 1.2, 'horizontal': 0.85},
            'vscode': {'vertical': 1.05, 'horizontal': 0.95},
            'hyper': {'vertical': 1.1, 'horizontal': 0.9},
            'generic': {'vertical': 1.1, 'horizontal': 0.9}
        }
        
        adjustment = base_adjustments.get(self.terminal_type, base_adjustments['generic'])
        
        if direction in [Direction.UP, Direction.DOWN]:
            return adjustment['vertical']
        else:
            return adjustment['horizontal']

class Difficulty:
    """Difficulty settings - used with terminal adapter"""
    
    @staticmethod
    def get_difficulty_settings(adapter=None):
        if adapter is None:
            adapter = TerminalAdapter()
            
        # Base settings
        base_settings = {
            'EASY': {"name": "Easy", "speed": 0.2, "base_board_size": (15, 25)},
            'MEDIUM': {"name": "Medium", "speed": 0.1, "base_board_size": (20, 35)},
            'HARD': {"name": "Hard", "speed": 0.05, "base_board_size": (25, 45)}
        }
        
        # Adjust for terminal
        for key, settings in base_settings.items():
            base_height, base_width = settings['base_board_size']
            optimized_size = adapter.get_optimal_board_size(base_height, base_width)
            settings['board_size'] = optimized_size
        
        return base_settings
    
    # Static properties for compatibility
    @staticmethod
    def get_easy():
        return Difficulty.get_difficulty_settings()['EASY']
    
    @staticmethod  
    def get_medium():
        return Difficulty.get_difficulty_settings()['MEDIUM']
    
    @staticmethod
    def get_hard():
        return Difficulty.get_difficulty_settings()['HARD']
    
    # Maintained for existing code compatibility
    EASY = {"name": "Easy", "speed": 0.2, "board_size": (15, 25)}
    MEDIUM = {"name": "Medium", "speed": 0.1, "board_size": (20, 35)}
    HARD = {"name": "Hard", "speed": 0.05, "board_size": (25, 45)}

class UIBox:
    """Text box creation and management class"""
    
    @staticmethod
    def get_text_width(text):
        """Calculate actual display width of text (considering emojis and Korean)"""
        width = 0
        i = 0
        while i < len(text):
            char = text[i]
            if ord(char) > 127:  # Non-ASCII characters (Korean, emojis, etc.)
                # Emojis and Korean characters typically take 2 columns
                if ord(char) >= 0x1F600:  # Emoji range
                    width += 2
                elif ord(char) >= 0xAC00:  # Korean range
                    width += 2
                else:
                    width += 2  # Other Unicode characters
            else:
                width += 1
            i += 1
        return width
    
    @staticmethod
    def pad_text(text, target_width, align='left'):
        """Pad text to specified width"""
        current_width = UIBox.get_text_width(text)
        padding_needed = target_width - current_width
        
        if padding_needed <= 0:
            return text[:target_width]
        
        if align == 'center':
            left_pad = padding_needed // 2
            right_pad = padding_needed - left_pad
            return ' ' * left_pad + text + ' ' * right_pad
        elif align == 'right':
            return ' ' * padding_needed + text
        else:  # left
            return text + ' ' * padding_needed
    
    @staticmethod
    def create_box(title, content_lines, width=65):
        """Create dynamic box"""
        box_lines = []
        inner_width = width - 2  # Exclude left and right borders
        
        # Top border
        box_lines.append("+" + "-" * width + "+")
        
        # Title
        if title:
            title_line = UIBox.pad_text(title, inner_width, 'center')
            box_lines.append("|" + title_line + "|")
            box_lines.append("+" + "-" * width + "+")
        
        # Content
        box_lines.append("|" + " " * inner_width + "|")
        
        for line in content_lines:
            if isinstance(line, dict):  # Special formatting
                if line.get('type') == 'separator':
                    box_lines.append("|" + " " * inner_width + "|")
                elif line.get('type') == 'menu_item':
                    prefix = line.get('prefix', '')
                    text = line.get('text', '')
                    selected = line.get('selected', False)
                    
                    if selected:
                        formatted_line = f"> {prefix}{text}"
                    else:
                        formatted_line = f"  {prefix}{text}"
                    
                    padded_line = UIBox.pad_text(formatted_line, inner_width)
                    box_lines.append("|" + padded_line + "|")
            else:
                # Regular text
                if len(line.strip()) == 0:
                    box_lines.append("|" + " " * inner_width + "|")
                else:
                    padded_line = UIBox.pad_text(f"  {line}", inner_width)
                    box_lines.append("|" + padded_line + "|")
        
        # Bottom margin and border
        box_lines.append("|" + " " * inner_width + "|")
        box_lines.append("+" + "-" * width + "+")
        
        return '\n'.join(box_lines)

class ScoreManager:
    """Score management class"""
    
    def __init__(self):
        self.scores_file = os.path.expanduser("~/.snake_game_scores.json")
        self.scores = self.load_scores()
    
    def load_scores(self):
        """Load saved scores"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def save_scores(self):
        """Save scores"""
        try:
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error occurred while saving scores: {e}")
    
    def add_score(self, score, difficulty_name):
        """Add new score"""
        score_entry = {
            'score': score,
            'difficulty': difficulty_name,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        self.scores.append(score_entry)
        
        # Sort by score (descending)
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Keep only top 10
        self.scores = self.scores[:10]
        
        self.save_scores()
    
    def get_top_scores(self, limit=5):
        """Return top scores"""
        return self.scores[:limit]
    
    def is_new_high_score(self, score):
        """Check if this is a new high score"""
        if not self.scores:
            return True
        return score > self.scores[0]['score']

class SnakeGame:
    def __init__(self, difficulty, terminal_adapter=None):
        self.difficulty = difficulty
        self.terminal_adapter = terminal_adapter or TerminalAdapter()
        
        # Use terminal-optimized board size
        if 'base_board_size' in difficulty:
            base_height, base_width = difficulty['base_board_size']
            self.height, self.width = self.terminal_adapter.get_optimal_board_size(base_height, base_width)
        else:
            self.height, self.width = difficulty["board_size"]
            
        self.speed = difficulty["speed"]
        self.score = 0
        self.running = True
        
        # Snake initial position (center)
        center_y, center_x = self.height // 2, self.width // 2
        self.snake = [(center_y, center_x), (center_y, center_x - 1), (center_y, center_x - 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Generate food
        self.food = self.generate_food()
        
        # Terminal settings
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

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

def get_menu_input():
    """Function to handle arrow key input in menus"""
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        
        while True:
            key = sys.stdin.read(1)
            
            if key == '\x1b':  # ESC sequence start
                key2 = sys.stdin.read(1)
                if key2 == '[':
                    key3 = sys.stdin.read(1)
                    if key3 == 'A':  # Up arrow
                        return 'UP'
                    elif key3 == 'B':  # Down arrow
                        return 'DOWN'
                    elif key3 == 'C':  # Right arrow
                        return 'RIGHT'
                    elif key3 == 'D':  # Left arrow
                        return 'LEFT'
            elif key == '\r' or key == '\n':  # Enter
                return 'ENTER'
            elif key in ['q', 'Q']:  # Quit
                return 'QUIT'
            elif key.isdigit():  # Number keys (existing compatibility)
                return key
            
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def handle_input(self):
        key = self.get_key_press()
        if key:
            if key == '\x1b':  # ESC sequence start
                key2 = sys.stdin.read(1)
                if key2 == '[':
                    key3 = sys.stdin.read(1)
                    if key3 == 'A' and self.direction != Direction.DOWN:  # Up
                        self.next_direction = Direction.UP
                    elif key3 == 'B' and self.direction != Direction.UP:  # Down
                        self.next_direction = Direction.DOWN
                    elif key3 == 'C' and self.direction != Direction.LEFT:  # Right
                        self.next_direction = Direction.RIGHT
                    elif key3 == 'D' and self.direction != Direction.RIGHT:  # Left
                        self.next_direction = Direction.LEFT
            elif key in ['q', 'Q']:
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
        
        # Check self-collision
        if new_head in self.snake:
            return False
        
        self.snake.insert(0, new_head)
        
        # Check if food was eaten
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
        else:
            self.snake.pop()
        
        return True

    def draw_board(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print(f"Score: {self.score} | Difficulty: {self.difficulty['name']} | Quit: Q")
        print("=" * (self.width + 2))
        
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1:
                    row += "#"
                elif (y, x) == self.snake[0]:  # head
                    row += "@"
                elif (y, x) in self.snake:  # body
                    row += "o"
                elif (y, x) == self.food:  # food
                    row += "*"
                else:
                    row += " "
            print(row)
        
        print("=" * (self.width + 2))
        print("Arrow keys to move, Q to quit")

    def game_over(self, score_manager):
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Check if it's a new high score (before saving)
        is_high_score = score_manager.is_new_high_score(self.score)
        
        # Save score
        score_manager.add_score(self.score, self.difficulty['name'])
        
        content = [
            "GAME OVER!",
            {"type": "separator"},
            f"Final Score: {self.score} points",
            f"Difficulty: {self.difficulty['name']}",
            {"type": "separator"}
        ]
        
        if is_high_score and self.score > 0:
            content.extend([
                "*** NEW HIGH SCORE! ***",
                {"type": "separator"}
            ])
        
        content.extend([
            "Press 'y' to restart, 'n' to return to menu"
        ])
        
        box = UIBox.create_box("", content)
        print(box)

    def cleanup(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_adjusted_speed(self):
        """Speed adjustment according to terminal environment"""
        base_speed = self.speed
        
        # Precise speed adjustment through TerminalAdapter
        adjustment = self.terminal_adapter.get_speed_adjustment(self.direction)
        return base_speed * adjustment
    
    def run(self, score_manager=None):
        if score_manager is None:
            score_manager = ScoreManager()
            
        try:
            while self.running:
                self.draw_board()
                self.handle_input()
                
                if not self.move_snake():
                    break
                
                # Use adjusted speed based on direction
                adjusted_speed = self.get_adjusted_speed()
                time.sleep(adjusted_speed)
            
            self.game_over(score_manager)
            
        finally:
            self.cleanup()

def show_logo():
    """Display game logo screen"""
    os.system('clear' if os.name == 'posix' else 'cls')
    logo = """
    +---------------------------------------------------------------+
    |                                                               |
    |    #######  ###    ##  #####  ##   ## #######     ######     |
    |    ##       ####   ## ##   ## ##  ##  ##         ##         |
    |    #######  ## ##  ## #######  #####   #####      ##   ###   |
    |         ##  ##  ## ## ##   ## ##  ##  ##         ##    ##   |
    |    #######  ##   #### ##   ## ##   ## #######     ######    |
    |                                                               |
    |                       CLASSIC SNAKE GAME                     |
    |                                                               |
    |                  Retro Arcade Game for Terminal               |
    |                                                               |
    +---------------------------------------------------------------+
    """
    print(logo)
    print("\n" + "-" * 67)
    print("                     Press any key to start...")
    print("-" * 67)
    
    # Wait for key input
    try:
        input()
    except KeyboardInterrupt:
        sys.exit(0)

def show_main_menu(selected_index=0):
    """Main menu screen"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    menu_items = [
        {"type": "menu_item", "prefix": "[1] ", "text": "Start Game", "selected": selected_index == 0},
        {"type": "menu_item", "prefix": "[2] ", "text": "How to Play", "selected": selected_index == 1},
        {"type": "menu_item", "prefix": "[3] ", "text": "Difficulty", "selected": selected_index == 2},
        {"type": "menu_item", "prefix": "[4] ", "text": "High Scores", "selected": selected_index == 3},
        {"type": "menu_item", "prefix": "[5] ", "text": "Exit Game", "selected": selected_index == 4}
    ]
    
    content = menu_items + [
        {"type": "separator"},
        "Use arrow keys to navigate, Enter to select, Q to quit"
    ]
    
    box = UIBox.create_box("MAIN MENU", content)
    print(box)

def show_how_to_play():
    """Game instructions"""
    os.system('clear' if os.name == 'posix' else 'cls')
    instructions = """
+---------------------------------------------------------------+
|                          HOW TO PLAY                          |
+---------------------------------------------------------------+
|                                                               |
|  CONTROLS:                                                    |
|     ^ v < >  Use arrow keys to control the snake              |
|     Q        Quit the game                                    |
|                                                               |
|  OBJECTIVE:                                                   |
|     @ Snake head (@)                                          |
|     o Snake body (o)                                          |
|     * Food (*) - eat to grow and increase score               |
|                                                               |
|  RULES:                                                       |
|     - Game ends if you hit the walls                          |
|     - Game ends if you hit your own body                      |
|     - Each food gives you 10 points                           |
|                                                               |
|  GOAL: Eat as much food as possible to achieve high score!    |
|                                                               |
+---------------------------------------------------------------+
"""
    print(instructions)
    print("\nPress any key to return to main menu...")
    input()

def show_difficulty_menu(selected_index=0, terminal_adapter=None):
    """Difficulty selection menu"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    if terminal_adapter is None:
        terminal_adapter = TerminalAdapter()
    
    difficulty_settings = Difficulty.get_difficulty_settings(terminal_adapter)
    
    difficulty_items = [
        {"name": "[1] Easy", "details": [
            f"Board size: {difficulty_settings['EASY']['board_size'][0]} x {difficulty_settings['EASY']['board_size'][1]}", 
            "Speed: Slow (For beginners)", 
            "Recommended for: First-time players"
        ]},
        {"name": "[2] Medium", "details": [
            f"Board size: {difficulty_settings['MEDIUM']['board_size'][0]} x {difficulty_settings['MEDIUM']['board_size'][1]}", 
            "Speed: Normal (For regular players)", 
            "Recommended for: Players with basic experience"
        ]},
        {"name": "[3] Hard", "details": [
            f"Board size: {difficulty_settings['HARD']['board_size'][0]} x {difficulty_settings['HARD']['board_size'][1]}", 
            "Speed: Fast (For experts)", 
            "Recommended for: Challenge seekers"
        ]},
        {"name": "[4] Back to Main Menu", "details": []}
    ]
    
    print("+---------------------------------------------------------------+")
    print("|                      SELECT DIFFICULTY                        |")
    print("+---------------------------------------------------------------+")
    print("|                                                               |")
    
    for i, item in enumerate(difficulty_items):
        if i == selected_index:
            print(f"|  > {item['name']}                                          |"[:67] + "|")
        else:
            print(f"|    {item['name']}                                          |"[:67] + "|")
            
        if item['details']:
            for detail in item['details']:
                print(f"|      - {detail}                                   |"[:67] + "|")
            print("|                                                               |")
    
    print("+---------------------------------------------------------------+")
    print("\nUse arrow keys to select, Enter to confirm, Q to go back")

def show_high_scores():
    """Display high scores"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    score_manager = ScoreManager()
    top_scores = score_manager.get_top_scores(10)
    
    content = []
    
    if not top_scores:
        content.extend([
            "No scores recorded yet.",
            {"type": "separator"},
            "Start your first game to set a record!"
        ])
    else:
        content.append("RANK   DIFFICULTY   SCORE     DATE")
        content.append("-" * 50)
        
        for i, score_entry in enumerate(top_scores):
            rank = f"#{i+1}".ljust(6)
            difficulty = score_entry['difficulty'].ljust(12)
            score = f"{score_entry['score']} pts".ljust(10)
            date = score_entry['date']
                
            score_line = f"{rank} {difficulty} {score} {date}"
            content.append(score_line)
    
    content.extend([
        {"type": "separator"},
        "TIPS FOR HIGH SCORES:",
        "- Move carefully near walls",
        "- Keep open space to avoid trapping yourself", 
        "- Plan your path to food efficiently",
        {"type": "separator"},
        "Press any key to return to main menu..."
    ])
    
    box = UIBox.create_box("HIGH SCORES", content)
    print(box)
    input()

def select_difficulty(terminal_adapter=None):
    """Difficulty selection function"""
    selected_index = 0
    max_index = 3  # 4 options (0-3)
    
    while True:
        show_difficulty_menu(selected_index, terminal_adapter)
        
        try:
            key = get_menu_input()
            
            if key == 'UP':
                selected_index = (selected_index - 1) % (max_index + 1)
            elif key == 'DOWN':
                selected_index = (selected_index + 1) % (max_index + 1)
            elif key == 'ENTER':
                if selected_index == 0:
                    return 'EASY'
                elif selected_index == 1:
                    return 'MEDIUM'
                elif selected_index == 2:
                    return 'HARD'
                elif selected_index == 3:
                    return None  # Return to main menu
            elif key == 'QUIT' or key == 'q':
                return None
            elif key in ['1', '2', '3', '4']:  # Existing number key support
                choice = int(key)
                if choice == 1:
                    return 'EASY'
                elif choice == 2:
                    return 'MEDIUM'
                elif choice == 3:
                    return 'HARD'
                elif choice == 4:
                    return None
                
        except KeyboardInterrupt:
            return None

def main():
    # Initialize terminal adapter
    terminal_adapter = TerminalAdapter()
    
    # Display logo
    show_logo()
    
    # Terminal-optimized difficulty settings
    difficulty_settings = Difficulty.get_difficulty_settings(terminal_adapter)
    current_difficulty = difficulty_settings['MEDIUM']
    score_manager = ScoreManager()
    selected_index = 0
    max_index = 4  # 5 menu items (0-4)
    
    # Display terminal info (debug - first run only)
    print(f"Terminal: {terminal_adapter.terminal_type} ({terminal_adapter.terminal_width}x{terminal_adapter.terminal_height})")
    print(f"Character ratio: {terminal_adapter.char_ratio:.1f}:1")
    print(f"Optimized board: {current_difficulty['board_size']}")
    print("\nPress any key to continue...")
    input()
    
    while True:
        show_main_menu(selected_index)
        
        try:
            key = get_menu_input()
            
            if key == 'UP':
                selected_index = (selected_index - 1) % (max_index + 1)
            elif key == 'DOWN':
                selected_index = (selected_index + 1) % (max_index + 1)
            elif key == 'ENTER':
                if selected_index == 0:  # Start game
                    game = SnakeGame(current_difficulty, terminal_adapter)
                    game.run(score_manager)
                    
                    # Check restart after game ends
                    while True:
                        restart = input().strip().lower()
                        if restart in ['y', 'yes', 'ㅛ']:
                            game = SnakeGame(current_difficulty, terminal_adapter)
                            game.run(score_manager)
                        elif restart in ['n', 'no', 'ㅜ']:
                            break
                        else:
                            print("Please enter y or n.")
                            
                elif selected_index == 1:  # How to play
                    show_how_to_play()
                    
                elif selected_index == 2:  # Difficulty settings
                    selected_difficulty_key = select_difficulty(terminal_adapter)
                    if selected_difficulty_key:
                        current_difficulty = difficulty_settings[selected_difficulty_key]
                        os.system('clear' if os.name == 'posix' else 'cls')
                        print(f"Difficulty set to '{current_difficulty['name']}'!")
                        print(f"Board size: {current_difficulty['board_size']}")
                        print("Press any key to continue...")
                        input()
                        
                elif selected_index == 3:  # High scores
                    show_high_scores()
                    
                elif selected_index == 4:  # Exit game
                    os.system('clear' if os.name == 'posix' else 'cls')
                    print("+---------------------------------------------------------------+")
                    print("|                          Exiting game                         |")
                    print("|                                                               |")
                    print("|                   Thanks for playing Snake!                   |")
                    print("|                                                               |")
                    print("+---------------------------------------------------------------+")
                    break
                    
            elif key == 'QUIT':  # Direct exit with Q key
                os.system('clear' if os.name == 'posix' else 'cls')
                print("+---------------------------------------------------------------+")
                print("|                          Exiting game                         |")
                print("|                                                               |")
                print("|                   Thanks for playing Snake!                   |")
                print("|                                                               |")
                print("+---------------------------------------------------------------+")
                break
                
            elif key in ['1', '2', '3', '4', '5']:  # Existing number key support
                choice = int(key)
                if choice == 1:  # Start game
                    game = SnakeGame(current_difficulty, terminal_adapter)
                    game.run(score_manager)
                    
                    # Check restart after game ends
                    while True:
                        restart = input().strip().lower()
                        if restart in ['y', 'yes', 'ㅛ']:
                            game = SnakeGame(current_difficulty, terminal_adapter)
                            game.run(score_manager)
                        elif restart in ['n', 'no', 'ㅜ']:
                            break
                        else:
                            print("Please enter y or n.")
                            
                elif choice == 2:  # How to play
                    show_how_to_play()
                    
                elif choice == 3:  # Difficulty settings
                    selected_difficulty_key = select_difficulty(terminal_adapter)
                    if selected_difficulty_key:
                        current_difficulty = difficulty_settings[selected_difficulty_key]
                        os.system('clear' if os.name == 'posix' else 'cls')
                        print(f"Difficulty set to '{current_difficulty['name']}'!")
                        print(f"Board size: {current_difficulty['board_size']}")
                        print("Press any key to continue...")
                        input()
                        
                elif choice == 4:  # High scores
                    show_high_scores()
                    
                elif choice == 5:  # Exit game
                    os.system('clear' if os.name == 'posix' else 'cls')
                    print("+---------------------------------------------------------------+")
                    print("|                          Exiting game                         |")
                    print("|                                                               |")
                    print("|                   Thanks for playing Snake!                   |")
                    print("|                                                               |")
                    print("+---------------------------------------------------------------+")
                    break
            
        except KeyboardInterrupt:
            print("\nExiting game.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()