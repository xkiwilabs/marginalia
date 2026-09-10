# Citation verification — four-tier protocol

The procedure `marginalia-verify-cites` follows. Loaded once at the start of every run. The SKILL.md is a thin entry point; this file is the actual orchestration. The per-citation work happens inside parallel sub-agents driven by `content/sub-agent-prompt.md` — this protocol describes WHAT the orchestrator does and HOW it dispatches; the sub-agent prompt describes WHAT each sub-agent does once dispatched.

Inputs may be Markdown, PDF, docx, doc, rtf, or odt; non-Markdown inputs are auto-converted per `content/input-ingestion.md` before Phase A. Output: a paired Markdown report + JSON companion, written alongside the review report in `<target>.marginalia/` (where `<target>` is the user-given path, including its original extension). The JSON drives `marginalia apply`.

Three phases, in order:

- **Phase A — Extraction.** Sequential, cheap. Find every in-text citation in the target, find the bibliography, cross-check both sides. Produces a `cites_inventory` and a list of Phase A issues (orphans, year mismatches, spelling mismatches).
- **Phase B — Per-citation verification.** Parallel. One sub-agent per unique cite, capped at `concurrency_cap` simultaneous agents. Each runs up to four tiers and returns structured JSON.
- **Phase C — Aggregation.** Sequential. Merge Phase A and Phase B results, sort, assign stable `C-NNN` IDs, write the paired reports.

Where a section says "if X, error", produce the error and stop — do not produce a partial report.

---

## Section 1: Inputs

- **`target`** (required) — one of:
  - path to a markdown file (`proposal.md`)
  - path with section anchor (`proposal.md#Process-accounts-of-intelligence`) — same anchor-resolution rules as the review protocol
  - pasted text (string, no file)
