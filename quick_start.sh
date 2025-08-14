#!/bin/bash

# 🐍 Snake Game CLI - Quick Start Script
# This script downloads and runs the Snake game without installation

set -e

echo "🐍 Snake Game CLI - Quick Start"
echo "==============================="

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "📁 Creating temporary directory: $TEMP_DIR"

# Navigate to temp directory
cd "$TEMP_DIR"

# Clone the repository
echo "⬇️  Downloading Snake Game..."
git clone -q https://github.com/movin-gun/snake.git

# Navigate to snake directory
cd snake

# Check Python version
echo "🐍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1)
    if [ "$PYTHON_VERSION" = "3" ]; then
        PYTHON_CMD="python"
    else
        echo "❌ Python 3 is required but not found"
        exit 1
    fi
else
    echo "❌ Python is not installed"
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing dependencies..."
$PYTHON_CMD -m pip install --user -e . > /dev/null 2>&1 || true

# Run the game
echo "🎮 Starting Snake Game..."
echo ""
$PYTHON_CMD -m snake_game.game

# Cleanup
echo ""
echo "🧹 Cleaning up temporary files..."
cd /
rm -rf "$TEMP_DIR"

echo "👋 Thanks for playing Snake Game CLI!"