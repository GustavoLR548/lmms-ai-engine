"""The electronic genre pack for lmms-core: ambient, deep focus, minimal and downtempo.

Sounds are LMMS's own synths (Zyn / TripleOscillator / Organic presets - generated, nothing to license), the
GeneralUser GS 808/909 kit and LMMS's DrumSynth models. Electronic music lives on slow change, so most of a
song's movement is written per section with lmms-core's "move" (filter sweeps, swells, fades) and "pump"
(sidechain-style ducking) - see lmms-core references/spec-format.md. This module only registers styles and
patterns with the registry.

Phrases: every pattern here follows the 8-bar phrase by itself - small changes on the 4th bar, a turnaround on the
8th (fills, pickups, the kick dropping out every 16th bar), arps opening up an octave in the second half. That keeps
a bar from being an exact copy of the one 4 bars before, but a whole section still repeats every 8 bars, so the
arrangement has to change something every 8 bars (the engine's loop check, style loop_max_s, says where it doesn't).
"""
from pathlib import Path

import common
import registry as R

EXAMPLES = Path(__file__).resolve().parent.parent / "assets" / "examples"
PROG = "electronic.py"
DEFAULT_TEMPLATE = "focus"

R.genre("electronic", "focus", skill="lmms-electronic", keys="whole", bass="whole", drums="none")

# ================================================================== styles
R.style("ambient",
        title="Ambient",
        about="beatless or nearly: long evolving pads and drones, chords that change every 2-4 bars, scattered "
              "bells / chimes, sub bass or none, deep reverb and long echoes, filter swells and fades; Eno, "
              "Stars of the Lid, Hammock",
        bpm=(60, 90), swing=0, humanize=2, snare_lag=0, wow=0.00012, loop_max_s=48,
        palette=dict(keys="glass_arp", bass="sub_bass", pad="dream_pad", kit="soft_electro", textures={"tape": -4}),
        leads=["chimes", "crystal_bells", "soft_hammer", "muffled_bells", "analog_bell", "soft_flute", "kalimba",
               "music_box", "gs_vibes"],
        keys=["drone", "seq_dotted", "seq8", "sparse", "whole", "arp", "broken", "rolled"],
        bass=["none", "whole", "sub_pulse"],
        drums=["none", "ticks", "shaker", "pulse_soft", "halfstep"],
        tone=dict(keys_lp=7500, keys_hp=90, keys_reverb=0.45, keys_echo_beats=0.75, keys_echo_fb=0.45,
                  keys_echo_wet=0.25, drums_lp=8000, drums_reverb=0.3, leads_lp=7500, leads_echo_beats=1.5,
                  leads_echo_fb=0.5, leads_echo_wet=0.3, leads_reverb=0.5, pad_level=1.7, pad_reverb=0.6, pad_hp=80, pad_lp=9000,
                  bass_lp=250))
R.style("focus",
        title="Deep focus",
        about="steady and unobtrusive for working and studying: a soft pulse (or none), a repeating pluck / "
              "arp figure, warm pad, sub bass, slow harmony (2-3 progressions alternating), soft melody phrases "
              "that come and go - the pulse stays while the figure, layers and chords change every 8 bars; "
              "Tycho, Bonobo's quiet side, 'deep focus' playlists",
        bpm=(72, 100), swing=1, humanize=1, snare_lag=0, wow=0.0001, loop_max_s=30,
        palette=dict(keys="soft_arp", bass="sub_bass", pad="soft_pad", kit="soft_electro", textures=[]),
        leads=["soft_hammer", "chimes", "kalimba", "gs_vibes", "muffled_bells", "soft_flute", "music_box", "marimba"],
        keys=["seq8", "seq16", "seq_dotted", "pulse8", "whole", "sparse", "arp", "broken"],
        bass=["sub_pulse", "whole", "downtempo", "halftime"],
        drums=["pulse", "pulse_soft", "halfstep", "shaker", "ticks", "none"],
        tone=dict(keys_lp=6500, keys_hp=110, keys_reverb=0.3, keys_echo_beats=0.75, keys_echo_fb=0.3,
                  keys_echo_wet=0.12, drums_lp=9000, drums_reverb=0.15, leads_lp=7000, leads_echo_beats=0.75,
                  leads_echo_fb=0.35, leads_echo_wet=0.2, leads_reverb=0.35, pad_level=1.5, pad_reverb=0.5, pad_hp=120, pad_lp=6000,
                  bass_lp=300))