- **`tiers`** (optional) — comma-separated subset of `{1,2,3,4}`. Default: `1,2,3,4`. Tier 1 is always run; if the user passes a subset that omits Tier 1, treat it as a fatal user error and stop (every downstream tier depends on Tier 1's resolution of the work).
- **`bibliography`** (optional) — path, or `path#Anchor`, pointing at a `## References` section. Default: auto-detect in `target` per A.3.
- **`concurrency_cap`** (optional) — maximum simultaneous sub-agents. Default `8`. If more unique cites than the cap, queue and dispatch additional batches as agents complete.
- **`tier_3_paywall_policy`** (optional) — `confidence_low` (default) | `skip`. What to do when only the abstract is available for Tier 3. `confidence_low` runs Tier 3 against the abstract and marks `confidence: low` on any resulting issue. `skip` returns `{status: "skipped", reason: "paywalled; abstract only"}` and emits no Tier 3 issues.

Unknown flags: record under `ignored_flags` in the report header, proceed.

---

## Section 2: Phase A — Extraction

### A.1 Resolve target

**Ingest non-Markdown formats first.** If the target's extension is not `.md` or `.markdown`, follow `content/input-ingestion.md` to obtain the Markdown equivalent before proceeding. From this point on, "the target" refers to the resulting Markdown file. The user's original source file is never modified, and cite-location coordinates in the report are relative to the converted Markdown. The bibliography (A.3) is auto-detected within the converted Markdown unless an explicit `--bib` path is supplied. Record `input_format`, `input_converted`, and `converter` in the report header per `content/input-ingestion.md` §5.

Then apply the same rules as the review protocol (`content/review-protocol.md` §2):

- **Path, no anchor.** Load the entire file. `line_offset = 0`.
- **Path with section anchor.** Load the file, match the anchor case-insensitively (normalising whitespace and replacing `-` with space), slice from the line after the anchor to the line before the next header at the same or higher level. Record `line_offset` so issue locations stay in source-file coordinates.
- **Pasted text.** Use as-is. `target_path = stdin-<YYYY-MM-DD-HHMM>` (UTC). `line_offset = 0`.
- **Missing file.** Error: `target not found: <path>`. Stop.
- **Empty target.** Proceed with zero cites and emit a minimal report (Section 7).

### A.2 Detect inline citations

Use these regex patterns. **Apply in order; the FIRST match wins for any text span.** Order is intentional: longest / most-specific patterns first so that a multi-cite parenthetical is not mis-detected as a single-author parenthetical, and a two-author cite is not mis-detected as a single-author cite.

1. **Multi-cite parenthetical:**
   `\(([A-Z][a-zA-Z'\-]+(?:\s*(?:&|and)\s*[A-Z][a-zA-Z'\-]+|\s+et\s+al\.?)?,?\s*\d{4}[a-z]?(?:;\s*[A-Z][a-zA-Z'\-]+(?:\s*(?:&|and)\s*[A-Z][a-zA-Z'\-]+|\s+et\s+al\.?)?,?\s*\d{4}[a-z]?)+)\)`
   — splits into individual cites by `;`. Example: `(Smith, 2003; Brown et al., 2021)`.
2. **Two-author parenthetical:**
   `\(([A-Z][a-zA-Z'\-]+)\s*(?:&|and)\s*([A-Z][a-zA-Z'\-]+),?\s*(\d{4}[a-z]?)\)`
   — e.g., `(Garcia & Lee, 2018)`.
3. **Multi-author parenthetical:**
   `\(([A-Z][a-zA-Z'\-]+)\s+et\s+al\.?,?\s*(\d{4}[a-z]?)\)`
   — e.g., `(Brown et al., 2021)`.
4. **Single-author parenthetical:**
   `\(([A-Z][a-zA-Z'\-]+),?\s*(\d{4}[a-z]?)\)`
   — e.g., `(Smith, 2003)`.
5. **Two-author narrative:**
   `([A-Z][a-zA-Z'\-]+)\s+(?:&|and)\s+([A-Z][a-zA-Z'\-]+)\s+\((\d{4}[a-z]?)\)`
   — e.g., `Garcia and Lee (2018)`.
6. **Multi-author narrative:**
   `([A-Z][a-zA-Z'\-]+)\s+et\s+al\.?\s+\((\d{4}[a-z]?)\)`
   — e.g., `Brown et al. (2021)`.
7. **Single-author narrative:**
   `([A-Z][a-zA-Z'\-]+)\s+\((\d{4}[a-z]?)\)`
   — e.g., `Jones (2019)`.

For each match, record a `cite_record`:

- `citation_text` — exact source text (the matched span, trimmed of trailing punctuation)
- `authors` — list of author surnames (one for single-author, two for two-author / narrative, one for `et al.` styles)
- `is_et_al` — boolean
- `year` — string, with optional disambiguation letter (e.g., `"2003a"`)
- `style` — `"parenthetical"` | `"narrative"`
- `location` — `{line_start, line_end, char_start, char_end}` in source-file coordinates (apply `line_offset`)

**Parsing rules — important:**

- **Skip matches inside fenced code blocks** (`` ``` `` or `~~~`) **or HTML comments** (`<!-- ... -->`). The fixture's planted issues are inside an HTML comment; those must not be counted as in-text cites.
- **Multi-cite parentheticals:** generate one `cite_record` per cite within the group, sharing the outer `location` span but with distinct `citation_text` (split on `;` and re-wrap in parens for display).
- **Trim trailing punctuation** from `citation_text` (a comma after the closing paren bleeds in if the regex is greedy).
- **Unicode-aware author names:** the character class `[A-Z][a-zA-Z'\-]+` covers `O'Brien`, `Lévy-Bruhl` only if the regex engine is Unicode-aware. Use a Unicode flag (`re.UNICODE` in Python; `u` flag in JS). If the runtime cannot handle Unicode in the class, fall back to allowing `\p{L}` where supported; otherwise note the limitation in the report header.
- **Year regex `\d{4}[a-z]?`** matches the four-digit year plus an optional disambiguation letter (`2003a`, `2003b`). Years 1500–2099 are reasonable in scholarly prose; the regex does not enforce this — out-of-range years (e.g., `(Smith, 1066)`) pass through to Tier 1 and will either resolve or fail there.
- **Narrative cite false positives:** the single-author narrative pattern (`Jones (2019)`) can match legitimate non-citation prose like `Section 4 (2019)` if a section heading happens to be a year — rare, but if Tier 1 returns "no plausible match and the surrounding text does not read like a citation", the sub-agent may downgrade to a `tier_1_skipped_likely_not_citation` note rather than a hallucination flag.

**Deduplication.** After all matches, deduplicate by `(first_author_surname, year)` to produce a `unique_cites` list. Each unique entry tracks its `locations: [...]` (one per appearance). Sub-agent dispatch is per unique cite, not per appearance.

### A.3 Detect bibliography

Look for the bibliography section in this order. Stop at the first hit.

1. **A markdown heading.** Regex (case-insensitive on the trailing word): `^#{1,2}\s+(References|Bibliography|Works\s+Cited)\s*$`. The bibliography is every line between this heading and the next heading at the same or higher level (or end of file).
2. **Trailing reference-like block.** If no heading was found, walk the file from the end backward. The bibliography is the last consecutive block of non-blank lines where each line matches a reference-like pattern: starts with `[A-Z][a-zA-Z'\-]+,` (surname-then-comma) **or** contains a year in parentheses `\(\d{4}[a-z]?\)`. Stop the block at the first non-matching line.
3. **Nothing.** Treat the target as having no bibliography. Skip orphan checks (Section A.4) entirely. Note `no bibliography section detected; orphan checks skipped` in the report header.

If the user passed an explicit `bibliography` input, that takes precedence — load and slice it the same way as A.1 resolves a target with anchor.

For each entry in the bibliography, parse:

- `first_author_surname` — the leading surname before the first comma
- `year` — four-digit year, possibly with disambiguation letter
- `title` — best-effort: the italicised or quoted portion, or everything after the year through the next `.`
- `venue` — best-effort: italicised journal/book title after the title
- `doi` — if present, the DOI string (regex `10\.\d{4,9}/[-._;()/:A-Za-z0-9]+`)
- `raw` — the full line(s) of the entry

Bibliography entries can span multiple lines (hanging indent). Treat consecutive non-blank lines as one entry; a blank line ends an entry. The `cites_inventory` later uses `first_author_surname + year` as the **lookup key**. If multiple entries share the same key, append disambiguation letters in the order they appear (`Smith-2003a`, `Smith-2003b`) and note this in the inventory.

### A.4 Cross-check (orphan and mismatch detection)

This step is the source of all Phase A issues. It runs **bidirectionally** between `unique_cites` (from A.2) and bibliography entries (from A.3). If A.3 returned no bibliography, skip this step.

**Direction 1 — in-text → bibliography:**

- **`citation-missing-bibliography-entry`** (high priority). Every unique `(first_author_surname, year)` in `unique_cites` must map to a bibliography entry with the same key. No match → issue:
  - `current = citation_text` of the first appearance
  - `proposed = null`
  - `auto_applicable = false`
  - `rationale`: `"In-text citation has no matching entry in the references section."`
- **`citation-year-mismatch`** (high priority). The in-text cite's author surname matches a bibliography entry's author surname, but the years differ by ≤2 (likely a typo, not a different work). Single closest match wins; if multiple bibliography entries match the author with different years, prefer the entry whose year is closest. Issue:
  - `current = citation_text` (e.g., `"(Smith, 2003)"`)
  - `proposed = citation_text with the bibliography's year` (e.g., `"(Smith, 2002)"`)
  - `auto_applicable = true`
  - `confidence = 0.85`
  - `rationale`: `"In-text year differs from bibliography entry (in-text: 2003, references: 2002). Mechanical correction applied to match the references."`
- **`citation-author-spelling-mismatch`** (medium priority). The year matches a bibliography entry exactly, but the author surname differs by 1–2 characters (Levenshtein) — e.g., in-text `Brown`, references `Browne`. Issue:
  - `current = citation_text`
  - `proposed = citation_text with the bibliography's spelling`
  - `auto_applicable = true`
  - `confidence = 0.80`
  - `rationale`: `"In-text author spelling differs from references entry by N characters; mechanical correction applied."`

**Direction 2 — bibliography → in-text:**

- **`bibliography-orphan`** (low priority). Every bibliography entry's `first_author_surname + year` key must appear at least once in `unique_cites`. Unreferenced entries → issue:
  - `current = bibliography_entry.raw` (truncated to 120 chars in the markdown report)
  - `proposed = null`
  - `auto_applicable = false`
  - `location`: the bibliography entry's line span
  - `rationale`: `"References entry has no matching in-text citation."`

**Edge case — totally mismatched bibliography.** If no in-text cites match any bibliography entry at all (zero overlap), emit a single high-priority `bibliography-mismatch-suspected` issue flagging the entire bibliography for author review, instead of dozens of orphan + missing-entry issues. Threshold: bibliography has ≥3 entries AND zero match the in-text cites' keys.

---

## Section 3: Phase B — Per-citation verification (parallel sub-agents)

### B.1 Dispatch model

For each entry in `unique_cites`:

1. Construct a sub-agent prompt that:
   - Tells the sub-agent to load and follow `content/sub-agent-prompt.md` from the marginalia repo.
   - Passes the structured inputs listed below.
2. Dispatch via the Agent tool with `subagent_type=general-purpose` and `run_in_background=true`.
3. Track each dispatch by `(citation_key, agent_id)`, where `citation_key = "<first_author_surname>-<year>"` (e.g., `"Wexler-2024"`).

**Structured inputs to each sub-agent:**

- `citation_text` — the exact in-text text (one representative `citation_text` per unique cite; use the first appearance).
- `citation_key` — `"<first_author_surname>-<year>"`.
- `authors`, `is_et_al`, `year` — from the `cite_record`.
- `surrounding_paragraph` — the full paragraph (text between blank lines) containing the first appearance of the cite. This is the **claim context** for Tier 3.
- `bibliography_entry` — the matching reference list entry's raw text, or the string `"not found"` if the cite is a Phase A orphan.
- `tiers_to_run` — array, e.g., `[1, 2, 3, 4]`. From the user's `--tiers` flag.
- `tier_3_paywall_policy` — `"confidence_low"` | `"skip"`. From inputs.

**Concurrency cap.** At any moment, at most `concurrency_cap` (default 8) sub-agents are dispatched. If `len(unique_cites) > concurrency_cap`, queue the remainder; as each sub-agent returns, dispatch the next one. This keeps Crossref/Semantic Scholar/OpenAlex within reasonable per-host rate-limit windows.

**Phase A cites that are already orphans still get dispatched.** A Phase A orphan (no bibliography entry) does not preclude existence — the work may exist, the author just forgot to add it to the references. Tier 1 either confirms (in which case the orphan issue stands but is more useful — author can add the entry) or fails (in which case the work is likely hallucinated AND missing from the bibliography, which compounds the issue).

### B.2 Tier descriptions (overview)

Full execution detail (queries, parsing, rate-limit handling) lives in `content/sub-agent-prompt.md`. This section documents WHAT each tier does so the caller understands the cost / value tradeoff and so the orchestrator can interpret sub-agent return values.

- **Tier 1 — Existence & accuracy.** Verify the cited work exists. Correct author / year / title / venue if a high-confidence match is found.
  - Sources, in order: Crossref API (free, primary), Semantic Scholar API (fallback), WebSearch (last resort).
  - **Match criteria:** first-author-surname match (exact, case-insensitive, after stripping accents) **AND** year ±1 **AND** title-similarity ≥ 0.7 (normalised Levenshtein on lowercased title; if no title in the in-text cite, similarity check is skipped and the (author, year, venue) triple is the only signal).
  - **Failure mode:** `citation-hallucinated` (high priority, not auto-applicable). The sub-agent returns `{tier_1: {status: "not_found", searched: [...], best_match: null}}`.
  - **Correction mode:** if Tier 1 finds the work but with a different title/venue/year, return `{status: "corrected", doi, corrections: {...}}`. The orchestrator emits a `citation-title-correction` issue (medium, auto-applicable when `confidence ≥ 0.85`).

- **Tier 2 — Source reputability.** Check the venue. Runs only if Tier 1 succeeded; otherwise skipped with `reason: "Tier 1 failed"`.
  - **Peer-reviewed signal.** OpenAlex `is_peer_reviewed` field; DOAJ membership for the venue.
  - **Preprint signal.** DOI prefix matches arXiv (`10.48550/`), bioRxiv (`10.1101/`), PsyArXiv (`10.31234/`), SSRN, etc. If the in-text citation text does not include "preprint" qualifier → `preprint-not-marked` (medium, auto-applicable — append ` (preprint)` to the cite).
  - **Predatory heuristics.** See Section B.3.
  - **Failure modes:** `predatory-venue-suspected` (medium), `preprint-not-marked` (medium), `pay-to-publish-venue` (low, advisory).

- **Tier 3 — Claim–source match.** Compare the in-text claim (drawn from `surrounding_paragraph`) against what the source actually argues. Runs only if Tier 1 succeeded.
  - Fetch abstract (always available via Crossref or Semantic Scholar). If the source is open access (OpenAlex `is_oa=true` or Semantic Scholar `openAccessPdf`), fetch the full text or key passages.
  - **Conservative flagging.** Flag only when the in-text claim is one of:
    - **OVERGENERALIZED** — the claim is more sweeping than the source supports (e.g., in-text says "uniformly impaired across" when the source reports a heterogeneous effect with confidence intervals crossing zero in some sub-populations).
    - **DIRECTIONALLY WRONG** — the source argues the opposite of the in-text claim.
    - **DOMAIN-MISMATCHED** — the source's findings are about a narrower or different domain than the in-text claim extends them to.
  - Do **not** flag mere imprecision, paraphrase, or compatible inference. False positives are still possible at Tier 3 and are explicitly accepted (per the spec) over silent passes.
  - **Failure mode:** `claim-source-mismatch` (high, not auto-applicable). The sub-agent returns `source_quote` — the passage from the source that contradicts or fails to support the claim.
  - **Paywall handling.** If only the abstract is available, behavior follows `tier_3_paywall_policy`: `confidence_low` runs Tier 3 against the abstract with `confidence: low` on any issue (default); `skip` returns `{status: "skipped", reason: "paywalled; abstract only"}`.

- **Tier 4 — Better-source + recency.** Advisory only — Tier 4 never marks the cite as failed. Runs only if Tier 1 succeeded.
  - Find:
    - The original empirical source if the cite is a review / commentary being used for a specific empirical claim.
    - Meta-analyses or replications published since the citation year that update the picture.
    - Higher-impact canonical sources for the same claim if the cite is to a low-impact paper.
  - **Output:** issues of type `better-source-suggestion` (advisory) and `recency-superseded-finding` (advisory). Both go to the "Better-source suggestions" section of the report. Cap at top 5 by relevance per sub-agent.

**Tier status values.** Each tier in the sub-agent's return JSON has a `status` field:

- `"pass"` — tier completed and found no issue.
- `"fail"` — tier completed and found an issue (the sub-agent populates the issue body).
- `"corrected"` — Tier 1 found the work but with corrections to author/year/title/venue.
- `"skipped"` — tier was not run; `reason` populated (e.g., `"Tier 1 failed"`, `"paywalled; abstract only"`, `"user excluded"`).
- `"tier_error"` — tier attempted but all sources failed; `reason` populated.

### B.3 Predatory venue heuristics (Phase 1)

Beall's list is unmaintained and was taken down in 2017; Cabells is paywalled and not redistributable. Phase 1 uses a heuristic combination plus a small curated list. This section documents the Phase 1 limitations explicitly — treat predatory-venue flags as suggestive, not authoritative, and prefer the `pay-to-publish-venue` advisory severity for borderline cases.

**Heuristic signals (combine; ≥2 triggers `predatory-venue-suspected`):**

- OpenAlex `apc_paid = true` AND venue has been cited fewer than 100 times across OpenAlex's record.
- DOI prefix or publisher name appears in the strong-signal list below.
- Venue is not indexed in DOAJ, Scopus, or Web of Science.
- Venue's editorial board page is missing or stub on the publisher site (manual signal only; not auto-checkable in Phase 1).

**Curated list (inline; Phase 1 simplicity — does not live in a separate file):**

*Strong predatory signals* → emit `predatory-venue-suspected` (medium, not auto-applicable):
- OMICS Publishing
- Scientific Research Publishing (SCIRP)
- Bentham Open
- Hilaris Publisher
- Longdom Publishing
- David Publishing Company

*Borderline / pay-to-publish but not predatory* → emit `pay-to-publish-venue` (low, advisory only — may not be acted on, just surfaced):
- MDPI journals
- Frontiers journals (post-2015 editorial controversies)
- Hindawi journals (post-2017 ownership changes; flag advisory)
- PLOS ONE (high volume, light editorial review)

**Open question for Phase 2:** integrate OpenAlex's full venue quality signals (`type`, `homepage_url`, `works_count`, citation distribution) rather than relying on a curated list. Cabells API access would also displace the curated list if licensing can be arranged.

### B.4 Error handling

**Per sub-agent:**

- **Timeout.** 10 minutes per sub-agent. If the Agent tool surface supports a timeout argument, set it there; otherwise the orchestrator waits and records `tier_error` for sub-agents that have not returned at the 10-minute mark. Do not block the whole run on one stuck sub-agent — collect what has returned and proceed.
- **API failure for a single source.** If Crossref returns an error, fall back to Semantic Scholar; if Semantic Scholar fails, fall back to WebSearch. Per-source failures are normal and not reported.
- **All sources fail for a tier.** Return `{"status": "tier_error", "reason": "all sources unavailable"}` for that tier and continue to the next tier (e.g., a Tier 2 failure does not block Tier 3 from running — the sub-agent decides per-tier).
- **Rate limits.** Respect `429 Too Many Requests`. Back off with exponential wait (2s, 4s, 8s, 16s); after the 4th retry, treat as an API failure for that source and fall back.

**Orchestrator-level:**

If a sub-agent returns malformed JSON, never returns, or returns a `tier_error` for Tier 1, record the citation as a `tier-error` issue:

```
{type: "tier-error", priority: "medium", auto_applicable: false,
 rationale: "Verification could not complete for this citation; re-run later."}
```

Do not silently drop tier-erroring citations. The user needs to know what was and was not checked.

---

## Section 4: Phase C — Aggregation

After all sub-agents have returned (or timed out):

### C.1 Roll up per-citation results

For each entry in `unique_cites`:

1. Gather the matching Phase A issues (from A.4) by `citation_key`.
2. Gather the sub-agent's tier-result JSON.
3. Determine the citation's overall **verification status**:
   - `verified` — every tier that ran returned `status: "pass"` or `status: "corrected"` (with corrections noted as low-severity issues, not failures), and no Phase A issues attached.
   - `flagged` — at least one tier returned `fail`, or there is at least one Phase A issue, at any severity.
   - `error` — at least one tier returned `tier_error`, or the whole sub-agent never returned.

### C.2 Generate issue records

For each issue (Phase A cross-check failure or Phase B tier failure), produce an issue record per the JSON schema in Section 5.

- `citation_key` is added to every citation-skill issue.
- `tier` is `null` for Phase A issues; `1`/`2`/`3`/`4` for Phase B issues.
- `doi` is populated when known (e.g., Tier 1 succeeded), `null` otherwise.
- `source_quote` is populated only for `claim-source-mismatch` (Tier 3), `null` otherwise.

**Phase A / Tier 1 merge rules.** Phase A.4 and the sub-agent's Tier 1 can produce overlapping findings for the same cite. Apply these deduplication rules during issue generation:

- If Phase A emitted a `citation-year-mismatch` for a cite AND Tier 1 returned `corrected` for that cite where the only field in `corrections` is `year`: suppress the would-be `citation-title-correction` issue (Phase A's finding is more specific). Carry Tier 1's confirmation into the Phase A issue's `rationale` (`"Bibliography year corroborated by Tier 1 record."`) and set `confidence` to `max(0.85, tier_1.confidence)`.
- If Phase A emitted a `citation-author-spelling-mismatch` AND Tier 1 returned `corrected` where corrections include only `author` (or `author` + `year`, with the year matching Phase A's proposed year): suppress the Tier 1 issue; promote Phase A's finding to `confidence = max(0.80, tier_1.confidence)`.
- If Tier 1's `corrections` field contains `title` or `venue` (regardless of year/author): always emit a `citation-title-correction` issue, even if Phase A already emitted a year-mismatch. Title/venue corrections are independent and should surface.
- If Phase A emitted `citation-missing-bibliography-entry` AND Tier 1 returned `not_found`: emit both — the cite is hallucinated AND not in the bibliography. The `citation-missing-bibliography-entry` rationale should note `"compounding: cite is also flagged hallucinated (see C-NNN)."`

### C.3 Sort and assign stable IDs

Sort by `(priority_rank, line_start, char_start, type)` where `priority_rank` is `high=0, medium=1, low=2, advisory=3`. Lexicographic `type` is the final tie-breaker so two issues at the same location land in deterministic order.

Assign `C-001`, `C-002`, ... in sort order. Zero-pad to three digits. If >999 issues (not expected in Phase 1), use four digits (`C-0001`) uniformly.

Stability is per-target-version, not across edits — when line numbers shift, IDs may change. This is identical to the review skill's ID policy.

### C.4 Compute summary

Counts:
- `total_unique_cites` — `len(unique_cites)` from A.2
- `verified` — count where verification status = `verified`
- `critical` — count of high-priority issues
- `reputability_flags` — count of Tier 2 issues
- `claim_source_mismatches` — count of Tier 3 fails
- `suggestions` — count of Tier 4 advisories (after capping per-citation at 5)
- `bibliography_orphans` — count of `bibliography-orphan` issues
- `tier_errors` — count of `tier-error` issues

---

## Section 5: Output

Two files, written to the **same directory the review skill uses**: `<target_directory>/<target_filename>.marginalia/`. For pasted text: `./stdin-<YYYY-MM-DD-HHMM>.marginalia/` in cwd. Create the directory if missing. If a file with the same timestamp exists, append `-2`, `-3`, etc. Never overwrite.

Both files use the same timestamp captured at the start of the skill run.

- `<YYYY-MM-DD-HHMM>-cites.md` — human-readable report
- `<YYYY-MM-DD-HHMM>-cites.json` — structured report with stable IDs

### 5a. Markdown report skeleton

```markdown
# Marginalia citation review: <target>
Generated: <ISO 8601 timestamp>
Cites scanned: <n> unique | Bibliography entries: <n> | Tier coverage: <tiers run>

## Summary
- Critical: <n>
- Reputability flags: <n>
- Claim–source mismatches: <n>
- Better-source suggestions: <n>
- Bibliography hygiene: <n>
- Verified: <n>
- Tier errors: <n>

## Critical issues (n=N)

[Tier 1 hallucinations, Tier 3 mismatches, citation-missing-bibliography-entry, citation-year-mismatch when severity high. Sorted by line.]

### C-001 — line <n>: <type>

**In-text:** <citation_text>
**Bibliography:** <matching entry raw, or "(no entry found)">
**Issue:** <rationale>
**Suggested action:** <if mechanical correction: "replace with X"; if not: "(needs author decision)">
**Confidence:** <confidence>
**Auto-applicable:** <true|false>

[repeat per critical issue]

## Reputability flags (n=N)

[Tier 2 fails: predatory-venue-suspected, preprint-not-marked, pay-to-publish-venue. Same record format.]

## Claim–source mismatches (n=N)

[Tier 3 fails. May overlap with Critical (above) but listed here with the quoted source passage:]

### C-NNN — line <n>: claim-source-mismatch

**In-text claim:** "<surrounding sentence>"
**Cited:** <citation_text>
**Source says:** "<source_quote>"
**Why this is flagged:** <rationale>
**Confidence:** <confidence>

## Better-source suggestions (n=N)

[Tier 4 — advisory only. Compact list grouped by citation_key.]

### For <citation_text>:
- <better source citation>: <one-line reason>
- <better source citation>: <one-line reason>

## Bibliography hygiene (n=N)

[bibliography-orphan, citation-author-spelling-mismatch, bibliography-mismatch-suspected.]

## Verified cites (n=N)

[Compact one-liners.]

- (Smith, 2003) — verified [Tier 1: ✓ (DOI: 10.x), Tier 2: peer-reviewed, Tier 3: claim supported]
- Jones (2019) — verified [Tier 1: ✓, Tier 2: peer-reviewed, Tier 3: claim supported]

## Notes
[Optional meta-observations. Examples: "Tier 3 ran against abstract only for 3 cites (paywalled); confidence is marked low.", "Bibliography contains 2 orphan entries — consider whether they should be cited in-text or removed.", "1 sub-agent timed out for (Author, Year); re-run to retry."]
```

### 5b. JSON report schema

```json
{
  "report_id": "<YYYY-MM-DD-HHMM>-cites",
  "target": "<absolute path or stdin-<timestamp>>",
  "generated_at": "<ISO 8601 UTC timestamp>",
  "tiers_run": [1, 2, 3, 4],
  "concurrency_cap": 8,
  "tier_3_paywall_policy": "confidence_low",
  "ignored_flags": [],
  "summary": {
    "total_unique_cites": 19,
    "verified": 15,
    "critical": 2,
    "reputability_flags": 1,
    "claim_source_mismatches": 1,
    "suggestions": 4,
    "bibliography_orphans": 1,
    "tier_errors": 0
  },
  "issues": [
    {
      "id": "C-001",
      "priority": "high",
      "type": "citation-hallucinated",
      "citation_key": "Wexler-2024",
      "citation_text": "(Wexler, 2024)",
      "tier": 1,
      "location": {"line_start": 47, "line_end": 47, "char_start": 1234, "char_end": 1248},
      "current": "(Wexler, 2024)",
      "proposed": null,
      "confidence": 0.95,
      "auto_applicable": false,
      "doi": null,
      "source_quote": null,
      "rationale": "No matching work in Crossref, Semantic Scholar, or web search; bibliography entry exists but the title and venue do not correspond to any indexed work.",
      "tier_results": {
        "tier_1": {"status": "not_found", "searched": ["Crossref", "Semantic Scholar", "WebSearch"], "best_match": null},
        "tier_2": {"status": "skipped", "reason": "Tier 1 failed"},
        "tier_3": {"status": "skipped", "reason": "Tier 1 failed"},
        "tier_4": {"status": "skipped", "reason": "Tier 1 failed"}
      }
    }
  ],
  "verified_cites": [
    {
      "citation_text": "(Smith, 2003)",
      "citation_key": "Smith-2003",
      "doi": "10.1037/0033-295X.109.2.295",
      "venue": "Psychological Review",
      "tier_1": "found",
      "tier_2": "peer_reviewed",
      "tier_3": "match",
      "tier_4_suggestions_count": 0
    }
  ],
  "notes": ""
}
```

Every field shown is required (use `null` for absent optional values, empty arrays for empty lists, empty strings where shown). Do not add fields not shown; do not omit fields shown. This JSON is the source of truth for `marginalia apply`.

---

## Section 6: Type values (canonical list)

All citation-skill issue types, with default priority, auto-applicable flag, and which phase / tier emits them. The apply mode uses this list to know which corrections it can mechanically apply.

| Type | Priority | Auto-applicable | Emitted by |
|---|---|---|---|
| `citation-hallucinated` | high | false | Tier 1 fail |
| `claim-source-mismatch` | high | false | Tier 3 fail |
| `citation-missing-bibliography-entry` | high | false | Phase A.4 (in-text → bib) |
| `citation-year-mismatch` | high | true (`proposed` = bibliography year) | Phase A.4 |
| `citation-author-spelling-mismatch` | medium | true (`proposed` = bibliography spelling) | Phase A.4 |
| `citation-title-correction` | medium | true when `confidence ≥ 0.85` | Tier 1 `corrected` |
| `predatory-venue-suspected` | medium | false | Tier 2 |
| `preprint-not-marked` | medium | true (append ` (preprint)` to cite) | Tier 2 |
| `pay-to-publish-venue` | low | false (advisory) | Tier 2 |
| `bibliography-orphan` | low | false | Phase A.4 (bib → in-text) |
| `bibliography-mismatch-suspected` | high | false | Phase A.4 edge case |
| `better-source-suggestion` | advisory | false | Tier 4 |
| `recency-superseded-finding` | advisory | false | Tier 4 |
| `tier-error` | medium | false (re-run later) | Orchestrator (B.4) |

`advisory` priority sorts after `low` for the purpose of ID assignment and report ordering. The Tier 4 advisories live in their own report section ("Better-source suggestions") and are excluded from the "Critical" / "Reputability" / "Bibliography hygiene" headings.

---

## Section 7: Edge cases

- **Target with no in-text citations.** Produce a minimal report: `summary.total_unique_cites = 0`, `issues = []`, `verified_cites = []`. Note `"Target contains no detectable in-text citations."` in `notes`. Do not error.
- **Target with no bibliography section.** Skip A.4 entirely. Phase B still runs (existence + reputability + claim match all work without a bibliography). Note `"No bibliography section detected; orphan and year-mismatch checks skipped."` in the report header and `notes`.
- **Citation appears 10+ times in target.** Only verify once. The resulting issue (if any) reports the **first** location in the `location` field and lists the rest in an additional `locations: [...]` array on the issue record (Phase 1 schema extension — every issue record may carry a `locations` array; if absent or single-element, the singular `location` field is canonical). Add a note to the `rationale`: `"This citation appears N times in the target; see issue.locations for all positions."`
- **A single sub-agent reports >5 Tier 4 suggestions.** Cap at top 5 by relevance (the sub-agent does the ranking). Note `"<N> additional Tier 4 suggestions truncated."` in the issue's rationale.
- **Bibliography parses but no entries match any in-text cite at all.** Emit a single high-priority `bibliography-mismatch-suspected` issue flagging the whole bibliography. Suppress the individual orphan / missing-entry issues that would otherwise fire. Author review is the only sensible resolution.
- **In-text cite with no year.** The regex requires `\d{4}`, so naked author references (`as Smith argues`) are not picked up. This is intentional — narrative author references without years are not verifiable as citations.
- **Et al. with different author counts in different locations.** `(Brown et al., 2021)` and `(Brown, Patel, & Chen, 2021)` deduplicate to the same `citation_key` (`Brown-2021`). The sub-agent receives the longest available author list from the cite records.
- **Non-Latin author names.** If the regex's character class does not match (the rules in A.2), the cite is silently skipped — record this in the report header (`"N citations could not be parsed; see notes"`) and surface them in `notes`. Phase 2 will widen to Unicode `\p{L}`.
- **Reference list uses URL or DOI fields with years inside.** The bibliography-detection regex looks for years in parentheses or surname-then-comma at line start; URL years (e.g., `https://example.com/2021/foo`) inside an entry do not falsely create new entries because entry boundaries are blank lines, not year matches.

---

## Worked example — `tests/fixtures/citations-sample.md`

The fixture contains five in-text cites and four planted issues (plus one bibliography orphan).

**Phase A unique_cites:**
- `Smith-2003` — `(Smith, 2003)` at line 18
- `Jones-2019` — `Jones (2019)` at line 18
- `Brown-2021` — `(Brown et al., 2021)` at line 20
- `Garcia-2018` — `(Garcia & Lee, 2018)` at line 20
- `Wexler-2024` — `(Wexler, 2024)` at line 22

The HTML-comment block at the top of the fixture is skipped per A.2.

**Phase A bibliography entries:**
- `Brown-2021`, `Garcia-2018`, `Jones-2019`, `Murphy-2017`, `Smith-2002`, `Wexler-2024`

**Phase A cross-check produces:**
- `citation-year-mismatch` for `(Smith, 2003)` — in-text year 2003, references entry year 2002, author matches. `proposed = "(Smith, 2002)"`, `auto_applicable = true`. (Covers must-catch item: Smith year mismatch.)
- `bibliography-orphan` for the Murphy 2017 entry — no in-text cite. (Covers must-catch item: Murphy orphan.)

**Phase B sub-agents dispatched** (one per unique cite, all five run in parallel since 5 ≤ concurrency_cap=8):

- `Wexler-2024`:
  - Tier 1 — Crossref / Semantic Scholar / WebSearch all return no match for the title "The arithmetic of distributed cognition" by Wexler in 2024. → `status: "not_found"`.
  - Tiers 2 / 3 / 4 — skipped (`reason: "Tier 1 failed"`).
  - Orchestrator emits `citation-hallucinated`, high priority, not auto-applicable, with `doi: null`. (Covers must-catch item: Wexler hallucination.)
- `Brown-2021`:
  - Tier 1 — Found. The actual paper is a meta-analysis with heterogeneity in effect sizes.
  - Tier 2 — `Trends in Cognitive Sciences` is a major peer-reviewed venue. Pass.
  - Tier 3 — `surrounding_paragraph` includes the claim "Metacognitive monitoring is uniformly impaired across major psychiatric and neurodevelopmental conditions" (an OVERGENERALIZATION). The sub-agent fetches the abstract, identifies that the meta-analysis reports heterogeneous effects with confidence intervals crossing zero for some sub-populations, and emits `claim-source-mismatch` with `source_quote` populated. (Covers must-catch item: Brown claim mismatch.)
- `Smith-2003`:
  - Tier 1 — Found at 2002 (matches the bibliography). The Phase A `citation-year-mismatch` already captures the in-text/bib disagreement; the sub-agent's Tier 1 corroborates that 2002 is the correct year. No additional Tier 1 issue beyond the Phase A finding.
- `Jones-2019`, `Garcia-2018`:
  - Tier 1 — Found. Tier 2 — peer-reviewed. Tier 3 — claim supported. Tier 4 — may emit advisories (acceptable, not required by the expected file).

**Phase C produces** (minimum, sorted by priority then line):
- `C-001` (high) — `citation-hallucinated` for `(Wexler, 2024)` at line 22.
- `C-002` (high) — `citation-year-mismatch` for `(Smith, 2003)` at line 18 (`proposed: "(Smith, 2002)"`, `auto_applicable: true`).
- `C-003` (high) — `claim-source-mismatch` for `(Brown et al., 2021)` at line 20 with `source_quote` populated.
- `C-004` (low) — `bibliography-orphan` for Murphy 2017 at line 34.

All four must-catch items in `tests/fixtures/expected/citations-sample.expected.md` are emitted; the JSON shape carries `citation_key`, `tier`, `doi`, and `source_quote` as required by the expected file's "JSON shape" section.

---

## Operational notes

- **Tier 1 is non-negotiable.** Every other tier depends on knowing the work exists; never let the user opt out of Tier 1.
- **Be conservative at Tier 3.** Claim–source match is the highest-value and most-fragile tier. The skill is deliberately conservative: it flags suspicious mismatches with quoted source passages so the author can decide. False positives at Tier 3 are accepted; silent passes on real mismatches are not.
- **Be cautious with predatory-venue flags.** Phase 1's heuristics are a Phase 1 expedient, not authoritative. Prefer `pay-to-publish-venue` (advisory) for borderline cases. Predatory-venue accusations against legitimate (if commercial) publishers create real risk for the author.
- **Surface tier errors, never drop them.** A sub-agent that fails to return for a citation should produce a `tier-error` issue, not a silent gap. The user needs an explicit list of cites that were and were not checked.
- **Parallel dispatch is essential for usability.** A 30-citation paper at Tier 4 takes ~1–3 minutes per citation; serial execution would be 30–90 minutes. The 8-way concurrency cap brings this to 4–12 minutes while staying within free-tier API rate limits.
- **The sub-agent prompt is the bigger half.** This protocol is the orchestration; `content/sub-agent-prompt.md` is where the actual API calls, similarity matching, and Tier 3 conservatism rules live. Read both together when debugging.
