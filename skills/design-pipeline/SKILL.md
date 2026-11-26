---
name: design-pipeline
description: Critique an existing frontend's look and feel, recommend how far to go, and fix it by running the installed design skills (impeccable, Emil Kowalski's skills, ui-ux-pro-max). Invoke only with /design-pipeline.
disable-model-invocation: true
---

# Design Pipeline

You are the conductor. You decide **what** to fix, **in what order**, and **with which skill**. You
hold no design knowledge of your own: every rule, palette, curve and recipe lives in the skills you
call. Do not restate their content here or in your output; run them.

Two files beside this one are part of the skill:

- `references/routing.md`: every skill you call, by phase (Critique, Fix, Check). It is the only
  list. Use the skill a row names; do not pick another from memory.
- `references/findings.md`: the one format every critique result is merged into.

How to call them:

- **Emil's skills** (`review-animations`, `improve-animations`, `apple-design`, `animate`,
  `choreograph`, `gestures`, `emil-design-eng`, `mobile-native`, `break-ui`): invoke by name with a
  concrete target and question. Several greet and wait when called with no question; always give
  them one. Some are invoke-only (`disable-model-invocation: true`, `review-animations` among
  them): those are hidden from you and a Skill call for one fails. For any skill you cannot
  invoke, Read `$HOME/.claude/skills/<name>/SKILL.md` and follow it as written. Never skip its
  routing row or substitute another skill.
- **impeccable**: follow its own `SKILL.md` setup, which runs its `scripts/impeccable context`
  launcher (`impeccable.cmd` on a Windows shell without `sh`), then the command a routing row
  names (`critique`, `layout`, `shape`, `document`...).
- **ui-ux-pro-max**: run its search script directly,
  `python "$HOME/.claude/skills/ui-ux-pro-max/scripts/search.py" "<query>" --domain <domain>`.
  Do not follow the `${CLAUDE_PLUGIN_ROOT}` path in its own instructions; for a user-level install
  it resolves to nothing. Use `python`, not `python3`.

## The rules that make this the pipeline

1. **No edit to the project's code or design before the user approves the fix list** (step 5).
   Steps 0 to 4 read, run and ask. Tooling files are fine: a `.claude/launch.json` entry to run the
   page, and the critique snapshots impeccable keeps in `.impeccable/`.
2. **Never replace a project's identity unless the user asked.** Overhaul is never automatic, and
   in keep-the-direction mode you never recommend it unless the user asked for a new identity.
3. **In keep-the-direction mode, never propose new colours or fonts**, from ui-ux-pro-max or
   anywhere else. Its styles, palettes and font pairings are for finding a direction only.
4. **Ask about the project, never "which skill do you want?"** Choosing skills is your job.
5. **Leave a `DESIGN.md` behind** (step 8), in impeccable's format.

## Step 0: Preflight

```bash
python "$HOME/.claude/skills/design-pipeline/scripts/preflight.py"
```

Report every line that is not `ok`. A `MISSING` or `DISABLED` line names the phases it limits:
carry on with the rest and say what you could not do. `DISABLED` means an entry in `skillOverrides`
in `~/.claude/settings.json` switches the skill off; tell the user that is the fix.

## Step 1: Read the project

Find the stack, the pages or routes, how to run it, and whether a design system exists:
`DESIGN.md`, a tokens file, a theme file, CSS custom properties used as tokens. Then state the mode
and why:

- **Keep the direction**: a design system exists. Its rules are what step 3 protects.
- **Find a direction**: none exists, or what exists is a framework default nobody chose.

## Step 2: Critique

Run every Critique row in `routing.md` against the project's main routes, sending each critic the
question `routing.md` gives for it.

**Run impeccable's critique the way it specifies: its two assessments in two isolated subagents.**
Do not fold them into one context to save tokens, even where the user's own instructions favour
fewer subagents; that is a decided exception, because the critique is the input every later step
rests on. Its single-context "degraded" run is only for a harness with no subagent tool, and then
it carries impeccable's banner.

**Judge feel from the running page**, not only from code or a still screenshot. Start it for the
built-in browser:

- a static folder: `python -m http.server <port>` in the background, from that folder;
- a `package.json` with a `dev` script: add an entry to the project's `.claude/launch.json` and
  open it with `preview_start`;
- anything else: ask the user how they run it.

