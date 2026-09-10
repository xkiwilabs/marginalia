---
name: marginalia-refine
description: Critically evaluate the user's own writing voice and propose corpus-grounded, voice-preserving refinements (overused tics, underused strengths, and other dimensions) which the user selects into their style file's Manual overrides. Use when the user wants to improve, evolve, sharpen, or de-repetitate their own style — not to draft, review a document, or build the profile.
---

# marginalia-refine

Critically evaluate the author's own voice and propose corpus-grounded, voice-preserving refinements.

## When to use this skill

Invoke when the user asks to:
- Improve, evolve, or sharpen their own style
- Critique their voice profile and suggest where it could be stronger
- De-repeat or de-tic their writing — cut overused crutches, surface underused strengths

This is a critic-of-the-voice tool: it grounds every suggestion in the author's own
corpus and proposes refinements the user selects into their style file's
`## Manual overrides`. It never silently rewrites the profile.

## Do NOT use this skill for

- Drafting or revising a piece of prose (use `marginalia-write`)
- Reviewing an existing draft for AI-drift (use `marginalia-review`)
- Building or refreshing the profile in the first place (use `marginalia-extract-style`)
- Testing whether the profile reproduces the voice (use `marginalia-calibrate`)

## How to invoke

Typically via `/marginalia refine [--genre=papers|grants|devdocs|business|other|<slug>] [--categories=tics,underused,...|all]`.

Defaults: `--genre=papers`, `--categories=tics,underused`.

## Protocol

0. Read `content/paths.md` and resolve `<STYLES_DIR>` and `<CORPUS_DIR>`. Every `content/styles/…` and `examples/…` path below is a name, not a location.
1. Read `content/refine-protocol.md` from the marginalia repo and follow it in order.
2. Never write a style file without showing the diff and getting explicit per-edit
   confirmation. Refinements land only in the `## Manual overrides` section — no other
   part of the style file is touched.

All operational detail — corpus sampling, category analysis, suggestion generation,
and the confirmation loop — lives in that protocol.

## Output

- A report at `.marginalia/refine-<YYYY-MM-DD-HHMM>.md` (gitignored): the per-category
  analysis, the corpus-grounded suggestions, and which were accepted or skipped.
- Accepted suggestions are written into the style file's `## Manual overrides` section.
