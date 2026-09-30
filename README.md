# lmms-ai-engine

Skills for Claude Code that compose music in [LMMS](https://lmms.io) from plain-language prompts. Each one writes
an editable `.mmp` project, checks every note against the harmony, renders with LMMS and masters an MP3 (or
seamless OGG loops for games). All sounds are license-safe: LMMS's own synths and samples, FreePats (CC0) and
GeneralUser GS.

| skill | what it makes |
|---|---|
| `lmms-core` | the shared engine: song.json format, harmony checker, instrument catalog, automation, render + master, game-loop export, level measurement, variety history. The genre skills run on it |
| `lmms-hiphop` | lofi: jazzy boom-bap, bossa, sleepy piano, Dilla / neo-soul, 80s city-pop |
| `lmms-gamemusic` | 16-bit game music loops: SNES-style sampled orchestra or Genesis / DOS FM, with intro + loop points |
| `lmms-electronic` | ambient, deep focus, minimal / deep house, downtempo |

## Install

Copy the four folders into `~/.claude/skills/` (lmms-core must sit next to the genre skills, or point the
`LMMS_CORE` environment variable at it). Then, once:

```bash
python ~/.claude/skills/lmms-electronic/scripts/electronic.py doctor
python ~/.claude/skills/lmms-electronic/scripts/electronic.py setup
```

`doctor` finds LMMS (1.2.2), its data folder, ffmpeg and the SoundFonts; `setup` creates `lmms-core/.venv` with
numpy + scipy. Any genre skill's entry script works for these two commands (`lofi.py`, `gamemusic.py`,
`electronic.py`).

## SoundFonts

The sampled instruments come from 13 SoundFonts. They are not in this repo (~200 MB); download them and put them
in `<LMMS working dir>/samples/soundfonts/` (usually `Documents/lmms/samples/soundfonts/`) under exactly these
file names, since the catalog (`lmms-core/scripts/catalog.py`) refers to them by name. Keep each one's readme and
licence next to them (e.g. in `soundfonts/licenses/<name>/`).

| file | SoundFont (version) | used for | source | licence |
|---|---|---|---|---|
| `generaluser_gs.sf2` | GeneralUser GS v1.472 by S. Christian Collins | 42 instruments (pianos, EPs, vibes, strings, brass, woodwinds, harp, choir, basses, synth leads...) and the Standard, Power, Orchestra, Brush and 808/909 drum kits: kits `brushes`, `latin`, `gs_standard`, `gs_power`, `gs_orchestral`, `tr808`, `tr909`, `soft_electro` | [schristiancollins.com/generaluser](https://www.schristiancollins.com/generaluser) | GeneralUser GS License v2.0: free for any music, private or commercial |
| `upright_piano_kw.sf2` | Upright piano KW (2022-02-21) | `upright_piano`, `piano_lead` | [FreePats](http://freepats.zenvoid.org/Piano/acoustic-grand-piano.html#UprightKW) | CC0 |
| `fm_epiano.sf2` | FM Synthesized Piano #1, DX7 "E. Piano 1" (2019-09-16) | `fm_epiano` | [FreePats](http://freepats.zenvoid.org/) | CC0 |
| `drawbar_organ.sf2` | Drawbar organ emulation (2019-07-12) | `drawbar_organ` | [FreePats](http://freepats.zenvoid.org/Organ/electric-organ.html) | CC0 |
| `nylon_guitar.sf2` | Spanish classical guitar (2019-06-18) | `nylon_guitar` | [FreePats](http://freepats.zenvoid.org/Guitar/acoustic-guitar.html) | CC0 |
| `jazz_guitar.sf2` | Electric Guitar FSBS, jazz (2026-08-07) | `jazz_guitar` | [FreePats](http://freepats.zenvoid.org/) | CC0 |
| `finger_bass.sf2` | Finger Bass YR (2019-09-30) | `finger_bass` | [FreePats](http://freepats.zenvoid.org/) | CC0 |
| `lately_bass.sf2` | Lately Bass, TX81Z patch (2024-03-21) | `lately_bass` | [FreePats](http://freepats.zenvoid.org/Synthesizer/synth-bass.html) | CC0 |
| `synth_strings.sf2` | Synth Strings #1 (2020-05-28) | `synth_strings` | [FreePats](http://freepats.zenvoid.org/) | CC0 |
| `tenor_sax.sf2` | Tenor Saxophone, from the Versilian Community Sample Library (2020-07-17) | `tenor_sax` | [FreePats](http://freepats.zenvoid.org/Reed/saxophone.html#TenorSax) | CC0 |
| `kalimba.sf2` | Kalimba (2019-07-23) | `kalimba` | [FreePats](http://freepats.zenvoid.org/Ethnic/kalimba.html) | CC0 |
| `world_percussion.sf2` | World percussion (2020-09-05): cajón, bongos, egg shaker, tambourine, castanets, maracas, darbuka, hand clap | hand percussion and shakers in kits `brushes`, `latin`, `tr808`, `tr909`, `soft_electro` | [FreePats](http://freepats.zenvoid.org/) | CC0 |
| `synth_percussion.sf2` | FreePats synthesizer percussion (2022-07-18) | kit `drum_machine` | [FreePats](http://freepats.zenvoid.org/) | CC0 |

Everything else is generated or ships with LMMS, so there is nothing else to download or license: ZynAddSubFX,
TripleOscillator, Organic and OPL2 presets, DrumSynth drum models and LMMS's factory samples (e.g. the crash
used for risers). After adding a SoundFont or instrument, `measure` records its level and octave in
`lmms-core/assets/levels.json`.

## Layout

```
lmms-core/        engine (scripts/), catalog levels (assets/levels.json), format references
lmms-<genre>/     SKILL.md, scripts/<genre>_pack.py (styles + patterns), assets/examples/ (templates),
                  references/ (style guides, feedback map), evals/ (test prompts, grader)
```

`lmms-core/references/genre-packs.md` explains how to add another genre.
