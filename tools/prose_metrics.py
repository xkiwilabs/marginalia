#!/usr/bin/env python3
"""
prose_metrics.py — deterministic surface measurement for marginalia review.

Why this exists
---------------
`content/styles/base.md` carries hand-written rules of the form "flag any
paragraph with two or more colons" and "more than a handful of either mark per
page". Those are counting rules, and a language model executing a prose protocol
under-counts them: the 2026-08-06 override in base.md is annotated
"reinforces the 2026-06-14 colon/semicolon override after two review passes
under-caught it".

So this tool counts. It does NOT judge. It locates every candidate with an exact
line number and reports the rates; `marginalia-review` Dimension E decides which
candidates are earned and which are drift. Deterministic counting plus model
judgement, rather than the model doing both.

Usage
-----
    python3 tools/prose_metrics.py TARGET [--genre papers] [--json]
    python3 tools/prose_metrics.py --corpus 'papers=<corpus>/papers/*.md' --emit-baseline

Supports .md, .mdx, .tex, .txt. Reads optional baselines from
<styles>/baselines.json (written by --emit-baseline); <styles> resolves per
content/paths.md: $MARGINALIA_HOME, then ~/.marginalia/, then the repo.
"""
from __future__ import annotations
import argparse, glob, json, os, re, statistics, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Vendored / generated trees whose docs are not the author's writing.
VENDOR_DIRS = {".venv", "venv", "node_modules", ".git", "site-packages",
               ".pytest_cache", "__pycache__", "dist", "build", ".tox", "vendor"}


def resolve_styles_dir() -> Path:
    """Locate the user's style profiles. Mirrors content/paths.md exactly.

    Order: $MARGINALIA_HOME, then ~/.marginalia/, then the repo itself. The
    profiles hold verbatim passages of their author's writing, so they are kept
    outside the checkout wherever possible; the in-repo location is the original
    layout and stays supported so existing installs keep working.
    """
    env = os.environ.get("MARGINALIA_HOME")
    if env:
        # An explicit override wins even when empty. A user who sets it means it.
        return Path(env).expanduser() / "styles"
    home = Path.home() / ".marginalia"
    if home.is_dir():
        return home / "styles"
    return REPO / "content" / "styles"


def resolve_corpus_dir() -> Path:
    """Locate the user's corpus. Same order as resolve_styles_dir()."""
    env = os.environ.get("MARGINALIA_HOME")
    if env:
        return Path(env).expanduser() / "examples"
    home = Path.home() / ".marginalia"
    if home.is_dir():
        return home / "examples"
    return REPO / "examples"


STYLES_DIR = resolve_styles_dir()
CORPUS_DIR = resolve_corpus_dir()
BASELINE_PATH = STYLES_DIR / "baselines.json"

# ---------------------------------------------------------------- extraction

ITEM = "\u27e6ITEM\u27e7"   # sentinel marking a list item, resolved in extract_prose


def _strip_braced(text: str, commands) -> str:
    """Remove \\cmd{...} with brace matching, so nested braces don't leave residue.

    A regex with [^{}]* fails on \\keywords{\\textbf{Keywords}: a; b; c} and leaves
    the argument behind, which then reads as prose full of semicolons.
    """
    for cmd in commands:
        while True:
            m = re.search(rf'\\{cmd}\s*\*?\s*(\[[^\]]*\])?\s*\{{', text)
            if not m:
                break
            i, depth = m.end(), 1
            while i < len(text) and depth:
                if text[i] == '{' and text[i - 1] != '\\':
                    depth += 1
                elif text[i] == '}' and text[i - 1] != '\\':
                    depth -= 1
                i += 1
            text = text[:m.start()] + ' ' + text[i:]
    return text


TEX_REF_HEAD = re.compile(
    r'\\(?:section|subsection|chapter)\*?\s*\{\s*'
    r'(?:references|bibliography|works cited|literature cited)\s*\}'
    r'|\\begin\{thebibliography\}|\\bibliography\s*\{|\\printbibliography',
    re.I)


