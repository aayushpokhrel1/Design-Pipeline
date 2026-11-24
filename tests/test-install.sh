#!/usr/bin/env bash
#
# Smoke test for scripts/install.sh. Runs the real installer against a throwaway directory, never
# your actual ~/.claude.
#
#   bash tests/test-install.sh
set -u

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fails=0
pass() { printf '  ok   %s\n' "$1"; }
fail() { printf '  FAIL %s\n' "$1"; fails=$((fails + 1)); }

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

# shellcheck source=scripts/install.sh
. "$REPO_DIR/scripts/install.sh"
# Sourcing must not have installed anything anywhere.
[ -z "$(ls -A "$SANDBOX")" ] && pass "sourcing has no side effects" || fail "sourcing installed something"

run() { DP_REPO_DIR="$REPO_DIR" DP_CLAUDE_DIR="$1" install_design_pipeline >/dev/null 2>&1; }
readable() { grep -q '^name: design-pipeline' "$1/skills/design-pipeline/SKILL.md" 2>/dev/null; }

echo "1. clean install"
C1="$SANDBOX/clean"
run "$C1"
readable "$C1" && pass "skill readable through the install path" || fail "skill unreadable through the install path"

echo "2. second run is idempotent"
run "$C1"
[ "$(ls -A "$C1/skills" | wc -l | tr -d ' ')" = 1 ] && pass "one entry under skills/" || fail "skills/ has $(ls -A "$C1/skills")"
[ ! -e "$C1/.backups" ] && pass "no backup made of our own link" || fail "a second run backed up our own link"

echo "3. a real directory in place is moved outside skills/"
C3="$SANDBOX/real"
mkdir -p "$C3/skills/design-pipeline" && echo old > "$C3/skills/design-pipeline/SKILL.md"
run "$C3"
ls "$C3/.backups/" 2>/dev/null | grep -q '^design-pipeline.bak-' && pass "backed up under .backups/" || fail "no backup under .backups/"
ls "$C3/skills/" | grep -q 'bak-' && fail "a backup was left inside skills/" || pass "nothing named *.bak-* under skills/"
readable "$C3" && pass "new skill installed over it" || fail "new skill not installed"

echo "4. a path with a space"
C4="$SANDBOX/with space/claude"
run "$C4"
readable "$C4" && pass "installs under a path with a space" || fail "failed under a path with a space"

echo
if [ "$fails" -eq 0 ]; then echo "installer checks passed"; else echo "$fails problem(s) found"; exit 1; fi
