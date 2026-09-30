# Styles

A song sets `"style"` in song.json; the style supplies defaults (palette, swing, humanize, tone, feel, wow) for
anything the spec leaves out. `python scripts/lofi.py styles` prints the live list. The engine accepts any
pattern in any style — the lists below are what makes each style sound like itself. **Pick the style first,
then write chords, melodies and form in that style's idiom** — the palette alone does not make a style.

| id | sounds like | BPM | the identity |
|---|---|---|---|
| `jazzy` | Nujabes, Uyama Hiroto | 70-86 | Rhodes, vibes/flute, dusty swung boom-bap, ii-V jazz |
| `bossa` | bossa lofi, Tom Jobim through a tape deck | 64-80 | nylon guitar comping, bossa bass + rim clave, straight 16ths |
| `sleepy` | Kupla, Philanter, piano lofi | 58-72 | a real upright piano with a left hand, brushes or nothing |
| `dilla` | J Dilla, Knxwledge, neo-soul beats | 76-92 | drunk timing, chopped-record keys, EP/organ, late synth bass |
| `citypop` | Tatsuro Yamashita / Mariya Takeuchi via lofi | 80-100 | DX7 EP, guitar cutting, slap bass, drum machine, sax hooks |

Every new song should differ from the last few (`lofi.py history`): change style, or at least the chord
instrument, key, tempo band and form. `build` prints a variety line and says TOO SIMILAR when a song shares
6+ of 10 dimensions with a recent one.

---

## bossa — Bossa lofi

**Palette**: keys `nylon_guitar` (catalog strum + guitar voicing range), bass `upright_bass`, pad `strings`,
kit `latin`. Leads: `tenor_sax` (keep it D4-E5), `gs_flute`, `muted_trumpet`, `kalimba`.
**Feel**: swing 0 (bossa is straight), humanize 2, no snare lag.

**Patterns** — keys: `bossa` (2-bar syncopated comp, the core), `bossa_soft` (intros/outros), `whole`
(bridge, under a melody), `arp`. Bass: `bossa` (root on 1 and 2&, fifth on 3, pickup on 4&), `walk` (bridge
lift), `whole`. Drums: `bossa` (kick 1-2&-3-4&, 2-bar rim clave, 16th shaker), `bossa_ride` (ride instead of
shaker - bridges), `bossa_light` (rim + shaker, no kick - intros/outros), `brushes_light`.
Section flags: `"perc": true` (congas + bongos), `"claves": true` (son clave 3-2), `"tambourine": true`.

**Harmony**: maj9 / 6/9 tonic, II9 (the V/V "Ipanema" move), ii9 → bII9 (tritone sub) → Imaj9, iv6
(minor plagal) in bridges, iii7 → VI7alt → ii9 → V13. Chromatic but smooth.
- A: `Imaj9 vi9 II9 II9 | ii9 bII9 Imaj9 V13sus`
- B: `IVmaj9 IVmaj9 iv6 bVII9 | iii7 VI7alt ii9 V13`
- tag: `ii9 bII9 Imaj9 Imaj9`

