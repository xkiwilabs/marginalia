# Calibration protocol

> **Paths.** `content/styles/…` and `examples/…` below are names, not locations. Resolve them via `content/paths.md` (`$MARGINALIA_HOME`, then `~/.marginalia/`, then the repo). Resolve once per run and keep the same root throughout.

The procedure `marginalia-calibrate` follows. Loaded once at the start of every calibration run. The SKILL.md is a thin entry point; this file is the actual procedure.

`calibrate` is a self-test, not a writing or review tool. It answers two questions about an extracted voice profile (`content/styles/base.md` + a genre overlay): does the profile reproduce the author's voice, and what does the profile change versus generic AI prose. It does so by holding out a passage of the author's own writing, stripping it to bare content, asking a blind subagent to reconstruct it from that skeleton plus the profile, and scoring the reconstruction move-by-move against the real original. When a move comes back weak, calibrate proposes a concrete, confirmable edit to the profile — so the loop closes and the user *tunes* the profile, not merely inspects it.

The verdict is a move-by-move rubric (reached / partial / missed), deliberately not a single number — the marks are the actionable unit. No prose calibrate produces is deliverable; the artifacts are a report and proposed profile edits.

Follow sections in order. Where a section says "if X, error", produce the error and stop — do not produce a partial report or a fabricated verdict.

---

## Section 1: Inputs

- **`genre`** (optional) — `papers`, `grants`, `other`, or any extracted/derived overlay slug (e.g. `blog`); loads `content/styles/{genre}.md`, falling back per the existing missing-overlay handling. Default `papers`. Selects which overlay is tested and which corpus directory is drawn from.
- **`mode`** (optional) — one of:
  - `reconstruct` — hold out a passage, reconstruct it blind from the skeleton + profile, score the reconstruction against the real original. **Default** (no mode flag).
  - `contrast` (`--contrast`) — reuse the same held-out passage and skeleton; draft it both with the profile (voiced) and without (generic baseline), and present a three-way read against the real original. Implies the rubric is applied to both the generic and the voiced output.
  - `both` (`--both`) — run one held-out passage through both flows, producing the rubric and the three-way read from a single selection.
- **Implicit inputs:**
  - Corpus location: `examples/{genre}/` relative to the marginalia repo root. Same converted `.md` corpus that `extract-style` reads — calibrate introduces no new ingestion path.
  - Profile: `content/styles/base.md` (required) plus the genre overlay `content/styles/{genre}.md`. Missing `base.md` → error per Section 9.

Record the resolved inputs in working memory; they appear in the report header (Section 8).

---

## Section 2: Shared setup

Both modes share these four steps. They are the steps the orchestrator (the skill, running in the main context) is *allowed* to perform while seeing the user's original passage; regeneration is firewalled into subagents that never see it (Sections 4 and 5).

1. **Resolve genre and load profile.** Resolve `genre` to the corpus directory and overlay. Load `content/styles/base.md` (required) and `content/styles/{genre}.md` (the overlay). If `base.md` is missing → error per Section 9 and stop. Record the overlay's `confidence` / `N` from its frontmatter for the report header; if the overlay is missing, note it and proceed against `base.md` alone (the rubric will be built from `base.md`'s sections only).

2. **Auto-select a held-out passage.** From a continuous-prose document in `examples/{genre}/`, select one clean passage of roughly **150–400 words** that bears **at least one signature move** (a parenthetical re-gloss, the gap→aim pivot, an em-dash appositive, a productive hedge, a characteristic claim setup, or a genre-specific move). **Prefer a passage that is NOT present verbatim in the overlay's `## Exemplars`.** If the only viable passages are exemplars, use one and flag it prominently (Section 9). Reject passages bearing conversion artifacts (broken hyphenation, figure/table debris, equation gibberish, footnote-number runs, mojibake, and injected running headers, footers, page numbers, or figure/caption lines that split otherwise-continuous prose at print-page breaks — common in pandoc/pdftotext output), and avoid titles, headers, captions, and reference-list fragments — apply the same cleanliness bar as `extraction-protocol.md` Group H criterion 4. When such pagination debris is injected mid-paragraph, skip the passage or stitch around the injection when choosing the held-out passage.

3. **Apply the leakage guard.** Build a temporary, in-memory copy of the profile with the held-out passage's *overlapping* exemplars removed. **Overlap test:** remove any `## Exemplars` entry that shares a verbatim run of **≥8 consecutive words** with the held-out passage (equivalently, shares a full sentence with it). State this threshold so two executors guard identically. This guarded copy is what the regen subagent receives, so it cannot reconstruct by echoing an exemplar that is itself the original. **Record which exemplars were excluded** (count and source) for the report header. The original profile files on disk are never modified by this step.

