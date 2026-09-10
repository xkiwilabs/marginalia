# marginalia

A writing toolkit for academic prose. It drafts and revises in **your** voice,
reviews writing for AI-drift, and verifies citations across four tiers.

The premise: the useful comparison is not against a generic style guide, it is
against your own published writing. marginalia learns your voice from work you
have already published, then flags where a draft has drifted away from it.

It is a critic, not a ghostwriter. Reports are annotated. You apply the edits.

## What it does

- **Reviews writing** for AI-default lexicon (delve, crucial, robust), structural tics (tricolons, three-example paragraphs), and drift from your own published voice.
- **Verifies citations** across four tiers: existence and accuracy, venue reputability, claim–source match, better-source suggestions.
- **Drafts in your voice**, using verbatim passages from your corpus as few-shot targets rather than an abstract rulebook.
- **Measures rather than guesses** where a count is what's needed. A deterministic tool counts sentence lengths, punctuation rates and gloss density against baselines from your own corpus; the prose sweep decides which counts matter.
- **Stays out of your way.** No silent writes, ever. Every edit goes through a diff you confirm.

## Requirements

- **Claude Code.** The current runtime is skills plus a slash command.
- **Python 3** on `PATH`. Backs the measurement layer. Standard library only, nothing to install. Without it reviews still run, minus the measured metrics.
- **`pandoc`** — only if your corpus includes `.docx`, `.doc`, `.rtf` or `.odt`. `brew install pandoc`, or your package manager.
- **`pdftotext`** (poppler) — only if your corpus includes `.pdf`. `brew install poppler`, or `apt install poppler-utils`.

## Install

```bash
git clone https://github.com/<owner>/marginalia.git
cd marginalia
./install.sh
```

That symlinks the seven skills and the `/marginalia` command into `~/.claude/`.
Symlinks rather than copies, so edits to the protocols take effect immediately
with no reinstall. `./install.sh --uninstall` removes them, and `CLAUDE_HOME=/path`
targets a non-default Claude config directory.

## Getting started

A fresh install has no profile, so it cannot yet compare anything to your voice.
Reviews still catch AI-drift and structural problems; the voice dimension is
skipped and says so. Building the profile takes four steps and one pass over
your corpus.

**1. Choose where your profile lives.** Recommended:

```bash
mkdir -p ~/.marginalia/examples/{papers,grants,other}
```

marginalia looks in `$MARGINALIA_HOME`, then `~/.marginalia/`, then the repo
itself. Keeping your corpus and profile outside the checkout means you can pull
updates without touching your voice. See `content/paths.md`.

**2. Add your own published work.**

```bash
cp ~/papers/*.pdf  ~/.marginalia/examples/papers/
cp ~/grants/*.docx ~/.marginalia/examples/grants/
```

Published or funded work only. The profile is a description of how you actually
write, so drafts and AI-assisted pieces poison it. Three or more per genre gives
a confident profile; one or two works but is marked low-confidence. Non-Markdown
files are converted automatically on first run.

**3. Extract the profile and measure the baselines.**

```
/marginalia extract-style --genre=all
```
```bash
python3 tools/prose_metrics.py --emit-baseline
```

The first writes `base.md` plus one overlay per genre. The second writes
`baselines.json`, the measured rates that turn a raw count into a finding. Run
both together whenever you add to the corpus.

**4. Check that it actually sounds like you.**

```
/marginalia calibrate --genre=papers
```

This holds out a passage of your own writing, reconstructs it blind from the
profile, and scores the reconstruction against the real thing. If it scores
badly the profile is wrong, and calibrate proposes fixes. Do not skip this: a
profile nobody has tested is a guess.

Then:

```
/marginalia review draft.md --genre=papers
```

## Usage

```
/marginalia write "draft an executive summary for X"
/marginalia review proposal.md --genre=grants
/marginalia cite proposal.md
/marginalia extract-style --genre=all
/marginalia calibrate --genre=papers
/marginalia refine --genre=papers --categories=tics,underused
/marginalia adapt --to=blog
/marginalia full proposal.md
/marginalia apply proposal.md.marginalia/2026-05-15-1142-review.md
/marginalia clean --older-than=30d
```

`marginalia-write` also engages **implicitly**: ask Claude for help drafting or
revising prose in any session and it pulls in your voice profile, no `/marginalia`
prefix needed.

See `claude-code/commands/marginalia.md` for the full command surface.

## Your profile is private

A style profile is not a set of abstract rules. It contains verbatim passages of
your writing, including unpublished work, because that is what makes it able to
reproduce your voice rather than describe it.

So: **profiles are gitignored, and the recommended location is outside the repo
entirely.** `content/styles/` here holds only `template.md`, which documents the
schema. If you fork this repo, check what you are about to push.

