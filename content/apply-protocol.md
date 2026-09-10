# Apply protocol

The procedure `/marginalia apply` follows. Loaded once at the start of every apply run. The command file (`claude-code/commands/marginalia.md`) is a thin router; this file is the actual procedure.

Apply consumes a report's `.json` sidecar and stages the proposed edits as a diff against the source file. Auto-applicable issues (mechanical fixes) auto-stage; everything else is presented interactively. No write ever happens without a confirmation step on the diff — even for high-confidence mechanical fixes.

Apply edits the Markdown file the originating report targeted. If the original user-given input was a non-Markdown format (PDF, docx, etc.), that input was converted to a sibling `.md` per `content/input-ingestion.md` and the report's `target_path` is the converted Markdown — apply edits that converted `.md`, never the user's original source file. Reports are produced by `marginalia-review` (per `content/review-protocol.md`) and `marginalia-verify-cites` (per `content/citation-tiers.md`).

Follow sections in order. Where a section says "if X, error", produce the error and stop — do not write a partial diff or partial update.

---

## Section 1: Inputs

- **`report_path`** (required) — path to a `.md` report or its `.json` sidecar. If `.md` is given, the `.json` companion is auto-located by extension swap.
- **Filters** (all optional):
  - `--priority=<csv>` — comma-separated subset of `{high, medium, low}`. Apply only issues at these priorities. Example: `--priority=high,medium`.
  - `--types=<csv>` — comma-separated issue types. Example: `--types=ai-drift-verb,lexicon-drift`.
  - `--ids=<csv>` — comma-separated specific issue IDs. Example: `--ids=R-001,R-005,C-003`.

**Filter combination rules:**

- `--types` AND `--priority` → intersect (apply only issues matching BOTH).
- `--ids` given → explicit list wins; ignore `--types` and `--priority` except to validate that listed IDs exist in the report (unknown IDs produce a warning, not an error).
- No filters → all issues in the report are eligible.

Unknown flags: record under `ignored_flags` in the run header, proceed.

---

## Section 2: Locate and validate

### 2.1 Resolve report paths

- `report_path` ends with `.md` → derive `.json` companion by replacing extension.
- `report_path` ends with `.json` → derive `.md` companion (for display purposes only; the `.json` is canonical).
- Only one of the pair exists → error: `paired <other extension> not found at <derived path>`. Stop.
- Both exist → proceed.

### 2.2 Validate JSON schema

Required top-level fields: `report_id`, `target`, `generated_at`, `issues` (array).

Expected (warn if missing, do not error):
- Review reports: `summary`, `style_files_loaded`, `mode`, `genre`.
- Citation reports: `summary`, `tiers_run`, `concurrency_cap`, `verified_cites`.

For each issue, required fields are: `id`, `priority`, `type`, `location`, `current`, `confidence`, `auto_applicable`, `rationale`. The `proposed` field is required to be present but may be `null`.

**Citation-issue additional required fields.** Issues produced by `marginalia-verify-cites` (i.e., those with `id` matching `C-NNN`, or any issue whose `type` begins with `citation-`, `bibliography-`, `preprint-`, `predatory-`, `pay-to-publish-`, `claim-source-`, `better-source-`, `recency-`, or `tier-error`) also require: `citation_key` (string), `tier` (integer or null), `doi` (string or null), `source_quote` (string or null), `tier_results` (object or null). See `content/citation-tiers.md` §5b for shape. Validation treats `null` as present.

If validation fails: error with the specific missing or malformed field. Stop.

### 2.3 Identify the source file

The source path is in the JSON's `target` field. Resolve in this order; stop at the first hit:

