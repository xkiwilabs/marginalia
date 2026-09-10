# Test fixtures

Small, hand-crafted documents with known issues used to verify each skill catches what it should.

## Files

- `ai-drift-sample.md` — 3 paragraphs with **six** planted AI-drift items (enumerated below)
- `citations-sample.md` — 5 inline citations + bibliography; one is hallucinated, one has wrong year, one is an orphan reference, one is a claim–source mismatch
- `style-extraction-corpus/` — 2 small fake papers in a deliberately consistent voice (long sentences, em-dashes, parenthetical citations, shared marker phrase)
- `expected/` — paired expected-output files for each fixture

## The six planted items in `ai-drift-sample.md`

A working review finds all six. Fewer means the protocol is not being executed,
whatever the report looks like. This is the check to run when trying marginalia
on a new model or a new runtime (see `docs/PORTING.md`).

| # | Line | Item | What it is |
|---|---|---|---|
| 1 | 3 | "it is contextual, dynamic, and emergent" | Tricolon |
| 2 | 3 | "we **delve** into the temporal structure" | AI-drift verb |
| 3 | 5 | "**In recent years**, accounts of cognition…" | AI-drift opener |
| 4 | 5 | "made it **crucial** to ask" | AI-drift adjective |
| 5 | 5 | "A **robust** account, on this reading" | AI-drift adjective, booster sense |
| 6 | 7–11 | "Three commitments organize the chapters that follow:" + bullets | Enumerative setup sentence, and bullets replacing argument in running prose |

Additional flags beyond these six are acceptable noise. Missing any of the six is
a failure.

## How to use

After implementing a skill, install via symlink (see repo README), then in a Claude Code session in the marginalia repo:

```
/marginalia review tests/fixtures/ai-drift-sample.md
/marginalia cite tests/fixtures/citations-sample.md
/marginalia extract-style --genre=papers
```

For style extraction, point the `examples/papers/` folder at `tests/fixtures/style-extraction-corpus/` (symlink or temporary copy) so the skill sees only the corpus.

Diff each produced report against the corresponding file under `expected/`. The fixture documents the *minimum* a working skill should catch — the actual skill may catch additional things, which is fine. False negatives on the listed "must catch" items are failures; additional flags are acceptable noise.
