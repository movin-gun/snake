#!/bin/sh
# Snake Game - play without installing.
#   curl -sL https://raw.githubusercontent.com/movin-gun/snake/main/play.sh | sh
set -e

PY=$(command -v python3 || command -v python || true)
if [ -z "$PY" ]; then
    echo "snake: Python 3.7+ is required" >&2
    exit 1
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT INT TERM

curl -fsSL https://github.com/movin-gun/snake/archive/refs/heads/main.tar.gz | tar -xz -C "$TMP"

# When run as `curl ... | sh`, stdin is the pipe, not the keyboard.
# Read keys from the controlling terminal instead.
cd "$TMP/snake-main"
"$PY" -m snake_game "$@" < /dev/tty
