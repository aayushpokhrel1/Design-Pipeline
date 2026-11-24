# Working in this repo

`design-pipeline` is a Claude Code user-level skill that critiques a frontend's look and feel and
then fixes it by running installed design skills (impeccable, Emil Kowalski's skills, the
ui-ux-pro-max database). The design is in `docs/superpowers/specs/2026-11-24-design-pipeline-design.md`.

## Where things are written down

| File | What it holds |
| --- | --- |
| `README.md` | What it is, what it does, how to use it. The repo is public, so this is the product |
| `PRODUCT.md` | **Gitignored** (public repo). Who it is for, decisions, roadmap (including the deferred parallel-critics upgrade, approach B), what was declined and why. The canonical copy is in the vault at `Projects/Design-Pipeline/PRODUCT.md` |
| `CLAUDE.md` | This file. Auto-loaded every session |
| `HANDOVER.md` | **Gitignored.** Current state only |
| `docs/OPERATIONS.md` | Install, verify, dependencies, environment traps |
| `docs/superpowers/specs/` | The design of one feature, written before building it. `YYYY-MM-DD-<feature>.md`. Tracked |
| `docs/superpowers/plans/` | **Gitignored** (public repo). Task breakdowns. Canonical copies go in the vault |
| a **code comment at the site** | A rule about specific code |
| the **Obsidian vault** | A lesson that would change how I work on a *different* project |
| nowhere | A dated narrative of what you did today. `git log` already holds it, in more detail |

There is deliberately **no `DESIGN.md` in this repo**: the skill has no UI of its own. The skill
*writes* a `DESIGN.md` into the projects it runs on, which is a different thing. Don't create one
here.

## The handover

`HANDOVER.md` is gitignored and lives on this machine only, so nothing durable may go in it. Before
adding a line, ask whether it will still be true in a month. If yes, it belongs in a permanent doc
or the vault. On FamilyRecipes the handover reached 1,365 lines, contradicted itself, and caused
real wrong work.

## Where knowledge goes

A lesson has exactly one home, chosen by how far it reaches:

- **A rule about specific code goes in a comment AT that code.** The most reliable form by a
  distance: you cannot edit the function without reading the warning above it.
- **A lesson that generalises goes in the vault**, phrased so it is useful on another project, with
  this one as the example.
- **Neither means it was not a lesson.**

**Do not create a `LESSONS.md`.** It was tried on FamilyRecipes on 2026-09-27 and deleted the same
day: every entry was already a third copy. Prefer a mechanical defence (a failing test, a CI job, a
grep, an unavoidable comment) over a written one. The failure mode is not ignorance, it is not
re-reading.

## When Aayush says "update"

"Update the docs", "update everything" or just "update" means **all of it, in this turn**:

1. **The vault**, `C:\Users\aayus\Documents\Knowledge-Vault\Projects\Design-Pipeline\`. Add what this
   session learned that is worth keeping. This is the part that gets forgotten, and the part that
   compounds. Write the note to a file, then append it with:

   ```bash
   python ~/.claude/bin/vault-note.py Design-Pipeline <scratchpad>/note.md
   ```

   Note content must never reach a command line, because a shell executes the backticks in it.
   Keep the vault's `PRODUCT.md` in step with the local one.
2. **Every doc in this repo**, not only the one already open.
3. **The handover**, current-state numbers only.

**Updating docs means making them TRUE, not just appending what shipped.** Correct or strike a stale
claim where it sits, and cross-check every number against reality rather than trusting the file.

## Project rules

- **Verify:** `python -m unittest discover -s tests -v`, `python scripts/check.py`,
  `bash tests/test-install.sh` and `./tests/test-install.ps1`. CI runs them all on Linux and
  Windows, with the routing check against upstream. The skill's run itself has no mechanical
  test: say so when a change touches `SKILL.md`'s behaviour.
- **`references/routing.md` is the only list of skills the pipeline calls.** Add a dependency
  there, never as a second list in `SKILL.md` or a script.
- **Never copy content out of impeccable, Emil's skills or ui-ux-pro-max.** Call them by name. A
  copy goes stale and competes with the original. That is the decision the whole design rests on.
- **Keep the skill invoke-only** (`disable-model-invocation: true`).
- **Nothing in `skills/` hardcodes a machine path.** Use `$HOME/.claude/skills/...` and skill names.
- On Windows call `python`, not `python3`.

## graphify

This repo has a knowledge graph in `graphify-out/` (gitignored, kept fresh by the global post-commit
hook). For codebase questions run `graphify query "<question>"`, `graphify path "A" "B"` or
`graphify explain "X"` before grep. There is no `GRAPH_REPORT.md` (it needs a separate
`graphify cluster-only .`); the graph alone is enough for query, path and explain.
