#!/usr/bin/env python3
"""Locate the three register faults specific to commercial prose.

Companion to prose_metrics.py for `--genre business`. Same contract: this tool
LOCATES and COUNTS; the reviewer adjudicates. It never decides that an instance
is drift, only that it is worth reading.

Three sweeps:

  teaching     The sentence whose subject-matter is the READER rather than the
               business. This is the fault that produced the overlay: a
               commercial document that explains a distinction, tells the
               counterparty what they are doing, reports its own editing
               history, or volunteers a hypothetical failure has stopped
               reporting and started teaching.

  em-dash      Split into paired interruptions and unpaired trailing dashes.
               Measured across 11 outward documents (~20,000 words): 16% paired,
               84% unpaired, and of the unpaired, 63% should be a full stop. The
               paired form carries a construction no other mark does; the
               unpaired form is a dash standing in for a sentence break.

  antithesis   The trailing "X, not Y." snap-close. Measured at 3.29 per 1,000
               words in the business corpus against 0.31 across the author's own
               16 papers. Roughly half rule out a real alternative and are kept;
               the tool cannot tell which, so it lists them all.

Usage:
    python3 tools/business_tells.py TARGET [TARGET ...] [--json]

Markdown, plain text and HTML are read directly. Structural em-dash forms
(markdown table rows, definition-list entries, titles, HTML table cells) are
subtracted before counting, per the base.md dev-doc precedent.
"""
import json
import os
import re
import sys

# ── source normalisation ─────────────────────────────────────────────────────

