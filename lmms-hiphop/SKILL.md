---
name: lmms-hiphop
description: Compose complete lofi instrumentals in LMMS from plain-language prompts, in five distinct styles - jazzy boom-bap (Nujabes), bossa lofi (nylon guitar, sax), sleepy piano (real upright piano, brushes), Dilla / neo-soul (drunk drums, chopped-sample keys) and 80s city-pop lofi (DX7 EP, slap bass, drum machine). Guides the user through a short brief (style, use, tempo, mood, melody), writes a song plan, builds a real editable LMMS .mmp project with sampled SoundFont instruments, checks every note against the harmony, keeps new songs different from recent ones, renders and masters an MP3, and refines it from feedback. Use this skill whenever the user wants to make, compose, generate or tweak a lofi / chill / study / jazzy / bossa / city-pop / neo-soul / piano beat, or background music for their videos, streams or voiceovers, wants such music made in LMMS, or asks to change a track made this way (slower, less repetitive, new melody, darker) - even if they don't say "LMMS" or "skill". Runs on the lmms-core engine skill. Not for game sound effects or ElevenLabs audio.
---

# LMMS lofi hip-hop

You compose lofi hip-hop as a producer would, and LMMS does the sound. The shared **lmms-core** engine
(`~/.claude/skills/lmms-core`, a sibling skill that must be installed) turns a readable song plan
(`song.json`) into an LMMS project, so your effort goes into the music — chords, melodies, arrangement —
while the file format, levels and wrong-note checks are handled by code that has already been debugged
against LMMS 1.2.2. This skill adds the lofi part: five styles, their grooves and comping patterns
(`scripts/lofi_pack.py`), templates, and the lofi guides in `references/`.

You cannot hear the result. Be upfront about that once, then compensate: the engine checks harmony
and levels, and the user's ears decide the rest. Their feedback is the most valuable input you get.

## Tools (scripts/lofi.py)

