# Arrangement: building 3–6 minutes that keep moving

Electronic tracks are long for the amount of material in them, and the patterns loop. What keeps a track alive
is that the listener hears something change **at least every 8 bars** — about 16 s at 122 BPM, 22 s at 86 BPM.
Change comes in three layers:

1. **Events, every 8 bars** — the arrangement's job: a part enters or leaves, a pattern swaps (`seq8` → `seq16`,
   `stab_dub` → `stab_off`, `rolling` → `offbeat` bass, `four_min` → `four`), the chords move to a second
   progression, a melody enters or is answered, a drum layer (`perc`, `shaker`, `clap`, `ride`) comes or goes,
   a drop (kick and bass out for 4 bars).
2. **Movement, inside the 8 bars** — `move` (filter sweeps, swells, fades) and `pump`. Movement makes the events
   smooth; it does not replace them. A filter opening over an unchanged 16-bar loop still sounds like a loop —
   the user heard exactly that in the first templates and called them repetitive.
3. **Punctuation, automatic** — the electronic patterns follow the 8-bar phrase by themselves: a small change on
   bar 4, a turnaround on bar 8 (hat rolls, clap and bass pickups, a soft kick pickup in focus), the kick drops
   out on beat 4 every 16 bars, and sequences open up an octave in bars 5–8. That is decoration, not
   arrangement: an 8-bar block played twice is still a loop.

**The loop check.** `build` prints a warning wherever the same 4- or 8-bar loop plays on longer than the style
allows: ambient 48 s, focus 30 s, downtempo 30 s, minimal 24 s (a song can set `"loop_max_s"`). It compares
notes — level and filter moves don't count, and a lone fill doesn't break a loop. Fix every loop warning with an
event from the list above; it is what a listener hears as "repetitive".

## Time per block

| BPM | 4 bars | 8 bars | 16 bars |
|---|---|---|---|
| 60 | 16 s | 32 s | 64 s |
| 68 | 14 s | 28 s | 56 s |
| 86 | 11 s | 22 s | 45 s |
| 90 | 11 s | 21 s | 43 s |
| 122 | 8 s | 16 s | 31 s |

seconds = bars × 240 / BPM. 4 minutes is ~68 bars at 68 BPM, ~86 at 86, ~90 at 90, ~122 at 122.

Build in **8-bar sections** (4 for intros, drops and transitions). A 16-bar section is fine only when its second
half changes something itself — a lead entering at `"at": 8`, a layer that differs — otherwise write two 8-bar
sections that differ ("Groove", "Groove 2"). Sections are cheap: a `move` that should span 16 bars becomes
`[500, 1500]` in the first and `[1500, 4000]` in the second.

## Openings: match the energy

- **A track that starts with drums** (minimal, downtempo, a focus pulse) reaches its groove — kick, bass and one
  more part — within 4 bars (~8 s at 122 BPM). A 16-bar kick-only intro is a DJ tool: it gives a DJ time to mix
  in and gives a listener 30 s of nothing. Use one only when the user asks for a DJ tool / club edit.
- **A track that starts from silence** (ambient, a focus intro) fades in from `0.1`, not `0`, over 4–8 bars, and
  brings the bass and kick in with their own short ramps (`"bass.level": [0.2, 1]`) — a pad-only intro followed
  by sub + kick at full level is a ~13 dB jump.
- A channel that needs more level than its track volume allows gets a held `"<channel>.level": 1.3` in the
  first section (it stays until another section moves it).

## Section plans by style

### ambient (~5 min at 68 BPM; 8 bars ≈ 28 s)

Ambient may hold a texture longer (the check allows 48 s) because the pad itself moves — but not one texture for
a minute.

| section | bars | what happens |
|---|---|---|
| Emerge | 8 | pad alone, master fading in from 0.1, pad filter opening |
| Wake | 4 | dotted-8th sequence enters filtered, sub bass fades in |
| Bloom | 8 | first bell phrase, sequence opening |
| Bloom 2 | 8 | chords start moving (2 bars each), soft flute long tones answer the bells |
| Tide | 8 | ticks, a second progression, pad swell |
| Tide 2 | 8 | the sequence becomes `seq8`, bells return with echo |
| Still | 8 | everything thins: drone chord, bells only, pad filter closing |
| Bloom 3 | 8 | the sequence returns, a soft pulse, bells with a harmony line |
| Bloom 4 | 8 | the flute answers, chords move |
| Dissolve | 12 | fade out, filters closing, one last bell |

### focus (~4 min at 86 BPM; 8 bars ≈ 22 s)

Steady, not static: the pulse never stops, and around it the sequence figure, the layers and the chords change
every 8 bars. A soft melody comes and goes — never in two blocks in a row.

