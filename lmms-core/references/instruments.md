# Instruments, kits and textures (scripts/catalog.py)

Every sound a song can use has a catalog id. All ids are shared by every genre skill; a genre pack may add
more (`catalog.INSTRUMENTS[id] = dict(...)`, then `measure`). Levels and octaves come from
`assets/levels.json`, written by `measure` and applied automatically when catalog.py loads.

## Sound sources

| kind | what | notes |
|---|---|---|
| `sf2` | SoundFonts in `<workingdir>/samples/soundfonts/` played by LMMS's sf2player (FluidSynth 1.1.6) | the sampled, realistic instruments. SF2 only (no SF3) |
| `zyn` | ZynAddSubFX presets from LMMS's factory data (954 of them) | synthetic; several sound an octave low (`octave` fixes it) |
| `tripleosc` | LMMS TripleOscillator, defined inline | simple sine / triangle sounds (`bell`, `warm_sine` bass) |
| samples | AudioFileProcessor on LMMS factory samples (`drums/…`) | the `dusty` and `dilla` kits |

**SoundFont licences** (copies in `soundfonts/licenses/`): the FreePats files are CC0 (public domain, no credit
needed); `generaluser_gs.sf2` is GeneralUser GS 1.472, free for any music, private or commercial. Everything
was chosen so the user can publish the music (their videos) without claims. Don't add samples of unclear
origin (e.g. uploads on the LMMS Sharing Platform) — the user rejected those.

## Instrument ids by role

| role | sampled (SoundFont) | synth (Zyn / TripleOsc) |
|---|---|---|
| keys | `upright_piano` `grand_piano` `tine_ep` (Rhodes-type) `chorus_ep` `fm_epiano` (DX7) `drawbar_organ` `clavinet` `nylon_guitar` `jazz_guitar` `muted_guitar` | `rhodes` `dx_rhodes` `fm_rhodes` `soft_piano` |
| lead | `tenor_sax` (keep ≤ E5) `kalimba` `piano_lead` `muted_trumpet` `gs_vibes` `music_box` `marimba` `gs_flute` `square_lead` | `vibes` `flute` `vibraphone` `bell` |
| pad | `synth_strings` `strings` `warm_pad` (any keys id also works as a pad, e.g. `drawbar_organ`) | `soft_saw_pad` `dark_strings` |
| bass | `upright_bass` `finger_bass` `slap_bass` `fretless_bass` `lately_bass` (TX81Z FM) | `warm_sine` |

Added for 16-bit game music (lmms-gamemusic), all GeneralUser GS unless marked:

| role | General MIDI (sampled) | FM - LMMS OpulenZ (Yamaha OPL2) |
|---|---|---|
| keys | `harp` `pizz_strings` `harpsichord` `accordion` `acoustic_guitar` `dist_guitar` | `opl_epiano` `opl_harp` `opl_organ` `opl_synth` |
| lead | `trumpet` `french_horns` `brass_section` `synth_brass` `oboe` `clarinet` `piccolo` `recorder` `pan_flute` `ocarina` `glockenspiel` `celesta` `xylophone` `tubular_bells` `saw_lead` | `opl_lead` `opl_brass` `opl_square` `opl_bells` `opl_vibes` `opl_clarinet` |
| pad | `orch_strings` `choir` | `opl_pad` |
| bass | `contrabass` `tuba` `synth_bass` | `opl_bass` |

Added for electronic music (lmms-electronic) - LMMS's own synths, generated sound (nothing to license):

| role | ids |
|---|---|
| pad | `soft_pad` `ice_pad` `sweep_pad` `dream_pad` `void_pad` `analog_pad` `space_choir` `ethereal_pad` (Organic, evolving) `hi_pad` `wind` (noise texture) |
| keys (plucks / arps / EP) | `house_pluck` `soft_arp` `glass_arp` `pluck_arp` `ping` `pluck` `ice_rhodes` |
| lead (bells / soft) | `chimes` `soft_hammer` `muffled_bells` `crystal_bells` `analog_bell` `soft_flute` |
| bass | `sub_bass` (pure sine) `decay_bass` `analog_bass` `thick_bass` `pluck_bass` `reso_bass` `acid_bass` (303-style) |

Most are Zyn presets (`z()` in catalog.py) or LMMS factory presets (`x()`), all measured; `retune=True` undoes
their measured tuning offsets (soft_arp +16, ping -13, glass_arp +10 cents).

