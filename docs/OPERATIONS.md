# Operations

## Install

`bash scripts/install.sh` (Git Bash, Linux, macOS) or `./scripts/install.ps1` (PowerShell) links
`skills/design-pipeline/` into `~/.claude/skills/design-pipeline/`, so a `git pull` updates the
installed skill in place. PowerShell uses a directory junction, which needs no admin rights. Bash
uses `ln -s` and falls back to a copy, which then needs a re-run after each pull. An existing real
directory is moved to `~/.claude/.backups/`, never left inside `skills/`, where it would be read as
a second skill. Both installers end by running the preflight.

There is no `commands/` file: an invoke-only user skill is already `/design-pipeline`.

## Use

In Claude Code, from the project you want to upgrade:

```
/design-pipeline
```

## Verify

```bash
python -m unittest discover -s tests -v   # preflight and check script
python scripts/check.py                   # routing.md vs ~/.claude/skills, skill rules
bash tests/test-install.sh                # installer, sandboxed
./tests/test-install.ps1                  # PowerShell installer, sandboxed
```

`scripts/check.py` fails when `routing.md` names a skill or impeccable command that does not
exist, when anything under `skills/` hardcodes a home directory, or when `SKILL.md` loses
`disable-model-invocation: true`. CI (`.github/workflows/ci.yml`, Linux and Windows) runs all of
the above, with `check.py --skills-root upstream` against shallow clones of the three upstream
repos, so an upstream rename turns CI red.

## Preflight

```bash
python "$HOME/.claude/skills/design-pipeline/scripts/preflight.py"
```

It lives inside the skill, not in repo `scripts/`, because only the skill folder is installed. It
reads its dependency list from `skills/design-pipeline/references/routing.md`, the only list of
skills the pipeline calls. Adding a row there is all it takes for both the preflight and the
check script to cover a new dependency.

## Dependencies

All are user-level skills in `~/.claude/skills/`. The exact set is whatever `routing.md` names:

| Skill | Source | Used for |
| --- | --- | --- |
| impeccable | github.com/pbakaus/impeccable | The look: critique, direction, layout, type, colour, `DESIGN.md` |
| Emil Kowalski's skills | github.com/emilkowalski/skills | The feel: `review-animations`, `improve-animations`, `apple-design`, `animate`, `choreograph`, `gestures`, `emil-design-eng`, `mobile-native`, `break-ui` |
| ui-ux-pro-max | github.com/nextlevelbuilder/ui-ux-pro-max-skill | The reference database, through `scripts/search.py` |

## Environment traps

- **`skillOverrides` can silently switch an installed skill off.** An entry `"<name>": "off"` in
  `~/.claude/settings.json` hides the skill from every session. Ten design skills sat installed and
  invisible for three months that way. The preflight reports these as `DISABLED`.
- **ui-ux-pro-max's `SKILL.md` assumes a plugin install.** Upstream calls
  `${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max/scripts/search.py`, which resolves to nothing
  for a user-level install. The pipeline calls `$HOME/.claude/skills/ui-ux-pro-max/scripts/search.py`
  itself rather than trusting ui-ux-pro-max's own instructions.
- **Upstream impeccable contains decoy copies of itself**: one per harness (`.claude/`,
  `.cursor/`...) and test fixtures under `tests/oracle/` named `impeccable` without a `reference/`
  folder. Skill discovery takes the shallowest `SKILL.md` per name for that reason.
- **On Windows `python3` is the Microsoft Store stub.** Call `python`.
- **This checkout converts line endings to CRLF**; `.gitattributes` keeps `*.sh` LF, or bash breaks.
- **Several of Emil's skills are invoke-only** (`review-animations`, `prototype`, `pick-ui-library`,
  `learn-taste`). Claude Code hides them from the model, and a Skill call for one fails, so naming
  them is not enough. `SKILL.md` tells the conductor to Read such a skill's `SKILL.md` and follow it.
  The preflight still reports them `ok`, because being installed is all it checks.
- **From Python 3.13, `Path.rglob` does not follow directory symlinks.** Skill discovery uses
  `os.walk(followlinks=True)`, or symlinked skills on macOS and Linux read as missing.
- **PowerShell 5.1 writes `settings.json` with a BOM.** The preflight reads it as `utf-8-sig`.
