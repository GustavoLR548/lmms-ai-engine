# LMMS internals (for extending the engine)

Read this only when adding instruments, kits, effects, or debugging a project that won't load/render.
Everything below was verified on LMMS 1.2.2 (Windows) by rendering and measuring.

## File format
- `.mmp` = plain XML; `.mmpz` = zlib-compressed (`lmms dump in.mmpz > out.xml` to read one).
- 192 ticks per 4/4 bar, 48 per beat, 12 per 16th. At B BPM one tick = 60/B/48 s (non-integer samples — fine).
- LMMS key = MIDI − 12 (A4/440 Hz = 57). AFP samples play at original pitch on key 57 (basenote 57).
- Song-editor instrument track: `<track type="0">` → `<instrumenttrack vol pan fxch basenote>` → `<instrument name=...>`,
  `<eldata>` (per-instrument filter + envelopes), then `<pattern type="1" pos len name>` with `<note pos len key vol pan>`.
  Notes past a pattern's `len` are not played — pattern length must cover them.
- Volumes: track `vol` 0–200 (%), linear. `mastervol` in `<head>` is linear too (70 → 50 = −2.9 dB).
  Mixer channel `volume` is a linear factor (1.75 ≈ +4.9 dB, 2.0 = +6 dB).
- `<fxmixer>` channels: `<fxchannel num name volume>` + `<fxchain>` + `<send channel="0" amount="1"/>`.

## LMMS silently ignores unknown node/attribute names
The effect's controls node must be named exactly what the plugin's `nodeName()` returns, or the effect
loads with defaults and no error. Verified names (the dll strings are the source of truth):

| effect `name=` | controls node | attributes |
|---|---|---|
| `reverbsc` | `ReverbSCControls` | `input_gain output_gain size color` |
| `delay` | `Delay` | `DelayTimeSamples` (seconds!) `FeebackAmount` (sic) `LfoFrequency` `LfoAmount` `OutGain` |
| `eq` | `Eq` | `HPactive HPfreq LPactive LPfreq HP12/24/48 LP12/24/48 PeakNactive PeakNfreq PeakNgain PeakNbw Lowshelf… Highshelf… Inputgain Outputgain` |
| `dualfilter` | `DualFilterControls` | `enabled1 filter1 cut1 res1 gain1 mix (-1 = filter 1 only) …2` |
| `bitcrush` | `bitcrushcontrols` | `ingain innoise outgain outclip rate stereodiff levels rateon depthon` |
| `stereoenhancer` | `stereoenhancercontrols` | `width` |
| `amplifier` | `AmplifierControls` | `volume pan left right` |
To verify a new effect: render a saw blip dry and through it (`rendertracks`), compare spectra/levels.
To find names: extract ASCII/UTF-16 strings from `plugins/<name>.dll` or grep the demo projects
(`lmms dump data/projects/demos/*.mmpz`).

## Tape wow
`Delay` with `DelayTimeSamples=0.01`, `FeebackAmount=0`, wet 1.0 and a slow LFO = pure pitch wobble.
Measured: `LfoAmount` 0.001 → ±21 cents, linear. Put it on the master so every instrument wobbles
together — wobbling only the keys detunes them against bass and leads.

## ZynAddSubFX
- Zyn renders fine from the CLI. The engine embeds a `.xiz` preset (gzipped XML `<INSTRUMENT>`) into a
  full Zyn master state (`assets/zyn_template.xml`, taken from a demo, system effects off) as part 0.
- Some presets sound an octave low (Soft Vibes, Vibraphone, Dark Strings). Always `measure` (or `audition`)
  a new preset: it reports octave shift, tuning (Clean Guitar1 is −7 cents — avoid) and a volume.
- Presets have their own velocity sensitivity; Soft Rhodes changes tone a lot with velocity (60–90 is the range).

## AudioFileProcessor
- `src` relative paths resolve against `<workingdir>/samples/` first, then the factory `data/samples/`.
- `looped="1"` loops the whole sample while the note is held → one long note plays a texture for any tempo.
- `reversed="1"` plays backwards → reverse-cymbal riser; place the note so it ENDS on the downbeat.
- A note shorter than the sample cuts it off; give drum notes at least the sample length.

## Rendering
- `lmms render song.mmp -o out.wav -f wav -a` (32-bit float: no clipping in the file). ~35 s for a 3.5-min song.
- `lmms rendertracks song.mmp -o dir/ -f wav` → `N_<track name>.wav` per track, each a full-song render:
  ~20–40 s per track (6+ min for 17 tracks). Run it in the background.
- A 16-bit render clips at 0 dBFS — the engine keeps master at 50 % and masters loudness with ffmpeg.
- Levels are measured with `ffmpeg -af ebur128=peak=true` (integrated LUFS + true peak).

## Adding things
- **Instrument**: add to `catalog.INSTRUMENTS` with `measured=False`, run `measure --instruments <id>`; the
  result (vol, octave, gain) lands in `assets/levels.json` and is applied on import.
- **Drum kit**: a dict of part → (sample path or `hit(sf2, note, bank, patch)`, vol, extra) in `catalog.KITS`,
  then `measure --kits <kit>`.
- **Pattern/style**: register it from a genre pack (references/genre-packs.md); only genuinely shared
  vocabulary goes into `common.py`. Keep all passing notes inside `chord.scale` and away from `song.rubs()`.

