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

class SnakeGame:
    def __init__(self, difficulty='medium'):
        # Difficulty settings
        self.difficulties = {
            'easy': {'size': (15, 30), 'speed': 0.15},
            'medium': {'size': (20, 40), 'speed': 0.1},
            'hard': {'size': (25, 50), 'speed': 0.05}
        }
        
        self.difficulty = self.difficulties[difficulty]
        self.height, self.width = self.difficulty['size']
        self.speed = self.difficulty['speed']
        self.score = 0
        self.running = True
        
        # Snake starts in center
        center_y, center_x = self.height // 2, self.width // 2
        self.snake = [(center_y, center_x), (center_y, center_x - 1), (center_y, center_x - 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Generate first food
        self.food = self.generate_food()
        
        # Terminal setup
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

    def draw_board(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Header
        score_text = Colors.color(f"Score: {self.score}", Colors.YELLOW + Colors.BOLD)
        quit_text = Colors.color("Quit: Q", Colors.RED)
        print(f"| {score_text} | {quit_text} |")
        print("+" + "=" * self.width + "+")
        
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
            print(row)
        
        # Footer
        print("+" + "=" * self.width + "+")
        print("| Arrow keys: Move | Q: Quit |")

    def game_over(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print("+" + "=" * 40 + "+")
        print("|" + "GAME OVER!".center(40) + "|")
        print("+" + "-" * 40 + "+")
        print("|" + f"Final Score: {self.score} points".center(40) + "|")
        print("|" + " " * 40 + "|")
        print("|" + "Press 'y' to play again, 'n' to quit".center(40) + "|")
        print("+" + "=" * 40 + "+")

    def cleanup(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def run(self):
        try:
            while self.running:
                self.draw_board()
                self.handle_input()
                
                if not self.move_snake():
                    break
                
                time.sleep(self.speed)
            
            self.game_over()
            
        finally:
            self.cleanup()

def show_logo():
    print("""
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
""")

def select_difficulty():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        show_logo()
        print("\nSelect Difficulty:")
        print("1. Easy   (15x30, Slow)")
        print("2. Medium (20x40, Normal)")  
        print("3. Hard   (25x50, Fast)")
        print("4. Quit")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == '1':
            return 'easy'
        elif choice == '2':
            return 'medium'
        elif choice == '3':
            return 'hard'
        elif choice == '4':
            return None
        else:
            print("Invalid choice! Press Enter to try again...")
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
            
            # Ask for restart
            while True:
                restart = input("Play again? (y/n): ").strip().lower()
                if restart in ['y', 'yes']:
                    break
                elif restart in ['n', 'no']:
                    print("Thanks for playing!")
                    return
                else:
                    print("Please enter 'y' or 'n'")
                    
    except KeyboardInterrupt:
        print("\nThanks for playing!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()