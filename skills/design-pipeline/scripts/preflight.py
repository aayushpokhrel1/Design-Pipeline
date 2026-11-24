"""Check that every skill the pipeline calls is installed and switched on.

    python "$HOME/.claude/skills/design-pipeline/scripts/preflight.py"

The list of skills comes from ../references/routing.md and nowhere else, so adding a row there is
all it takes for the preflight (and the repo's check script) to cover a new dependency.

Exit 0 when every line is "ok", 1 otherwise. A missing dependency limits phases, it does not stop
the run, so the report says which ones.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

ROUTING = Path(__file__).resolve().parent.parent / "references" / "routing.md"


class Route(NamedTuple):
    section: str
    finding: str
    skills: tuple
    commands: tuple


def parse_routing(text: str) -> list:
    routes, section = [], ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # Header and separator rows are not routes.
        if len(cells) < 2 or set(cells[0]) <= set("-: ") or cells[0] == "Finding":
            continue
        tokens = re.findall(r"`([^`]+)`", cells[-1])
        skills = tuple(dict.fromkeys(t.split()[0] for t in tokens))
        commands = tuple(t.split()[1] for t in tokens if t.split()[0] == "impeccable" and len(t.split()) > 1)
        routes.append(Route(section, cells[0], skills, commands))
    return routes


def _frontmatter_name(skill_md: Path):
    try:
        lines = skill_md.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line[5:].strip().strip("'\"")
    return None


def installed_skills(root: Path) -> dict:
    # rglob, not <root>/<name>/: CI scans cloned upstream repos, whose layouts differ. When a name
    # appears more than once the shallowest copy wins: upstream impeccable carries test fixtures that
    # are SKILL.md files named impeccable, deeper than the real skill and without its reference/.
    found = {}
    if not root.is_dir():
        return found
    for skill_md in root.rglob("SKILL.md"):
        name = _frontmatter_name(skill_md)
        if name and (name not in found or len(skill_md.parts) < len(found[name].parts) + 1):
            found[name] = skill_md.parent
    return found


def disabled_skills(settings: Path):
    # An entry "<name>": "off" hides an installed skill from every session. That is how ten design
    # skills sat installed and invisible for three months, so disk alone is not enough.
    try:
        data = json.loads(settings.read_text(encoding="utf-8"))
        overrides = data.get("skillOverrides", {}) or {}
        return {k for k, v in overrides.items() if v == "off"}
    except (OSError, ValueError, AttributeError):
        return None


def preflight(routing: Path, root: Path, settings: Path) -> tuple:
    routes = parse_routing(routing.read_text(encoding="utf-8"))
    have = installed_skills(root)
    off = disabled_skills(settings)
    lines = []
    if off is None:
        lines.append(f"warning: could not read skillOverrides from {settings}; checked disk only")
        off = set()
    order = list(dict.fromkeys(s for r in routes for s in r.skills))
    for skill in order:
        if skill not in have:
            uses = "; ".join(f"{r.section}: {r.finding}" for r in routes if skill in r.skills)
            lines.append(f"MISSING {skill}: limits {uses}")
        elif skill in off:
            lines.append(f"DISABLED {skill} (skillOverrides in {settings})")
        else:
            lines.append(f"ok {skill}")
    # Called by this path rather than through ui-ux-pro-max's own instructions, which assume a
    # plugin install and resolve to nothing for a user-level one.
    if "ui-ux-pro-max" in have and (have["ui-ux-pro-max"] / "scripts" / "search.py").is_file():
        lines.append("ok ui-ux-pro-max/scripts/search.py")
    else:
        lines.append("MISSING ui-ux-pro-max/scripts/search.py: limits finding a direction")
    code = 0 if all(l.startswith("ok") or l.startswith("warning") for l in lines) else 1
    return lines, code


def main() -> int:
    home = Path.home() / ".claude"
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skills-root", type=Path, default=home / "skills")
    ap.add_argument("--settings", type=Path, default=home / "settings.json")
    args = ap.parse_args()
    lines, code = preflight(ROUTING, args.skills_root, args.settings)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
