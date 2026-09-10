# Input ingestion

marginalia's protocols (`review-protocol.md`, `citation-tiers.md`, `extraction-protocol.md`) operate on Markdown. This file describes how non-Markdown inputs are converted to Markdown before any protocol consumes them.

The procedure is the same whether the caller is a single-file path (review, cite) or a directory listing (extract-style): each non-Markdown file is converted in place to a sibling `.md`, and the rest of the protocol reads that `.md`.

---

## Section 1: Supported formats

| Extension | Converter | Notes |
|---|---|---|
| `.md`, `.markdown` | none | Use the file directly, no conversion. |
| `.txt` | none | Treated as Markdown (no headers, single paragraph blocks). |
| `.tex`, `.latex` | none — **markup-native** | Read in place. Do NOT convert. See Section 6. |
| `.mdx` | none — **markup-native** | Read in place. Do NOT convert. See Section 6. |
| `.pdf` | `pdftotext` | Layout-preserving plain-text extract from poppler. |
| `.docx`, `.doc` | `pandoc` | Word documents. |
| `.rtf` | `pandoc` | |
| `.odt` | `pandoc` | OpenDocument. |
| anything else | — | Error: `Unsupported input format: <ext>. Convert to one of: md, txt, pdf, docx, doc, rtf, odt.` |

The format is determined by extension, case-insensitively. Files with no extension are treated as `.txt`.

---

## Section 2: Procedure for one file

Given an input path `<src>`:

1. **Resolve the target Markdown path.** Let `<dst>` be `<src>` with its extension replaced by `.md`. If `<src>` already ends in `.md` or `.markdown`, set `<dst> = <src>` and return — no conversion needed.

2. **Check cache.** If `<dst>` exists and its mtime is greater than `<src>`'s mtime, return `<dst>` — cached conversion is up-to-date. (Delete `<dst>` manually to force re-conversion.)

3. **Check name collision.** If `<dst>` exists but is older than `<src>`, log a warning (`stale converted file detected; regenerating`) and proceed to overwrite. If `<dst>` exists and the user has a separate `<src>` (e.g., both `paper.pdf` and `paper.md` were dropped in by hand and `paper.md` is newer than `paper.pdf`), step 2 returns the user's hand-written `paper.md` — this is the correct behaviour.

4. **Convert.** Shell out per the table above:
   - `pdf` → `pdftotext -layout "<src>" "<dst>"`
   - `docx`/`doc` → `pandoc -f docx -t gfm-raw_html --wrap=preserve "<src>" -o "<dst>"` (use `-f doc` for `.doc`)
   - `rtf` → `pandoc -f rtf -t gfm-raw_html --wrap=preserve "<src>" -o "<dst>"`
   - `odt` → `pandoc -f odt -t gfm-raw_html --wrap=preserve "<src>" -o "<dst>"`

5. **Validate.**
   - If the converter exits non-zero, propagate its stderr in the error and stop. Do not write a partial `<dst>`.
   - If the converter exits zero but `<dst>` is empty or contains only whitespace, error: `<converter> produced empty output for <src> — file may be image-only (needs OCR) or corrupted.` Delete the empty `<dst>` before stopping.
   - If `<dst>` has no `#` header within its first 50 lines, prepend `# <basename without ext>\n\n` so downstream anchor resolution and section-header passes have something to work with. This is mainly a PDF concern; `pdftotext` does not synthesise structure.

6. **Return** `<dst>`. The caller proceeds with this path as if the user had passed it.

---

## Section 3: Procedure for a directory listing (extract-style)

Given a directory `<dir>` (e.g., `examples/papers/`):

1. List every file in `<dir>` whose extension is in the supported set (Section 1) and is not excluded by the caller's rules (e.g., `_*` prefix, `README.md`, `.gitkeep`).
2. For each non-Markdown file, apply Section 2 to obtain its sibling `.md`. Errors from any single file are non-fatal here: skip that file with a note `<src>: conversion failed (<reason>) — skipped` and proceed with the rest.
3. The caller now has a list of `.md` paths to process.

The sibling `.md` files persist in `<dir>` between runs and serve as the canonical text representation of each corpus entry. They are within `examples/` and therefore gitignored by default; the user may commit them or further edit them to refine the corpus.

---

## Section 4: Tool availability

Before conversion, check that the required tool is on `PATH`:

- `pdftotext --help` for PDF.
- `pandoc --version` for docx/doc/rtf/odt.

If a required tool is missing, error with:

```
<tool> is not installed. Install with:
  macOS:  brew install <pkg>
  Linux:  apt install <pkg>  (or your package manager's equivalent)
```

