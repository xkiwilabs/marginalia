# Refine protocol

> **Paths.** `content/styles/…` and `examples/…` below are names, not locations. Resolve them via `content/paths.md` (`$MARGINALIA_HOME`, then `~/.marginalia/`, then the repo). Resolve once per run and keep the same root throughout.

The procedure `marginalia-refine` follows. Loaded once at the start of every refine run. The SKILL.md is a thin entry point; this file is the actual procedure.

`refine` is the inverse of `calibrate`. Where `calibrate` asks "does the profile reproduce the author's voice?" (fidelity), `refine` asks "where could the author's voice, measured against the author's own corpus, be tightened — overused crutches dialed back, underused strengths reached for more?" (within-voice evolution). It is a critic of the *style profile and the corpus behind it*, not of any draft — `marginalia-review` reviews drafts. The output is a categorized, evidence-backed suggestions report; the author selects which suggestions to adopt, and accepted ones are written as `## Manual overrides` in the relevant style file.

Refine measures distributions over the author's actual corpus (`examples/{genre}/`), not the profile's summary rules — tics and underused strengths are facts about the writing, not facts about the abstract rules. This is why refine needs the corpus and not just the profile.

Follow sections in order. Where a section says "if X, error", produce the error and stop — do not produce a partial report or a fabricated suggestion.

---

## Section 1: Inputs

- **`--genre`** (optional) — which profile and corpus to refine. One of `papers`, `grants`, `other`, or a custom `<slug>`. Default: `papers`. Selects the overlay loaded (`content/styles/{genre}.md`) and the corpus directory read (`examples/{genre}/`). The literal value `base` targets `base.md` directly (see Section 7 for the write-target consequence). `--genre=base` has no dedicated corpus — `examples/base/` does not exist — so base-level refinement runs against the union of all genre corpora (`examples/papers/`, `examples/grants/`, `examples/other/`); this is not an empty-corpus error.
- **`--categories`** (optional) — a comma-separated subset of the analyzer categories, or `all`. The available categories are: `tics`, `underused`, `rhythm`, `lexicon`, `hedging`, `openers`, `paragraphs`. Default: `tics,underused` — the two highest-precision, safest categories, the ones least likely to surface a false positive that would push the voice toward a generic mean.
- **Implicit inputs:**
  - Profile: `content/styles/base.md` (required) plus the genre overlay `content/styles/{genre}.md`. Missing `base.md` → error per Section 8.
  - Corpus location: `examples/{genre}/` relative to the marginalia repo root. The same converted `.md` corpus that `extract-style` and `calibrate` read — refine introduces no new ingestion path. Non-Markdown source files have already been converted to `.md` siblings per `content/input-ingestion.md`; refine reads the `.md`, never the original source.

Record the resolved inputs in working memory; they appear in the report header (Section 6).

---

## Section 2: Loading

1. **Load the profile.** Load `content/styles/base.md` (required) and the genre overlay `content/styles/{genre}.md`. If `base.md` is missing → error per Section 8 and stop. Record the overlay's `confidence` / `N` from its frontmatter for the report header. If the overlay is missing, note it and proceed against `base.md` alone (Section 8 covers the no-overlay case). **Read the existing `## Manual overrides` section** of both files and hold its rules in working memory: a feature already addressed by a manual override must NOT be re-proposed (Section 8 suppression rule). This is the same discipline by which `extract-style` and `calibrate` treat `## Manual overrides` as sacred — refine adds to it, never duplicates within it.

2. **Load the corpus.** List and read the eligible `.md` files in `examples/{genre}/`, applying the same exclusions as `extraction-protocol.md` Section 2 (skip `.gitkeep`, `README.md`, and underscore-prefixed `_*.md`). Record the document count `k` for the report header.

   - **If the corpus directory is empty or absent** (no eligible files after exclusions): enter **DEGRADED mode**. Corpus-grounded measurement is the entire point of refine, so this is explicitly a fallback. Proceed against the profile alone — the analyzers (Section 4) run over the rules and exemplars the profile records rather than over a measured distribution. Mark **every** suggestion `confidence: low (no corpus)` and emit the prominent degraded-mode warning in the report header (Section 6). Do not silently produce confident-looking suggestions from no corpus.

