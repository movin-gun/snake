#!/usr/bin/env python3
import sys
import termios
import tty
import time
import random
import os
import json
from enum import Enum
from datetime import datetime

class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

class Difficulty:
    # 터미널 문자 비율 고려하여 높이:너비를 약 1:2 비율로 조정
    EASY = {"name": "쉬움", "speed": 0.2, "board_size": (15, 25)}
    MEDIUM = {"name": "보통", "speed": 0.1, "board_size": (20, 35)}
    HARD = {"name": "어려움", "speed": 0.05, "board_size": (25, 45)}

class UIBox:
    """텍스트 박스 생성 및 관리 클래스"""
    
    @staticmethod
    def get_text_width(text):
        """텍스트의 실제 표시 너비 계산 (이모지 및 한글 고려)"""
        width = 0
        i = 0
        while i < len(text):
            char = text[i]
            if ord(char) > 127:  # 비ASCII 문자 (한글, 이모지 등)
                # 이모지나 한글은 보통 2칸 너비
                if ord(char) >= 0x1F600:  # 이모지 범위
                    width += 2
                elif ord(char) >= 0xAC00:  # 한글 범위
                    width += 2
                else:
                    width += 2  # 기타 유니코드 문자
            else:
                width += 1
            i += 1
        return width
    
    @staticmethod
    def pad_text(text, target_width, align='left'):
        """텍스트를 지정된 너비로 패딩"""
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
        """동적 박스 생성"""
        box_lines = []
        inner_width = width - 2  # 양쪽 경계선 제외
        
        # 상단 경계선
        box_lines.append("╔" + "═" * width + "╗")
        
        # 제목
        if title:
            title_line = UIBox.pad_text(title, inner_width, 'center')
            box_lines.append("║" + title_line + "║")
            box_lines.append("╠" + "═" * width + "╣")
        
        # 내용
        box_lines.append("║" + " " * inner_width + "║")
        
        for line in content_lines:
            if isinstance(line, dict):  # 특수 포맷팅
                if line.get('type') == 'separator':
                    box_lines.append("║" + " " * inner_width + "║")
                elif line.get('type') == 'menu_item':
                    prefix = line.get('prefix', '')
                    text = line.get('text', '')
                    selected = line.get('selected', False)
                    
                    if selected:
                        formatted_line = f"► {prefix}{text}"
                    else:
                        formatted_line = f"  {prefix}{text}"
                    
                    padded_line = UIBox.pad_text(formatted_line, inner_width)
                    box_lines.append("║" + padded_line + "║")
            else:
                # 일반 텍스트
                if len(line.strip()) == 0:
                    box_lines.append("║" + " " * inner_width + "║")
                else:
                    padded_line = UIBox.pad_text(f"  {line}", inner_width)
                    box_lines.append("║" + padded_line + "║")
        
        # 하단 여백 및 경계선
        box_lines.append("║" + " " * inner_width + "║")
        box_lines.append("╚" + "═" * width + "╝")
        
        return '\n'.join(box_lines)

