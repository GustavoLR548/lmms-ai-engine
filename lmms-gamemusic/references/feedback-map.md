# Feedback → edits

| they say | likely cause | change |
|---|---|---|
| "I can hear where it loops", "the loop jumps" | musical seam (the end doesn't lead back) or a real seam problem | read `seam:` in the make output. SEAMLESS → it's musical: end on V / V7 / III7 / bVII, add a melody pickup into the first note, `fill: "build"`, remove anything that sounds like an ending. Not seamless → re-run `make`; if it persists run `loopcheck` on the file and report the numbers |
| "gets repetitive / annoying after a few loops" | loop too short or one idea | 24–32 bars with a B part; vary the repeat of A (new lead, harmony line, keys2 arp16, crash4); leave some bars without melody |
| "too busy", "fights the sound effects" | dense mids / constant melody | `"mode": "bed"`; keys `pulse` or `whole` instead of `stabs8`; drop keys2; lower lead `vel`; rests in the melody; no `crash4` |
| "not epic / heroic enough" | small palette, low energy | horns or brass lead, `bVI bVII I` cadence, `march` or `adventure` drums with `crash: true`, `gallop` bass, `pad: true`, harmony line in A' |
| "too happy for a dungeon / battle" | major harmony | vi-centred progressions, Phrygian `vi bVII`, `III7` dominants, lower lead register, clarinet / oboe / choir |
| "too dark / scary" | minor + low register | relative major for the B part (`IV V I`), brighter leads (flute, glockenspiel), less tremolo |
| "more retro / more 16-bit" | too clean or too lush | `snes`: lower `master_lp` (10000), more lead echo (`leads_echo_wet` 0.25); `fm`: `drums_crush` 2, opl_* instruments only |
| "too harsh / buzzy" (fm) | bright FM leads | `leads_lp` 6500, `opl_square` or `opl_clarinet` instead of `opl_lead`, `master_lp` 11000 |
| "too slow / too fast" | tempo | ±10–20 BPM within the mood's range (the loop length changes — say so) |
| "melody is forgettable" | no motif | rewrite A around a 2-bar rhythmic motif, repeat it with a change, climb to a high point near the end of the phrase |
| "the intro is too long / short" | intro bars | 1–2 bars for battles, 2–4 for title / boss; `loop.from` names the first looping section |
| "too loud / quiet next to my other tracks" | loudness target | `--lufs` (SOUND.md's target); re-run `make` |
| "the loop is too long / short" | bars | add or remove whole 8-bar sections (keep the bar count a multiple of 4) |
| "I want an 8-bit / NES version" | not this skill's sound yet | say so; LMMS has NES / Game Boy / SID emulators (Nescaline, FreeBoy, SID) — lmms-core would need catalog entries for them |