Run from the skill folder: `python scripts/lofi.py <command>` (it loads the lofi pack, then lmms-core's
command line, and re-launches itself inside lmms-core's `.venv`).

| command | what it does |
|---|---|
| `doctor` | finds LMMS, its data folder, the user's LMMS working dir, ffmpeg, numpy — run first in a session |
| `setup` | one-time: creates lmms-core's `.venv` with numpy + scipy |
| `new <slug> [--template T]` | makes `<workingdir>/projects/<slug>/song.json` from `assets/examples/T.json`: one per style — `bossa` (68 BPM D, nylon + sax), `sleepy` (62 BPM Db, piano + kalimba), `dilla` (82 BPM Bb, mpc chops + horn), `citypop` (88 BPM E, FM EP + guitar + sax) — and jazzy ones: `slow-and-warm`, `sad-and-rainy`, `voice-bed` (bed mode). Rewrite the content; keep the format |
| `build <song.json>` | writes `<slug>.mmp`, prints the arrangement (section times + chords) and any harmony problems |
| `make <song.json>` | build + render + per-section level report + `<slug>_vN.mp3` at −16 LUFS (~40 s) |
| `stems` / `calibrate` | per-track renders (slow, run in background) → corrects `mix.gains` in song.json |
| `styles` | the five styles with their palettes and pattern vocabulary |
| `history` | recent songs and what they used — read it before designing a new song |
| `measure` | sets level + octave of new catalog instruments / kits (→ lmms-core `assets/levels.json`) |

If `doctor` says NOT READY: missing numpy → `setup`; missing LMMS/ffmpeg → tell the user what to install.
If `lofi.py` says lmms-core is missing, the lmms-core skill has to be installed next to this one.
The sampled instruments are SoundFonts in `<workingdir>/samples/soundfonts/` (FreePats CC0 + GeneralUser GS,
licenses in `soundfonts/licenses/`); if that folder is missing, only `jazzy` works — say so. Adding
instruments, kits or effects and debugging .mmp files is lmms-core's job (its SKILL.md and references).

## Workflow

### 1. Brief — find out what they want (one round)

Pull everything you can from the prompt and from memory (this user's known preferences: slower tempos,
no repetitive loops, and songs that don't all sound alike; tracks often sit behind their voice in videos).
Ask only what's missing, in a single `AskUserQuestion` call of at most 4 questions, with your recommended
option first. Typical questions:

- **Style** (the most important one): jazzy boom-bap / bossa / sleepy piano / Dilla-neo-soul / city-pop —
  recommend one the user hasn't heard recently (`history`)
- **Use**: standalone listening / behind a voice or video (→ `mode: "bed"`) / beat to rap over
- **Tempo feel**: sleepy 68–74 / laid-back 75–82 / head-nod 83–90
- **Mood**: warm & nostalgic / melancholic & rainy / dreamy / jazzy & bright
- **Melody**: none (chords + answers only) / subtle / featured hooks (flute, vibes)
- **Length** or **textures** (vinyl, rain) when they matter

Reference artists ("like Nujabes") answer most of these at once — see `references/music-guide.md` §8.
If the prompt already covers everything, skip the questions and say what you assumed.

### 2. Design the song — write song.json

Run `history` first. Create the project folder with `new <slug> --template <style>` (or write `song.json`
directly into `<workingdir>/projects/<slug>/`) and set `"style"`. Read `references/styles.md` for the chosen
style's palette, patterns, harmony, melody and form idioms; `references/patterns.md` for the lofi-only
patterns; `references/music-guide.md` for general melody writing and the anti-repetition checklist; and
`~/.claude/skills/lmms-core/references/spec-format.md` for every song.json field, chord suffix and the
shared patterns (`references/instruments.md` there lists every instrument id).

Make each song its own: a template is a starting point for the *format*, not the content. The style is
more than a palette — use its patterns, harmony and form, and differ from recent songs (`history`) in key,
tempo, instruments and structure unless the user asks for "like that one". Write your own progressions
(at least verse / hook / bridge), compose the melodies (motif → answer → varied repeat; note names like
`"C#5"` are the least error-prone), and give every section at least two changes from the previous one.
Name sections so the user can talk about them ("Hook 2", "Bridge").

### 3. Build and fix

`python scripts/lofi.py build <song.json>`. The summary shows each section's start time, chords and each
lead's note range (`flute:hook C5-Bb5`) — check it matches what you intended; an unexpected range is
almost always an octave-mark typo in a melody. If it lists harmony problems, each one is a real wrong note (a
melody or bass note outside the chord, or a half-step rub against the held chord): fix the melody note
or the chord, don't `--force`. Warnings about unmeasured instruments or kits mean run `measure` first.
The last line is the variety check: "TOO SIMILAR" means change at least three of the listed dimensions
(unless the user asked for a sequel to that song).

### 4. Render

`python scripts/lofi.py make <song.json>` renders and masters. Read the level report: sections of a full
song should sit within ~4 dB of each other (intro/bridge/outro quieter is intended); "clipping risk" means
lower the busiest tracks in `mix.gains`. Only run `stems` + `calibrate` if you added an instrument or the
user says the balance is off — it takes several minutes.

### 5. Deliver

Send the mp3 (use `SendUserFile` when available, otherwise give the path) and reply with:
- one line: title, BPM, key, length
- a table of sections with timestamps and what changes in each (from the build summary), so they know
  what to listen for and can point at moments
- file locations (project folder, `.mmp` to open in LMMS, mp3)
- one question inviting feedback with timestamps

Keep it short; the music is the deliverable.

### 6. Iterate

Map each comment to concrete edits with `references/feedback-map.md`, change song.json, `make` again
(it writes `_v2.mp3`, `_v3.mp3`… — never overwrite a version the user may want to compare), and say in
one or two lines what changed and where. If they state a lasting preference (tempo, instruments, "never
use X"), save it to memory so the next song starts there.

## Things that matter

- **No chromatic approach notes under sustained chords.** A B under a Bb chord made this user hear "the
  chords are arranged wrong". The engine's bass never does this; keep hand-written melodies clean too.
- **Through-composed, not looped.** Even for long voice beds, write longer songs or several songs.
- **Songs must not all sound alike.** This user's main complaint about the first batch was that every song
  used the same instruments and structure. Vary style, palette, key, tempo and form between songs.
- **Tape wow goes on the master only** (engine default) — wobbling one instrument detunes it.
- **The user may edit the .mmp in LMMS.** If they did, ask before regenerating from song.json, since a
  rebuild replaces their edits; offer to port their change into song.json instead.
- Extending the palette (new presets, kits, effects) or debugging LMMS files: lmms-core
  (`references/instruments.md`, `references/lmms-format.md`). Engine changes go into lmms-core, never into a
  copy here; lofi-only patterns go into `scripts/lofi_pack.py`.
