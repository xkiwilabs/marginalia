---
name: marginalia-adapt
description: Derive a provisional style overlay for a format the author has no corpus for (e.g. a new blog) by transforming their base voice for the target register and anchoring it in their own least-formal writing. Output is marked provisional and decays into a real profile via extract-style as real pieces accumulate. Use when the user wants to write in a new format/genre they haven't built a corpus for yet.
---

# marginalia-adapt

Derive a provisional voice overlay for a format the author has no corpus for yet.

## When to use this skill

Invoke when the user asks to:
- Write in a new format or genre they haven't built a corpus for yet
- Adapt their voice to a blog, op-ed, newsletter, talk, or email

This transforms the author's cross-genre invariants (`content/styles/base.md`) for
the target format's register, anchored in their own least-formal existing writing.
The result is a hypothesis about how the author would write in the new format —
explicitly low-confidence and provisional — built to decay into a real profile as
real pieces accumulate.

## Do NOT use this skill for

- A genre that already has a corpus (use `marginalia-extract-style`)
- Drafting or revising prose (use `marginalia-write`)
- Reviewing an existing draft for AI-drift (use `marginalia-review`)

## How to invoke

Typically via `/marginalia adapt --to=<format> [--samples=<paths>] [--from=base]`.

`--to` is the target format — a preset (`blog`, `op-ed`, `newsletter`, `talk`,
`email`) or an arbitrary slug. `--samples` (optional) sharpens the register.
`--from` (optional, default `base`) is the base profile to transform.

## Protocol

0. Read `content/paths.md` and resolve `<STYLES_DIR>` and `<CORPUS_DIR>`. Every `content/styles/…` and `examples/…` path below is a name, not a location.
1. Read `content/adapt-protocol.md` from the marginalia repo and follow it in order.
2. Never write a style file without showing the diff and getting explicit confirmation.
   The output is provisional and low-confidence by construction.

All operational detail — register presets, mining informal anchors, the register
transform, the output schema, and error handling — lives in that protocol.

## Output

- A new `content/styles/{target}.md` overlay, marked DERIVED (provisional, low-confidence).
- Suggested next step: write with `--genre={target}`, then run
  `extract-style --genre={target} --mode=update` once real pieces in the format exist,
  to replace the derived rules with measured ones.
