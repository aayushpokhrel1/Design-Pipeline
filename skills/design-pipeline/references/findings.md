# Findings format

Every critique in the pipeline ends as one table in this format, whoever produced it. Keep the
field names fixed: a later version runs the critics as parallel subagents that each write rows in
this format, and only the producer changes.

| id | layer | finding | evidence | severity | fix-with |
| --- | --- | --- | --- | --- | --- |
| F1 | feel | Opening a recipe from its card swaps the whole screen with no link between them | `/recipes`, seen in the browser: tap card, instant cut to `/recipes/42` | high | `choreograph` |

- **id**: `L1`, `L2`... for look, `F1`... for feel, `R1`... for robustness.
- **layer**: `look` (layout, hierarchy, type, colour, copy, accessibility), `feel` (transitions,
  continuity, motion, gestures, interaction states) or `robustness` (breaks on real data, on a
  phone, on a slow device).
- **finding**: what is wrong, in the user's terms, one sentence.
- **evidence**: a `file:line`, a route plus what was seen in the running page, or a screenshot
  path. A finding without evidence is an opinion; leave it out.
- **severity**: `high` (breaks use or the project's identity), `medium` (noticeably off), `low`
  (polish).
- **fix-with**: a token copied from a Fix row in `routing.md`. When no row fits, write `none` and
  raise it with the user. Never drop it silently.