def _strip_latex(text: str) -> str:
    if "\\begin{document}" in text:
        text = text.split("\\begin{document}", 1)[1]
    text = text.split("\\end{document}")[0]
    # Metadata commands whose arguments are not prose. Brace-matched: these
    # routinely nest (\keywords{\textbf{Keywords}: …}).
    text = _strip_braced(text, ["keywords", "thanks", "affiliation", "affil",
                                "author", "date", "titlenote", "acks"])
    text = re.sub(r'(?<!\\)%.*$', '', text, flags=re.M)                 # comments
    # Drop the reference list. extract_prose already truncates at a Markdown
    # `# References` heading, but it runs AFTER this function, by which point the
    # heading-dropping rule below has deleted `\section*{References}` and left the
    # entries behind as ordinary prose. A hand-formatted bibliography is dense in
    # exactly the marks Dimension E counts — page ranges (20(2):243–255), `arXiv:`
    # and `doi:` prefixes, and colon-bearing article subtitles — so those entries
    # land in the colon and semicolon rates as if they were sentence-avoidance.
    # Measured on a 22-reference IEEE-style paper: 44 of 58 colons came from the
    # bibliography, which was enough to raise a spurious HIGH punctuation finding.
    m = TEX_REF_HEAD.search(text)
    if m:
        text = text[:m.start()]
    for env in ("equation", "align", "eqnarray", "figure", "table", "tabular",
                "lstlisting", "verbatim", "algorithm", "tikzpicture", "matrix"):
        text = re.sub(rf'\\begin\{{{env}\*?\}}.*?\\end\{{{env}\*?\}}', ' ', text, flags=re.S)
    text = re.sub(r'\$\$.*?\$\$', ' MATH ', text, flags=re.S)
    text = re.sub(r'\\\[.*?\\\]', ' MATH ', text, flags=re.S)
    text = re.sub(r'(?<!\\)\$[^$]{0,400}?(?<!\\)\$', ' MATH ', text)
    # citations/refs become opaque tokens so they never split a sentence
    text = re.sub(r'\\(?:cite[a-zA-Z]*|autocite|parencite|textcite)\s*(?:\[[^\]]*\])*\s*\{[^}]*\}',
                  ' (CITE) ', text)
    text = re.sub(r'\\(?:ref|autoref|eqref|cref|Cref|pageref|label)\s*\{[^}]*\}', ' REF ', text)
    text = re.sub(r'\\(?:section|subsection|subsubsection|chapter|title|caption)\*?\s*\{[^}]*\}',
                  '\n', text)                                            # headings: drop
    text = re.sub(r'\\(?:textbf|textit|emph|texttt|textsc|underline|mbox|text)\s*\{([^{}]*)\}',
                  r'\1', text)                                           # keep the words
    text = re.sub(r'\\footnote\s*\{([^{}]*)\}', r' (\1) ', text)
    text = re.sub(r'\\begin\{[^}]*\}(\[[^\]]*\])?', ' ', text)
    text = re.sub(r'\\end\{[^}]*\}', ' ', text)
    text = re.sub(r'\\item\s*(\[[^\]]*\])?', ' ' + ITEM + ' ', text)
    text = re.sub(r'\\[a-zA-Z@]+\s*(\[[^\]]*\])?(\{[^{}]*\})?', ' ', text)  # residual commands
    text = re.sub(r'\\\\(\[[^\]]*\])?', ' ', text)      # line break, not a sentence boundary
    # LaTeX writes an em-dash as `---` and an en-dash as `--`. Counting only the
    # Unicode character reports zero em-dashes for every .tex file, which is a
    # silent false negative on the rule the author cares most about. Order matters:
    # the three-hyphen form must be replaced before the two-hyphen form. This is
    # LaTeX-only — in Markdown `---` is a horizontal rule, not a dash.
    text = text.replace("---", "—").replace("--", "–")
    # Stray braces from raw grouping ({\footnotesize … \par}). Left in place they
    # prefix the line and defeat the structural-label anchors below.
    text = text.replace("{", " ").replace("}", " ")
    return text.replace("~", " ").replace("\\%", "%").replace("\\&", "&")


