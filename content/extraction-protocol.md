# Extraction protocol

> **Paths.** `content/styles/…` and `examples/…` below are names, not locations. Resolve them via `content/paths.md` (`$MARGINALIA_HOME`, then `~/.marginalia/`, then the repo). Resolve once per run and keep the same root throughout.

The procedure `marginalia-extract-style` follows. Loaded once at the start of every extraction. The SKILL.md is a thin entry point; this file is the actual procedure.

The output of this protocol is one or more files under `content/styles/`, each containing the user's voice rendered as declarative rules. Those rules are consumed verbatim by `marginalia-review` as Dimension C (style overlay) and as the negative-space reference for Dimensions A and B. The rules in style files are instructions to the review skill, not statistical descriptions of the corpus — see Section 5b.

Follow sections in order. Where a section says "if X, error", produce the error and stop.

---

## Section 1: Inputs

- **`genre`** (optional) — one of `papers`, `grants`, `other`, `all`. Default: `all`.
  - When `genre=all`, iterate over `papers`, `grants`, `other` in that order, then synthesize a cross-genre `base.md`.
  - When `genre` is a single value, extract only that genre's overlay file; do not refresh `base.md` unless `--genre=base` is passed explicitly.
- **`mode`** (optional) — one of:
  - `init` — write fresh style files; fail if the target file already exists. Default for first run.
  - `refresh` — re-derive from scratch, overwriting after diff + confirmation. Preserves the existing file's `## Manual overrides` section verbatim.
  - `update` — re-extract from the (possibly enlarged) corpus and merge with the existing style file: keep rules that still hold, drop rules that no longer hold, add new rules. Always preserves `## Manual overrides`.
  - Default: `init` when no style file exists; otherwise the skill prompts the user to pick `refresh` or `update`.
- **Implicit inputs:**
  - Corpus location: `examples/{genre}/` relative to the marginalia repo root.
  - Supported file types: `.md`, `.markdown`, `.txt`, `.pdf`, `.docx`, `.doc`, `.rtf`, `.odt`. Non-Markdown formats are auto-converted to a sibling `.md` per `content/input-ingestion.md` §3 (directory-listing flow). Conversion is cached: re-running on an unchanged corpus reuses the prior conversion.
  - Negative-space reference: `content/ai-drift.md`. Required. Missing → error and stop.

Record the resolved inputs in the skill's working memory; they appear in the final skill report (Section 8).

---

## Section 2: List examples

For each target genre (one pass per genre when `genre=all`):

