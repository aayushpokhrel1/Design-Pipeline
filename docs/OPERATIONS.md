# Operations

## Install

Not built yet. The plan is `scripts/install.sh` and `scripts/install.ps1`, which link
`skills/design-pipeline/` into `~/.claude/skills/design-pipeline/`, so a `git pull` updates the
installed skill in place.

## Use

In Claude Code, from the project you want to upgrade:

```
/design-pipeline
```

## Verify

No test suite or CI yet. The first plan adds a check script (every skill in the routing table
exists, nothing hardcodes a path, the frontmatter stays invoke-only) and a CI job that runs it.

## Dependencies

All are user-level skills in `~/.claude/skills/`:

| Skill | Source | Used for |
| --- | --- | --- |
| impeccable | github.com/pbakaus/impeccable | The look: critique, direction, layout, type, colour |
| Emil Kowalski's skills | github.com/emilkowalski/skills | The feel: `review-animations`, `improve-animations`, `apple-design`, `animate`, `choreograph`, `gestures`, `emil-design-eng`, `mobile-native`, `break-ui` |
| ui-ux-pro-max | github.com/nextlevelbuilder/ui-ux-pro-max-skill | The reference database, through `scripts/search.py` |

## Environment traps

- **`skillOverrides` can silently switch an installed skill off.** An entry `"<name>": "off"` in
  `~/.claude/settings.json` hides the skill from every session. Ten design skills sat installed and
  invisible for three months that way. The preflight check has to look here, not only on disk.
- **ui-ux-pro-max's `SKILL.md` assumes a plugin install.** Upstream calls
  `${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max/scripts/search.py`, which resolves to nothing
  for a user-level install. The installed copy on Aayush's machine is patched to
  `$HOME/.claude/skills/ui-ux-pro-max/scripts/search.py`, and the patch is lost on every update.
  So the pipeline calls the script by the `$HOME` path itself, rather than trusting ui-ux-pro-max's
  own instructions.
- **On Windows `python3` is the Microsoft Store stub.** Call `python`.
- **Several of Emil's skills are invoke-only** (`review-animations`, `prototype`, `pick-ui-library`,
  `learn-taste`), so the model won't pick them up by itself. The pipeline names them explicitly.