Mapping:
- `pdftotext` → `poppler` (macOS) / `poppler-utils` (Debian/Ubuntu)
- `pandoc` → `pandoc`

Do not fall back silently to a less-capable converter. If the user's intended path can't run, they need to know.

---

## Section 5: Conversion caveats (record these in the protocol's report header)

- **PDF (`pdftotext`):** Preserves reading order and approximate layout but discards figures, complex tables, and multi-column reconstruction can introduce paragraph splits. Citations embedded in figure captions or tables may be lost. Scan-only PDFs (image-based, no text layer) produce empty output — the user must OCR first (`ocrmypdf` is a reasonable choice).
- **Word (`pandoc`):** Track-changes and comments are dropped silently. Footnotes are converted to GFM-style footnotes. Math from Word's equation editor is preserved as raw HTML or MathML and treated by the review protocol as an opaque block (skipped).
- **All converters:** The converted `.md` is a best-effort representation. If a protocol's output is suspicious near a converted boundary (e.g., spurious paragraph breaks, broken hyphenation across lines), check the converted `.md` against the original. Hand-editing the `.md` is supported; cached conversion will not overwrite a newer `.md`.

Each protocol that calls into this file should record in its report header:

- `input_format: <ext>`
- `input_converted: true|false`
- `converter: <tool> | none`
- `converter_caveats_apply: true|false` — true for `.pdf` and `.docx`; false otherwise.

---

## Section 6: Markup-native formats (`.tex`, `.mdx`)

These are **not converted**. Every other supported format is a read-only source
that happens to contain prose, so a sibling `.md` is harmless. LaTeX and MDX are
different: they are the file the author actually edits. Converting them would
break line-number fidelity and leave `marginalia apply` writing into a derived
file the author does not use. So protocols read them in place and skip the
markup.

`tools/prose_metrics.py` implements exactly the extraction described here, so
Dimension E and the prose sweep see the same text. Prefer it over re-deriving the
stripping by hand.

### What counts as prose

**LaTeX.** Consider only material between `\begin{document}` and
`\end{document}`. Skip entirely:

- The preamble, and `%` comments (but not escaped `\%`).
- Math: `$…$`, `$$…$$`, `\[…\]`, and the `equation`, `align`, `eqnarray`,
  `matrix` environments. Math is opaque; never flag inside it.
- Float and verbatim environments: `figure`, `table`, `tabular`, `lstlisting`,
  `verbatim`, `algorithm`, `tikzpicture`.
- Sectioning commands (`\section{…}` and friends) — these are headings, and the
  prose sweep ignores headings as it does in Markdown.

Handle specially:

- `\cite{…}`, `\parencite`, `\autocite`, `\textcite` become a single opaque token.
  A bare `\cite{key}` left in place splits sentences at the braces and corrupts
  every sentence-length measurement. The same applies to `\ref`/`\eqref`/`\label`.
- Text-bearing commands keep their argument: `\textbf{x}`, `\emph{x}`,
  `\texttt{x}`, `\textsc{x}` → `x`. Otherwise a bolded clause vanishes from the
  sweep.
- `\footnote{…}` is prose. Treat it as a parenthetical of the sentence it hangs
  off, not as a separate paragraph.
- `~` is a space. `\\` is a line break, not a sentence boundary.

**MDX.** Strip YAML frontmatter, `import`/`export` lines, `{/* … */}` comments,
and all JSX/HTML tags, keeping the text between them. Fenced and inline code is
skipped as in Markdown. A `<Component>` wrapping prose contributes its prose;
a self-closing `<Component />` contributes nothing.

### Citation verification in LaTeX

`citation-tiers.md` expects `(Author, Year)` parentheticals. In LaTeX the cite is
a `\cite{key}` against a `.bib` file, so:

1. Collect keys from every `\cite`-family command.
2. Resolve each key in the `.bib` file (`\bibliography{…}`/`\addbibresource{…}`,
   else the nearest `.bib` beside the target). Its fields are the citation
   metadata — do not re-derive them from the prose.
3. An unresolvable key is `bibliography-orphan` and needs no network lookup.
4. A `.bib` entry never cited is reported as unused, not as an error.

### Report header

Record `input_format: tex|mdx`, `input_converted: false`, `converter: none`,
`converter_caveats_apply: false`, and additionally `markup_native: true` so the
reader knows line numbers refer to the original source.

### Known limits

- Macros the author defines themselves (`\newcommand`) are dropped along with
  their arguments rather than expanded. A macro wrapping prose hides that prose
  from review. Flag this in the report when `\newcommand` definitions carrying
  text arguments are present.
- Multi-file LaTeX (`\input{…}`, `\include{…}`) is **not** followed. Review the
  included files as separate targets.
