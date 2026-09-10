# AI-drift: lexicon and structural anti-patterns

This file catalogs patterns over-represented in LLM-generated academic prose. It is consumed by `marginalia-review` as the lexicon and anti-pattern sweep, and by `marginalia-extract-style` as the negative-space reference — the author's voice is partly defined by which of these patterns they do *not* use.

Entries describe LLM defaults that survive light editing, not general writing faults. Each entry names the pattern, says why it reads as AI rather than as bad style, and gives a concrete alternative the review skill can propose. Where a pattern is sometimes acceptable, the entry says so and gives a triggering condition for flagging.

How to read severity cues:
- "Why flagged" should anchor the issue in LLM statistical behaviour, not in taste.
- "Confidence" (where present) tells the review skill how aggressively to flag.
- "Suggested alternatives" are intended as drop-in replacements for the `proposed` field of a review issue; for structural patterns the proposal is usually `null` because the fix needs author judgement.

---

## Lexicon — verbs

### "delve"
**Pattern:** Used as a verb of inquiry: "we delve into…", "this paper delves into…", "let us delve deeper into…"
**Why flagged:** The single most over-represented academic verb in LLM output since 2023; corpus studies of post-ChatGPT text show order-of-magnitude jumps. Human academic writers in cognitive science, philosophy, and adjacent fields rarely choose "delve" for first-pass inquiry framing.
**Suggested alternatives:** "examine", "investigate", "consider", "treat", "take up", "engage with", "turn to", "work through"

### "leverage"
**Pattern:** Used as a transitive verb meaning "use" or "make use of": "we leverage X to do Y", "leveraging recent advances in…"
**Why flagged:** A management-consulting borrowing that LLMs reach for whenever the underlying verb is "use". Outside of finance and management writing, it almost always reads as register-mismatch; the plain verb is stronger.
**Suggested alternatives:** "use", "draw on", "exploit", "build on", "apply", "recruit" (for cognitive/biological contexts)

### "navigate"
**Pattern:** Used metaphorically with abstract objects: "navigate the complexities of…", "navigating uncertainty", "navigate this tension"
**Why flagged:** LLMs use "navigate" as a default verb for any situation involving difficulty or ambiguity, well beyond its literal sense. Human writers tend to reserve it for genuinely spatial or sequential-decision contexts.
**Suggested alternatives:** "work through", "address", "handle", "manage", "respond to", or simply name the activity ("decide between…", "weigh…")

### "foster"
**Pattern:** Used with abstract nouns: "foster collaboration", "foster understanding", "foster a culture of…"
**Why flagged:** A high-frequency LLM verb for any positive-causal relationship. It is rarely the most precise option; specific causal verbs ("support", "enable", "produce", "make possible") usually do more work.
**Suggested alternatives:** "support", "enable", "encourage", "produce", "give rise to", "make room for"

### "harness"
**Pattern:** Used with technology, methods, or capacities as direct objects: "harness the power of…", "harness AI", "harness recent advances"
**Why flagged:** Combines two LLM tendencies — energy-metaphor verbs and inflated diction for ordinary "use". Almost always means "use" in academic contexts.
**Suggested alternatives:** "use", "apply", "draw on", "recruit", "deploy"

### "unpack"
**Pattern:** Used as a verb of explication: "let us unpack this claim", "unpacking the implications of…"
**Why flagged:** Has a real life in some philosophical and qualitative-methods writing, but LLMs reach for it whenever explication is needed, producing it 5–10x more often than human authors typically do. Flag when paired with abstract nouns ("unpack the complexity", "unpack the nuance").
**Confidence:** Medium. Flag in argumentative prose; tolerate in methods sections where unpacking really is the move.
**Suggested alternatives:** "examine", "set out", "spell out", "make explicit", "work through", or restructure to do the explication rather than announcing it.

### "unlock"
**Pattern:** Used with abstract direct objects: "unlock new possibilities", "unlock insights", "unlock the potential of…"
**Why flagged:** Marketing-register metaphor. Pervasive in LLM grant-style prose; rare in mature academic writing.
**Suggested alternatives:** "reveal", "make available", "open up", "allow", or rephrase to name what becomes possible.

### "weave"
**Pattern:** Used as a verb of integration: "weave together", "weave X into Y", "this chapter weaves…"
**Why flagged:** Default LLM metaphor for synthesis or integration. The textile metaphor is conspicuous in academic prose and rarely fits the actual relationship being described.
**Suggested alternatives:** "integrate", "combine", "bring together", "link", "connect", "draw together"

### "illuminate"
**Pattern:** Used for any clarificatory move: "this illuminates how…", "the case illuminates…"
**Why flagged:** Light-metaphor verb LLMs reach for whenever the underlying claim is "shows" or "clarifies". Inflated relative to the work it does.
**Suggested alternatives:** "show", "clarify", "make clear", "expose", "bring out", "reveal"

### "surface" (as verb)
**Pattern:** Used transitively for bringing something to attention: "surface tensions", "surface assumptions", "surface the underlying…"
**Why flagged:** A tech-industry borrowing that LLMs have absorbed into general academic register. Outside UX and product writing it reads as out of place.
**Suggested alternatives:** "bring out", "make explicit", "expose", "identify", "raise"

### "spotlight" (as verb)
**Pattern:** "This study spotlights…", "we spotlight three issues…"
**Why flagged:** Journalism-register verb that LLMs use for emphasis. Rare in scholarly writing.
**Suggested alternatives:** "highlight" (still mildly journalistic but defensible), "draw attention to", "focus on", "single out", or just state the point.

