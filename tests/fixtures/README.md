# Test fixtures

Small, hand-crafted documents with known issues used to verify each skill catches what it should.

## Files

- `ai-drift-sample.md` — 3 paragraphs with planted AI-drift (one tricolon, one "delve", one "in recent years" opener, plus AI-drift adjectives and a bulleted summary inside argumentative prose)
- `citations-sample.md` — 5 inline citations + bibliography; one is hallucinated, one has wrong year, one is an orphan reference, one is a claim–source mismatch
- `style-extraction-corpus/` — 2 small fake papers in a deliberately consistent voice (long sentences, em-dashes, parenthetical citations, shared marker phrase)
- `expected/` — paired expected-output files for each fixture

## How to use

After implementing a skill, install via symlink (see repo README), then in a Claude Code session in the marginalia repo:

```
/marginalia review tests/fixtures/ai-drift-sample.md
/marginalia cite tests/fixtures/citations-sample.md
/marginalia extract-style --genre=papers
```

For style extraction, point the `examples/papers/` folder at `tests/fixtures/style-extraction-corpus/` (symlink or temporary copy) so the skill sees only the corpus.

Diff each produced report against the corresponding file under `expected/`. The fixture documents the *minimum* a working skill should catch — the actual skill may catch additional things, which is fine. False negatives on the listed "must catch" items are failures; additional flags are acceptable noise.
