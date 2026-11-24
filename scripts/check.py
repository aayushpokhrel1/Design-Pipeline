"""Hold the skill to the rules CLAUDE.md states, so they are not just prose.

    python scripts/check.py [--skills-root DIR]

1. Every skill routing.md names exists under --skills-root (default ~/.claude/skills; CI passes a
   directory of shallow-cloned upstream repos), and every `impeccable <command>` it names has a
   reference/<command>.md in impeccable. A renamed upstream skill fails here, not mid-run.
2. Nothing under skills/ hardcodes a home directory.
3. Every SKILL.md's name matches its directory and it stays invoke-only.
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "skills" / "design-pipeline" / "scripts"))

from preflight import ROUTING, _frontmatter_name, installed_skills, parse_routing  # noqa: E402

# Same pattern as Knowledge-Pipeline's scripts/check-skills.sh. A placeholder such as <you> is fine.
HOME_PATH = re.compile(r"(/home/[a-z]|/Users/[A-Za-z]|C:[/\\]+Users[/\\]+[A-Za-z]|/mnt/[a-z]/Users/[A-Za-z])")


def check_routing(text: str, root: Path) -> list:
    errs, have = [], installed_skills(root)
    for r in parse_routing(text):
        if not r.skills:
            errs.append(f"routing.md: '{r.finding}' ({r.section}) names no skill in backticks")
        for s in r.skills:
            if s not in have:
                errs.append(f"routing.md: skill '{s}' ({r.section}: {r.finding}) not found under {root}")
        for c in r.commands:
            if "impeccable" in have and not (have["impeccable"] / "reference" / f"{c}.md").is_file():
                errs.append(f"routing.md: impeccable has no command '{c}' ({r.section}: {r.finding})")
    return errs


def check_skill_files(skills_dir: Path) -> list:
    errs = [] if any(skills_dir.rglob("SKILL.md")) else [f"no SKILL.md under {skills_dir}"]
    for f in sorted(p for p in skills_dir.rglob("*") if p.is_file()):
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for n, line in enumerate(lines, 1):
            if HOME_PATH.search(line) and "<" not in line:
                errs.append(f"{f}:{n} hardcodes a home directory; use $HOME or a skill name")
        if f.name == "SKILL.md":
            name = _frontmatter_name(f)
            if name != f.parent.name:
                errs.append(f"{f} declares name '{name}' but lives in '{f.parent.name}'")
            head = lines[: lines.index("---", 1)] if "---" in lines[1:] else lines
            if "disable-model-invocation: true" not in head:
                errs.append(f"{f} must keep 'disable-model-invocation: true' in its frontmatter")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skills-root", type=Path, default=Path.home() / ".claude" / "skills")
    args = ap.parse_args()
    errs = check_routing(ROUTING.read_text(encoding="utf-8"), args.skills_root)
    errs += check_skill_files(REPO / "skills")
    for e in errs:
        print(f"  FAIL {e}")
    print(f"{len(errs)} problems")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