### "explore"
**Pattern:** Used as the default verb for any investigative move: "we explore the relationship between…", "this paper explores…"
**Why flagged:** Not wrong, but LLMs use "explore" as the universal undirected investigation verb where a more precise verb would commit to a method (test, model, argue, characterise). Flag when it appears as the headline verb of a section or paper without a more committed verb nearby.
**Confidence:** Low. Single uses are fine; flag clustering or use in load-bearing thesis sentences.
**Suggested alternatives:** "argue", "characterise", "model", "test", "examine", "develop an account of"

### "underscore"
**Pattern:** "These results underscore the importance of…", "this point underscores…"
**Why flagged:** A heightened-emphasis verb that LLMs over-use in claim-restatement sentences. Often signals a sentence that exists only to repeat the previous one.
**Suggested alternatives:** Often the sentence containing "underscore" can be cut. If kept: "show", "demonstrate", "make clear", "support".

### "elucidate"
**Pattern:** "We seek to elucidate…", "this elucidates the mechanism by which…"
**Why flagged:** Latinate elevation of "explain" or "clarify". LLMs reach for it when academic register is being signalled rather than achieved.
**Suggested alternatives:** "explain", "clarify", "make clear", "show"

---

## Lexicon — adjectives & adverbs

### "crucial"
**Pattern:** "It is crucial to…", "a crucial step", "crucially, …"
**Why flagged:** The default LLM intensifier for importance. Massively over-represented relative to "important", "central", "necessary", and load-bearing-specific terms. Flagged regardless of whether the underlying claim is right.
**Suggested alternatives:** "central", "necessary", "load-bearing", "decisive", or — most often — drop the intensifier and let the claim carry its own weight.

### "robust"
**Pattern:** "A robust account", "robust evidence", "robust framework"
**Why flagged:** LLM default adjective for any positive epistemic property. In statistics and engineering "robust" has a technical sense (insensitive to assumption violations); outside those uses it is a content-free booster.
**Confidence:** High when paired with abstract nouns (account, framework, approach); lower when modifying a method whose robustness is empirically tested.
**Suggested alternatives:** Specify what makes the thing strong — "well-supported", "general", "stable across X", "carefully argued" — or, if the technical sense isn't intended, drop the word.

### "comprehensive"
**Pattern:** "A comprehensive review", "comprehensive understanding", "comprehensive framework"
**Why flagged:** Almost always an over-claim in academic prose; LLMs reach for it as a default booster for coverage claims. Genuine comprehensiveness is rare and usually qualified.
**Suggested alternatives:** "broad", "wide-ranging", "extensive", "systematic", or qualify the scope ("covering X, Y, and Z").

### "multifaceted"
**Pattern:** "A multifaceted problem", "multifaceted phenomenon"
**Why flagged:** A content-free adjective whose only function is to signal complexity. Where the facets matter, they should be named.
**Suggested alternatives:** Name the facets. If that is not feasible, "complex" is shorter and equally informative; "many-dimensional" if precision is needed.

### "nuanced"
**Pattern:** "A nuanced view", "this nuanced position", "more nuanced understanding"
**Why flagged:** LLMs use "nuanced" as a positive evaluation of any non-extreme position. It typically does no descriptive work and signals approval rather than content.
**Suggested alternatives:** Specify the nuance — "qualified", "case-dependent", "stratified by X", or name the specific distinction the position draws.

### "intricate"
**Pattern:** "Intricate web of…", "intricate relationships", "intricate dynamics"
**Why flagged:** Decorative adjective that LLMs reach for when "complex" feels too plain. Adds no information.
**Suggested alternatives:** "complex", "tightly coupled", "interdependent", or characterise the structure ("recursive", "many-to-many", "feedback-laden").

### "vibrant"
**Pattern:** "A vibrant field", "vibrant community", "vibrant discussion"
**Why flagged:** Promotional adjective that almost never appears in mature academic argument. Strong AI signal.
**Suggested alternatives:** "active", "productive", "growing", "ongoing", or characterise what makes the field live ("rapidly producing replications", "publishing across journals X, Y, Z").

### "dynamic"
**Pattern:** "A dynamic process", "dynamic interaction", "dynamic relationship"
**Why flagged:** In cognitive science, dynamics has a technical meaning (state-space evolution over time); LLMs use "dynamic" as a content-free positive adjective. Flag the loose use; preserve technical uses.
**Confidence:** Context-sensitive. High when paired with abstract nouns and no technical follow-through; low when the surrounding text actually discusses temporal evolution, attractors, etc.
**Suggested alternatives:** If technical sense not intended: "changing", "evolving", "interactive", "ongoing", or be specific about the time-course.

### "transformative"
**Pattern:** "Transformative impact", "transformative technology", "transformative approach"
**Why flagged:** Grant-prose booster that LLMs reach for in any positive-impact framing. Over-claim by default.
**Suggested alternatives:** Specify what is transformed and how — "changes how X is measured", "reframes Y in terms of Z". If unspecifiable, drop the word.

### "paradigm-shifting"
**Pattern:** "Paradigm-shifting research", "paradigm shift in the field"
**Why flagged:** A claim that is almost always false and that working scientists almost never make about their own work in writing. Strong AI signal in author-voice prose.
**Suggested alternatives:** Drop, almost always. If a real reframing is being claimed, describe the reframing concretely.

### "seamless"
**Pattern:** "Seamless integration", "seamless interaction", "seamless experience"
**Why flagged:** Product-marketing register. Pervasive in LLM prose about systems and pipelines; absent from careful academic writing about the same systems (which would acknowledge the seams).
**Suggested alternatives:** "well-integrated", "low-friction", or — more honestly — name the residual frictions.

