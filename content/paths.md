# Path resolution

Where marginalia looks for the two things that belong to the *user* rather than
to the tool: their style profiles and their corpus.

Every other protocol writes these paths in their short form — `content/styles/base.md`,
`examples/papers/` — because that is what they were called when there was only one
place they could be. **Those are names, not locations.** Resolve them here.

## The two roots

| Short form used in protocols | Resolve as |
|---|---|
| `content/styles/…` | `<STYLES_DIR>/…` |
| `examples/…` | `<CORPUS_DIR>/…` |

## Resolution order

Take the first that exists, checked in this order:

1. **`$MARGINALIA_HOME`**, if set. Then `STYLES_DIR = $MARGINALIA_HOME/styles`
   and `CORPUS_DIR = $MARGINALIA_HOME/examples`. An explicit override always wins,
   even if the directory is empty — a user who sets it means it.
2. **`~/.marginalia/`**, if that directory exists. Then `STYLES_DIR =
   ~/.marginalia/styles` and `CORPUS_DIR = ~/.marginalia/examples`.
3. **The repo itself.** `STYLES_DIR = <repo>/content/styles` and `CORPUS_DIR =
   <repo>/examples`, where `<repo>` is the marginalia checkout containing
   `content/` and `tools/`. This is the original layout and remains supported.

Resolve once at the start of a run and use the same answer throughout it. Do not
resolve `base.md` under one root and the overlay under another: a profile is a
set, and mixing roots would silently blend two people's voices.

**Report which root was used** in the run's header, next to which style files
loaded. A user who thinks they are editing a profile that the run is not reading
has no way to discover that except by being told.

## Why this exists

The tool is shared; the profile is not. A style profile contains verbatim
passages of its author's writing, including unpublished work, so it cannot live
inside a repo that other people clone. Keeping the profile outside the checkout
makes a public distribution safe by construction rather than by `.gitignore`,
and it means a user can pull an update to the tool without touching their voice.

Order 3 exists because the original layout put both inside the repo, and an
existing checkout must keep working unchanged. It is a fallback, not the
recommended arrangement.

## Migrating an existing setup

Moving from order 3 to order 2 is a move plus a baseline regeneration:

```bash
mkdir -p ~/.marginalia
mv <repo>/content/styles   ~/.marginalia/styles
mv <repo>/examples         ~/.marginalia/examples
python3 <repo>/tools/prose_metrics.py --emit-baseline
```

Nothing else changes. The next run finds `~/.marginalia/` at order 2 and reads
the same profiles from their new home. Keep `<repo>/content/styles/.gitkeep` and
`<repo>/examples/*/.gitkeep` so the directory structure survives in the checkout.

## Cold start

If `STYLES_DIR` resolves but holds no `base.md`, there is no profile yet. That is
the expected state of a fresh install, not an error condition to work around:

- `review` runs its AI-drift and structural dimensions and skips the voice
  comparison, noting `no base style available` in the header.
- `write` cannot apply a voice it does not have. It stops and says so.
- `extract-style` is the way out. Point the user at `CORPUS_DIR`, then
  `--emit-baseline`, then `calibrate`.

Never invent a profile to fill the gap, and never fall back to a generic style
guide. Measuring an author against a generic rulebook is the failure marginalia
exists to prevent, so doing it silently would be worse than doing nothing.

## Baselines

`baselines.json` lives in `STYLES_DIR` alongside the profiles, because it is
measured from that user's corpus and is meaningless against anyone else's.
`tools/prose_metrics.py` resolves it by the same order above, and
`--emit-baseline` writes it back to the same place.

A `baselines.json` from a different corpus is worse than none: Dimension E would
report `baseline-delta` findings comparing one person's prose to another person's
voice, with nothing on the surface to show it. Never ship one, and never copy one
between users.
