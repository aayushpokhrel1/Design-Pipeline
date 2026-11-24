# Routing

Every skill the pipeline calls, and when. This file is the only list: `scripts/preflight.py` and
the repo's `scripts/check.py` both parse it, so a skill named here is checked on this machine and
against upstream in CI.

Format, which the parser depends on: each `## Section` is a phase (Critique, Fix, Check) followed
by a two-column table `| Finding | Skill |`. The Skill cell holds one or more backticked tokens.
A token's first word is a skill name; in `impeccable <command>` the second word is an impeccable
command. Keep exactly two columns, and keep every skill name in backticks.

## Critique

| Finding | Skill |
| --- | --- |
| look: layout, hierarchy, type, colour, copy, accessibility | `impeccable critique` |
| feel: audit of the existing motion and what is missing | `improve-animations` |
| feel: motion held to a high craft bar | `review-animations` |
| feel: physicality, interruptibility, gestures | `apple-design` |

## Fix

| Finding | Skill |
| --- | --- |
| hard cut between views | `choreograph` `animate` |
| a drag, swipe or sheet that doesn't track the finger | `gestures` |
| motion that can't be interrupted, or feels non-physical | `apple-design` |
| press, hover and transition details | `emil-design-eng` |
| feels wrong on a phone | `mobile-native` |
| breaks on real data | `break-ui` |
| generic look, weak hierarchy or spacing | `impeccable layout` |
| weak type | `impeccable typeset` |
| weak or flat colour | `impeccable colorize` |
| no direction | `impeccable shape` `ui-ux-pro-max` |

## Check

| Finding | Skill |
| --- | --- |
| changed components on worst-case data | `break-ui` |
| a second look pass on what changed | `impeccable critique` |
| record the design system in `DESIGN.md` | `impeccable document` |
