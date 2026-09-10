<!--
planted issues:
  1. Flavell — in-text reads (Flavell, 1980); bibliography entry below has year 1979 (year mismatch)
  2. Wexler — (Wexler, 2024) is a hallucinated work; bibliography entry exists but the paper does not (fabricated title "The arithmetic of distributed cognition", fabricated venue "Journal of Computational Mind")
  3. Orphan reference: bibliography contains "Huys, Q. J. M., Maia, T. V., & Frank, M. J. (2016). Computational psychiatry..." with no matching in-text citation
  4. Claim–source mismatch: the sentence introducing (Rouault et al., 2018) attributes a sweeping general claim ("metacognitive monitoring is uniformly impaired across major psychiatric and neurodevelopmental conditions") that the actual source does not support. Rouault et al. report metacognitive shifts associated with *transdiagnostic symptom dimensions* in a general-population sample, explicitly dissociated from task performance, and do not test clinical diagnostic categories or neurodevelopmental conditions at all. The paper's own title contains the contradicting qualifier ("but Not Task Performance").

Exactly five distinct in-text citations are planted (in the order they appear):
  - (Flavell, 1980)
  - Fleming and Lau (2014)
  - (Rouault et al., 2018)
  - (Weil et al., 2013)
  - (Wexler, 2024)

IMPORTANT — fixture design note (2026-08-11):
Four of the five cites are REAL, Crossref-indexed works, verified by DOI at the
time of writing. This is deliberate and load-bearing. The previous version of this
fixture used plausible-but-fictional metadata for the four cites that are meant to
PASS, which made Tier 1 fail for every one of them. Because the tier cascade stops
at a Tier 1 failure, the planted Tier-3 claim–source mismatch was masked and could
never be exercised. With real cites, Tier 1 passes, the cascade proceeds, and
issue 4 above becomes testable — which is the whole point of the fixture.

Only Wexler (2024) is fictional, and that is the intended hallucination test.

Real works used (DOIs for verification):
  Flavell 1979    10.1037/0003-066x.34.10.906
  Fleming & Lau   10.3389/fnhum.2014.00443
  Rouault 2018    10.1016/j.biopsych.2017.12.017
  Weil 2013       10.1016/j.concog.2013.01.004
  Huys 2016       10.1038/nn.4238            (orphan — bibliography only)
-->

# Metacognition in reasoning systems

Metacognitive monitoring, the ongoing evaluation of whether one's current reasoning is on track, has long been treated as a hallmark of mature human cognition (Flavell, 1980). The clearest evidence comes from confidence-calibration paradigms in which participants both produce a response and rate their certainty in it. Fleming and Lau (2014) set out the measurement problem directly, distinguishing metacognitive sensitivity from response bias and showing that the two are easily conflated by naive confidence measures.

Recent work has tried to generalize this picture. Metacognitive monitoring is uniformly impaired across major psychiatric and neurodevelopmental conditions, an effect taken to support a domain-general account of metacognition (Rouault et al., 2018). In adolescent samples, metacognitive ability improves with age independently of task performance, suggesting a developmental trajectory specific to the monitoring process itself (Weil et al., 2013).

Whether these findings extend to artificial reasoning systems is less clear. One formal argument holds that any system whose intermediate representations are inaccessible to the system itself cannot in principle meet the conditions for metacognitive monitoring (Wexler, 2024), a result with sharp implications for large language models, which lack privileged read access to their own activations.

Taken together, the literature suggests that metacognition is best treated as a graded property of reasoning processes rather than as a discrete capacity.

## References

Flavell, J. H. (1979). Metacognition and cognitive monitoring: A new area of cognitive-developmental inquiry. *American Psychologist*, 34(10), 906–911.

Fleming, S. M., & Lau, H. C. (2014). How to measure metacognition. *Frontiers in Human Neuroscience*, 8, 443.

Huys, Q. J. M., Maia, T. V., & Frank, M. J. (2016). Computational psychiatry as a bridge from neuroscience to clinical applications. *Nature Neuroscience*, 19(3), 404–413.

Rouault, M., Seow, T., Gillan, C. M., & Fleming, S. M. (2018). Psychiatric symptom dimensions are associated with dissociable shifts in metacognition but not task performance. *Biological Psychiatry*, 84(6), 443–451.

Weil, L. G., Fleming, S. M., Dumontheil, I., Kilford, E. J., Weil, R. S., Rees, G., Dolan, R. J., & Blakemore, S.-J. (2013). The development of metacognitive ability in adolescence. *Consciousness and Cognition*, 22(1), 264–271.

Wexler, D. (2024). The arithmetic of distributed cognition. *Journal of Computational Mind*, 12(4), 488–510.
