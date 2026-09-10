# Write protocol

> **Paths.** `content/styles/…` and `examples/…` below are names, not locations. Resolve them via `content/paths.md` (`$MARGINALIA_HOME`, then `~/.marginalia/`, then the repo). Resolve once per run and keep the same root throughout.

The procedure `marginalia-write` follows. Loaded once at the start of every writing-help invocation. The SKILL.md is a thin entry point; this file is the actual procedure.

The output of this protocol is **prose** (or an edit to existing prose) that matches the author's learned voice rather than generic AI register. This is preventive rather than corrective: the rules in the style files act as constraints on the draft, not as flags on a draft already produced.

Follow sections in order.

---

## Section 1: Inputs

- **`task`** (required) — implicit, from the user's request. Common task shapes:
  - **Draft from scratch.** "Draft an executive summary for X", "Write an introduction for…", "Compose a paragraph on…"
  - **Revise existing text.** "Tighten this paragraph", "Rewrite this section to read more like me", "Make this less AI-sounding"
  - **Edit in place.** "Apply edits to this sentence", "Make this sharper", "Cut 20% from this paragraph"
  - **Short-form prose.** Titles, captions, abstracts, section headers, bullet items in grants.

- **`source_text`** (optional) — when the task is revising or editing existing prose, the source. Usually pasted into the chat or referenced by file path.

- **`genre`** (optional, override) — `papers`, `grants`, `other`. If not supplied, auto-detect from the working directory and request context:
  - Path contains `grant-proposals`, `proposals`, `grants`, `funding`, or cwd contains files matching `*proposal*` / `*grant*` → `genre = grants`.
  - Path contains `papers`, `manuscripts`, `drafts`, or cwd contains files matching `*paper*` / `*manuscript*` / `*draft*` → `genre = papers`.
  - Path contains `essays`, `op-eds`, `letters`, or the request explicitly names a non-paper/non-grant form → `genre = other` (if `other.md` exists, else fall back to base.md alone).
  - Otherwise default to `papers` and silently note the assumption.
  - When the request explicitly overrides ("write this in grant register" while in a paper workspace), honour the override.
  - An explicit `--genre=<slug>` may name **any** extracted or derived overlay (e.g. `--genre=blog`), loading `content/styles/{genre}.md`; the genre space is not limited to `papers`/`grants`/`other`. Auto-detection (above) remains limited to `papers`/`grants`/`other` — new formats require an explicit `--genre=<slug>`.

If genre detection is ambiguous and the request is non-trivial (a section, multiple paragraphs), ask one short clarifying question rather than guess.

---

## Section 2: Load context files

Paths are relative to the marginalia repo root.

1. **`content/styles/base.md`** — required. Missing → error and stop with: `No base style available. Run /marginalia extract-style --genre=all first to bootstrap from your published work.`
   - Read its `## Signature phrasings` section — the cross-genre frames. Hold them as generation targets (Section 3).
2. **`content/styles/{genre}.md`** — optional. Missing → note `no {genre} overlay available; using base.md only` in the response header and proceed with base.md alone.
   - When present, read its `## Exemplars` and `## Signature phrasings` sections in full. These are the **single most important inputs** to drafting in voice — real specimens of the author's prose and the author's recurring sentence frames. The abstract rules in the other sections describe the voice; these *show* it. Keep them in working memory throughout generation.
3. **`content/ai-drift.md`** — *do not load by default*. The base.md + genre overlay already contain the corpus-derived avoid lists, which are the subset of ai-drift.md relevant to this author. Load `ai-drift.md` only if the user explicitly asks for an exhaustive AI-drift check on the produced prose — and in that case prefer routing to `marginalia-review` for a formal post-check.

Record the loaded files in the response header (one short line, e.g., `*Drafting in your voice — base.md + grants.md.*`).

---

## Section 3: Apply style as positive + negative constraints

The style files contain two kinds of material, applied differently: **concrete voice specimens** (`## Exemplars`, `## Signature phrasings`) and **abstract rules** (everything else). Lead with the specimens — they carry the texture that abstract rules flatten away — and use the rules to keep the draft inside the author's envelope.

### Exemplars and signature phrasings (primary voice targets)

This is the lever that makes prose sound like the author rather than like generic academic register. Before writing, study the loaded `## Exemplars` and `## Signature phrasings`, then generate prose that **imitates their rhythm and construction**:

- **Match the sentence rhythm and clause architecture of the exemplars** — how clauses stack, where elaboration is inserted, how long a typical sentence runs, where the author breaks for a parenthetical gloss or an em-dash appositive. The exemplars are the ground truth for what one of the author's sentences actually feels like; the `## Sentence` rules are a summary of them, not a substitute.
- **Reach for the signature-phrasing frames** where the content fits. If you are introducing a claim and the author's frame `The [adjective] implication of these findings is that [claim]` fits, instantiate it with the current content rather than inventing a generic frame. These frames are the author's structural fingerprints.
- **Reproduce the density of characteristic moves** the exemplars show — e.g., if most exemplar passages carry a `(i.e., …)` / `(e.g., …)` re-gloss, the draft should too, at a comparable rate; if hedges sit mid-clause on the main verb, place them there.