The same goes for `baselines.json`. It is measured from one corpus and is
meaningless against another. Copying someone else's would silently compare your
prose to their voice, with nothing on the surface to show it.

## The commands

**`review`** sweeps a draft across five dimensions: AI-drift lexicon, structural
anti-patterns, distance from your profile, citation integration, and measured
surface metrics. Output is an annotated report plus a JSON sidecar.

**`cite`** verifies citations across four tiers, dispatching one sub-agent per
unique citation, capped at 8 concurrent.

**`write`** drafts or revises with your profile as a generation constraint,
using the corpus exemplars as few-shot targets.

**`extract-style`** builds the profile: per-document feature extraction, then
cross-document synthesis. Features stable across genres land in `base.md`;
genre-specific ones land in the overlay.

**`calibrate`** is the self-test above. `--contrast` adds a generic-versus-voiced
read so you can see what the profile is buying you.

**`refine`** critiques the voice itself rather than a draft, proposing
corpus-grounded refinements: overused tics to dial back, underused strengths to
lean into. Every suggestion cites your own corpus. It never measures you against
an external standard, and accepted suggestions land only in `## Manual overrides`.

**`adapt`** derives a *provisional* overlay for a format you have no corpus for
yet, a blog or a newsletter or a talk, by transforming your base voice for the
target register. Marked DERIVED and low-confidence, it decays into a real profile
via `extract-style` as real pieces accumulate.

**`apply`** stages a report's edits as a diff against the source. **`full`** runs
review and cite in parallel and merges them. **`clean`** deletes old reports.

### Genres

`papers`, `grants` and `other` are the starting set, but the genre space is open:
any slug you pass to `--genre` names an overlay. Two ship with rules worth
reading before you use them.

- **`devdocs`** — READMEs, docstrings, changelogs, PR text. Most academic surface rules do not transfer. Short sentences, imperatives and dense headings are correct here rather than voice loss. What carries over is the AI-slop avoid-list and the structural anti-patterns, because a README goes wrong the same way a grant does.
- **`business`** — partner terms, letters of intent, investor memos, onboarding packs. The reader is a counterparty rather than a student, so the characteristic failure is teaching them something they already know.

## Architecture

A portable content layer holds all of the procedure and lexicon; a runtime layer
wraps it. Today the runtime is Claude Code skills and a router command. Nothing
in `content/` has to change to add another.

Alongside it sits a small `tools/` layer, deliberately code rather than protocol.
Everything else in marginalia is a judgement task, which is what a language model
executing a prose protocol is good at. Counting is not. `prose_metrics.py` counts
sentence lengths, punctuation rates, gloss density and contrast-frame surfaces
against your measured baselines. `business_tells.py` does the same for the
business register. The split: **the tools count and locate; the protocols judge.**

```text
marginalia/
├── content/                    # portable: all procedure and lexicon
│   ├── paths.md                # where profiles and corpus resolve
│   ├── ai-drift.md             # lexicon + structural anti-pattern catalogue
│   ├── write-protocol.md
│   ├── review-protocol.md
│   ├── extraction-protocol.md
│   ├── citation-tiers.md
│   ├── sub-agent-prompt.md
│   ├── apply-protocol.md
│   ├── input-ingestion.md
│   ├── calibration-protocol.md
│   ├── refine-protocol.md
│   ├── adapt-protocol.md
│   └── styles/
│       └── template.md         # schema; real profiles are gitignored
│
├── tools/                      # deterministic measurement
│   ├── prose_metrics.py
│   └── business_tells.py
│
├── claude-code/                # runtime
│   ├── plugin.json
│   ├── skills/                 # 7 thin loaders
│   └── commands/marginalia.md
│
├── examples/                   # your corpus, gitignored
└── tests/fixtures/             # smoke-test inputs and expected outputs
```

Skill files stay thin. If procedure logic is creeping into a `SKILL.md`, it
belongs in `content/` instead.

## How style learning works

1. Put published work in your corpus directory. Supported: `.md`, `.markdown`, `.txt`, `.pdf`, `.docx`, `.doc`, `.rtf`, `.odt`. Non-Markdown is converted to a sibling `.md` on first run; the conversion is cached and you can hand-edit the result to clean it up.
2. `extract-style` does per-document feature extraction (lexicon, sentence structure, hedging, citation integration, paragraph architecture, argumentative moves) then cross-document synthesis.
3. Output is declarative rules a reviewer can check, like "median sentence length 24 words; rarely exceed 38", not raw statistics. Plus verbatim exemplars, which is what lets `write` imitate rather than paraphrase.
4. Hand-edit any profile. The `## Manual overrides` section survives every refresh and outranks all extracted rules.

Sparse corpora are supported. A genre with one or two examples is marked
`confidence: low | N=k` and review leans on `base.md` accordingly.