1. The exact `target` path (absolute or relative to cwd).
2. The path relative to cwd, if it was absolute and didn't exist at the absolute location.
3. The path relative to the `.marginalia/` parent directory (reports live in `<source>.marginalia/`, so `..` from that directory should land on the source's parent).

If still not found: error listing every path tried. Stop. Suggest re-running with `--target=<new_path>` (see Section 8).

Special case: `target` of the form `stdin-<timestamp>` indicates the report was produced from pasted text. Apply does not support pasted-text targets — error: `apply does not support stdin targets; re-run review/cite on a file instead`. Stop.

### 2.4 Detect source drift (before filtering, before classification)

**What `current` anchors to, by issue category** (the producing protocols are responsible for emitting these correctly; apply only anchors and edits):

- **Lexicon swaps** (`ai-drift-verb`, `-adjective`, `-discourse-marker`, `-meta-phrase`, `lexicon-drift`): the exact word or short phrase to swap. Substring-unique by definition or via cluster-collapse (review §6).
- **Structural review issues** (`ai-drift-opener-in-recent-years`, `ai-drift-bullets-in-argument`, etc.): the exact opening phrase, structural marker, or paragraph-leading sentence — whichever substring is unique in the paragraph's source span. The producing protocol picks the shortest substring-unique anchor.
- **Mechanical citation corrections** (`citation-year-mismatch`, `citation-author-spelling-mismatch`, `citation-title-correction`, `preprint-not-marked`): the exact in-text citation text (e.g., `"(Smith, 2003)"`).
- **`citation-hallucinated`** and other Tier-1 fails: the in-text citation text. The surrounding clause is not part of `current`; it appears in the interactive prompt's context window (Section 4.2).
- **`claim-source-mismatch`** (Tier 3): the in-text citation text is `current`. The full source-quote and surrounding-claim context live in `source_quote` and the issue's `rationale`; apply uses them for the interactive prompt but does NOT anchor on them. This is why this type is always interactive — there is no clean replacement at the anchor.
- **`bibliography-orphan`**: the bibliography entry's first ~120 characters (substring-unique within the bibliography). Apply re-locates the full entry by walking forward to the next blank line at edit time.
- **`citation-missing-bibliography-entry`**: the in-text citation text (the missing reference is in the bibliography, not at the cite location; this issue is always interactive).

For each issue in the report, search the current source file for the issue's `current` text:

- **Exact one match.** OK. Record the match's source offset on the issue.
- **Multiple matches.** Mark the issue `ambiguous`. It cannot be auto-applied; it can only be applied via `--ids=<specific_id>` with explicit user confirmation of the location during the interactive step.
- **Zero matches.** The source has drifted since the report was generated. Mark the issue `conflict`. Skip from auto-apply path; offer for manual review in the interactive listing.

Drift detection runs **before** filtering and classification so the user sees, in the run header, how much of the report is still actionable against the current source.

Re-anchoring is by **exact text**, not by line numbers — the JSON's `location.line_start/char_start` fields are advisory only at apply time. Any prior edit (made between the report generation and now, including edits applied in an earlier apply run) shifts those offsets.

---

## Section 3: Classify each issue

### 3.1 Apply user filters

Reduce the issue set to those matching the filter flags from Section 1. If `--ids` is given, that list is the issue set (after Section 2.4 has annotated `ambiguous`/`conflict` flags); otherwise intersect `--priority` and `--types` against the report's issues.

### 3.2 Decide auto-apply vs. interactive

Per-type classification. The table below is canonical for Phase 1. New types added to either review or citation protocols must be added here.

| Issue type | Auto-applicable | Min confidence | Notes |
|---|---|---|---|
| `ai-drift-verb` | Yes | 0.80 | word-level swap |
| `ai-drift-adjective` | Yes | 0.80 | word-level swap |
| `ai-drift-discourse-marker` | Yes | 0.80 | word-level swap |
| `ai-drift-meta-phrase` | Yes | 0.80 | phrase-level swap |
| `ai-drift-tricolon` | Yes | 0.85 | context-dependent; only when `proposed` is non-null |
| `lexicon-drift` | Yes | 0.80 | only when `proposed` is non-null (clear alternative) |
| `sentence-length-drift` | No | — | always interactive (rewrite) |
| `hedging-pattern-drift` | No | — | always interactive |
| `citation-integration-drift` | No | — | always interactive |
| `paragraph-architecture-drift` | No | — | always interactive |
| `em-dash-pattern-drift` | No | — | always interactive |
| `argumentative-claim-buried` | No | — | always interactive |
| `argumentative-restatement-closer` | No | — | always interactive |
| `argumentative-hedged-opener` | No | — | always interactive |
| `argumentative-cite-mismatch` | No | — | always interactive — defer to citation report |
| `argumentative-contradiction` | No | — | always interactive |
| `ai-drift-opener-in-recent-years` | No | — | structural — author rewrites paragraph opener |
| `ai-drift-todays-x-opener` | No | — | structural |
| `ai-drift-bullets-in-argument` | No | — | structural — convert list to prose |
| `ai-drift-restatement-closer` | No | — | structural — section-ending paragraph |
| `ai-drift-topic-example-restate` | No | — | structural |
| `ai-drift-topic-with-tricolon` | No | — | structural |
| `ai-drift-transition-paragraph` | No | — | structural |
| `ai-drift-symmetric-parallel` | No | — | structural rhythm |
| `ai-drift-importance-marker` | No | — | structural |
| `ai-drift-adversative-rhythm` | No | — | structural |
| `ai-drift-hedge-stacking` | No | — | structural |
| `ai-drift-not-just-x-but-y` | No | — | structural rhythm |
| `ai-drift-hedging-without-substance` | No | — | structural |
| `ai-drift-false-balance` | No | — | structural |
| `ai-drift-concession-reversal-rhythm` | No | — | structural |
| `ai-drift-ultimately-closer` | No | — | structural |
| `ai-drift-importance-pivot` | No | — | structural |
| `ai-drift-recursive-three-part` | No | — | structural |
| `ai-drift-per-paragraph-thesis-restate` | No | — | structural |
| `ai-drift-excessive-headers` | No | — | formatting |
| `ai-drift-bold-overuse` | No | — | formatting |
| `ai-drift-em-dash-overuse` | No | — | formatting |
| `ai-drift-inconsistent-headers` | No | — | formatting |
| `ai-drift-decorative-hr` | No | — | formatting |
| `ai-drift-emoji-decoration` | No | — | formatting |
| `ai-drift-summary-blockquote` | No | — | formatting |
| `citation-year-mismatch` | Yes | 0.85 | mechanical: replace in-text year with bibliography year |
| `citation-author-spelling-mismatch` | Yes | 0.80 | mechanical: replace surname spelling |
| `citation-title-correction` | Yes | 0.85 | mechanical: Tier 1 found work with corrected title |
| `preprint-not-marked` | Yes | 0.80 | mechanical: append ` (preprint)` to cite |
| `citation-hallucinated` | No | — | user decides: remove / replace / rewrite surrounding clause |
| `claim-source-mismatch` | No | — | narrowing the claim is intellectual work |
| `citation-missing-bibliography-entry` | No | — | could be missing entry OR wrong author/year |
| `predatory-venue-suspected` | No | — | flag only — no edit makes the venue not-predatory |
| `pay-to-publish-venue` | No | — | advisory |
| `bibliography-orphan` | No | — | bibliography pruning; needs author confirmation |
| `bibliography-mismatch-suspected` | No | — | bulk issue, author triage |
| `better-source-suggestion` | No | — | advisory — author may not act |
| `recency-superseded-finding` | No | — | advisory |
| `tier-error` | No | — | re-run later; not actionable in apply |

**Classification rule (applied per issue):**

1. If the issue's `auto_applicable` field in the JSON is `false`: always interactive, regardless of the table. The producing protocol's judgement wins.
2. Otherwise, if the table marks the type auto-applicable AND `confidence >= min_confidence_for_type` AND `proposed != null` AND the issue is not flagged `ambiguous` or `conflict` from Section 2.4: auto-stage.
3. Otherwise: interactive.

**Principle:** mechanical changes auto-stage; intellectual changes always return to the author. Never silent-write structural edits.

**Type not in the table.** If a future protocol revision introduces an issue type not listed above, default to interactive (`auto_applicable=false`) and surface a note in the run header: `"unknown issue type <type>; treated as interactive"`. The table is the canonical safety net.

---

## Section 4: Build the diff

### 4.1 Auto-stage path

For each issue classified auto-stageable in Section 3:

1. Search the current source for the unique occurrence of the issue's `current` text (already done in Section 2.4; reuse the recorded offset).
2. Build a planned-edit record:
   ```
   {
     issue_id,
     source_offset_start,
     source_offset_end,
     current,
     replacement: proposed
   }
   ```
3. If, between Section 2.4 and now, an earlier auto-staged edit has changed the source enough to invalidate this issue's offset, recompute the offset by re-searching for `current`. If `current` no longer appears exactly once, demote this issue to a conflict-on-apply (don't fail silently — surface in the conflicts list at confirmation time).

