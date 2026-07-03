#!/usr/bin/env bash
#
# sync.sh — copy the MynaDB documentation portal from the (private) mynadb
# repo into this (public) portal repo, then optionally commit & push.
#
# Usage:
#   ./sync.sh                       # sync from ../mynadb/web/portal
#   ./sync.sh /path/to/web/portal   # sync from a custom source dir
#   ./sync.sh --push                # sync, then commit & push to origin/main
#   MYNADB_PORTAL_SRC=/x ./sync.sh  # source dir via env var
#
set -euo pipefail

# Directory this script lives in = the portal repo root.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PUSH=0
SRC=""
for arg in "$@"; do
  case "$arg" in
    --push) PUSH=1 ;;
    *)      SRC="$arg" ;;
  esac
done

# Source portal dir: positional arg > env var > sibling default.
SRC="${SRC:-${MYNADB_PORTAL_SRC:-$SCRIPT_DIR/../mynadb/web/portal}}"

if [[ ! -d "$SRC" ]]; then
  echo "error: source portal dir not found: $SRC" >&2
  echo "usage: ./sync.sh [path-to-mynadb/web/portal] [--push]" >&2
  exit 1
fi

echo "Syncing portal"
echo "  from: $SRC"
echo "    to: $SCRIPT_DIR"

# Mirror source -> repo root, removing stale files. Repo-only files
# (.git, .github, LICENSE, sync.sh) are always preserved.
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete \
    --exclude='.git/' \
    --exclude='.github/' \
    --exclude='LICENSE' \
    --exclude='sync.sh' \
    "$SRC"/ "$SCRIPT_DIR"/
else
  # Fallback without rsync: clear existing portal content (keeping the
  # protected files), then copy a fresh snapshot from the source.
  find "$SCRIPT_DIR" -mindepth 1 -maxdepth 1 \
    ! -name '.git' ! -name '.github' ! -name 'LICENSE' ! -name 'sync.sh' \
    -exec rm -rf {} +
  cp -a "$SRC"/. "$SCRIPT_DIR"/
fi

echo "Sync complete."

if [[ "$PUSH" -eq 1 ]]; then
  cd "$SCRIPT_DIR"
  git add -A
  if git diff --cached --quiet; then
    echo "No changes to commit."
  else
    git commit -m "docs: sync portal from mynadb"
    git push origin main
    echo "Pushed to origin/main."
  fi
else
  echo "Review changes:  git -C \"$SCRIPT_DIR\" status"
  echo "Or run with --push to commit & push automatically."
fi
