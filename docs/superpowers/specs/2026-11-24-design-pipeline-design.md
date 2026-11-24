# Design Pipeline: design

Status: approved by Aayush on 2026-11-24.
Built as v1 (approach A) on 2026-11-24; not yet judged on a real project (see Done when).

## Intent

One invoke-only skill, `/design-pipeline`, upgrades the frontend of a project the user has already
built. It critiques how the project looks and how it feels to use, asks the user about the project,
recommends how far to go, and fixes it by running the specialist design skills that are already
installed. It is a conductor: it decides *what* to fix, *in what order*, and *with which skill*,
and it holds no design knowledge of its own.

## Why

There are about 25 design skills installed (impeccable, Emil Kowalski's 19, ui-ux-pro-max), and
choosing between them by hand is the problem. Two real projects are behind it:

- **Portfolio** looks generic. It has no visual identity and no `DESIGN.md`.
- **EnamelVault** looks right but feels mechanical. Every change is a hard cut: tap a recipe card
  and the whole screen is swapped for the recipe page, with nothing connecting the two. Partly,
  too, everything happens one step at a time: opening anything takes over the screen, so you can't
  glance at one thing while doing another. The user wants it to feel organic and continuous.

## Goals

- Critique both layers: **look** (layout, hierarchy, type, colour, copy, accessibility) and **feel**
  (transitions, continuity, motion, gestures, interaction states).
- Judge feel from the running page, not only from code or a still screenshot.
- Tell a project that needs a direction (Portfolio) from one whose direction must be kept
  (EnamelVault), and behave differently for each.
- Ask questions about the project, never "which skill do you want?".
- Leave a `DESIGN.md` in the project after every run.

## Non-goals

- Building pages from a brief. The user builds the page.
- Holding design content: rules, palettes or recipes live in the skills it calls.
- Backend or non-UI work.

## Anti-goals (failure even if it technically works)

- Editing code before the user approves the fix list.
- Replacing a project's identity without being asked. An Overhaul is never automatic.
- Triggering on its own and competing with impeccable for ordinary requests.
- Copying content out of the skills it calls. Two copies drift.
- On a project with a design system, suggesting a new palette or fonts from the database. That
  fights the system it should respect.

## Constraints

- A Claude Code **user-level skill** in `~/.claude/skills/design-pipeline/`, linked from this repo
  so a `git pull` updates it. Not a plugin: a plugin would list it a second time under a namespace.
- `disable-model-invocation: true` in the frontmatter.
- **Nothing hardcodes a machine path.** Reference skills by name, and the ui-ux-pro-max script as
  `$HOME/.claude/skills/ui-ux-pro-max/scripts/search.py`.
- Depends on installed skills: impeccable; Emil's `review-animations`, `improve-animations`,
  `apple-design`, `animate`, `choreograph`, `gestures`, `break-ui`, `mobile-native` and
  `emil-design-eng`; and ui-ux-pro-max. Several of Emil's are invoke-only, so the pipeline runs
  them as commands.
- Windows is a first-class platform: call `python`, not `python3` (on this machine `python3` is
  the Microsoft Store stub).
- The repo is public.

## Approaches

| | Approach | Trade-off | Decision |
| --- | --- | --- | --- |
| **A** | **One conductor skill.** A single `SKILL.md` runs every phase in one conversation, calling the installed skills by name, with a routing table, a preflight check and an installer | Thin, and stays current as upstream skills improve. Depends on those skills, and a big app's critique fills one context | **Chosen** |
| B | Conductor plus three parallel critic subagents (look, feel, robustness) whose findings are merged | Deeper, faster critique and a clean main context, at about three times the critique token cost per run | **Deferred.** The upgrade path and its triggers are in `PRODUCT.md`, Roadmap |
| C | One bundled skill containing copies of the others' content | Works without dependencies, but goes stale and competes with the originals | **Rejected** |

A was chosen to start cheap and learn whether B is needed. The user noted that weekly Claude usage
isn't maxed out thanks to the delegation pipeline, so B's cost is not the blocker. Waiting to see
the need is.

## The run (decided)

0. **Preflight.** Check that the skills it depends on are installed and enabled (an entry in
   `skillOverrides` in `~/.claude/settings.json` can switch an installed skill off silently).
   Report anything missing, and say which phases it limits instead of failing outright.
1. **Read the project.** Find the stack, the pages or routes, how to run it, and whether a design
   system exists (`DESIGN.md`, tokens, a theme file). The answer sets the mode: **find a
   direction** or **keep the direction**.
2. **Critique.** Run the existing skills' review modes: impeccable's critique for the look;
   `improve-animations`, `review-animations` and `apple-design` for the feel. Open the page in a
   browser where it can run (the built-in browser), so transitions are judged in motion. Collect
   the results as **one list of findings** in a shared format: finding, evidence, severity, layer
   (look, feel or robustness) and the skill that would fix it. Approach B only changes who produces
   this list, so keep the format stable.
3. **Ask** the user a few questions about the project. These cover what it should make people feel,
   what must be kept, and how far to go. In keep-the-direction mode, the protected parts are
   `DESIGN.md`'s rules.
4. **Recommend a level** with reasons, and the user picks:

   | Level | When | What changes |
   | --- | --- | --- |
   | Polish | The system is good, the execution is off | Code only, `DESIGN.md` kept |
   | Refresh | The system has gaps or weak sections (no motion rules, a weak type scale) | `DESIGN.md` gains or sharpens sections, then the code follows |
   | Overhaul | Really bad or generic | New direction, `DESIGN.md` rewritten, applied across the pages |

5. **Plan.** An ordered fix list, each item naming its skill. Look and structure come before motion,
   because motion tuned on a layout that then changes is wasted. **The user approves the list before
   any edit.**
6. **Apply** each approved item by running its skill.
7. **Check** the result: `break-ui` on the changed components, a second critique pass on what
   changed, and before and after screenshots.
8. **Write `DESIGN.md`**: create it in find-a-direction mode, update its sections on a Refresh or an
   Overhaul, and leave it untouched on a pure Polish. **impeccable owns the file's format.** Its
   context command already loads the project's `PRODUCT.md` and `DESIGN.md`, and it ships a
   documenter that records `DESIGN.md` from a finished build. So the pipeline has impeccable write
   or update the file rather than inventing a second format that would fight it. Motion rules from
   Emil's skills go into that file as a section, in impeccable's format.

The ui-ux-pro-max database is used where it helps: candidate styles, palettes and font pairings
when finding a direction, and UX guidelines and stack notes in both modes. It is never used to
propose new colours or fonts in keep-the-direction mode.

## Repo layout (decided in outline)

- `skills/design-pipeline/SKILL.md`: the conductor.
- `skills/design-pipeline/references/routing.md`: finding to skill. Starting rows:
  - hard cut between views: `choreograph`, `animate`
  - a drag, swipe or sheet that doesn't track the finger: `gestures`
  - motion that can't be interrupted, or feels non-physical: `apple-design`
  - press, hover and transition details: `emil-design-eng`
  - feels wrong on a phone: `mobile-native`
  - breaks on real data: `break-ui`
  - generic look, weak hierarchy, type or colour: impeccable
  - no direction: impeccable plus the ui-ux-pro-max search
- `skills/design-pipeline/scripts/preflight.py`: the dependency check from step 0. Inside the
  skill, not repo `scripts/`, because only the skill folder is installed.
- `scripts/install.sh` and `scripts/install.ps1`: link the skill into `~/.claude/skills/`. Mirror
  `scripts/install-scaffold.{sh,ps1}` in Knowledge-Pipeline, including its rule that sourcing the
  installer has no side effects, so it can be tested in a sandbox.
- A check script and CI that fail when `routing.md` names a skill that doesn't exist upstream.

## Left to the builder

- The exact questions in step 3, and how many (a few, asked one at a time).
- Which impeccable command names to call. Read impeccable's `SKILL.md` rather than assuming them.
  It runs through its own launcher (`scripts/impeccable context`, with `impeccable.cmd` on a Windows
  shell without `sh`) and reads the target project's `PRODUCT.md` and `DESIGN.md`.
- How to start each kind of project for the browser pass (a static folder, Vite's dev server).
- The findings format's field names.
- Whether mechanical follow-through on an approved item (say, renaming a token across forty files)
  goes to the delegation pipeline. Design judgment stays in-session.

## Done when

- `/design-pipeline` on **Portfolio** produces a critique, recommends Overhaul (or explains why
  not), and once approved, leaves the site with a distinct direction and a new `DESIGN.md`.
- `/design-pipeline` on **EnamelVault** keeps its design system intact, and, once approved, replaces
  at least the main hard cuts (opening a recipe from a card, among others) with continuous
  transitions, plus updates `DESIGN.md`'s motion section.
- Aayush judges both by using them.