class ScoreManager:
    """점수 관리 클래스"""
    
    def __init__(self):
        self.scores_file = os.path.expanduser("~/.snake_game_scores.json")
        self.scores = self.load_scores()
    
    def load_scores(self):
        """저장된 점수 불러오기"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def save_scores(self):
        """점수 저장하기"""
        try:
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"점수 저장 중 오류 발생: {e}")
    
    def add_score(self, score, difficulty_name):
        """새 점수 추가"""
        score_entry = {
            'score': score,
            'difficulty': difficulty_name,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        self.scores.append(score_entry)
        
        # 점수순으로 정렬 (내림차순)
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        
        # 상위 10개만 유지
        self.scores = self.scores[:10]
        
        self.save_scores()
    
    def get_top_scores(self, limit=5):
        """상위 점수 반환"""
        return self.scores[:limit]
    
    def is_new_high_score(self, score):
        """새로운 최고 기록인지 확인"""
        if not self.scores:
            return True
        return score > self.scores[0]['score']

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

def get_menu_input():
    """메뉴에서 방향키 입력을 처리하는 함수"""
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        
        while True:
            key = sys.stdin.read(1)
            
            if key == '\x1b':  # ESC 시퀀스 시작
                key2 = sys.stdin.read(1)
                if key2 == '[':
                    key3 = sys.stdin.read(1)
                    if key3 == 'A':  # 위쪽 화살표
                        return 'UP'
                    elif key3 == 'B':  # 아래쪽 화살표
                        return 'DOWN'
                    elif key3 == 'C':  # 오른쪽 화살표
                        return 'RIGHT'
                    elif key3 == 'D':  # 왼쪽 화살표
                        return 'LEFT'
            elif key == '\r' or key == '\n':  # Enter
                return 'ENTER'
            elif key in ['q', 'Q']:  # 종료
                return 'QUIT'
            elif key.isdigit():  # 숫자키 (기존 호환성)
                return key
            
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

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

    def game_over(self, score_manager):
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # 새로운 최고 기록인지 확인 (저장하기 전에)
        is_high_score = score_manager.is_new_high_score(self.score)
        
        # 점수 저장
        score_manager.add_score(self.score, self.difficulty['name'])
        
        content = [
            "게임 오버!",
            {"type": "separator"},
            f"최종 점수: {self.score}점",
            f"난이도: {self.difficulty['name']}",
            {"type": "separator"}
        ]
        
        if is_high_score and self.score > 0:
            content.extend([
                "🎉 새로운 최고 기록입니다! 🎉",
                {"type": "separator"}
            ])
        
        content.extend([
            "💡 재시작하려면 'y', 메뉴로 돌아가려면 'n'을 입력하세요"
        ])
        
        box = UIBox.create_box("", content)
        print(box)

    def cleanup(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_adjusted_speed(self):
        """방향에 따른 속도 조정 - 터미널 문자 간격 차이 보정"""
        base_speed = self.speed
        
        # 터미널에서 문자의 세로 간격이 가로 간격보다 약 1.5~2배 크므로 조정
        if self.direction in [Direction.UP, Direction.DOWN]:
            return base_speed * 1.1  # 10% 느리게 (세로 간격 보정)
        else:  # LEFT, RIGHT
            return base_speed * 0.9  # 10% 빠르게 (가로 간격 보정)
    
    def run(self, score_manager=None):
        if score_manager is None:
            score_manager = ScoreManager()
            
        try:
            while self.running:
                self.draw_board()
                self.handle_input()
                
                if not self.move_snake():
                    break
                
                # 방향에 따른 조정된 속도 사용
                adjusted_speed = self.get_adjusted_speed()
                time.sleep(adjusted_speed)
            
            self.game_over(score_manager)
            
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

def show_main_menu(selected_index=0):
    """메인 메뉴 화면"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    menu_items = [
        {"type": "menu_item", "prefix": "🎮  ", "text": "게임 시작", "selected": selected_index == 0},
        {"type": "menu_item", "prefix": "🎯  ", "text": "게임 방법", "selected": selected_index == 1},
        {"type": "menu_item", "prefix": "⚙️   ", "text": "난이도 설정", "selected": selected_index == 2},
        {"type": "menu_item", "prefix": "🏆  ", "text": "최고 기록", "selected": selected_index == 3},
        {"type": "menu_item", "prefix": "🚪  ", "text": "게임 종료", "selected": selected_index == 4}
    ]
    
    content = menu_items + [
        {"type": "separator"},
        "방향키로 선택, Enter로 확인, Q로 종료"
    ]
    
    box = UIBox.create_box("메인 메뉴", content)
    print(box)

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

