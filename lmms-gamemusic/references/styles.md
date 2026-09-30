# The two 16-bit sounds, their instruments and the game patterns

A style is the console sound: default palette, tone (filters, echo, reverb) and which patterns suit it. The
*mood* (town, boss ...) is chosen separately (moods.md). Any instrument can be used in either style through
`palette` / `leads` — the style only sets defaults — but keep a track inside one sound unless the game's
SOUND.md mixes them.

## `snes` — 16-bit sampled (SNES-style)

The Super Nintendo played short samples of real instruments at 32 kHz through a soft (Gaussian) filter, with
a hardware echo that almost every soundtrack used on the melody. So: orchestral and folk instruments, a
slightly muffled top end (`master_lp` 11.5 kHz), a clear 1/8-note echo on the leads, modest reverb. Think
Chrono Trigger, Secret of Mana, Final Fantasy VI, Zelda: A Link to the Past, Donkey Kong Country.

Default palette: keys `harp`, bass `contrabass`, pad `orch_strings`, kit `gs_standard`.

| role | ids (written range that sounds best) | typical use |
|---|---|---|
| keys | `harp` (arp16, broken, rolled) | the RPG accompaniment — overworld, title, sad |
| | `pizz_strings` (march, pulse, stabs8) | towns, sneaking, comic |
| | `harpsichord` (march, arp) | castles, courts, puzzles |
| | `accordion` (march, offbeat) | taverns, harbour towns |
| | `acoustic_guitar` (arp, hold, arp16) | villages, campfire, travel |
| | `dist_guitar` (stabs8, brass_hits with `5` power chords) | boss, final battle |
| | `orch_strings` as keys (tremolo, whole) | tension, dungeon, battle backing |
| lead | `french_horns` (G4–E5; transpose −12 for tunes written around C5–C6) | heroic themes, overworld, title |
| | `trumpet` (C5–C6), `brass_section` (A4–A5) | fanfares, battle, castle |
| | `gs_flute` (C5–D6), `ocarina` (C5–C6), `recorder`, `pan_flute` | overworld, towns, forests |
| | `oboe` (D5–D6), `clarinet` (G4–C6, dark below C5) | pastoral, sad, mystery, dungeon |
| | `piccolo` (C6–C7) | playful doubling, marches |
| | `glockenspiel`, `celesta` (C6 and up), `xylophone`, `music_box` | sparkle, doubling, shops, ice levels |
| | `tubular_bells` (single long notes) | churches, ominous hits |
| pad | `orch_strings`, `strings` (slower), `choir`, `french_horns` | sustain under everything; choir = dungeon, boss, sacred |
| bass | `contrabass`, `tuba` (march!), `synth_bass`, `finger_bass`, `slap_bass` | orchestral / oompah / action / DKC-style funk |
| kit | `gs_standard` | light rock kit — most SNES soundtracks |
| | `gs_orchestral` | concert bass drum + snare, orchestral hi-hats and ride, castanets as claves, and timpani as toms — tuned to the song's tonic and fifth automatically (`toms` fill = timpani roll; `"timpani": "D"` in song.json sets the tonic by hand) — marches, castles, dungeons, fanfares |
| | `gs_power` | punchier rock kit — battles |
| | `brushes`, `latin` | jazzy shops / beach and jungle levels |

## `fm` — 16-bit FM (Genesis / DOS)

Yamaha FM chips: the Genesis / Mega Drive's YM2612 and the PC's OPL2 (AdLib / Sound Blaster). LMMS's OpulenZ
is an OPL2 — two operators, buzzy and metallic, very punchy on bass. Bright, dry mix (`master_lp` 14 kHz),
lightly crushed PCM-style drums, short echo. Think Streets of Rage, Sonic, Thunder Force, Gunstar Heroes, and
the DOS games of the era.

Default palette: keys `opl_epiano`, bass `opl_bass`, pad `opl_pad`, kit `gs_power`.

