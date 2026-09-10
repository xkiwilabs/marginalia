# Adapt protocol

> **Paths.** `content/styles/…` and `examples/…` below are names, not locations. Resolve them via `content/paths.md` (`$MARGINALIA_HOME`, then `~/.marginalia/`, then the repo). Resolve once per run and keep the same root throughout.

The procedure `marginalia-adapt` follows. Loaded once at the start of every adapt run. The SKILL.md is a thin entry point; this file is the actual procedure.

`adapt` derives a **provisional style overlay** for a target format the author has not yet built a corpus for — a blog, an op-ed, a newsletter, a talk, an email. `extract-style` needs a corpus; when none exists, `adapt` transforms the author's known cross-genre invariants (`content/styles/base.md`) for the target format's register, anchored in the author's own least-formal existing writing. The output is explicitly a *hypothesis* — marked low-confidence and provisional — about how the author would write in the new format, and it is built to **decay into a real profile**: as real pieces accumulate, `extract-style --genre={target} --mode=update` replaces the derived rules with measured ones.

Three things `adapt` is **not**: (1) it is not a real extraction — its output is derived, never presented as measured fact; if a corpus already exists for the format, use `extract-style`, not `adapt`. (2) It is not a generic format-voice generator — it must not import format clichés (fake hooks, listicles, "in this post we'll…"); `base.md`'s `## Lexicon — avoid` is a hard constraint. (3) It performs no silent writes — the derived overlay is shown as a diff and written only on confirmation.

The output overlay uses the **same section schema as `extraction-protocol.md` Section 5**, so that `write`, `review`, and `calibrate` consume a derived `{target}.md` exactly as they consume an extracted one.

Follow sections in order. Where a section says "if X, error", produce the error and stop — do not produce a partial overlay or write a file.

---

## Section 1: Inputs

- **`--to=<format>`** (required) — the target format. Either a **preset name** (`blog`, `op-ed`, `newsletter`, `talk`, `email`) or an **arbitrary slug** (e.g. `substack`, `keynote`, `cover-letter`). The slug also names the output file: `content/styles/{target}.md` and the `--genre={target}` flag downstream. An arbitrary slug with no matching preset **requires** `--samples` to ground the register — without it, error per Section 6.
- **`--samples=<paths>`** (optional) — paths to **1–3** samples of the target format. Used to sharpen the register: measured values from the samples override preset defaults (Section 3 step 2). Samples may be any format `input-ingestion.md` supports; they are converted to `.md` siblings before measurement, the same as the corpus.
- **`--from=base`** (optional) — the base profile to transform. Default: `base`. Resolves to `content/styles/{from}.md` (default `content/styles/base.md`).
- **Implicit inputs:**
  - The base profile: `content/styles/base.md` (or the `--from` target). Required. Missing → error per Section 6.
  - The corpus: `examples/` (all available genre subdirectories — `papers/`, `grants/`, `other/`), read to mine the author's loosest existing passages (Section 3 step 3). Same converted `.md` corpus that `extract-style` reads; adapt introduces no new ingestion path.

Record the resolved inputs in working memory; they appear in the output banner/frontmatter (Section 4) and the skill report.

---

## Section 2: Register presets

A preset is a **register delta** — a description of how the target format differs *from the author's academic prose* along a fixed set of dimensions. Presets are **register transforms, not voices.** They do not describe a voice to imitate; they describe how to *bend* the author's existing voice for a looser, more public register. The author's voice (sentence habits, signature phrasings, the `## Lexicon — avoid` constraint) comes from `base.md` and from the mined informal anchors; the preset only says *which dial moves, and how far.*

The fixed dimensions, applied to every preset:

