---
name: lmms-electronic
description: Compose complete electronic tracks in LMMS from plain-language prompts, in four styles - ambient (beatless drones, evolving pads, bells, long echoes), deep focus (a soft steady pulse, repeating plucks, warm pads, slow harmony - music to work or study to), minimal / deep (four-on-the-floor 909, rolling bass, echoing chord stabs, pumping pads, parts trading places every 8 bars) and downtempo (swung broken beats on 808s, electric piano, round synth bass, bell / flute / kalimba hooks). Writes a real editable LMMS project with LMMS's own synths (nothing to license) and real 808 / 909 kits, moves filters, swells, fades and sidechain-style pumping over time with automation, checks every note against the harmony and flags stretches that would sound like a loop, keeps new tracks different from recent ones, renders and masters an MP3 of 3-6 minutes, and refines it from feedback. Use this skill whenever the user wants to make, compose, generate or tweak ambient, chill electronic, deep focus / study / work / concentration music, minimal techno, deep house, downtempo, trip-hop, chillout, electronica or Eno / Tycho / Bonobo-style music - or background music for streams and videos in that vein - even if they don't mention LMMS. Runs on the lmms-core engine skill. Not for lofi hip-hop (lmms-hiphop) or game loops (lmms-gamemusic).
---

# LMMS electronic: ambient, deep focus, minimal, downtempo

You produce electronic music the way it is made in a DAW: a few sounds, a groove, and slow change over
minutes. The shared **lmms-core** engine (`~/.claude/skills/lmms-core`, a sibling skill that must be installed)
turns a readable song plan (`song.json`) into an LMMS project; this skill adds the electronic part - four styles,
their patterns (`scripts/electro_pack.py`), four templates and the guides in `references/`.

In this genre a few sounds and a groove carry minutes of music, so the arrangement decides whether it lives or
sounds like a loop. Plan it in 8-bar blocks: something a listener notices changes every 8 bars (a part in or out,
a pattern swap, a chord, a melody), and per-section `move` (filter sweeps, swells, fades) and `pump`
(sidechain-style ducking) - LMMS automation - make those changes smooth. Movement alone isn't enough: the user
heard filter sweeps over an unchanged 16-bar loop as repetitive.

You cannot hear the result. Say so once, then compensate: the engine checks harmony and levels, and the user's
ears decide the rest - synth sounds especially. Their feedback is the most valuable input you get.

## Tools (scripts/electronic.py)

Run from this skill's folder: `python scripts/electronic.py <command>` (it loads the electronic pack, then
lmms-core's command line, and re-launches itself inside lmms-core's `.venv`).

| command | what it does |
|---|---|
| `doctor` | finds LMMS, its data folder, the LMMS working dir, ffmpeg, numpy, SoundFonts — run first in a session |
| `setup` | one-time: creates lmms-core's `.venv` with numpy + scipy |
| `styles` | the four styles with their palettes and pattern vocabulary |
| `history` | recent songs (all lmms-* skills) and what they used — read it before designing a new song |
| `new <slug> --template T` | makes `<workingdir>/projects/<slug>/song.json` from `assets/examples/T.json`: `ambient` (68 BPM E, 4:56), `focus` (86 BPM F, 3:43), `minimal` (122 BPM A minor, 3:40), `downtempo` (90 BPM G minor, 3:54). Rewrite the content; keep the format |
| `build <song.json>` | writes `<slug>.mmp`, prints the arrangement (times, chords, lead ranges, moves), harmony problems and loop warnings |
| `make <song.json>` | build + render + per-section level report + `<slug>_vN.mp3` at −16 LUFS |
| `stems` / `calibrate` | per-track renders (slow, background) → corrects `mix.gains` in song.json |
| `measure` | sets level + octave of new catalog instruments / kits (lmms-core) |

If `doctor` says NOT READY: missing numpy → `setup`; missing LMMS / ffmpeg → tell the user what to install.

## Workflow

### 1. Brief — one round

Pull what you can from the prompt and from memory (this user: tracks of **3–6 minutes**, songs that don't all
sound alike, license-safe sounds only; music often goes behind their videos or is listened to while working).
Ask only what's missing, in one `AskUserQuestion` call (≤ 4 questions, recommended option first):
- **Style**: ambient / deep focus / minimal / downtempo — recommend one the user hasn't heard recently (`history`)
- **Use**: listening while working / background for a video or stream (quieter leads: `"mode": "bed"`) /
  foreground listening
- **Energy / tempo** within the style, and **mood** (warm, melancholic, nocturnal, hopeful, cold / spacey)
- **Melody**: none (texture only) / subtle / a featured hook — and **length** if not given (default ~4 min)

