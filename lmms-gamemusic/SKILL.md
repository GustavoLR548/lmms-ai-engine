---
name: lmms-gamemusic
description: Compose original 16-bit video game music in LMMS and export it as seamless, game-ready loops - SNES-style sampled soundtracks (orchestral strings, harp, horns, flute, timpani - JRPG / Zelda / Mana / Chrono feel) or Genesis / DOS FM synthesis (OPL2 FM bass, brassy FM leads, 16th arpeggios, punchy drums). Covers every in-game context - title screen, overworld, town, dungeon, battle, boss, castle, shop / menu, sad cutscene, action stage, racing / shmup - from a plain-language prompt. Writes a real editable LMMS project, checks every note against the harmony, renders the loop three times so reverb tails wrap correctly, and delivers OGG loops with an optional play-once intro, LOOPSTART/LOOPLENGTH tags, a loop-points JSON, a measured seam check and engine notes (Godot, Unity, GameMaker, RPG Maker). Reads and updates the game project's SOUND.md (music palette, loudness, file layout, audio log). Use this skill whenever the user wants music for a game - a level / stage / area / battle / boss theme, background music (BGM), a looping soundtrack, retro / 16-bit / SNES / Super Nintendo / Genesis / Mega Drive / JRPG / FM music - or wants such a track changed, even if they never mention LMMS or loops. Runs on the lmms-core engine skill. Not for sound effects or voice (sound-director) or lofi beats (lmms-hiphop).
---

# LMMS 16-bit game music

You write game soundtracks the way a 90s console composer did: short, memorable themes built to loop for
minutes without wearing thin. The shared **lmms-core** engine (`~/.claude/skills/lmms-core`, a sibling
skill that must be installed) turns a readable song plan (`song.json`) into an LMMS project and, for a
looping song, renders and cuts the loop, masters it and verifies the seam. Your effort goes into the music -
motif, harmony, arrangement, how the end leads back to the start. This skill adds the game part: two console
styles, their patterns (`scripts/game_pack.py`), two templates and the guides in `references/`.

You cannot hear the result. Say so once, then compensate: the engine checks every note and the seam, the
user's ears decide the rest, and their feedback is the most valuable input you get.

## Tools (scripts/gamemusic.py)

Run from this skill's folder: `python scripts/gamemusic.py <command>` (it loads the game pack, then
lmms-core's command line, and re-launches itself inside lmms-core's `.venv`).

| command | what it does |
|---|---|
| `doctor` | finds LMMS, its data folder, the LMMS working dir, ffmpeg, numpy, SoundFonts — run first in a session |
| `setup` | one-time: creates lmms-core's `.venv` with numpy + scipy |
| `styles` | the two styles (`snes`, `fm`) with their palettes and pattern vocabulary |
| `history` | recent songs (all lmms-* skills) and what they used — read it before designing a new song |
| `new <slug> --template T` | makes `<workingdir>/projects/<slug>/song.json` from `assets/examples/T.json`: `snes-town` (SNES town, 104 BPM F, whole-song loop) or `fm-stage` (Genesis action stage, 152 BPM E minor, 4-bar intro + loop). Rewrite the content; keep the format |
| `build <song.json>` | writes `<slug>.mmp`, prints the arrangement (times, chords, lead ranges) and any harmony problems |
| `make <song.json> [--lufs L] [--to PATH]` | for a looping song: build, render, cut, master and export the loop files (below); `--to` also copies the game-ready file(s) to the game project |
| `loopcheck <file> [--bars N --bpm B]` | seam / length / loudness check of any loop file |
| `measure` | sets level + octave of new catalog instruments (lmms-core) |

If `doctor` says NOT READY: missing numpy → `setup`; missing LMMS / ffmpeg / SoundFonts → tell the user what
to install. If the script says lmms-core is missing, that skill has to be installed next to this one.

## Workflow

### 1. Brief — what the music is for

Everything in game music follows from **where it plays**: title, overworld, town, dungeon, battle, boss,
menu, cutscene... Pull what you can from the prompt, then look for the game's audio guide: if the user names a
game project (or you are inside one), read its `SOUND.md` — the **Music** section (genre, instrument palette,
*Avoid* line, tempo range, key tendency, the context → file table) and the **Technical Specs** Music row
(format, loudness target). A `DESIGN.md` art direction helps choose the style. SOUND.md's rules win over your
defaults: its palette and Avoid line constrain the instruments, its loudness target becomes `--lufs`, its file
table / layout gives the `--to` path.

Ask only what is still missing, in one `AskUserQuestion` call (≤ 4 questions, recommended option first):
- **Context / mood** — the most important (see `references/moods.md`)
- **Sound**: `snes` (sampled orchestra, RPG / adventure) or `fm` (Genesis / DOS FM, action) — recommend from
  the game's look and genre
- **Intro**: loop the whole thing, or a short play-once intro (fanfare / count-in) then the loop
- **Length** of the loop (default 40–90 s: 16–32 bars) and a reference game ("like Chrono Trigger's...")

If the prompt already answers these, skip the questions and state what you assumed.

### 2. Design — write song.json

Run `history`, then `new <slug> --template snes-town` (or `fm-stage`) and rewrite it. Read:
- `references/moods.md` — the recipe for the context: tempo, harmony, patterns, instruments, form
- `references/styles.md` — the two sounds, every instrument and kit that fits them, the game patterns
- `~/.claude/skills/lmms-core/references/spec-format.md` — every song.json field and chord suffix

