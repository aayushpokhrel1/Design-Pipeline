# Design Pipeline

One command that upgrades a frontend you already built. `/design-pipeline` reads your project,
critiques how it **looks** and how it **feels to use**, asks you a few questions about the
project, recommends how far to go, and then fixes it with the design skills best suited to each
problem.

It doesn't hold design knowledge of its own. It runs specialist skills you already have installed,
in the right order:

| Layer | Skill | What it covers |
| --- | --- | --- |
| How it looks | [impeccable](https://github.com/pbakaus/impeccable) | Layout, hierarchy, type, colour, copy, accessibility, design direction |
| How it moves and feels | [Emil Kowalski's skills](https://github.com/emilkowalski/skills) | Animation, choreography, gestures, sheets, interaction polish, edge cases |
| Reference data | [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | A searchable local database of styles, palettes, font pairings, UX guidelines and stack notes |

## Status

Design stage. The design is in
[`docs/superpowers/specs/2026-11-24-design-pipeline-design.md`](docs/superpowers/specs/2026-11-24-design-pipeline-design.md).
Nothing is installable yet.

## How a run goes

1. **Read** the project: its stack, and whether it already has a design system (`DESIGN.md`,
   tokens).
2. **Critique** the look and the feel, in a real browser where possible, so transitions and
   motion get judged, not just screenshots.
3. **Ask** a few questions about the project: what it should make people feel, what to protect,
   how far to go.
4. **Recommend a level**, which you pick:
   - **Polish**: fix the execution and keep `DESIGN.md`.
   - **Refresh**: sharpen `DESIGN.md`'s weak sections, then fix the code.
   - **Overhaul**: a new direction and a rewritten `DESIGN.md`, applied across the pages. Never
     automatic.
5. **Plan**: an ordered list of fixes and the skill behind each one. Nothing is edited until you
   approve it.
6. **Apply** the fixes, structure first and motion second, then check the result.
7. **Leave a `DESIGN.md` behind**, so the next run (or any other session) keeps the direction.

## What it is not

- It doesn't build pages from a brief. You build the page, it makes it look and feel right.
- It doesn't bundle or copy the skills it uses. Copies go stale, and they would compete with the
  originals.
- It never triggers on its own. You invoke it, so it never competes with impeccable for an
  ordinary "review my UI" request.

## Requirements

[Claude Code](https://claude.com/claude-code), with impeccable, Emil Kowalski's skills and
ui-ux-pro-max installed as user-level skills, and Python for the ui-ux-pro-max search script.