1. **List files** in `examples/{genre}/` matching `*.md` or `*.txt`.
2. **Exclude:**
   - `.gitkeep`
   - `README.md` (case-insensitive)
   - Any file matching `_*.md` or `_*.txt` (underscore prefix is the user's signal to exclude a file from extraction without deleting it)
3. **Handle empty directories.** If the genre directory does not exist, or contains no eligible files after exclusions, **skip the genre with a note** in the skill report; do not error. The base.md synthesis can still proceed from the genres that did have content.
4. **Count and set confidence** based on the number of eligible files (`N`):
   - `N = 0` → skip this genre.
   - `N = 1` or `N = 2` → `confidence: low | N=<k>`. Be conservative when phrasing rules (Section 9).
   - `N = 3` to `N = 5` → `confidence: medium | N=<k>`.
   - `N ≥ 6` → `confidence: high | N=<k>`.
5. **Size cap per file.** If a file exceeds 50,000 words, read only the first 30,000 words and record a note in the skill report that extraction was truncated for that file.
6. **Frontmatter / empty files.** If a file is empty, or contains only YAML frontmatter and whitespace, skip it with a note. Do not count it toward `N`.

Cross-genre synthesis (for `base.md`) uses the union of all per-genre file lists.

---

## Section 3: Per-document feature extraction

For each example file, extract features across seven groups. Each group specifies *what* to measure and *how* the raw observation maps onto a declarative rule in the output style file. Per-document extraction is local; cross-document synthesis happens in Section 4.

For each file, build an intermediate **feature record** (held in working memory; not written to disk) with one entry per group below.

### Group A: Lexicon

Per document, identify:

- **Characteristic verbs.** Verbs that appear ≥3 times in this document **and** are not present in the verb section of `content/ai-drift.md`. These are verbs the user reaches for.
- **Characteristic adjectives and adverbs.** Adjectives or adverbs that appear ≥3 times and are not in the AI-drift adjective/adverb section.
- **Preferred transitions and discourse markers.** Sentence-initial or paragraph-initial markers that appear ≥2 times (e.g., "Notably,", "What is striking is", "On the present view,", "Taken seriously,"). Include markers that double as argumentative pivots.
- **Marker phrases.** A 2-to-5-word phrase appearing ≥2 times and not present in `ai-drift.md`. These are high-value signals — the user's idiomatic glue.
- **Negative space.** Which AI-drift from `ai-drift.md` are **absent or rare** in this document. Walk every entry in `ai-drift.md`'s verb, adjective/adverb, discourse-marker, and meta-phrase sections; record any entry that appears 0 or 1 times.

Output to working memory: lists of `(word_or_phrase, frequency, sample_contexts)` plus a list of AI-drift absent from this document.

### Group B: Sentence structure

Per document:

- **Length distribution.** Bucket sentences by word count: short (<12), medium (12–25), long (25–40), very long (>40). Report bucket proportions, not exact statistics. Identify the **dominant bucket** (the one with the most sentences) and the **median bucket**.
- **Em-dash frequency.** Average em-dashes per paragraph. Note whether em-dashes appear in most paragraphs (a baseline device) or only in a few (occasional).
- **Parenthetical-clause frequency.** Average parenthetical clauses (between `(` `)` excluding citations) per paragraph.
- **Semicolon use.** Bucket: `rare` (<0.2 per paragraph), `occasional` (0.2–1.0), `frequent` (>1.0).
- **Sentence-initial constructions.** Does the author start sentences with adverbs ("Notably,"), participial phrases ("Taken seriously,"), subordinate clauses ("If we treat X as Y, then…"), or pure subject-first declarations? Record the dominant opening style and any recurring variants.

### Group C: Hedging patterns

Per document:

- **Identify hedge constructions** in use: "appears to", "may be understood as", "is best treated as", "tends to", "is plausibly", "to the extent that", "on the present view", "in a broadly X sense", etc. Record each construction with its frequency.
- **Position.** Where in the sentence does the hedge sit — preceding the verb, preceding the claim, embedded in a subordinate clause, or at the end of the sentence as a qualifier?
- **Frequency.** Average hedges per paragraph.
- **Productive vs filler hedging.** Distinguish:
  - **Productive hedges** that qualify a real epistemic position ("is best understood as", "to the extent the term picks out something worth keeping").
  - **Filler hedges** that add no calibration ("It is important to note that", "One might argue that"). Filler hedges should appear in the avoid list; productive hedges in the preferred list.

### Group D: Citation integration

Per document:

- **Parenthetical-vs-narrative ratio.** Count parenthetical `(Author, Year)` citations and narrative `Author (Year)` citations; report as a ratio expressed in 10-percent buckets (e.g., "~90% parenthetical / ~10% narrative" rather than "0.91:0.09"). If one form is absent, say so explicitly ("narrative citations do not appear").
- **Citation density.** Average citations per paragraph; also approximate citations per 100 words.
- **Position.** Are cites end-of-sentence dominant, mid-sentence, or grouped (e.g., `(Smith, 2003; Jones, 2007)`)?
- **Maximum cites in a single parenthetical.** Record the highest count observed.
- **Grammatical integration.** Are cites integrated into sentence grammar (narrative form: "as Smith (2003) argues, X is…") or appended (parenthetical form: "…X is the case (Smith, 2003).")? Most academic prose mixes these; record the dominant mode.

### Group E: Paragraph architecture

Per document:

- **Average paragraph length** in sentences. Bucket: short (1–2), medium (3–5), long (6+).
- **Topic-sentence placement.** Where does the paragraph's central claim sit — first sentence, second sentence (after a setup), late in the paragraph, or implicit (claim distributed across the paragraph)?
- **Paragraph shapes.** Identify recurring shapes: e.g., `claim → support → qualification`, `setup → counterpoint → resolution`, `observation → development → consequence`. Record the dominant shape(s).
- **Transitions between paragraphs.** Are transitions explicit (signposting phrases like "Turning now to…"), implicit (content carries the link), or pivot-phrase-based (the new paragraph opens by reframing the previous one)?

### Group F: Argumentative moves

Per document:

- **Claim setup.** How does the author introduce a claim? Common patterns: `If we treat X as Y, then…`, `On the present view, X…`, `The question becomes not X, but Y`, pure assertion (`X is Y because…`), or hypothetical-framing (`Suppose X. Then…`).
- **Claim anchoring.** What backs the claim — citation density at the moment of claim, appeal to a specific example, appeal to logical entailment from a prior premise, or appeal to consequence?
- **Section closing.** How does the author close a section — forward-pointing pivot ("…what the chapters that follow undertake"), deliberate ambiguity (leaving a tension open), restatement (rare in academic voice but possible), or extension (drawing a fresh consequence)?
- **Argumentative moves NOT used.** What does the author conspicuously avoid? E.g., "in conclusion" closers, bullet-summary closers, "ultimately" pivots, false-balance framings, concession-then-reversal as a default rhythm. Cross-reference `ai-drift.md`'s discourse-level section.

### Group G: Negative space (cross-cutting)

After Groups A–F are complete, walk through `content/ai-drift.md` end-to-end and, for each entry, record whether the pattern is **absent** from this document (0 occurrences), **rare** (1 occurrence), or **present** (≥2 occurrences). The absent + rare list becomes the document's contribution to the `## Lexicon — avoid` and discourse-level avoid rules in the output style file.

The negative-space list is the largest single signal in low-N corpora. With N=1 or N=2 you cannot confidently claim what the user *does*; you can confidently claim what the user *does not* do, because the absence is observed in every document you have.

### Group H: Exemplars and signature phrasings (the write-side payload)

Groups A–G describe the voice *abstractly* — they are the fuel for the **review** skill, which detects drift. Group H captures the voice *concretely* — verbatim specimens and reusable sentence frames — which is the fuel for the **write** skill, which reproduces voice. An LLM imitates far better from real examples than from descriptions, so this group is what makes drafted prose sound like the author rather than like generic academic register. Do not skip it, and do not paraphrase its contents into rules — the value is in the literal text.

Per document, collect two things and **retain them for output** (unlike the sample_contexts in Group A, which were discard-after-synthesis):

- **Exemplar passages.** Verbatim sentences or short passages (≤60 words each) lifted unchanged from the document, selected to showcase the author's signature moves. Aim to gather a generous pool per document (10–20 candidates); synthesis (Section 4) trims to the final set. Selection criteria, in order:
  1. **Must carry a signature move** — at least one of: a parenthetical re-gloss (`directly specify (are information about) X`), a characteristic sentence frame (the Group-A marker phrases and the Group-H templates below), the gap→aim pivot, a productive hedge construction, a definitional em-dash appositive, or a genre-specific move (grant deliverable/impact framing, paper claim-anchoring).
  2. **Span variety** — do not collect ten instances of the same move. Prefer a set that, taken together, covers sentence-opening habits, mid-sentence elaboration habits, hedging, and closing/pivoting habits.
  3. **Body prose, not scaffolding** — prefer mid-document argumentative prose. Avoid titles, author lists, headers, captions, table cells, equation lines, and reference-list fragments.
  4. **Clean text only** — reject anything bearing conversion artifacts: broken hyphenation across line breaks (`for-\nmalize`), figure/table debris, gibberish from equation rendering, footnote-number runs (`results3,16`), or mojibake. A mangled exemplar actively *degrades* the write skill — when in doubt, drop it.
  5. **Self-contained** — the passage should be intelligible without its surrounding paragraph. Trim leading/trailing fragments to a clean clause boundary, but never alter interior wording.

- **Signature phrasings (templates).** Recurring multi-word *syntactic frames* with slots — the structural habits that a bare word-list cannot capture. A frame qualifies if its shape recurs (≥2× in this document, or appears in this document and matches a frame already seen in another document of the genre), even when the filler words differ each time. Record each as a `frame` (with `[bracketed slots]`) plus one real instantiation from the corpus. Examples of the *kind* of thing to capture (the actual frames come from the corpus, not this list):
  - `Building on [prior foundation], we propose [X] that uses [Y] to [verb] how [Z].`
  - `The [adjective] implication of these findings is that [claim].`
  - `[Construct] is best understood as [gloss], (i.e., [restatement]).`
  - `[Prior work] remains [unclear/unresolved]; accordingly, the aim of [the current study] was to [verb].`

  Capture frames at the threshold of frequency *and* distinctiveness: a frame that recurs but is generic ("It is the case that…") is not signature; a frame that is distinctive but appears once is a candidate the synthesis step may keep if it is strongly characteristic. Unlike Group A's avoid-list (which needs frequency), the write-side payload values the distinctive even at low frequency.

Output to working memory: a candidate exemplar pool with provenance (source file), and a list of `(frame, instantiation)` pairs.

---

## Section 4: Cross-document synthesis

After per-document extraction is complete for a genre, aggregate the feature records into one **genre profile**.

### Per-genre synthesis (producing `content/styles/{genre}.md`)

- **High-confidence rules** — features that appear in **all** documents in the genre. Phrase as invariants ("Citations are parenthetical `(Author, Year)`; narrative form is rare or absent.").
- **Genre rules** — features that appear in **≥50%** of the genre's documents (or in all of them when N ≤ 2). Phrase as preferences ("Paragraphs typically open with a substantive claim, not a scene-setting opener.").
- **Genre-specific rules** — features present in this genre and absent (or markedly weaker) in others. These become **overlay** rules that the review skill applies only when the target's genre matches.

If the genre's documents **conflict** on a feature (e.g., one paper is parenthetical-heavy, another is narrative-heavy), do not pick a side. Phrase the rule as a range: "Citation integration varies — both parenthetical and narrative forms appear; no strong preference observed." Conflicts at low N (1–2) are common and acceptable.

### Cross-genre synthesis (producing `content/styles/base.md`)

`base.md` captures the author's invariants regardless of genre.

- A feature enters `base.md` if it appears consistently **across all examined genres** that had ≥1 document. "Consistently" means: the feature appears in every genre's high-confidence or genre-rule set.
- Genre-specific features stay in the overlay files and do not bubble up to `base.md`.
- The review skill loads both `base.md` and the relevant genre overlay; rules in `base.md` apply to every review.

When `genre=all` and one or more genres were skipped for emptiness, `base.md` is still produced from the genres that did have content, with a note recording which genres were excluded.

### Exemplar and signature-phrasing synthesis (Group H)

Exemplars and signature phrasings are placed where they do the most generative work — in the **genre overlays**, not flattened into `base.md`.

- **Genre overlays (`papers.md`, `grants.md`, `other.md`)** carry the full payload:
  - `## Exemplars` — the final curated set, **8–15 passages** per genre, selected from the candidate pool across all of that genre's documents. Curation: dedupe near-identical passages; keep the cleanest instance of each signature move; ensure the final set spans the variety axis from Group H criterion 2 (openings, mid-sentence elaboration, hedging, closings/pivots) rather than over-representing one move; drop any passage whose cleanliness is doubtful. Preserve each verbatim with a short provenance tag (source filename). Prefer breadth of move-types over volume — 8 well-chosen passages beat 15 repetitive ones.
  - `## Signature phrasings` — **5–10 frames** per genre, each the union of frames that recurred within or across that genre's documents, with one real instantiation each.
- **`base.md`** carries only `## Signature phrasings` — the subset of frames that recur **across genres** (the author's cross-genre structural habits). It does **not** carry an `## Exemplars` section: exemplars are register-bound, and duplicating them into base.md would reintroduce the cross-genre averaging that washes out distinctive voice. The write skill always loads a genre overlay alongside base.md, so the genre exemplars are always available at draft time.

Confidence handling: at low N, exemplars are still reliable (a verbatim sentence is real regardless of N) — so do not suppress the `## Exemplars` section at low N. Signature-phrasing *frames*, by contrast, assert a recurring habit; at N=1 phrase them as "observed once; treat as candidate" and prefer frames that also show within-document repetition.

### Update-mode synthesis

When `mode=update`, before writing:

1. Read the existing style file.
2. Extract its current `## Manual overrides` section verbatim and set it aside.
3. Re-extract from the full corpus (the existing examples plus any new ones).
4. Compare the existing extracted rules (everything except `## Manual overrides`) against the newly extracted rules:
   - **Rules that still hold** (the feature still appears at the required threshold) → keep.
   - **Rules that no longer hold** (the feature is now below threshold, or now conflicts) → flag in the diff for the user to review; remove unless the user objects.
   - **New rules** (a feature now appears that did not before) → add.
5. Re-attach the preserved `## Manual overrides` section at the bottom of the new file (Section 7).

---

## Section 5: Write style files

### Output frontmatter

Every style file begins with YAML frontmatter:

```yaml
---
genre: papers
extracted_at: 2026-05-15T11:42:00Z
example_count: 4
confidence: high | N=4
---
```

Field semantics:
- `genre`: one of `papers`, `grants`, `other`, `base`.
- `extracted_at`: UTC timestamp at the moment the file was written, ISO 8601.
- `example_count`: integer `N` after exclusions and size-cap truncation.
- `confidence`: the literal string `low | N=<k>`, `medium | N=<k>`, or `high | N=<k>` per the Section 2 thresholds.

### Required sections, in order

```markdown
# <Genre> style (extracted from <N> <genre-noun>)

## Sentence
- <rules about sentence length, em-dash use, parentheticals, semicolons, opening constructions>

## Lexicon — preferred
- <words, phrases, transitions, marker phrases the user reaches for>

## Signature phrasings
- <recurring syntactic frames with `[bracketed slots]`, each with one real instantiation — see Group H. In base.md, cross-genre frames only.>

## Lexicon — avoid (AI defaults absent from your corpus)
- <list of AI-drift from content/ai-drift.md that did not appear, or were rare, in the corpus>

## Hedging
- <how the user hedges: which constructions, position in sentence, productive vs filler distinction>

## Citation integration
- <parenthetical vs narrative ratio, density, position, grammatical integration mode>

## Paragraph architecture
- <length, topic-sentence placement, dominant shapes, transition types>

## Argumentative moves
- <how the user sets up, anchors, and closes claims; conspicuous absences>

## Exemplars
<!-- Genre overlays only (omitted from base.md). 8–15 verbatim passages from the corpus, each ≤60 words, each showcasing a signature move and tagged with its source file. These are voice targets for the write skill — verbatim, never paraphrased; the write skill imitates their rhythm and frames, it does not reuse their content. The review skill does not consult this section. -->
- "<verbatim passage>" — *<source filename>*

## Manual overrides
<!-- User-authored rules. Preserved across re-extractions. Add rules here that you want the review skill to enforce, in addition to (or overriding) the extracted rules above. -->
```

The `## Manual overrides` section is always present, even when empty (it carries the comment instructing the user how to use it). The review skill treats rules in `## Manual overrides` as the highest-priority overlay (Dimension C, HIGH severity).

### Section 5b: Style file rules — operational, not statistical

This is the critical translation step. The review skill consumes style files as **instructions**, not as numeric thresholds. Each rule in the output file must be:

- **Declarative** — a sentence stating what the user does, not a statistic about the corpus.
- **Actionable** — phrased so the review skill can apply it to a paragraph and decide whether the paragraph matches or violates the rule.
- **Concrete** — naming specific words, constructions, or shapes, not generic categories.

Below, for each feature group, are 2–3 examples of how raw observations translate to rule strings.

#### Group A → Lexicon — preferred / avoid

| Raw observation                                           | Rule in the output file                                                                                       |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `"What is striking here is that"` appears 4× across N=2   | "Reaches for **'What is striking here is that…'** as a discourse pivot; preserve this phrasing when present." |
| `"Notably,"` appears 2× as sentence-initial               | "Opens emphasis-sentences with **'Notably,'** rather than 'Importantly,' or 'Crucially,'."                    |
| `"delve"` appears 0× across the corpus                    | "Does not use 'delve'. The review skill should flag any occurrence as drift."                                 |
| `"crucial"` appears 0×; `"robust"` appears 0×             | "AI defaults absent from this corpus: 'crucial', 'robust'. Flag occurrences."                                 |

Avoid statistical phrasings like "verb frequency: delve=0, examine=4, treat=3". Translate to declarative rules.

#### Group B → Sentence

| Raw observation                                                                                              | Rule in the output file                                                                                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Median sentence falls in the long bucket (25–40 words); 3 sentences in the very-long bucket; 1 in the short bucket | "Median sentence length is approximately 28 words; sentences rarely exceed 40. Short declarative sentences (<12 words) are rare and used for emphasis, not as a default."                                                     |
| Em-dashes appear in most paragraphs, used for parenthetical elaboration                                       | "Em-dashes are a baseline device, used for parenthetical elaboration mid-sentence (not for slide-style emphasis on a single word). Multiple em-dashes per paragraph are normal."                                              |
| All paragraphs use sentence-initial adverbs or subordinate-clause openers                                     | "Sentences frequently open with sentence-initial adverbs ('Notably,', 'Taken seriously,') or with a subordinate clause ('If we treat X as Y, then…'). Subject-first openers are not the default."                             |

Avoid raw statistics like "mean = 27.4, std = 8.2, max = 47". Translate to the declarative form above.

#### Group C → Hedging

| Raw observation                                                                                                    | Rule in the output file                                                                                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Hedges sit inside subordinate clauses ("to the extent the term picks out something worth keeping"), not fronted    | "Hedges are embedded in subordinate clauses, not fronted as meta-comments. **Avoid** 'It is important to note that…' and 'One might argue that…' as preambles to claims the author endorses."                            |
| `"is best understood as"` appears 2×; `"appears to"` appears 3×                                                    | "Reaches for **'is best understood as'** and **'appears to'** as productive hedges. These qualify the epistemic position rather than soften the assertion."                                                              |

Distinguish productive from filler hedging in the rule wording. "Filler hedges absent" goes to the avoid list, not the preferred list.

#### Group D → Citation integration

| Raw observation                                                          | Rule in the output file                                                                                                                                                                |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| All cites parenthetical; 0 narrative                                     | "Citations are uniformly parenthetical `(Author, Year)`; narrative `Author (Year)` form does not appear. Treat narrative citations as drift unless the surrounding sentence integrates the author's name into the prose deliberately." |
| Density ≈1 cite per 100 words; end-of-sentence dominant                  | "Citation density is approximately one per 100 words. Cites sit at end-of-sentence, appended rather than grammatically integrated."                                                    |
| Grouped citations up to 3 per parenthetical observed                     | "Groups of up to three cites per parenthetical (e.g., `(Smith, 2003; Jones, 2007; Brown, 2012)`) are used to bundle convergent support."                                               |

#### Group E → Paragraph architecture

| Raw observation                                                            | Rule in the output file                                                                                                                                              |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Paragraphs run 3–5 sentences; topic sentence is first                      | "Paragraphs are 3–5 sentences. The topic sentence is first; the remainder of the paragraph develops, qualifies, or extends the opening claim."                       |
| No bullet lists appear inside argumentative passages                       | "Bullet lists do not appear inside argumentative prose. Flag any list inside an argument as structural drift."                                                       |
| Paragraphs close by qualifying or extending, not by restating              | "Paragraphs close by qualifying or extending the opening claim — not by restating it. Section-closing restatements ('Ultimately,', 'In summary,') do not appear."    |

#### Group F → Argumentative moves

| Raw observation                                                                                                   | Rule in the output file                                                                                                                                                                                                         |
| ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claims are introduced via "If we treat X as Y, then…" and "On the present view, X…"                               | "Sets up claims with hypothetical framings ('If we treat X as Y, then…') or perspective-explicit framings ('On the present view, X…'). Pure unframed assertion is rare."                                                        |
| Sections close with forward-pointing pivots ("…what the chapters that follow undertake")                          | "Sections close by pivoting forward — naming what the next move or chapter will undertake — rather than by restating what the section argued. Avoid 'In summary,' / 'Taken together,' closers."                                 |
| No "ultimately" closers; no false-balance framings; no concession-then-reversal as default                        | "Conspicuously avoids: 'Ultimately,' as a closer; false-balance 'On one hand X, on the other hand Y' framings; concession-then-reversal as a default rhythm."                                                                   |

#### Group G → Avoid list

The avoid list is generated by walking `content/ai-drift.md` and listing entries that were absent or rare across the corpus. Phrase the rule as:

> "AI defaults absent from your corpus: 'delve', 'leverage', 'crucial', 'robust', 'foster', 'harness', 'navigate', 'in recent years', 'it is important to note that'. The review skill should flag any occurrence as drift."

For low-N corpora, prefix the rule with "in the examples examined" to acknowledge that the absence is observed, not proven:

> "In the N=2 examples examined, the following AI defaults do not appear: …"

#### Group H → Exemplars / Signature phrasings

This is the one group that **inverts** Section 5b's usual rule. Everywhere else, raw observations are translated into abstract declarative rules. Here, the raw material *is* the output — do **not** translate it.

| Raw observation                                                                                  | Output                                                                                                                              |
| ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| A clean body sentence carrying a parenthetical re-gloss                                           | Quote it verbatim under `## Exemplars`, tagged with its source file. Do not summarize what makes it characteristic — let it stand. |
| The frame `Building on [X], we propose [Y] that uses [Z] to [verb] how…` recurs across documents | A `## Signature phrasings` bullet: the frame with `[slots]`, plus one real instantiation in quotes.                                |
| A striking one-off turn of phrase in an N=1 corpus                                                | Eligible as an exemplar (verbatim sentences are reliable at any N); as a *frame* only if flagged "observed once; treat as candidate". |

Hard rules for this section:
- **Verbatim, never paraphrased.** An exemplar is a copy of the author's text. If you find yourself improving or shortening interior wording, stop — trim only at clause boundaries.
- **Clean only.** Re-apply Group H criterion 4. A passage with conversion artifacts is worse than no passage.
- **Frames are structure, not content.** A signature phrasing captures the *shape* (`The [adj] implication of these findings is that [claim]`), so the write skill can fill it with new content — it is explicitly not a sentence to be reused wholesale.

---

## Section 6: Diff and confirm

Before writing any style file in `refresh` or `update` mode, the skill must show the user a diff against the existing file and request explicit confirmation.

1. **Read the existing file**, if any.
2. **Compute a section-by-section diff**:
   - For each `## ...` heading, list rules added, removed, or modified.
   - Treat `## Manual overrides` as out-of-scope for the diff — it is preserved verbatim and is not subject to extraction.
3. **Present the diff to the user as a markdown summary**, grouped by section. For each change, show old → new (or `+ added` / `- removed`).
4. **Request explicit confirmation.** Do not write the file until the user replies affirmatively. If the user rejects, do not write; the existing file remains untouched.
5. **In `init` mode**, no diff is shown (there is no existing file). If a style file already exists at the target path in `init` mode, **error** with:
   > "Style file `content/styles/<genre>.md` already exists. Use `--mode=refresh` (re-derive from scratch, with diff confirmation) or `--mode=update` (merge new examples)."

For `genre=all`, the diff is computed and confirmed **per file**, not in a single combined diff. The user may accept some files and reject others.

---

## Section 7: Manual overrides preservation

The `## Manual overrides` section in any existing style file is sacred. It contains rules the user has hand-authored; the extraction skill must **never** rewrite, summarize, paraphrase, reorder, or remove entries from it.

In `refresh` mode:
1. Read the existing file.
2. Locate the `## Manual overrides` section. Capture it verbatim, including its HTML comment, any blank lines, and any user-added rules.
3. Generate the new file body from extraction.
4. Append the captured `## Manual overrides` section verbatim at the bottom, preserving exact whitespace and any user comments.

In `update` mode: same. The section is preserved verbatim regardless of what else changes.

If the existing file is missing the `## Manual overrides` section (e.g., it was hand-edited away), the new file uses the default template:

```markdown
## Manual overrides
<!-- User-authored rules. Preserved across re-extractions. Add rules here that you want the review skill to enforce. -->
```

---

## Section 8: Output paths and skill report

### Output paths

- `content/styles/base.md` — written when `genre=all` (synthesizing across all genres) or when explicitly invoked with `--genre=base`.
- `content/styles/papers.md`, `content/styles/grants.md`, `content/styles/other.md` — written per genre.

All paths are relative to the marginalia repo root. Create the parent directory (`content/styles/`) if missing.

### Skill report

After all writes complete (or are rejected), emit a single user-facing report:

```markdown
# Style extraction — <timestamp>

## Files written
- `content/styles/base.md` — confidence: high | N=12 (across 3 genres)
- `content/styles/papers.md` — confidence: medium | N=4
- `content/styles/grants.md` — confidence: low | N=2

## Files skipped
- `other`: no eligible files in `examples/other/` (0 markdown/text files after exclusions)

## Notes
- `examples/papers/long-monograph.md` was truncated to 30,000 words for extraction (file is 52,400 words total).
- `examples/grants/2021-grant.md` was excluded (filename matches `_*.md` underscore prefix? No — actually skipped because it is empty.)

## Reminder
Style files are editable. Open them and add manual overrides under the `## Manual overrides` section if you want specific rules enforced beyond what was extracted. Manual overrides are preserved across re-extractions.
```

The report includes:
- Each file written (with confidence level).
- Each genre skipped (with the reason).
- Any per-file notes (truncation, exclusions, conflicts).
- The reminder about `## Manual overrides`.

---

## Section 9: Edge cases

- **A genre has only one example (N=1).** Extract anyway; mark `confidence: low | N=1`. Phrase rules conservatively. Prefer "In the example examined, the author tends to…" over "The author always…". Do not assert invariants from a single document. The negative-space (Group G) signal is the most reliable contribution from an N=1 corpus — what the document does not contain can be reported with confidence; what it does contain cannot.
- **An example file is empty or contains only frontmatter.** Skip with a note in the skill report. Do not count toward N.
- **A file exceeds 50,000 words.** Read the first 30,000 words for extraction. Note the truncation in the skill report.
- **The corpus conflicts on a feature.** Phrase the rule to reflect the range, not to pick a side. Example: "Citation integration varies — both parenthetical and narrative forms appear; no strong preference observed."
- **No examples exist in any genre** (all directories empty). Error and stop: "No example files found under `examples/`. Drop `.md` or `.txt` files into `examples/papers/`, `examples/grants/`, or `examples/other/` and re-run."
- **`content/ai-drift.md` missing.** Error and stop: extraction depends on it for the negative-space sweep.
- **User rejects the diff.** Do not write the file. Do not partially write (no scratch files left behind). The existing file is untouched.
- **An existing style file has been hand-edited beyond `## Manual overrides`.** In `refresh` mode, the user's edits to other sections will be overwritten (with confirmation). In `update` mode, the skill should warn that hand-edits outside `## Manual overrides` are not preserved and recommend moving them to `## Manual overrides`.

---

## Worked example — fixture corpus

Running this protocol with `--genre=papers --mode=init` against `tests/fixtures/style-extraction-corpus/` (two short papers in a consistent voice):

**Section 2:** Lists `sample-paper-1.md`, `sample-paper-2.md`. N=2 → `confidence: low | N=2`.

**Section 3 per-document features (aggregated):**
- Group A: marker phrase `"What is striking here is that"` (4×); discourse marker `"Notably,"` (2×); verbs like `treat`, `displace`, `incorporate`, `decompose` (≥3× each); negative-space: `delve`, `leverage`, `crucial`, `robust`, `foster`, `harness`, `navigate`, `in recent years` all 0×.
- Group B: median sentence in the long bucket (~28 words); em-dashes present in most paragraphs as parenthetical elaboration; semicolons occasional; sentence-initial adverbs and subordinate-clause openers dominant.
- Group C: hedges embedded in subordinate clauses ("to the extent the term picks out something worth keeping"); productive hedges like "is best understood as" present; filler meta-hedges ("It is important to note that") absent.
- Group D: 100% parenthetical citations; ~1 cite per 100 words; cites end-of-sentence; max 1 cite per parenthetical observed; appended (not grammatically integrated).
- Group E: paragraphs 3–5 sentences; topic-sentence first; no bullets inside argument; paragraphs close by qualifying or extending.
- Group F: claims set up by hypothetical/perspective framings ("If we treat X as Y, then…", "On the present view, X…"); sections close with forward-pointing pivots; conspicuously avoids "ultimately" closers, false balance, concession-reversal default.
- Group G: large absent-AI-drift set as above.
- Group H: exemplar candidates such as the verbatim sentence carrying the "What is striking here is that…" pivot and a subordinate-clause-opener sentence; signature frame `If we treat [X] as [Y], then [Z].` with a real instantiation.

**Section 4 synthesis** (N=2, every feature appears in both → genre rules):
- Marker phrase, "Notably," opener, em-dash baseline, parenthetical-only citations, embedded hedging, forward-pointing closers, absence of named AI-drift — all become rules.
- Group H: a curated handful of verbatim exemplars (clean, move-spanning) and the recurring `If we treat [X] as [Y], then…` frame go into `papers.md`; nothing exemplar-related enters base.md.

**Section 5 output file** (`content/styles/papers.md`):
- Frontmatter: `confidence: low | N=2`.
- `## Sentence`: median ~28 words; rarely exceed ~40; em-dashes baseline; sentence-initial adverbs / subordinate-clause openers dominant.
- `## Lexicon — preferred`: "What is striking here is that"; "Notably,"; preferred inquiry verbs.
- `## Lexicon — avoid`: the absent AI-drift list.
- `## Hedging`: embedded in subordinate clauses; productive hedges preferred; filler meta-hedges to avoid.
- `## Citation integration`: parenthetical-dominant; ~1 per 100 words; end-of-sentence; appended.
- `## Paragraph architecture`: 3–5 sentences; topic-sentence first; no bullets in argument; close by qualifying/extending.
- `## Argumentative moves`: hypothetical/perspective claim setups; forward-pointing section closers; conspicuous avoidances.
- `## Signature phrasings`: the `If we treat [X] as [Y], then [Z]` frame with one real instantiation.
- `## Exemplars`: a few verbatim, clean, move-spanning passages, each tagged with its source file.
- `## Manual overrides`: empty template.

This matches every "Required observations" item in `tests/fixtures/expected/style-extraction.expected.md`: median sentence length, em-dash use, parenthetical-citation dominance, marker phrase captured, absent AI-drift listed, paragraph architecture described, embedded hedging noted, low-confidence marker present.

---

## Operational notes

- Rules are instructions to the review skill, not numeric thresholds. Whenever in doubt about a rule's phrasing, ask: would the review skill know what to do with this as Dimension C input? If not, rephrase.
- Be conservative at low N. The user can always add to `## Manual overrides` if the extracted rules undershoot.
- Negative space carries more signal than positive features at low N. Absences are observable across all N documents trivially; positive features need replication.
- `## Exemplars` and `## Signature phrasings` are the **write-side payload** — they exist to make `marginalia-write` reproduce voice, and are not consumed by `marginalia-review`. Their value is the literal text, so the cardinal sin here is a mangled or paraphrased exemplar. When extracting from a PDF-converted corpus, spend the curation effort on rejecting artifact-bearing passages; a smaller clean set beats a larger dirty one.
- The `## Manual overrides` section is sacred. Never paraphrase, summarize, or reorder it. Preserve byte-for-byte.
- No silent overwrites. `refresh` and `update` always require diff + confirmation.