def _strip_mdx(text: str) -> str:
    text = re.sub(r'\A---\n.*?\n---\n', '', text, flags=re.S)            # frontmatter
    text = re.sub(r'^\s*(?:import|export)\s+.*$', '', text, flags=re.M)
    text = re.sub(r'\{/\*.*?\*/\}', ' ', text, flags=re.S)
    text = re.sub(r'<[A-Za-z][^>]*/>', ' ', text)                        # self-closing JSX
    text = re.sub(r'</?[A-Za-z][^>]*>', ' ', text)                       # JSX/HTML tags
    return text


def _strip_markdownish(text: str) -> str:
    text = re.sub(r'```.*?```', ' ', text, flags=re.S)
    text = re.sub(r'`[^`\n]*`', ' ', text)
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', text)
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    return re.sub(r'\*\*|__|(?<!\*)\*(?!\*)', '', text)


REF_HEAD = re.compile(r'^\s*#{0,6}\s*(references|bibliography|works cited|literature cited)\s*$',
                      re.I | re.M)
BULLET = re.compile(r'^\s*([-*+•]|\d+[.)]\s|\([a-z0-9ivx]+\)\s)')


def extract_prose(path: Path):
    """Return [(orig_lineno, text)] of prose-bearing lines, format-aware."""
    raw = path.read_text(encoding="utf-8", errors="ignore")
    suffix = path.suffix.lower()
    if suffix == ".tex":
        body = _strip_latex(raw)
    elif suffix in (".mdx", ".jsx"):
        body = _strip_markdownish(_strip_mdx(raw))
    else:
        body = _strip_markdownish(raw)
    m = REF_HEAD.search(body)
    if m:
        body = body[:m.start()]
    # Map back to original line numbers where the line survives verbatim.
    orig = raw.split("\n")
    index: dict[str, int] = {}
    for i, ln in enumerate(orig, 1):
        s = ln.strip()
        if len(s) > 20:
            index.setdefault(s, i)
    out = []
    for approx, ln in enumerate(body.split("\n"), 1):
        s = ln.strip()
        if not s:
            out.append((None, ""))
            continue
        if re.match(r'^#{1,6}\s', s) or s.startswith("|"):
            continue
        digits = sum(c.isdigit() for c in s)
        if len(s) > 3 and digits / len(s) > 0.25:
            continue
        if s.isupper() and len(s) < 80:
            continue
        was_bullet = bool(BULLET.match(s))
        s = BULLET.sub('', s).strip()
        if _is_structural(s, was_bullet):
            continue
        s = s.replace(ITEM, '').strip()
        if len(s) < 45 and not s.endswith(('.', '?', '!', ';', ',')):
            continue
        out.append((index.get(s, approx), s))
    return out


# A metadata field label ("Funding:", "Conflicts of interest:") or a glossary
# entry ("Include: drink; take a sip", "Drink — drinking from the glass").
# These carry colons and semicolons as structure, not as sentence-avoidance, and
# counting them misreports the punctuation rate — the 2026-08-11 review of
# manuscript.tex had to discard the tool's colon flag and recount by hand.
LABEL_ONLY = re.compile(r'^[A-Z][\w /&\'-]{0,40}:\s*$')
FIELD_LABEL = re.compile(
    r'^(conflicts?( of interest)?|funding|ethics?( approval)?|data( availability)?|'
    r'materials?|code|analysis scripts?|preregistration|competing interests?|'
    r'author contributions?|acknowledge?ments?|availability|correspondence|'
    r'include|exclude|note|keywords?)\b[^.]{0,80}:', re.I)
GLOSS_ENTRY = re.compile(r'^[A-Z][\w\'-]{1,24}([ -][A-Z]?[\w\'-]{1,24}){0,2}\s*(—|:)\s')