### 4.2 Interactive path

For each issue classified interactive in Section 3 (sorted: high priority → low; within the same priority, ascending by source offset):

Present to the user:
- Issue ID, type, priority
- The `current` text with 1–2 surrounding sentences of source context
- The `rationale`
- If `proposed != null`: the proposed replacement text
- For citation issues: a one-line summary of tier results (e.g., `Tier 1: not_found`, `Tier 2: skipped`, `Tier 3: skipped`). For `claim-source-mismatch`, also show the `source_quote` field.

Accept one of:

- **`accept`** — add to staged edits using the `proposed` text. If `proposed == null`, prompt the user to supply replacement text inline.
- **`accept with edit: <text>`** — add to staged edits with the user's text instead of `proposed`.
- **`reject`** — record the decision; the issue is excluded from this run and marked rejected in the report JSON (Section 6).
- **`skip`** — defer: not applied this run, but eligible for future apply runs (the report JSON entry is left unchanged).

For issues flagged `ambiguous` in Section 2.4 (multiple matches in source): before accept/reject, the user must select which occurrence. List occurrences with surrounding context; the user picks one or rejects.

For issues flagged `conflict` in Section 2.4 (zero matches): present the issue with a note `"source no longer contains this text — may have been edited or applied previously"`. The user may still `reject` or `skip`; `accept` is disabled unless the user supplies an offset hint (out of scope for Phase 1; document as `skip` for now).