DEFLIST = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\*\*[^*]+\*\*\s+—")
TITLE = re.compile(r"^\s*#{1,6}\s.*—")
# Two more markdown structural forms met in this corpus. The bracketed editorial
# label ("[TRANSFER LINE — pick one:]") is an instruction to whoever sends the
# document, and the field line ("**Subject:** … — initial data") is a header, not
# prose. Both are the definition-list convention in another costume.
BRACKET_LABEL = re.compile(r"^\s*\[[^\]]*—[^\]]*\]\s*$")
FIELD_LINE = re.compile(r"^\s*(?:>\s*)?\*\*[A-Z][^*]{0,24}:\*\*")
ENTITIES = [("&mdash;", "—"), ("&ndash;", "–"), ("&nbsp;", " "),
            ("&rsquo;", "'"), ("&lsquo;", "'"), ("&amp;", "&"),
            ("&times;", "x"), ("&minus;", "-"), ("&euro;", "€"),
            ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')]


def read_source(path):
    """Return prose text with structural markup removed.

    HTML tables are stripped wholesale: "label — value" inside a cell is the
    same formatting convention as a markdown table row, and counting it as prose
    inflated an earlier measurement of this corpus by 43%.
    """
    src = open(path, encoding="utf-8", errors="replace").read()
    if path.lower().endswith((".html", ".htm")):
        src = re.sub(r"<(style|script).*?</\1>", " ", src, flags=re.S)
        src = re.sub(r"<table.*?</table>", " ", src, flags=re.S)
        # The definition-list entry, HTML form: <li><b>Term</b> &mdash; gloss</li>.
        # Exactly the markdown "- **term** — gloss" convention that base.md's
        # dev-doc override already excludes, so the dash is dropped before counting
        # while the gloss itself stays in the prose stream.
        src = re.sub(r"(<(?:li|p|div|span|dt|dd)[^>]*>\s*(?:<(?!/)[^>]+>\s*)*"
                     r"(?:<(?:b|strong)>[^<]{1,70}</(?:b|strong)>)\s*)"
                     r"(?:&mdash;|\u2014)", r"\1", src, flags=re.I)
        # The glossary lead-in, where the bold spans both term and gloss:
        # <p><strong>Controller &mdash; the Club.</strong> The organisation that...
        # Same convention, dash inside the emphasis rather than outside it.
        src = re.sub(r"(<(?:p|li|div|span|dt|dd)[^>]*>\s*<(?:b|strong)>[^<]{1,45}?)"
                     r"(?:&mdash;|\u2014)", r"\1", src, flags=re.I)
        # Titles and headings are the HTML form of "# Name — Subtitle".
        src = re.sub(r"<title>.*?</title>", " ", src, flags=re.S | re.I)
        src = re.sub(r"<h[1-6][^>]*>.*?</h[1-6]>", " ", src, flags=re.S | re.I)
        # Block tags become line breaks so the label heuristic below can see one
        # block at a time; inline tags become spaces, or a sentence spanning
        # <strong> would be split in half and its paired dashes miscounted.
        src = re.sub(r"</?(div|p|li|ul|ol|tr|td|th|section|article|br|hr|blockquote)\b[^>]*>",
                     "\n", src, flags=re.I)
        src = re.sub(r"<[^>]+>", " ", src)
        for a, b in ENTITIES:
            src = src.replace(a, b)
        # A short block with no sentence-ending punctuation is a field label, the
        # HTML counterpart of the markdown definition-list entry ("Pricing region
        # — tick one", "7. Exclusivity — binding"). Never prose; never counted.
        kept = []
        for block in src.split("\n"):
            t = block.strip()
            if "—" in t and len(t.split()) <= 10 and not re.search(r"[.!?:;]\s*$", t):
                continue
            kept.append(block)
        return "\n".join(kept), False
    keep = [ln for ln in src.split("\n")
            if not (DEFLIST.match(ln) or TITLE.match(ln) or BRACKET_LABEL.match(ln)
                    or FIELD_LINE.match(ln) or ln.lstrip().startswith("|"))]
    return "\n".join(keep), True


def line_of(src, pos):
    return src.count("\n", 0, pos) + 1


def sentence_at(src, pos, width=220):
    lo = max(src.rfind(". ", 0, pos), src.rfind("\n", 0, pos)) + 1
    hi = src.find(". ", pos)
    hi = hi + 1 if hi != -1 else min(len(src), pos + width)
    return re.sub(r"\s+", " ", src[lo:hi]).strip()


# ── sweep 1: the teaching sentence ───────────────────────────────────────────
# Each pattern is a grammatical signal, not a keyword: the sentence is ABOUT the
# reader. Validated against the nine sentences that prompted the overlay; the
# set catches all nine.

TEACHING = [
    (r"\b(routinely|commonly|often|frequently|widely|easily)\s+"
     r"(confused|misunderstood|conflated|missed|overlooked)\b",
     "explains-the-concept", "names a mistake the reader might make"),
    (r"\bthe two are\s+\w+", "explains-the-concept",
     "compares two ideas for the reader's benefit"),
    (r"\b(a|one)\s+common\s+(mistake|error|misconception|confusion)\b",
     "explains-the-concept", "names a common error"),
    (r"\b(people|readers|most\s+\w+s)\s+"
     r"(often|usually|typically|tend to|assume|think|believe)\b",
     "explains-the-concept", "generalises about what people think"),
    (r"\bit is worth (understanding|remembering|knowing|bearing in mind)\b",
     "explains-the-concept", "instructs the reader to hold something in mind"),
    (r"\b(put simply|simply put|in plain terms|think of (it|this) as|"
     r"which simply means|that is to say|to be clear)\b",
     "explains-the-concept", "signals a simplification for the reader"),
    (r"\bis (routinely|often|sometimes) (mistaken|taken) for\b",
     "explains-the-concept", "corrects an anticipated misreading"),

    (r"\ban?\s+(investor|reader|club|buyer|partner)\s+\w{0,12}\s*"
     r"(underwriting|reading|considering|evaluating|looking at)\b[^.]{0,80}\bis\b",
     "instructs-the-reader", "tells the counterparty what they are doing"),
    (r"\b(the|a) (key )?(takeaway|thing to (note|see|understand)|"
     r"point to (note|grasp))\b", "instructs-the-reader", "announces the conclusion"),
    (r"\bthis is the (view|table|number|figure|chart|exhibit) that\b",
     "instructs-the-reader", "tells the reader which exhibit matters"),
    (r"\bwhich is the clearest (statement|expression|illustration)\b",
     "instructs-the-reader", "interprets the fact for the reader"),
    (r"\b(what matters here|what this (means|shows|tells you) is|read this as|"
     r"the number to watch)\b", "instructs-the-reader", "interprets rather than reports"),
    (r"\bis the whole (investment case|point|reason|story)\b",
     "instructs-the-reader", "asserts significance instead of showing it"),
    (r"\b(nothing|everything) (here|in this|about this)\b[^.]{0,60}"
     r"(;|,)\s*(nothing|everything)\b",
     "instructs-the-reader", "totalising chiasmus in place of a fact"),

    (r"\ban? earlier (version|draft|model|note|page)\b",
     "narrates-its-own-revisions", "reports the document's editing history"),
    (r"\bthe (earlier|previous|old|former) "
     r"(three-tier|ladder|model|structure|version|approach)\b",
     "narrates-its-own-revisions", "references a superseded internal model"),
    (r"\b(this|it) (has been|was) (corrected|revised|updated|superseded)\b",
     "narrates-its-own-revisions", "reports a revision"),
    (r"\bdoes not survive (the|our) \w+",
     "narrates-its-own-revisions", "reports a failed prior claim"),

    (r"\bif (this|that|the) \w+ ever (has to|needs to|must) (break|change|move|rise)\b",
     "hypothetical-self-criticism", "volunteers a failure case nobody raised"),
    (r"\bwould be a (problem|failure|concern) (with|for|in)\b",
     "hypothetical-self-criticism", "volunteers a hypothetical fault"),
]


def sweep_teaching(src):
    found, seen = [], set()
    for rx, kind, why in TEACHING:
        for m in re.finditer(rx, src, re.I):
            sent = sentence_at(src, m.start())
            if sent in seen:
                continue
            seen.add(sent)
            found.append(dict(kind="teaching", subtype=kind, line=line_of(src, m.start()),
                              why=why, text=sent[:200]))
    return sorted(found, key=lambda f: f["line"])


# ── sweep 2: em-dashes, paired versus unpaired ───────────────────────────────

FINITE = re.compile(
    r"\b(is|are|was|were|has|have|had|will|would|can|could|does|do|did|sits|runs|"
    r"costs|carries|means|makes|gets|goes|comes|stays|holds|pays|buys|scales|"
    r"starts|takes|needs|becomes|applies|reflects|covers|turns)\b", re.I)
SUBJ = re.compile(r"^\s*(it|that|this|they|we|you|there|the\s+\w+|a\s+\w+|an\s+\w+|"
                  r"\w+ing|[A-Z]\w+)\b")


def replacement_for(tail):
    """Which mark should carry this, if not a dash."""
    t = tail.strip().rstrip(".")
    if re.match(r"^(see|check|fix|note|use|read)\b", t, re.I):
        return "full stop"
    if re.match(r"^not\b", t, re.I):
        return "comma"
    if SUBJ.match(t) and FINITE.search(t):
        return "full stop"
    if re.match(r"^(the|a|an)\b", t, re.I) and "," in t:
        return "colon"
    if re.match(r"^(i\.e\.|e\.g\.|which|where|whose|especially|in particular)\b", t, re.I):
        return "parentheses"
    if len(t.split()) <= 6:
        return "comma"
    return "full stop"


def sweep_emdash(src):
    """Paired interruptions carrying internal commas are the permitted form."""
    out = []
    for sent in re.split(r"(?<=[.!?])\s+(?=[A-Z*`\"'])", src):
        if "—" not in sent:
            continue
        s = re.sub(r"\s+", " ", sent).strip()
        pos = src.find(sent)
        n = s.count("—")
        if n >= 2:
            inner = s.split("—")[1]
            earned = "," in inner and len(inner.split()) >= 4
            out.append(dict(kind="em-dash", form="paired", count=n,
                            verdict="keep" if earned else "recast",
                            fix="" if earned else "parentheses, or two sentences",
                            line=line_of(src, pos if pos >= 0 else 0), text=s[:200]))
        else:
            out.append(dict(kind="em-dash", form="unpaired", count=1, verdict="recast",
                            fix=replacement_for(s.split("—", 1)[1]),
                            line=line_of(src, pos if pos >= 0 else 0), text=s[:200]))
    return out


# ── sweep 3: the trailing antithesis ─────────────────────────────────────────

ANTITHESIS = re.compile(r",\s*not\s+(?:just\s+|merely\s+)?[a-z][^.,;]{2,45}[.;]")


def sweep_antithesis(src):
    return [dict(kind="antithesis", line=line_of(src, m.start()),
                 text=sentence_at(src, m.start())[:200],
                 why="does the reader need the alternative ruled out, "
                     "or is the sentence landing a beat?")
            for m in ANTITHESIS.finditer(src)]


# ── report ───────────────────────────────────────────────────────────────────

def analyse(path):
    src, _ = read_source(path)
    words = len(re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", src))
    teaching = sweep_teaching(src)
    em = sweep_emdash(src)
    anti = sweep_antithesis(src)
    dashes = sum(e["count"] for e in em)
    keep = sum(e["count"] for e in em if e["verdict"] == "keep")
    return dict(
        file=path, words=words,
        teaching=teaching, em_dash=em, antithesis=anti,
        summary=dict(
            teaching_count=len(teaching),
            em_dash_prose=dashes,
            em_dash_paired_kept=keep,
            em_dash_to_recast=dashes - keep,
            em_dash_per_1k=round(dashes / words * 1000, 2) if words else 0.0,
            em_dash_per_1k_after=round(keep / words * 1000, 2) if words else 0.0,
            antithesis_count=len(anti),
            antithesis_per_1k=round(len(anti) / words * 1000, 2) if words else 0.0,
        ))


def main(argv):
    as_json = "--json" in argv
    targets = [a for a in argv if not a.startswith("--")]
    if not targets:
        print(__doc__)
        return 2
    results = [analyse(t) for t in targets if os.path.exists(t)]
    if as_json:
        print(json.dumps(results, indent=1))
        return 0
    for r in results:
        s = r["summary"]
        print(f"\n{'=' * 92}\n{r['file']}  ({r['words']} words)\n{'=' * 92}")
        print(f"  teaching sentences   {s['teaching_count']}")
        print(f"  prose em-dashes      {s['em_dash_prose']}  "
              f"({s['em_dash_per_1k']}/1k)  keep {s['em_dash_paired_kept']}, "
              f"recast {s['em_dash_to_recast']}  -> {s['em_dash_per_1k_after']}/1k")
        print(f"  trailing antithesis  {s['antithesis_count']}  "
              f"({s['antithesis_per_1k']}/1k, corpus 0.31/1k)")
        for t in r["teaching"]:
            print(f"\n  L{t['line']} [{t['subtype']}] {t['why']}\n      \"{t['text'][:150]}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