| section | bars | what happens |
|---|---|---|
| Intro | 4 | pad only, fading in from 0.1, filter opening |
| Arrive | 4 | the 8th-note sequence enters filtered, the sub fades in (`bass.level` [0.2, 1]) |
| Pulse | 8 | `pulse_soft`, sub pulse, sequence opening |
| Pulse 2 | 8 | shaker layer, a soft melody phrase |
| Flow | 8 | `pulse` (kick 1 + 3, rim), the second progression, melody out |
| Flow 2 | 8 | `seq16`, an answer phrase on another bell |
| Drift | 8 | drums thin to `ticks`, `seq_dotted`, chords move every 2 bars, pad swell |
| Return | 8 | home progression, `seq8_hi`, `pulse_soft`, perc layer |
| Return 2 | 8 | `pulse`, the melody with a quiet harmony line |
| Settle | 8 | `seq8`, melody out, ride layer, sequence filter closing |
| Outro | 8 | fade out, drums thin to `pulse_soft` |

Harmony: 2–3 progressions alternated by block (home / away / drift); a two-chord 4-bar loop under the whole
track is what made the first focus template repetitive. Keep the kick soft (`pulse`, `pulse_soft`), no crashes,
no risers — the automatic turnarounds in these patterns are gentle (a soft kick pickup, a shaker breath).

### minimal (~4 min at 122 BPM; 8 bars ≈ 16 s)

One or two chords for the whole track is fine; the change comes from parts trading places every 8 bars.

| section | bars | what happens |
|---|---|---|
| Intro | 4 | kick, hats and the rolling bass from bar 1, bass filter opening (`bass.cutoff` [400, 1500]) |
| Groove | 8 | clicky hats + rim (`four_min`), bass open |
| Stabs | 8 | dub stabs enter filtered and open |
| Drive | 8 | full `four` (clap), perc layer |
| Lift | 8 | pad enters pumping, `stab_off` instead of `stab_dub`, keys filter opening further |
| Break | 8 | no kick, no bass: pad, the lead motif, pad filter opening; the second chord (a lift progression) |
| Break 2 | 8 | the motif with a harmony line, `four_break` hats + claps back, riser into the peak, snare `build` fill |
| Peak | 8 | everything, crash: offbeat bass, offbeat stabs, pumping pad + keys, the motif |
| Peak 2 | 8 | motif out, shaker + perc, `seq16_hi` over the stabs (`keys2`) |
| Drop | 4 | kick and bass out, stabs and pad alone, master filter dips and reopens |
| Peak 3 | 8 | back in with the `rolling` bass and `ride`, the motif returns |
| Wind down | 8 | `stab_dub`, `four_min`, keys filter closing, pad fading |
| Outro | 8 | kick, hats and bass, master fading |

That is 96 bars (3:09); for 4–5 minutes add blocks from the same menu (a Groove 2 with the sequence, a second
Break) rather than lengthening sections.

### downtempo (~4 min at 90 BPM; 8 bars ≈ 21 s)

| section | bars | what happens |
|---|---|---|
| Intro | 8 | EP chords alone through an opening filter, fading in, a little vinyl |
| Verse | 16 | broken beat, synth bass, kalimba motif at bar 0 — and an answer at bar 8 |
| Hook | 16 | busier beat, pad, flute hook (the memorable part); second half: the hook's answer or a harmony line |
| Break | 8 | half-time, sparse chords, vibes, pad filter closing |
| Verse 2 | 16 | beat back, 8th sequence instead of held chords, perc layer, motif again |
| Hook 2 | 16 | hook with a harmony line, shaker, riser into it |
| Outro | 8 | chords alone, filter closing, fade |

The `broken` / `breaks` beats vary by themselves over 4 bars, so 16-bar sections work here as long as the
melody changes at bar 8.

## Movement recipes (`move` / `pump`)

| effect | how |
|---|---|
| fade in / out | first section `"master.level": [0.1, 1]`; last section `"master.level": [1, 0]` (8–12 bars) |
| a part "opening up" | `"keys.cutoff": [600, 2500]` in one block, `[2500, 5000]` in the next — the classic build |
| closing into a breakdown | `"keys.cutoff": [5000, 900]` — then the next section jumps back to 5000 for impact |
| underwater intro | `"pad.cutoff": [300, 2000]` with the master fading in |
| swell | `"pad.level": [0.6, 1.2]` across a section, back to `1` in the next |
| a part leaving gently | `"pad.level": [1, 0]` in the section before it stops |
| sidechain pump | `"pump": {"pad": 0.6}` (house), `{"pad": 0.4, "keys": 0.25}` (subtle); only with a four-on-the-floor kick |
| whole-mix filter drop | `"master.cutoff": [18000, 800]` over the last 4 bars before a drop, then `"master.cutoff": 20000` |

Values persist: a cutoff opened in one section stays open until a later `move` changes it — set it explicitly in
the section after a breakdown.

## Melody in electronic music

- Ambient / focus: few, long notes (half and whole notes), often starting off the downbeat; let the echo answer.
  A 4-bar phrase and an answer phrase, each appearing 2–3 times across the track on different instruments or
  with a harmony line, is plenty.
- Minimal: a short motif (1–2 bars, 3–6 notes) repeated exactly within a section; between sections it comes and
  goes, moves to another instrument or gets a harmony line.
- Downtempo: a real hook (2–4 bars) with a clear rhythm; answer it with a second instrument.
- Harmony lines: add a second lead with `"harmony": "below"` in a later appearance of a phrase.
