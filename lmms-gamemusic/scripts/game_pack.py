"""The 16-bit game-music pack for lmms-core: two console sounds (SNES-style samples, Genesis/DOS FM) and the
patterns game themes are built from. Moods (overworld, town, dungeon, battle, boss ...) are not styles - they
choose tempo, harmony and which of these patterns to use (references/moods.md).
"""
from pathlib import Path

import registry as R

EXAMPLES = Path(__file__).resolve().parent.parent / "assets" / "examples"
PROG = "gamemusic.py"
DEFAULT_TEMPLATE = "snes-town"

R.genre("game", "snes", skill="lmms-gamemusic", drums="adventure")
# game harmony is triad-based: a bare "I" is a major triad, "vi" a minor triad, "V7" a plain dominant 7th (the
# jazz qualities stay available by name: Imaj7, Imaj9, ii9, V13 ...). Fast scalar melodies pass through
# non-chord tones, so only notes held an 8th or longer against a half-step clash count as rubs.
R.chords(major="triad", minor_numeral={"": "mtriad", "7": "m7", "9": "m9", "o": "dim", "dim": "dim"},
         alias={"maj": "triad", "m": "mtriad", "min": "mtriad", "7": "dom7", "sus": "sus4"}, rub_min_overlap=24)

# ================================================================== styles (the console sound)
R.style("snes",
        title="16-bit sampled (SNES-style)",
        about="sample-based console sound: orchestral strings, harp/pizzicato, horns and trumpets, woodwinds, "
              "bells, a light rock kit (or the orchestral kit: concert drums, timpani, castanets), soft echo on the melody, a slightly "
              "muffled top end like the SNES's 32 kHz samples. RPG / adventure / Zelda-Mana-Chrono feel",
        bpm=(60, 170), swing=0, humanize=1, snare_lag=0, wow=0.0,
        palette=dict(keys="harp", bass="contrabass", pad="orch_strings", kit="gs_standard", textures=[]),
        leads=["french_horns", "trumpet", "gs_flute", "oboe", "ocarina", "piccolo", "glockenspiel", "brass_section",
               "clarinet", "pan_flute", "celesta"],
        keys=["arp16", "arp", "tremolo", "brass_hits", "march", "pulse", "whole", "hold", "rolled", "broken"],
        bass=["march", "gallop", "drive8", "walk", "halftime", "whole"],
        drums=["march", "adventure", "battle", "boss", "townfolk", "dungeon", "halftime", "none"],
        tone=dict(master_lp=11500, keys_lp=9000, keys_hp=90, keys_reverb=0.25, drums_lp=11000, drums_reverb=0.12,
                  leads_lp=8000, leads_echo_beats=0.5, leads_echo_fb=0.35, leads_echo_wet=0.2, leads_reverb=0.18,
                  pad_reverb=0.35, bass_lp=3000))
R.style("fm",
        title="16-bit FM (Genesis / DOS)",
        about="Yamaha FM synthesis (OPL2 / AdLib - the DOS and, roughly, Mega Drive sound): plucky FM bass, "
              "brassy FM leads, FM e-piano and bells, 16th-note arpeggios, punchy slightly crushed PCM drums, "
              "dry mix. Action stages, racing, shmups, boss fights",
        bpm=(90, 180), swing=0, humanize=1, snare_lag=0, wow=0.0,
        palette=dict(keys="opl_epiano", bass="opl_bass", pad="opl_pad", kit="gs_power", textures=[]),
        leads=["opl_lead", "opl_brass", "opl_square", "opl_bells", "synth_brass", "saw_lead", "opl_clarinet"],
        keys=["arp16", "stabs8", "brass_hits", "tremolo", "arp", "push", "sync", "offbeat", "whole"],
        bass=["octaves", "funk16", "drive8", "gallop", "kick_lock", "whole"],
        drums=["adventure", "battle", "boss", "fm_rock", "halftime", "dungeon", "none"],
        tone=dict(master_lp=14000, keys_lp=10000, keys_hp=150, keys_reverb=0.08, drums_lp=12000, drums_reverb=0.04,
                  drums_crush=1, leads_lp=9000, leads_echo_beats=0.75, leads_echo_fb=0.3, leads_echo_wet=0.12,
                  leads_reverb=0.1, pad_reverb=0.2, bass_lp=5000))

