---
name: marginalia-verify-cites
description: Verify all citations in a document across four tiers: existence/accuracy, venue reputability, claim-source match, and better-source suggestions. Dispatches parallel sub-agents (one per unique cite, capped at 8 concurrent). Use when the user wants to verify, check, or audit citations in a paper or grant before submission.
---

# marginalia-verify-cites

Four-tier citation verification with parallel sub-agents.

## When to use this skill

Invoke when the user asks to:
- Verify, check, audit, or validate citations
- Find hallucinated references
- Cross-check in-text claims against cited sources
- Suggest better, more current, or higher-impact sources
- Audit a bibliography before submission

Do NOT use this skill for:
- Style or prose review (use `marginalia-review`)
- Generating new references (this skill is a critic, not a writer)
- Grammar / spelling checks
- Full rewrites of the bibliography

## How to invoke

The user typically runs this via `/marginalia cite <target> [--tiers=1,2,3,4] [--bib=<path>]`. When called directly without the command, parse the user's request to identify:
1. The target (file path, file#section, or pasted text)
2. The tier subset (default: all four)
3. The bibliography location (default: auto-detect in target)

Defaults: all four tiers run; bibliography auto-detected; concurrency capped at 8 simultaneous sub-agents; `tier_3_paywall_policy = confidence_low`.

Tier 1 is non-negotiable — if the user passes a tier subset that omits Tier 1, stop with a user error.

## Protocol

1. Read `content/citation-tiers.md` from the marginalia repo. This is the orchestration spec — follow it section by section.
2. Read `content/sub-agent-prompt.md` from the same repo. This is the prompt passed to every dispatched sub-agent; you do not execute it yourself.
3. Run **Phase A — Extraction** sequentially (Section 2 of `citation-tiers.md`): resolve the target, detect inline citations, detect the bibliography, cross-check, and produce the `unique_cites` list plus any Phase A issues.
4. Run **Phase B — Per-citation verification** in parallel (Section 3): dispatch one sub-agent per unique cite via the Agent tool, capped at 8 concurrent. See sub-agent dispatch notes below.
5. Run **Phase C — Aggregation** sequentially (Section 4): roll up Phase A and Phase B results, sort, assign stable `C-NNN` IDs, compute summary counts.
6. Write outputs to `<target>.marginalia/<YYYY-MM-DD-HHMM>-cites.{md,json}`. For pasted text, write to `./stdin-<YYYY-MM-DD-HHMM>.marginalia/` in the cwd. Never overwrite — if a file with the same timestamp exists, append `-2`, `-3`, etc.

## Locating the marginalia repo

The repo root is the directory containing `content/`, `claude-code/` and `tools/`. From within Claude Code, find it by walking up from the symlinked SKILL.md to its actual location: if the symlink resolves to `<repo>/claude-code/skills/marginalia-verify-cites/SKILL.md`, the repo root is `<repo>`.

If the user is invoking from elsewhere, the working directory is the document directory (where the target file lives), but `content/` files always come from the marginalia repo.

## Sub-agent dispatch notes

Phase B is the operationally complex part. Read Section 3 of `content/citation-tiers.md` and `content/sub-agent-prompt.md` together before dispatching anything.

**Dispatching:**
- Use the Agent tool with `subagent_type=general-purpose` and `run_in_background=true`. Each dispatch is non-blocking.
- The sub-agent prompt is the full text of `content/sub-agent-prompt.md` concatenated with the structured inputs for that citation (see `citation-tiers.md` §B.1 for the input fields: `citation_text`, `citation_key`, `authors`, `is_et_al`, `year`, `surrounding_paragraph`, `bibliography_entry`, `tiers_to_run`, `tier_3_paywall_policy`).
- Track each in-flight agent by `(citation_key, agent_id)`.

**Concurrency cap:**
- At most 8 sub-agents in flight at any moment (the `concurrency_cap` default in `citation-tiers.md` §1).
- If `len(unique_cites) > 8`, dispatch the first 8, then dispatch additional agents as earlier ones complete. Keep a small FIFO queue of pending cites.
- The cap protects external API rate limits (Crossref, Semantic Scholar, OpenAlex); do not raise it without reason.

**Waiting for results:**
- Use the harness notification mechanism — sub-agents started with `run_in_background=true` will notify when they complete. Do NOT sleep-poll in tight loops.
- If polling is unavoidable, use the longest reasonable interval (≥30s). The cost model of this skill assumes background notifications, not active polling.

**Per sub-agent timeouts and errors:**
- 10-minute soft timeout per sub-agent. If an agent has not returned at that mark, stop waiting on it and record a `tier-error` issue for its citation (`citation-tiers.md` §B.4): `{type: "tier-error", priority: "medium", auto_applicable: false, rationale: "Verification could not complete for this citation; re-run later."}`.
- Do not let one stuck agent block the whole run. Collect what has returned, mark the rest, proceed to Phase C.
- If a sub-agent returns malformed JSON (cannot be parsed) or returns `tier_error` for Tier 1, treat it the same as a non-return: emit a `tier-error` issue. Never silently drop a cite — the user needs to know which citations were and were not checked.
- Per-tier errors within an otherwise successful return (e.g., Tier 2 fails but Tier 3 succeeded) are not fatal; record them in the JSON `tier_results` for that issue and proceed.

**What you do NOT do:**
- You do not make Crossref, Semantic Scholar, OpenAlex, or WebSearch calls yourself. All external lookups happen inside sub-agents, per the budget caps in `content/sub-agent-prompt.md`.
- You do not interpret Tier 3 claim–source mismatches. The sub-agent decides whether to flag; you aggregate the verdict.

## Output expectations

After completing the protocol, summarize for the user:
- Path to the markdown report and JSON sidecar.
- Total unique cites scanned and the tier coverage actually run.
- Breakdown: critical / reputability flags / claim–source mismatches / bibliography hygiene / better-source suggestions / verified / tier errors.
- Top 3 highest-priority issues inline (citation, type, one-line rationale) for quick triage.
- A single next-step suggestion: either `/marginalia apply <report-path>` to stage the mechanical fixes (year mismatches, author spelling, preprint labelling), or "I'll wait while you decide how to handle the hallucinations and claim-source mismatches" if the report is dominated by issues that require author judgement.

Do NOT modify the target file or the bibliography directly. The apply step is a separate, explicit user action.