def show_difficulty_menu(selected_index=0):
    """난이도 선택 메뉴"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    difficulty_items = [
        {"name": "🟢  쉬움", "details": ["게임판 크기: 15 x 25", "속도: 느림 (초보자용)", "추천: 처음 하시는 분"]},
        {"name": "🟡  보통", "details": ["게임판 크기: 20 x 35", "속도: 보통 (일반용)", "추천: 기본적인 게임 경험이 있으신 분"]},
        {"name": "🔴  어려움", "details": ["게임판 크기: 25 x 45", "속도: 빠름 (고수용)", "추천: 도전을 원하시는 분"]},
        {"name": "🔙  메인 메뉴로 돌아가기", "details": []}
    ]
    
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                        난이도 선택                             ║")
    print("╠═══════════════════════════════════════════════════════════════╣")
    print("║                                                               ║")
    
    for i, item in enumerate(difficulty_items):
        if i == selected_index:
            print(f"║  ► {item['name']}                                           ║")
        else:
            print(f"║    {item['name']}                                           ║")
            
        if item['details']:
            for detail in item['details']:
                print(f"║      • {detail}                                   ║"[:67] + "║")
            print("║                                                               ║")
    
    print("╚═══════════════════════════════════════════════════════════════╝")
    print("\n방향키로 선택, Enter로 확인, Q로 뒤로가기")

def show_high_scores():
    """최고 기록 표시"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    score_manager = ScoreManager()
    top_scores = score_manager.get_top_scores(10)
    
    content = []
    
    if not top_scores:
        content.extend([
            "아직 기록된 점수가 없습니다.",
            {"type": "separator"},
            "첫 번째 게임을 시작해보세요! 🎮"
        ])
    else:
        content.append("🏆 순위    난이도      점수       날짜")
        content.append("─" * 50)
        
        rank_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for i, score_entry in enumerate(top_scores):
            if i < len(rank_emojis):
                emoji = rank_emojis[i]
            else:
                emoji = f"{i+1}."
                
            score_line = f"  {emoji}     {score_entry['difficulty']}      {score_entry['score']}점    {score_entry['date']}"
            content.append(score_line)
    
    content.extend([
        {"type": "separator"},
        "💡 최고 기록 달성을 위한 팁:",
        "• 벽 근처에서는 신중하게 움직이세요",
        "• 꼬리를 피하기 위해 넓은 공간을 확보하세요", 
        "• 음식 위치를 미리 계산해서 효율적으로 이동하세요",
        {"type": "separator"},
        "아무 키나 눌러 메인 메뉴로 돌아가세요..."
    ])
    
    box = UIBox.create_box("최고 기록", content)
    print(box)
    input()

def select_difficulty():
    """난이도 선택 함수"""
    selected_index = 0
    max_index = 3  # 4개 선택지 (0-3)
    
    while True:
        show_difficulty_menu(selected_index)
        
        try:
            key = get_menu_input()
            
            if key == 'UP':
                selected_index = (selected_index - 1) % (max_index + 1)
            elif key == 'DOWN':
                selected_index = (selected_index + 1) % (max_index + 1)
            elif key == 'ENTER':
                if selected_index == 0:
                    return Difficulty.EASY
                elif selected_index == 1:
                    return Difficulty.MEDIUM
                elif selected_index == 2:
                    return Difficulty.HARD
                elif selected_index == 3:
                    return None  # 메인 메뉴로 돌아가기
            elif key == 'QUIT' or key == 'q':
                return None
            elif key in ['1', '2', '3', '4']:  # 기존 숫자키 지원
                choice = int(key)
                if choice == 1:
                    return Difficulty.EASY
                elif choice == 2:
                    return Difficulty.MEDIUM
                elif choice == 3:
                    return Difficulty.HARD
                elif choice == 4:
                    return None
                
        except KeyboardInterrupt:
            return None