4. **Extract the content skeleton** from the held-out passage (Section 3).

---

## Section 3: Content skeleton

The skeleton is the de-styled propositional content of the held-out passage: *what the passage says*, with *how it says it* discarded. A faithful reconstruction then reflects the profile, not an echo of the original. The skeleton is the load-bearing firewall — because the orchestrator saw the original, a leaky skeleton would bake the author's style back in and the verdict would be dishonest. Keep it strict.

```
RULE: Reduce the passage to bare propositional bullets — claims, entities, and
logical relations only. Strip ALL of: adjectives/adverbs, signature phrasings,
sentence shapes, hedging constructions, citation formatting, em-dashes and
parentheticals. Write in deliberately flat register.

ORIGINAL:
"The degree to which the self-organized behavioral dynamics of interpersonal
rhythmic coordination can be generalized to more complex multiagent tasks
remains uncertain, however, because the majority of previous research has
explored only simple rhythmic behaviors."

SKELETON:
- prior coordination findings come mostly from simple rhythmic tasks
- whether they generalize to complex multi-agent tasks is unknown
```

Notice what the skeleton drops: the hedge ("remains uncertain"), the signature gap-marker rhythm ("however, because…"), the field-technical noun phrases compressed to flat terms, and any sentence shape. It keeps only the two propositions and their logical relation. If you find a bullet smuggling in an adjective, a sentence frame, or a hedge, flatten it further before proceeding.

---

## Section 4: Mode — reconstruct

1. **Spawn the regen subagent.** Pass the content skeleton (Section 3) and the leakage-guarded profile (Section 2 step 3) using the prompt below verbatim. The subagent is blind to the original passage — it sees only the skeleton and the guarded style files.

   ```
   You are drafting academic prose in a specific author's voice. You are given:
   (1) a CONTENT SKELETON — bare propositional bullets, and
   (2) STYLE FILES — base.md plus a genre overlay, including ## Exemplars and
       ## Signature phrasings describing the author's voice.

   Write prose that expresses EXACTLY the content in the skeleton — no more, no
   less — while imitating the rhythm, sentence frames, and characteristic moves of
   the exemplars and signature phrasings. Do NOT reuse any exemplar's wording,
   subject matter, or claims. You will NOT see the original passage; reconstruct
   from the skeleton alone. Return ONLY the prose, no commentary.

   <skeleton>{skeleton}</skeleton>
   <style>{guarded base.md + overlay}</style>
   ```

   If the subagent fails or returns nothing usable, handle per Section 9 — report the failure, do not fabricate a verdict.

2. **Judge the reconstruction.** In the main context, score the returned prose against the **real held-out original** as ground truth, on the rubric derived in Section 6. "Reached" means the reconstruction did what the original did *at that point* — not merely that it used the device somewhere.

3. **Identify the weakest move(s).** From the rubric, take every `✗ missed` and `~ partial` move and route it to the feedback loop (Section 7).

4. **Write the report and apply confirmed edits.** Emit the report (Section 8). For each proposed edit from Section 7, show the diff and confirm individually before any write (Section 7 and the diff-and-confirm discipline of `content/apply-protocol.md` §5).

---

## Section 5: Mode — contrast

Contrast reuses the **same held-out passage and skeleton** from Section 2, so the author's real original anchors the comparison — a stronger test than a topic with no ground truth.

1. **Spawn the baseline subagent.** Pass only the skeleton, with *no* profile loaded, using the prompt below verbatim. This produces generic academic prose — the "without profile" column.

   ```
   Write a clear, competent academic paragraph expressing EXACTLY the content in
   the skeleton below. Use your default register. No special voice instructions.
   Return ONLY the prose, no commentary.

   <skeleton>{skeleton}</skeleton>
   ```

2. **Spawn the regen subagent** with the skeleton + the leakage-guarded profile, using the verbatim prompt from Section 4 step 1. This produces the voiced "with profile" column.

3. **Present the three-way read.** Lay out the three texts side by side or in sequence: **generic / voiced / the real original**. Apply the Section 6 rubric to **both** the generic column and the voiced column, scored against the real original as ground truth, so the user can see which voice moves the profile recovers that the generic baseline does not.

4. **Print the caveat.** State plainly that the generic baseline is **model-generated** — by a model that already knows the voice — so it is illustrative, not a naive control. This caveat also goes in the report header (Section 8).

