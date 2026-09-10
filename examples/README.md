# Your corpus (alternative location)

This folder can hold your own published writing, the work marginalia learns your
voice from.

**Most people should not use this folder.** The recommended location is
`~/.marginalia/examples/`, outside the project, so your writing can never be
caught up in anything you later share or publish. The main README walks through
setting that up.

This folder exists for two cases: you are trying marginalia out and would rather
not create anything in your home directory yet, or you deliberately keep the tool
and your corpus together. Either is fine. marginalia looks in
`~/.marginalia/examples/` first and falls back to here.

Anything you put in `papers/`, `grants/` or `other/` is ignored by git and will
not be uploaded if you push changes. That protection lives in `.gitignore`. If
you move things around, check it still holds.

## Layout

- `papers/` — journal articles, book chapters
- `grants/` — funded proposals, full text rather than summaries
- `other/` — anything else you write: essays, reports, talks

You can add more folders. Any name you use becomes a genre you can pass to
`--genre`.

## What to put here

Published or funded work only, or writing you did entirely yourself and are happy
with. Not drafts, and nothing written with AI help.

marginalia learns to imitate whatever it finds here, so an AI-assisted draft
teaches it the drift as though it were your voice, and it will then defend that
drift in every future review.

Three or more per folder gives a solid profile. One or two works but is marked
low-confidence. An empty folder is fine.

## File formats

Supported: `.md`, `.markdown`, `.txt`, `.pdf`, `.docx`, `.doc`, `.rtf`, `.odt`.

Anything that is not already Markdown is converted automatically the first time
you run `extract-style`, producing a `.md` alongside the original. The conversion
is cached, so later runs skip it, and you can hand-edit the `.md` to clean it up.
Your edits survive as long as the `.md` stays newer than the source.

Conversion needs two tools, and only for the formats you actually use:

- **`pandoc`** for `.docx`, `.doc`, `.rtf`, `.odt`. Install with `brew install pandoc`, or your package manager.
- **`pdftotext`** for `.pdf`. Install with `brew install poppler`, or `apt install poppler-utils`.

Conversion is imperfect. Figures, complex tables and multi-column PDF layouts
come through badly, and a scanned PDF produces nothing at all until you run OCR
on it (`ocrmypdf` works well). The profile is only as good as the text it sees,
so it is worth opening one converted file to check it is readable.

See `content/input-ingestion.md` for the full procedure and caveats.
