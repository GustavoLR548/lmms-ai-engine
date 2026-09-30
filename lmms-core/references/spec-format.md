# song.json — the song spec (all lmms-* genre skills)

One JSON file per song, living in its project folder (`<lmms workingdir>/projects/<slug>/song.json`).
The engine turns it into `<slug>.mmp`. Start from the genre skill's `assets/examples/*.json` (`new <slug>
--template <name>`) and change everything that makes a song itself (key, tempo, progressions, melodies, form,
palette). The genre skill's own references list its styles and the patterns it adds on top of the common
vocabulary below.

```jsonc
{
  "title": "Slow And Warm",          // shown in LMMS project notes
  "slug": "slow-and-warm",           // file names: <slug>.mmp, <slug>_vN.mp3
  "style": "jazzy",                  // one of the genre pack's styles (`styles` lists them) - supplies defaults
                                     // for swing, humanize, snare_lag, wow, palette, tone and feel
  "bpm": 74,                         // within the style's range
  "key": "Eb",                       // tonic of the MAJOR key used for Roman numerals + melody degrees
                                     // (a "C minor" song = key "Eb" with vi-centred progressions)
  "swing": 3,                        // ticks (of 12 per 16th) that off-16ths are late: 0 straight, 3 ≈ 62 %, 4-5 = drunk
  "humanize": 1,                     // +/- ticks of random timing on hats/keys
  "snare_lag": 3,                    // snare/sidestick laid back this many ticks
  "seed": 1,                         // change for a different humanisation, same notes
  "mode": "listen",                  // "listen" or "bed" (behind a voice: leads -5 dB, 2.5 kHz dip, softer hats)
  "loop_max_s": 30,                  // optional: warn where one 4/8-bar loop plays longer (default: the style's)
  "loop": {"from": "A"},             // optional: a game loop (see Loops) - true loops the whole song
  "wow": 0.0002,                     // tape wobble on the master (0 = off; 0.0002 ≈ +/-4 cents; >0.0004 sounds seasick)
  "palette": {                       // merged over the style's palette - only list what you change
    "keys": "rhodes",                // catalog ids (references/instruments.md) - also sets the chord voicing range
    "keys2": "jazz_guitar",          // optional second comping instrument (sections with "keys2": pattern)
    "sample": "chorus_ep",           // optional: instrument recorded for "mpc" chops (default: keys)
    "bass": "warm_sine",
    "pad": "soft_saw_pad",           // any keys/pad id (e.g. drawbar_organ)
    "kit": "dusty",                  // dusty | brushes | latin | drum_machine | dilla
    "textures": ["vinyl"]            // vinyl, rain, tape; or {"vinyl": 0, "rain": -3} (dB offsets)
  },
  "feel": {"kick": [4, 3], "bass": [6, 2]},   // optional per-part timing [lag, jitter] in ticks (12 = a 16th);
                                              // parts: kick snare clap hat open_hat ... bass keys pad lead
  "instruments": { "vibes": {"vol": 110} },   // optional per-song catalog overrides
  "progressions": { "verse": ["ii9", "V13", "Imaj9", "vi11"], "hook": ["IVmaj9", "III7alt", "vi9", "ii9 V13"] },
  "melodies": { "hook": [[0, 0, 3, "1"], [0, 3, 3, "3"], [0, 6, 4, "5"]] },
  "sections": [ { "name": "Verse 1", "bars": 8, "prog": "verse", "keys": "hold", "bass": "kick_lock", "drums": "..." } ],
  "mix": { "gains": { "Vibes": -2.0 } }       // dB per track label; written by `calibrate`, editable by hand
}
```

## Chords

Each progression entry is one bar. Two chords in a bar: `"ii9 V13"` (or `["ii9", "V13"]`) — split evenly.
Symbols are Roman numerals relative to `key` (so changing `key` transposes the whole song) or absolute
names (`"Fm9"`, `"Bb13"`). Case sets the default quality: `ii` → m9, `IV` → maj9.

| suffix | quality | sound | voiced as (above the bass root) |
|---|---|---|---|
| (none, upper) / `maj9` | maj9 | warm, the default | 3 5 7 9 |
| `maj7` | maj7 | plainer | 1 3 5 7 |
| `6/9` | 6/9 | open, sunny | 3 5 6 9 |
| (none, lower) / `9` on lower / `m9` | m9 | mellow minor | b3 5 b7 9 |
| `11` on lower / `m11` | m11 | airy, suspended minor | b3 4 5 b7 |
| `7` on lower / `m7` | m7 | plain minor | 1 b3 5 b7 |
| `m6` / `6` on lower | m6 | dark, filmic | b3 5 6 9 |
| `7`, `9` (upper) | dom9 | bluesy | 3 5 b7 9 |
| `13` | dom13 | the classic jazz V | 3 b7 9 13 |
| `7alt` | 7(b9 b13) | tense, resolves down a 5th / half-step | 3 b7 b9 b13 |
| `13sus` / `sus` | 13sus4 | floating V | 4 b7 9 13 |
| `9sus` | 9sus4 | softer sus | 4 5 b7 9 |
| `m7b5` / `ø` | half-dim | sad ii of minor | 1 b3 b5 b7 |
| `dim7` | dim7 | passing | 1 b3 b5 bb7 |
| `triad` | major triad | plain, bright (game default) | 1 3 5 + one doubled |
| `mtriad` | minor triad | plain minor (game default for lower case) | 1 b3 5 + one doubled |
| `dom7` | dominant 7th | plain V7 | 1 3 5 b7 |
| `sus4` / `sus2` | suspended triads | open, modal | 1 4 5 / 1 2 5 + one doubled |
| `dim` / `o` | diminished triad | tense passing chord | 1 b3 b5 + one doubled |
| `aug` / `+` | augmented triad | mysterious, rising | 1 3 #5 + one doubled |
| `5` | power chord | rock / boss | 1 5 (doubled) |

What a bare symbol means depends on the genre pack (`registry.chords`): lofi keeps the jazz defaults above
(`I` = maj9, `vi` = m9, `7` = dom9); lmms-gamemusic makes `I` a major triad, `vi` a minor triad, `m` a minor
triad and `7` a plain dominant 7th. Triads are voiced with one chord tone doubled — whichever voice-leads best.

Accidentals before numerals: `bVIImaj9`, `bIIImaj9`, `#ivm7b5`, `bVI9`.
The engine voice-leads every chord automatically (4 notes in the chord instrument's range — catalog
`voicing`, default E3-D5 — smallest movement, no low mud); you only choose the chord. Chord names are
spelled with sharps in sharp keys (G D A E B F#), flats otherwise.

## Melodies

A melody is a list of `[bar, step, length, note]`:
- `bar` — bar index inside the section (0-based; shift with the lead's `"at"`)
- `step` — 16th within the bar (0-15; odd steps get swung)
- `length` — in 16ths
- `note` — a note name (`"C#5"`, the least error-prone), a scale degree string relative to `key`
  (`"1" "2" "b3" "3" "4" "#4" "5" "b6" "6" "b7" "7"`, `"9"` = 2 an octave up; `'` raises and `,` lowers an
  octave), or an integer (semitones from `"1"`). Degree `"1"` is the tonic between F#4 and F5 (Eb → Eb5, A → A4).

Degrees are relative to the MAJOR key, so a C-minor melody in key Eb uses `"6,"` for C, `"1"` for Eb, etc.
Octave pitfall: in keys C–F, `"1"` is already in octave 5 (F major: `"5'"` = C7 — far too high). `build`
prints each lead's lowest–highest note per section (e.g. `bell:answers E5-C6`); check it matches what you
meant, and treat an "outside the comfortable lead range" warning as a typo.

Sus chords: the major 3rd is an avoid note over `13sus`/`9sus` (it rubs against the 4th) — use 4, 5, 9, b7.

## Sections

| field | values | notes |
|---|---|---|
| `name`, `bars`, `prog` | required | `bars` should be a multiple of the progression length |
| `keys` | common: `whole` `filtered` `hold` `sync` `sparse` `push` `offbeat` `arp` · piano: `rolled` `rolled_half` `broken` · `mpc` · `none` — plus the genre pack's | default `hold` |
| `keys2` | any keys pattern except piano / `mpc` | second instrument (palette.keys2), upper 3 chord notes, channel 8 |
| `bass` | common: `none` `whole` `kick_lock` `hook` `walk` `halftime` `bounce` `octaves` — plus the pack's | default `hook` |
| `drums` | the genre pack's grooves (`styles` lists them per style) · `none` | default set by the pack |
| `pad` | true/false | sustained pad on the chords (bridges, late hooks) |
| `leads` | list of `{inst, melody, vel?, at?, transpose?, harmony?}` | `harmony: "below"` makes THIS lead play a chord-tone line under the melody instead of the melody - pair it with a second lead that plays the melody; `transpose` in semitones |
| `fill` | `pickup` `build` `stop` `drop` `toms` (+ pack fills) | on the section's last bar |
| `crash` | true | soft crash on the section's first beat |
| `riser` | true | reverse cymbal swelling INTO this section |
| pack layers | e.g. `shaker`, `perc`, `claves` | section flags a genre pack defines |
| `move` | `{"<channel>.<param>": value or [from, to]}` | automation over the section - see Movement |
| `pump` | `{"<channel>": depth}` | sidechain-style ducking on every beat - see Movement |

**Common keys patterns** — `filtered`: whole-bar chords through a 900 Hz low-pass (intros/outros,
"underwater"). `whole`: sustained, ties repeated chords. `hold`: long hit + re-hit on the "and" of 3.
`sync`: syncopated (1, "e", "and" of 3). `sparse`: two soft hits, leaves room for a solo. `push`: long hit +
anticipation of the next chord. `offbeat`: chords on the 8th off-beats. `arp`: broken-chord 8ths.
Piano (left hand root C2-B2 + pedal): `rolled` one rolled chord per chord, `rolled_half` re-rolled on beat
3, `broken` pedalled broken-chord 8ths. `mpc`: chopped sample — the chords are rendered once on the keys
(or `palette.sample`) instrument, aged like an old record and re-triggered in 4 rotating chop rhythms (one
"Chops" audio track; cached in renders/).

**Common bass styles** — `kick_lock`: root, fifth on the "and" of 3, anticipates the next root. `hook`:
long root + octave pop + approach note. `walk`: jazz quarters (root, step, fifth, approach). `halftime`:
root + fifth, slow. `bounce`: root, ghost, octave/fifth pop. `whole`: one note per chord (tied). `octaves`:
disco 8ths alternating root and octave. Passing/approach notes are always picked from the chord's scale and
never a half-step from what the keys hold. When the keys pattern anticipates (`push` and pack patterns like
`chop`), the bass anticipates with it automatically.

A kit that lacks a drum part plays a stand-in (toms → snare, pedal hat → hat, claves → sidestick) or drops it.

## Mixer (fixed by the engine)

1 Drums · 2 Keys (+ Chops) · 3 Keys filtered · 4 Bass · 5 Leads (delay + reverb) · 6 Pad · 7 FX/Texture ·
8 Keys 2 · Master: 25 Hz high-pass (+ optional cassette low-pass) + tape wow. Master volume 50 % leaves ~2 dB
headroom; `master` normalises the mp3.

## Tone (optional — the style sets most of these)

`"tone": {"keys_lp": 5500, "keys_hp": 120, "keys_reverb": 0.22, "drums_lp": 10000, "drums_reverb": 0.08,
"drums_crush": 0, "leads_lp": 6500, "pad_reverb": 0.4, "bass_lp": 1500, "master_lp": null}` — low-pass /
high-pass cutoffs (Hz) and reverb mixes per channel; also `pad_hp` / `pad_lp` (the Pad channel's band, default
200-3500 Hz - ambient pads want it wider), `leads_echo_beats` / `_fb` / `_wet` / `leads_reverb` (the Leads
echo) and `keys_echo_beats` / `_fb` / `_wet` (an echo on the Keys channel, off at 0 - dub stabs, echoing plucks); `drums_crush` 1 = light / 2 = heavy bit-crush on the drum
bus; `master_lp` e.g. 12500 = cassette top end. Lower = darker, dustier; higher = clearer. Piano songs need a
low `keys_hp` (~45) so the left hand survives.

## Loops (game music)

`"loop": true` makes the whole song a seamless loop; `"loop": {"from": "<section name>"}` plays the sections
before that one once (an intro) and loops the rest. With a loop:
- the last bar leads into the loop start: bass approach notes, anticipations and the harmony checker all look
  at the loop's first chord instead of "the end"
- `make` renders intro + the loop body three times, masters the continuous audio to `--lufs`, cuts the middle
  pass (so reverb / echo tails from the end wrap into the start exactly) and exports `<slug>_loop.ogg`
  (+ `_intro.ogg` and `_full.ogg` tagged `LOOPSTART` / `LOOPLENGTH` for intro songs), `<slug>_loop.json`
  (loop points in seconds and samples, loudness, seam check, engine notes) and a preview mp3 that plays the
  loop twice; `--to <path>.ogg` copies the game files into a game project
- the seam check (`loopcheck <file>` for any file) passes when the wrap is sample-continuous, has no click or
  level jump compared with continuous playback and the length is the exact bar length
- chopped-sample keys (`mpc`) and textures are not supported in loops

## Movement: "move" and "pump" (automation)

Electronic and ambient music changes slowly *inside* sections: a filter opens over 16 bars, a pad swells, the
song fades in. A section's `move` sets automation targets for its whole length:

```jsonc
"move": {"keys.cutoff": [600, 5000],   // [from, to] ramps across the section
         "pad.level": 1.2,             // a number holds that value for the section
         "master.level": [0, 1]},      // fade in (use [1, 0] on the last section to fade out)
"pump": {"pad": 0.6, "keys": 0.3}      // duck these channels on every beat (0-0.9)
```

- channels: `master drums keys keys2 bass leads pad fx`; params: `level` (0-1.5, a multiplier of the channel's
  normal volume) and `cutoff` (40-20000 Hz - adds a resonant 24 dB low-pass first in that channel; 20000 = open).
- Sections without a `move` for a target keep its last value, so a filter opened in the build stays open until a
  later section moves it. Cutoffs and non-zero levels ramp exponentially (even to the ear); fades into or out of
  silence ramp quadratically.
- `pump` (sidechain-style): the channel dips on each beat and recovers within about half a beat - depth 0.6 is a
  classic house pump (~8-10 dB). It multiplies the channel's `level`. Don't pump the drums or the master.
- The build summary prints each section's moves; the automation shows up in LMMS as automation tracks the user
  can edit ("pad cutoff", "master level" ...).
