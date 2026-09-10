---
genre: <papers | grants | devdocs | business | other | your-own-slug>
extracted_at: <ISO 8601 timestamp, written by extract-style>
example_count: <N documents this was derived from>
confidence: <high | low> | N=<N>
---

# <Genre> style (extracted from <N> documents)

**This file is a template, not a profile.** It shows the schema
`marginalia-extract-style` writes and the other skills read. You do not fill it
in by hand: put your own published work in your corpus directory and run
`/marginalia extract-style --genre=all`, which writes real files beside this one.

Delete nothing here. `extract-style` ignores `template.md`.

Everything below describes what each section is for and what a useful entry
looks like. The rules are illustrative, and deliberately not anyone's actual
voice.

## Sentence

Measured sentence-level habits. Length distribution, clause density, punctuation
that is genuinely characteristic. Written as constraints a reviewer can check,
not as statistics.

- Median sentence length ~N words; the dominant bucket is X–Y words.
- Whether long clause-dense sentences are the baseline (do not flag) or unusual.
- Per-mark rules where the corpus supports one, e.g. an em-dash target.

## Lexicon — preferred

Words and constructions the corpus shows this author reaching for. Used by
`marginalia-write` as generation targets, and by `review` to notice absence.

## Signature phrasings

Slotted phrasings lifted from the corpus, with the variable part marked, e.g.
`X does not merely Y; it Zs`. These are write-side few-shot targets. `review`
Dimension C ignores this section, so nothing here becomes a drift rule.

## Lexicon — avoid (AI defaults absent from this corpus)

Negative space, and the load-bearing part of the file. Constructions from the
AI-drift catalogue that do **not** appear in the corpus. Because they are absent
from real writing by this author, a single occurrence in a draft is evidence.

### Carve-out — genuine habits, do NOT flag on single use

The exceptions: entries on the AI-drift list that this author genuinely uses.
Without this section, review flags real voice as drift. Every profile needs one.

### Contrast-frame family — measured per-surface split

Per-surface rates for the contrast-frame family, so a surface the author really
uses is judged on rate while a surface absent from the corpus is flaggable on
occurrence. Populated from `contrast_by_surface` in `baselines.json`.

## Hedging

How claims are qualified. Which hedges appear, at what density, and where.

## Citation integration

How sources enter a sentence: parenthetical, narrative, grouped, and the usual
density.

## Paragraph architecture

Typical paragraph length, where the claim sits, how the argument is carried.

## Argumentative moves

Recurring rhetorical structures: how a problem is set up, how an objection is
handled, how a section closes.

## Exemplars

Verbatim passages from the corpus, used by `marginalia-write` as few-shot voice
targets under an imitate-the-shape-never-the-content guard. `review` ignores
this section.

**These are the reason a profile is private.** They are literal extracts of the
author's writing, including unpublished work, which is why profiles live outside
the repo. See `content/paths.md`.

## Manual overrides

**Yours. Hand-written, and never overwritten by `extract-style --refresh`.**

Anything here outranks every extracted rule above, and `review` treats a match
as HIGH priority. This is where a rule goes when extraction got something wrong,
or when you have decided to write differently from how you used to.

Date each entry and say why, because in six months the reason is the part you
will have forgotten.

- **YYYY-MM-DD — <rule>.** <What to do, and what prompted it.>
