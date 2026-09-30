# The four styles, their sounds and patterns

`styles` prints the live palettes. Any catalog id can be used in any style via `palette` / `leads` — the style
sets defaults, tone and the pattern vocabulary that fits it.

## ambient — beatless or nearly

Long evolving pads and drones, chords that change every 2–4 bars (or not at all), scattered bells and chimes,
a sub or no bass, deep reverb and long echoes. Movement comes from filter swells, pad level swells and slow
dotted-8th sequences drifting against the bar. Eno, Stars of the Lid, Hammock, Harold Budd.

- 60–90 BPM (tempo mostly sets the speed of sequences and echoes)
- default palette: keys `glass_arp`, pad `dream_pad`, bass `sub_bass`, kit `soft_electro`, texture tape
- harmony: maj9 / 6/9 / sus chords, slow plagal moves (I–IV), relative-minor shades (vi9), pedal points;
  avoid strong V–I cadences. 2 bars per chord or slower.
- keys: `drone` (held, tied), `seq_dotted` (dotted-8th drift), `seq8`, `sparse`, `whole`, `arp`, `broken`
- bass: `none`, `whole`, `sub_pulse` | drums: `none`, `ticks` (random clicks), `shaker`, `pulse_soft`, `halfstep`
- leads: `chimes`, `crystal_bells`, `soft_hammer`, `muffled_bells`, `analog_bell`, `soft_flute`, `kalimba`,
  `music_box`, `gs_vibes` — long notes, lots of space; the Leads echo is long (1.5 beats, high feedback)

## focus — deep focus / study / work

Steady and unobtrusive: a soft pulse (or none), a repeating pluck or arp figure, a warm pad, sub bass, slow
harmony (a chord per 1–2 bars, 2–3 progressions that alternate by block). No attention-grabbing melody — soft
phrases that come and go. The pulse never stops, but the sequence figure, the layers and the chords change every
8 bars. Tycho's quiet tracks, Bonobo's calm side, "deep focus" playlists.

- 72–100 BPM, swing 0–1
- default palette: keys `soft_arp`, pad `soft_pad`, bass `sub_bass`, kit `soft_electro`
- harmony: maj9 / m9 (I–vi, I–IV, vi–IV) for the home loop, a longer away progression (IV–I–ii–V9sus),
  9sus for gentle tension
- keys: `seq8`, `seq16`, `seq_dotted`, `pulse8`, `whole`, `sparse`, `arp`, `broken`
- bass: `sub_pulse`, `whole`, `downtempo`, `halftime` | drums: `pulse`, `pulse_soft`, `halfstep`, `shaker`,
  `ticks`, `none`
- leads: `soft_hammer`, `chimes`, `kalimba`, `gs_vibes`, `muffled_bells`, `soft_flute`, `music_box`, `marimba`
- layers: `shaker`, `perc` (soft claves / rim), `ride`

## minimal — minimal techno / deep house

Four-on-the-floor 909, offbeat hats, a rolling or offbeat bass, short chord stabs through an echo (often ONE
chord for a long time), pads pumping against the kick, and the track built by adding, removing and swapping
parts every 8 bars (16 s) while filters open. Kompakt, Lawrence, Dixon, early Border Community.

- 116–128 BPM, swing 0–1
- default palette: keys `house_pluck`, pad `analog_pad`, bass `decay_bass`, kit `tr909`
- harmony: minor 9 / 11 vamps (`vi9`, `ii9`), two-chord moves (vi9–IVmaj9), 9sus lifts in breaks
- keys: `stab_off` (offbeat stabs), `stab_dub` (dub-techno syncopation, 4 rotating bars), `seq16`, `pulse8`,
  `whole`, `sparse` — Keys echo is on in this style (dotted 8th)
- bass: `offbeat`, `rolling` (16ths around the kick), `minimal`, `sub_pulse`, `whole`
- drums: `four` (kick, clap 2+4, offbeat open hat), `four_min` (clicky 16th hats + rim, no clap), `four_kick`
  (kick + light hat: intros, outros), `four_break` (everything but the kick: breakdowns), `none`
- leads: `ping`, `glass_arp`, `chimes`, `crystal_bells`, `analog_bell`, `pluck` — short motifs repeated
- layers: `clap`, `perc`, `shaker`, `ride`; `pump: {"pad": 0.6}` is the signature

## downtempo — chill electronic / trip-hop

