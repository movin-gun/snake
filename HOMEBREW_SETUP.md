# 홈브루 설치 가이드 (Homebrew Setup Guide)

## ⚠️ 현재 상태: 홈브루 탭 미설정

**홈브루 탭이 아직 설정되지 않았습니다.**

현재 `brew tap movin-gun/snake`를 실행하면 다음 오류가 발생합니다:
```
Warning: No available formula with the name "snake-game-cli"
```

## 🔧 현재 권장 설치 방법

### 1. pip으로 설치 (가장 안정적)

```bash
git clone https://github.com/movin-gun/snake.git
cd snake
pip install .
snakegame
```

### 2. 직접 실행 (설치 불필요)

```bash
git clone https://github.com/movin-gun/snake.git
cd snake
python3 -m snake_game.game
```

### 3. 원클릭 실행 스크립트

```bash
curl -s https://raw.githubusercontent.com/movin-gun/snake/main/quick_start.sh | bash
```

## 🎮 설치 후 사용법

설치가 완료되면 터미널에서 다음 명령어로 게임을 실행할 수 있습니다:

```bash
snakegame      # 추천 명령어
snake-game     # 대체 명령어
snake          # 짧은 명령어
```

## 🔧 로컬 테스트

홈브루 탭을 퍼블리시하기 전에 로컬에서 테스트:

```bash
# 현재 프로젝트에서
cd snake
pip install .

# 명령어 테스트
snakegame
```

## ⚠️ 주의사항

1. **GitHub 저장소**: `homebrew-snake` 저장소가 public이어야 함
2. **Formula 파일명**: `snake-game-cli.rb`로 유지
3. **Python 의존성**: Python 3.7+ 필요
4. **권한**: 탭 저장소에 대한 관리 권한 필요

## 🚀 배포 체크리스트

- [ ] `homebrew-snake` 저장소 생성
- [ ] Formula 파일 업로드
- [ ] 로컬 테스트 완료
- [ ] `brew tap movin-gun/snake` 실행
- [ ] `brew install snake-game-cli` 실행
- [ ] `snakegame` 명령어로 게임 실행 확인