### "holistic"
**Pattern:** "A holistic approach", "holistic understanding"
**Why flagged:** Often empty in LLM use — does not specify what is being held together with what. Sometimes a genuine commitment (e.g., to non-reductive accounts), but the loose use far outnumbers the committed use.
**Confidence:** Medium. Flag in headline framing; tolerate where a specific holist position is being defended.
**Suggested alternatives:** "integrative", "non-reductive", "systems-level", or name the integration ("treating X, Y, and Z together rather than as separable").

### "thoughtful" (in the generic-positive sense)
**Pattern:** "A thoughtful approach to…", "thoughtful design", "thoughtfully crafted"
**Why flagged:** Content-free LLM compliment that adds approval without information. Rare in author-voice academic writing.
**Suggested alternatives:** Specify what makes the work thoughtful — "carefully argued", "attentive to X", "responsive to prior objections", or drop.

### "meaningful"
**Pattern:** "Meaningful progress", "meaningful contribution", "meaningful insights"
**Why flagged:** A booster that signals significance without specifying it. LLMs use it where statistical, theoretical, or practical significance should be named distinctly.
**Suggested alternatives:** Specify the kind of significance: "substantial", "non-trivial in effect size", "practically relevant", "theoretically novel".

### "rich"
**Pattern:** "A rich literature", "rich tradition", "rich body of work", "rich tapestry"
**Why flagged:** Default LLM adjective for any non-empty domain. Carries no descriptive load. "Rich tapestry" in particular is a near-certain AI signal in current prose.
**Suggested alternatives:** "extensive", "long-standing", "deeply developed", or — better — cite the actual contours of the literature.

### "compelling"
**Pattern:** "Compelling evidence", "compelling reasons", "a compelling case"
**Why flagged:** A persuasion-claim the writer is making on the reader's behalf. LLMs use it as a free booster; careful academic writing lets the evidence be compelling rather than asserting that it is.
**Suggested alternatives:** Drop, almost always. If kept: "strong", "well-supported", or characterise the strength ("converging across three independent measures").

### "deeply"
**Pattern:** "Deeply rooted", "deeply intertwined", "deeply problematic"
**Why flagged:** Intensifier-of-default LLMs append to any adjective or participle. Almost always removable without loss.
**Suggested alternatives:** Drop. If genuine intensification is needed, choose a stronger underlying word.

---

## Lexicon — discourse markers and transitions

These markers are not AI-drift in isolation. Flag the pattern of use: multiple per paragraph, sentence-initial as default opener, or filling the role that argumentative connective tissue should fill.

### "moreover"
**Pattern:** Sentence-initial transition between independent points.
**Why flagged:** LLMs use "moreover" 5–10x more often than careful academic writers, often as filler between weakly connected claims. Real "moreover" relations (adding strength to a same-direction argument) are rare.
**Confidence:** Low for any single instance; high when two or more appear per page, or when the connection between sentences is not actually additive.
**Suggested alternatives:** Drop and let the connection be carried by content; or use a more specific connective ("further", "in the same direction", "for the same reason"); or restructure so the additive relation is shown rather than announced.

### "furthermore"
**Pattern:** Sentence-initial transition, often interchangeable with "moreover".
**Why flagged:** Same profile as "moreover" — high-frequency LLM filler for additive transitions. Doubly suspect when paired with "moreover" in adjacent paragraphs.
**Suggested alternatives:** Drop; or "in addition" (still suspect; see below); or restructure.

### "additionally"
**Pattern:** Sentence-initial: "Additionally, …"
**Why flagged:** Same family as "moreover" / "furthermore". Strong AI signal especially when starting consecutive sentences or paragraphs.
**Suggested alternatives:** Drop; sometimes "also" (mid-sentence) reads better; usually restructure.

### "in addition"
**Pattern:** "In addition, X is also …"
**Why flagged:** Same additive-filler role. Often pairs redundantly with "also" later in the same sentence.
**Suggested alternatives:** Drop, or move the addition into the preceding sentence as a clause.

### "consequently"
**Pattern:** Sentence-initial causal connector.
**Why flagged:** Over-used by LLMs where the causal link is weak or implied rather than argued. Real "consequently" relations require the antecedent to actually entail the consequent.
**Confidence:** Medium. Acceptable when the causal logic has been set out; flag when used to paper over an inference gap.
**Suggested alternatives:** "so", "therefore", "as a result", or restructure to make the inference visible.

### "thus"
**Pattern:** Sentence-initial summary connector.
**Why flagged:** Has a legitimate role in argument summation but is over-used by LLMs as a generic connective. Flag when "thus" appears without a preceding argument that genuinely yields the conclusion.
**Confidence:** Low for single use; medium when "thus" / "hence" / "therefore" cluster within a few paragraphs.
**Suggested alternatives:** Keep if earned; otherwise drop or replace with "so".

### "hence"
**Pattern:** Sentence-initial or mid-sentence consequential.
**Why flagged:** Same profile as "thus". The combination of formal register and weak causal anchor is the AI-drift marker.
**Suggested alternatives:** Same as "thus".

### "indeed"
**Pattern:** Sentence-initial: "Indeed, X is …"
**Why flagged:** Used by LLMs as a free emphasiser that adds no logical content. Distinct from real "indeed" use, which strengthens a preceding claim against an implicit objection.
**Suggested alternatives:** Drop unless an objection is being answered.

