---
name: marginalia-extract-style
description: Bootstrap or refresh the user's per-genre style guides by analyzing their own published papers/grants in examples/. Produces content/styles/base.md and content/styles/{genre}.md. Use when the user wants to (re)build their style profile from their own work, typically after dropping new examples into examples/.
---

# marginalia-extract-style

Derive style guides from the user's own corpus.

## When to use this skill

Invoke when the user asks to:
- Extract, derive, build, or refresh their style guide
- Analyze their published papers / grants to define their voice
- Initialize marginalia with their corpus

Do NOT use this skill for:
- Reviewing a draft (use `marginalia-review`)
- Verifying citations (use `marginalia-verify-cites`)

This is a bootstrap-and-occasional-refresh operation — it reads multiple full documents and is expensive. Run it once per genre after adding examples, then occasionally to refresh.

## How to invoke

Typically via `/marginalia extract-style [--genre=papers|grants|devdocs|business|other|<slug>|all] [--mode=init|refresh|update]`.

Defaults: `--genre=all --mode=init` (or `refresh` if style files already exist).

## Protocol

0. Read `content/paths.md` and resolve `<STYLES_DIR>` and `<CORPUS_DIR>`. Every `content/styles/…` and `examples/…` path below is a name, not a location.
1. Read `content/extraction-protocol.md` from the marginalia repo.
2. For each target genre (or all), list files in `examples/{genre}/`.
3. If no files found for a genre, skip with a note (do not error).
4. Follow the protocol: per-document extraction → cross-document synthesis → write style files.
5. Before overwriting an existing style file, show the diff and ask the user to confirm.
6. Preserve the `## Manual overrides` section of any existing style file across re-runs.

## Sparse corpus

If a genre has 1–2 examples, extract anyway and mark the output `confidence: low | N=k` in the frontmatter. Note in the user-facing summary that more examples would strengthen the profile.

## Output

After running, summarize for the user:
- Which style files were written/updated
- Confidence level for each (`high | N>=3` vs `low | N<3`)
- Any genres skipped for lack of examples
- Suggested next step: "Review the style files at content/styles/ — they're meant to be editable. Then run `/marginalia review <doc>` to use them."