**Critical guard — imitate the voice, not the content.** The exemplars are specimens of *style*, not source material. Never reuse an exemplar's wording, subject matter, examples, or claims in the draft. If the requested prose is on a topic an exemplar happens to discuss, still write fresh content — the exemplar governs *how* a sentence is shaped, never *what* it says. Lifting phrases verbatim from an exemplar is a failure of this protocol, not a success of voice-matching. A reader who knows the author's work should think "this reads like them," never "I've seen that sentence before."

If no genre overlay loaded (base.md only), you have the cross-genre `## Signature phrasings` but no `## Exemplars`; lean harder on the abstract rules below and note the reduced fidelity in the header per Section 5.

### Positive rules
The `## Sentence`, `## Lexicon — preferred`, `## Hedging`, `## Citation integration`, `## Paragraph architecture`, and `## Argumentative moves` sections describe the **shape** of the author's voice. The output should reach for these constructions where natural. Specifically:

- Use the author's preferred verbs (the **Lexicon — preferred** list) instead of AI-default verbs of inquiry.
- Use the author's preferred discourse pivots (`Indeed,`, `However,`, `Accordingly,`, `Consistent with`, `Building on`) where a transition is needed.
- Use the author's preferred claim-setup patterns appropriate to the genre (paper register: `Consider X`, `Take for example X`, `On the present view`, `If X is Y, then Z`; grant register: `Aim 1: …`, `Building on prior work…`, problem-statement → gap → solution).
- Match the author's typical sentence length (long bucket dominant; subordinate clauses; embedded parentheticals).
- Match the author's typical paragraph length (4–6 sentences) and architecture (topic-sentence first; develops or qualifies the opener; closes by extending or pivoting, not by restating).
- Match hedging style — embedded inside subordinate clauses, not as fronted meta-comments.

### Negative rules
The `## Lexicon — avoid` section lists constructions the author *does not use*. The output should **never** include them. From the author's corpus the relevant absences include:

- Verbs: `delve`, `leverage` (in papers), `navigate` (metaphorical), `foster`, `harness`, `unpack`, `unlock`, `weave`, `illuminate`, `surface` (as verb), `spotlight`, `underscore`, `elucidate`, `explore` (as default investigative verb).
- Adjectives: `multifaceted`, `nuanced`, `intricate`, `vibrant`, `transformative`, `paradigm-shifting`, `seamless`, `holistic`, `thoughtful`, `meaningful` (as booster), `rich`, `compelling`, `deeply`.
- Closers: `Ultimately,`, `In conclusion,`, `In summary,`, `Taken together,`, `As we have seen`.
- Openers: `In recent years,`, `Today,`, `In the modern era,`, `In today's world,`, `In the modern landscape`.
- Meta-hedges: `It is important to note that`, `It should be noted`, `One might argue that`, `It is worth considering that`.
- Meta-phrases: `navigating the complexities of`, `the intersection of X and Y`, `at its core`, `by no means exhaustive`, `a growing body of`, `plays a crucial role in`, `a deeper understanding of`, `shed light on`, `the realm of`.
- Filler discourse markers used decoratively (not where the logical relation is real): `Moreover,`, `Furthermore,`, `Additionally,`, `In addition,`, `Consequently,`, `Hence,`.
- Formatting tells: emoji in headers, trailing-summary boxes / blockquote pull-outs, decorative `---` rules, bold-emphasis on every other sentence, inconsistent header capitalisation.

The exact list in effect is whatever the loaded style files say. The above is illustrative.

### Manual overrides
The `## Manual overrides` section at the bottom of each style file is user-authored. It takes precedence over both positive and negative extracted rules. Apply manual-override rules even when they appear to conflict with the extracted profile — the user has hand-edited them deliberately.

### Genre caveats
Per `grants.md`, some lexicon entries (`robust`, `comprehensive`, `crucial`, `dynamic`) appear in the author's grant prose more often than in their paper prose. In grant register these can carry technical meaning rather than filler. Treat them case-by-case: use them when they're doing real work (`robust performance under occlusion`, `dynamic systems analysis`); avoid them as default boosters. The default behaviour is conservative — prefer the alternatives unless the technical sense is plainly the right word.

---

## Section 4: Produce prose