### "ultimately"
**Pattern:** Sentence- or paragraph-initial summary: "Ultimately, X …"
**Why flagged:** Often introduces a conclusion the prose has not actually reached. A reliable signal of LLM closing moves, especially at the end of a section.
**Suggested alternatives:** Drop, or replace with the specific claim being made ("This means that…", "The upshot is…").

---

## Lexicon — meta-phrases

These are full phrases that LLMs use as connective scaffolding. They typically announce a move rather than making it; their removal almost never costs content.

### "it is important to note that"
**Pattern:** Sentence-initial: "It is important to note that X …"
**Why flagged:** The flag-bearer of LLM hedging-without-substance. If the thing is important, the sentence stating it carries the importance; the meta-announcement is redundant. Almost a definitional AI-drift marker at this point.
**Suggested alternatives:** Delete the preamble; start with the noted claim. If genuine emphasis is needed, restructure so the importance is shown in the surrounding argument.

### "it should be noted"
**Pattern:** "It should be noted that X …"
**Why flagged:** Same as above; passive variant. By whom should it be noted, and why is the noting necessary?
**Suggested alternatives:** Delete the preamble; state the claim.

### "as we have seen"
**Pattern:** "As we have seen, X …"
**Why flagged:** A closing-move LLM tic. Real "as we have seen" reaches are rare in academic prose, which more often cites a section number or reframes the prior claim. The phrase functions as a hand-wave back to material the reader is assumed to remember.
**Suggested alternatives:** Cite the section ("as argued in §2"), reframe the prior claim, or drop.

### "in the modern landscape"
**Pattern:** Scene-setting opener.
**Why flagged:** Almost never appears in pre-2023 academic prose. Pure LLM register.
**Suggested alternatives:** Specify the timeframe ("since 2010", "post-deep-learning") or drop the scene-setting.

### "in today's world"
**Pattern:** Scene-setting opener, often paired with "rapidly changing" or "increasingly complex".
**Why flagged:** Magazine/blog register. Strong AI-drift marker in scholarly contexts.
**Suggested alternatives:** Drop; if a present-tense framing is needed, name the specific current condition.

### "in recent years"
**Pattern:** Scene-setting opener: "In recent years, X has …"
**Why flagged:** The single most common LLM opening move for paragraphs introducing a literature or trend. Specific enough to feel scholarly, vague enough to commit to nothing. Flag whenever it appears as a paragraph-opener; especially flag when it opens a section or the document.
**Confidence:** High when opening a paragraph; high when used to introduce a literature; lower when used mid-paragraph with specific dates following.
**Suggested alternatives:** Replace with a specific date range ("since 2018", "over the past decade") or with the actual event ("after the publication of X"). Or drop the temporal scaffolding entirely if the literature can be introduced directly.

### "navigating the complexities of"
**Pattern:** "Navigating the complexities of [abstract noun]"
**Why flagged:** Combines two LLM defaults ("navigate" + "complexities of"). Almost always replaceable with the underlying activity.
**Suggested alternatives:** Name the activity directly: "deciding between X and Y", "weighing X against Y", "working out how X relates to Y".

### "the intersection of X and Y"
**Pattern:** "At the intersection of cognition and culture", "the intersection of AI and education"
**Why flagged:** A geographic-metaphor framing that LLMs reach for whenever two domains are jointly relevant. Carries no commitment to what the joint relevance is.
**Confidence:** Medium. Acceptable in field-positioning sentences when the intersection is the actual object of study; flag when used as a content-free positioning move.
**Suggested alternatives:** Specify the relation: "how X bears on Y", "X under conditions imposed by Y", "the import of X for Y".

### "at its core"
**Pattern:** "At its core, X is …"
**Why flagged:** LLM essence-claim opener. Promises a fundamental characterisation, usually delivers a paraphrase.
**Suggested alternatives:** State the characterisation directly; let the reader see whether it is core.

### "by no means exhaustive"
**Pattern:** Closing qualifier on a list or survey: "This list is by no means exhaustive…"
**Why flagged:** A self-aware meta-comment about the survey's incompleteness that LLMs append by default. If the survey is not exhaustive, that should be evident; the disclaimer is redundant.
**Suggested alternatives:** Drop. If a real scope-limitation needs stating, name what is being excluded and why.

### "a growing body of"
**Pattern:** "A growing body of work suggests…", "a growing body of evidence…"
**Why flagged:** Vague-citation-shape that LLMs use in place of actually citing work. Sets up a claim about literature volume that the cites should establish directly.
**Suggested alternatives:** Cite the works. If the volume of work is itself the point, give a count or characterise the publication trajectory.

### "plays a crucial role in"
**Pattern:** "X plays a crucial role in Y."
**Why flagged:** Triple AI-drift marker: "plays a role", "crucial", and the indirection of role-talk where a direct causal claim would be stronger.
**Suggested alternatives:** State the role directly: "X enables Y", "X is necessary for Y", "X produces Y under conditions Z".

### "a deeper understanding of"
**Pattern:** "Gain a deeper understanding of…"
**Why flagged:** Goal-talk that LLMs append to research-motivation sentences. Almost never specifies what depth would consist in.
**Suggested alternatives:** Name what would be understood: "how X depends on Y", "the mechanism by which…".

### "shed light on"
**Pattern:** "These results shed light on…"
**Why flagged:** Light-metaphor cliché. Pervasive in LLM prose summarising findings.
**Suggested alternatives:** "show", "clarify", "indicate", or characterise what the result actually reveals.