FM kinds: `xpf` = an LMMS factory preset (`presets/OpulenZ/*.xpf`); `opl2` = a patch defined in catalog.py
(`params` → `lmmsgen.opl2`: per operator `mul`, `lvl` 0-63 (63 loudest), `a`/`d`/`r` times (0 fastest), `s`
sustain level (15 full), `perc` 1 = no sustain, `fm` 1 = FM / 0 = additive, `feedback` 0-7). `opl_bass` and
`opl_lead` are custom patches. A pad-measured sound (`orch_strings`, `choir`, `opl_pad`) used as `keys` or as a lead is raised to that slot's level automatically (ROLE_TARGET difference) unless the song overrides its `vol`. `tubular_bells` measures an octave high (weak fundamental) but is heard at the
written pitch, so levels.json keeps octave 0.

Catalog fields: `label` (track name), `vol`, `octave` (semitones added so it sounds at the written pitch),
`voicing` (lo, hi, centre MIDI for chord instruments — piano higher, guitar lower), `strum` (ticks between
chord notes), `chorus` (FluidSynth chorus), `gain` (FluidSynth gain for quiet SoundFonts), `measured`.

GeneralUser GS has ~250 more General-MIDI instruments than the catalog lists (brass section, choir, harp,
accordion, orchestral strings, synth leads/pads, 13 drum kits incl. Standard, Room, Power, Electronic,
808/909, Jazz, Brush, Orchestral). `python scripts/sf2info.py <file.sf2>` lists every preset; add one with
`gs(program, bank)` in catalog.py and run `measure --instruments <id>`.

## Drum kits

| kit | source | parts |
|---|---|---|
| `dusty` | LMMS factory samples | kick snare snare_body hat open_hat sidestick shaker ride crash reverse_crash |
| `dilla` | LMMS factory samples | kick snare clap hat open_hat sidestick shaker ride crash |
| `brushes` | GeneralUser "Brush" kit + FreePats egg shaker | kick snare brush_swirl sidestick hat pedal_hat open_hat ride crash shaker tom_hi tom_lo |
| `latin` | Brush kit kick/rim/cymbals + FreePats world percussion | + conga_hi conga_lo conga_mute bongo_hi bongo_lo claves tambourine shaker |
| `drum_machine` | FreePats analog-style synth percussion | kick snare clap sidestick hat open_hat crash ride shaker tom_hi tom_lo |
| `gs_standard` | GeneralUser GS Standard kit (GM) — 16-bit console / light rock | kick snare sidestick clap hat pedal_hat open_hat crash ride tom_hi tom_lo tambourine shaker |
| `gs_power` | GeneralUser GS Power kit — punchier, Genesis / arcade | same parts as `gs_standard` |
| `tr808` | GeneralUser GS "808/909" kit (real TR-808) + DrumSynth 808 claves / toms + FreePats shaker — downtempo | kick snare clap sidestick hat pedal_hat open_hat crash ride claves tom_hi tom_lo shaker tambourine |
| `tr909` | GeneralUser TR-909 kick / snare + DrumSynth 909 hats / clap / 808 rim — minimal, house | kick snare clap sidestick hat pedal_hat open_hat crash ride tom_hi tom_lo shaker tambourine |
| `soft_electro` | DrumSynth 808 kick / snare, "sleepy" hats and ride, claves, FreePats shaker — focus, ambient pulses | kick snare clap sidestick hat open_hat ride claves shaker crash |
| `gs_orchestral` | GeneralUser GS Orchestra kit — marches, castles, dungeons | kick (concert bass drum) snare sidestick claves (castanets) hat pedal_hat open_hat ride (orchestral) crash tambourine, tom_lo / tom_hi = timpani (chromatic F2–F3 in the SoundFont) tuned to the song: tonic + fifth of the first (loop) chord, or spec `"timpani": "<note>"` (engine.timpani_notes) |

Every kit also has `reverse_crash` (riser). A SoundFont drum part is one track playing a fixed MIDI note
(`catalog.hit(sf2, note, bank, patch)`); `sf2info.py file.sf2 128 <program>` prints a kit's key map. LMMS also
ships ~760 DrumSynth patches (TR-808/909/606, CR-78, LinnDrum, …) under `data/samples/drumsynth/` — usable as
AudioFileProcessor sources for new kits (verify they render before relying on them).

## Textures

`vinyl` (crackle), `rain`, `tape` (cassette hiss) — seamless loops generated on first use into
`<workingdir>/samples/lofi/` by textures.py; any song can layer them via `palette.textures`.

## Measuring

`measure` renders each unmeasured instrument / kit part next to a measured reference of the same role and
writes `vol` (to hit the ROLE_TARGET loudness), `octave` and tuning to `assets/levels.json`. The octave check
takes the lowest octave whose spectral peak is within 12 dB of the loudest (plain harmonic-product detection
was fooled by bright pickups and FM sub layers). Known facts: the Zyn vibes/vibraphone/dark strings and the
FreePats drawbar organ (16' drawbar) sound an octave low (octave +12); everything sampled is within ±10 cents.
Very quiet SoundFont drum parts get `gain` instead of a volume above 200.