R.style("minimal",
        title="Minimal / deep",
        about="minimal techno and deep house: four-on-the-floor 909, offbeat hats, a rolling or offbeat bass, "
              "short chord stabs with echo (often one chord for a long time), pads pumping against the kick, and "
              "the whole track built by adding, removing and swapping parts every 8 bars while filters open; "
              "Kompakt, Lawrence, Dixon, early Border Community",
        bpm=(116, 128), swing=1, humanize=1, snare_lag=0, wow=0.0, loop_max_s=24,
        palette=dict(keys="house_pluck", bass="decay_bass", pad="analog_pad", kit="tr909", textures=[]),
        leads=["ping", "glass_arp", "chimes", "crystal_bells", "analog_bell", "pluck"],
        keys=["stab_off", "stab_dub", "seq16", "pulse8", "whole", "sparse"],
        bass=["offbeat", "rolling", "minimal", "sub_pulse", "whole"],
        drums=["four", "four_min", "four_kick", "four_break", "none"],
        tone=dict(keys_lp=8000, keys_hp=180, keys_reverb=0.2, keys_echo_beats=0.75, keys_echo_fb=0.4,
                  keys_echo_wet=0.18, drums_lp=15000, drums_reverb=0.05, leads_lp=8000, leads_echo_beats=0.75,
                  leads_echo_fb=0.4, leads_echo_wet=0.2, leads_reverb=0.2, pad_level=1.4, pad_reverb=0.35, pad_hp=250, pad_lp=5000,
                  bass_lp=1200))
R.style("downtempo",
        title="Downtempo",
        about="chill electronic / trip-hop: a swung broken beat on 808s, warm electric-piano chords, round synth "
              "bass, lush sweeping pads, melodic hooks on bells, flute or kalimba, a little vinyl; Bonobo, "
              "Emancipator, Nightmares on Wax, Tycho's warmer tracks",
        bpm=(80, 100), swing=3, humanize=2, snare_lag=2, wow=0.00015, loop_max_s=30,
        palette=dict(keys="ice_rhodes", bass="thick_bass", pad="sweep_pad", kit="tr808", textures={"vinyl": -8}),
        leads=["soft_flute", "kalimba", "gs_vibes", "chimes", "muffled_bells", "gs_flute", "music_box", "analog_bell"],
        keys=["hold", "sync", "push", "sparse", "whole", "seq8", "arp", "stab_dub"],
        bass=["downtempo", "hook", "kick_lock", "halftime", "whole"],
        drums=["broken", "breaks", "halfstep", "pulse", "none"],
        tone=dict(keys_lp=6500, keys_reverb=0.28, keys_echo_beats=0.75, keys_echo_fb=0.3, keys_echo_wet=0.1,
                  drums_lp=10000, drums_reverb=0.12, leads_lp=7000, leads_echo_beats=0.75, leads_echo_fb=0.35,
                  leads_echo_wet=0.22, leads_reverb=0.35, pad_level=1.2, pad_reverb=0.5, pad_hp=150, pad_lp=6000, bass_lp=900))

# ================================================================== keys
S16 = 12

# data patterns: (16th step, length in 16ths, velocity, plays-next-chord)
R.keys("drone", [(0, 16, 70, 0)], strum=0, tie=True)                     # held chord, tied across bars


def phrase(base, bar4, bar8):
    """an 8-bar cycle of bar variants: the base bar, a small change on bar 4, a turnaround on bar 8"""
    return [base, base, base, bar4, base, base, base, bar8]


_P8 = [(st, 1, 78 if st % 4 == 0 else 60, 0) for st in range(0, 16, 2)]
R.keys("pulse8", phrase(_P8, _P8[:6] + [(13, 1, 62, 0), (15, 1, 56, 0)],
                        _P8[:6] + [(12, 1, 70, 0), (13, 1, 56, 0), (14, 1, 64, 0), (15, 1, 58, 0)]), strum=0)