---

## Section 3: Core principle — corpus-grounded only

This is the load-bearing guardrail. **Every suggestion MUST cite the author's own corpus as evidence, and must be exactly one of two kinds:**

- **(a) A tic** — a feature the author *overuses relative to their own distribution*. Not relative to an external ideal of good writing — relative to the rate at which the author themselves deploys the feature elsewhere. A discourse marker that opens a disproportionate share of the author's own paragraphs is a tic; a discourse marker that a style guide dislikes is not.
- **(b) An underused strength** — a strong move the author *already makes, but rarely*, that could be reached for more often. The evidence is the rare real instances in the corpus, which prove the move is the author's own and not an import.

If a proposed change cannot be grounded in the author's own corpus evidence, **it must NOT appear in the report.** No external style rules — no Strunk-and-White, no generic "good writing," no readability heuristics, no preference for short sentences or active voice as such. Refine never measures the author against anyone else.

This guardrail is what keeps refine from becoming the homogenizing force marginalia exists to fight. Marginalia's whole reason for being is to protect a distinctive voice from drift toward a generic mean; a refine that imported external taste would defeat that purpose from the inside. When in doubt whether a candidate suggestion is corpus-grounded, drop it.

---

## Section 4: Category analyzers

For each selected category, measure the author's own distribution across the corpus and surface deviations *within that distribution*. Each analyzer states what to measure and what evidence to attach to any suggestion it produces. Run only the categories named by `--categories` (Section 1).

- **`tics`** — features the author overuses relative to their own baseline. Look for: a discourse marker or transition opening a disproportionate share of paragraphs or sentences (e.g., a single connective fronting a large fraction of paragraph openers); a signature device stacked beyond the author's typical density (e.g., the `(i.e., …)` re-gloss or the em-dash appositive appearing several times in one sentence, or in a meaningful fraction of sentences, well above the corpus norm for that device). **Evidence to attach:** the measured rate (the device's frequency, expressed against the author's own baseline rate for it) plus 2–3 sample passages quoted verbatim, each with its source filename.

- **`underused`** — strong moves the author makes but rarely. Look for: the short-sentence punch landing after a long multi-clause run (the deliberate intuition-pump beat); the "Consider…" / intuition-pump opener; a vivid analogy or worked example — moves the profile's exemplars show are genuinely the author's, but which the corpus deploys only a handful of times. **Evidence to attach:** the rare real instances, quoted verbatim with source filenames, and the suggestion to reach for the move more often.

- **`rhythm`** — sentence-length monotony measured against the author's own occasional range. Look for stretches where sentence length clusters tightly with little variation, in an author whose corpus elsewhere shows a wider range (including the deliberate short beat). **Evidence:** the measured clustering (the tight band) contrasted with quoted passages from the same corpus showing the author's range.

- **`lexicon`** — over-reliance on a narrow set of verbs or connectives where the corpus shows the author commands a wider set. Look for a small handful of verbs/connectives carrying a disproportionate load when `## Lexicon — preferred` and the corpus together demonstrate a broader repertoire. **Evidence:** the frequency of the over-relied-on items, plus quoted instances of the wider set the author already uses elsewhere.

- **`hedging`** — hedge calibration measured against the author's own norm. Look for hedge clustering or hedge-stacking (multiple hedges qualifying a single claim) above the author's typical density. This is calibration, not removal: the author's productive hedges are voice (see `papers.md` `## Hedging`); the target is over-clustering, not hedging as such. **Evidence:** the measured stacking/clustering rate plus 2–3 quoted passages with source filenames.

- **`openers`** — repetition in paragraph openers relative to the author's own variety. Look for the same opening construction (a fronted connective, a fixed sentence frame) recurring across a disproportionate share of paragraph starts when the corpus elsewhere shows the author varies openers. **Evidence:** the rate of the repeated opener plus quoted instances of the variety the author achieves elsewhere.

- **`paragraphs`** — repetition in paragraph *shape* relative to the author's own variety. Look for one dominant paragraph shape (e.g., claim → gloss → qualification) recurring beyond the author's typical mix when the corpus shows the author commands several shapes. **Evidence:** the rate of the repeated shape plus quoted/identified instances of the alternative shapes the author already uses.