def _is_structural(s: str, was_bullet: bool = False) -> bool:
    core = s.replace(ITEM, '').strip()
    if not core:
        return True
    if LABEL_ONLY.match(core) or FIELD_LABEL.match(core):
        return True
    # A list item opening on a short label is a definition entry, not prose. This
    # applies to Markdown bullets exactly as it does to LaTeX \item: `- **term** —
    # gloss` is the same construction as `\item[term] gloss`, and the separating
    # dash or colon is a formatting convention rather than an interruption. Without
    # this, README definition lists land in the em-dash and colon rates: on one
    # 12-README corpus the raw em-dash median was 14.04/1k, most of it this form.
    if (ITEM in s or was_bullet) and GLOSS_ENTRY.match(core):
        return True
    # A short line that only introduces something is a label, not a sentence.
    if core.endswith(':') and len(core.split()) <= 8:
        return True
    # Several semicolons with no sentence ending is a delimiter list (keyword
    # lists, deliverable lists), whatever markup produced it. Counting these as
    # clause-joins is what inflated the manuscript.tex semicolon rate.
    if core.count(';') >= 3 and not core.rstrip().endswith(('.', '?', '!')):
        return True
    return False


def paragraphs(lines):
    """Group prose lines into paragraphs: [(start_line, joined_text)]."""
    paras, buf, start = [], [], None
    for lineno, text in lines:
        if not text:
            if buf:
                paras.append((start, " ".join(buf)))
                buf, start = [], None
            continue
        if start is None:
            start = lineno
        buf.append(text)
    if buf:
        paras.append((start, " ".join(buf)))
    return [(s, re.sub(r'\s+', ' ', t)) for s, t in paras if t.strip()]


# ---------------------------------------------------------------- sentences

# A boundary is terminal punctuation NOT preceded by a known abbreviation and NOT
# preceded by a digit (so "0.77" and "Fig. 3" do not split). Validated against the
# papers corpus: yields median 28.5 w, matching the independently extracted 28-32.
BOUNDARY = re.compile(
    r'(?<!\be\.g)(?<!\bi\.e)(?<!\bcf)(?<!\bvs)(?<!\bal)(?<!\bFig)(?<!\bEq)(?<!\bNo)'
    r'(?<!\bVol)(?<!\bpp)(?<!\bSt)(?<!\bDr)(?<!\bapprox)(?<!\bca)(?<!\d)'
    r'[.!?]+["\')\]]*\s+(?=[A-Z(])')


def sentences(text: str):
    return [s.strip() for s in BOUNDARY.split(text) if len(s.split()) >= 3]


# ---------------------------------------------------------------- measurement

# The contrast-frame family from ai-drift.md. Counted here because the protocol
# otherwise asks the reviewer to total six surfaces across a whole document by
# hand, which is the counting task this tool exists to remove.
#
# These LOCATE, they do not verdict. Every hit is emitted with its excerpt for
# reading, because the surfaces differ in how cleanly a pattern identifies them
# and a count alone would invite exactly the false precision that regex-based
# em-dash classification produced in dev docs.
CONTRAST_SURFACES = [
    ("rather_than", "X rather than Y",
     r'\brather than\b'),
    ("not_just_but", "not just X but Y",
     r'\bnot (?:just|merely|simply|only)\b[^.]{0,100}\bbut\b'),
    ("not_semi_it_is", "not X; it is Y",
     r'\bnot\b[^.]{0,100};\s*(?:it|they|this|that|these)\s+(?:is|are|was|were)\b'),
    ("not_stop_it_is", "not X. It is Y.",
     r'\bis not\b[^.]{0,100}\.\s+(?:It|They|This|These)\s+(?:is|are|was|were)\b'),
    ("cleft", "It is X, not Y, that",
     r'\b[Ii]t (?:is|was)\b[^.]{0,80},\s*not\b[^.]{0,80},?\s*that\b'),
    ("not_only_it_is", "not only X, it is Y",
     r'\bnot only\b[^.]{0,120}[,;]\s*(?:it|they|this)\s+(?:is|are)\b'),
]
CONTRAST_RE = [(k, label, re.compile(p, re.I)) for k, label, p in CONTRAST_SURFACES]