### 4.3 Sort edits in document order

Once all edits are collected (auto + interactive accepts), sort the planned-edit list by `source_offset_start` ascending. Ties at the same offset (rare but possible if two issues target overlapping spans) are resolved by adopting only one — see 4.5 conflict detection.

### 4.4 Compose the diff

Apply edits to a working copy of the source file in **REVERSE source-offset order** (highest offset first). Reverse order ensures that each edit's recorded offsets remain valid as later-in-file edits change file length first.

Generate a unified diff between the original source and the working copy. Use 3 lines of context. The diff is what the user sees at the confirmation step; the working copy is what gets written if the user confirms.

For bibliography edits (e.g., `bibliography-orphan` resulting in entry deletion), the edit is a line-range deletion in the bibliography section rather than an inline replacement. Compute the offset of the entry's first character and the offset one past its trailing newline; replacement is the empty string. Bibliography edits sort alongside in-text edits in 4.3 by their source offset.

### 4.5 Detect conflicts

A conflict occurs when:

- An issue's `current` text no longer matches the source (file changed since report generation — already flagged in 2.4 as `conflict`).
- Multiple matches for `current` and the user did not disambiguate (already flagged as `ambiguous`).
- Two edits target overlapping or adjacent source spans (e.g., an auto-staged lexicon swap inside an interactive-accepted sentence rewrite). Detect by checking, after 4.3 sort, that consecutive edits have `edits[i].source_offset_end <= edits[i+1].source_offset_start`. If overlap: drop the lower-priority edit, surface the conflict to the user at the confirmation step.

Conflicts are reported to the user; they are **not** included in the diff. The user can resolve them manually (edit the source by hand) and rerun apply.

---

## Section 5: Show diff and confirm

This step is **mandatory**. NEVER write to the source file without an explicit confirmation, even when every staged edit is a high-confidence mechanical fix.

Present to the user:

- The unified diff (3 lines of context).
- Run summary:
  - `N auto-applied` — auto-staged in 4.1
  - `M interactive-accepted` — accepted in 4.2
  - `K rejected` — rejected in 4.2
  - `L skipped` — deferred in 4.2
  - `J conflicts` — surfaced in 4.5; not in the diff
- Optional per-type or per-priority breakdown if the run touches more than a handful of issue types.

Accept one of:

- **`confirm`** / **`yes`** / **`apply`** — write the diff (Section 6).
- **`cancel`** / **`no`** — abort. The source file is untouched. The report JSON is untouched. No state is recorded.
- **`edit`** — out of scope for Phase 1. Tell the user: `"in Phase 1, edit-the-diff is not supported; either confirm to apply as shown, or cancel and re-run apply with different filters / different accept-with-edit responses"`.