In every category, the deviation is measured **against the author's own corpus**, never against an external target. An analyzer that cannot ground a candidate in a measured rate plus real corpus instances produces nothing for that category — silence is the correct output when there is no corpus-grounded tic or underused strength to report.

---

## Section 5: Suggestion record

Each suggestion the analyzers produce is recorded with these fields:

- **`category`** — which analyzer produced it (one of the Section 4 categories).
- **`observation`** — a one-sentence statement of the tic or underused strength, in the author's-own-terms framing (e.g., "You open a disproportionate share of paragraphs with 'Thus,' relative to your own variety elsewhere").
- **`corpus_evidence`** — the measured rate or frequency **and** 2–3 quoted sample passages, each tagged with its source filename. This field is mandatory and is the embodiment of the Section 3 guardrail: a suggestion with no corpus evidence is not a valid suggestion. In DEGRADED mode (Section 2), this field cites the profile's rules/exemplars instead and the suggestion carries `confidence: low (no corpus)`.
- **`proposed_override`** — a concrete rule phrased for the `## Manual overrides` section, written as "more/less of your own X" (e.g., "Vary paragraph openers more — you front 'Thus,' too often relative to your own range; reach for subject-first construct-naming openers, which you already use."). The rule must be actionable as a write-side/review-side instruction, consistent with the override conventions in `extraction-protocol.md` Section 5b.
- **`keep_as_is_note`** — a brief statement of why the author might reasonably *decline* this suggestion (e.g., "If 'Thus,' density is intentional argumentative scaffolding in this genre, leave it"). Refine is a critic the author overrules at will; this note makes the decline a first-class option.
- **`confidence`** — the analyzer's confidence in the suggestion, factoring corpus size and effect strength. In DEGRADED mode this is always `low (no corpus)`.

---

## Section 6: Report

Write the report to `.marginalia/refine-<YYYY-MM-DD-HHMM>.md` (UTC, minute precision). Create the `.marginalia/` directory if missing; if a file with the same timestamp exists, append `-2`, `-3`, etc. — never overwrite. The `.marginalia/` directory is gitignored.

The report begins with this header, verbatim (fill the angle-bracket slots):

```
# Refine — <YYYY-MM-DD-HHMM>

- **Genre:** <genre> · overlay confidence: <conf | N>
- **Categories:** <csv>
- **Corpus:** examples/<genre>/ (<k> docs)  |  or: NO CORPUS — degraded, profile-only
```

In normal mode, fill the `Corpus:` line with `examples/<genre>/ (<k> docs)` and drop the alternative. In DEGRADED mode (Section 2), use the `NO CORPUS — degraded, profile-only` form and ensure the degraded-mode warning is unmissable at the top of the report.

After the header, the report contains the suggestions, **grouped by category** (in the order the categories were selected). Render each suggestion as the full Section 5 record — `category`, `observation`, `corpus_evidence` (rate + quoted samples with source), `proposed_override`, `keep_as_is_note`, `confidence`. A category that produced no suggestions is named with a one-line "no corpus-grounded suggestions" note, so the author sees the category was run.

---

## Section 7: Feedback loop

The author reads the report and selects which suggestions to adopt. For each accepted suggestion:

1. **Show the `proposed_override` as a diff** into the target file's `## Manual overrides` section. The target file is the **genre overlay** (`content/styles/{genre}.md`) by default; it is `content/styles/base.md` only when the run was invoked with `--genre=base`.
2. **Write only on per-edit confirmation.** No edit is written without its own confirmation; the author may take some suggestions and skip others. This follows the diff-and-confirm discipline of `content/apply-protocol.md` §5 exactly — show the diff, confirm individually, never silent-write.
3. **Tag each applied rule** with a `(refine <date>)` provenance marker appended to the rule (day precision, matching the `(calibrate <date>)` convention in `calibration-protocol.md` Section 7), so the origin of every refine-authored override is visible.

