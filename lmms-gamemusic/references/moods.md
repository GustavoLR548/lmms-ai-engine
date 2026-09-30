# Moods — recipes by game context

Each recipe is a starting point: tempo, harmony, patterns, instruments and a loop form that work for that
context. Mix and adapt (a "sad town", an "underwater dungeon"), and always make the melody your own.
Progressions are Roman numerals in the song's MAJOR key; minor themes are vi-centred (example chords in
A minor = `"key": "C"`). With this skill a bare numeral is a triad (`"vi"` = Am, `"V7"` = G7).

Loop length = bars × 240 / BPM seconds (16 bars at 120 = 32 s, 32 bars at 140 = 55 s). Aim for 40–90 s unless
the user asks otherwise; shorter loops (16–24 bars) suit menus and very fast tracks.

| context | style | BPM | mode | drums | bass | keys (+ keys2) | leads |
|---|---|---|---|---|---|---|---|
| title / main theme | snes (fm) | 96–132 | major, heroic | march / adventure | march / gallop | arp16 harp, brass_hits | horns, trumpet → flute; brass harmony |
| overworld / field | snes | 112–144 | major / Mixolydian | adventure | gallop | arp16 (harp, guitar), stabs8 | horns, flute, trumpet, ocarina |
| town / village | snes | 88–116 | major, warm | townfolk / none | march (tuba), walk | march / pulse (pizz, accordion) + arp16 harp | flute, ocarina, oboe, recorder, clarinet |
| shop / menu / save | snes / fm | 96–120 | major 7ths | townfolk / none | walk, march | pulse, offbeat | celesta, glockenspiel, gs_vibes, opl_vibes, marimba |
| dungeon / cave / ruins | snes | 66–100 | minor, Phrygian | dungeon / none | whole (pedal), halftime | tremolo, sparse, arp16_up (slow harp) | clarinet (low), oboe, pan_flute, bells; choir pad |
| battle | snes / fm | 140–172 | minor | battle | gallop, drive8, octaves | stabs8 + tremolo / arp16_up | trumpet, brass, horns · opl_lead, saw_lead |
| boss | snes / fm | 150–180 (or 80–100 heavy) | minor, chromatic | boss | drive8, octaves | stabs8 (dist_guitar power chords), tremolo | brass_section, trumpet, opl_brass, saw_lead; choir / organ |
| castle / throne | snes | 84–112 | major or minor, stately | march (`gs_orchestral`) | march | brass_hits, march (harpsichord) | brass_section, trumpet, horns |
| sad / memories / cutscene | snes | 60–84 | minor or bittersweet major | none / soft halftime | whole, halftime | broken / rolled harp, pulse | oboe, flute, clarinet, piano_lead, music_box |
| action stage | fm | 138–170 | minor | fm_rock, battle | octaves, funk16 | stabs8 + arp16 (opl_harp) | opl_lead, opl_brass; opl_square harmony |
| racing / shmup | fm | 150–180 | minor / Mixolydian | battle | drive8, octaves | arp16_up, stabs8 | saw_lead, opl_square, synth_brass |
| mystery / puzzle / ice / space | either | 84–110 | Lydian, sus, whole-tone | none / dungeon / halftime | whole | arp16_up (celesta, harp, opl_bells), whole | glockenspiel, celesta, opl_bells; more echo |

## Harmony that sounds 16-bit

- **Heroic cadence** `bVI bVII I` (C: Ab Bb C) — the Zelda / Mario / Final Fantasy lift. Also a great last
  bar of a loop: `"bVI bVII"` in the final bar, then the loop starts on `I`.
- **Mixolydian drive** `I bVII IV I` (C Bb F C) — adventure without sweetness.
- **Royal road** `IV V iii vi` (F G Em Am) — the JRPG emotional progression; with 7ths (`IVmaj7 V7 iii7 vi`)
  for sad scenes and shops.
- **Pachelbel / canon** `I V vi iii IV I IV V` — castles, weddings, endings, sad themes.
- **Minor battle** `vi V IV III7` (Am G F E7, the Andalusian descent), `vi IV V vi`, `vi bVII bVI V7`...
  In A minor the harmonic-minor dominant is `III7` (E7) — use it at the loop's end.
- **Dark / dungeon** `vi bVII vi bVII` (Am Bb: Phrygian), `vi bVI` (Am Ab: chromatic mediant), a pedal (the
  same chord for 2–4 bars with the melody moving), `viio` / `#ivo` (diminished) as passing tension, `Iaug`.
- **Boss** power chords `vi5 IV5 V5`, half-step moves `vi5 bVII5`, diminished runs; keep the bass driving.
- **Lydian wonder** `I II` (C D — the D-major triad's F# is the #4): mystery, flying, space, ice.
- **Key change** (a classic in racing / action loops): write the section's chords a whole step up (in C: `II`
  = D, `V` = G→ `VI` = A, `vi` → `vii`) and give its leads `"transpose": 2`; step back down before the loop
  restarts so the wrap is in the home key.

## Melody

- **Motif first.** One or two bars with a recognisable rhythm (e.g. long–short–short–long), then an answer,
  then the motif again changed (higher, inverted, new ending). Players remember rhythm before pitch.
- **Range**: about an octave and a half; heroic tunes climb to their high point in bar 5–7 of an 8-bar phrase.
- **Call and response** between two leads (horn phrase → flute answer) keeps a long loop fresh.
- **Harmony line**: in the repeat of A, add a second lead with `"harmony": "below"` (it plays chord tones under
  the melody) — brass sections, twin flutes, FM leads in thirds.
- **Rest.** Gameplay loops need bars without melody (let the arpeggio carry them); dungeon and menu loops
  especially.
- **Fast runs** (16ths) may pass through non-chord tones; anything longer than an 8th should be a chord tone
  or a 6th / 9th. The checker enforces this.

## Loop forms

| length | form (loop part) | notes |
|---|---|---|
| 16 bars | A 8 · B 8 | menus, very fast battles |
| 24 bars | A 8 · B 8 · A' 8 | dungeons, shops |
| 32 bars | A 8 · A' 8 · B 8 · A'' 8 or A · B · A' · C | overworld, towns, stages, bosses |
| + intro | `"loop": {"from": "A"}` with a 1–4 bar intro (fanfare, drum build, stab + timpani roll) | title, battle, boss, stages |

Every loop form ends with a bar that leads home (V / V7 / III7 / bVII / bVI–bVII and a `fill`), and the repeat
of A differs from the first A (instrument, harmony line, keys2 arpeggio, crash4, tambourine...).

## Context notes

- **Title**: the game's identity — the main motif should be one you can reuse in other tracks. Intro fanfare.
- **Overworld**: the most-heard track of the game; strongest melody, forward motion (gallop bass), no
  sudden loud hits. 32 bars.
- **Town**: relaxed and friendly; swing 3–4 gives a lilting shuffle; less percussion; melody can breathe.
- **Dungeon**: space and dread, not volume: sparse drums, low register, long notes, a pedal bass; `"mode": "bed"`
  keeps it under combat sounds.
- **Battle**: short intro stab then straight in; energy from bass and drums, melody in brass; 24–32 bars.
- **Boss**: heavier and more chromatic than battle; an intro that builds (halftime + `build` fill).
- **Shop / menu**: loops for a long time while the player reads — gentle, no strong accents; 16–24 bars.
- **Sad scene**: often no drums; harp or piano broken chords, oboe or flute melody with suspensions.
