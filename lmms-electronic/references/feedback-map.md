# Feedback → edits

| they say | likely cause | change |
|---|---|---|
| "too repetitive", "sounds like a loop" | the same loop for too long (see the build's loop warnings) | split long sections into 8-bar blocks and change something in each: a part in or out, sequence patterns (`seq8` → `seq16` → `seq_dotted`), bass pattern, a second progression, a melody or answer phrase, a 4-bar drop — filter moves alone don't fix it |
| "takes too long to get going", "slow transitions" | long intro / 16-bar sections | reach the groove within 4 bars (bass and kick from bar 1, filters opening), 8-bar sections, no kick-only DJ intro |
| "boring", "flat" | no arc | a breakdown (drop drums + bass, filter closing) before the last main section, then everything back with the filter open; a harmony line in the last lead phrase |
| "too busy", "distracting" (focus) | too much melody / percussion | fewer lead notes (or none), `pulse_soft` / `shaker` instead of `pulse`, drop `perc`, `seq8` instead of `seq16`, `"mode": "bed"` |
| "too dark", "cold" | minor / filtered | maj9 / 6/9 chords, `soft_pad` / `analog_pad` instead of `void_pad` / `dream_pad`, open `pad_lp` (`tone`), brighter bells |
| "too bright", "harsh" | open filters, bright plucks | cap cutoffs at 3000–4000, `soft_arp` instead of `house_pluck` / `ping`, `tone.keys_lp` 5000 |
| "more energy" (minimal) | groove too thin | `four` instead of `four_min`, `rolling` bass, `pump` on pad and keys, `perc` + `shaker` layers, tempo +2–4 |
| "the pad is too loud / quiet" | balance | `mix.gains` for the Pad label (dB), or `pad.level` in a `move` |
| "I don't like that sound" | taste | swap the id: pads `soft_pad` / `analog_pad` / `sweep_pad` / `ice_pad` / `dream_pad` / `void_pad` / `space_choir` / `ethereal_pad`; plucks `soft_arp` / `house_pluck` / `pluck` / `pluck_arp` / `ping` / `glass_arp`; bells `chimes` / `soft_hammer` / `muffled_bells` / `crystal_bells` / `analog_bell` |
| "the bass is inaudible on my speakers" | `sub_bass` is a pure sine | `decay_bass` / `thick_bass` / `pluck_bass`, or keep the sub and double the root in the keys |
| "the fade is too long / abrupt" | fade length | change the last section's bars, or split it (hold, then `master.level` [1, 0] over 8 bars) |
| "no pumping" / "too much pumping" | pump depth | 0.3 subtle, 0.6 house, 0.8 heavy |
| "longer / shorter" | length | add or remove whole sections (keep the arc: intro → build → peak → break → peak → outro) |