If either subagent fails, handle per Section 9: report the failure for that column and do not fabricate its verdict.

When `mode = both`, run Section 4's reconstruct judging and Section 5's three-way read over the single held-out passage and skeleton. As in `contrast` mode, the Section 6 rubric is rendered over **both** columns (generic and voiced), scored against the real original; the voiced column's rubric also serves as the reconstruct verdict that feeds Section 7. The result is one rubric (both columns) and one three-way read in a single report.

---

## Section 6: Rubric

The rubric is **derived from the loaded style file, not hard-coded**, so it stays in sync as the profile evolves and differs by genre automatically. Build the move list, in this order, from:

- The overlay's **`## Signature phrasings`** — each frame becomes a move ("did the reconstruction deploy this frame where the original did?").
- Load-bearing rules in **`## Sentence`** (e.g., em-dash appositive, the `(i.e., …)` parenthetical re-gloss, characteristic openings).
- **`## Hedging`** (productive hedge constructions; position).
- **`## Lexicon — preferred`** (did the reconstruction reach for the author's preferred verbs/refrains at the points the original did?).
- **`## Argumentative moves`** (claim setup, anchoring, forward-pointing closings).
- The **`## Lexicon — avoid`** list, rendered as a single **no-drift check** move (did the reconstruction stay clean of the avoid-list defaults?).

Select the moves the held-out original *actually exercises* — do not score the reconstruction on a move the original never made. Keep the list to the moves that carry the passage's voice (typically 5–8), not every rule in the file.

Mark each move with one of three marks, each carrying an evidence quote, scored against the real original as ground truth:

- **`✓ reached`** — the reconstruction deploys the move where the original did; quote it.
- **`~ partial`** — attempted but weak or incomplete; quote it and state what is off.
- **`✗ missed`** — absent, or replaced by a drift pattern; quote what it did instead.

If the reconstruction compresses or merges the host clause so that an original move has no slot in which to appear (e.g., the original fronts "Moreover," or "Indeed," on a clause the reconstruction folded away), score that move `~ partial` with a "no slot (compressed)" note — do not force `✓` or `✗`.

**No aggregate score is emitted.** The per-move marks are the verdict. Close the rubric with a one-line "Weakest:" summary naming the `✗`/`~` moves that feed Section 7.

```
Voice fidelity — reconstruct (papers, N=16)
Held-out: <corpus-file>.md  ·  leakage guard: 1 exemplar excluded

✓ gap→aim pivot          "…remains unclear; accordingly, the aim…"
✓ parenthetical re-gloss "specify (are information about)…"
✗ em-dash appositive     missed — used a comma-bounded clause instead
~ preferred lexicon      3/5 — reached 'specify','constrain'; used 'explore' (drift)
✓ forward-pointing close "…what allows it to recover" (not a restatement)
✓ no AI-drift            clean (0 avoid-list hits)

Weakest: em-dash appositive (missed), 'explore' (drift)
```

In `contrast` mode, render the rubric twice (or as two columns) — once for the generic baseline, once for the voiced reconstruction — so the differential is visible.

---

## Section 7: Feedback loop

For each `✗ missed` or `~ partial` move from the rubric, generate **exactly one** proposed style-file edit. The fix type is chosen by the weakness:

- **Add or strengthen an `## Exemplars` entry** — the **default**, and the right lever for a *missed* move. The likely cause is that the overlay's `## Exemplars` under-represents the move, so the regen subagent had no clean specimen to imitate. Pull a clean corpus passage that *does* demonstrate the move (apply the cleanliness bar from Section 2 step 2) and propose adding it verbatim to `## Exemplars`, tagged with its source file and the move it shows.
- **Add a `## Manual overrides` rule** — for *drift despite good exemplification* (the move is well-represented in `## Exemplars` but the reconstruction drifted anyway, e.g., reached for an avoid-list word). A standing instruction is the right lever; `## Manual overrides` is the highest-priority section for both write and review.

Apply the diff-and-confirm discipline of `content/apply-protocol.md` §5: show each proposed edit as a diff and confirm it **individually** — the user may take some and skip others. No edit is written without its own confirmation. When an edit is applied, log it in the profile with a `(calibrate <date>)` tag so the provenance of every tuned entry is visible (e.g., append ` — (calibrate 2026-06-14)` to the entry, or include the tag in the manual-override rule). For an `## Exemplars` entry that already ends with a bracketed `[move]` tag, append the `(calibrate <date>)` tag at the very end of the entry line, after any existing source-file and `[move]` tags. The provenance tag is intentionally day-precision (`<date>`), unlike the minute-precision report filename in Section 8 — entry-level provenance does not need run-level granularity, so this difference is by design, not an oversight.

Re-running calibrate after applying an edit should move the corresponding mark toward `✓` — the loop is observable. This observability assumes the **same held-out passage is re-selected**; because passage auto-selection (Section 2 step 2) is non-deterministic, the report records the held-out passage (file + approximate location, per the Section 8 header) so the user can re-run on the same passage and see the mark move.

**SCOPE GUARD.** calibrate proposes edits to **only** `## Exemplars` and `## Manual overrides`. It must **never** propose an edit to any other section — `## Sentence`, `## Lexicon — preferred`, `## Lexicon — avoid`, `## Hedging`, `## Citation integration`, `## Paragraph architecture`, `## Argumentative moves`, `## Signature phrasings`, or frontmatter are all off-limits. Those are the auto-derived, validated rule sections; calibrate cannot silently rewrite them.

---

## Section 8: Report

Write the report to `.marginalia/calibrate-<YYYY-MM-DD-HHMM>.md` (UTC, minute precision). Create the directory if missing; if a file with the same timestamp exists, append `-2`, `-3`, etc. — never overwrite. The `.marginalia/` directory is gitignored.

The report begins with this header, verbatim (fill the angle-bracket slots):

```
# Calibrate — <YYYY-MM-DD-HHMM>

- **Genre:** <genre> · overlay confidence: <confidence | N>
- **Mode(s):** <reconstruct | contrast | both>
- **Held-out passage:** <examples/{genre}/<file>> (~<n> words)
- **Leakage guard:** <k> exemplar(s) excluded for this run
- **Caveat:** Auto-hold-out measures in-sample fit of the rules, not true
  generalization.<if contrast: The generic baseline is model-generated.>
```

After the header, the report contains, in order:

1. **The rubric table** (Section 6). In `contrast`/`both` mode, render the rubric for both the generic and the voiced columns.
2. **The texts:**
   - `reconstruct` → the voiced reconstruction vs. the real original.
   - `contrast` → the three-way read: generic / voiced / real original.
   - `both` → the three-way read plus the reconstruct rubric.
3. **Weakest-move analysis** — the `✗`/`~` moves named in the rubric's "Weakest:" line, with a sentence each on the likely cause.
4. **Proposed edits** (Section 7) — each rendered as a diff and **marked applied or skipped** per the user's per-edit confirmation.

---

## Section 9: Errors and edge cases

- **No `base.md`.** Error and stop: "No style profile. Run `/marginalia extract-style` first."
- **Empty `examples/{genre}/`** (no eligible clean passage). Error naming the genre and suggesting genres that *do* have content; stop. E.g., "No clean passage available in `examples/papers/`; try `--genre=grants`."
- **Corpus too small to hold one out cleanly** (e.g., a single short document). Proceed, but print a **strong caveat** in the report that the held-out passage and the in-sample corpus fully overlap, so the test measures memorization rather than generalization.
- **Held-out passage is unavoidably a verbatim exemplar.** Use it and **flag prominently** in the report. The leakage guard (Section 2 step 3) still excludes that exemplar from the run's profile, so the test retains teeth.
- **Regen or baseline subagent fails** (errors out, returns empty, or returns commentary instead of prose). Report the failure for that mode/column; do **not** fabricate a verdict for it. In `contrast`/`both`, the surviving column may still be reported.
- **Non-Markdown corpus files.** Already converted to `.md` siblings by `content/input-ingestion.md`; calibrate reads the `.md`, the same as `extract-style`. Never operate on the original source.

---

## Operational notes

- All operational logic lives in this protocol; the SKILL.md is a thin loader ("load `content/calibration-protocol.md`, then follow it"). The same applies to the Phase 2 MCP `marginalia.calibrate` tool and the Phase 3 CLI — they call this protocol unchanged.
- **No silent writes.** Every style-file edit is proposed, diffed, and applied only on explicit per-edit confirmation (Section 7, and the diff-and-confirm discipline of `content/apply-protocol.md` §5).
- **Reports are annotated artifacts.** calibrate is a self-test that recommends; the author decides which proposed edits to apply.
- The verdict is the move-by-move rubric — never an aggregate fidelity number. The marks are what the user acts on.
- The skeleton is the firewall. The honesty of the whole test rests on a strict, style-stripped skeleton (Section 3); when in doubt, flatten the bullets further.
- `.marginalia/` report directories are gitignored intermediate artifacts.