### "the realm of"
**Pattern:** "In the realm of cognition…", "the realm of AI ethics"
**Why flagged:** Fantasy/territory metaphor that LLMs use for any domain. Rare in mature academic prose, which tends to say "in cognition" or "in AI ethics" without the spatial scaffolding.
**Suggested alternatives:** Drop ("In cognition…"); or use "field", "domain", "area" if scaffolding is needed.

---

## Structural patterns — sentence level

### Tricolons (three-adjective or three-noun lists)
**Pattern:** "X is A, B, and C." Three parallel adjectives or short noun phrases for emphasis or summary. Especially common as the predicate of a thesis sentence ("intelligence is contextual, dynamic, and emergent").
**Why flagged:** The default LLM rhythm for emphasis. Three is the cadence trained into the model by web prose; human academic writing more often uses pair + qualifier ("X is A and B — though C…") or develops a single strong descriptor. Flag both adjective tricolons and short-noun tricolons.
**Confidence:** Medium. Tricolons are not always wrong; flag when they appear ≥2x per paragraph, in a load-bearing thesis sentence, or when the three terms are not genuinely independent (e.g., near-synonyms).
**Suggested alternative:** Pair + em-dash qualifier ("X is A and B — though C also matters when…"); or choose the strongest of the three terms and extend it; or replace with a single committed characterisation.

### Symmetric parallel construction overused
**Pattern:** Multiple consecutive sentences with the same syntactic shape: "Not only A but B." / "Not only C but D." Or: "It is not X; it is Y." repeated.
**Why flagged:** LLMs reach for syntactic symmetry to signal rhetorical care; in academic prose, repeated symmetry across sentences reads as performance rather than argument.
**Confidence:** Medium. Single parallels are fine and often forceful; flag chains of three or more parallel sentences.
**Suggested alternative:** Break the chain — vary sentence shape; subordinate one of the parallels; or replace the parallel with a single longer sentence that develops the contrast.

### Sentence-initial "Crucially," / "Importantly," / "Notably," as filler
**Pattern:** Sentences beginning with a free-standing importance-marker adverb.
**Why flagged:** These markers tell the reader to pay attention rather than earning attention through the sentence's content. LLMs use them as a default flag for "this is the key point". Genuine emphasis is usually carried by the surrounding argument.
**Confidence:** Medium. Occasional use is fine; flag clustering (two or more in a section) or use on every load-bearing sentence.
**Suggested alternative:** Drop the marker and let the sentence stand. If emphasis is needed, restructure so the prior sentence sets up the importance.

### Adversative "However," / "Yet," / "Nevertheless," opening every sentence-after-claim
**Pattern:** Habitual sentence-initial adversatives used to acknowledge a counter, often followed by an under-developed concession.
**Why flagged:** LLMs default to the concession-then-reversal move (see discourse patterns below) and front-load it with an adversative. Real adversatives are fine; the tell is the rhythm — every claim followed by a "However…" sentence.
**Confidence:** Medium. Flag when the rhythm is consistent over multiple paragraphs.
**Suggested alternative:** Vary: integrate the qualification into the same sentence ("X is true, though…"); or place the counter before the main claim; or skip the concession when it is not actually doing work.

### Hedge-stacking
**Pattern:** Multiple hedges in the same clause: "it may perhaps be possible that…", "it is somewhat likely that…", "it could potentially be argued that…"
**Why flagged:** LLMs hedge by accumulation when they should hedge by precision. Stacked hedges read as evasive rather than careful.
**Suggested alternative:** Choose one calibrated hedge; or state the claim and qualify the conditions under which it holds.

### Appended commentary clause (the "and-clause epigram")
**Pattern:** A sentence states a claim, then appends a coordinated clause that comments on, generalises, or evaluates the claim rather than adding information: "X is the case, **and it is** the reason Y", "X narrows the gap, **and the residue is** instructive", "X is the second constraint, **and it binds** independently of Z". The appended clause is typically abstract, quotable, and content-free.
**Why flagged:** LLMs close sentences with a summarising flourish because the training distribution rewards well-rounded prose. Scientific writing closes sentences with the next piece of information, not with a comment on the information just given. The tell is that deleting the appended clause loses nothing except the cadence.
**Confidence:** High when the appended clause contains no new noun the reader did not already have, or when it evaluates rather than specifies ("is instructive", "is what matters", "is the reason", "is a weaker guarantee than it appears").
**Suggested alternatives:** Delete the clause; or replace it with the specific detail it gestures at (the number, the mechanism, the condition, the citation). If the comment is genuinely load-bearing, make it its own sentence and give it evidence.

### Abstract nominalisation as sentence subject
**Pattern:** The grammatical subject is a derived abstract noun rather than the thing itself: "**Reviewability** is the property that…", "**Admissibility** is evaluated with respect to…", "**The residue** is instructive", "**The upshot** is…"
**Why flagged:** LLMs prefer nominalised subjects because they permit a definitional predicate ("X is the property that Y"). Scientific prose more often makes the concrete actor or artefact the subject ("A reviewer can read the policy before it runs"), which forces the writer to say who does what.
**Confidence:** Medium. Nominalisation is legitimate in formal definition; flag when the sentence could name a concrete agent or artefact instead, and when the predicate is a bare copula.
**Suggested alternatives:** Recast with the concrete subject and an active verb. "Reviewability is the property that makes assurance tractable" → "A reviewer can read the policy and check it against doctrine before it executes."

### Vague gesture in place of the specific
**Pattern:** The sentence points at a fact without stating it: "where the difficulty actually lies", "what matters here", "how many people are in the room", "whatever the generator failed to anticipate", "the part that surprised us".
**Why flagged:** LLM prose gestures at specificity to sound informed while committing to nothing checkable. In scientific writing the gesture should be replaced by the fact, which is usually one clause longer and far more useful.
**Suggested alternatives:** State the fact. If the fact is not known, say that it is not known and why.

