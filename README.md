# marginalia

**A writing assistant that learns how *you* write, then tells you where a draft has stopped sounding like you.**

It also checks that your citations exist and actually say what you claim they say.

Built by an academic, for academic writing: papers, grant proposals, chapters, reports.

Runs on Claude Code today. The procedures themselves are plain English and not
tied to any model, so it can be adapted to OpenAI, Gemini or a local model. See
[docs/PORTING.md](docs/PORTING.md).

---

## The problem it solves

If you use AI to help with writing, your prose drifts. Not dramatically, and not
in ways you notice while you are inside the document. It gets smoother, flatter
and more generic. Sentences shorten. Certain words creep in: *delve*, *crucial*,
*robust*, *underscore*. Your actual voice, the thing that made the writing
recognisably yours, quietly leaks out.

The other problem is citations. AI-assisted drafts contain references that do not
exist, references with the wrong year, and references that are real but do not
support the claim attached to them.

marginalia checks for both. It is a **critic, not a ghostwriter**: it tells you
what it found and you decide what to do. It never edits your files without
showing you exactly what it wants to change and waiting for you to say yes.

The unusual part is what it compares against. Most writing tools measure you
against generic "good writing" rules. marginalia measures you against **your own
published work**. If you write long, clause-dense sentences, it will not tell you
to shorten them. It will tell you when a draft has stopped doing what you
normally do.

---

## Before you start