**SCOPE GUARD.** refine writes to **only** the `## Manual overrides` section. **Every other `## …` heading and the frontmatter is off-limits, regardless of its exact wording** — the auto-derived sections are the validated output of `extract-style`, and refine never touches them. The guard is positive, not a blocklist: do not match section names against a fixed list, because the real style files carry parenthetical qualifiers the list will not anticipate (e.g. `## Lexicon — avoid (AI defaults absent from the papers corpus)`, `## Lexicon — avoid / WATCH (…)`, and `grants.md`'s `## Notes on confidence`). Illustrative examples of the off-limits auto-derived sections — not an exhaustive list — are `## Sentence`, `## Lexicon — *`, `## Hedging`, `## Signature phrasings`, `## Citation integration`, `## Paragraph architecture`, `## Argumentative moves`, `## Exemplars`. If a heading is not the literal `## Manual overrides`, it is off-limits. refine proposes standing instructions that sit alongside the auto-derived sections in `## Manual overrides`, and the review/write skills already treat overrides as the highest-priority overlay. This scope guard is the write-side complement to the Section 3 corpus-grounded guardrail: together they bound refine to additive, evidence-backed, author-confirmed changes.

---

## Section 8: Errors and edge cases

- **No `base.md`.** Error and stop: "No style profile. Run `/marginalia extract-style` first."
- **Empty or absent corpus** (`examples/{genre}/` has no eligible files). Do not error: enter DEGRADED mode per Section 2 — run the analyzers against the profile alone, mark every suggestion `confidence: low (no corpus)`, and emit the prominent degraded-mode warning in the report header (Section 6). Corpus-grounded measurement is the point of refine, so the warning must make plain that these suggestions are inferred from the profile, not measured.
- **A suggestion duplicates an existing `## Manual overrides` rule.** Suppress it. Section 2 loaded the existing overrides for exactly this check; refine never re-proposes a feature the author has already addressed with a standing rule.
- **Genre with no overlay** (only `base.md` exists for the requested genre). Refine base-level features against the corpus and note the missing overlay in the report header. Accepted overrides in this case target `base.md`'s `## Manual overrides` only if the run was `--genre=base`; otherwise note that there is no overlay to write to and recommend running `extract-style` for the genre first. The report is still produced either way — the corpus-grounded suggestions are the durable artifact; only the write step (Section 7) is unavailable until the overlay exists.
- **Target file has no `## Manual overrides` section** (e.g. it was hand-edited away). Do not error and do not write silently. Create the section as part of the confirmed diff: prepend, to the same diff that adds the accepted rule, the default template from `extraction-protocol.md` Section 7 —

  ```markdown
  ## Manual overrides
  <!-- User-authored rules. Preserved across re-extractions. Add rules here that you want the review skill to enforce. -->
  ```

  — appended at the bottom of the file, then add the accepted rule under it. Because the section creation is shown in the diff and applied only on the same per-edit confirmation (Section 7), the no-silent-write discipline is preserved.
- **The author declines all suggestions.** Write the report (it is the durable artifact), change nothing in the style files. This is a valid outcome — refine recommends; the author decides.
- **Non-Markdown corpus files.** Already converted to `.md` siblings by `content/input-ingestion.md`; refine reads the `.md`, the same as `extract-style` and `calibrate`. Never operate on the original source.

---

## Operational notes

- All operational logic lives in this protocol; the SKILL.md is a thin loader ("load `content/refine-protocol.md`, then follow it"). The same applies to the Phase 2 MCP `marginalia.refine` tool and the Phase 3 CLI — they call this protocol unchanged.
- **No silent writes.** Every style-file edit is proposed, diffed, and applied only on explicit per-edit confirmation (Section 7, and the diff-and-confirm discipline of `content/apply-protocol.md` §5).
- **Only `## Manual overrides` is ever written.** Every other `## …` heading and the frontmatter is off-limits regardless of its exact wording — the guard is positive (write to the one named section only), not a blocklist of idealized names that real headings with parenthetical qualifiers would slip past (Section 7 scope guard). Refine is additive: it never rewrites what `extract-style` produced.
- **Reports are annotated artifacts.** refine is a critic of the profile; it recommends, the author decides which suggestions to adopt.
- **Corpus-grounded only.** Every suggestion cites the author's own corpus (Section 3). A suggestion that cannot be grounded in the author's own writing does not belong in the report — refine measures the author against the author, never against an external standard.
- `.marginalia/` report directories are gitignored intermediate artifacts.
