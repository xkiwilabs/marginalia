---
description: Marginalia — draft and revise in your own voice, review writing for AI-drift, verify citations, extract style. Subcommands: write, review, cite, extract-style, calibrate, refine, adapt, full, apply, clean.
---

# /marginalia

Subcommand router for the marginalia writing toolkit.

## Argument parsing

The first argument after `/marginalia` is the subcommand. Remaining arguments are flags or positional values.

`<target>` arguments accept `.md`, `.markdown`, `.txt`, `.pdf`, `.docx`, `.doc`, `.rtf`, and `.odt`. Non-Markdown inputs are auto-converted to a sibling `.md` per `content/input-ingestion.md` before the underlying skill runs; the user's original source file is never modified, and the report directory is named after the user-given target path (e.g., `proposal.pdf.marginalia/`). `<report-path>` arguments to `apply` remain `.md` (or its `.json` sidecar) — reports are always Markdown.

## Path resolution

Style profiles and the corpus do not necessarily live inside the repo. Before any
subcommand that reads or writes them, read `content/paths.md` and resolve
`<STYLES_DIR>` and `<CORPUS_DIR>`. Order: `$MARGINALIA_HOME`, then
`~/.marginalia/`, then the repo's own `content/styles/` and `examples/`. Every
`content/styles/…` path written below is a name, not a location. Report the root
that was used in the run header.

## Subcommands

### `write [task] [--genre=papers|grants|devdocs|business|other|<slug>]`

Invoke the `marginalia-write` skill explicitly to draft or revise prose in the author's voice. The skill engages implicitly on writing-help requests (drafts, revisions, polish) so this subcommand is mostly for forcing engagement — e.g., to apply paper register while inside a grant workspace, or to be explicit about the voice constraints.

`[task]` is optional inline prose describing the writing task ("draft an abstract for X", "tighten this paragraph: …"). If omitted, the skill prompts for the task and target prose.

If `--genre` is not specified, the skill auto-detects from cwd (matches `marginalia-review` heuristic: `grants` if workspace has files matching `*proposal*` or `*grant*`, else `papers`). Specify explicitly to override.

### `review <target> [--genre=papers|grants|devdocs|business|other|<slug>]`

Invoke the `marginalia-review` skill on `<target>`. Pass `--genre` if specified; otherwise let the skill infer per the table in `content/review-protocol.md` §1, falling back to `grants` if the working directory looks like a grant workspace (contains files matching `*proposal*` or `*grant*`), else `papers`.

Use `--genre=business` for commercial documents a counterparty reads: partner terms and pricing, letters of intent, investor appendices and memos, onboarding and data-request packs. It keeps the zero-em-dash rule, drops the papers sentence-length and gloss baselines, and adds the failure modes specific to the register.

Use `--genre=devdocs` for developer documentation: repository and module READMEs, in-code docstrings and comments, changelogs, issue and PR text, and design notes. Most `base.md` surface rules do not transfer to this register — what carries over is the AI-slop avoid-list and the structural anti-patterns. Note the em-dash carve-out: devdocs is exempt from the zero target, and structural em-dashes (table rows, definition-list entries, titles) must be subtracted by reading, not by regex.

### `cite <target> [--tiers=1,2,3,4] [--bib=<path>]`

Invoke the `marginalia-verify-cites` skill on `<target>`. Pass through the tier subset and bibliography hint.

### `extract-style [--genre=papers|grants|devdocs|business|other|<slug>|all] [--mode=init|refresh|update]`

Invoke the `marginalia-extract-style` skill. Defaults to `--genre=all --mode=init` (or `refresh` if style files already exist).

### `calibrate [--genre=papers|grants|devdocs|business|other|<slug>] [--contrast] [--both]`

Voice-fidelity self-test: reconstruct a held-out passage and score it against the original. `--contrast` adds a generic-vs-voiced read; `--both` runs both.

Invoke the `marginalia-calibrate` skill, which reads `content/calibration-protocol.md` and follows it. The default mode is `reconstruct`: hold out a passage from the author's corpus, reconstruct it under the learned voice profile, and score the reconstruction against the original. `--contrast` instead runs the generic-vs-voiced contrast (a generic read against a voiced read of the same passage). `--both` runs both modes over one held-out passage. If `--genre` is not specified, default to `papers`. Unknown flags are recorded under ignored flags and the run proceeds.