def main():
    # 로고 표시
    show_logo()
    
    # 기본 난이도 설정 및 점수 관리자 초기화
    current_difficulty = Difficulty.MEDIUM
    score_manager = ScoreManager()
    selected_index = 0
    max_index = 4  # 5개 메뉴 (0-4)
    
    while True:
        show_main_menu(selected_index)
        
        try:
            key = get_menu_input()
            
            if key == 'UP':
                selected_index = (selected_index - 1) % (max_index + 1)
            elif key == 'DOWN':
                selected_index = (selected_index + 1) % (max_index + 1)
            elif key == 'ENTER':
                if selected_index == 0:  # 게임 시작
                    game = SnakeGame(current_difficulty)
                    game.run(score_manager)
                    
                    # 게임 종료 후 재시작 여부 확인
                    while True:
                        restart = input().strip().lower()
                        if restart in ['y', 'yes', 'ㅛ']:
                            game = SnakeGame(current_difficulty)
                            game.run(score_manager)
                        elif restart in ['n', 'no', 'ㅜ']:
                            break
                        else:
                            print("y 또는 n을 입력해주세요.")
                            
                elif selected_index == 1:  # 게임 방법
                    show_how_to_play()
                    
                elif selected_index == 2:  # 난이도 설정
                    selected_difficulty = select_difficulty()
                    if selected_difficulty:
                        current_difficulty = selected_difficulty
                        os.system('clear' if os.name == 'posix' else 'cls')
                        print(f"난이도가 '{current_difficulty['name']}'로 설정되었습니다!")
                        print("아무 키나 눌러 계속하세요...")
                        input()
                        
                elif selected_index == 3:  # 최고 기록
                    show_high_scores()
                    
                elif selected_index == 4:  # 게임 종료
                    os.system('clear' if os.name == 'posix' else 'cls')
                    print("╔═══════════════════════════════════════════════════════════════╗")
                    print("║                       게임을 종료합니다                        ║")
                    print("║                                                               ║")
                    print("║                🐍 플레이해 주셔서 감사합니다! 🐍                ║")
                    print("║                                                               ║")
                    print("╚═══════════════════════════════════════════════════════════════╝")
                    break
                    
            elif key == 'QUIT':  # Q키로 직접 종료
                os.system('clear' if os.name == 'posix' else 'cls')
                print("╔═══════════════════════════════════════════════════════════════╗")
                print("║                       게임을 종료합니다                        ║")
                print("║                                                               ║")
                print("║                🐍 플레이해 주셔서 감사합니다! 🐍                ║")
                print("║                                                               ║")
                print("╚═══════════════════════════════════════════════════════════════╝")
                break
                
            elif key in ['1', '2', '3', '4', '5']:  # 기존 숫자키 지원
                choice = int(key)
                if choice == 1:  # 게임 시작
                    game = SnakeGame(current_difficulty)
                    game.run(score_manager)
                    
                    # 게임 종료 후 재시작 여부 확인
                    while True:
                        restart = input().strip().lower()
                        if restart in ['y', 'yes', 'ㅛ']:
                            game = SnakeGame(current_difficulty)
                            game.run(score_manager)
                        elif restart in ['n', 'no', 'ㅜ']:
                            break
                        else:
                            print("y 또는 n을 입력해주세요.")
                            
                elif choice == 2:  # 게임 방법
                    show_how_to_play()
                    
                elif choice == 3:  # 난이도 설정
                    selected_difficulty = select_difficulty()
                    if selected_difficulty:
                        current_difficulty = selected_difficulty
                        os.system('clear' if os.name == 'posix' else 'cls')
                        print(f"난이도가 '{current_difficulty['name']}'로 설정되었습니다!")
                        print("아무 키나 눌러 계속하세요...")
                        input()
                        
                elif choice == 4:  # 최고 기록
                    show_high_scores()
                    
                elif choice == 5:  # 게임 종료
                    os.system('clear' if os.name == 'posix' else 'cls')
                    print("╔═══════════════════════════════════════════════════════════════╗")
                    print("║                       게임을 종료합니다                        ║")
                    print("║                                                               ║")
                    print("║                🐍 플레이해 주셔서 감사합니다! 🐍                ║")
                    print("║                                                               ║")
                    print("╚═══════════════════════════════════════════════════════════════╝")
                    break
            
        except KeyboardInterrupt:
            print("\n게임을 종료합니다.")
            break
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()