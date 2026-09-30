---
name: lmms-core
description: Shared LMMS music engine behind the lmms-* genre skills (lmms-hiphop, lmms-gamemusic, lmms-electronic and future ones) - song.json format, harmony checker, instrument catalog (SoundFonts, GM, FM, LMMS synth presets, 808/909 kits), automation (filter sweeps, swells, fades, sidechain pumping), render + master pipeline, seamless game-loop export, level measurement, variety history. Use it directly to set up or diagnose LMMS rendering (doctor, setup), add or measure instruments, SoundFonts and drum kits, debug a generated .mmp project, or build a new lmms-* genre skill for another genre. For composing a song, use the genre skill instead (lmms-hiphop for lofi / bossa / city-pop / neo-soul / sleepy piano, lmms-gamemusic for 16-bit game music loops, lmms-electronic for ambient / deep focus / minimal / downtempo).
---

# lmms-core

The genre-neutral engine the lmms-* skills share. A genre skill supplies styles and patterns (its "pack")
and calls this engine through its own entry script; everything that is not genre identity lives here, so a
fix or a new instrument helps every genre at once. You cannot hear the output — the engine's checks
(harmony, levels, octaves) and the user's ears are the quality gate.

## Layout

| path | what |
|---|---|
| `scripts/engine.py` | song.json → LMMS project: chords, voicing, timeline, harmony checker, mixer, summary |
| `scripts/registry.py` | the plug-in points a genre pack fills (styles, keys / bass / drum patterns, layers, fills) |
| `scripts/common.py` | the shared vocabulary: whole / hold / sync / push / offbeat / arp, piano, `mpc` chops, basic bass lines, fills |
| `scripts/catalog.py` | every instrument, kit and texture (+ `assets/levels.json` from `measure`) |
| `scripts/lmmscli.py` | the commands (doctor, setup, new, build, make, render, master, stems, calibrate, styles, history, measure, audition, textures, loopcheck) |
| `scripts/looper.py` | seamless game loops: 3-pass render, cut, master, OGG export with loop tags, seam check |
| `scripts/chops.py`, `textures.py`, `history.py`, `measure.py`, `sf2info.py`, `lmmsgen.py`, `lmmsenv.py` | chopped samples, texture loops, variety memory, measurement, SoundFont inspector, .mmp writer, environment |
| `.venv` | numpy + scipy (created by `setup`; entry scripts re-launch themselves in it) |

Sounds live in the user's LMMS working dir: `<workingdir>/samples/soundfonts/` (FreePats CC0 + GeneralUser GS,
licences in `licenses/`) and generated textures in `samples/lofi/`. Projects go to `<workingdir>/projects/<slug>/`;
the shared variety history is `projects/.lmms-history.json`.

## Running commands

Always through a genre skill's entry script, which loads its pack first:
`python ~/.claude/skills/lmms-hiphop/scripts/lofi.py <command>`. Genre-free commands (`doctor`, `setup`,
`measure`, `history`, `audition`, `textures`) also work as `python scripts/lmmscli.py <command>` from here.

- **Not rendering / NOT READY** → `doctor`. Missing numpy → `setup`. Missing LMMS or ffmpeg → tell the user what
  to install. No SoundFonts → only the Zyn/sample instruments work; say so.
- **Add an instrument or kit** → find the preset with `python scripts/sf2info.py <file.sf2> [bank program]`,
  add a catalog entry (see references/instruments.md), run `measure --instruments <id>` or `--kits <kit>`,
  then use it. Ask before downloading any new sound library, check its licence allows published music, and
  store its licence under `soundfonts/licenses/`.
- **Debug a .mmp** → references/lmms-format.md (verified node names, render quirks, what LMMS ignores silently).
- **New genre skill** → references/genre-packs.md (pack API, style-vs-skill rule, checklist). Keep genre
  identity (grooves, styles, brief, templates) in the genre skill; put anything reusable here.

## References

- `references/spec-format.md` — the song.json format and the common pattern vocabulary (read before writing a song)
- `references/instruments.md` — catalog ids by role, kits, textures, licences, measuring
- `references/genre-packs.md` — building a genre skill on this engine
- `references/lmms-format.md` — LMMS 1.2.2 file-format and rendering internals

## Changing the engine safely

Songs are reproducible: the same song.json must build the same .mmp. Before and after an engine change,
rebuild the existing projects (`build` for each `<workingdir>/projects/*/song.json`) and compare the .mmp files —
any difference must be one you intended. Keep genre-specific behaviour out of engine.py; add a registry hook
instead.
