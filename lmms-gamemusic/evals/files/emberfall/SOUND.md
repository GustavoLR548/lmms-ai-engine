# SOUND.md — Audio Style Guide

## Sonic Direction & References
Warm, hand-crafted 16-bit fantasy adventure: the soundtrack should feel like a lost SNES action-RPG
(Secret of Mana, Zelda: A Link to the Past, Chrono Trigger). Matches DESIGN.md's bright pixel-art forests,
villages and ruins.

## Music
- Genre / style: SNES-style orchestral fantasy (sampled instruments, soft echo)
- Instrument palette: french horns, flute, ocarina, oboe, harp, pizzicato and orchestral strings,
  contrabass or tuba, timpani and concert percussion, glockenspiel
- Avoid: synth leads, FM sounds, distorted guitar, electric or synth bass, modern drum machines
- Tempo range: 80–140 BPM
- Key / mode tendency: major for exploration and towns, minor for danger
- Loops vs. stingers: every area theme loops; victory and game-over are one-shot stingers

| Context | File | Loop? | Notes |
|---|---|---|---|
| title | assets/audio/music/title.ogg | yes | short fanfare intro is fine |
| overworld | assets/audio/music/overworld.ogg | yes | the main exploration theme |
| town | assets/audio/music/town.ogg | yes | |
| dungeon | assets/audio/music/dungeon.ogg | yes | planned |

## SFX Character
- Realism level: stylized
- Tone words: soft, wooden, chimey
- Space / reverb: short room
- Frequency slots: UI and pickups sit high (bells, plucks); impacts own the low mids
- Variation sets: footsteps (4), sword swings (3), hits (3)

## Voice
- Needed: no

## Technical Specs
| Category | Format | Sample rate | Channels | Loudness target | Max length |
|---|---|---|---|---|---|
| SFX | wav | 44.1 kHz | mono | peak -1 dBFS | 2 s |
| UI | wav | 44.1 kHz | mono | peak -6 dBFS | 0.5 s |
| Ambience | ogg | 44.1 kHz | stereo | -24 LUFS | loop |
| Music | ogg | 44.1 kHz | stereo | -18 LUFS | loop / stinger |

## File Layout & Naming
- Music: `assets/audio/music/<context>.ogg` (loop metadata next to it)
- SFX: `assets/audio/sfx/<family>/<name>_01.wav`
- UI: `assets/audio/ui/<name>.wav`

## Mix Priorities
Player feedback (hits, pickups) > UI > ambience > music. Music must never mask a hit.

## Audio Log
| Date | Asset | Tool / Model | Notes |
|---|---|---|---|
| 2026-09-12 | assets/audio/sfx/footsteps/grass_01.wav | ElevenLabs SFX | pre-existing, 4 variations |
| 2026-09-12 | assets/audio/ui/menu_select.wav | ElevenLabs SFX | pre-existing |