_SO = [(2, 1, 84, 0), (6, 1, 74, 0), (10, 1, 82, 0), (14, 1, 72, 0)]
R.keys("stab_off", phrase(_SO, _SO[:3] + [(13, 1, 70, 0), (15, 1, 62, 0)],
                          _SO[:2] + [(9, 1, 72, 0), (11, 1, 78, 0), (14, 2, 80, 0)]), strum=0)
R.keys("stab_dub", [[(3, 1, 80, 0), (10, 1, 70, 0)],
                    [(0, 1, 76, 0), (6, 1, 66, 0), (11, 1, 72, 0)],
                    [(3, 1, 80, 0), (10, 1, 70, 0), (14, 1, 60, 0)],
                    [(6, 1, 72, 0), (11, 2, 76, 0)],
                    [(3, 1, 80, 0), (10, 1, 70, 0)],
                    [(0, 1, 76, 0), (6, 1, 66, 0), (11, 1, 72, 0)],
                    [(3, 1, 80, 0), (10, 1, 70, 0), (14, 1, 60, 0)],
                    [(3, 1, 74, 0), (7, 1, 66, 0), (10, 1, 72, 0), (13, 1, 64, 0), (15, 1, 58, 0)]], strum=0)


def seq(order, step, gate, up=0):
    """A repeating sequence through the chord: a note every `step` 16ths (1 = 16ths, 2 = 8ths, 3 = dotted 8ths),
    each held `gate` 16ths. The position runs on from bar to bar (a dotted-8th figure drifts against the bar
    like a delay line), velocity accents the first note of each cycle and rises slowly through the section. In
    bars 5-8 of each 8-bar phrase the highest step of the figure jumps an octave (the arp "opens up")."""
    top = max(order)
    def fn(song, b, track, rng, inst, pick):
        bars = int(song.sections[b["sec"]]["bars"])
        lift = 10 * b["bis"] / (bars - 1) if bars > 1 else 0
        t_bar = b["tick"]
        k0 = (b["bar"] * 16 + step - 1) // step                  # first global step index inside this bar
        k = k0
        while True:
            t16 = k * step - b["bar"] * 16                         # 16th position inside this bar
            if t16 >= 16:
                break
            t = t_bar + song.step(t16)
            seg = song.seg_at(t)
            v = pick(seg["voicing"])
            o = order[k % len(order)]
            n = v[o % len(v)] + up + (12 if b["bis"] % 8 >= 4 and o == top else 0)
            end = min(t + int(gate * S16), seg["end"])                # never rings into the next chord
            vel = (90 if k % len(order) == 0 else 78) + lift + rng.randint(-4, 4)
            song.add(track, "keys", t + 1, max(6, end - t - 2), n, vel, b["sec"])
            k += 1
    return fn


R.keys_fn("seq16", seq([0, 1, 2, 3, 1, 2, 3, 2], 1, 1.5))
R.keys_fn("seq16_hi", seq([0, 1, 2, 3, 1, 2, 3, 2], 1, 1.5, up=12))
R.keys_fn("seq8", seq([0, 2, 1, 3], 2, 3))
R.keys_fn("seq8_hi", seq([0, 2, 1, 3], 2, 3, up=12))
R.keys_fn("seq_dotted", seq([0, 1, 2, 3, 2], 3, 5))

# ================================================================== bass (figures resolved per chord)
def phrased_bass(name, base, bar4, bar8):
    """a bass figure with a change on bar 4 and a pickup on bar 8 of each 8-bar phrase"""
    figs = phrase(base, bar4, bar8)
    R.bass_fn(name, lambda song, bc: common.bass_figure(song, bc, figs[bc.b["bis"] % 8]))


_SP = [(0, 44, "r", 92), (4, 44, "r", 78), (8, 44, "r", 86), (12, 44, "last", 78)]
phrased_bass("sub_pulse", _SP, _SP, _SP[:3] + [(12, 20, "8", 74), (14, 20, "last", 80)])
_OB = [(2, 20, "r", 96), (6, 20, "r", 86), (10, 20, "r", 94), (14, 20, "last", 84)]
phrased_bass("offbeat", _OB, _OB[:3] + [(14, 10, "8", 80), (15, 10, "last", 76)],
             _OB[:2] + [(10, 20, "r", 94), (12, 10, "8", 78), (14, 20, "last", 86)])