## Measured surface metrics

Review Dimensions A–D ask the model to notice things. Dimension E does not.

```bash
python3 tools/prose_metrics.py <target> --genre <genre> --json
python3 tools/prose_metrics.py --emit-baseline
```

The prose sweep is not bad at finding punctuation drift, and it catches things no
counter reaches, such as voice loss by subtraction or a claim contradicted by a
table. What it cannot do is be consistent about it, or estimate a rate against a
corpus by reading. Dimension E is a floor under the sweep, not a replacement.

Reads `.md`, `.mdx`, `.tex` and `.txt` directly, using the same extraction as the
ingestion protocol, so the counter and the sweep see identical text.

## What the citation tiers mean

**Tier 1 — Existence and accuracy.** Cheap, always run. Searches Crossref, Semantic Scholar, and Google Scholar for the cited work; verifies author, year, title, venue; returns a DOI if found. This tier catches the single most common AI failure mode: hallucinated citations and citations with the wrong year, wrong first author, or wrong venue.

**Tier 2 — Source reputability.** Cheap, default on. Checks whether the venue is peer-reviewed and indexed (Scopus, Web of Science), flags predatory journals against curated heuristics, and flags preprints that appear in the text without a preprint qualifier. Reputability is signal, not verdict — a flag here means the venue warrants scrutiny, not that the cite is wrong.

**Tier 3 — Claim–source match.** Expensive, default on. The sub-agent reads the source's abstract (always available) and, where open-access, key passages of the full text, then compares what the in-text claim asserts against what the source actually argues. Flags overgeneralized claims, directionally-wrong claims, and domain-mismatched applications. Deliberately conservative: it flags suspicious mismatches with quoted source passages so you can decide. False positives are expected and acceptable; silent passes on real mismatches are not.

**Tier 4 — Better-source and recency.** Advisory only. Looks for the original empirical source if the cite is a review or commentary; looks for more recent meta-analyses, replications, or higher-impact alternatives. Output is suggestions, never failures — Tier 4 never blocks a cite, it only proposes you consider stronger ones.

## Apply mode

Reports are never silently applied. `/marginalia apply <report-path>` reads the
report's JSON sidecar and stages edits as a diff against the source, but writing
is always behind explicit confirmation.

The split between auto-staging and interactive review is mechanical versus
intellectual. Mechanical fixes (lexicon swaps, tricolon rewrites, citation year
and author corrections) auto-stage when confidence is high enough. Intellectual
changes (removing a hallucinated citation, narrowing an overgeneralised claim,
fixing argumentative drift) come back to you one at a time to accept, reject or
edit.

The diff preview is mandatory even for high-confidence changes. No silent writes,
ever.

## Limitations

Worth knowing before you rely on it.

- **Lexicon-swap suggestions are sometimes context-blind.** "delve into" → "examine into" is ungrammatical. The safety net is the mandatory diff, not the suggestion. Read the diff.
- **Sparsely-indexed work can be flagged as hallucinated.** A real citation that does not surface in Crossref, Semantic Scholar or Scholar within the sub-agent's tool budget lands in the Tier 1 "no match" bucket. Expect this for older monographs, grey literature and niche venues.
- **Tier 3 false positives are common by design.** Claim–source match is calibrated to flag and let you decide rather than to minimise flags. Expect to dismiss some.
- **Predatory-venue detection is heuristic.** A small curated list plus open signals. Beall's list is unmaintained and Cabells is paid.
- **Non-Markdown input is converted, not natively parsed.** Conversion quality limits review quality. Figures, complex tables and multi-column PDFs are lossy. Scanned PDFs need OCR first.
- **Measured baselines go stale.** They reflect the corpus as of the last `--emit-baseline`. Add work without regenerating and you are compared against an older version of your voice.
- **Structural em-dash subtraction cannot be automated.** In dev-doc registers, table rows and definition lists carry em-dashes that are not prose. The tool removes some and is documented as insufficient; the residual has to be read.
- **A profile is only as good as the corpus.** Feed it AI-assisted drafts and it will faithfully learn the drift as your voice. Use published work.
- **English only.**

## Roadmap

- **Now** — Claude Code skills plus a router command.
- **Later** — an MCP server over the same `content/` layer, so it works from any MCP-capable client.
- **Later** — a standalone CLI with a model-agnostic backend, so it runs without Claude Code.

## Origin

marginalia was built by one academic to solve a specific problem: AI-drift and
weakly-grounded citations creeping into his own manuscripts and grant proposals.
It has been in daily use on real papers, grants, presentations and documentation
since mid-2026. It is shared because other people asked for a copy, not because
it is a finished product. Expect rough edges, and expect the defaults to reflect
one person's register until you build your own profile.

Issues and pull requests welcome.

## License

MIT. See `LICENSE`.
