# Turning listener feedback into spec changes

Claude cannot hear the track. The user's words are the only ear in the loop, so treat every comment as
precise information: find WHERE (timestamp → section/bar via the build summary; bar = 240/bpm seconds)
and WHAT (the rows below), change the fewest things that address it, rebuild, and say what you changed.
Keep the previous mp3 (versions are numbered) so they can compare.

| they say | likely cause | change in song.json |
|---|---|---|
| "too fast" / "too slow" | tempo | `bpm` ±6–10 (stay in the style's range); re-check form length |
| "repetitive", "loops", "boring" | sections too similar | apply the anti-repetition checklist (music-guide §6): new progression for a bridge, different keys/bass/drum styles per section, alternate lead instruments, add a solo verse, shorten sections to 4 bars |
| "too busy", "distracting", "fights my voice" | too many moving parts | fewer leads (answers only), keys `hold`/`whole`, drums `boombap` not `busy`/`ride`, drop shaker, `mode: "bed"` |
| "empty", "needs more" | too sparse | pad in hooks, vibes answers in verses, `boombap_busy`, keys `stabs`/`sync`, a harmony line in the last hook |
| "chords sound off / wrong" at a time | a real clash, or harsh colour | run `build`: the checker lists half-step rubs. If clean, the colour is the issue — swap `7alt`/`13` for `9`/`maj9`/`m7`, lower `wow`, check the lead notes at that bar |
| "melody is annoying / cheesy" | too many notes, too prominent | fewer notes, longer rests, lower `vel` (−10), switch to `bell` or `vibes`, keep it to hooks |
| "sounds cheap / synthetic" | a preset or lead too exposed | lower that track in `mix.gains` (−3 dB), more keys reverb (`tone.keys_reverb` 0.3), darker `tone.leads_lp` 5000, swap lead instrument |
| "darker", "more muffled", "more lofi" | brightness | `tone.keys_lp` 4000, `tone.drums_lp` 8000, `wow` 0.0003, vinyl +3, more `filtered` sections |
| "brighter", "clearer" | brightness | `tone.keys_lp` 7500, `tone.drums_lp` 12000, `wow` 0.0001 |
| "drums too loud / quiet" | balance | `mix.gains` Kick/Snare/Snare body ±2–3 dB (hats separately) |
| "bass too much / boomy" | balance | `mix.gains.Bass` −2 to −3; bass style `whole`/`hook` instead of `walk`/`bounce` |
| "can't hear the bass" | phone speakers | `mix.gains.Bass` +2; it already has triangle harmonics |
| "hi-hats annoying" | hat density | drop `boombap_busy`, `mix.gains.Hat` −3 |
| "sadder" | harmony + tempo | vi-centred progressions, m9/m11/m6, slower, flute long tones, rain |
| "happier", "sunnier" | harmony | I-centred, maj9 and 6/9, brighter tone, vibes |
| "jazzier" | harmony + rhythm | ii–V–I with `13` and `7alt`, `walk` bass, `ride` hooks, vibes solo verse |
| "more like <artist>" | style | music-guide §8 table |
| "the intro is too long/quiet" | form / level | intro 2–4 bars; filtered channel already +6 dB |
| "longer" / "shorter" | form | add/remove a verse+hook pair or change section bars (keep multiples of the progression) |
| "ending is abrupt" | outro | outro `fade_out` drums, `whole` bass, last progression bars repeat `Imaj9` so it rings 2 bars |
| "they all sound the same", "same instruments" | palette + form reuse | a different `style` (references/styles.md), and check `lofi.py history`: new key, tempo band, chord instrument, kit and form |
| "more real / less synthetic" | Zyn / TripleOsc presets exposed | sampled SoundFont instruments: `tine_ep`/`upright_piano` for keys, `upright_bass`/`finger_bass`, `tenor_sax`, `gs_vibes` |
| "drums feel robotic / too quantized" | timing | raise `humanize`; add `feel` lags (kick +3, hat +2 with jitter 3); `dilla` style for the extreme |
| "too drunk / sloppy" (Dilla) | feel too strong | halve the `feel` lags and jitters, `swing` 4 |
| "chops too choppy / glitchy" | mpc hits | use `mpc` in fewer sections, `hold` or `whole` in the others; raise `tone.keys_reverb` |
| "guitar too busy" (bossa / city-pop) | comping density | `bossa_soft` instead of `bossa`; keys2 `sparse` or none in verses |
| "piano too plain" (sleepy) | voicings / motion | alternate `broken` and `rolled_half`; add `kalimba` answers; strings `pad` in the second half |
| "sax too loud / honky" | lead exposure | `mix.gains["Tenor sax"]` −3, `tone.leads_lp` 5500, fewer long high notes (keep it below E5) |

When a comment is vague ("something feels off around 1:30"), look at that bar in the summary, name
the candidates in one sentence ("at 1:30 the bridge starts: new chords, half-time drums, and the flute
comes in — is it one of those?") rather than guessing silently.