If the prompt already covers everything, skip the questions and say what you assumed.

### 2. Design — write song.json

Run `history`, then `new <slug> --template <style>` and rewrite it. Read:
- `references/styles.md` — each style's palette, sounds, patterns, harmony and tone
- `references/arrangement.md` — how to build 3–6 minutes: section plans per style, layering, movement recipes
- `~/.claude/skills/lmms-core/references/spec-format.md` — every song.json field, chord suffix and the
  `move` / `pump` syntax

Length: bars × 240 / BPM seconds. 4 minutes is ~70 bars at 70 BPM, ~86 at 86, ~122 at 122. Write 8-bar
sections (4 for intros, drops and transitions) with progressions that divide them; a 16-bar section only when
its second half changes something itself (a lead entering at bar 8).

Make each track its own: a template shows the format, not the content. Change key, tempo, sounds, progression,
sequence patterns and the shape of the arc; differ from recent songs in at least three dimensions (`history`).
Then check the pacing against the clock (`arrangement.md`, "Time per block"):
- **something a listener notices changes every 8 bars** (~16 s at 122 BPM, ~22 s at 86): a part in or out,
  another keys / bass / drum pattern, a chord move, a melody entrance or answer, a drop. The patterns already
  add fills and pickups on every 4th and 8th bar — that is punctuation, not a change.
- **the opening matches the energy**: a track that starts with drums has its groove (kick, bass and one more
  part) within 4 bars; a track that fades in from a pad brings the pulse in within ~20 s. No 16-bar kick-only
  intro unless the user wants a DJ tool.

### 3. Build and fix

`python scripts/electronic.py build <song.json>`. Check lead ranges in the summary (an unexpected range is an
octave typo) and the `moves:` lines (is the arc what you meant?). Fix every harmony problem at the note or the
chord — don't `--force`. "TOO SIMILAR" means change at least three of the listed dimensions. A **loop
warning** ("the same 8-bar loop for 42 s") marks a stretch a listener will hear as repetitive: split the
section and change something in the second half — a filter or level move doesn't clear it.

### 4. Render

`python scripts/electronic.py make <song.json>` (a few minutes — run it in the background). Read the level
report: sections are *meant* to differ here (fades, breakdowns), but a main section more than ~6 dB under the
others usually means a layer is missing or a filter never opened. "clipping risk" → lower the busiest tracks in
`mix.gains`.

### 5. Deliver

Send the mp3 (`SendUserFile` when available, otherwise the path) and reply briefly with:
- one line: title, style, BPM, key, length
- a table of sections with timestamps and what changes in each (what enters, what opens, where it peaks)
- file locations (project folder, `.mmp` to open in LMMS, mp3)
- one question inviting feedback with timestamps — for sounds, offer alternatives by name ("the pad could be
  warmer: `soft_pad` or `analog_pad` instead of `dream_pad`")

### 6. Iterate

Map comments to edits with `references/feedback-map.md`, change song.json, `make` again (it writes `_v2.mp3`,
`_v3.mp3`... — never overwrite a version the user may compare), and say in one or two lines what changed and
where. Save lasting preferences (favourite pads, tempo, "no bells") to memory.

## Things that matter

- **Change every 8 bars, movement in between.** Parts entering and leaving, pattern swaps, chord moves and
  melody entrances are the arrangement; filters, swells and pumping connect them. `arrangement.md` has a plan
  per style in 8-bar blocks — use it as a starting point, not a template to copy.
- **Deep focus stays out of the way without standing still.** No sudden hits, no loud fills, no busy lead, a
  steady pulse — but the sequence figure, the layers and the chords still change every 8 bars, and a soft melody
  comes and goes. A two-chord loop under the whole track is too static even for background music.
- **Minimal is built from few elements** — one or two chords for minutes is fine — but they trade places every
  8 bars: stabs in, clap in, bass pattern swap, pad in, a 4-bar drop. Start with the groove, not a DJ intro.
- **Sounds are synths the user hasn't heard yet.** Their levels and octaves are measured, but taste isn't —
  when a sound choice is a guess, say which one and offer alternatives.
- **Only license-safe sounds**: LMMS's own synths and factory samples, FreePats (CC0) and GeneralUser GS. Don't
  add samples of unclear origin.
- **The user may edit the .mmp in LMMS.** Ask before regenerating from song.json (a rebuild replaces their edits);
  offer to port their change into song.json instead.
- New sounds, kits, effects or engine fixes belong in lmms-core; electronic-only patterns go into
  `scripts/electro_pack.py`.