GLOSS = re.compile(r'\((?:i\.e\.|e\.g\.)', re.I)
# Any parenthetical span. Semicolons and colons inside parentheses are delimiters
# (reference lists, statistics, "(F(1,58) = 4.2; p = .04)"), not clause-joins, so
# they are excluded before punctuation rates are computed.
CITE_PAREN = re.compile(r'\([^()]{0,300}\)')


def measure(path: Path):
    lines = extract_prose(path)
    paras = paragraphs(lines)
    all_sents, lengths = [], []
    for _, text in paras:
        for s in sentences(text):
            all_sents.append(s)
            lengths.append(len(s.split()))
    words = sum(lengths)
    if not lengths:
        return None
    per1k = lambda n: round(1000 * n / words, 2)
    prose = " ".join(t for _, t in paras)
    # colons/semicolons outside citation parentheticals
    stripped = CITE_PAREN.sub(' ', prose)
    return {
        "file": str(path),
        "words": words,
        "sentences": len(lengths),
        "paragraphs": len(paras),
        "median_sentence": statistics.median(lengths),
        "mean_sentence": round(statistics.mean(lengths), 1),
        "pct_over_40w": round(100 * sum(l > 40 for l in lengths) / len(lengths), 1),
        "pct_under_15w": round(100 * sum(l < 15 for l in lengths) / len(lengths), 1),
        "emdash_per_1k": per1k(prose.count("—")),
        "emdash_count": prose.count("—"),
        "colon_per_1k": per1k(len(re.findall(r'\w:\s', stripped))),
        "semicolon_per_1k": per1k(stripped.count(";")),
        # The three interruption marks summed. Reported, deliberately NOT thresholded.
        #
        # A document written to the zero-em-dash override can satisfy it completely
        # and still carry every original interruption, because the dashes were
        # swapped for colons and semicolons rather than restructured into sentences.
        # The em-dash rate alone therefore cannot tell a reviewer whether the rule
        # was met or merely routed around, which is why this total is printed
        # alongside it.
        #
        # It carries no threshold because none survives calibration. Tried against
        # the 16-paper corpus with a reference of colon+semicolon median and a zero
        # em-dash allowance (3.90/1k), it fired on 8 of the 16 — the author's own
        # combined load ranges 1.72 to 14.59, so no single cut separates drift from
        # register. The relocation judgement belongs to Dimension E's adjudication
        # step in review-protocol.md, which can compare against the same document's
        # prior revision and add the Dimension B contrast-frame count. Both of those
        # are unavailable here, and a counter that guesses is worse than one that
        # reports.
        "punct_load_per_1k": per1k(prose.count("—")
                                   + len(re.findall(r'\w:\s', stripped))
                                   + stripped.count(";")),
        "gloss_per_1k": per1k(len(GLOSS.findall(prose))),
        "paren_per_1k": per1k(prose.count("(")),
        "contrast_per_1k": per1k(sum(len(rx.findall(prose)) for _, _, rx in CONTRAST_RE)),
        "contrast_by_surface": {k: per1k(len(rx.findall(prose))) for k, _, rx in CONTRAST_RE},
        "_paras": paras,
        "_lengths": lengths,
    }


