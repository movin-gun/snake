# 홈브루 설치 가이드 (Homebrew Setup Guide)

## 🍺 홈브루 탭(Tap) 생성하기

### 1단계: 홈브루 탭 저장소 생성

GitHub에서 새 저장소를 생성하세요:
- 저장소 이름: `homebrew-snake` (반드시 `homebrew-` 접두사 필요)
- 공개 저장소로 설정

### 2단계: Formula 파일 복사

현재 `Formula/snake-game-cli.rb` 파일을 새로 만든 저장소의 루트에 복사하세요:

```bash
# 새 탭 저장소 생성 후
git clone https://github.com/movin-gun/homebrew-snake.git
cd homebrew-snake

# Formula 파일 복사 (이 프로젝트에서)
cp ../snake/Formula/snake-game-cli.rb .

# 커밋 및 푸시
git add snake-game-cli.rb
git commit -m "Add snake-game-cli formula"
git push origin main
```

### 3단계: 탭 등록 및 설치

```bash
# 탭 추가
brew tap movin-gun/snake

# 게임 설치
brew install snake-game-cli

# 게임 실행
snakegame
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