- **Sentence length** — relative to the academic baseline (median ~28–32 words, long-bucket dominant).
- **Formality** — register level: how far below journal/grant formality.
- **Citation density** — how much of the academic citation apparatus survives.
- **Grammatical person** — first-person stance (`I` vs `we` vs impersonal).
- **Contractions** — permitted or not.
- **Opener style** — how a piece / paragraph opens in this register.
- **Paragraph length** — relative to the academic 4–8-sentence baseline.
- **Devices encouraged / forbidden** — format-appropriate moves to reach for, and clichés to refuse (the forbidden list is *additive* to `base.md`'s avoid-list, never a replacement for it).

### `blog`

- **Sentence length:** shorter and more varied than academic prose; mix short punchy sentences with the author's longer clause-dense ones. Median drops toward ~18–22 words; the very-long tail is trimmed.
- **Formality:** informal-but-substantive. A knowledgeable peer talking, not lecturing.
- **Citation density:** sparse. Replace parenthetical `(Author, Year)` bundles with inline links or a named mention ("as Gibson argued"); keep at most the load-bearing references.
- **Grammatical person:** first-person singular `I` is permitted and natural (a departure from the academic `we`); `we` for genuinely collaborative work only.
- **Contractions:** permitted ("don't", "it's", "we've").
- **Opener style:** open on a concrete observation, a question the post answers, or a stake — never a fake hook or a throat-clearing scene-setter.
- **Paragraph length:** shorter — 2–4 sentences; single-sentence paragraphs allowed for emphasis.
- **Devices encouraged:** worked examples, the author's intuition-pump openers ("Consider…"), direct address sparingly. **Forbidden:** listicles, "in this post we'll…", fake hooks, clickbait framing, SEO keyword stuffing, "Let's dive in."

### `op-ed`

- **Sentence length:** tight and forceful; shorter than academic, with deliberate rhythm. Median ~16–20 words.
- **Formality:** public-intellectual register — authoritative but accessible; no jargon without a gloss.
- **Citation density:** near-zero formal apparatus; evidence is named in prose, not parenthesized.
- **Grammatical person:** first-person `I` for the argued position; `we` only as the civic/collective "we."
- **Contractions:** permitted.
- **Opener style:** lead with the claim or the stake in the first sentence; the thesis is up front, not buried.
- **Paragraph length:** short — 1–3 sentences; journalistic paragraphing.
- **Devices encouraged:** a clear single thesis, concrete stakes, a forward-pointing close that lands the argument. **Forbidden:** academic hedging stacks, false-balance "on one hand / on the other," bullet summaries, "in conclusion," rhetorical-question filler.

### `newsletter`

- **Sentence length:** conversational; medium-short with variation. Median ~18–24 words.
- **Formality:** warm and direct — writing to a known audience who opted in. Personal but informed.
- **Citation density:** light; inline links over parentheticals; name sources conversationally.
- **Grammatical person:** first-person `I`; direct address to the reader ("you") is natural here.
- **Contractions:** encouraged.
- **Opener style:** a brief personal or topical lead-in that earns the reader's attention honestly; can reference the cadence ("this week").
- **Paragraph length:** short — 2–4 sentences; scannable.
- **Devices encouraged:** a clear through-line, occasional direct address, a sign-off that points forward. **Forbidden:** fake urgency, "you won't believe…", listicle padding, hype openers, manufactured FOMO.

### `talk`

- **Sentence length:** short and spoken — built for the ear, not the eye. Median ~12–18 words; one idea per sentence.
- **Formality:** spoken register; the author thinking aloud to a room.
- **Citation density:** essentially none in the spoken line; sources named lightly ("Gibson's idea was…").
- **Grammatical person:** first-person `I`; direct address to the audience ("you", "imagine you…").
- **Contractions:** encouraged (spoken language uses them).
- **Opener style:** open with a question, a concrete image, or an intuition pump the audience can hold in mind — the author already favors "Consider…" / "Imagine…", which travel directly here.
- **Paragraph length:** very short — these are spoken beats, not paragraphs; 1–3 sentences per beat, with signposting between them ("So here's the puzzle.").
- **Devices encouraged:** intuition pumps, repetition for emphasis, explicit signposting, the worked example. **Forbidden:** dense subordinate-clause stacks that lose a listener, parenthetical citation apparatus, on-screen-bullet prose, "Thank you for your attention" filler.

### `email`

- **Sentence length:** brief and purposeful. Median ~12–18 words; respect the reader's time.
- **Formality:** professional but human; calibrated to the recipient (collegial by default).
- **Citation density:** none, beyond a named link or attachment reference.
- **Grammatical person:** first-person `I`; `we` for shared work; direct `you`.
- **Contractions:** permitted (professional email is not a journal article).
- **Opener style:** state the purpose in the first line; no warm-up paragraph before the ask.
- **Paragraph length:** very short — 1–3 sentences; one ask or point per paragraph.
- **Devices encouraged:** a clear ask, a single subject per message, a concrete next step. **Forbidden:** corporate filler ("I hope this email finds you well", "circle back", "touch base", "per my last email"), hedging stacks, buried asks.

An arbitrary `--to` slug with **no matching preset** cannot be transformed from a register delta alone — there is nothing to bend toward. Such a slug **requires `--samples`** so the register can be measured directly (Section 3 step 2). With neither a preset nor samples, error per Section 6.

---

## Section 3: Flow

1. **Load the base profile and the corpus.** Load `content/styles/base.md` (or the `--from` target). If it is missing → error per Section 6 and **stop** — there is nothing to transform. Note the base profile's `confidence` / `N` from its frontmatter for provenance. List the corpus under `examples/` (all available genre subdirectories), converting any non-Markdown files to `.md` siblings per `content/input-ingestion.md`. An empty corpus is not fatal here — adapt can proceed from `base.md`'s rules alone — but it weakens step 3 (note it).

2. **Resolve the target register.** Resolve `--to`:
   - If `--to` matches a **preset**, load that preset's register delta (Section 2) as the starting register.
   - If `--samples` are given, **measure them** — sentence length (median bucket), grammatical person (`I` / `we` / impersonal), and contraction use, at minimum; also citation density and paragraph length where the samples are long enough to be reliable. **Measured values override the preset defaults** on the dimensions they cover; preset defaults stand on dimensions the samples do not exercise. Record which dimensions came from samples vs. preset.
   - If `--to` is an **arbitrary slug with no preset**, the register comes entirely from the measured samples (an arbitrary slug without samples already errored at step 1 / Section 6).
   - If samples were requested but are unreadable or empty, proceed on the preset alone with a note (Section 6).

3. **Ground the informal end in the author.** The looser register must be anchored in the author's *own* writing, not invented. Auto-mine the corpus for the author's **loosest existing passages** — the ones nearest the target register: **lowest citation density, shortest sentences, most first-person, discussion / introduction register** (intros, discussions, and any conversational/tutorial passages carry the author's least-formal voice). Select a small set of clean passages — target **3–6 passages** — (apply the cleanliness bar of `extraction-protocol.md` Group H criterion 4 — reject conversion artifacts, broken hyphenation, figure/table debris, footnote-number runs, mojibake; prefer body prose over scaffolding). **Record which passages were used** (source file + approximate location) for the report and the overlay's provenance. If no minable informal passages exist (a uniformly formal corpus), proceed from preset + invariants and note that the informal end is preset-inferred (lower confidence) — Section 6.

4. **Transform.** Apply the resolved register delta (step 2) to the invariants (`base.md`) and the mined anchors (step 3) to produce the overlay's sections (Section 4 schema). The transform *bends the dials the delta names* while keeping the author's voice intact. HARD RULES:

   a. **`base.md`'s `## Lexicon — avoid` carries over UNCHANGED** as a hard constraint. Copy it verbatim into the overlay's `## Lexicon — avoid` section. The register changes; the avoid-list does not. No format clichés are admitted: no fake hooks, no listicles, no "in this post we'll…", no clickbait. The preset's own "forbidden" devices are *added* to this list, never substituted for it.

   b. **Carry register-portable `## Signature phrasings`; drop or flag the non-portable ones.** Walk `base.md`'s (and, if relevant, the most apt overlay's) signature frames. A frame is portable if its *shape* survives the register shift (e.g. the definitional em-dash appositive, the "Consider…" intuition pump, the gap→aim pivot all travel to a blog or talk). A frame is non-portable if it belongs to the academic apparatus the target sheds — **grant deliverable / impact frames do not belong in a blog**, dense parenthetical-citation frames do not belong in a talk. Drop non-portable frames, or carry them with an explicit `[non-portable in {target} — flagged]` note rather than silently importing them.

   c. **`## Exemplars` = the mined informal anchors (step 3), tagged as cross-register specimens.** Place the mined passages verbatim under `## Exemplars`, each tagged with its source file AND a marker that it is borrowed from another register (e.g. `[cross-register specimen: from papers — discussion register]`). They are real authorial text, marked as borrowed — a starting point for the target voice, not measured target-format text.

---

## Section 4: Output overlay

Write `content/styles/{target}.md` in the **standard schema** — the same sections, in the same order, as `extraction-protocol.md` Section 5. Do not invent new sections; `write` / `review` / `calibrate` expect the standard shape.

**Top-of-file order (so two executors produce byte-identical files):** frontmatter → DERIVED / PROVISIONAL banner → H1 (`# {Target} style …`) → sections (in the order below).

### Frontmatter

```yaml
---
genre: {target}
confidence: low | derived
derived_from: base
derived_at: <UTC ISO-8601 write time>
---
```

Field semantics:
- `genre`: the target slug (`blog`, `op-ed`, `substack`, …). This is what `--genre={target}` selects downstream.
- `confidence`: the literal string `low | derived` — distinct from the extraction confidences (`low | N=k`, etc.) precisely so a derived overlay is never mistaken for a measured one.
- `derived_from`: the `--from` profile (default `base`).
- `derived_at`: UTC timestamp at the moment the file was written, ISO 8601.

### Provisional banner

The **first line after the frontmatter** is this banner, VERBATIM (substitute the target slug for `{target}`):

```
<!-- DERIVED / PROVISIONAL: transformed from base.md, not extracted from a {target} corpus.
     Replace via `extract-style --genre={target} --mode=update` once real pieces exist. -->
```

### Sections (standard schema, in order)

`# {Target} style (derived from base.md — provisional)`, then: `## Sentence`, `## Lexicon — preferred`, `## Signature phrasings`, `## Lexicon — avoid (carried over from base.md — hard constraint)`, `## Hedging`, `## Citation integration`, `## Paragraph architecture`, `## Argumentative moves`, `## Exemplars`, `## Manual overrides`. Populate each from the Section 3 transform:

The avoid-list heading deliberately differs from extraction's `## Lexicon — avoid (AI defaults absent from your corpus)`: for a derived overlay the "absent from your corpus" parenthetical is wrong — this avoid-list is carried over from `base.md`, not corpus-measured. Downstream consumers (review Dimension C) match the `## Lexicon — avoid` **prefix**, not the full heading string, so the parenthetical qualifier is free to differ across extracted and derived overlays.

- `## Sentence` — the register-adjusted sentence rules (length, openers, devices per the resolved delta), phrased as declarative instructions per `extraction-protocol.md` §5b.
- `## Lexicon — preferred` — the author's preferred lexicon from `base.md`, minus academic-only items the register sheds; plus contraction guidance where the preset permits.
- `## Signature phrasings` — the portable frames (Section 3 rule b), with non-portable ones dropped or flagged.
- `## Lexicon — avoid (carried over from base.md — hard constraint)` — `base.md`'s avoid-list **verbatim** (Section 3 rule a), plus the preset's forbidden devices.
- `## Hedging` — register-adjusted (academic registers hedge heavily; op-ed / talk hedge far less — trim the hedging stacks while keeping the author's productive hedges).
- `## Citation integration` — the register-adjusted citation rule (inline links / named mentions vs. parenthetical bundles).
- `## Paragraph architecture` — the register-adjusted paragraph rule (shorter paragraphs per the delta).
- `## Argumentative moves` — claim setup / close adjusted for the register, while keeping the conspicuous-avoidances list from `base.md`.
- `## Exemplars` — the mined cross-register specimens (Section 3 rule c), verbatim, tagged.
- `## Manual overrides` — the standard empty template (always present):
  ```markdown
  ## Manual overrides
  <!-- User-authored rules. Preserved across re-extractions. Add rules here that you want the review skill to enforce. -->
  ```

### Diff and confirm

Show a **diff preview** of the new file (it is a new file, so the diff is the full proposed content presented for review) and **write only on confirmation**. The no-silent-write norm applies even to a new file. If the user rejects, write nothing and leave no scratch files behind.

---

## Section 5: Decay path

The derived overlay is a stopgap meant to be **replaced by real extraction**, not maintained as a hand-tuned artifact. Document this in the output (the banner says it) and here:

- As real pieces land in `examples/{target}/`, run `extract-style --genre={target} --mode=update`. Update-mode merges the new corpus with the existing file: derived rules that the real pieces contradict are dropped, derived rules the real pieces confirm are kept and re-grounded, and new measured rules are added. Over successive updates, the derived rules are replaced by measured ones and the `confidence: low | derived` frontmatter becomes a real `confidence: … | N=k`.
- Once **≥1 real piece** exists in `examples/{target}/`, `calibrate --genre={target}` can validate the overlay against held-out real text (the calibration protocol needs at least one real document to hold a passage out of — see `calibration-protocol.md` §9).
- **Genre generalization.** `write`, `review`, and `calibrate` all load `content/styles/{genre}.md` from the `--genre` flag, so `--genre={target}` works as soon as the derived file exists — the toolkit's genre space is not limited to `papers/grants/other`. Note the one fixed exception: genre **auto-detection** (in `write-protocol.md`) stays limited to the original genres; **new formats require an explicit `--genre={target}`**, they are not auto-detected.

---

## Section 6: Errors and edge cases

- **No `base.md` (or `--from` target missing).** Error and **stop**: "No base profile. Run `/marginalia extract-style` first." There is nothing to transform.
- **Unknown `--to` slug AND no `--samples`.** Error and **stop**, listing the available presets: "No preset for `{slug}`. Available presets: `blog`, `op-ed`, `newsletter`, `talk`, `email`. For an arbitrary format, pass `--samples=<paths>` (1–3 samples of the target format) so the register can be measured." An arbitrary slug needs either a preset or samples; it has neither.
- **`content/styles/{target}.md` already exists.** Do **not** silently overwrite. Warn that a profile for this format already exists, and suggest the right next step: if real pieces exist, `extract-style --genre={target} --mode=update` (replace derived rules with measured ones); otherwise, confirm explicitly that a re-derivation (overwriting the existing derived file) is intended. Proceed only on explicit confirmation, through the Section 4 diff-and-confirm.
- **Samples unreadable or empty.** Proceed on the preset alone, with a note in the report that the requested samples could not be measured and the register is preset-default only. (If the slug had no preset, this collapses to the unknown-slug error above — an arbitrary slug with unreadable samples has no register source.)
- **No minable informal passages** (a uniformly formal corpus, or an empty corpus). Proceed from preset + invariants, and note in the overlay and report that the informal end is **preset-inferred, not author-grounded** — lower confidence. The `## Exemplars` section in this case is empty or carries only the formal-corpus passages nearest the register, flagged as such.

---

## Operational notes

- All operational logic lives in this protocol; the SKILL.md is a thin loader ("load `content/adapt-protocol.md`, then follow it"). The same applies to the Phase 2 MCP `marginalia.adapt` tool and the Phase 3 CLI — they call this protocol unchanged. The register-preset catalog (Section 2) is portable across runtimes.
- **No silent writes.** The derived overlay is proposed, diffed, and written only on explicit confirmation (Section 4), and an existing target file is never overwritten without it (Section 6).
- **The output is provisional and meant to be replaced.** A derived overlay is a hypothesis about the author's voice in a new register; it is `confidence: low | derived` and decays into a real profile via `extract-style --mode=update` (Section 5). Do not present it, or let downstream tools present it, as measured fact.
- **`content/styles/*` is the author's local profile** — gitignored. The derived overlay lands in the same directory as the extracted ones and is treated identically by `write` / `review` / `calibrate`, distinguished only by its `derived` confidence and provisional banner.
