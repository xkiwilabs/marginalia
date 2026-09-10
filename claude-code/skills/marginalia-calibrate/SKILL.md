---
name: marginalia-calibrate
description: Verify that the extracted style profile actually reproduces the user's voice. Reconstructs a held-out passage of their own writing from a de-styled skeleton and scores it move-by-move against the real original; optionally contrasts voiced vs generic prose; proposes confirmable style-file edits. Use when the user wants to test, calibrate, or verify their voice profile after extract-style.
---

# marginalia-calibrate

Self-test the extracted voice profile against the author's own writing.

## When to use this skill

Invoke when the user asks to:
- Verify, check, or test their style profile
- Find out whether the profile "sounds like me"
- Calibrate or tune their voice profile after `extract-style`

Do NOT use this skill for:
- Drafting or revising prose (use `marginalia-write`)
- Reviewing an existing draft for AI-drift (use `marginalia-review`)
- Building or refreshing the profile in the first place (use `marginalia-extract-style`)

This is a self-test, not a writing or review tool. It holds out a passage of the
user's own work, reconstructs it blind from a de-styled skeleton plus the profile,
and scores the reconstruction move-by-move against the real original — then proposes
confirmable edits to close the loop.

## How to invoke

Typically via `/marginalia calibrate [--genre=papers|grants|devdocs|business|other|<slug>] [--contrast] [--both]`.

Defaults: `--genre=papers`, reconstruct mode (no `--contrast`/`--both`).

## Protocol

0. Read `content/paths.md` and resolve `<STYLES_DIR>` and `<CORPUS_DIR>`. Every `content/styles/…` and `examples/…` path below is a name, not a location.
1. Read `content/calibration-protocol.md` from the marginalia repo and follow it in order.
2. Never write a style file without showing the diff and getting explicit per-edit confirmation.

All operational detail — passage selection, leakage guard, skeleton construction,
subagent prompts, rubric derivation, and the feedback loop — lives in that protocol.

## Output

- A report at `.marginalia/calibrate-<YYYY-MM-DD-HHMM>.md` (gitignored): the move-by-move
  rubric, the texts (reconstruction vs. original, or the three-way read), the
  weakest-move analysis, and any proposed edits marked applied or skipped.
- Suggested next step: apply the proposed style-file edits, then re-run calibrate on the
  same held-out passage to confirm a `✗`/`~` move has moved toward `✓`.