def find_candidates(m, baseline=None):
    """Locate every item review must adjudicate. Counting only, no judgement."""
    out = []
    for start, text in m["_paras"]:
        stripped = CITE_PAREN.sub(' ', text)
        for mt in re.finditer(r'—', text):
            out.append({"kind": "em-dash", "line": start, "rule": "base.md: default zero",
                        "excerpt": _around(text, mt.start())})
        colons = len(re.findall(r'\w:\s', stripped))
        if colons >= 2:
            out.append({"kind": "colon-cluster", "line": start, "count": colons,
                        "rule": "base.md 2026-08-06: flag any paragraph with 2+ colons",
                        "excerpt": text[:180]})
        semis = stripped.count(";")
        if semis >= 2:
            out.append({"kind": "semicolon-cluster", "line": start, "count": semis,
                        "rule": "base.md: sparing, only when earned", "excerpt": text[:180]})
    # Long sentences are only candidates when the document runs longer than the
    # author's own measured register. Their baseline share is 22% in papers, so
    # emitting every >40w sentence floods the report with the author's own voice.
    over_base = baseline.get("pct_over_40w") if baseline else None
    flood = over_base is not None and m["pct_over_40w"] <= over_base * 1.3
    if not flood:
        longs = []
        for start, text in m["_paras"]:
            for s in sentences(text):
                n = len(s.split())
                if n > 40:
                    longs.append({"kind": "long-sentence", "line": start, "words": n,
                                  "rule": "judge: length from construction (split) or content (keep)",
                                  "excerpt": s[:220]})
        longs.sort(key=lambda c: -c["words"])
        out.extend(longs[:15])
        if len(longs) > 15:
            out.append({"kind": "note", "line": None,
                        "rule": f"{len(longs)} sentences over 40 words; showing the 15 longest"})
    # Cap per-kind volume. A grant with a document-wide colon habit yields dozens
    # of identical paragraph findings; the rate delta already states the systemic
    # problem, and review needs specimens rather than an exhaustive list.
    capped, seen = [], {}
    for c in out:
        k = c["kind"]
        seen[k] = seen.get(k, 0) + 1
        if seen[k] <= 12:
            capped.append(c)
    for k, n in seen.items():
        if n > 12:
            capped.append({"kind": "note", "line": None,
                           "rule": f"{n} '{k}' findings; showing the first 12. "
                                   f"The document-level rate is the finding that matters."})
    out = capped

    # Contrast frames. Two regimes, per ai-drift.md and the per-surface split a
    # style profile records: surfaces the author genuinely uses are judged on the
    # family rate alone, and surfaces effectively absent from their corpus are
    # flagged on occurrence as negative-space evidence.
    corpus = (baseline or {}).get("contrast_by_surface") or {}
    for start, text in m["_paras"]:
        for key, label, rx in CONTRAST_RE:
            if corpus and corpus.get(key, 0) > 0.05:
                continue                      # author's own construction; rate test only
            for mt in rx.finditer(text):
                out.append({"kind": "contrast-frame-rare", "line": start, "surface": label,
                            # The negative-space argument rests entirely on the corpus
                            # split. With no baseline there is no evidence that this
                            # surface is rare *for this author*, so say so rather than
                            # let the protocol treat it as flaggable on one occurrence.
                            "corpus_backed": bool(corpus),
                            "rule": "absent from the author's corpus; ai-drift.md contrast-frame family"
                                    if corpus else
                                    "contrast-frame family (no per-surface corpus split available)",
                            "excerpt": _around(text, mt.start())})
    fam = m["contrast_per_1k"]
    if fam > 1.0:
        # Carry the breakdown. A family total is uninterpretable without it: a rate
        # made entirely of one surface the author genuinely uses is a different
        # finding from the same rate spread across surfaces absent from their
        # corpus, and only the second is drift by the family argument. Observed
        # in live use: 100% of a 2.57/1k family total was `rather than`, whose
        # instances a prose review had already judged load-bearing.
        by = {lab: m["contrast_by_surface"][k] for k, lab, _ in CONTRAST_RE
              if m["contrast_by_surface"][k]}
        top = max(by.items(), key=lambda x: x[1]) if by else None
        concentrated = bool(top and fam and top[1] / fam >= 0.8)
        out.append({"kind": "contrast-frame-rate", "line": None, "observed": fam,
                    "threshold": 1.0, "by_surface": by,
                    "concentrated_in": top[0] if concentrated else None,
                    "rule": "ai-drift.md: family total above ~1/1k is medium, above ~1.25/1k high. "
                            + ("Nearly all of this total is a single surface: check the per-surface "
                               "split in the style profile before treating it as drift, because a "
                               "surface the author genuinely uses can carry the whole rate."
                               if concentrated else
                               "Spread across surfaces; judge on the family argument.")})

    if baseline:
        # Two-directional: drifting either side of the author's measured voice is
        # drift. Flat-and-glossless is the AI-collaboration failure; inflated is
        # the grant-register failure.
        for key, label in (("median_sentence", "median sentence length"),
                           ("gloss_per_1k", "(i.e./e.g.) gloss density"),
                           ("pct_over_40w", "share of sentences over 40 words")):
            base, got = baseline.get(key), m.get(key)
            if not base:
                continue
            delta = (got - base) / base
            if abs(delta) >= 0.30:
                out.append({"kind": "baseline-delta", "metric": label, "line": None,
                            "observed": got, "baseline": base,
                            "delta_pct": round(100 * delta, 1),
                            "rule": "distance from the author's measured voice, either direction"})
        # Punctuation is one-directional: under-use is never a fault. The reference
        # is the papers rate even when reviewing a grant, because grants.md records
        # the measured grant rate (colons 8.39/1k) as a problem to correct rather
        # than a register to match. Matching that baseline would legitimise it.
        # The threshold is the 90th-percentile papers rate, not the median.
        #
        # It was the median until 2026-08-11, which fired on 7 of the author's own
        # 16 papers: half a corpus sits above its own median by definition, and a
        # 1.3x tolerance does not cover a spread this wide (colons range 0.40 to
        # 9.56 per 1k, semicolons 0.37 to 4.13). A flag that marks 44% of the
        # reference corpus as drift is telling the reviewer nothing.
        #
        # p90 asks the answerable question instead: is this document heavier than
        # nine in ten of the author's own papers? With a 1.15x band that fires on
        # 3 of 16 rather than 7, and still catches the grant register (median colon
        # rate 7.39/1k) that grants.md records as a fault to correct. The median is
        # still reported next to it as the voice baseline; it is simply not the
        # threshold.
        ref = _punct_reference()
        for key, p90key, label in (("colon_per_1k", "colon_p90", "colon rate"),
                                   ("semicolon_per_1k", "semicolon_p90", "semicolon rate")):
            got = m.get(key)
            base, mult = ref.get(p90key), 1.15
            if not base:                      # baselines.json predates the p90 keys
                base, mult = ref.get(key), 1.3
            if not base or got <= base * mult:
                continue
            out.append({"kind": "punctuation-above-reference", "metric": label, "line": None,
                        "observed": got, "reference": base,
                        "reference_kind": "papers p90" if ref.get(p90key) else "papers median",
                        "median": ref.get(key),
                        "delta_pct": round(100 * (got - base) / base, 1),
                        "rule": "base.md: colons/semicolons sparing; heavier than 9 in 10 of the "
                                "author's own papers"})
    return out