Game harmony here is **triad-based**: a bare `"I"` is a major triad, `"vi"` a minor triad, `"V7"` a plain
dominant 7th, `"Isus4"`, `"viio"`, `"I5"` (power chord), `"Iaug"` exist; the jazz qualities still work by
name (`"IVmaj7"`, `"ii9"`, `"V13"`). Keys are written as the MAJOR key: an A-minor theme is `"key": "C"`
with vi-centred progressions (`"vi IV V vi"` = Am F G Am), its harmonic-minor dominant is `"III7"` (E7).

Make the loop (`"loop": true`, or `"loop": {"from": "<first looping section>"}` for a play-once intro):

- **It will be heard 20 times in a row.** Give it at least two contrasting parts inside the loop (A and B:
  new chords, new lead instrument or register, different groove) and a varied return of A. One 8-bar
  phrase repeated is a ringtone, not a theme.
- **The last bar leads back to the first.** End on a dominant or a step into the loop's first chord (V, V7,
  III7 in minor, bVII, or IV), with a pickup in the melody toward its first note and a drum `fill`
  (`build`, `pickup`, `toms`). Never write an ending: no final tonic chord held out, no fade, no ritardando,
  no crash on the last beat.
- **A pickup into the loop start** belongs at the end of the last section (and at the end of the intro), not
  before the first bar.
- The first looping section may start with `"crash": true` — the loop wraps into it every time.
- Reverb and echo tails need no space: the engine renders three passes, so the tails of the end wrap into
  the start exactly as they would in continuous playback.
- Not in loops: `keys: "mpc"` and textures (vinyl, rain, tape) — those are lofi tools.

Write melodies as a game composer would: a 1–2 bar motif with a clear rhythm, answered, repeated with a
change, within about an octave and a half; the hook should be hummable after one loop. Note names (`"C#5"`)
are the least error-prone. Fast scalar runs may pass through non-chord tones (anything an 8th or shorter);
longer notes should be chord tones or a 6th / 9th.

### 3. Build and fix

`python scripts/gamemusic.py build <song.json>`. Check each lead's range in the summary (an unexpected range
is an octave typo) and fix every harmony problem at the note or the chord — never `--force`. A "TOO SIMILAR"
variety verdict means change at least three of the listed dimensions.

### 4. Render the loop

`python scripts/gamemusic.py make <song.json> --lufs <SOUND.md target, default -16> [--to <game path>.ogg]`
(a few minutes; run it in the background). It writes, next to song.json:

| file | use |
|---|---|
| `<slug>_loop.ogg` | the loop body — loop the whole file |
| `<slug>_intro.ogg` | (with an intro) play once, then start the loop file |
| `<slug>_full.ogg` | (with an intro) intro + loop in one file, tagged `LOOPSTART` / `LOOPLENGTH` in samples |
| `<slug>_loop.json` | loop points (seconds + samples), loudness, seam check, engine notes |
| `<slug>_preview_vN.mp3` | for listening: intro + the loop twice + a fade — the seam is audible here if there is one |

With `--to assets/audio/music/boss.ogg` the game gets `boss.ogg` (the full file with an intro, else the loop),
plus `boss_intro.ogg` / `boss_loop.ogg` for intro songs and `boss.loop.json`.

Read the end of the output. `seam: ... -> SEAMLESS` means the wrap is sample-continuous, has no click and no
level jump compared with continuous playback, and the loop is the exact bar length. Anything else: read
`references/feedback-map.md` (loop problems) before rendering again. Sections should sit within ~4 dB of each
other in the level report; the loop is mastered to the target loudness with a true peak at or below −1 dBFS.

### 5. Deliver

Send the preview mp3 (`SendUserFile` when available, otherwise the path) and reply briefly with:
- one line: title, style, BPM, key, loop length (bars / seconds), intro length if any
- a table of the loop's sections with timestamps and what changes, so they know what to listen for
- the game files and where they went, and how to loop them in their engine (from `_loop.json`)
- the seam result, in plain words
- one question inviting feedback with timestamps

If the game has a SOUND.md, append one row to its **Audio Log** table — date, asset path, `LMMS + lmms-gamemusic
(<style>)`, and notes (context, BPM, key, loop length, intro, LUFS). That is a factual record; do it without
asking. If the track introduced something SOUND.md does not have yet (an instrument outside its palette, a new
file in its context table), propose the exact change and wait for a yes before editing the style sections.

### 6. Iterate

Map each comment to concrete edits with `references/feedback-map.md`, change song.json, `make` again (new
preview version each time; the game files are overwritten, so say so if `--to` was used), and say in one or two
lines what changed and where. Save lasting preferences to memory.

## Things that matter

- **Music sits under the game.** Busy mids and loud one-off hits compete with sound effects. For gameplay
  loops keep accompaniment patterns steady and let the melody rest now and then; `"mode": "bed"` (leads −5 dB,
  a dip at 2.5 kHz, softer hats) helps under dialogue-heavy scenes. Menus, title and victory can be fuller.
- **Only license-safe sounds.** Every instrument comes from FreePats (CC0) or GeneralUser GS (free for any
  use) SoundFonts, or LMMS's built-in synths — the tracks can ship in a commercial game. Don't add samples of
  unclear origin.
- **Songs must not all sound alike.** Different contexts need different keys, tempos, palettes and grooves;
  check `history`, especially when writing several tracks for one game (they should still share the game's
  palette from SOUND.md).
- **The user may edit the .mmp in LMMS.** If they did, ask before regenerating from song.json (a rebuild
  replaces their edits); offer to port the change into song.json.
- New instruments, kits, effects or engine fixes belong in lmms-core; game-only patterns go into
  `scripts/game_pack.py`.
