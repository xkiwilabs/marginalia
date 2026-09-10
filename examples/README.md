# Example corpus

Drop your own published work here so `marginalia-extract-style` can learn your voice. Files in this directory are gitignored — they stay on your machine.

## Layout

- `papers/` — peer-reviewed journal articles, book chapters
- `grants/` — funded grant proposals (full text, not summaries)
- `other/` — anything else you write in (essays, op-eds, letters)

## Format

Supported: `.md`, `.markdown`, `.txt`, `.pdf`, `.docx`, `.doc`, `.rtf`, `.odt`.

Non-Markdown formats are auto-converted to a sibling `.md` the first time `marginalia-extract-style` runs. The conversion is cached (re-runs skip it if the source hasn't changed), and you can hand-edit the resulting `.md` to refine the corpus — your edits survive subsequent runs as long as the `.md` is newer than the source.

Requirements:
- `pandoc` on `PATH` — for `.docx`, `.doc`, `.rtf`, `.odt`. Install: `brew install pandoc` (macOS) or via your package manager.
- `pdftotext` on `PATH` — for `.pdf`. Install: `brew install poppler` (macOS) or `apt install poppler-utils` (Debian/Ubuntu).

See `content/input-ingestion.md` for the full conversion procedure and caveats (figures, multi-column PDFs, scanned PDFs requiring OCR, track-changes, etc.).

## How many examples do I need?

- 3+ per genre gives a confident style profile.
- 1–2 works but the resulting style file is marked low-confidence; the review skill leans more on the cross-genre `base.md`.
- 0 examples for a genre is fine — the review skill falls back to `base.md` alone.
