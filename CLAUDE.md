# CLAUDE.md

Guidance for Claude Code working in the marginalia repo. Contributors should
read it too: it is mostly a description of where things live and why.

## What this repo is

marginalia is a writing toolkit for academic prose. It drafts and revises in the
author's own voice, reviews writing for AI-drift and voice loss, and verifies
citations across four tiers (existence, reputability, claim–source match,
better-source suggestions).

It is a critic, not a writer. Reports are annotated. Nothing is ever applied
without a diff and an explicit confirmation.

## The architectural rule

**All operational logic lives in `content/`.** Runtimes are loaders. A `SKILL.md`
should say "read protocol X, then follow it" and little else.

This is what makes the toolkit portable. The current runtime is Claude Code
skills; an MCP server or a CLI would read exactly the same protocol files. If
logic leaks into a runtime, that portability quietly dies.

| To change… | Edit |
|---|---|
| Where profiles and corpus resolve | `content/paths.md` |
| AI-drift lexicon and structural anti-patterns | `content/ai-drift.md` |
| Co-writer logic (voice applied at draft time) | `content/write-protocol.md` |
| Review sweeps: dimensions, scoring, schema | `content/review-protocol.md` |
| The 4-tier citation orchestrator | `content/citation-tiers.md` |
| The prompt each cite sub-agent receives | `content/sub-agent-prompt.md` |
| Style extraction: per-doc then cross-doc synthesis | `content/extraction-protocol.md` |
| Apply-mode classification, diff, confirmation | `content/apply-protocol.md` |
| Voice-fidelity self-test | `content/calibration-protocol.md` |
| Voice-evolution critique | `content/refine-protocol.md` |
| New-format overlay derivation | `content/adapt-protocol.md` |
| Input format support (PDF/docx; `.tex`/`.mdx` read natively) | `content/input-ingestion.md` |
| Surface counting: sentences, punctuation, gloss | `tools/prose_metrics.py` |
| Business-register counters | `tools/business_tells.py` |
| Subcommand routing, `full`, `clean` guards | `claude-code/commands/marginalia.md` |
| Skill entry metadata only | `claude-code/skills/*/SKILL.md` |

### The one exception: `tools/`

`tools/` is deliberately code, not protocol. Everything else in marginalia is a
judgement task, which is what a model executing a prose protocol is good at.
Counting is not.

Be accurate about why this exists. The prose sweep is **not** bad at this when it
works: it has caught colon-substitution failures unaided, enumerated every
offending line, and found voice loss by *subtraction* and claims contradicted by
a table, none of which a counter can do. The tool exists because that performance
is **not guaranteed** across runs. A counter makes the count deterministic and
supplies rates against a corpus baseline, which cannot be estimated by reading.

So: **the tools count and locate; the protocols judge.** Keep new counting rules
in `tools/` and new judgement rules in `content/`. Do not re-implement counting
as prose instructions, and do not re-implement judgement in Python.

## Paths: profiles are not in the repo

Style profiles and the corpus belong to the user. They resolve via
`content/paths.md`: `$MARGINALIA_HOME`, then `~/.marginalia/`, then the repo's
own `content/styles/` and `examples/` as a fallback.

Protocols still write the short form (`content/styles/base.md`). **Those are
names, not locations.** Never hardcode a resolved path in a protocol.

A profile contains verbatim passages of its author's writing, including
unpublished work. That is why it is gitignored and why the recommended home is
outside the checkout. `content/styles/` here holds only `template.md`.

`baselines.json` is likewise personal: it is measured from one corpus and is
actively misleading against another. Never commit one, and never copy one
between users.

## Working norms

- **`content/` is the contract.** Resist embedding logic in a runtime.
- **Skill files stay thin**, roughly 50–90 lines.
- **No silent file writes.** Apply mode requires a diff preview and explicit confirmation, enforced in `content/apply-protocol.md` §5.
- **Reports are annotated, not autocorrected.** The author always decides.
- **Nothing in `content/` should name a specific person.** It is the portable layer, shared by everyone. Write "the author", never a name, and never cite a specific profile's dated overrides: those exist only in one person's file and dangle for everyone else.
- **`.marginalia/` report directories are gitignored.** They accumulate fast.
- **Frequent commits, descriptive messages**, one logical unit each.

## Verifying changes

No CI and no test runner. Smoke tests are manual: run the subcommand against the
fixture and diff against `tests/fixtures/expected/`.

- **Review protocol** → `/marginalia review tests/fixtures/ai-drift-sample.md`. Should detect all 6 planted items (see the fixture header).
- **Citation protocol** → `/marginalia cite tests/fixtures/citations-sample.md`. Should detect all 4 planted issues. The four passing cites are real, Crossref-indexed works, so **a run in which Tier 3 does not execute is a failure, not a pass.**
- **Extract-style** → point your corpus dir at `tests/fixtures/style-extraction-corpus`, run `/marginalia extract-style --genre=papers`, compare to the expected file, then restore. There is no `--corpus` flag on `extract-style`; `--corpus` exists only on `prose_metrics.py`.
- **Apply protocol** → run a review, then `/marginalia apply` on the report. Verify the auto/interactive split is sane and the diff confirmation fires before any write.
- **Calibrate** → `/marginalia calibrate --genre=papers`. Confirm a passage is held out, the sub-agent runs blind, the rubric renders, and the diff fires before any write. Decline, to keep it non-destructive.
- **Refine** → `/marginalia refine --genre=papers --categories=tics,underused`. Confirm suggestions cite corpus evidence and only `## Manual overrides` is written.
- **Adapt** → `/marginalia adapt --to=blog`. Confirm a provisional overlay with the DERIVED banner and the avoid-list carried over verbatim.
- **Tools** → both are standard-library Python 3:
  ```bash
  python3 tools/prose_metrics.py tests/fixtures/ai-drift-sample.md --genre papers --json
  python3 tools/business_tells.py tests/fixtures/ai-drift-sample.md --json
  ```

Cold start is a supported state and worth testing deliberately: with no profile
and no `baselines.json`, review must still run its drift and structural
dimensions, skip the voice comparison with a note, and never invent a profile or
fall back to a generic style guide.

## Installation

```bash
./install.sh              # install or repair the symlinks
./install.sh --uninstall  # remove them
```

Symlinks all seven skills and the `/marginalia` command into `~/.claude/`.
Because they are symlinks, protocol edits take effect immediately. Set
`CLAUDE_HOME` to target a non-default config directory.