---

## Section 6: Write and record

On confirmation:

1. **Write the modified source.** Atomic: write the working copy to a temp file in the same directory (`<source>.marginalia-tmp-<pid>`), then `rename`/`mv` over the original. Never write partial content directly to the source.

2. **Update the report JSON.** Non-destructively — never modify any of the issue's original fields. For each issue, add fields:
   - Auto-applied or interactive-accepted: `"applied": true, "applied_at": "<ISO 8601 UTC timestamp>", "decision": "accepted"` (or `"accepted_with_edit"` if the user supplied custom text in 4.2; in that case also add `"applied_text": "<user-supplied text>"`).
   - Rejected: `"applied": false, "applied_at": "<ISO 8601 UTC timestamp>", "decision": "rejected"`.
   - Skipped: leave the issue record unchanged. (A future apply run will re-evaluate.)
   - Conflict: `"applied": false, "applied_at": "<ISO 8601 UTC timestamp>", "decision": "conflict"`, plus `"conflict_reason": "<source drift | ambiguous match | overlap with <other_id>>"`.

3. **Append a run record to the JSON.** Top-level `apply_runs` array (create if absent). Each entry:
   ```json
   {
     "run_id": "<YYYY-MM-DD-HHMM>-apply",
     "applied_at": "<ISO 8601 UTC>",
     "filters": {"priority": [...], "types": [...], "ids": [...]},
     "counts": {"auto_applied": N, "interactive_accepted": M, "rejected": K, "skipped": L, "conflicts": J}
   }
   ```

4. **Report to the user:**
   - Total edits applied
   - Path to the modified source file
   - Path to the updated report JSON
   - Conflicts summary (if any), with a hint on how to resolve

---

## Section 7: Citation-specific edit semantics

Citation issues carry richer structure than review issues (per `content/citation-tiers.md` §5b: `citation_text`, `citation_key`, `tier`, `tier_results`, `source_quote`, `doi`). The apply procedure handles them as follows:

### Mechanical citation corrections (auto-stage path)

`citation-year-mismatch`, `citation-author-spelling-mismatch`, `preprint-not-marked`, `citation-title-correction`: the `current` field is the in-text citation text (e.g., `"(Smith, 2003)"`); `proposed` is the corrected citation text (e.g., `"(Smith, 2002)"`). Apply as a straightforward text replacement at the matched offset.

For `preprint-not-marked` specifically, the convention is to append ` (preprint)` after the closing paren of the cite; the producing protocol pre-computes this in `proposed`.

### `citation-hallucinated` (interactive)

When the user chooses `accept`, ask a follow-up: `"delete cite and surrounding clause, delete just the cite, or replace with another work?"`

- **delete cite and surrounding clause** — the user must supply the clause boundary; default to the sentence containing the cite. Stage as a text deletion spanning the clause.
- **delete just the cite** — stage a deletion of the cite text plus any leading whitespace/preceding comma. The user is warned that the surrounding sentence may now read awkwardly and may need manual revision; flag this in the apply run summary.
- **replace with another** — prompt for the replacement citation text. Stage as a text replacement.

Hallucinated-citation edits are delicate; if the user is unsure, `skip` is the safe choice.

### `claim-source-mismatch` (interactive)

The intellectual work is narrowing the surrounding claim, not editing the citation itself. If `proposed != null` (the producing sub-agent suggested a starting rewrite), present it as a starting point and let the user `accept`, `accept with edit`, or supply a fresh rewrite. If `proposed == null`, prompt the user for replacement prose for the surrounding sentence (the `source_quote` field shows what the source actually says — useful context).

### `bibliography-orphan` (interactive)

The action is bibliography pruning, not in-text editing. The `current` text is the bibliography entry's raw line(s). On `accept`, stage a deletion of those lines (offset of first character through one past the trailing newline). Present a separate "Bibliography edits" section in the confirmation diff if both bibliography and in-text edits are staged in the same run.

### `citation-missing-bibliography-entry` (interactive)