| role | ids | typical use |
|---|---|---|
| keys | `opl_epiano` (arp16, stabs8), `opl_harp` (arp16 — great as keys2), `opl_organ` (whole, stabs), `opl_synth` (offbeat, push) | comping, arpeggios |
| | `fm_epiano` (DX7 sample), `synth_strings` | lusher 80s colour |
| lead | `opl_lead` (brassy, vibrato — the main melody), `opl_brass` (stabs, fanfares), `opl_square` (hollow — counter-lines, harmony), `opl_bells` (glassy — bridges, ice), `opl_vibes`, `opl_clarinet` | melody |
| | `synth_brass`, `saw_lead`, `square_lead` (sampled synths) | fatter / brighter leads |
| pad | `opl_pad`, `synth_strings`, `warm_pad` | |
| bass | `opl_bass` (plucky slap-like FM — default), `lately_bass` (TX81Z FM sample), `synth_bass`, `slap_bass` | |
| kit | `gs_power` (default), `gs_standard`, `drum_machine` (analog drum machine — Streets of Rage club tracks) | |

## Patterns

Game patterns come from `scripts/game_pack.py`; lmms-core's common ones (spec-format.md) work too.

**keys**
| pattern | what | good for |
|---|---|---|
| `arp16` | 16th-note arpeggio up and down the chord (1 2 3 4 3 2 3 4) — *the* 16-bit accompaniment | harp, opl_epiano, opl_harp, celesta; very often as `keys2` |
| `arp16_up` | rising 16ths (1 2 3 4) — more urgent | battle, racing, mystery |
| `stabs8` | the chord on every 8th, accents on the beats | battle, action, boss |
| `tremolo` | soft 16th repetitions | tension: dungeon, boss, suspense (orch_strings as keys) |
| `brass_hits` | 1, 2&, 4 | fanfares, intros, castle |
| `march` | long 1, pickup on 2&, 3, 4 | towns, marches, oompah with tuba |
| `pulse` | quarter notes | calm towns, shops, sad scenes |
| common | `whole` `hold` `sync` `push` `offbeat` `sparse` `arp` (8ths) `rolled` `broken` (with a left hand) | |

**bass**
| pattern | what | good for |
|---|---|---|
| `march` | root / fifth on the beats with rests (oompah) | towns, castles, marches |
| `gallop` | 8th + two 16ths ("horse ride") | overworld, adventure, battle |
| `drive8` | straight 8th roots, last one leads to the next chord | action, racing, boss |
| `funk16` | syncopated 16ths with octave pops | Genesis funk, action stages |
| common | `octaves` (8th octaves — the FM classic) `whole` (pedal / sustained) `walk` `halftime` `kick_lock` `hook` `bounce` | |

**drums**
| pattern | what | good for |
|---|---|---|
| `adventure` | friendly pop-rock: 8th hats, kick 1 / 2& / 3, snare 2 and 4 | overworld, title |
| `march` | military snare with drags, roll into every 4th bar | castle, title, heroic (best on `gs_orchestral`) |
| `battle` | four-on-the-floor, 16th hats, snare pickups | battle, racing |
| `boss` | 8th kicks, crash every 4 bars, tom accents | boss |
| `townfolk` | soft kick 1 and 3, sidestick 2 and 4, shaker 8ths | town, shop |
| `dungeon` | a deep kick every other bar, a low tom / timpani answer every 4th | dungeon, cave, mystery |
| `fm_rock` | Genesis stage beat: 16th hats, open-hat lifts, ghost snare | action stage |
| `halftime` | half-time feel | bridges, breakdowns, slow tension |
| `none` | | calm scenes, intros |

**Section extras**: `"crash": true` (downbeat crash), `"riser": true`, `"pad": true`, `"fill"` on the last bar
(`build` snare 16ths — ideal at the loop's end, `pickup`, `toms` = timpani roll on `gs_orchestral`, `stop`,
`drop`), layers `"tambourine": true` (off-beat tambourine lift) and `"crash4": true` (a crash every 4 bars).

## Tone

Set by the style; override per song with `"tone"` (spec-format.md). The leads' echo is the most "16-bit"
parameter: `leads_echo_beats` (0.5 = an 8th), `leads_echo_fb` (repeats), `leads_echo_wet` — more for dreamy
and ice / space tracks, less for fast battles (it blurs 16ths).
