# Expected detections for `ai-drift-sample.md`

The review skill MUST flag at least the following issues. It may flag others; additional flags are acceptable as long as the items below are all caught.

## Must catch
- ¶1: tricolon ("contextual, dynamic, and emergent")
- ¶1: AI-drift verb "delve"
- ¶2: opener "In recent years,"
- ¶2: AI-drift adjective "crucial"
- ¶2: AI-drift adjective "robust"
- ¶3: bullet list inside argumentative prose (three bullets summarizing the preceding paragraph where continuous prose would be expected)

## Severity expected
- Tricolon, lexicon swaps ("delve", "crucial", "robust"): medium priority
- "In recent years" opener: high priority (structural)
- Bullet-list inside argument: high priority (structural)

## JSON shape expected
Each issue has: `id`, `priority`, `type`, `location.{line_start,line_end}`, `current`, `proposed` (may be `null` for structural issues), `confidence`, `auto_applicable`, `rationale`.

Type values expected for this fixture:
- `ai-drift-tricolon`
- `ai-drift-verb` (for "delve")
- `ai-drift-adjective` (for "crucial" and "robust")
- `ai-drift-opener-in-recent-years`
- `ai-drift-bullets-in-argument`

`auto_applicable: true` for the lexicon swaps and tricolon rewrite; `auto_applicable: false` for the opener and bullet-list issues (these require author intervention to restructure).