### Metadiscursive setup sentence (announcing the move instead of making it)
**Pattern:** A sentence that describes what the *next* sentence is about to do, rather than doing it: "Before narrowing the claim **we should state** the strongest objection to it", "**We should be precise about** what is and is not novel here", "**It is worth separating** them because they are often run together", "**The question is** which agents talk to which others", "and the reason **turns on a distinction that is easy to lose**", "**What the result does establish is** that…". Frequently paired with an abstract noun the sentence never cashes out ("a distinction", "a tension", "an asymmetry", "a subtlety").
**Why flagged:** LLMs stage-manage the reader because the training distribution rewards signposted, essayistic argument. Formal scientific prose states the claim and lets the reader see the structure from the content. The tell: delete the setup sentence and the paragraph is unchanged except that it now begins with the actual point.
**Confidence:** High when the sentence contains no noun that appears in the argument itself, or when it opens with "Before…", "We should…", "It is worth…", "The question is…", "What X does is…".
**Suggested alternatives:** Delete it and promote the following sentence. If the setup carried real content (a concession being flagged, a term being fixed), state that content plainly and without the announcement: "We should be careful not to overstate the contrast" → "The contrast should not be overstated." "Before describing the loop we should fix one term" → "One term is used throughout what follows."

### The contrast-frame family ("not just X but Y" and its variants)
**Pattern:** One construction with several surfaces, all of which define a claim by first denying its cheaper alternative:
- `not just / not merely X but Y` — "This is not just X but Y"
- `not X; it is Y` — "Safety is not a stroke of luck; it is a guarantee"
- `not X. It is Y.` — the same move split across two sentences
- `X rather than Y` — "a rational choice rather than a compromise"
- `It is X, not Y, that …` — the cleft form
- `not only X, it is Y` — the additive form

**Why flagged:** A high-frequency LLM contrast construction. Any one instance can earn its keep, and often does when a reader really would reach for the wrong reading first. The tell is the **rate across the family**, not any single surface. Counted separately no variant clusters enough to notice; counted together the frame turns out to be carrying most of the document's emphasis, substituting for an argument about why the simpler description is inadequate.

This is also where a naively applied em-dash rule ends up when it does not end up in colons and semicolons. The contrast frame carries the same interruption in words rather than punctuation, so a document can post zero em-dashes, a disciplined colon rate, and still be built entirely out of pre-empted objections.

**Confidence:** The family is **not homogeneous**, and treating it as one undifferentiated set both over-flags and under-flags.

- Some surfaces are ordinary academic constructions that many authors use at a steady low rate. `X rather than Y` and `not just / not merely X but Y` are usually in this group. For these the family rate is the only reliable signal: **low** for a single instance, **medium** once the family total exceeds roughly one per 1,000 words, **high** above one per 800.
- The remaining surfaces — `not X; it is Y`, `not X. It is Y.`, the cleft `It is X, not Y, that …`, and `not only X, it is Y` — are markedly rarer in human academic prose and are strongly over-represented in LLM output. Where a style profile shows a surface at or near zero across the author's corpus, that is negative-space evidence of the same kind as `## Lexicon — avoid`, and a single occurrence is flaggable on its own.

**So: check the author's per-surface rates before applying a single family threshold.** Where `content/styles/` records them, follow the profile. Where it does not, count the family together and use the rates above, and say in the report that the split was unavailable.
**Suggested alternative:** Keep the instances where the denied alternative is one a reader would genuinely reach for first, and cut the rest to plain assertion. "Safety is not a stroke of luck; it is Unit 4's guarantee" → "Safety is Unit 4's guarantee." Where the contrast is real but the frame is overused, develop it across the surrounding sentences instead of compressing it into the construction.

---

## Structural patterns — paragraph level

### Topic sentence → three examples → restatement
**Pattern:** Paragraph opens with a general claim, gives three short examples (often as a tricolon or as three short sentences), and closes by restating the opening claim.
**Why flagged:** The default LLM paragraph architecture. Human academic paragraphs more often develop a single example at length, or use the paragraph to advance the argument rather than to illustrate it. The restatement closer is particularly telling.
**Confidence:** Medium-high when all three components are present.
**Suggested alternative:** Drop the restatement; develop one example fully; or restructure so the paragraph carries the argument one step further rather than illustrating a claim already made.

### "In recent years," / "Today, more than ever," / "In the modern era" openers
**Pattern:** Paragraph or section opens with a temporal scene-setting phrase, often introducing a literature or trend.
**Why flagged:** The single most recognisable LLM opener. Specific enough to feel scholarly, vague enough to commit to nothing. Often introduces a paragraph that the rest of the document could open without.
**Confidence:** High when opening a paragraph; high when opening a section.
**Suggested alternative:** Replace with a specific anchor ("Since the publication of X in 2018…"); or cut the opener and start with the actual claim.

### Closing paragraphs that restate the opening
**Pattern:** Final paragraph of a section restates, in different words, the section's first paragraph. Often signalled by "As we have seen…", "In summary…", "Ultimately…", "Taken together…"
**Why flagged:** LLMs close by restating because closing is hard; human academic writers more often close by extending — drawing a consequence, setting up the next move, or marking what remains unresolved.
**Confidence:** Medium-high when the closer's content is paraphrastic of the opener.
**Suggested alternative:** Replace the closer with a forward-looking move: an implication for the next section, a tension that remains, an empirical commitment the argument now incurs.

