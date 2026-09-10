# Review protocol

> **Paths.** `content/styles/…` and `examples/…` below are names, not locations. Resolve them via `content/paths.md` (`$MARGINALIA_HOME`, then `~/.marginalia/`, then the repo). Resolve once per run and keep the same root throughout.

The procedure `marginalia-review` follows. Loaded once at the start of every review. The SKILL.md is a thin entry point; this file is the actual review.

Inputs may be Markdown, PDF, docx, doc, rtf, or odt; non-Markdown inputs are auto-converted per `content/input-ingestion.md` before any other step. Output: a paired Markdown report + JSON companion. The JSON drives `marginalia apply`.

Follow sections in order. Where a section says "if X, error", produce the error and stop — do not produce a partial report.

---

## Section 1: Inputs

- **`target`** (required) — one of:
  - path to a markdown file (`proposal.md`)
  - path with section anchor (`proposal.md#Process-accounts-of-intelligence`)
  - pasted text (string, no file)
- **`genre`** (optional) — `grants` | `papers` | `devdocs` | `business` | `other`, or any extracted/derived overlay slug (e.g. `blog`); loads `content/styles/{genre}.md`, falling back per the existing missing-overlay handling.

  **When `genre` is not passed, infer it from the target before defaulting.** An
  explicit `--genre` always wins; infer only in its absence, and state the inferred
  genre and the reason in the report header so a wrong inference is visible rather
  than silent.

  | Signal (first match wins) | Inferred genre |
  |---|---|
  | Filename is `README*`, `CONTRIBUTING*`, `CHANGELOG*`, `AGENTS.md`, `CLAUDE.md`, or the path lies under `docs/`, `.github/`, or a source tree (`src/`, `lib/`, `tools/`) | `devdocs` |
  | Extension is `.tex`, or the target contains `\documentclass`, `\begin{abstract}`, or a bibliography marker | `papers` |
  | Extension is `.mdx`, or the path lies under a blog/posts directory | `blog` |
  | Path contains `grant`, `proposal`, `application`, or `fellowship` | `grants` |
  | Filename or path contains `terms`, `pricing`, `LOI`, `letter-of-intent`, `investor`, `onboarding`, `MSA`, `SOW`, `quote`, or `economics`; or the document is a partner/customer/investor-facing commercial document | `business` |
  | none of the above | `grants` (existing default) |

  Genre choice is consequential for Dimension E, not merely cosmetic: reviewing a
  README as `papers` reports its gloss density as −100% against a 2.97/1k baseline
  and flags every em-dash against a zero target, both of which are register
  differences rather than drift. See `content/styles/devdocs.md`.

  The same holds for `business`. A partner terms sheet or investor appendix
  reviewed as `papers` reports a median 15-word sentence as flattening and a 0.0/1k
  gloss rate as −100%, both of which are register. Reviewed as `devdocs` it inherits
  the em-dash carve-out, which is wrong in the other direction: a document a
  counterparty signs is formal, and the zero-em-dash override applies to it in full.
  See `content/styles/business.md`, which also carries the four failure modes
  specific to commercial prose (explaining the concept, instructing the reader,
  narrating the document's own revisions, and volunteering hypothetical
  self-criticism) and the trailing-antithesis tic.
- **Flags** (optional, acknowledge if passed):
  - `--style-overlay-only` — skip Dimensions A and B (the `ai-drift.md` sweep)
  - `--ai-drift-only` — skip Dimension C (style overlay)
  - `--no-argumentative` — skip Dimension D
  - `--paragraphs=N-M` — restrict sweep to paragraphs N–M (1-indexed)

Unknown flags: record under "ignored flags" in the report header, proceed.

---

## Section 2: Resolve target

**Ingest non-Markdown formats first.** If the target path's extension is not `.md` or `.markdown`, follow `content/input-ingestion.md` to obtain the Markdown equivalent before proceeding. From this point on, "the target" refers to the resulting Markdown file (the sibling `.md`); the user's original source file is never modified. Record `input_format`, `input_converted`, and `converter` in the report header per `content/input-ingestion.md` §5.

**A — path, no anchor.** Load the entire file. `line_offset = 0`.