_RO = [(st, 9, "last" if st == 15 else "r", 92 if st % 4 == 2 else (80 if st % 2 else 76)) for st in range(16) if st % 4]
phrased_bass("rolling", _RO, [n if n[0] != 14 else (14, 9, "8", 84) for n in _RO],
             [n for n in _RO if n[0] < 13] + [(13, 9, "8", 84), (14, 9, "8", 88), (15, 9, "last", 92)])
_MI = [(3, 10, "r", 90), (6, 20, "r", 82), (10, 10, "8", 78), (11, 10, "r", 88), (14, 16, "last", 80)]
phrased_bass("minimal", _MI, _MI, _MI[:3] + [(11, 10, "r", 88), (13, 10, "8", 80), (15, 10, "last", 84)])
R.bass_fig("downtempo", [(0, 60, "r", 96), (7, 18, "r", 72), (10, 40, "5", 86), (14, 20, "last", 78)])


# ================================================================== drums
def phrase_pos(dc):
    """(bar 4 of the phrase, bar 8 = turnaround, every 16th bar = a bigger turnaround); a section's own fill
    takes the place of the turnaround"""
    ph = dc.bis % 8
    turn = ph == 7 and not (dc.bis == dc.bars - 1 and dc.sec.get("fill"))
    return ph == 3, turn, turn and dc.bis % 16 == 15


def four(style):
    """four / four_min / four_kick / four_break - the four-on-the-floor family"""
    def fn(dc):
        V, J, hit, bis, t0 = dc.V, dc.J, dc.hit, dc.bis, dc.t0
        bar4, turn, big = phrase_pos(dc)
        if style != "four_break":
            for st in (0, 4, 8, 12):
                if not (big and st == 12):                         # the kick drops out on beat 4 every 16 bars
                    hit("kick", st, V(100 if st == 0 else 92, 3), 30)
        if style == "four_kick":
            for st in (2, 6, 10) + (() if turn else (14,)):
                hit("open_hat" if bar4 and st == 14 else "hat", st, V(40, 4), 8)
            if turn:
                for st in (12, 13, 14, 15):
                    dc.out.append(("hat", J(t0 + dc.step(st)), 6, V(30 + (st - 12) * 8, 3)))
            return
        if style in ("four", "four_break"):
            for st in (4, 12):
                hit("clap", st, V(78, 4), 20)
            if bar4:
                hit("clap", 15, V(40, 4), 20)
            if turn:
                for st in (13, 14, 15) if big else (14, 15):
                    hit("clap", st, V(46 + (st - 13) * 10, 4), 20)
            for st in (2, 6, 10, 14):
                hit("open_hat", st, V(52, 4), 20)
            for st in range(1, 16, 2):
                dc.out.append(("hat", J(t0 + dc.step(st)), 6, V(28, 3)))
        else:                                                      # four_min: clicky, no clap
            for st in range(16):
                acc = 58 if st % 4 == 2 else (34 if st % 2 else 42)
                dc.out.append(("hat", J(t0 + dc.step(st)), 6, V(acc, 4)))
            rim = (3, 11) if bis % 2 == 0 else (3, 11, 14)
            if turn:
                rim = (3, 10, 13, 15)
            for st in rim:
                hit("sidestick", st, V(56, 4), 10)
            if bar4:
                hit("open_hat", 14, V(46, 4), 20)
    return fn


def pulse(style):
    """pulse (kick 1 and 3, rim 2 and 4, shaker 8ths) / pulse_soft (kick on 1, shaker)"""
    def fn(dc):
        V, J, hit, t0 = dc.V, dc.J, dc.hit, dc.t0
        bar4, turn, big = phrase_pos(dc)
        hit("kick", 0, V(90 if style == "pulse" else 80, 3), 30)
        if style == "pulse":
            hit("kick", 8, V(80, 3), 30)
            for st in (4, 12):
                hit("sidestick", st, V(62, 4), 10)
        if turn:
            hit("kick", 14, V(64, 3), 30)                          # a soft pickup into the next phrase
        for st in range(0, 12 if big else 16, 2):                  # every 16 bars the shaker takes a breath
            dc.out.append(("shaker", J(t0 + dc.step(st)), 8, V(62 if st % 4 == 2 else 46, 3)))
        if bar4:
            for st in (13, 15):
                dc.out.append(("shaker", J(t0 + dc.step(st)), 8, V(40, 3)))
    return fn


