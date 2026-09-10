---
name: marginalia-write
description: Use when the user asks for help drafting, revising, polishing, or rewriting academic prose — papers, grants, essays, abstracts, paragraphs, sections. Loads the author's learned voice profile (base.md plus the genre overlay) and applies it as a generation constraint so the output sounds like the author rather than generic AI. Co-writer aid, not a post-write critic — engages before prose is produced, not after.
---

# marginalia-write

Draft or revise academic prose in the author's own voice, using the style profile derived from their published corpus.

## When to use this skill

Invoke when the user asks for help with:

- **Drafting prose from scratch** — executive summaries, abstracts, introductions, paragraphs, sections, donor-intent statements, project descriptions, significance claims.
- **Revising existing prose** to read more like them — "tighten this paragraph", "rewrite this section in my voice", "make this less AI-sounding".
- **Polishing or rewriting** — line-edits, sharper phrasing, cutting word count while keeping the argument.
- **Short-form academic content** — titles, captions, section headers, abstract sentences, bullet items inside grant deliverable lists.

This skill triggers on description match: phrases like "draft", "revise", "rewrite", "polish", "tighten", "compose", "write this paragraph" in the context of academic prose should engage it.

## Do NOT use this skill for

- **Reviewing prose already written** — use `marginalia-review` instead. That's the critic; this is the co-writer.
- **Verifying citations** — use `marginalia-verify-cites`.
- **Code, configs, technical documentation** — the voice profile is for prose, not for software artefacts.
- **Email drafts** unless the user explicitly invokes — email register differs.
- **Drafts where the user has asked for a non-personal voice** ("write this in Hemingway's voice", "make it more casual").

## How to invoke

The skill engages implicitly — by description match — when the user asks for writing help. It can also be invoked explicitly via `/marginalia write [task]` (which the `/marginalia` command routes here).

## Protocol

0. Read `content/paths.md` and resolve `<STYLES_DIR>` and `<CORPUS_DIR>`. Every `content/styles/…` and `examples/…` path below is a name, not a location.
1. Read `content/write-protocol.md` from the marginalia repo (lives in the same repo as this skill).
2. Auto-detect the target genre from the working directory and request context per protocol §1.
3. Read `content/styles/base.md` and `content/styles/{genre}.md` if they exist; note in the response header which were loaded.
4. Apply both files as **positive constraints** (preferred lexicon, sentence rhythm, paragraph architecture, argumentative moves) and **negative constraints** (the corpus-derived avoid list) during prose generation.
5. Produce the prose with a one-line header and (for paragraph-length or longer outputs) a post-write offer to run `/marginalia review` for a formal voice check.

## Locating the marginalia repo

The repo root is the directory containing `content/`, `claude-code/` and `tools/`. From within Claude Code, find it by walking up from the symlinked SKILL.md to its actual location: if the symlink resolves to `<repo>/claude-code/skills/marginalia-write/SKILL.md`, the repo root is `<repo>`.

When invoked from any Claude Code session — regardless of the user's current working directory — the skill resolves the symlink to find the style files. The user can be in a grant-proposal workspace, a paper-drafting workspace, or any other directory.

## Output expectations

After applying the voice profile, deliver:

- **One-line header** noting the style files in use:
  - Drafting: `*Drafting in your voice — base.md + {genre}.md.*`
  - Revision: `*Revising in your voice — {genre} register.*`
  - Overlay missing: `*Drafting in your voice — base.md only ({genre}.md not yet extracted).*`
- **The prose itself.** Ready to copy-paste. No surrounding quotation marks unless the prose is a list or code-adjacent.
- **Optional one-line note** if a constraint was hard to honour or a content-level concern surfaced.
- **For paragraph+ outputs:** an offer to run `/marginalia review` for a formal voice check, and (if the prose carries citations) a note that `/marginalia cite` will verify them.

Skip the post-write offers for sub-paragraph outputs (single sentences, phrases, titles).

Do NOT modify files in-place. The default deliverable is the chat artefact; ask the user before writing to disk.

## Edge cases

- **No style files yet.** Error with `No style profile available. Run /marginalia extract-style --genre=all first.` Stop.
- **Ambiguous genre.** If cwd hints don't resolve, ask once: `Paper register or grant register?`
- **User explicitly overrides genre.** "Write this for a paper" → load `papers.md` regardless of cwd.
- **User asks for explicit AI-drift inclusion** (contrast prose, parody, demo). Honour the request and note that voice constraints are being intentionally suspended for this turn.

See `content/write-protocol.md` for the full protocol, including genre auto-detection rules, constraint application detail, and additional edge cases.