**Make the browser pane visible before judging any motion.** A hidden pane runs the page as a
background tab, which throttles `requestAnimationFrame`, IntersectionObserver and View
Transitions: animations stall, screenshots show nothing moving, and timing loops time out. If
the browser's tab listing says the pane is hidden, show it first.

Click through the main flows in the browser (open an item, go back, open a menu or sheet, submit a
form) and note every hard cut, jump and dead moment. If the page cannot run, say plainly that feel
was judged from code only.

When a called skill ends by asking the user what to do next, its question belongs to this
pipeline, which asks in step 3.

Merge everything into **one** findings table in the format of `references/findings.md`, with
duplicates folded together. Show it to the user, grouped by layer, highest severity first.

## Step 3: Ask

Ask one question at a time, and wait for each answer:

1. What should someone feel in the first ten seconds of using it? Three words is enough.
2. What must not change? In keep-the-direction mode, list `DESIGN.md`'s rules (or the tokens you
   found) as the protected list and ask what to add to it.
3. Who uses it most, and on what device?

Skip a question the project already answers (a `PRODUCT.md` that names the audience, say), and say
that you skipped it and why.

## Step 4: Recommend a level

Recommend one level with reasons drawn from the findings and the answers. The user picks.

| Level | When | What changes |
| --- | --- | --- |
| Polish | The system is good, the execution is off | Code only, `DESIGN.md` kept |
| Refresh | The system has gaps or weak sections (no motion rules, a weak type scale) | `DESIGN.md` gains or sharpens sections, then the code follows |
| Overhaul | Really bad or generic | New direction, `DESIGN.md` rewritten, applied across the pages |

In find-a-direction mode, an Overhaul or Refresh starts from a direction: run the `no direction`
Fix row (impeccable's `shape`, with ui-ux-pro-max searches for candidate styles, palettes and font
pairings) and let the user choose before step 5.

## Step 5: Plan, and wait for approval

Write an ordered fix list. Each item names the findings it closes and its `fix-with` skill.
**Look and structure come before motion**: motion tuned on a layout that then changes is wasted.
Findings marked `none` go at the end as open questions.

Stop here. **Do not edit anything until the user approves the list.** They may drop or reorder
items; the approved list is the contract for step 6.

## Step 6: Apply

Run each approved item's skill on its target, in order. Respect the protected list from step 3.
After each item, check the page still runs before starting the next.

**Reload past the cache after every item.** A static server such as `python -m http.server` lets
the browser keep serving old CSS and JS, so a check can pass or fail against files you already
changed. In the page, `fetch` each changed asset with `{cache: 'reload'}`, then reload, and
confirm the change is in what the browser now has before judging it.

Mechanical follow-through on an approved item, such as renaming a token across many files, may go
to the delegation pipeline when `$HOME/.claude/bin/delegate` exists. Design judgment stays here.

## Step 7: Check

Run every Check row in `routing.md` on what changed, except the `DESIGN.md` row, which is step 8:
`break-ui` on the changed components, a second critique pass on the changed routes. Take before and
after screenshots of each changed route in the browser.

`break-ui` expects a data boundary and a dev-only fixture toggle. A static site has neither: there,
feed the worst-case values straight into the rendered page in the browser (long names, wrapping
labels, missing images) at a 320px viewport, and add no toggle to the project. Those edits live in
the browser only. Fix what the check finds in the same
scope, or report it; do not widen the scope without asking.

## Step 8: DESIGN.md

impeccable owns the format of `DESIGN.md`. Do not invent a second one.

Before writing it, run `git check-ignore -q DESIGN.md` in the project. If it is ignored, tell the
user: a `DESIGN.md` nobody else can see does not keep the direction for the next run. Ask whether
to un-ignore it; do not edit `.gitignore` on your own.

Give impeccable the step 3 answers, and the protected list, as already answered, so its own
questions skip what the user has said once. Ask only what is still open.

- **Find a direction**: have impeccable's `document` command create it from the finished build.
- **Refresh or Overhaul**: have impeccable update the sections that changed. Motion rules from
  Emil's skills go in as a section, in impeccable's format.
- **Polish**: leave it untouched.

## Finish

Report: the level chosen, what was fixed (by finding id), the before and after screenshots, what
the check found, anything preflight said you could not do, and the findings left open. Stop any
server you started for the browser pass.
