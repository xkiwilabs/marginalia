#!/usr/bin/env bash
#
# install.sh — install marginalia into Claude Code as skills + a slash command.
#
# Symlinks the seven marginalia skills and the /marginalia command into
# ~/.claude/ so Claude Code discovers them. Symlinks (not copies) mean edits to
# the protocols in this repo take effect immediately, with no reinstall.
#
# Usage:
#   ./install.sh            # install (or repair) the symlinks
#   ./install.sh --uninstall  # remove the symlinks this script created
#   CLAUDE_HOME=/path ./install.sh   # override the target (default: ~/.claude)
#
set -euo pipefail

# Resolve the repo root from this script's own location, so the script works
# regardless of where it's invoked from or where the repo is cloned.
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"

SKILLS=(
  marginalia-write
  marginalia-review
  marginalia-extract-style
  marginalia-verify-cites
  marginalia-calibrate
  marginalia-refine
  marginalia-adapt
)
COMMAND="marginalia.md"

link() {
  # link <source> <target> — symlink source→target, backing up a real file/dir
  # but silently replacing a stale symlink.
  local src="$1" dest="$2"
  if [[ -e "$src" ]]; then :; else
    echo "  ✗ missing source: $src" >&2
    return 1
  fi
  if [[ -L "$dest" ]]; then
    rm "$dest"
  elif [[ -e "$dest" ]]; then
    mv "$dest" "$dest.bak.$$"
    echo "  • backed up existing $dest → $dest.bak.$$"
  fi
  ln -s "$src" "$dest"
  echo "  ✓ $dest → $src"
}

uninstall() {
  echo "Uninstalling marginalia from $CLAUDE_HOME ..."
  for s in "${SKILLS[@]}"; do
    local dest="$CLAUDE_HOME/skills/$s"
    if [[ -L "$dest" ]]; then rm "$dest"; echo "  ✓ removed $dest"; fi
  done
  local cdest="$CLAUDE_HOME/commands/$COMMAND"
  if [[ -L "$cdest" ]]; then rm "$cdest"; echo "  ✓ removed $cdest"; fi
  echo "Done. (Any *.bak.* backups were left in place.)"
}

if [[ "${1:-}" == "--uninstall" ]]; then
  uninstall
  exit 0
fi

echo "Installing marginalia from $REPO_DIR into $CLAUDE_HOME ..."
mkdir -p "$CLAUDE_HOME/skills" "$CLAUDE_HOME/commands"

for s in "${SKILLS[@]}"; do
  link "$REPO_DIR/claude-code/skills/$s" "$CLAUDE_HOME/skills/$s"
done
link "$REPO_DIR/claude-code/commands/$COMMAND" "$CLAUDE_HOME/commands/$COMMAND"

echo
echo "Done. Restart Claude Code (or start a new session) to pick up the skills."
echo "Try:  /marginalia review <file>   or ask for writing help to engage marginalia-write."
