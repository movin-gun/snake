#!/usr/bin/env python3
import sys
import termios
import tty
import time
import random
import os
from enum import Enum

class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

class Difficulty:
    EASY = {"name": "쉬움", "speed": 0.2, "board_size": (15, 30)}
    MEDIUM = {"name": "보통", "speed": 0.1, "board_size": (20, 40)}
    HARD = {"name": "어려움", "speed": 0.05, "board_size": (25, 50)}

class SnakeGame:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.height, self.width = difficulty["board_size"]
        self.speed = difficulty["speed"]
        self.score = 0
        self.running = True
        
        # 스네이크 초기 위치 (중앙)
        center_y, center_x = self.height // 2, self.width // 2
        self.snake = [(center_y, center_x), (center_y, center_x - 1), (center_y, center_x - 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # 음식 생성
        self.food = self.generate_food()
        
        # 터미널 설정
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    def generate_food(self):
        while True:
            food_pos = (random.randint(1, self.height - 2), random.randint(1, self.width - 2))
            if food_pos not in self.snake:
                return food_pos

    def get_key_press(self):
        """논블로킹 키 입력"""
        import select
        if select.select([sys.stdin], [], [], 0.0)[0]:
            return sys.stdin.read(1)
        return None

    def handle_input(self):
        key = self.get_key_press()
        if key:
            if key == '\x1b':  # ESC 시퀀스 시작
                key2 = sys.stdin.read(1)
                if key2 == '[':
                    key3 = sys.stdin.read(1)
                    if key3 == 'A' and self.direction != Direction.DOWN:  # 위쪽
                        self.next_direction = Direction.UP
                    elif key3 == 'B' and self.direction != Direction.UP:  # 아래쪽
                        self.next_direction = Direction.DOWN
                    elif key3 == 'C' and self.direction != Direction.LEFT:  # 오른쪽
                        self.next_direction = Direction.RIGHT
                    elif key3 == 'D' and self.direction != Direction.RIGHT:  # 왼쪽
                        self.next_direction = Direction.LEFT
            elif key in ['q', 'Q']:
                self.running = False

    def move_snake(self):
        self.direction = self.next_direction
        head = self.snake[0]
        dy, dx = self.direction.value
        new_head = (head[0] + dy, head[1] + dx)
        
        # 벽 충돌 체크
        if (new_head[0] <= 0 or new_head[0] >= self.height - 1 or 
            new_head[1] <= 0 or new_head[1] >= self.width - 1):
            return False
        
        # 자기 자신과 충돌 체크
        if new_head in self.snake:
            return False
        
        self.snake.insert(0, new_head)
        
        # 음식 먹었는지 체크
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
        else:
            self.snake.pop()
        
        return True

    def draw_board(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print(f"점수: {self.score} | 난이도: {self.difficulty['name']} | 종료: Q")
        print("=" * (self.width + 2))
        
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1:
                    row += "█"
                elif (y, x) == self.snake[0]:  # 머리
                    row += "●"
                elif (y, x) in self.snake:  # 몸
                    row += "○"
                elif (y, x) == self.food:  # 음식
                    row += "◆"
                else:
                    row += " "
            print(row)
        
        print("=" * (self.width + 2))
        print("방향키로 이동, Q로 종료")

    def game_over(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print("=" * 40)
        print("           게임 오버!")
        print(f"         최종 점수: {self.score}")
        print("=" * 40)
        print("다시 하시겠습니까? (y/n)")

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
    """게임 로고 화면 표시"""
    os.system('clear' if os.name == 'posix' else 'cls')
    logo = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║    ███████ ███    ██  █████  ██   ██ ███████     ██████       ║
    ║    ██      ████   ██ ██   ██ ██  ██  ██         ██           ║
    ║    ███████ ██ ██  ██ ███████ █████   █████      ██   ███     ║
    ║         ██ ██  ██ ██ ██   ██ ██  ██  ██         ██    ██     ║
    ║    ███████ ██   ████ ██   ██ ██   ██ ███████     ██████      ║
    ║                                                               ║
    ║                      🐍 클래식 스네이크 게임 🐍                ║
    ║                                                               ║
    ║              터미널에서 즐기는 레트로 아케이드 게임              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(logo)
    print("\n" + "═" * 67)
    print("                      아무 키나 눌러 시작하세요...")
    print("═" * 67)
    
    # 키 입력 대기
    try:
        input()
    except KeyboardInterrupt:
        sys.exit(0)

def show_main_menu():
    """메인 메뉴 화면"""
    os.system('clear' if os.name == 'posix' else 'cls')
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                          메인 메뉴                             ║")
    print("╠═══════════════════════════════════════════════════════════════╣")
    print("║                                                               ║")
    print("║  🎮  1. 게임 시작                                              ║")
    print("║  🎯  2. 게임 방법                                              ║")
    print("║  ⚙️   3. 난이도 설정                                           ║")
    print("║  🏆  4. 최고 기록                                              ║")
    print("║  🚪  5. 게임 종료                                              ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print("\n선택하세요 (1-5): ", end="")

def show_how_to_play():
    """게임 방법 설명"""
    os.system('clear' if os.name == 'posix' else 'cls')
    instructions = """
╔═══════════════════════════════════════════════════════════════╗
║                          게임 방법                             ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  🕹️  조작법:                                                   ║
║     ↑ ↓ ← →  방향키로 스네이크를 조작합니다                     ║
║     Q        게임을 종료합니다                                 ║
║                                                               ║
║  🎯  목표:                                                     ║
║     ● 스네이크의 머리 (●)                                      ║
║     ○ 스네이크의 몸 (○)                                        ║
║     ◆ 음식 (◆)을 먹으면 점수가 올라가고 스네이크가 자랍니다     ║
║                                                               ║
║  ⚠️  주의사항:                                                  ║
║     • 벽에 부딪히면 게임이 끝납니다                            ║
║     • 자신의 몸에 부딪혀도 게임이 끝납니다                     ║
║     • 음식을 먹을 때마다 10점을 획득합니다                     ║
║                                                               ║
║  🏆  목표: 최대한 많은 음식을 먹고 높은 점수를 달성하세요!       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(instructions)
    print("\n아무 키나 눌러 메인 메뉴로 돌아가세요...")
    input()

def show_difficulty_menu():
    """난이도 선택 메뉴"""
    os.system('clear' if os.name == 'posix' else 'cls')
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                        난이도 선택                             ║")
    print("╠═══════════════════════════════════════════════════════════════╣")
    print("║                                                               ║")
    print("║  🟢  1. 쉬움                                                   ║")
    print("║      • 게임판 크기: 15 x 30                                   ║")
    print("║      • 속도: 느림 (초보자용)                                   ║")
    print("║      • 추천: 처음 하시는 분                                    ║")
    print("║                                                               ║")
    print("║  🟡  2. 보통                                                   ║")
    print("║      • 게임판 크기: 20 x 40                                   ║")
    print("║      • 속도: 보통 (일반용)                                     ║")
    print("║      • 추천: 기본적인 게임 경험이 있으신 분                    ║")
    print("║                                                               ║")
    print("║  🔴  3. 어려움                                                 ║")
    print("║      • 게임판 크기: 25 x 50                                   ║")
    print("║      • 속도: 빠름 (고수용)                                     ║")
    print("║      • 추천: 도전을 원하시는 분                               ║")
    print("║                                                               ║")
    print("║  🔙  4. 메인 메뉴로 돌아가기                                   ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print("\n선택하세요 (1-4): ", end="")

def show_high_scores():
    """최고 기록 표시 (임시로 더미 데이터 사용)"""
    os.system('clear' if os.name == 'posix' else 'cls')
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                         최고 기록                             ║")
    print("╠═══════════════════════════════════════════════════════════════╣")
    print("║                                                               ║")
    print("║  🏆 순위    난이도      점수       날짜                        ║")
    print("║  ─────────────────────────────────────────────────────────    ║")
    print("║   1️⃣     어려움      480점    2024-01-15                      ║")
    print("║   2️⃣     보통        350점    2024-01-12                      ║")
    print("║   3️⃣     보통        290점    2024-01-08                      ║")
    print("║   4️⃣     쉬움        240점    2024-01-05                      ║")
    print("║   5️⃣     어려움      220점    2024-01-03                      ║")
    print("║                                                               ║")
    print("║  💡 최고 기록 달성을 위한 팁:                                  ║")
    print("║     • 벽 근처에서는 신중하게 움직이세요                        ║")
    print("║     • 꼬리를 피하기 위해 넓은 공간을 확보하세요                ║")
    print("║     • 음식 위치를 미리 계산해서 효율적으로 이동하세요          ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print("\n아무 키나 눌러 메인 메뉴로 돌아가세요...")
    input()

def select_difficulty():
    """난이도 선택 함수"""
    while True:
        show_difficulty_menu()
        
        try:
            choice = input().strip()
            
            if choice == '1':
                return Difficulty.EASY
            elif choice == '2':
                return Difficulty.MEDIUM
            elif choice == '3':
                return Difficulty.HARD
            elif choice == '4':
                return None  # 메인 메뉴로 돌아가기
            else:
                print("잘못된 선택입니다. 다시 시도해주세요.")
                time.sleep(1)
                continue
                
        except KeyboardInterrupt:
            return None

def main():
    # 로고 표시
    show_logo()
    
    # 기본 난이도 설정
    current_difficulty = Difficulty.MEDIUM
    
    while True:
        show_main_menu()
        
        try:
            choice = input().strip()
            
            if choice == '1':  # 게임 시작
                game = SnakeGame(current_difficulty)
                game.run()
                
                # 게임 종료 후 재시작 여부 확인
                while True:
                    restart = input().strip().lower()
                    if restart in ['y', 'yes', 'ㅛ']:
                        game = SnakeGame(current_difficulty)
                        game.run()
                    elif restart in ['n', 'no', 'ㅜ']:
                        break
                    else:
                        print("y 또는 n을 입력해주세요.")
                        
            elif choice == '2':  # 게임 방법
                show_how_to_play()
                
            elif choice == '3':  # 난이도 설정
                selected_difficulty = select_difficulty()
                if selected_difficulty:
                    current_difficulty = selected_difficulty
                    os.system('clear' if os.name == 'posix' else 'cls')
                    print(f"난이도가 '{current_difficulty['name']}'로 설정되었습니다!")
                    print("아무 키나 눌러 계속하세요...")
                    input()
                    
            elif choice == '4':  # 최고 기록
                show_high_scores()
                
            elif choice == '5':  # 게임 종료
                os.system('clear' if os.name == 'posix' else 'cls')
                print("╔═══════════════════════════════════════════════════════════════╗")
                print("║                       게임을 종료합니다                        ║")
                print("║                                                               ║")
                print("║                🐍 플레이해 주셔서 감사합니다! 🐍                ║")
                print("║                                                               ║")
                print("╚═══════════════════════════════════════════════════════════════╝")
                break
                
            else:
                print("잘못된 선택입니다. 다시 시도해주세요.")
                time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n게임을 종료합니다.")
            break
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()