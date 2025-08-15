#!/bin/bash
# Snake Game CLI - Quick Start

set -e

echo "🐍 Downloading and starting Snake Game..."

# Create temp directory and download
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Download and extract
curl -sL https://github.com/movin-gun/snake/archive/main.zip -o snake.zip
unzip -q snake.zip
cd snake-main

# Run the game
echo "🎮 Starting game..."
python3 snake_game/game.py

# Cleanup
cd / && rm -rf "$TEMP_DIR"
echo "👋 Thanks for playing!"