### Bullet lists inside argumentative prose
**Pattern:** A bulleted list appears in the middle of continuous argumentative prose to enumerate items that could be — and would more naturally be — given as a sentence or short paragraph. Often three bullets summarising the preceding paragraph.
**Why flagged:** Bullets are a presentation-software default that LLMs port into prose contexts where continuous argument is expected. Genuine list contexts (methods steps, criteria for a decision, lists of cases that will each be developed separately) tolerate bullets; argumentative bullets break the reader's expectation that the prose will carry the inference.
**Confidence:** High when the bulleted items are short clauses or noun phrases and the surrounding prose is argumentative. Lower when the list is a methods/criteria list or when each bullet is itself a developed paragraph.
**Suggested alternative:** Convert to continuous prose with explicit connectives. If three items genuinely belong together, a single sentence with serial commas or a short paragraph usually carries the weight better than a list.

### One-sentence transition paragraphs
**Pattern:** A standalone paragraph consisting of one short sentence whose job is to announce what the next paragraph will do ("Three considerations bear on this question.", "We turn now to the second feature.").
**Why flagged:** LLMs produce these as scaffolding. They are common in textbooks and rare in research-level academic prose, which tends to carry transitions within paragraphs.
**Confidence:** Medium. Acceptable in long-form pedagogical writing; flag in research prose unless the transition is genuinely load-bearing.
**Suggested alternative:** Move the transition into the prior or following paragraph as its opening or closing sentence.

### "Today's [X]" / present-tense scene-setting as paragraph opener
**Pattern:** Paragraph opens with a present-tense generalisation about the current state of a field or world ("Today's research on intelligence faces…", "The field is currently grappling with…").
**Why flagged:** Same family as "in recent years" — temporal scaffolding without commitment. Especially common as the opener of introductions.
**Suggested alternative:** Anchor with a citation or specific event; or drop and open with the claim the paragraph will defend.

### Topic-sentence-with-three-clauses
**Pattern:** Paragraph opens with a sentence whose predicate is a tricolon ("Intelligence is contextual, dynamic, and emergent"). The remainder of the paragraph addresses the three clauses in order.
**Why flagged:** Combines tricolon (sentence-level tell) with paragraph architecture (three-example tell). High-confidence LLM signature when present.
**Suggested alternative:** Choose the strongest of the three predicates and develop it; structure the paragraph around the development rather than the enumeration.

---

## Structural patterns — discourse level

### Hedging-without-substance
**Pattern:** "It is important to note that…", "It is worth considering that…", "One might argue that…" used to introduce claims the writer in fact endorses.
**Why flagged:** LLMs use these phrases as politeness scaffolding around assertions. The hedge does no epistemic work; it softens the assertion without qualifying it. Worse, it shifts agency away from the author ("one might argue") in places where the author is in fact arguing.
**Confidence:** High for "it is important to note that…" specifically; medium for the others.
**Suggested alternative:** Drop the preamble. State the claim. If the hedge is doing real work — flagging uncertainty, attributing a view to others — make that work explicit ("This is contested; X holds that…", "I am less confident here, but…").

### False balance / both-sides framing where no real balance exists
**Pattern:** "On one hand X, on the other hand Y" where Y is a strawman, or where the author plainly favours one side but the prose pretends to weigh them.
**Why flagged:** LLM trained behaviour toward apparent neutrality. In academic argument, a position the author favours should be argued for, with real engagement with the opposing view; faux balance reads as evasive.
**Suggested alternative:** State the position you hold. Engage the strongest version of the opposing view as a serious objection, not as a balanced alternative.

### Concession-then-reversal as default move
**Pattern:** "While [opposing view has merit], [opposing view ultimately fails because…]." Used as the dominant rhythm of an argument.
**Why flagged:** The concession-then-reversal is a legitimate move, but LLMs over-use it as a default rhythm for engaging any opposing view. The result is prose where every paragraph performs balanced acknowledgement before reaching the conclusion the writer always intended.
**Confidence:** Medium. Single uses are fine; flag when the rhythm dominates multiple paragraphs.
**Suggested alternative:** Vary: direct argument without concession; concession without reversal (where the opposing view has a real point you accept); reversal-then-concession (claim first, then qualify).

### Closing with "ultimately" or "in the end"
**Pattern:** Section, chapter, or paper closes with a paragraph beginning "Ultimately, …" or "In the end, …"
**Why flagged:** LLM default closer. Often signals that the closing move is a paraphrase of the opening rather than an extension of the argument.
**Suggested alternative:** Drop the marker; if the closing claim is genuinely the upshot, state it without the meta-flag. Better, replace the closer with a forward-looking move (see "Closing paragraphs that restate the opening" above).

### "Importantly," / "Crucially," as section-pivot
**Pattern:** A new paragraph or section begins with "Importantly, …" or "Crucially, …" as its sole connective tissue with what came before.
**Why flagged:** Tells the reader the next claim matters without arguing for why it follows. The pivot does no inferential work.
**Suggested alternative:** Make the connection explicit ("This bears on X because…"); or restructure so the importance is shown.

### Three-part section architecture (overview → development → restatement) at every level
**Pattern:** Every section, sub-section, and paragraph follows the same three-part shape: announce what will be argued, argue it, restate. Applied recursively at multiple scales.
**Why flagged:** Pedagogical scaffolding that LLMs apply to argumentative prose. Heavy at every level produces prose that feels exhaustively signposted but advances slowly.
**Suggested alternative:** Vary the architecture by level. At paragraph level, often skip the announce and restate steps. At section level, keep signposting but lean.

