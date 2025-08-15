#!/bin/bash
# Snake Game CLI - One-line installer
# Usage: curl -s https://raw.githubusercontent.com/movin-gun/snake/main/quick_start.sh | bash
# or: curl -s https://raw.githubusercontent.com/movin-gun/snake/main/quick_start.sh | bash -s install

set -e

INSTALL_MODE="${1:-play}"
INSTALL_DIR="$HOME/.local/bin"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

if [ "$INSTALL_MODE" = "install" ]; then
    echo -e "${YELLOW}🐍 Snake Game CLI - Installing...${NC}"
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        print_error "Python is required but not found. Please install Python 3.7+ first."
        exit 1
    fi
    
    PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        PYTHON_CMD="python"
    fi
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    
    # Download and install
    print_status "Downloading Snake Game..."
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    curl -sL https://github.com/movin-gun/snake/archive/main.zip -o snake.zip
    unzip -q snake.zip
    cd snake-main
    
    # Create standalone executable
    print_status "Creating executable..."
    cat > "$INSTALL_DIR/snakegame" << 'EOF'
#!/bin/bash
# Snake Game CLI - Standalone executable

SNAKE_DIR="$HOME/.snake-game"

# Check if game files exist
if [ ! -f "$SNAKE_DIR/snake_game/game.py" ]; then
    echo "🐍 Setting up Snake Game..."
    mkdir -p "$SNAKE_DIR"
    cd "$SNAKE_DIR"
    curl -sL https://github.com/movin-gun/snake/archive/main.zip -o snake.zip
    unzip -q snake.zip
    mv snake-main/* .
    rm -rf snake-main snake.zip
fi

# Run the game
cd "$SNAKE_DIR"
if command -v python3 &> /dev/null; then
    python3 snake_game/game.py
else
    python snake_game/game.py
fi
EOF
    
    chmod +x "$INSTALL_DIR/snakegame"
    
    # Setup game files
    print_status "Installing game files..."
    SNAKE_DIR="$HOME/.snake-game"
    mkdir -p "$SNAKE_DIR"
    cp -r * "$SNAKE_DIR/"
    
    # Cleanup
    cd /
    rm -rf "$TEMP_DIR"
    
    print_success "Snake Game CLI installed successfully!"
    echo ""
    echo -e "${YELLOW}🎮 To play the game, run:${NC}"
    echo -e "   ${GREEN}snakegame${NC}"
    echo ""
    echo -e "${BLUE}💡 Make sure ${GREEN}$INSTALL_DIR${BLUE} is in your PATH${NC}"
    echo -e "   Add this to your ~/.bashrc or ~/.zshrc:"
    echo -e "   ${GREEN}export PATH=\"\$PATH:$INSTALL_DIR\"${NC}"
    
else
    echo -e "${YELLOW}🐍 Snake Game CLI - Quick Play${NC}"
    
    # Quick play mode (default)
    print_status "Downloading and starting game..."
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    curl -sL https://github.com/movin-gun/snake/archive/main.zip -o snake.zip
    unzip -q snake.zip
    cd snake-main
    
    print_status "Starting game..."
    if command -v python3 &> /dev/null; then
        python3 snake_game/game.py
    else
        python snake_game/game.py
    fi
    
    # Cleanup
    cd /
    rm -rf "$TEMP_DIR"
    print_success "Thanks for playing!"
fi