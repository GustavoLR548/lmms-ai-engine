# Writing lofi hip-hop that doesn't sound generated

Contents: 1 Feel · 2 Progressions · 3 Melodies · 4 Bass · 5 Drums · 6 Form & anti-repetition ·
7 Behind a voice · 8 Reference artists

## 1. Feel

- **Tempo**: lofi hip-hop lives at 68–90 BPM. 70–78 = sleepy, head-nod slow (this user's preference);
  80–90 = boom-bap bounce (Nujabes territory). Below 68 the drums start to drag.
- **Swing**: 3 ticks (~62 %) is the default nod. 4–5 plus `humanize` 2 and `snare_lag` 4–5 gives the
  drunk, behind-the-beat Dilla feel. 0–1 sounds quantised and stiff — avoid unless asked.
- **Dust**: vinyl texture, gentle tape wow (0.0002), filtered intro/outro keys, soft-attack Rhodes.

## 2. Progressions

Write in Roman numerals so key changes are free. Minor-feeling songs still use the relative MAJOR key
in `key` and centre on `vi` (e.g. key Eb, tonic chord `vi9` = Cm9).

Warm / nostalgic
- `ii9 · V13 · Imaj9 · vi11` — the classic; pair with `ii9 · V13 · Imaj9 · VI7alt` as the 8-bar answer
- `Imaj9 · vi9 · ii9 · V13sus`
- `IVmaj9 · III7alt · vi9 · "ii9 V13"` — strong hook: the alt chord pulls into vi

Melancholic / rainy (vi-centred)
- `vi9 · IVmaj9 · ii9 · III7alt`
- `vi9 · vi11 · IVmaj9 · III7alt`
- `vii m7b5 · III7alt · vi9 · vi9` (written `viim7b5` — the minor ii–V–i)

Dreamy / floating
- `IVmaj9 · Imaj9 · IVmaj9 · V13sus`
- `Imaj9 · bVIImaj9 · IVmaj9 · iv6` (the borrowed `iv6` is the "sigh")

Jazzy / bright
- `Imaj9 · VI7alt · ii9 · V13` (I–VI–ii–V turnaround)
- `iii7 · VI7alt · ii9 · V13`

Neo-soul / chromatic colour (great for bridges)
- `IVmaj9 · iv6 · iii7 · VI7alt`
- `bVIImaj9 · vi7 · v9 · V13sus` (descending, lands back on a hook in IV or I)

Rules of thumb: give the bridge chords the verse/hook never used; a `7alt` wants to fall a fifth
(`III7alt → vi`, `VI7alt → ii`); `13sus` floats — good as a section's last chord; end the song on `Imaj9`
(or `vi9` for a sad ending) held 2 bars.

## 3. Melodies

The engine rejects melody notes outside the chord's scale or a half-step against a held chord tone, so
most "wrong notes" are caught — but a line can be in key and still be dull. Make it sing:

- **Motif + answer**: bars 1–2 state a short idea (3–6 notes), bars 3–4 answer it (different rhythm,
  lands lower), bars 5–8 repeat the idea but change the ending (go higher, or resolve to "1"/"5").
- **Strong beats** (steps 0, 4, 8, 12) take chord tones or 9ths; weak 16ths can pass through scale tones.
- **Range**: roughly `"5,"` to `"5'"`; the top note of the song only once or twice. Vibes and flute both sit
  well between Bb4 and C6.
- **Space**: at least a beat of rest every two bars; phrase ends are long notes. Lofi melodies breathe.
- **Answers, not melodies**, in verses: 3–5 note fills in the last half of bars 4 and 8.
- **Solo sections**: 8th/16th lines are fine, but still land on chord tones at bar lines.
- **Re-use across hooks** but change the instrument (vibes → flute → flute + vibes `harmony: "below"`).
- Over `7alt` chords the good notes are b9, #9, 3, b13, b7 — they sound "bent"; resolve next bar.

## 4. Bass

- Roots on the downbeat, always. Movement happens on weak 16ths (steps 10, 14).
- Never a chromatic approach note under a sustained chord — a B under a Bb chord reads as "the chords
  are wrong" to listeners (it happened in this user's first track). The engine only picks passing
  notes from the chord's scale that don't rub against what the keys hold.
- Low and warm: roots between E1 and Eb2, triangle harmonics so phones still hear it.
- Styles by section: verse `kick_lock`, second verse `walk`, hook `hook`, bridge `halftime`/`whole`,
  solo `bounce`, outro `whole`.

## 5. Drums

- Boom-bap core: kick on 1 and the "and" of 3, snare on 2 and 4 laid back, 8th hats with accents.
- Variation every bar (the kick banks rotate), a ghost pickup every 4th bar, an open hat on bar 4's last 8th.
- Hooks get busier hats + shaker or a ride; bridges go half-time or drop the kick (`breakdown`).
- Section ends need an event: `pickup` (snare ghosts), `build` (snare roll into a hook), `stop` (drums cut on
  beat 3 — the next section hits harder), `drop` (a full bar without drums).
- `crash` only on hook downbeats; `riser` (reverse cymbal) into hooks and the first verse.

## 6. Form & anti-repetition

This user dislikes loops. Every song is through-composed with named sections.

Templates (bars; at 74 BPM one bar = 3.24 s):
- **~2:00** Intro 4 · Verse 8 · Hook 8 · Bridge 4 · Hook 8 · Outro 4 (36 bars)
- **~3:00** Intro 4 · Verse 8 · Hook 8 · Verse 8 · Bridge 8 · Hook 8 · Outro 8 (52 bars)
- **~3:40** Intro 4 · V 8 · H 8 · V 8 · Bridge 4+4 · H 8 · Solo verse 8 · H 8 · Outro 8 (68 bars) — see `slow-and-warm.json`

Checklist before building:
- Each section changes at least **two** of: keys pattern, bass style, drum style, lead (instrument or
  melody), pad on/off, texture.
- At least three different progressions (verse, hook, bridge); the bridge brings new chords.
- No two hooks identical: vary lead instrument, add harmony, swap hats→ride, add pad.
- Every section's last bar has a fill, stop or drop; hooks start with a crash and a riser into them.
- Something new appears in the second half (a solo, a harmony line, a new texture).

## 7. Behind a voice (`"mode": "bed"`)

Speech has no tempo to match — choose the tempo for mood. What matters is space:
- `mode: "bed"` (engine: leads −5 dB, 2.5 kHz dip on keys/leads/pad, softer hats).
- No continuous melodies; only short answers or the `bell` lead. Prefer keys `hold`/`whole`/`sparse`,
  drums `boombap` (not `busy`), no ride.
- Long videos: write a long through-composed song (repeat the verse/hook cycle with different leads and
  keys patterns) or 2–3 songs in the same key and tempo — never loop a 30-second section for 30 minutes.
- Deliver at −16 LUFS anyway; the user sets the bed level in their video editor (typically 12–15 dB under the voice).

## 8. Reference artists → settings

| reference | bpm | settings |
|---|---|---|
| Nujabes | 84–92 | swing 3, jazzy ii–V–I + alt chords, flute hooks, `walk` bass, `ride` in hooks, pad in bridge |
| J Dilla | 82–90 | swing 5, humanize 2, snare_lag 5, keys `chop`/`stabs`, few leads |
| Lofi Girl / chillhop study | 70–80 | filtered intro, `arp` keys, soft kit sections, vinyl + rain, bell/vibes answers |
| Tomppabeats / dusty | 72–82 | wow 0.0003, vinyl +3 dB, keys `chop`, short form (~2:00) |
| Idealism / Kupla (dreamy) | 68–76 | dreamy progressions, pad most of the song, sparse drums, vibes |
| "sad / rainy" | 68–74 | vi-centred progressions, m9/m11, flute long tones, rain texture |
