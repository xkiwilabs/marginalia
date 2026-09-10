# Expected output for style extraction on `style-extraction-corpus/`

When `marginalia-extract-style` is run with `--genre=papers` against the two-paper corpus in `style-extraction-corpus/`, it MUST produce `content/styles/papers.md` (or, in a test harness, a comparable output file) containing at minimum the sections and observations below.

## Required sections
- `## Sentence` (with length and em-dash observations)
- `## Lexicon — preferred` (capturing the marker phrase)
- `## Signature phrasings` (recurring syntactic frames with `[slots]` + a real instantiation — write-side payload)
- `## Lexicon — avoid`
- `## Hedging`
- `## Citation integration` (parenthetical-dominant)
- `## Paragraph architecture`
- `## Exemplars` (verbatim specimens lifted from the corpus, each tagged with its source file — write-side payload)
- `## Manual overrides` (empty, present for user edits)

## Required observations

### Sentence
- Median sentence length flagged at ~28 words (the corpus runs long; "rarely exceed ~40" is an acceptable upper-bound articulation)
- Em-dash use noted as a deliberate voice marker, used for parenthetical elaboration mid-sentence
- Long sentences with embedded subordinate clauses noted as characteristic; short declarative sentences are rare

### Lexicon — preferred
- The marker phrase **"What is striking here is that"** is captured as a preferred lexicon item (it appears 4 times across the two papers)
- The opener **"Notably,"** is captured as a preferred discourse marker (appears 2 times across the corpus)
- Verbs of inquiry that do appear (e.g., "treat", "displace", "incorporate", "decompose") may be listed as preferred; not strictly required

### Lexicon — avoid
- The avoid list should reflect the absence of common AI-drift in the corpus: no "delve", "leverage", "crucial", "robust", "foster", "harness", "navigate", "in recent years"
- The skill is expected to draw on `content/ai-drift.md` for the avoid list and note which entries are *especially* avoided given the corpus

### Signature phrasings
- At least one recurring syntactic frame is captured with `[bracketed slots]` plus one real instantiation quoted from the corpus (e.g. a `If we treat [X] as [Y], then [Z]` / `On the present view, [X]` claim-setup frame). Frames are structure, not content — they must contain slots, not be a copied whole sentence.

### Exemplars
- At least a few **verbatim** passages are lifted unchanged from the two sample papers, each ≤60 words and tagged with its source filename. These are write-side voice specimens — they must be verbatim (not paraphrased) and free of conversion artifacts. The marker-phrase sentence ("What is striking here is that…") is a natural exemplar candidate.

### Citation integration
- Parenthetical-citation dominance noted explicitly (all citations in both papers are parenthetical `(Author, Year)` form; narrative `Author (Year)` form does not appear)
- Citation density approximately 1 per 100 words noted

### Paragraph architecture
- Paragraphs are long (3–5 sentences), open with a substantive claim rather than a scene-setting opener, and close by qualifying or extending the opening claim rather than restating it
- No bullet lists inside argumentative passages — flagged as a structural negative-space marker

### Hedging
- Hedging is present but embedded in subordinate clauses ("to the extent the term picks out something worth keeping") rather than fronted ("It is important to note that...")
- Fronted meta-hedges are absent from the corpus and should be on the avoid list

## Confidence marker
Since the corpus is N=2, the file must be marked `confidence: low | N=2` in a header or YAML frontmatter. The review skill is expected to weight low-confidence overlays less heavily and lean more on `base.md`.

## What the test does NOT require
- The skill may produce additional observations (sentence-length variance, clause depth statistics, specific verb-frequency lists). Those are acceptable but not required.
- Exact phrasing of the rules is not prescribed; the *content* of each required observation must be present in some form.