Generate the requested prose (or revision). Keep the constraints in mind throughout — they shape word choice, sentence structure, paragraph architecture, and rhythm, not just lexicon. Hold the `## Exemplars` beside the draft as you write and check each sentence against them: does this read like one of the author's sentences? The goal is prose that would not need a `/marginalia review` pass to clean up, because the writing pass already used the same rules and the same specimens. (Remember the Section 3 guard: imitate their shape, never their content.)

### When revising existing prose

- Preserve the source's content and argumentative structure. Style edits only by default.
- If the source has issues beyond style (a buried claim, an over-strong assertion, a non-sequitur, a citation hung on a claim broader than the cite supports), flag them separately in a brief note after the revision rather than silently rewriting the argument.
- For citation-bearing prose, flag uncertain citations rather than tightening or removing them — citation accuracy is the `marginalia-verify-cites` skill's job.

### When drafting from scratch

- Match the user's typical paragraph length and architecture.
- Match the user's claim-setup and section-closing patterns for the genre.
- Use the corpus-derived marker phrases and signature-phrasing frames where they fit naturally — do not force them, and do not copy exemplar content (Section 3 guard).
- If the user has not specified length, default to a paragraph (4–6 sentences for both papers and grants). Ask if more is needed.

### When producing very short prose (a sentence, a phrase, a title)

- The full voice profile still applies, but the post-write review offer (Section 5) is overkill. Skip the offer for sub-paragraph outputs.

---

## Section 5: Output discipline

The chat response is minimal scaffolding around the prose:

1. **One-line header** before the prose:
   - For drafting: `*Drafting in your voice — base.md + {genre}.md.*`
   - For revision: `*Revising in your voice — {genre} register.*`
   - When the genre overlay is missing: `*Drafting in your voice — base.md only ({genre}.md not yet extracted).*`

2. **The prose itself.** Verbatim, ready to copy-paste. No surrounding quotation marks or fenced blocks unless the prose is a list or code-adjacent.

3. **Optional brief note (one line)** if a constraint was hard to honour or if a content-level concern surfaced during revision. Example: `Left "foster" in line 3 — replacement made the surrounding clause awkward; easy to swap if you'd rather.`

4. **Optional offers** for paragraph-length or longer prose:
   - `Want me to run /marginalia review on this for a formal voice check?`
   - For prose with citations: `Citations not verified — run /marginalia cite when ready.`

Skip the offers for sub-paragraph outputs (single sentences, phrases, titles).

---

## Section 6: When NOT to engage

This skill is for academic prose specifically. Do not engage on:

- Code drafting (programming, scripts, configs).
- Email drafts unless the user explicitly invokes — email has different register.
- Brief Q&A or factual questions ("what is X?") — the answer should be direct, not styled.
- Documentation that isn't academic prose (READMEs, technical docs, API references).
- Drafts where the user has asked for a non-personal voice ("write this in Hemingway's voice", "make it more casual", "draft a corporate-style version").

For ambiguous requests ("help me write something about X"), ask one short clarifying question: `Academic prose (pull in your voice profile), or something else?`

---

## Section 7: Edge cases

- **No style files yet.** If `content/styles/base.md` does not exist, the skill cannot apply the user's voice. Error with: `No style profile available. Run /marginalia extract-style --genre=all first to bootstrap from your published work.`
- **Ambiguous genre.** If cwd hints do not resolve and the request itself is genre-agnostic ("draft a paragraph on X"), ask once: `Paper register or grant register?`
- **User explicitly overrides genre.** "Write this for a paper" → load `papers.md` regardless of cwd.
- **Source text in a different genre than the request.** If the user pastes paper-style prose and asks for grant-register revision, follow the request (it is an intentional cross-register rewrite).
- **Conflict between base.md and overlay.** Manual overrides win; otherwise the overlay's more-specific rule takes precedence (matches the review-protocol convention).
- **User asks for explicit AI-drift inclusion** ("write this in deliberately generic AI style for contrast"). Honour the request and note that the voice constraints are being intentionally suspended.
- **Long-form drafting (multiple sections).** Produce the prose. Offer `/marginalia review` once at the end of the draft rather than after each section.
- **Output is meant to be written into a file.** Ask first — do not modify files in-place. The chat artefact is the default deliverable.

---

## Operational notes

- This skill is a **co-writer aid**, not a review tool. Output that doesn't match the voice rules should be revised before delivery, not flagged after.
- The style files are the source of truth for what the author's voice is. If the user disagrees with a rule, that is a signal to update the style file (typically by adding a manual override in `## Manual overrides`), not to bypass the skill for one turn.
- This skill is paired with `marginalia-review` (post-write critic) and `marginalia-verify-cites` (citation verifier). The three together cover the lifecycle: write in voice, then review for drift, then verify citations.
- The skill engages on description match — pattern-matched against the user's request — not by explicit invocation. The user can still invoke explicitly via `/marginalia write [task]` if they want to force engagement, but the default is silent auto-engagement on writing-help requests.
