# Running marginalia on other models

**Short answer: yes, and the repo was built for it. With one real exception,
which is citation checking on a machine with no internet access.**

marginalia is not a Claude program. It is a set of written procedures that
happen to be executed by Claude Code today. Nothing about the procedures assumes
which model reads them. This document is about what it takes to point a
different model at them.

Be warned that "possible" and "as good" are different claims. The procedures are
long and demand careful multi-step instruction-following, so a weaker model will
produce a worse review rather than an error message. That failure is quiet. Read
[Judging whether it worked](#judging-whether-it-worked) before you trust output
from a model you have not tested.

---

## What is portable, and what is not

| Layer | Files | Portable? |
|---|---|---|
| `content/` | 10 of 12 `.md` files | **Yes, completely.** Plain English procedure. No code, no API calls, no model-specific syntax. |
| `content/sub-agent-prompt.md`, `content/citation-tiers.md` | 2 files | **Almost.** Both name two Claude Code tools, and only in the citation-checking path. See [The two substitutions](#the-two-substitutions). |
| `tools/` | 2 Python scripts | **Yes, completely.** Standard-library Python 3. No model involved at all. |
| `claude-code/` | 7 skills + 1 command | **No.** This is the Claude Code adapter. You replace it. |

That ratio is the whole story. The part you would have to rewrite is about 530
lines of thin loader. The part you keep is about 4,000 lines of procedure and
AI-drift catalogue, which is where the actual value sits.

This was deliberate. `content/` is described throughout the repo as "the
portable contract", and the rule that operational logic never goes in a
`SKILL.md` exists precisely so that this document can be short.

---

## What a runtime has to provide

Six capabilities. A runtime missing one loses the features that depend on it,
and the table in [What degrades](#what-degrades) says which.

1. **Read a file.** Protocols, style profiles, the document under review.
2. **Write a file.** Reports go to `<target>.marginalia/<timestamp>-review.md` plus a JSON sidecar.
3. **Long-context instruction-following.** The binding constraint. See below.
4. **Ask the user and wait.** Apply mode must show a diff and get a yes. A runtime that cannot pause for confirmation must not run `apply` at all.
5. **Run a shell command.** For `tools/prose_metrics.py`. Optional: without it, review Dimension E is skipped and says so.
6. **Fetch a URL, and search the web.** Citation verification only. No substitute exists.

Parallel sub-agents are *not* on this list. Citation checking dispatches one
sub-agent per citation because it is faster, not because it is required. A
serial loop over the same prompt produces the same answers, slowly.

### Context budget

Measured from the actual files. Add your document on top.

| Operation | Instructions loaded | Rough tokens |
|---|---|---|
| `review` | review-protocol + ai-drift + base.md + genre overlay + paths | **~33,000** |
| `cite` (orchestrator) | citation-tiers | ~10,000 |
| `cite` (per citation) | sub-agent-prompt | ~5,800 |
| `extract-style` | extraction-protocol, plus one document at a time | ~11,000 + document |

So a review of a 5,000-word draft needs roughly **40k tokens of usable context**,
and comfortably more if you want the model reasoning rather than just fitting.
Treat 64k as the practical floor and 128k as comfortable.

Note that `extract-style` reads one document at a time and then synthesises, so a
large corpus does not need a large context. Reviewing does.

---

## Three ways to do it

### Route A: another agentic CLI

**Easiest by far.** If your tool can read files, write files and run shell
commands, you are most of the way there.

Candidates: OpenAI's Codex CLI, Gemini CLI, Cursor, Aider, Continue, Cline, or
any harness with a filesystem.

The work is replacing `claude-code/` with an equivalent loader. Read one of the
existing `SKILL.md` files first: they are 50 to 90 lines and most of that is
guidance on when to trigger. The operative part of `marginalia-review` is
essentially:

```
0. Read content/paths.md; resolve <STYLES_DIR> and <CORPUS_DIR>.
1. Read content/review-protocol.md.
2. Read content/ai-drift.md.
3. Read <STYLES_DIR>/base.md and <STYLES_DIR>/{genre}.md if they exist.
4. Follow content/review-protocol.md step by step.
5. Write outputs to <target>.marginalia/<YYYY-MM-DD-HHMM>-review.{md,json}.
```

If your tool has custom commands or rules files, that maps directly. If it does
not, paste the six lines above into a chat with the repo open. It works, and it
is a reasonable way to find out whether your model is up to the procedure before
you build anything.

**Expect to spend an afternoon**, most of it on `cite`, because parallel dispatch
and tool budgets differ between harnesses.

### Route B: a driver script over any API

Write a program that does the orchestration and calls a model for the judgement.
This is the most portable option and works with OpenAI, Gemini, Anthropic,
Mistral, or anything with an OpenAI-compatible endpoint.

The shape, deliberately provider-neutral:

```python
from pathlib import Path

REPO = Path(__file__).resolve().parent
STYLES = Path.home() / ".marginalia" / "styles"   # see content/paths.md

def call_model(system: str, user: str) -> str:
    """Swap this one function per provider. Everything else stays."""
    ...

def review(target: Path, genre: str = "papers") -> str:
    parts = [
        (REPO / "content" / "review-protocol.md").read_text(),
        (REPO / "content" / "ai-drift.md").read_text(),
    ]
    for name in ("base.md", f"{genre}.md"):        # profile is optional
        p = STYLES / name
        if p.exists():
            parts.append(f"# Style profile: {name}\n\n{p.read_text()}")

    system = "\n\n---\n\n".join(parts)
    user = (f"Review the following document, genre={genre}. "
            f"Follow the protocol above exactly.\n\n{target.read_text()}")

    report = call_model(system, user)
    out = target.parent / f"{target.name}.marginalia"
    out.mkdir(exist_ok=True)
    (out / "review.md").write_text(report)
    return report
```

That is genuinely most of it for `review`. Notes that matter:

- **Cache the system prompt.** It is ~33k tokens and identical across every review. Every major provider offers prompt caching, and without it you pay full price per run.
- **Run `prose_metrics.py` yourself** and paste its `--json` output into the user message. Do not ask the model to count. The protocol is explicit that the tool counts and the model judges.
- **`apply` needs a real confirmation loop.** Do not automate past it. The no-silent-writes rule is the reason people trust the tool with their manuscripts.
- **`cite` is the hard one.** You supply the search and fetch, then run `sub-agent-prompt.md` once per citation, in parallel if you can.

This route is what the repo's roadmap calls the standalone CLI. If you build it
well, please open a pull request.

### Route C: a local model

**Honest assessment: partly.** Splitting by feature, because the answer differs
sharply.

| Feature | Local model verdict |
|---|---|
| `review` | **Workable on a large model with long context.** Quality drops with model size, and drops quietly. |
| `extract-style` | **Workable.** Reads one document at a time, so context is less of a constraint. Slow over a big corpus. |
| `write` | **Workable.** Imitating exemplars is a natural fit. |
| `calibrate` | **Workable, and the thing to run first.** It is a self-test, so it tells you whether the model is good enough. |
| `cite` Tiers 1 and 2 | **Only with internet access and search tooling.** The model is not the constraint; the network is. |
| `cite` Tiers 3 and 4 | **Realistically no.** Needs fetching full texts and judging claim-source fit across long documents. |

What actually bites, in order:

1. **Context.** A review needs ~40k tokens minimum. Many local setups default to 4k or 8k, and quietly truncate rather than erroring. Check your actual configured context, not the model's advertised maximum.
2. **Instruction adherence over long procedures.** `review-protocol.md` is a five-dimension sweep with per-dimension severity and confidence rules. Smaller models drift into summarising the document instead of executing the protocol.
3. **Structured output.** The JSON sidecar drives `apply`. Models that cannot hold a schema across a long generation break that pipeline. Consider dropping the sidecar and using the Markdown report by hand.
4. **No search.** Citation verification is not a reasoning problem, it is a data problem. If the machine cannot reach Crossref, no model size fixes it.

**If privacy is why you want local:** consider splitting. Run `review`, `write`
and `extract-style` locally, since those touch your unpublished prose. Run `cite`
against a hosted model when you need it, since citations are already public
metadata. Your draft never leaves the machine; only bibliography entries do.

---

## The two substitutions

Two files name Claude Code tools, `content/sub-agent-prompt.md` and
`content/citation-tiers.md`, and both only in the citation-checking path. Two
tool names between them, each with an obvious equivalent:

| In the file | Means | Replace with |
|---|---|---|
| `WebFetch` | Fetch a URL, return readable content | Your HTTP client. It hits the Crossref and Semantic Scholar JSON APIs, and fetches open-access PDFs. |
| `WebSearch` | General web search | Your search tool, or a search API. |

Everything else in that file is procedure: which source to try first, what counts
as a match, when to declare `not_found`, and the tool-call budgets. Keep those.
The budgets in particular (3 calls for Tier 1, 5 for Tier 4, 12 total per
citation) exist to stop a citation check running forever, and are not
Claude-specific.

The other ten files in `content/` need no changes at all. If you are not
porting `cite`, none of this applies to you.

---

## What degrades

If your runtime is missing a capability, this is what you lose. Nothing here
fails loudly on its own, so wire the notices in deliberately.

| Missing | Consequence |
|---|---|
| Shell execution | Review Dimension E skipped. Report must say `Dimension E: skipped (prose_metrics unavailable)`. A–D still run. Never let the model fake the numbers. |
| Web search or fetch | `cite` cannot run. Do not substitute the model's memory for a database lookup: that is precisely the failure the tool exists to catch. |
| Confirmation prompts | `apply` must be disabled. Reports are still useful; apply them by hand. |
| Long context | Everything degrades quietly. See below. |
| A style profile | Voice comparison is skipped, by design. Review still catches AI-drift and structural problems. This is the supported cold-start state, not a failure. |

---

## Judging whether it worked

A weaker model does not error. It produces a plausible-looking report that
misses things. Two checks, both already in the repo.

**1. The fixtures.** `tests/fixtures/ai-drift-sample.md` contains six planted
problems, described in `tests/fixtures/README.md`. Run a review and count how
many come back. Fewer than six means the model is not executing the protocol,
whatever the report looks like. `tests/fixtures/citations-sample.md` has four
planted citation problems listed in a comment at the top of the file, one of
which is an invented reference that must be caught.

**2. `calibrate`.** This is the real test, and it is the reason the command
exists. It hides a passage of your own writing, asks the model to reconstruct it
from the profile alone, then scores the attempt against the original. It measures
whether *this model with this profile* can actually reproduce your voice. Run it
before trusting a new setup, and run it again after switching models.

A model that passes the fixtures and scores well on calibrate is doing the job.
One that does neither is producing text that resembles a review.

---

## Things that are genuinely hard

Not discouragement, just the parts worth knowing before you start.

- **Tier 3 claim–source matching** is the most demanding judgement in the toolkit. It reads a source and decides whether it supports a specific sentence. It is deliberately calibrated to over-flag, which only works if the model can hold a full text and a claim in mind simultaneously.
- **The carve-outs matter more than the rules.** Every style profile has a section listing AI-drift entries that are genuine habits of that author. A model that ignores it flags real voice as drift, and the user stops trusting the tool. This is a subtle instruction-following requirement and a good early test.
- **Confidence and severity scoring** is specified per-dimension in `review-protocol.md`. Models that ignore it produce reports where everything is HIGH, which is the same as nothing being HIGH.
- **The JSON sidecar schema** has to be exact for `apply` to work. Budget time here, or ship without `apply` initially.

---

## If you build one

Open an issue or a pull request. A working adapter for another runtime is
genuinely useful to other people, and the `content/` layer only stays honest
about being portable if someone other than its author has ported it.

Worth saying explicitly: if you port this and the reviews come out worse, that is
information about the model, not necessarily about your adapter. Run `calibrate`
and the fixtures before concluding you did something wrong.