You need three things. If you already have them, skip to [Install](#install).

### 1. A terminal

On a Mac, press `Cmd + Space`, type `Terminal`, press Enter. A window opens where
you type commands. That is all a terminal is.

On Windows, use Windows Terminal or PowerShell.

Throughout this guide, anything in a box like this is something you type or paste
into that window, then press Enter:

```bash
echo hello
```

### 2. Claude Code

marginalia runs inside **Claude Code**, Anthropic's assistant for the terminal.
It needs a Claude account on a paid plan.

Install instructions: <https://docs.claude.com/en/docs/claude-code/overview>

To check it worked:

```bash
claude --version
```

A version number means you are set. "Command not found" means it is not installed
yet.

### 3. Python 3

Almost certainly already on your machine. Check:

```bash
python3 --version
```

If you see `Python 3.something`, you are done. Otherwise install it from
<https://www.python.org/downloads/>.

### Optional, depending on your files

Only needed if your published work is in PDF or Word format, which it probably
is.

On a Mac, first install Homebrew (a tool for installing other tools) from
<https://brew.sh>, then:

```bash
brew install pandoc poppler
```

`pandoc` reads Word documents. `poppler` reads PDFs. Without them marginalia
still runs, but only sees plain text and Markdown files.

---

## Install

**Step 1.** Open your terminal and pick where to put it. Your home folder is
fine:

```bash
cd ~
```

**Step 2.** Download marginalia:

```bash
git clone https://github.com/xkiwilabs/marginalia.git
cd marginalia
```

*(`git clone` downloads a copy of this project. `cd` moves you into the folder it
just created.)*

**Step 3.** Install it into Claude Code:

```bash
./install.sh
```

You should see a list of green ticks ending in "Done."

**Step 4.** Restart Claude Code, or start a new session.

To check it worked, start Claude Code and type `/marginalia`. It should be
recognised as a command.

> **What just happened?** The installer created shortcuts from Claude Code's
> settings folder to this project. Claude Code now knows about seven new
> abilities, called *skills*, plus a `/marginalia` command. They are shortcuts
> rather than copies, so updating this project updates what Claude Code uses,
> automatically.

---

## Teaching it your voice

marginalia starts out knowing nothing about you. Until you finish this section it
can still catch generic AI-sounding writing, but it cannot tell you when
something does not sound like *you*, because it has never seen your writing.

Budget about ten minutes, most of it the computer working.

### Step 1: Make a folder for your writing

```bash
mkdir -p ~/.marginalia/examples/papers
mkdir -p ~/.marginalia/examples/grants
mkdir -p ~/.marginalia/examples/other
```

This creates a hidden folder in your home directory. **That is deliberate: it
sits outside the marginalia project folder**, so your writing is never caught up
in anything you later share or publish.

### Step 2: Add your published work

Copy in things you have actually published or been funded for. PDFs and Word
files are fine.

```bash
cp ~/Documents/my-papers/*.pdf ~/.marginalia/examples/papers/
```

Or drag the files in using Finder. To open that folder in Finder:

```bash
open ~/.marginalia/examples
```

**This step matters more than anything else in this guide.** marginalia will
learn to imitate whatever you put here.

- **Do add:** published papers, funded applications, book chapters, anything peer-reviewed or written entirely by you.
- **Do not add:** drafts, anything written with AI help, anything you are not happy with.

Feed it AI-assisted drafts and it will faithfully learn the drift as though it
were your voice, then defend that drift in every future review.

**How many?** Three or more per category gives a solid profile. One or two works
but gets marked low-confidence. An empty category is fine.

### Step 3: Build the profile

Start Claude Code inside the marginalia folder:

```bash
cd ~/marginalia
claude
```

Then type:

```
/marginalia extract-style --genre=all
```

This reads every document and works out how you write: typical sentence length,
which words you reach for, how you bring in citations, how you build a paragraph,
how you handle an objection. It takes a few minutes and reports what it found.

Then, back in the terminal:

```bash
python3 tools/prose_metrics.py --emit-baseline
```

This measures the numbers, such as your average sentence length and punctuation
rates. They become the yardstick a review compares a draft against.

### Step 4: Check that it worked

```
/marginalia calibrate --genre=papers
```

This is a test, and worth the five minutes. It takes a passage of your own
writing, hides it, rebuilds it from the profile alone, then compares its attempt
against what you actually wrote. If the profile is wrong, this is where you find
out, and it proposes fixes.

**Do not skip this.** A profile nobody has tested is a guess.

---

## Using it

Start Claude Code in the folder where your document lives, then:

### Review a draft

```
/marginalia review my-paper.md
```

You get a report of what it found: AI-sounding words, structural tics, places the
draft has drifted from your usual style, each with a line number and a suggested
fix. Your file is not touched.

Add `--genre=grants` for a grant application, since the register differs.

### Check the citations

```
/marginalia cite my-paper.md
```

Checks every citation at four levels: does it exist, is the venue reputable, does
the source actually support your claim, and is there a better source. This one
takes a while, because it searches academic databases for each reference.

### Apply the suggested edits

```
/marginalia apply my-paper.md.marginalia/2026-05-15-1142-review.md
```

Walks through the report's suggestions. **It shows a before-and-after for every
change and waits for your approval.** Mechanical fixes are grouped; anything
needing judgement comes to you one at a time.

### Write something new in your voice

```
/marginalia write "draft an abstract about coordination dynamics"
```

You can also just ask Claude for writing help normally, in any session. It
notices and applies your voice profile without being asked.

### Everything else

| Command | What it does |
|---|---|
| `/marginalia review <file>` | Check a draft for drift |
| `/marginalia cite <file>` | Verify citations |
| `/marginalia full <file>` | Both at once |
| `/marginalia apply <report>` | Apply edits, with your approval |
| `/marginalia write "<task>"` | Draft in your voice |
| `/marginalia extract-style` | Build or rebuild your profile |
| `/marginalia calibrate` | Test that the profile sounds like you |
| `/marginalia refine` | Improve your voice, not just enforce it |
| `/marginalia adapt --to=blog` | Guess a profile for a format you have not written in yet |
| `/marginalia clean` | Delete old reports |

### File types

Works directly with `.md`, `.txt`, `.tex` and `.mdx`. PDFs and Word files are
converted automatically, though conversion is imperfect for figures, complex
tables and multi-column layouts.

---

## Where your files live, and why

Two locations, kept deliberately apart.

| What | Where | Why |
|---|---|---|
| The tool | `~/marginalia/` | Shared. Anyone can have a copy. |
| **Your writing and profile** | `~/.marginalia/` | **Private. Yours alone.** |

Your profile is not a list of abstract rules. It contains **actual sentences from
your papers**, because that is what lets it reproduce your voice rather than
merely describe it. It may quote unpublished work.

That is why it lives outside the project folder, and why this repository refuses
to track profiles even if you put one there. If you fork this project or push
changes anywhere, check what you are about to publish.

The same goes for `baselines.json`, the file of measured numbers. It describes
one person's writing. Using someone else's would silently compare your prose to
their voice, with nothing visible to tell you it was happening.

---

## When something goes wrong

**`/marginalia` is not recognised.** Restart Claude Code. If it still fails, run
`./install.sh` again from the marginalia folder and read the output for errors.

**"No base style available."** The profile has not been built yet. See
[Teaching it your voice](#teaching-it-your-voice).

**"command not found: python3"** Python is not installed. See
[Before you start](#before-you-start).

**A PDF produced nothing.** It is probably a scan rather than text. Run it
through OCR first (`ocrmypdf` works well), or find a text version.

**It flags things that are genuinely your style.** The profile is missing
something. Add a note to the `## Manual overrides` section at the bottom of the
relevant file in `~/.marginalia/styles/`. Anything written there outranks
everything the tool worked out by itself, and survives every rebuild.

**It flags nothing on a document you know is bad.** Check the report header for
which profile files were loaded. If it says none, the profile is not being found.

**Everything looks wrong after I added new work.** Rebuild both halves, not just
one:

```
/marginalia extract-style --genre=all
```
```bash
python3 tools/prose_metrics.py --emit-baseline
```

---

## Glossary

Terms this guide could not entirely avoid.

- **Terminal** — the window where you type commands.
- **Claude Code** — Anthropic's assistant that runs in your terminal. marginalia is an add-on for it.
- **Skill** — an ability you add to Claude Code. marginalia installs seven.
- **Repository (repo)** — a project folder, usually shared through GitHub.
- **Clone** — download your own copy of a repository.
- **Corpus** — your collection of published writing, the thing the profile is learned from.
- **Profile** — the description of how you write, kept in `~/.marginalia/styles/`.
- **Genre** — a category of writing with its own register: `papers`, `grants`, `business`, `devdocs`, or any label you invent.
- **Baseline** — the measured numbers from your corpus, used to judge a draft.
- **AI-drift** — the flattening that creeps in when AI helps with writing.
- **Register** — how formal a kind of writing is. A grant and a blog post differ in register.

---

<details>
<summary><strong>Reference: how citation checking works</strong></summary>

**Tier 1 — Existence and accuracy.** Cheap, always run. Searches Crossref,
Semantic Scholar and Google Scholar; verifies author, year, title and venue;
returns a DOI. Catches the most common AI failure: invented citations, and real
ones with the wrong year or first author.

**Tier 2 — Source reputability.** Cheap, default on. Checks whether the venue is
peer-reviewed and indexed, flags likely predatory journals, and flags preprints
cited without a preprint qualifier. A flag means the venue is worth a look, not
that the citation is wrong.

**Tier 3 — Claim–source match.** Expensive, default on. Reads the source's
abstract and, where open-access, key passages of the full text, then compares
what your sentence claims against what the source actually argues. Flags
overgeneralised, directionally wrong and domain-mismatched claims. Deliberately
cautious: it would rather raise a defensible question than stay quiet about a
real mismatch, so expect to dismiss some.

**Tier 4 — Better sources.** Advisory only. Looks for the original empirical
source when you have cited a review, and for newer meta-analyses or replications.
Never blocks anything.

</details>

<details>
<summary><strong>Reference: genres</strong></summary>

`papers`, `grants` and `other` are the starting set, but you can invent any
label. Two ship with rules worth knowing about.

**`devdocs`** — READMEs, code comments, changelogs. Most academic rules do not
transfer. Short sentences and imperatives are correct here rather than voice
loss. What carries over is the AI-slop word list and the structural tics, because
a README goes wrong the same way a grant does.

**`business`** — partner terms, letters of intent, investor memos. The reader is
a counterparty rather than a student, so the characteristic failure is explaining
something they already know.

</details>

<details>
<summary><strong>Reference: how it is built</strong></summary>

A portable content layer holds all the procedure and vocabulary; a runtime layer
wraps it. Today that runtime is Claude Code skills plus a router command. Nothing
in `content/` has to change to add another.

Alongside it is a small `tools/` layer, deliberately code rather than written
instructions. Everything else here is a judgement task, which is what a language
model following a protocol is good at. Counting is not. So two Python scripts
count sentence lengths, punctuation rates and vocabulary density against your
measured baselines. **The tools count and locate; the protocols judge.**

```text
marginalia/
├── content/          # every protocol, and the AI-drift catalogue
│   ├── paths.md      # where profiles and corpus are found
│   └── styles/
│       └── template.md   # the schema; real profiles are never tracked
├── tools/            # two Python counters
├── claude-code/      # the runtime: 7 skills + the /marginalia command
├── examples/         # your corpus, if you keep it here instead
└── tests/fixtures/   # test documents with known problems
```

Contributor guidance is in `CLAUDE.md`.

</details>

<details>
<summary><strong>Reference: known limitations</strong></summary>

- **Suggested word swaps are sometimes ungrammatical in context.** "delve into" becomes "examine into". The safety net is the diff you approve, not the suggestion. Read it.
- **Real but obscure citations can be flagged as invented.** A reference that does not surface in the major databases within the search budget lands in the "no match" bucket. Expect this for older monographs, grey literature and niche venues.
- **Tier 3 over-flags by design.** Calibrated to raise a question rather than to minimise questions.
- **Predatory-venue detection is rough.** A curated list plus open signals.
- **Converted PDFs and Word files lose things.** Figures, complex tables, multi-column layouts.
- **Baselines go stale.** They reflect your corpus as of the last rebuild.
- **A profile is only as good as the corpus.** Feed it AI-assisted drafts and it learns the drift as your voice.
- **English only.**

</details>

---

## Using a different AI model

marginalia runs on Claude Code, but it is not a Claude program. Almost everything
it knows lives in ordinary Markdown files that describe *how* to review writing.
Any model capable of following them can do the job.

Of the twelve procedure files, eleven need no changes at all. One names two
Claude Code tools, and only for citation checking.

**[docs/PORTING.md](docs/PORTING.md)** covers what a replacement runtime has to
provide, how much context each operation needs (measured, not guessed), three
routes to get there, and an honest account of what a local model can and cannot
do. Short version: reviewing and writing port well; citation checking needs
internet access, which is a network problem rather than a model one.

## Where this came from

marginalia was built by one academic to solve his own problem: AI-drift and
weakly-grounded citations creeping into his manuscripts and grant proposals. It
has been in daily use on real papers, grants, presentations and documentation
since mid-2026.

It is shared because people asked for a copy, not because it is a polished
product. Expect rough edges. Issues and pull requests are welcome, and so are
questions from people new to this kind of tool.

## License

MIT. Use it, change it, share it. See `LICENSE`.