**Melody**: long notes that land on 9ths and 13ths, stepwise lines, phrases starting on the "and" of 1.
Over bII9 use its chord tones (it's chromatic: in D, Eb9 = Eb G Bb Db F). Answer the sax with flute in the
bridge. **Form**: guitar-alone intro → A (groove, no melody) → A (theme) → B (bridge, ride + walking bass +
strings) → A (theme varied, + claves) → tag with guitar and bass.

## sleepy — Sleepy piano

**Palette**: keys `upright_piano` (PIANO voicing range, the Keys channel keeps lows for the left hand),
bass `upright_bass` (only in the middle), pad `strings`, kit `brushes`, textures vinyl -3 dB + `tape`.
Leads: `piano_lead` (right-hand melody on the Leads channel), `kalimba`, `music_box`, `gs_vibes`.
**Feel**: swing 2, humanize 3, keys jitter ±4 ticks (rubato), master low-pass 12.5 kHz, wow 0.0003.

**Patterns** — keys: `rolled` (one rolled chord per chord + LH root + soft fifth, pedal held), `rolled_half`
(re-rolled on beat 3), `broken` (pedalled broken-chord 8ths: LH root, fifth, then up and down the voicing).
Bass: `none` (first half!), `whole`, `halftime`. Drums: `none`, `brushes_light` (swirl + pedal hat),
`brushes` (+ soft kick and brush snare), `heartbeat` (two soft kicks).

**Harmony**: diatonic, gentle — Imaj9, iii7, vi9, IVmaj9 and the borrowed iv6 (the bittersweet "sigh"
chord: in Db, Gbm6 — its A natural falling to Ab is the whole mood). V13sus rather than V7.
- A: `Imaj9 iii7 vi9 IVmaj9 | Imaj9 iii7 IVmaj9 iv6`
- B: `vi9 iii7 IVmaj9 Imaj9 | ii9 iii7 IVmaj9 V13sus`
- coda: `IVmaj9 iv6 Imaj9 Imaj9`

**Melody**: simple, singable, quarter/half notes, mostly chord tones above the voicing (Ab4-Bb5 in Db).
Let it breathe: rests at bar ends. **Form**: rolled-chord intro → theme on piano ALONE (no drums, no bass) →
theme varied with brushes and bass → bridge (strings + kalimba answers) → reprise → rolled coda.

## dilla — Dilla / neo-soul

**Palette**: keys `chorus_ep` (also the source for `mpc` chops; set `palette.sample` to chop another
instrument), bass `lately_bass` (or `finger_bass`), pad `drawbar_organ`, kit `dilla` (snare + clap layer,
crushed drum bus). Leads: `muted_trumpet`, `gs_flute`, `gs_vibes`, `square_lead`.
**Feel** (the point of the style): swing 5, `feel` = kick +4±3 ticks late, clap 5 early, snare 1 early,
hats +2±4, bass +6±3 late, keys +3. Change `feel` to make it more or less drunk.

**Patterns** — keys: `mpc` (chopped sample: re-triggered, aged record of the chords, 4 rotating chop
patterns, occasional reversed slice), `filtered` (cold open), `stabs`, `hold`. Bass: `hook`, `kick_lock`,
`halftime`, `whole`. Drums: `dilla` (4 rotating kick patterns, ghost snares, skipped hats), `dilla_sparse`
(breaks), `dilla_ride`. Fill `drop` before the beat returns.

**Harmony**: minor 9ths moving by whole steps and borrowed chords — vi9 v9 IVmaj9 III7alt (in Bb: Gm9 Fm9
Ebmaj9 D7alt), IVmaj9 iv9 (chromatic minor plagal), iii7 VI7alt ii9 V13sus. Loops are 4 bars; the variety
comes from the chop pattern rotating, organ entering, B sections played live (`hold`) instead of chopped.
**Form**: filtered cold open → Flip A (chops) → Flip A + organ → B side (live EP + horn melody) → break
(bass + sparse drums, `drop`) → Flip A + flute → B stabs → chops alone ("tape out").

## citypop — City-pop lofi

**Palette**: keys `fm_epiano` (DX7), keys2 `jazz_guitar` (or `muted_guitar`), bass `slap_bass` (or
`lately_bass`, `finger_bass`), pad `synth_strings`, kit `drum_machine`, textures tape + vinyl -6 dB.
Leads: `tenor_sax`, `square_lead`, `muted_trumpet`. **Tone**: bright (keys 9 kHz, drums 12 kHz) with a
cassette master low-pass at 13 kHz, wow 0.0003.

**Patterns** — keys: `push`, `sync`, `hold`, `offbeat`, `whole`. keys2 (upper 3 notes of the chord on a
second channel): `cutting` (16th guitar chops on 2 and 4), `offbeat`, `sparse`. Bass: `slap` (root / octave
pops), `octaves` (disco 8ths), `kick_lock`. Drums: `citypop` (16th hats, snare + clap), `disco` (four on
the floor + open hats - last chorus), `halftime` (bridge). Fill `toms` into choruses.

**Harmony**: the "Just the Two of Us" loop IVmaj9 III7alt vi9 | v9 I9 (in E: Amaj9 G#7alt C#m9 Bm9 E9) for
verses; choruses IVmaj9 V13 iii7 vi9 ii9 V13sus Imaj9 I9; bridge from bVImaj9. The I9 → IVmaj9 pull keeps
it cycling. **Melody**: catchy, syncopated (3+3+2 rhythms), sax in B3-E5; a synth-lead motif in intro /
outro. **Form**: intro (pad + EP + synth motif) → verse (guitar cutting, slap) → chorus (sax hook) →
verse 2 (synth answers) → bridge (halftime, sax) → final chorus (disco drums, sax harmony below) → outro.

## jazzy — Jazzy boom-bap

The original skill sound — see references/music-guide.md (progression bank, melody rules, forms). Use it
when the user asks for Nujabes / classic lofi hip-hop, not by default.

---

## Instruments and patterns

Instrument, kit and texture ids (and how to add and measure new ones) are in lmms-core:
`~/.claude/skills/lmms-core/references/instruments.md`. The lofi-only patterns named above are described in
`references/patterns.md`; the shared ones in `~/.claude/skills/lmms-core/references/spec-format.md`.