The action is either: add the missing entry to the bibliography (intellectual — requires the author to confirm the correct entry text); or correct the in-text cite to match an existing entry. The producing protocol cannot disambiguate — that is the author's call. On `accept`, prompt: `"add new bibliography entry, or correct the in-text cite?"` and handle accordingly.

### Tier-4 advisories

`better-source-suggestion` and `recency-superseded-finding` are advisory. They appear in the interactive listing but most users will `skip` or `reject` them. They do not directly correspond to an edit; if the user `accept`s, they must supply replacement citation text (`accept with edit: <new cite>`).

### `tier-error`

Present in the interactive listing as informational only. The only useful actions are `skip` (re-run cite later) or `reject` (acknowledge and drop from the report). Auto-applicable is always false.

---

## Section 8: Edge cases

- **Target file moved or renamed since report generation.** Section 2.3's fallback paths fail. Error: `source file not found at any of: <list>`. Suggest: re-run with `--target=<new_path>` (Phase 1 documents this; the `--target` flag itself is a stub for Phase 2). For now, the user must restore the file at the recorded path, or copy the report directory to sit alongside the new source.
- **Source file has been completely rewritten.** Bulk conflict: all or most issues fail Section 2.4 text-anchoring. The run header surface this as `"<N> of <total> issues no longer anchor in source; consider re-running /marginalia review and /marginalia cite to regenerate the report"`. Proceed if the user wants to handle the few remaining issues; abort cleanly if all fail.
- **Report contains zero auto-applicable issues.** Skip the auto-stage section in 4.1; go straight to interactive in 4.2. The confirmation step still runs.
- **User confirms with no edits to apply** (all rejected or skipped in interactive). Exit cleanly with no diff written. Update the report JSON with the rejection records per Section 6 step 2.
- **Apply on a `-full.md` orchestrator report.** The `-full.md` indexes both a review and a cite report. Phase 1: detect the `-full.md` shape (no `issues` array at top level; contains links to two reports), tell the user `"run apply on the individual reports: /marginalia apply <review-path> and /marginalia apply <cite-path>"`, exit. Phase 2 may aggregate; Phase 1 keeps it simple.
- **Same source file targeted by multiple recent reports.** Phase 1: each apply invocation handles one report at a time. If the user applies report A then report B on the same source, B's apply will see the source has drifted from A's perspective (text-anchoring re-runs in 2.4) — most of B's issues should still anchor, but any that target text A changed will surface as conflicts. Future apply runs of B will see A's recorded `applied: true` markers in the JSON if A is the same report; but B is a different report so it does not see A's markers. Document this clearly. Phase 2 may add cross-report awareness.
- **Source file under version control (git).** Apply does not interact with git. The user is responsible for committing or reverting the post-apply state. The atomic write in 6.1 means a `git diff` post-apply shows exactly what changed.
- **Report JSON manually edited by user since generation.** If validation in 2.2 passes, apply proceeds — user edits are honored. If validation fails, error per 2.2.

---

## Section 9: Output discipline

The apply skill MUST:

- **Never silent-write.** The confirmation step (Section 5) is mandatory and unskippable, even for runs containing only high-confidence mechanical fixes.
- **Always show a diff before any write.** No "trust me" mode.
- **Always record decisions in the report JSON** (Section 6 step 2). Every issue the user saw gets `applied: true|false` and `decision`.
- **Never modify the report's original issue fields.** Apply only adds `applied`, `applied_at`, `decision`, `applied_text`, `conflict_reason` keys. The original `current`, `proposed`, `confidence`, `rationale`, etc., are preserved verbatim for audit.
- **Never write to a source that does not exist** (Section 2.3 failure paths). Errors precede writes.
- **Atomic source writes only** (Section 6 step 1). No partial-file writes that could leave the source corrupted on crash.

---

## Worked example — applying a review report with 7 issues

Suppose `marginalia-review` produced `proposal.md.marginalia/2026-05-15-1142-review.md` and its `.json` sidecar with 7 issues:

- `R-001` — `ai-drift-opener-in-recent-years`, HIGH, `auto_applicable: false`, `proposed: null`
- `R-002` — `ai-drift-bullets-in-argument`, HIGH, `auto_applicable: false`, `proposed: null`
- `R-003` — `ai-drift-tricolon`, MEDIUM, `auto_applicable: true`, `proposed: "contextual and dynamic — and emergent under conditions where ..."`, `confidence: 0.85`
- `R-004` — `ai-drift-verb`, MEDIUM, `auto_applicable: true`, `current: "delve"`, `proposed: "examine"`, `confidence: 0.85`
- `R-005` — `ai-drift-adjective`, MEDIUM, `auto_applicable: true`, `current: "crucial"`, `proposed: "central"`, `confidence: 0.85`
- `R-006` — `ai-drift-adjective`, MEDIUM, `auto_applicable: true`, `current: "robust"`, `proposed: "well-supported"`, `confidence: 0.85`
- `R-007` — `argumentative-claim-buried`, MEDIUM, `auto_applicable: false`, `confidence: 0.65`

User runs: `/marginalia apply proposal.md.marginalia/2026-05-15-1142-review.md`

**Section 2.1:** `.json` companion found.

**Section 2.2:** JSON validates.

**Section 2.3:** `target` resolves to `./proposal.md`.

**Section 2.4:** All 7 issues' `current` text anchors uniquely in the source. No drift, no ambiguity.

**Section 3.1:** No filters, all 7 eligible.

**Section 3.2 classification:**
- `R-001, R-002, R-007`: `auto_applicable: false` in JSON → interactive.
- `R-003`: `ai-drift-tricolon`, auto-applicable, `confidence=0.85 >= 0.85`, `proposed != null` → auto-stage.
- `R-004`: `ai-drift-verb`, auto-applicable, `confidence=0.85 >= 0.80` → auto-stage.
- `R-005, R-006`: same → auto-stage.

**Section 4.1:** 4 auto-staged edits, offsets recorded.

**Section 4.2:** 3 interactive issues presented in order (R-001 high, R-002 high, R-007 medium):
- R-001 (opener "In recent years,"): user supplies rewrite as `accept with edit: "Since 2018,"`.
- R-002 (bullets): user `rejects` — keeps the list.
- R-007 (buried claim): user `skips` — wants to think about it.

**Section 4.3:** 5 edits in document order (4 auto + R-001 accepted-with-edit).

**Section 4.4:** Apply in reverse offset order; generate unified diff with 3-line context.

**Section 4.5:** No conflicts.

**Section 5:** Show diff. Summary: `4 auto-applied, 1 interactive-accepted (with edit), 1 rejected, 1 skipped, 0 conflicts`. User confirms.

**Section 6:**
1. Atomic write `proposal.md`.
2. Update JSON: R-001 marked `applied: true, decision: accepted_with_edit, applied_text: "Since 2018,"`; R-002 marked `applied: false, decision: rejected`; R-003–R-006 marked `applied: true, decision: accepted`; R-007 unchanged (skipped).
3. Append run record to `apply_runs`.
4. Report: `"5 edits applied to proposal.md; 1 issue rejected, 1 skipped. Report JSON updated."`

If the user later runs `/marginalia apply proposal.md.marginalia/2026-05-15-1142-review.md` again, R-007 will be presented again (skip preserves eligibility); R-002 will not (rejection is recorded); R-001 and R-003–R-006 will not anchor in source (their `current` text was replaced) — they surface as `conflict` in 2.4 with `decision: accepted` from the prior run, and apply notes them as "already applied in earlier run".

---

## Operational notes

- The apply skill is the only marginalia component that writes to the source file. Review and cite produce reports; apply applies them. This separation is load-bearing — never blur it.
- Mechanical changes that auto-stage are still subject to the confirmation step in Section 5. A user who runs `apply` with `--ids=R-004` on a single word swap still sees a diff and confirms.
- Interactive prompts should be terse: one line of issue summary, one line of context, the question. Long prompts encourage rubber-stamping. Apply is a careful tool.
- The report JSON is append-only at apply time. This preserves the full audit trail: future tooling can reconstruct what every issue looked like at report-generation time, what decision was made, and when.
- Citation issues with overlapping spans (e.g., a `citation-year-mismatch` inside a sentence flagged for `claim-source-mismatch`) are common. The Section 4.5 overlap detection catches them; the user resolves manually.
