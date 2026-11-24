#!/usr/bin/env bash
#
# Installs skills/design-pipeline into ~/.claude/skills as a USER-LEVEL skill, not a plugin: a
# plugin copy would show up beside the user-level one under a second, namespaced name.
#
#   bash scripts/install.sh
#
# Linked at the repo so `git pull` updates the installed skill in place, with a copy as the fallback
# for a filesystem that refuses symlinks (Windows without Developer Mode).
#
# Sourcing this file has no side effects: it only defines functions, so tests/test-install.sh can
# source it, point DP_CLAUDE_DIR at a sandbox and call one function. It installs only when executed.
# Mirrors Knowledge-Pipeline's scripts/install-scaffold.sh.
#
# Inputs, overridable for the test:
#   DP_REPO_DIR    the checkout to link at   (default: this file's parent's parent)
#   DP_CLAUDE_DIR  where to install          (default: $HOME/.claude)

# Replace $2 with a link to $1. An existing symlink is ours to replace; a real file or directory is
# the user's, so it is moved aside rather than deleted.
link_or_copy() {
  src="$1"; dst="$2"
  [ -e "$src" ] || { printf ' warning: missing %s; skipping\n' "$src"; return 1; }
  if [ -L "$dst" ]; then
    rm -f "$dst"
  elif [ -e "$dst" ]; then
    # Back up OUTSIDE <claude>/skills. A "design-pipeline.bak-<stamp>/" left in there is itself
    # read as a skill, so Claude would list a second, stale copy under the backup's name.
    bakdir="${DP_CLAUDE_DIR:-$HOME/.claude}/.backups"
    mkdir -p "$bakdir"
    bak="$bakdir/$(basename "$dst").bak-$(date -u +%Y%m%d%H%M%S)"
    printf ' warning: %s is not a link; moving it to %s\n' "$dst" "$bak"
    mv "$dst" "$bak" || { printf ' warning: could not move it aside; skipping\n'; return 1; }
  fi
  if ln -s "$src" "$dst" 2>/dev/null && [ -L "$dst" ]; then
    printf '    linked %s\n' "$dst"
  elif cp -R "$src" "$dst"; then
    printf '    copied %s (symlinks unavailable: re-run this script after a git pull)\n' "$dst"
  else
    printf ' warning: could not install %s\n' "$dst"
    return 1
  fi
}

install_design_pipeline() {
  repo="${DP_REPO_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
  claude_dir="${DP_CLAUDE_DIR:-$HOME/.claude}"
  printf '\n==> Installing design-pipeline into %s\n' "$claude_dir"
  mkdir -p "$claude_dir/skills"
  link_or_copy "$repo/skills/design-pipeline" "$claude_dir/skills/design-pipeline" || return 1

  # Report the dependencies, but never fail the install on them: a missing design skill limits a
  # phase of a run, it does not make this install wrong.
  for py in python python3; do
    if "$py" -c 'pass' >/dev/null 2>&1; then
      printf '\n==> Dependency check\n'
      "$py" "$claude_dir/skills/design-pipeline/scripts/preflight.py" --skills-root "$claude_dir/skills" || true
      return 0
    fi
  done
  printf ' warning: no working python found; run the preflight by hand\n'
}

# Git Bash on Windows: `ln -s` silently copies unless MSYS is told to make native links.
case "$(uname -s 2>/dev/null)" in MINGW*|MSYS*) export MSYS="${MSYS:+$MSYS }winsymlinks:nativestrict" ;; esac

if [ "${BASH_SOURCE[0]}" = "$0" ]; then install_design_pipeline; fi
