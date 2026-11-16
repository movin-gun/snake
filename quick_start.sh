#!/bin/sh
# Snake Game CLI - installer / quick play
#   play once : curl -fsSL https://raw.githubusercontent.com/movin-gun/snake/main/quick_start.sh | sh
#   install   : curl -fsSL https://raw.githubusercontent.com/movin-gun/snake/main/quick_start.sh | sh -s install
#   uninstall : curl -fsSL https://raw.githubusercontent.com/movin-gun/snake/main/quick_start.sh | sh -s uninstall
set -e

MODE="${1:-play}"
REPO_TARBALL="${SNAKE_TARBALL:-https://github.com/movin-gun/snake/archive/refs/heads/main.tar.gz}"
BIN_DIR="${SNAKE_BIN_DIR:-$HOME/.local/bin}"
GAME_DIR="${SNAKE_GAME_DIR:-$HOME/.local/share/snake-game/app}"

info() { printf '\033[34m[INFO]\033[0m %s\n' "$1"; }
ok()   { printf '\033[32m[ OK ]\033[0m %s\n' "$1"; }
die()  { printf '\033[31m[FAIL]\033[0m %s\n' "$1" >&2; exit 1; }

PY=$(command -v python3 || command -v python || true)
[ -n "$PY" ] || die "Python 3.7+ is required"
"$PY" -c 'import sys; sys.exit(sys.version_info < (3, 7))' || die "Python 3.7+ is required"

fetch() {
    TMP=$(mktemp -d)
    trap 'rm -rf "$TMP"' EXIT INT TERM
    curl -fsSL "$REPO_TARBALL" | tar -xz -C "$TMP"
    SRC="$TMP/snake-main"
}

case "$MODE" in
  install)
    info "Downloading Snake Game..."
    fetch
    rm -rf "$GAME_DIR"
    mkdir -p "$GAME_DIR" "$BIN_DIR"
    cp -R "$SRC/snake_game" "$GAME_DIR/"
    cat > "$BIN_DIR/snakegame" <<WRAPPER
#!/bin/sh
PYTHONPATH="$GAME_DIR\${PYTHONPATH:+:\$PYTHONPATH}" exec "$PY" -m snake_game "\$@"
WRAPPER
    chmod +x "$BIN_DIR/snakegame"
    ok "Installed. Run: snakegame"
    case ":$PATH:" in
      *":$BIN_DIR:"*) ;;
      *) info "Add $BIN_DIR to your PATH, e.g.  export PATH=\"\$PATH:$BIN_DIR\"" ;;
    esac
    ;;
  uninstall)
    rm -f "$BIN_DIR/snakegame"
    rm -rf "$GAME_DIR"
    ok "Removed. (Best scores are kept in ~/.local/share/snake-game/scores.json)"
    ;;
  play)
    fetch
    cd "$SRC"
    "$PY" -m snake_game < /dev/tty
    ;;
  *)
    die "unknown mode '$MODE' (use: play | install | uninstall)"
    ;;
esac