A swung broken beat on 808s, warm electric-piano chords, round synth bass, lush sweeping pads, melodic hooks
on bells, flute or kalimba, a little vinyl. Bonobo, Emancipator, Nightmares on Wax, Tycho's warmer tracks.

- 80–100 BPM, swing 2–4
- default palette: keys `ice_rhodes`, pad `sweep_pad`, bass `thick_bass`, kit `tr808`, texture vinyl (quiet)
- harmony: m9 / maj9 / 13 — ii–V colours, IV–V–iii–vi, chromatic mediants for the break
- keys: `hold`, `sync`, `push`, `sparse`, `whole`, `seq8`, `arp`, `stab_dub`
- bass: `downtempo`, `hook`, `kick_lock`, `halftime`, `whole` | drums: `broken`, `breaks` (busier), `halfstep`,
  `pulse`, `none`
- leads: `soft_flute`, `kalimba`, `gs_vibes`, `chimes`, `muffled_bells`, `gs_flute`, `music_box`, `analog_bell`

## Sounds by role

All measured (level, octave, tuning); several Zyn presets sound an octave low and are corrected automatically.

| role | ids | character |
|---|---|---|
| pad | `soft_pad` `analog_pad` `sweep_pad` `ice_pad` `dream_pad` `void_pad` `space_choir` `ethereal_pad` `hi_pad` | soft/warm · classic analog · filter-swept · glassy · dreamy · dark/empty · voices · evolving (Organic LFO) · bright |
| | `wind` | a noise texture played as a pad (long notes) |
| | also `strings` `warm_pad` `synth_strings` `soft_saw_pad` `choir` `orch_strings` | sampled / lofi pads |
| keys | `soft_arp` `house_pluck` `pluck` `pluck_arp` `ping` `glass_arp` | plucks for sequences |
| | `ice_rhodes` `rhodes` `tine_ep` `fm_epiano` | electric pianos for chords |
| lead | `chimes` `soft_hammer` `muffled_bells` `crystal_bells` `analog_bell` `soft_flute` | synth bells and a soft flute (`muffled_bells` has a slow attack: half notes and longer only) |
| | `kalimba` `music_box` `gs_vibes` `marimba` `gs_flute` | sampled |
| bass | `sub_bass` (pure sine — felt, pair with keys for the note), `decay_bass` (plucky), `analog_bass`, `thick_bass` (round), `pluck_bass`, `reso_bass`, `acid_bass` (303-style) | |
| kit | `soft_electro` (focus / ambient), `tr909` (minimal / house), `tr808` (downtempo), `drum_machine` (analog), `dusty` / `dilla` (sampled, for dustier downtempo) | |

## Patterns (scripts/electro_pack.py; the common ones are in lmms-core spec-format.md)

- **Phrases**: every pattern here follows the 8-bar phrase by itself — a small change on bar 4, a turnaround on
  bar 8 (hat roll, clap / bass pickup, a soft kick pickup in `pulse`), the kick dropping out on beat 4 every 16
  bars (`four`), a shaker breath (`pulse`). A section's own `fill` replaces the turnaround on its last bar.
- **Sequences** (`seq16`, `seq16_hi`, `seq8`, `seq8_hi`, `seq_dotted`): a note every 16th / 8th / dotted 8th
  cycling through the chord; the figure runs on across bar lines (a dotted-8th figure drifts against the bar like
  a delay line), velocity rises slowly through the section, and in bars 5–8 of each phrase the top note jumps an
  octave. `_hi` = an octave up.
- **Stabs**: `stab_off` (offbeats), `stab_dub` (8 rotating dub-techno bars), `pulse8` (8th-note chords).
- **drone**: the chord held and tied for as long as it doesn't change. `drone` / `whole` need a SUSTAINING keys
  sound (a pad id as `palette.keys`, `ice_rhodes` fades slowly) — on a pluck they are one short note per chord;
  with plucks use the sequences, and let the pad carry the drone.

## Tone

Set by the style; override per song with `"tone"`. `pad_level` is the Pad channel's volume: pads carry these
styles, so they sit 1.6–4.6 dB louder than in lofi (ambient 1.7, focus 1.5, minimal 1.4, downtempo 1.2; 2.0 max,
and `pad.level` moves multiply it). The Pad channel's band (`pad_hp` / `pad_lp`) is wide in
ambient (80–9000 Hz) and narrow in minimal (250–5000 Hz) so pads stay out of the kick and hats. `keys_echo_*`
puts an echo on the chords (on in ambient, focus, minimal, downtempo); `leads_echo_*` sets the melody's echo.