# ================================================================== keys
S16 = 12


def arp16(order):
    """16th-note arpeggio through the chord (the signature 16-bit accompaniment)."""
    def fn(song, b, track, rng, inst, pick):
        for st in range(16):
            t = b["tick"] + song.step(st)
            seg = song.seg_at(t)
            v = pick(seg["voicing"])
            n = v[order[st % len(order)] % len(v)]
            song.add(track, "keys", t + 1, min(S16 + 6, seg["end"] - t - 1), n,
                     (74 if st % 4 == 0 else 58) + rng.randint(-4, 4), b["sec"])
    return fn


R.keys_fn("arp16", arp16([0, 1, 2, 3, 2, 1, 2, 3]))
R.keys_fn("arp16_up", arp16([0, 1, 2, 3]))
# data patterns: (16th step, length in 16ths, velocity, plays-next-chord)
R.keys("stabs8", [(st, 1, 84 if st % 4 == 0 else 66, 0) for st in range(0, 16, 2)], strum=0)
R.keys("tremolo", [(st, 1, 70 if st % 4 == 0 else 56, 0) for st in range(16)], strum=0)
R.keys("brass_hits", [(0, 3, 90, 0), (6, 2, 76, 0), (12, 4, 84, 0)], strum=1)
R.keys("march", [(0, 3, 84, 0), (7, 1, 60, 0), (8, 3, 80, 0), (12, 2, 64, 0)], strum=1)
R.keys("pulse", [(0, 4, 72, 0), (4, 4, 58, 0), (8, 4, 66, 0), (12, 4, 56, 0)], strum=1)

# ================================================================== bass (figures resolved per chord)
R.bass_fig("march", [(0, 40, "r", 96), (4, 18, "5", 70), (8, 40, "r", 90), (12, 18, "5", 70)])
R.bass_fig("gallop", [(0, 20, "r", 100), (2, 10, "r", 74), (3, 10, "r", 80), (4, 20, "r", 94), (6, 10, "r", 72),
                      (7, 10, "8", 78), (8, 20, "r", 98), (10, 10, "r", 74), (11, 10, "r", 80), (12, 20, "5", 92),
                      (14, 10, "r", 72), (15, 10, "last", 80)])
R.bass_fig("drive8", [(st, 16, "last" if st == 14 else "r", 100 if st % 4 == 0 else 80) for st in range(0, 16, 2)])
R.bass_fig("funk16", [(0, 14, "r", 100), (3, 10, "8", 74), (4, 10, "r", 84), (6, 14, "r", 88), (9, 10, "8", 72),
                      (10, 14, "5", 88), (12, 10, "r", 80), (14, 10, "8", 76), (15, 10, "last", 78)])


# ================================================================== drums
def march(dc):
    """military / RPG march: kick on 1 and 3, snare on 2 and 4 with a drag of 16ths, roll into bar 4"""
    V, hit, bis = dc.V, dc.hit, dc.bis
    hit("kick", 0, V(90))
    hit("kick", 8, V(80))
    for st in (4, 12):
        hit("snare", st, V(84), 16)
    for st in (6, 7, 14, 15):
        hit("snare", st, V(46, 4), 10)
    if bis % 4 == 3:
        for st in (9, 10, 11):
            hit("snare", st, V(52, 4), 10)


def adventure(dc):
    """driving but friendly pop-rock kit: 8th hats, kick 1 / 2& / 3, snare 2 and 4"""
    V, J, hit, bis, t0 = dc.V, dc.J, dc.hit, dc.bis, dc.t0
    for st in ((0, 6, 8) if bis % 2 == 0 else (0, 8, 10)):
        hit("kick", st, V(96 if st == 0 else 82))
    for st in (4, 12):
        hit("snare", st, V(90))
    for st in range(0, 16, 2):
        if st == 14 and bis % 4 == 3:
            hit("open_hat", st, V(58), 24)
            continue
        dc.out.append(("hat", J(t0 + dc.step(st)), 8, V(62 if st % 4 == 0 else 46)))