**B — path with section anchor (`path#Anchor-Text`).** Anchor refers to a markdown header.
1. Load the file. Match `Anchor-Text` to a header case-insensitively, normalising whitespace and replacing `-` with space.
2. Record the header's level (`#` = 1, `##` = 2, `###` = 3, etc.).
3. Slice from the line **after** the anchor header to the line **before** the next header at the **same or higher** level. Higher = smaller number (`#` is higher than `##`). If the anchor is `##`, the slice ends at the next `##` or `#`; a `###` between does **not** end the slice. If the anchor is `###`, the slice ends at the next `###`, `##`, or `#`.
4. Record `line_offset` so issue locations are in source-file coordinates.
5. Anchor matches no header → error, listing existing headers (text + level + line). Stop.
6. Anchor matches multiple headers → use the first, warn in the report header.

**C — pasted text.** Use as-is. `target_path = stdin-<YYYY-MM-DD-HHMM>` (UTC). `line_offset = 0`.

**D — missing file.** Error: `target not found: <path>`. Stop.

**E — empty target** (file empty, or slice empty). Proceed with zero paragraphs and emit a minimal report (Section 9).

---

## Section 3: Load context files

Paths are relative to the marginalia repo root.

1. **`content/ai-drift.md`** — required. Missing → error and stop.
2. **`content/styles/base.md`** — optional. Missing → note `no base style available` in report header.
3. **`content/styles/{genre}.md`** — optional. Missing → note `no {genre} overlay available`.
4. **`content/styles/baselines.json`** — optional. Supplies Dimension E's per-genre measured baselines. Missing → Dimension E still runs, but reports only the absolute rules (em-dash presence, colon/semicolon clustering) and omits `baseline-delta` findings. Regenerate with `python3 tools/prose_metrics.py --emit-baseline`.

**Modes:**

- All three style/catalog files loaded → `mode: "full"`, all five dimensions run.
- Only `ai-drift.md` loaded → `mode: "ai-drift-only"`. Dimension C skipped; noted as `skipped (no style overlay)`. A, B, D still run. Dimension E still runs: its counting rules do not depend on a style profile, and the em-dash and punctuation-clustering thresholds come from the catalog and the tool, not from the overlay.
- `--style-overlay-only` with no style files → error and stop.

Record loaded style files (basenames) in the report header.

---

## Section 4: Segment the target

A **paragraph** is a maximal run of non-empty lines separated by blank lines, excluding the categories below.