### Per-paragraph thesis restatement
**Pattern:** Every paragraph closes (or opens) with a restatement of the section's overall thesis, as though the reader might have forgotten.
**Why flagged:** LLM redundancy default. Genuine argumentative prose builds: each paragraph adds something the previous did not, and the relation to the thesis is carried by structure, not by repeated assertion.
**Suggested alternative:** State the thesis once, where it belongs. Let later paragraphs do new work and trust the reader to track the connection.

---

## Formatting tells

### Excessive headers / sub-headers in flowing argument
**Pattern:** A short section (one or two paragraphs) split into multiple `###` or `####` sub-headings; or every paragraph getting a bold lead-in label.
**Why flagged:** LLMs default to over-segmentation, producing the visual structure of a textbook or product page in contexts where continuous argument is expected. Academic prose tolerates dense un-headed sections.
**Confidence:** Medium. Flag when sub-section bodies are shorter than ~150 words, or when consecutive sub-headings carry no real partition of content.
**Suggested alternative:** Merge into continuous prose with transitions; reserve headers for genuine partitions of the argument.

### Bold-emphasis on every other sentence
**Pattern:** Frequent **bold** spans applied to key terms, phrases, or whole sentences throughout a paragraph or section.
**Why flagged:** LLMs apply bold as a reading aid in contexts where the prose should carry emphasis through structure. Pervasive bolding in academic prose reads as a slide deck rather than an argument.
**Confidence:** High when more than one bold span appears per paragraph and the bolded items are not technical terms being introduced.
**Suggested alternative:** Reserve bold for the first use of a technical term, or drop entirely and let sentence structure carry emphasis.

### Em-dash overuse
**Pattern:** Em-dashes used for parenthetical asides, mid-sentence qualification, or emphasis. In LLM prose they cluster: several per page, often more than one per paragraph.
**Why flagged:** Since 2023 the em-dash has become one of the strongest surface tells in generated text. Models reach for it whenever a clause needs attaching and no other construction has been chosen, so it marks the absence of a decision about sentence structure rather than a positive stylistic choice. Note that authors often *believe* the em-dash is characteristic of their own writing when measurement shows it is rare. Check the corpus rate before treating it as voice; a rate below roughly 1 per 1,000 words is rare, not signature.
**Confidence:** High in formal and scientific register, where the default posture is to flag every occurrence and let the author's style file relax it. Medium in informal register. An author's `## Manual overrides` is authoritative wherever it sets an explicit target.
**Suggested alternative:** Restructure. Split into two sentences, or convert the aside to parentheses where it is genuinely subordinate. **Never substitute a colon, semicolon, or a dash of another width.** That preserves the undecided structure and converts one tell into another (see the entry below).

### Colon and semicolon as sentence-avoidance
**Pattern:** A colon splicing an ordinary independent clause onto the one before it ("The result is clear: the model fails on long inputs"); a semicolon joining two clauses that would stand perfectly well as sentences; either mark appearing two or more times in a paragraph.
**Why flagged:** Models use mid-sentence punctuation to bolt clauses together instead of committing to a sentence boundary, producing prose that is locally fluent and structurally undecided. Each instance looks earned in isolation, so the tell is the rate rather than the individual mark. This is also the standard destination for a naively applied em-dash rule: strip the dashes and the same joins reappear as colons and semicolons, with the same structure underneath.
**Confidence:** High when a paragraph carries two or more colons, or when a colon's right-hand side is an ordinary clause rather than a genuine list or a definitional gloss. High when the semicolon rate rises sharply in a document written under an em-dash constraint, which indicates substitution rather than restructuring.
**Suggested alternative:** Split into separate sentences, or join with a plain connective that names the relation ("because", "so", "in which"). Keep the colon only where it introduces a real list or a definition the preceding clause sets up, and the semicolon only where a full stop would genuinely over-separate. Do not swap one mark for another.

### Inconsistent header capitalisation
**Pattern:** Title Case in one header, sentence case in the next, within the same document. Or capitalisation of minor words inconsistently across sibling headers.
**Why flagged:** A frequent artefact of LLM-generated outline structure, especially when generated in multiple turns. Human-edited documents tend to converge on a single convention.
**Suggested alternative:** Pick one convention (sentence case is the most common in current academic Markdown) and apply uniformly.

### Triple-hyphen `---` horizontal rules between subsections
**Pattern:** Frequent `---` horizontal rules separating short subsections within a section, without a structural reason for the separation.
**Why flagged:** LLM default for visual separation when the model is uncertain whether the next block continues the prior section. Real horizontal rules serve a structural purpose (separating top-level sections, marking a hard break in voice); decorative use is an AI-drift marker.
**Suggested alternative:** Remove decorative rules; rely on headers for structure. Keep horizontal rules only where they mark a genuine top-level boundary (e.g., between front matter and body).

### Emoji decoration in section headers or body
**Pattern:** Section headers prefixed with emoji (🔬, 📚, ✨, ⚡), or emoji peppered through body prose.
**Why flagged:** Strong AI register signal in academic writing. Almost never appears in author-voice scholarly prose.
**Suggested alternative:** Remove. If visual differentiation between sections is genuinely needed, use header levels.

### Trailing-summary boxes / blockquote pull-outs
**Pattern:** A blockquote or fenced block at the end of a section summarising the section ("> **Summary:** This section argued that…").
**Why flagged:** Documentation-page convention ported into academic prose by LLMs. Rare in research writing.
**Suggested alternative:** Drop. If the summary is genuinely needed, integrate it into the final paragraph of the section.
