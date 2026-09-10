---
name: marginalia-review
description: Review academic prose for AI-drift, voice loss, and structural anti-patterns. Compares against the user's learned style (base.md + genre overlay) and produces an annotated report with targeted edits. Use when the user wants to check, audit, review, or improve writing in a paper, grant, or essay.
---

# marginalia-review

Review scholarly prose for AI-drift and voice loss against the user's own published style.

## When to use this skill

Invoke when the user asks to:
- Review, check, or audit writing
- Find AI-sounding patterns in prose
- Compare a draft to their own voice
- Suggest edits without rewriting wholesale

Do NOT use this skill for:
- Generating new prose (this skill is a critic, not a writer)
- Grammar/spelling checks (use a spellchecker)
- Citation verification (use `marginalia-verify-cites` instead)
- Full rewrites (the skill produces edits, not replacements)

## How to invoke

The user typically runs this via `/marginalia review <target> [--genre=papers|grants|devdocs|business|other|<slug>]`. When called directly without the command, parse the user's request to identify:
1. The target (file path, file#section, or pasted text)
2. The genre (default to `grants` if working in a grant-proposal workspace, `papers` otherwise; ask if ambiguous)

## Protocol

0. Read `content/paths.md` and resolve `<STYLES_DIR>` and `<CORPUS_DIR>`. Every `content/styles/…` and `examples/…` path below is a name, not a location.
1. Read `content/review-protocol.md` from the marginalia repo (the file lives in the same repo as this skill).
2. Read `content/ai-drift.md`.
3. Read `content/styles/base.md` and `content/styles/{genre}.md` if they exist; note in the report header which were loaded.
4. Follow `content/review-protocol.md` step by step.
5. Write outputs to `<target>.marginalia/<YYYY-MM-DD-HHMM>-review.{md,json}`.

## Locating the marginalia repo

The repo root is the directory containing `content/`, `claude-code/` and `tools/`. From within Claude Code, find it by walking up from the symlinked SKILL.md to its actual location: if the symlink resolves to `<repo>/claude-code/skills/marginalia-review/SKILL.md`, the repo root is `<repo>`.

If the user is invoking from elsewhere, the working directory is the document directory (where the target file lives), but content/ files always come from the marginalia repo.

## Output expectations

After completing the protocol, summarize for the user:
- Path to the markdown report and JSON sidecar
- Total issues found, grouped by priority
- Top 3 highest-priority issues inline (for quick triage)
- A single suggestion: either `/marginalia apply <report-path>` to stage edits, or "I'll wait while you decide which edits to apply manually."

Do NOT modify the target file directly. The apply step is a separate, explicit user action.