**Skip entirely (treat as separators, do not review):**
- Markdown headers. Record each crossed so subsequent paragraphs are tagged with `section` (most recent header text).
- Fenced code blocks (`` ``` `` or `~~~`). Skip the whole block.
- Indented code blocks (4-space indent, outside lists).
- Horizontal rules (`---`, `***`, `___` alone on a line).
- YAML frontmatter (`---` block at file start). Count its lines for offset accuracy; don't review.

**Reduced aggression:**
- **Block quotes** (lines starting `>`). Review for AI-drift, but reduce severity by one step (high→medium, medium→low). Quotes may be from other authors. Do **not** down-rate Dimension D findings — those concern the author's framing.

**Bullet/numbered lists:** Treat the list as one paragraph for segmentation; review each item separately for Dimensions A/C/D. **In addition**, flag the list structure itself under Dimension B (`ai-drift-bullets-in-argument`) when in argumentative context.

For each paragraph, record:
- `paragraph_index` — 1-based, in document order within the slice
- `line_start`, `line_end` — 1-based, in **source file** coordinates (apply `line_offset`)
- `char_start`, `char_end` — 0-based, in **source file** coordinates
- `section` — most recent header text, or `null`
- `kind` — `prose` | `blockquote` | `list`
- `text` — raw paragraph content

---

## Section 5: Sweep — five dimensions

Dimensions **A–D** run per paragraph. Dimension **E** runs once for the whole
document, after the paragraph sweep, and is driven by a counting tool rather than
by reading. Each produces zero or more **issue records**. Collect into a flat
list; aggregate in Section 6.

**Issue record shape:**

```
{
  type: <one of the type values listed per dimension>,
  dimension: "A" | "B" | "C" | "D" | "E",
  paragraph_index: <int>,          // null for document-level Dimension E findings
  section: <string or null>,
  location: { line_start, line_end, char_start, char_end },
  current: <exact substring of source>,
  proposed: <string or null>,
  confidence: <float 0.0–1.0>,
  auto_applicable: <bool>,
  priority: "high" | "medium" | "low",
  rationale: <1–2 sentences>
}
```

`location` covers the **exact span** of the issue (one word for a lexicon swap; the full tricolon span; the full paragraph for structural issues).

### Dimension A — AI-drift lexicon

Compare against the lexicon sections of `content/ai-drift.md`: verbs, adjectives & adverbs, discourse markers, meta-phrases.

For each match:

- `type` (by catalog section) — always emit the specific subtype, never a collapsed `ai-drift-lexicon`:
  - verb → `ai-drift-verb`
  - adjective/adverb → `ai-drift-adjective`
  - discourse marker → `ai-drift-discourse-marker`
  - meta-phrase → `ai-drift-meta-phrase`

- **Severity:**
  - **HIGH** — ≥3 lexicon tells in one paragraph (cluster), OR a single tell in a load-bearing thesis sentence (paragraph topic sentence, or sentence carrying the section's central claim).
  - **MEDIUM** — 1–2 tells in non-thesis sentences with the catalog entry not marked `Confidence: Low`.
  - **LOW** — single tell where the catalog entry is `Confidence: Low` or `Medium` and no clustering.

- `proposed`: most-fitting alternative from the catalog's "Suggested alternatives". If the catalog's primary recommendation is "drop", `proposed = ""` with `auto_applicable: true`.
- `auto_applicable`: **true** for all word-level lexicon swaps.
- `confidence`: from catalog `Confidence` field if present; default **0.85** for verbs/adjectives/meta-phrases, **0.75** for discourse markers.

### Dimension B — AI structural patterns

Compare against the structural-pattern sections of `content/ai-drift.md` (sentence-level, paragraph-level, discourse-level, formatting tells).

**Honor trigger conditions in each catalog entry.** In particular:
- **Tricolon:** flag only when ≥2 in one paragraph, OR a single tricolon in a load-bearing thesis/summary sentence, OR a tricolon of near-synonyms. A single tricolon in passing prose is **not** flagged.
- **"In recent years" opener:** flag when the paragraph **begins** with the phrase or a close variant ("Over recent years,", "In the past few years,"). HIGH when opening a section.
- **Bullets in argument:** flag when the list sits inside argumentative prose, not methods/criteria/cases. Three short-clause bullets is the strongest signal.
- **Closing restatement:** flag only for the **last paragraph in a section** whose content paraphrases the section's opening.
- **One-sentence transition paragraph:** flag a standalone sentence whose only job is to announce the next paragraph.

**Type values** (one per matched catalog entry — emit additional types as you map new catalog entries):

`ai-drift-tricolon`, `ai-drift-symmetric-parallel`, `ai-drift-importance-marker`, `ai-drift-adversative-rhythm`, `ai-drift-hedge-stacking`, `ai-drift-not-just-x-but-y`, `ai-drift-topic-example-restate`, `ai-drift-opener-in-recent-years`, `ai-drift-restatement-closer`, `ai-drift-bullets-in-argument`, `ai-drift-transition-paragraph`, `ai-drift-todays-x-opener`, `ai-drift-topic-with-tricolon`, `ai-drift-hedging-without-substance`, `ai-drift-false-balance`, `ai-drift-concession-reversal-rhythm`, `ai-drift-ultimately-closer`, `ai-drift-importance-pivot`, `ai-drift-recursive-three-part`, `ai-drift-per-paragraph-thesis-restate`, `ai-drift-excessive-headers`, `ai-drift-bold-overuse`, `ai-drift-em-dash-overuse`, `ai-drift-inconsistent-headers`, `ai-drift-decorative-hr`, `ai-drift-emoji-decoration`, `ai-drift-summary-blockquote`.

**Severity:**
- **HIGH** — paragraph-opener tells (`ai-drift-opener-in-recent-years`, `ai-drift-todays-x-opener`), `ai-drift-bullets-in-argument`, `ai-drift-topic-example-restate`, `ai-drift-topic-with-tricolon`, `ai-drift-restatement-closer` at section end
- **MEDIUM** — tricolons in non-thesis sentences, restatement closers not at section end, single instance of hedging-without-substance, most formatting tells
- **LOW** — borderline matches, patterns the catalog marks low-confidence

`proposed`:
- `ai-drift-tricolon`: attempt a pair + em-dash qualifier reconstruction ("A, B, and C" → "A and B — though C also matters when…") if a faithful reduction exists. Otherwise `null`.
- All other structural types: `null`. The rationale should explain what to consider; the fix is the author's.

`auto_applicable`: **true** only for `ai-drift-tricolon` when `proposed` is non-null. **false** otherwise.

`confidence`: from catalog `Confidence` if present; defaults — **0.80** paragraph-level, **0.70** sentence-level, **0.90** for "in recent years" opener.

### Dimension C — Style drift from base + genre overlays

**Active only if `content/styles/base.md` or `content/styles/{genre}.md` was loaded.** Otherwise zero issues; note `Dimension C: skipped (no style overlay)` in the report header.

Consult sections: `## Sentence`, `## Lexicon — preferred`, `## Lexicon — avoid`, `## Hedging`, `## Citation integration`, `## Paragraph architecture`, `## Manual overrides`. Treat each rule as a constraint the paragraph matches or violates.

**Do not consult `## Exemplars` or `## Signature phrasings`.** Those sections are the write-side payload (verbatim voice specimens and slotted frames) consumed only by `marginalia-write`. They are not rules and must not be turned into review findings — a paragraph that fails to resemble an exemplar is not a drift violation. Dimension C's contract is unchanged by their presence.

**Type values** (one per violated rule family):
- `lexicon-drift` — word in `Lexicon — avoid`, or absent characteristic preferred-lexicon item
- `sentence-length-drift` — sentence outside user's typical range
- `hedging-pattern-drift` — hedge frequency/shape mismatched
- `citation-integration-drift` — narrative vs. parenthetical mismatch with user's dominant style
- `paragraph-architecture-drift` — topic-sentence placement, paragraph length, or transition style mismatched
- `em-dash-pattern-drift` — em-dash use diverges from user's baseline

**Severity:**
- **HIGH** — rule lives in `## Manual overrides` (user-authored)
- **MEDIUM** — rule in a non-low-confidence section, or overlay frontmatter `confidence: high`
- **LOW** — overlay marked `confidence: low | N<3`, or rule qualified as soft preference

`proposed`:
- Simple lexicon-drift with clear preferred alternative: the alternative. `auto_applicable: true`.
- Sentence/paragraph/citation rewrites: `proposed: null`, directive rationale, `auto_applicable: false`.

`confidence`: **0.90** Manual overrides; **0.75** `confidence: high`; **0.55** `confidence: low | N<3`.

### Dimension D — Argumentative structure

Judgement-heavy. Be conservative: do not flag unless the issue is clearly present. Confidence capped at **0.70**.

For each paragraph, ask:

1. **Load-bearing claim in main clause, or buried?** If the central commitment sits inside a `while X, Y` / `although X, Y` / `it has been suggested that…` construction, flag `argumentative-claim-buried`.
2. **If the paragraph closes a section, does it restate or advance?** Section-closing paraphrase → `argumentative-restatement-closer`. (Overlaps Dimension B's `ai-drift-restatement-closer`; emit both if both apply.)
3. **If the paragraph opens a section, does the topic sentence commit or hedge?** Topic sentence mostly hedges with no thesis → `argumentative-hedged-opener`.
4. **Quiet contradiction with an earlier paragraph in the same target?** Flag `argumentative-contradiction`. Reference both paragraphs in the rationale. Track key claims as you sweep.
5. **Citation treated as load-bearing but the prose claim is broader than a single cite supports?** Flag `argumentative-cite-mismatch` (advisory — defers to the citation-verification skill).

**Severity:**
- **HIGH** — `argumentative-claim-buried` in a thesis sentence; `argumentative-restatement-closer` for a section-closing paragraph; `argumentative-contradiction`
- **MEDIUM** — `argumentative-hedged-opener`; `argumentative-cite-mismatch`
- **LOW** — minor structural awkwardness not in the above

`proposed`: **always null**. `auto_applicable`: **always false**.

`confidence`: cap at **0.70**; **0.60** for cite-mismatch and contradiction.

---

### Dimension E — Measured surface metrics

**Document-level, not per-paragraph.** Run once for the whole target, after the
paragraph sweep.

Dimensions A–D ask the model to notice things. This one does not: it runs
`tools/prose_metrics.py`, which counts. **The tool locates; you adjudicate.**
Never re-count by hand, and never override a count with an impression.

This is a floor under the paragraph sweep, not a replacement for it. A–D
routinely catch punctuation substitution unaided and can find things no counter
reaches (voice loss by *subtraction*, a claim contradicted by a table). The
problem is consistency: a mature profile will usually carry a `## Manual
overrides` entry that exists only because the same check had already been
under-caught on an earlier pass. Dimension E makes the count deterministic and
supplies rates against a corpus baseline, which cannot be estimated reliably by
reading. Where E and your reading
disagree on a *count*, E is right. Where they disagree on whether a count
*matters*, you are.

**Run:**

```bash
python3 tools/prose_metrics.py <target> --genre <genre> --json
```

It handles `.md`, `.mdx`, `.tex`, and `.txt` directly (see
`content/input-ingestion.md`). If the script is missing or errors, note
`Dimension E: skipped (prose_metrics unavailable)` in the report header and
continue with A–D. Never fabricate metrics.

**Additionally, when `--genre business`, run the companion counter:**

```bash
python3 tools/business_tells.py <target> --json
```

`prose_metrics.py` measures against academic baselines that the business
register deliberately does not share, so on its own it under-reports here.
`business_tells.py` supplies what that register actually needs: the paired
versus unpaired em-dash split (paired is earned, unpaired is not), located
teaching-the-counterparty passages, and the trailing-antithesis construction.
Same contract as `prose_metrics.py` — **it locates, you adjudicate.** Its
`verdict` and `fix` fields are candidates, not findings; read the `text` before
emitting. If it is missing or errors, note `business tells: skipped
(business_tells unavailable)` in the report header and continue. The adjudication
criteria for each category live in `content/styles/business.md`.

**Consume `candidates[]`.** Each entry is a located, counted fact. Your job is to
decide whether it is earned, then emit an issue record or discard it:

| `kind` | What you must judge |
|---|---|
| `em-dash` | Emit unless the document has exactly one and it carries a genuinely essential interruption (`base.md` override). `type: punctuation-em-dash`, `auto_applicable: false`, fix = split the sentence or use parentheses, **never** substitute another mark. **Developer documentation is exempt from the zero target** where the profile's `## Manual overrides` says so: for READMEs, docstrings, changelogs and PR text, first subtract the structural uses (table rows, definition-list entries in bullet **and** numbered form, and titles), then flag only above roughly 10 prose em-dashes per 1,000 words, and never on rate alone below ~500 words. **Do not estimate this subtraction with a regex.** It was attempted four times on one repository and gave four different answers, each wrong in a way that inverted the conclusion; the counts are small, so extract the residual lines and read them. Report how many of the raw total were structural. |
| `colon-cluster` | Is each colon introducing a genuine list or a definitional gloss, or is it splicing an ordinary clause? Emit `punctuation-colon-splice` for the latter. |
| `semicolon-cluster` | Is it delimiting items in a real list (acceptable, common in grant deliverables) or joining two clauses that should be sentences? Emit `punctuation-semicolon-splice` for the latter. |
| `long-sentence` | Only appears when the document exceeds the author's own long-sentence share. Judge the *source* of the length: length from stacked specification, numbers, or qualified claims is voice and is kept; length from clauses bolted on with coordinators and mid-sentence punctuation is drift. Emit `sentence-overlong-construction` only for the latter. |
| `punctuation-above-reference` | A document-wide rate above the author's most disciplined register. Emit one HIGH issue naming the rate and the multiple. This is usually the finding that matters most; individual paragraph hits are its symptoms. The threshold is the **90th-percentile** papers rate with a 1.15× band, not the median: half a corpus sits above its own median by definition, and this one's colon rates span 0.40–9.56 per 1k. It fires on 3 of the author's own 16 papers, all genuine outliers. Still treat it as "look here" rather than a verdict, and say in the report which instances you adjudicated as earned. |
| `contrast-frame-rare` | A contrast-frame surface that is effectively absent from the author's corpus (per `contrast_by_surface` in `baselines.json`), located with its excerpt. Negative-space evidence of the same kind as `## Lexicon — avoid`, so a single occurrence is flaggable. **Read the excerpt before emitting** — these patterns match across clause boundaries and a minority are coincidental. Emit `ai-drift-contrast-frame`. **Check `corpus_backed` first.** When it is `false` there is no baseline, so nothing establishes that this surface is rare *for this author* and the negative-space argument does not hold. Do not flag on a single occurrence; fall back to judging the family rate alone, and say in the report that the per-surface split was unavailable. |
| `contrast-frame-rate` | The family total, above ~1/1k medium and ~1.25/1k high. **Always read `by_surface` before emitting.** When `concentrated_in` is set, ~80%+ of the rate is one surface; if the style profile records that surface as the author's own, this is register rather than drift and usually should not be emitted. The family argument only holds when the rate is spread across surfaces, several of which the author does not use. |
| `baseline-delta` | Distance from measured voice in **either** direction. Both failures are real: flat-and-glossless (the AI-collaboration failure) and inflated (the grant-register failure). Emit `voice-distance` with the metric, observed value, baseline, and direction. |
| `note` | Volume was capped. Not an issue; mention the total in `## Notes for the author`. |

**Severity:**
- **HIGH** — `punctuation-above-reference`; any `baseline-delta` at or beyond ±40%; em-dashes in a document whose target is zero.
- **MEDIUM** — `baseline-delta` between ±30% and ±40%; colon/semicolon splices.
- **LOW** — isolated long sentences whose length is arguable.

`confidence`: **0.95** for anything resting purely on a count (em-dash present,
rate above reference) — the count is not in doubt, only its interpretation.
**0.70** where you judged construction versus content.

**The relocation check (run before recording the em-dash rule as satisfied).** A zero em-dash
count is not by itself evidence that the interruptions were removed. The same clause-joins survive
a de-em-dashing pass by moving somewhere else, and each destination looks locally earned:

1. **Into colons and semicolons.** The tool prints `punct_load_per_1k`, the three marks summed,
   next to the papers reference. It carries no threshold on purpose (one was tried and fired on 8
   of the author's own 16 papers; the corpus load ranges 1.72 to 14.59, so no single cut separates
   drift from register). Read it as a pair with the em-dash rate: a document at zero em-dashes whose
   combined load is well above its own prior revision has relocated, not restructured.
2. **Into contrast frames.** The tool now counts these: read `contrast_per_1k` against the genre
   baseline, and the `contrast-frame-rate` candidate's `by_surface` breakdown. Above roughly one
   per 1,000 words the frame may be carrying interruptions that punctuation used to carry — **but
   only if the rate is spread across surfaces.** A total made almost entirely of one surface the
   author genuinely uses is register, not relocation. Measured case: `manuscript.tex` posts zero
   em-dashes, colons and semicolons below reference, and a contrast rate of 2.57/1k against a
   0.35 baseline, which looks like textbook relocation until the breakdown shows 100% of it is
   `rather than`, a construction a prose review had already judged load-bearing in five of six
   instances. Relocation shows up as *new* surfaces appearing, not as an existing one thickening.

Where a prior measurement of the same document exists, compare against it: an absolute rate cannot
distinguish a heavy register from a relocated one, but a within-document rise after a de-em-dashing
pass can. Where no prior measurement exists, say so in the report rather than treating the em-dash
count alone as a pass. Record the outcome explicitly in `## Measured metrics` either way, because
"em-dashes: 0" published without it reads as a clean bill of health.

**Guard against flattening.** A `baseline-delta` showing sentences *shorter* than
baseline, or glosses *below* baseline, must never be answered by proposing
padding. The fix is to restore the author's own devices: the parenthetical
re-gloss, the clause architecture carrying real specification. Equally, a
document running longer than baseline is never fixed by deleting specifics,
numbers, or glosses. Shorten by removing construction, never by removing content.

**Report placement.** Dimension E findings go in their own `## Measured metrics`
block in the Markdown report, above `## High-priority issues`, showing the
observed-versus-baseline table. Individual issue records still flow into the
normal priority sections and the JSON.

---

## Section 6: Aggregate issues

1. **Deduplicate.** Same `type`, same `current` text, overlapping `location` → keep higher confidence; merge rationales if substantively different.
2. **Cluster collapse.** If ≥5 issues of the same `type` appear in one paragraph, collapse to a single cluster issue:
   - `type` unchanged, `current` = first instance's `current`
   - `location` spans first instance's `char_start` to last instance's `char_end`
   - `rationale`: summary + list of instances ("N=8 in ¶3: 'crucial' (×3), 'robust' (×2), …")
   - `proposed: null`, `auto_applicable: false`
   - `confidence`: median of collapsed instances; `priority`: highest among them
3. **Compute summary counts.** Paragraphs from Section 4; sentences by splitting on `. `, `! `, `? ` followed by capital or end-of-paragraph; citations via regex on `(Author,? \d{4})`, `\w+ \(\d{4}\)`, `\w+ et al\.,? \d{4}`; per-priority counts.
4. **Sort.** Canonical sort tuple: `(priority_rank, line_start, char_start, type)`, where `priority_rank` is `high=0, medium=1, low=2`. The `type` tie-breaker keeps two issues at the same location in deterministic order.
5. **Assign IDs** (Section 8). Cluster collapse runs **before** ID assignment — each cluster takes a single ID.

---

## Section 7: Emit reports

Output directory: `<target_directory>/<target_filename>.marginalia/`. For pasted text: `./stdin-<YYYY-MM-DD-HHMM>.marginalia/` in cwd.

Filenames: `<YYYY-MM-DD-HHMM>-review.md` and `<YYYY-MM-DD-HHMM>-review.json` (UTC, minute precision). Create the directory if missing. If a file with the same timestamp exists, append `-2`, `-3`, etc. Never overwrite.

### 7a. Markdown report

```markdown
# Marginalia review: <target>
Genre: <genre> | Style files loaded: <comma-separated basenames, or "none">
Scanned: <n> paragraphs, <n> sentences, <n> citations
Mode: <"full" | "ai-drift-only" | other>
Generated: <ISO 8601 timestamp>

## Summary
- High: <n>
- Medium: <n>
- Low: <n>

## High-priority issues (n=N)

### R-001 — ¶<paragraph_index>, line <line_start>: <type>

> "<current text>"

**Section:** <section, or "(no preceding header)">
**Why flagged:** <rationale>
**Suggested edit:** <proposed text, or "(structural — see rationale)">
**Confidence:** <confidence>
**Auto-applicable:** <true|false>

[repeat per issue]

## Medium-priority issues (n=N)
[same format]

## Low-priority / stylistic nudges (n=N)
[same format]

## What's working
- <up to 5 positive observations: paragraphs that match the user's style cleanly, sections with strong argumentative integrity, citations integrated naturally, etc.>

## Notes for the author
<Optional: meta-observations about the target. Examples: "¶4–7 are dense with planted AI-drift, suggesting drafted-with-assistance passages; ¶1–3 have a different register suggesting hand-edited.", "The 'seven features' phrasing is consistent across sections — good.", "Two paragraphs make claims a single cite cannot bear; flagged in argumentative-cite-mismatch issues for citation-skill follow-up.">
```

### 7b. JSON report

```json
{
  "report_id": "<YYYY-MM-DD-HHMM>-review",
  "target": "<absolute path or stdin-<timestamp>>",
  "genre": "<grants|papers|other>",
  "style_files_loaded": ["base.md", "grants.md"],
  "mode": "full",
  "generated_at": "<ISO 8601 UTC timestamp>",
  "ignored_flags": [],
  "summary": {
    "paragraphs_scanned": 12,
    "sentences_scanned": 47,
    "citations_in_target": 19,
    "high": 3,
    "medium": 7,
    "low": 12
  },
  "issues": [
    {
      "id": "R-001",
      "priority": "high",
      "type": "ai-drift-opener-in-recent-years",
      "dimension": "B",
      "paragraph_index": 2,
      "section": "Process accounts of intelligence",
      "location": {"line_start": 5, "line_end": 5, "char_start": 0, "char_end": 17},
      "current": "In recent years,",
      "proposed": null,
      "confidence": 0.90,
      "auto_applicable": false,
      "rationale": "Paragraph-opening 'In recent years,' is the single most recognisable LLM opener; commits to no specific time range. Replace with a specific anchor ('since 2018', 'after the publication of X') or cut and open with the claim directly."
    }
  ],
  "whats_working": [
    "¶1 opening: argumentative claim placed in main clause, not buried in subordinate"
  ],
  "notes_for_author": "<string, may be empty>"
}
```

The JSON is the source of truth for `marginalia apply`. Every field shown is required (use `null` for absent optional values, empty arrays for empty lists). Do not add fields not shown; do not omit fields shown.

---

## Section 8: Stable ID generation

`R-NNN`, zero-padded to three digits, starting at `R-001`, assigned in canonical sort order.

**Determinism:** Re-running on an unchanged target produces the same IDs. Sort by `(priority_rank, line_start, char_start, type)` before assigning IDs. `priority_rank`: `high=0, medium=1, low=2`. The `type` tie-breaker is lexicographic.

Stability is per-target-version, not across edits — when line numbers shift, IDs may change.

>999 issues (not expected in Phase 1): use four digits (`R-0001`) uniformly across the report. Do not mix widths.

---

## Section 9: Edge cases and error handling

- **Empty target** (file empty or only headers/code/blank lines). Minimal report: all summary counts zero, no issues, `notes_for_author = "Target was empty or contained only headers, code blocks, and blank lines."`
- **Plain prose, no markdown structure.** Segment by blank lines; `section: null` for all paragraphs.
- **Target >10,000 words.** Single report. Add `Target size: <n> words (large)` to header. No splitting, no truncation.
- **Frontmatter block.** Skip the YAML between `---` markers at file start. Count its lines toward `line_offset` so locations remain accurate.
- **Headers without surrounding blank lines.** Still treated as paragraph separators.
- **Anchor matches multiple headers.** Use the first; warn in report header with all match lines.
- **Catalog edited between runs.** ID stability across catalog changes is not guaranteed.
- **Style file missing expected sections.** Skip that rule family; do not error.
- **Issue clusters:** see Section 6 step 2 (≥5 same-type issues in one paragraph collapse).

---

## Worked example — `tests/fixtures/ai-drift-sample.md`

Three paragraphs: ¶1 prose, ¶2 prose, ¶3 list.

**¶1** (line 3) — "intelligence … is contextual, dynamic, and emergent" + "we delve into".
- A: `delve` → `ai-drift-verb`, MEDIUM, proposed `"examine"`, `auto_applicable: true`, conf 0.85.
- B: tricolon in load-bearing thesis → `ai-drift-tricolon`, MEDIUM, proposed `"contextual and dynamic — and emergent under conditions where …"`, `auto_applicable: true`, conf 0.75.

**¶2** (line 5) — opens "In recent years,", contains `crucial`, `robust` (paired with "account").
- B: opener → `ai-drift-opener-in-recent-years`, **HIGH**, `proposed: null`, `auto_applicable: false`, conf 0.90.
- A: `crucial` → `ai-drift-adjective`, MEDIUM, proposed `"central"` or drop, `auto_applicable: true`, conf 0.85.
- A: `robust` → `ai-drift-adjective`, MEDIUM, proposed `"well-supported"`, `auto_applicable: true`, conf 0.85.

**¶3** (lines 7–11) — three short-clause bullets summarising ¶2 in argumentative context.
- B: `ai-drift-bullets-in-argument`, **HIGH**, `proposed: null`, `auto_applicable: false`, conf 0.85.

All six "must catch" items emit. Severities match the fixture's expected output. `auto_applicable` flags match (true for lexicon swaps + tricolon; false for opener + bullets). JSON shape matches Section 7b.

---

## Operational notes

- Be conservative in Dimension D — false positives there cost the author more than false negatives.
- Be aggressive in Dimensions A and B — false positives there cost a glance; false negatives let AI-drift through to submission.
- `proposed` is a suggestion. The author decides via `marginalia apply`.
- If a finding does not fit the rubric, record it in `notes_for_author` rather than mislabelling.