def _punct_reference():
    """Colon/semicolon reference rates: the author's most disciplined register."""
    if BASELINE_PATH.exists():
        data = json.loads(BASELINE_PATH.read_text())
        if "papers" in data:
            return data["papers"]
    return {}


def _around(text, i, w=70):
    return ("…" if i - w > 0 else "") + text[max(0, i - w):i + w] + ("…" if i + w < len(text) else "")


# ---------------------------------------------------------------- baselines

def emit_baseline(patterns):
    out = {}
    keys = ("median_sentence", "gloss_per_1k", "pct_over_40w",
            "colon_per_1k", "semicolon_per_1k", "paren_per_1k", "contrast_per_1k")
    # Punctuation also gets a p90, because the flag needs an upper bound of the
    # author's observed range rather than its centre (see find_candidates).
    p90_keys = ("colon_per_1k", "semicolon_per_1k")
    for genre, pattern in patterns:
        acc, files = {k: [] for k in keys}, 0
        surf = {k: [] for k, _, _ in CONTRAST_RE}
        # recursive=True so `**` works: a dev-doc corpus is READMEs scattered
        # through a source tree, not a flat directory like examples/papers. That
        # makes vendored directories reachable, and a dependency's README is not
        # the author's writing, so they are excluded here rather than left to the
        # caller's glob.
        for f in sorted(glob.glob(pattern, recursive=True)):
            if any(part in VENDOR_DIRS for part in Path(f).parts):
                continue
            m = measure(Path(f))
            if m and m["sentences"] >= 20:
                for k in keys:
                    acc[k].append(m[k])
                for k, v in m["contrast_by_surface"].items():
                    surf[k].append(v)
                files += 1
        if files:
            out[genre] = {"n_docs": files}
            out[genre].update({k: round(statistics.median(v), 2) for k, v in acc.items()})
            for k in p90_keys:
                v = sorted(acc[k])
                p90 = (v[-1] if len(v) < 4
                       else statistics.quantiles(v, n=100, method="inclusive")[89])
                out[genre][k.replace("_per_1k", "_p90")] = round(p90, 2)
            # Per-surface contrast-frame rates. A surface at ~0 across the corpus
            # is negative-space evidence and review flags it on occurrence; a
            # surface the author genuinely uses is judged on the family rate only.
            # Corpus MEAN, not median: most surfaces are absent from most single
            # documents, so a median would read 0.0 for constructions the author
            # demonstrably uses.
            out[genre]["contrast_by_surface"] = {
                k: round(statistics.mean(v), 3) if v else 0.0 for k, v in surf.items()}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", nargs="?")
    ap.add_argument("--genre")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--corpus", action="append", metavar="GENRE=GLOB")
    ap.add_argument("--emit-baseline", action="store_true")
    a = ap.parse_args()

    if a.emit_baseline:
        pats = [tuple(c.split("=", 1)) for c in (a.corpus or [])] or [
            ("papers", str(CORPUS_DIR / "papers/*.md")),
            ("grants", str(CORPUS_DIR / "grants/*.md"))]
        data = emit_baseline(pats)
        if not data:
            print(f"no corpus files matched under {CORPUS_DIR} — nothing written",
                  file=sys.stderr)
            return 1
        BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        BASELINE_PATH.write_text(json.dumps(data, indent=2) + "\n")
        print(json.dumps(data, indent=2))
        print(f"\nwritten to {BASELINE_PATH}", file=sys.stderr)
        return 0

    if not a.target:
        ap.error("TARGET required (or use --emit-baseline)")
    p = Path(a.target)
    if not p.exists():
        print(f"target not found: {p}", file=sys.stderr); return 2
    m = measure(p)
    if not m:
        print(f"no prose found in {p}", file=sys.stderr); return 2

    baseline = None
    if BASELINE_PATH.exists() and a.genre:
        baseline = json.loads(BASELINE_PATH.read_text()).get(a.genre)
    cands = find_candidates(m, baseline)
    summary = {k: v for k, v in m.items() if not k.startswith("_")}

    if a.json:
        print(json.dumps({"summary": summary, "baseline": baseline,
                          "candidates": cands}, indent=2))
        return 0

    print(f"# {p.name}  ({summary['words']} words, {summary['sentences']} sentences, "
          f"{summary['paragraphs']} paragraphs)\n")
    ref = _punct_reference()
    load_ref = round((ref.get("colon_per_1k") or 0) + (ref.get("semicolon_per_1k") or 0), 2)
    for k in ("median_sentence", "mean_sentence", "pct_over_40w", "pct_under_15w",
              "emdash_per_1k", "colon_per_1k", "semicolon_per_1k", "punct_load_per_1k",
              "gloss_per_1k", "contrast_per_1k"):
        line = f"  {k:<18} {summary[k]:>8}"
        if k in ("colon_per_1k", "semicolon_per_1k"):
            if ref.get(k):                       # papers rate, not the genre rate
                line += f"    reference {ref[k]:>6} (papers)"
        elif k == "punct_load_per_1k":
            if load_ref:
                line += f"    reference {load_ref:>6} (papers, em-dash target 0)"
        elif baseline and k in baseline:
            line += f"    baseline {baseline[k]:>6}"
        print(line)
    if summary["emdash_count"]:
        print(f"\n  em-dashes present: {summary['emdash_count']} (target is zero)")
    print(f"\n# candidates for review to adjudicate: {len(cands)}\n")
    for c in cands:
        loc = f"line {c['line']}" if c.get("line") else "document"
        extra = c.get("count") or c.get("words") or c.get("delta_pct") or ""
        print(f"  [{c['kind']}] {loc} {extra}")
        if c.get("excerpt"):
            print(f"      {c['excerpt'][:150]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