### `refine [--genre=papers|grants|devdocs|business|other|<slug>] [--categories=tics,underused,...|all]`

Critique the author's own voice and propose corpus-grounded, voice-preserving refinements by category (e.g., overused tics, underused strengths).

Invoke the `marginalia-refine` skill, which reads `content/refine-protocol.md` and follows it. Suggestions are grounded in the author's own corpus and grouped by the requested `--categories`. If `--genre` is not specified, default to `papers`; if `--categories` is not specified, default to `tics,underused` (pass `--categories=all` for every category). Accepted refinements are written only into the style file's `## Manual overrides` section, after a diff and explicit per-edit confirmation. Unknown flags are recorded under ignored flags and the run proceeds.

### `adapt --to=<format> [--samples=<paths>] [--from=base]`

Derive a provisional style overlay for a format the author has no corpus for yet (a new blog, op-ed, newsletter, talk, or email).

Invoke the `marginalia-adapt` skill, which reads `content/adapt-protocol.md` and follows it. It derives a provisional `content/styles/{format}.md` overlay from the author's base invariants plus the target register preset (presets: `blog`, `op-ed`, `newsletter`, `talk`, `email`). Optional `--samples` (1–3 paths) sharpen the register by overriding preset defaults with measured values. `--from` (default `base`) selects the base profile to transform. The output is low-confidence by construction and decays into a real profile via `extract-style --genre={format} --mode=update` once real pieces accumulate. Unknown flags are recorded under ignored flags and the run proceeds.

### `full <target> [--genre=grants]`

Parallel-dispatch `marginalia-review` and `marginalia-verify-cites` as two background sub-agents. Use the Agent tool with `run_in_background=true` for each. Wait for both to complete.

After both finish, write a merged index file at `<target>.marginalia/<YYYY-MM-DD-HHMM>-full.md`:

```markdown
# Marginalia full review: <target>
Generated: <ISO timestamp>

## Combined priority queue
[interleave high-priority issues from both reports, sorted by severity then line number]

## Detail reports
- [Review report](./<timestamp>-review.md) — <n> issues
- [Citation report](./<timestamp>-cites.md) — <n> issues

## Next steps
- Apply mechanical fixes: `/marginalia apply <review-report-path>`
- Apply citation corrections: `/marginalia apply <cite-report-path>`
- Hallucinations and claim-mismatches need your attention — see citation report.
```

### `apply <report-path> [--priority=high|medium|low] [--types=t1,t2,...] [--ids=R-001,...]`

Read `content/apply-protocol.md` and follow it. The `<report-path>` may be a `.md` (paired `.json` is auto-located) or `.json` directly.

Mandatory: show the user a full diff before any write. Never silent-write.

### `clean [--scope=<path>] [--older-than=30d]`

Find `*.marginalia/` directories under `--scope` (default: cwd). For each, delete reports older than the threshold (default 30 days). Do not delete `*.marginalia/` directories themselves; only old reports inside.

**Scope guards (refuse-by-default, no override flag — re-run from a narrower cwd or pass an explicit `--scope`):**

- Refuse if the effective scope is `$HOME`, `/`, `/tmp`, `/var`, `/usr`, `/etc`, `/opt`, or any direct child of `/` other than the user's project root. Error: `clean refuses to traverse <scope> — pass --scope=<specific-project-path> or cd into a narrower directory first`.
- Refuse if the effective scope is a parent of `$HOME` (e.g., `/Users` on macOS, `/home` on Linux).
- If `--scope` is given, it must be an existing directory and must not match any guard above. Relative paths resolve against cwd.

**Mandatory preview before any deletion** (already required, restated): walk the scope, build the full list of files-to-be-deleted with their sizes and ages, present this list to the user. Require explicit confirmation (`yes` / `confirm`) before any unlink. `cancel` aborts with no filesystem changes.

If the preview list is empty, exit cleanly with `nothing to clean`.

## Locating the marginalia repo

This command file is typically symlinked from `~/.claude/commands/marginalia.md` into a marginalia checkout, e.g. `<repo>/claude-code/commands/marginalia.md`. To locate `content/*.md` files, resolve the symlink and walk up two levels (commands/ → claude-code/ → repo root).

## Error handling

- Unknown subcommand → print available subcommands, exit
- Missing required arg (`<target>`, `<report-path>`) → prompt user
- Target file not found → error with clear message
- Both `--ids` and `--types` filters: intersect (apply only issues that match BOTH)
