# Expected detections for `citations-sample.md`

The verify-cites skill MUST flag at least the issues below. It may flag others (e.g., Tier 4 better-source advisories on the real cites); additional flags are acceptable. The four planted issues plus the orphan are documented in an HTML comment at the top of the fixture and constitute the ground truth.

**Fixture revised 2026-08-11.** Four of the five in-text cites are now real, Crossref-indexed works (verified by DOI). Previously all five carried fictional metadata, so Tier 1 failed for every cite and the cascade never reached Tier 3 — which meant the planted claim–source mismatch, the single hardest thing this fixture is meant to test, was unreachable. **A run in which Tier 3 does not execute is a failed run**, not a passing one.

## Must catch (critical)
- `(Wexler, 2024)` — hallucinated work; no match in Crossref / Google Scholar / Semantic Scholar. Tier 1 fail. Type: `citation-hallucinated`.
- `(Flavell, 1980)` — year mismatch with bibliography entry (bibliography lists 1979, in-text reads 1980). Tier 1 fail. Type: `citation-year-mismatch`.

## Must catch (medium)
- Orphan reference in bibliography: `Huys, Q. J. M., Maia, T. V., & Frank, M. J. (2016). Computational psychiatry as a bridge from neuroscience to clinical applications.` has no matching in-text citation. Phase A bibliography-hygiene check. Type: `bibliography-orphan`.
- Claim–source mismatch on `(Rouault et al., 2018)`: the sentence claims metacognitive monitoring is "uniformly impaired across major psychiatric and neurodevelopmental conditions". The source does not support this. Rouault et al. report metacognitive shifts associated with **transdiagnostic symptom dimensions in a general-population sample**, explicitly dissociated from task performance; they do not test clinical diagnostic categories, and they do not test neurodevelopmental conditions at all. Tier 3. Type: `claim-source-mismatch`. The `source_quote` should draw on the title's own qualifier ("but Not Task Performance") or the abstract's symptom-dimension framing.

## Must reach Tier 3
The four real cites must pass Tier 1 (all are Crossref-indexed and the bibliography metadata matches, apart from the deliberate Flavell year error). If Tier 1 fails for Fleming & Lau, Rouault et al., or Weil et al., that is a **false hallucination** and a regression — check tool budget and query construction rather than adjusting the fixture. Known limitation #2 in `CLAUDE.md` describes this failure mode.

DOIs for verification:

| cite | DOI |
|---|---|
| Flavell 1979 | `10.1037/0003-066x.34.10.906` |
| Fleming & Lau 2014 | `10.3389/fnhum.2014.00443` |
| Rouault et al. 2018 | `10.1016/j.biopsych.2017.12.017` |
| Weil et al. 2013 | `10.1016/j.concog.2013.01.004` |
| Huys et al. 2016 (orphan) | `10.1038/nn.4238` |

## Should NOT flag
- `Fleming and Lau (2014)` — the prose claim (distinguishing metacognitive sensitivity from response bias, and the two being conflated by naive confidence measures) is an accurate characterization of the source. A Tier 3 flag here is a false positive.
- `(Weil et al., 2013)` — the prose claim (metacognitive ability improves with age in adolescence, independently of task performance) matches the source. A Tier 3 flag here is a false positive.

## May catch (advisory)
- Better-source / recency suggestions for any of the real cites. Tier 4 advisories are not required.
- Tier 2 reputability flags are not expected — *American Psychologist*, *Frontiers in Human Neuroscience*, *Biological Psychiatry*, *Consciousness and Cognition* and *Nature Neuroscience* are all reputable peer-reviewed venues.

## JSON shape
Same base schema as the review skill — `id`, `priority`, `type`, `location`, `current`, `proposed`, `confidence`, `auto_applicable`, `rationale` — plus citation-specific fields per `content/citation-tiers.md`:
- `citation_key` (e.g., `"Wexler-2024"`)
- `tier` (1 | 2 | 3 | 4)
- `doi` (when found; null when not)
- `source_quote` (for Tier 3 mismatches: the passage from the source that contradicts or fails to support the in-text claim)

`auto_applicable: true` for the Flavell year correction (mechanical bibliography fix); `auto_applicable: false` for the Wexler hallucination, the Rouault et al. claim–source mismatch, and the Huys et al. orphan (all require author judgment).

## Issue-count expectation
At minimum 4 flagged issues (2 critical, 2 medium). Five in-text citations should be enumerated in the Phase A inventory; one bibliography entry (Huys et al.) should appear in the orphan list. Two cites (Fleming & Lau, Weil et al.) should pass all tiers cleanly.
