#!/bin/bash
# Snake Game - One-liner
mkdir -p /tmp/snake;cd /tmp/snake;curl -sL github.com/movin-gun/snake/archive/main.zip -o s.zip;unzip -q s.zip;cd snake-main;python3 snake_game/game.py;cd /;rm -rf /tmp/snake