def halfstep(dc):
    """half-time: kick 1 and the 'a' of 2, clap / snare on 3, soft 8th hats"""
    V, J, hit, t0 = dc.V, dc.J, dc.hit, dc.t0
    hit("kick", 0, V(88, 3), 30)
    hit("kick", 7, V(66, 3), 30)
    hit("clap", 8, V(74, 4), 20)
    bar4, turn, big = phrase_pos(dc)
    if turn:
        hit("kick", 10, V(70, 3), 30)
        hit("open_hat", 14, V(44, 4), 20)
    for st in range(0, 16, 2):
        if not (turn and st == 14):
            dc.out.append(("hat", J(t0 + dc.step(st)), 6, V(40 if st % 4 == 0 else 30, 3)))
    if bar4:
        dc.out.append(("hat", J(t0 + dc.step(15)), 6, V(28, 3)))


def shaker(dc):
    for st in range(16):
        dc.out.append(("shaker", dc.J(dc.t0 + dc.step(st)), 8, dc.V(62 if st % 4 == 2 else (46 if st % 2 == 0 else 34), 3)))


def ticks(dc):
    """sparse random clicks (claves / rim / hat) - a texture, not a beat"""
    for st in range(16):
        if dc.rng.random() < 0.14:
            part = dc.rng.choice(["claves", "hat", "sidestick"])
            dc.out.append((part, dc.J(dc.t0 + dc.step(st)), 8, dc.V(30, 6)))


BROKEN_KICKS = [[0, 10], [0, 7, 10], [0, 10, 13], [0, 3, 10]]


def broken(style):
    """broken / breaks - downtempo beats: kick off the grid, snare 2 and 4, swung 16th hats with ghosts"""
    def fn(dc):
        V, J, hit, bis, t0 = dc.V, dc.J, dc.hit, dc.bis, dc.t0
        for st in BROKEN_KICKS[bis % 4] + ([11] if style == "breaks" and bis % 2 else []):
            hit("kick", st, V(96 if st == 0 else 82, 3), 30)
        for st in (4, 12):
            hit("snare", st, V(90, 4), 24, dc.song.snare_lag)
        if style == "breaks":
            for st in (7, 15) if bis % 2 else (9,):
                hit("snare", st, V(36, 4), 12, 2)
        for st in range(16):
            if st == 14 and bis % 4 == 3:
                hit("open_hat", st, V(54, 4), 24)
                continue
            if style == "broken" and st % 2 and dc.rng.random() < 0.5:
                continue
            dc.out.append(("hat", J(t0 + dc.step(st)), 6, V(52 if st % 4 == 0 else (40 if st % 2 == 0 else 26), 4)))
    return fn


for _s in ("four", "four_min", "four_kick", "four_break"):
    R.drums(_s, four(_s))
for _s in ("pulse", "pulse_soft"):
    R.drums(_s, pulse(_s))
R.drums("halfstep", halfstep)
R.drums("shaker", shaker)
R.drums("ticks", ticks)
for _s in ("broken", "breaks"):
    R.drums(_s, broken(_s))


# ================================================================== section flags (layers)
def shaker_layer(dc):
    for st in range(16):
        dc.out.append(("shaker", dc.J(dc.t0 + dc.step(st)), 8, dc.V(54 if st % 4 == 2 else 36, 3)))


def perc(dc):
    """syncopated claves / rim - 3-3-2 over the bar"""
    turn = dc.bis % 8 == 7
    for st, part in ((0, "claves"), (3, "sidestick"), (6, "claves"), (10, "sidestick"), (13, "claves")) + \
            (((14, "claves"), (15, "sidestick")) if turn else ()):
        dc.hit(part, st, dc.V(44, 5), 10)


def ride(dc):
    for st in (2, 6, 10, 14):
        dc.hit("ride", st, dc.V(44, 4), 30)


def clap(dc):
    for st in (4, 12):
        dc.hit("clap", st, dc.V(70, 4), 20)


R.layer("shaker", shaker_layer)
R.layer("perc", perc)
R.layer("ride", ride)
R.layer("clap", clap)
