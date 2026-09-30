# Building a genre skill on lmms-core

A genre skill (lmms-hiphop is the reference) is a thin skill folder next to lmms-core:

```
~/.claude/skills/lmms-<genre>/
  SKILL.md                    brief questions, workflow, what matters in this genre
  scripts/<genre>.py          entry script (copy lmms-hiphop/scripts/lofi.py, change the pack import)
  scripts/<genre>_pack.py     registers styles + patterns with lmms-core's registry
  references/styles.md        each style's palette, patterns, harmony, melody and form idioms
  references/feedback-map.md  listener phrases -> song.json changes for this genre
  assets/examples/*.json      one starter song.json per style (used by `new --template`)
```

Everything else — song.json format, harmony checker, voicing, mixer, render/master, chops, measure, variety
history, the catalog and SoundFonts — comes from lmms-core. Fix engine bugs in lmms-core, never in a copy.

## Style or skill?

Add a **style** to an existing genre skill when the new genre shares its brief and song shape (lounge jazz or
lofi house → lmms-hiphop). Make a **new skill** when the brief or the deliverable differs: game music (seamless
loops, stingers, per-level variants), video underscore (cues timed to a video), chiptune (writing for a few
chip voices), or when its description would otherwise dilute the existing skill's triggering.

## The pack module

```python
from pathlib import Path
import registry as R

EXAMPLES = Path(__file__).resolve().parent.parent / "assets" / "examples"
PROG = "<genre>.py"                  # name shown in -h
DEFAULT_TEMPLATE = "<an example>"    # for `new` without --template

R.genre("<genre>", "<default style>", drums="<default drum pattern>")   # section defaults: keys, bass, drums

R.style("<id>", title=..., about=..., bpm=(lo, hi), swing=0, humanize=1, snare_lag=0, wow=0.0002,
        palette=dict(keys=..., bass=..., pad=..., kit=..., textures=[...]), leads=[...],
        keys=[...], bass=[...], drums=[...],            # the vocabulary `styles` prints for this style
        tone=dict(...), feel=dict(kick=(lag, jitter), ...),
        loop_max_s=30)                                  # optional: `build` warns where one 4/8-bar loop plays
                                                        # longer (seconds; omit = no check)

R.keys("name", [(step, len16, vel, plays_next_chord), ...], strum=1)          # one bar
R.keys("name2", [[bar A hits], [bar B hits]], strum=1)                        # rotating bar variants
R.keys_fn("name3", fn)            # fn(song, b, track, rng, inst, pick) for anything procedural
R.bass_fig("name", [(step, len_ticks, "r" | "5" | "8" | "last", vel), ...])  # resolved per chord
R.bass_fn("name", fn)             # fn(song, bc)  bc: BassCtx (v(), last_note(seg), nxt, ant)
R.drums("name", fn)               # fn(dc)  dc: DrumCtx (hit(), V(), J(), hats8(), out, bis, bars, sec, song)
R.layer("flag", fn)               # adds hits when a section sets "flag": true
R.fill("name", fn)                # replaces / adds hits on a section's last bar
R.chords(major="triad", minor_numeral={"": "mtriad"}, alias={"7": "dom7"}, rub_min_overlap=24)
                                  # optional: what bare chord symbols mean + how long a half-step clash must
                                  # last to count as a rub (ticks; default 12 = a 16th)
```

Rules that keep songs correct:
- Only generate notes from the chord's voicing, root, fifth and `chord.scale`; use `song.approach(seg,
  target)` for passing notes and `song.rubs(n, seg)` to reject half-step rubs. The checker catches the rest.
- Drum functions append `(part, tick, length, velocity)`; unknown parts fall back through
  `registry.PART_FALLBACK` or are dropped, so a groove can use `clap` even on kits without one.
- Use the rng you are given (dc.rng / rng) and nothing else, so builds are reproducible.
- Return `False` from a drum function to make the bar silent (skips layers and fills).
- New instruments or kits: add them to catalog.py (or the pack) and run `measure`.

## Checklist for a new genre skill
1. Decide the styles (2-5) and, for each, what makes it itself: palette, grooves, harmony, form, tone.
2. Write the pack; `python scripts/<genre>.py styles` must list them.
3. Write one example song.json per style; `build` must report 0 problems; `make` and listen for balance.
4. SKILL.md: a short brief (≤ 4 questions, style first), the workflow (design → build → make → deliver →
   iterate, as in lmms-hiphop), and pointers to `../lmms-core/references/spec-format.md` and your styles.md.
5. Record new songs in the shared variety history automatically (build does it) and keep the SKILL.md
   description specific so it does not trigger for the other genres.
