# Lofi pack patterns (scripts/lofi_pack.py)

These are added on top of lmms-core's common vocabulary (`../../lmms-core/references/spec-format.md`: whole,
filtered, hold, sync, sparse, push, offbeat, arp, rolled, rolled_half, broken, mpc; bass whole, kick_lock,
hook, walk, halftime, bounce, octaves; fills pickup, build, stop, drop, toms). Section default drums: `boombap`.

## Keys
- `chop`: short stabs like a chopped sample; the last 16th anticipates the next chord (verses).
- `stabs`: busy rhythmic chops.
- `cutting`: 16th guitar chops accenting 2 and 4 (city-pop, usually as `keys2`).
- `bossa` / `bossa_soft`: 2-bar bossa guitar comping (A bar / B bar), strummed low-to-high.

## Bass
- `bossa`: root on 1 and 2&, fifth on 3, pickup on 4&.
- `slap`: root / octave pops in 16ths (city-pop).

## Drums
- `boombap`: kick/snare backbeat, 8th hats, ghost pickups. `boombap_ghost`: + ghost snares, open-hat
  variations (good second verse). `boombap_busy`: + 16th ghost hats + shaker (hooks). `ride`: ride cymbal
  instead of hats (jazzier hooks). `soft`: quiet kit.
- `halftime`: snare on 3 (bridges). `breakdown`: hats + sidestick on 3 (no kick). `hats`, `hats_rim`.
- `intro`: nothing, then hats + sidestick for the second half. `fade_out`: soft → hats → silence.
- `bossa`: kick 1-2&-3-4&, 2-bar rim clave, 16th shaker. `bossa_ride`: ride instead of shaker.
  `bossa_light`: rim + shaker only.
- `brushes`: swirls on 1 and 3, pedal hat on 2 and 4, soft kick + brush snare. `brushes_light`: swirls +
  pedal hat only. `heartbeat`: two soft kicks per bar.
- `dilla`: rotating off-kilter kicks, snare + clap, ghost snares, skipped hats (pair with the style's `feel`).
  `dilla_sparse`: quarter hats. `dilla_ride`.
- `citypop`: 16th hats, snare + clap, open hat every 2 bars. `disco`: four on the floor + open hats on the
  off-beats.

## Section flags (layers)
- `shaker`: shaker 16ths on any boombap groove.
- `perc`: congas + bongos. `claves`: son clave 3-2. `tambourine`: on 2 and 4. (Kits with those parts: `latin`.)