def battle(dc):
    """fast and urgent: four-on-the-floor kick with pickups, snare 2 and 4, 16th hats, ride-bell drive"""
    V, J, hit, bis, t0 = dc.V, dc.J, dc.hit, dc.bis, dc.t0
    for st in (0, 4, 8, 12):
        hit("kick", st, V(98 if st == 0 else 88))
    if bis % 2:
        hit("kick", 15, V(70))
    for st in (4, 12):
        hit("snare", st, V(96))
    for st in range(16):
        dc.out.append(("hat", J(t0 + dc.step(st)), 6, V(58 if st % 4 == 0 else (46 if st % 2 == 0 else 32))))
    if bis % 4 == 3:
        for st in (13, 14, 15):
            hit("snare", st, V(60 + (st - 13) * 10), 10)


def boss(dc):
    """relentless: 8th-note kicks, snare 2 and 4, crash on every 4th bar, tom accents"""
    V, hit, bis = dc.V, dc.hit, dc.bis
    for st in range(0, 16, 2):
        hit("kick", st, V(100 if st % 8 == 0 else 84))
    for st in (4, 12):
        hit("snare", st, V(100))
    for st in (2, 6, 10, 14):
        hit("hat", st, V(56), 8)
    if bis % 4 == 0:
        hit("crash", 0, V(80), 60)
    if bis % 2:
        hit("tom_hi", 14, V(70), 12)
        hit("tom_lo", 15, V(76), 12)


def townfolk(dc):
    """light and bouncy: soft kick on 1 and 3, sidestick on 2 and 4, shaker 8ths"""
    V, J, hit, t0 = dc.V, dc.J, dc.hit, dc.t0
    hit("kick", 0, V(72))
    hit("kick", 8, V(62))
    for st in (4, 12):
        hit("sidestick", st, V(70), 10)
    for st in range(0, 16, 2):
        dc.out.append(("shaker", J(t0 + dc.step(st)), 8, V(48 if st % 4 == 2 else 34)))


def dungeon(dc):
    """sparse and heavy: a deep kick every other bar, a low tom / timpani answer every 4th bar"""
    V, hit, bis = dc.V, dc.hit, dc.bis
    if bis % 2 == 0:
        hit("kick", 0, V(84), 60)
    if bis % 4 == 3:
        hit("tom_lo", 8, V(70), 40)
        hit("tom_lo", 11, V(58), 30)


def fm_rock(dc):
    """Genesis stage beat: kick 1, 2&, 3&, snare 2 and 4 with a ghost, 16th hats with open-hat lifts"""
    V, J, hit, bis, t0 = dc.V, dc.J, dc.hit, dc.bis, dc.t0
    for st in (0, 6, 10):
        hit("kick", st, V(96 if st == 0 else 84))
    for st in (4, 12):
        hit("snare", st, V(94))
    hit("snare", 15, V(40, 4), 10)
    for st in range(16):
        if st in (2, 10) and bis % 2:
            hit("open_hat", st, V(54), 20)
        else:
            dc.out.append(("hat", J(t0 + dc.step(st)), 6, V(54 if st % 4 == 0 else (42 if st % 2 == 0 else 30))))


def halftime(dc):
    """half-time feel for bridges and tension: kick 1 and 3&, snare on 3"""
    dc.hats8(40, 26)
    dc.hit("kick", 0, dc.V(96))
    dc.hit("kick", 11, dc.V(78))
    dc.hit("snare", 8, dc.V(90), 24)


for _n, _f in (("march", march), ("adventure", adventure), ("battle", battle), ("boss", boss),
               ("townfolk", townfolk), ("dungeon", dungeon), ("fm_rock", fm_rock), ("halftime", halftime)):
    R.drums(_n, _f)


# ================================================================== section flags (layers)
def tambourine(dc):
    for st in (2, 6, 10, 14):
        dc.hit("tambourine", st, dc.V(48, 4), 12)


def crash4(dc):
    """a crash on the first beat of every 4th bar - lift for choruses / B sections"""
    if dc.bis % 4 == 0:
        dc.hit("crash", 0, dc.V(78), 60)


R.layer("tambourine", tambourine)
R.layer("crash4", crash4)