## LMMS 1.3 / nightly
Untested. Known renames there: `<fxmixer>`→`<mixer>`, `fxch`→`mixch`, `fxchannel`→`mixerchannel`. If the user
runs 1.3, build a tiny project, open it, and check that effects and mixer routing survived before relying on it.

## SoundFont player (sf2player)

`lmmsgen.sf2(src, bank, patch, gain)` → `<instrument name="sf2player"><sf2player src=... bank=... patch=... gain=.../>`.
LMMS 1.2.2 ships FluidSynth **1.1.6**: SF2 only (no SF3), and GeneralUser GS 2.x needs FluidSynth 2.3+ - use
the legacy 1.472 bank (what `soundfonts/generaluser_gs.sf2` is). Relative `src` resolves against
`<workingdir>/samples/`. Renders fine from the CLI; the `fluid_synth_sfont_unref` CRITICAL lines on exit are
harmless. MIDI note = LMMS key + 12 (same as everything else); drum kits are bank 128 - one track per drum
part with a fixed note (`catalog.hit()`), so levels and pans stay per part. Soft kits (GeneralUser "Brush")
need `gain` > 1 (measure sets it). `scripts/sf2info.py file.sf2 [bank program]` lists presets / a kit's key map.

## Chopped-sample track

`chops.py` renders the chords once (one-track project, `lmms render`), ages the audio with numpy/scipy and
writes `renders/<slug>_chops.wav`, placed as one AudioFileProcessor note (key 57 = original speed) on the
"Chops" track (Keys channel). The record is cached by a hash of instrument + tempo + voicings.

## Automation (verified by rendering)

- An automated knob is saved as a CHILD element with an id instead of an attribute: `<fxchannel ...><fxchain/>
  <volume id="910001" value="1" scale_type="linear"/>...`, or inside an effect's controls node
  `<DualFilterControls ...><cut1 id="910002" value="800" scale_type="log"/></DualFilterControls>`
  (`lmmsgen.automatable()`).
- The automation lives in a song-editor track `<track type="5" name=...><automationtrack/><automationpattern
  name pos len tens="1" mute="0" prog="1">` with `<time pos=... value=.../>` points (pos relative to the pattern)
  and `<object id="910002"/>` naming the knob. prog 0 = discrete, 1 = linear, 2 = cubic. Dense points make any
  curve (`lmmsgen.AutomationTrack`).
- **Log-scaled knobs** (filter cutoffs, `scale_type="log"`): LMMS reads automation values as knob POSITIONS -
  real = min + (max - min) * ((v - min) / max) ** e - so writing the frequency itself is wrong ("3000" on a
  1-20000 Hz cutoff plays ~117 Hz). Convert with `lmmsgen.log_knob(real, min, max)`; verified identical to a
  static filter at 300 / 1000 / 3000 Hz.
- LFO controllers exist (`<controllers><lfocontroller .../>` + `<connection><data id="N"/></connection>` on the
  knob) but their phase isn't tied to the song position; the engine uses automation points for everything,
  pumping included, so renders are deterministic.

## DualFilter types
`filter1`: 0 LowPass, 1 HiPass, 6 Moog, 7 2x LowPass, 11 RC LowPass 24 dB, 13 RC HighPass 24 dB, 16 SV LowPass.
LMMS 1.2's **Moog type self-oscillates** with resonance near the top of the range (a 7.5 kHz whistle at 12 kHz,
res 0.9) and gets LOUDER as the cutoff falls - don't sweep it. RC LowPass 24 dB (11) at res 0.5 behaves: steadily
louder and brighter as it opens. The engine's `cutoff` moves use it.

## Instrument presets (.xpf)
- Any plugin's factory preset loads with `lmmsgen.xpf_instrument()`. Presets from LMMS 0.4 / 1.0 (e.g.
  `TripleOscillator/HiPad.xpf`, `Organic/*.xpf`) have no `<instrument name=...>` wrapper - the plugin element
  sits directly in `<instrumenttrack>`; the loader wraps it.
- TripleOscillator / Organic / BitInvader presets get their pluck, swell or filter sweep from the preset's own
  `<eldata>` (instrument filter + volume / cutoff envelopes and LFOs): `lmmsgen.xpf_eldata()` takes it when it is
  active (the OPL2 presets' eldata is inert, so they are unaffected). Presets may also switch on LMMS's chord /
  arpeggio tools - never copy those, the engine writes the chords itself.
- Many ZynAddSubFX presets sound an octave low (their loudest partial and waveform period sit at half the
  written pitch - `measure` sets octave +12). Presets whose FUNDAMENTAL is weak but whose 2nd harmonic is loud
  (TripleOscillator `PluckArpeggio`, `TB303`) fool the "lowest strong octave" rule into -12: check the spectrum
  (energy at 1.5x / 2.5x the written pitch means the series is built on the lower octave) and the waveform
  period before trusting an octave result.
- Track pitch (`<instrumenttrack pitch=...>`) is in cents: catalog entries with `retune=True` get their measured
  tuning offset undone there.

## DrumSynth (.ds)
LMMS ships ~760 DrumSynth models under `data/samples/drumsynth/` (TR-808 / 909 / 606, CR-78, LinnDrum ...).
AudioFileProcessor renders them directly from the CLI (`afp("drumsynth/tr909/Hat-c.ds")`). Some are quiet: a
too-quiet AFP kit part gets `gain`, applied as the sampler's `amp` (up to 500 %).
