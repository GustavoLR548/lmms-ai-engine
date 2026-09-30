"""The lofi genre pack for lmms-core: five styles, their grooves and the lofi-only comping / bass figures.

Imported by scripts/lofi.py before the core command line runs. Everything here only registers things with
lmms-core's registry; the engine itself is genre-neutral (see lmms-core/references/genre-packs.md).
"""
from pathlib import Path

import registry as R

EXAMPLES = Path(__file__).resolve().parent.parent / "assets" / "examples"
PROG = "lofi.py"
DEFAULT_TEMPLATE = "slow-and-warm"

R.genre("lofi", "jazzy", drums="boombap")

# ================================================================== styles
R.style("jazzy",
        title="Jazzy boom-bap",
        about="Nujabes-style: Rhodes chords, vibes/flute hooks, dusty swung boom-bap, ii-V jazz harmony",
        bpm=(70, 86), swing=3, humanize=1, snare_lag=3, wow=0.0002,
        palette=dict(keys="rhodes", bass="warm_sine", pad="soft_saw_pad", kit="dusty", textures=["vinyl"]),
        leads=["vibes", "flute", "bell", "gs_vibes"],
        keys=["chop", "hold", "sync", "push", "sparse", "stabs", "whole", "filtered", "arp"],
        bass=["kick_lock", "hook", "walk", "bounce", "halftime", "whole"],
        drums=["boombap", "boombap_ghost", "boombap_busy", "ride", "halftime", "breakdown", "intro", "fade_out"])
R.style("bossa",
        title="Bossa lofi",
        about="nylon guitar comping, upright bass in the bossa pattern, rim clave + shaker + congas, "
              "straight 16ths, sax or flute melodies, lush maj7/m9/7(#11) harmony with chromatic ii-Vs",
        bpm=(64, 80), swing=0, humanize=2, snare_lag=0, wow=0.00015,
        palette=dict(keys="nylon_guitar", bass="upright_bass", pad="strings", kit="latin", textures=["vinyl"]),
        leads=["tenor_sax", "gs_flute", "muted_trumpet", "kalimba"],
        keys=["bossa", "bossa_soft", "whole", "arp", "sparse"],
        bass=["bossa", "walk", "whole"],
        drums=["bossa", "bossa_ride", "bossa_light", "brushes_light", "fade_out"],
        tone=dict(keys_lp=7500, keys_hp=90, keys_reverb=0.18, drums_lp=11000, drums_reverb=0.12, bass_lp=2500,
                  leads_lp=7000))
R.style("sleepy",
        title="Sleepy piano",
        about="a real upright piano alone or nearly alone: rolled chords with a left hand, slow broken "
              "arpeggios, brushes or no drums, strings/kalimba answers, cassette hiss, 58-72 BPM",
        bpm=(58, 72), swing=2, humanize=3, snare_lag=2, wow=0.0003,
        palette=dict(keys="upright_piano", bass="upright_bass", pad="strings", kit="brushes",
                     textures={"vinyl": -3, "tape": 0}),
        leads=["piano_lead", "kalimba", "music_box", "gs_vibes"],
        keys=["rolled", "rolled_half", "broken", "whole", "filtered"],
        bass=["none", "whole", "halftime"],
        drums=["none", "brushes_light", "brushes", "heartbeat", "fade_out"],
        tone=dict(keys_lp=7500, keys_hp=45, keys_reverb=0.32, drums_lp=9000, drums_reverb=0.2, master_lp=12500,
                  pad_reverb=0.5),
        feel=dict(keys=(0, 4)))
R.style("dilla",
        title="Dilla / neo-soul",
        about="off-grid 'drunk' drums (late kicks, early claps, loose hats), chorused EP or organ, "
              "chopped-sample keys (mpc), late synth bass, neo-soul harmony (m9/maj9 moving by steps and "
              "chromatic mediants), crushed drum bus",
        bpm=(76, 92), swing=5, humanize=2, snare_lag=0, wow=0.00025,
        palette=dict(keys="chorus_ep", bass="lately_bass", pad="drawbar_organ", kit="dilla", textures=["vinyl"]),
        leads=["gs_flute", "gs_vibes", "muted_trumpet", "square_lead"],
        keys=["mpc", "chop", "stabs", "hold", "sparse", "whole", "filtered"],
        bass=["hook", "kick_lock", "halftime", "whole"],
        drums=["dilla", "dilla_sparse", "dilla_ride", "halftime", "breakdown", "intro", "fade_out"],
        tone=dict(keys_lp=5000, drums_lp=8000, drums_crush=1, drums_reverb=0.06),
        feel=dict(kick=(4, 3), snare=(-1, 2), clap=(-5, 2), hat=(2, 4), open_hat=(2, 3), bass=(6, 3), keys=(3, 2)))
R.style("citypop",
        title="City-pop lofi",
        about="80s Tokyo night drive: DX7 FM electric piano, clean guitar 'cutting', slap or FM synth bass, "
              "string-machine pads, drum machine with 16th hats, sax or synth hooks, IVmaj7-III7-vi7 harmony, "
              "cassette tone",
        bpm=(80, 100), swing=1, humanize=1, snare_lag=0, wow=0.0003,
        palette=dict(keys="fm_epiano", keys2="jazz_guitar", bass="slap_bass", pad="synth_strings",
                     kit="drum_machine", textures={"tape": 0, "vinyl": -6}),
        leads=["tenor_sax", "square_lead", "muted_trumpet", "gs_vibes"],
        keys=["push", "sync", "hold", "offbeat", "whole", "filtered", "arp"],
        keys2=["cutting", "offbeat", "sparse"],
        bass=["slap", "octaves", "kick_lock", "hook", "whole"],
        drums=["citypop", "disco", "halftime", "breakdown", "intro", "fade_out"],
        tone=dict(keys_lp=9000, keys_reverb=0.25, drums_lp=12000, drums_reverb=0.14, leads_lp=8000, bass_lp=3500,
                  master_lp=13000))

# ================================================================== keys (lofi-only comping)
R.keys("chop", [(0, 5, 88, 0), (6, 3, 62, 0), (10, 4, 76, 0), (14, 2, 64, 1)], strum=0)
R.keys("stabs", [(0, 2, 86, 0), (3, 2, 64, 0), (6, 3, 74, 0), (11, 2, 62, 0), (13, 3, 70, 0)], strum=0)
R.keys("cutting", [(2, 1, 60, 0), (4, 1, 84, 0), (6, 1, 58, 0), (7, 1, 50, 0), (10, 1, 62, 0), (12, 1, 84, 0),
                   (14, 1, 58, 0)], strum=1)
R.keys("bossa", [[(0, 3, 80, 0), (3, 2, 62, 0), (6, 4, 72, 0), (10, 2, 64, 0), (12, 4, 70, 0)],
                 [(2, 2, 66, 0), (6, 3, 72, 0), (8, 2, 62, 0), (12, 2, 66, 0), (14, 2, 70, 1)]], strum=1)
R.keys("bossa_soft", [[(0, 6, 70, 0), (6, 4, 60, 0), (12, 4, 62, 0)],
                      [(2, 4, 60, 0), (8, 4, 62, 0), (14, 2, 60, 1)]], strum=1)

# ================================================================== bass
R.bass_fig("bossa", [(0, 58, "r", 96), (6, 20, "r", 68), (8, 58, "5", 86), (14, 20, "last", 70)])
R.bass_fig("slap", [(0, 30, "r", 100), (3, 10, "8", 76), (6, 20, "r", 88), (7, 10, "8", 70), (10, 20, "5", 88),
                    (12, 10, "r", 72), (14, 20, "last", 80)])

# ================================================================== drums
KICKS = {
    "boombap": [[0, 10], [0, 7, 10], [0, 10], [0, 3, 10]],
    "boombap_ghost": [[0, 7, 10], [0, 10, 13], [0, 7, 10], [0, 2, 10]],
    "boombap_busy": [[0, 10], [0, 8, 10], [0, 10], [0, 7, 10]],
    "ride": [[0, 10], [0, 8, 10], [0, 10], [0, 7, 10]],
    "soft": [[0, 10]],
    "dilla": [[0, 7, 10], [0, 3, 10, 13], [0, 7, 11], [0, 6, 10, 15]],
    "dilla_sparse": [[0, 10], [0, 11], [0, 10], [0, 7, 11]],
    "dilla_ride": [[0, 7, 10], [0, 10, 13], [0, 7, 11], [0, 10]],
    "citypop": [[0, 8, 10], [0, 6, 8], [0, 8, 10], [0, 6, 8, 14]],
}


def hats(style):
    def fn(dc):
        dc.hats8(40, 28)
        if style == "hats_rim":
            for st in (4, 12):
                dc.hit("sidestick", st, dc.V(52), 10, dc.song.snare_lag)
    return fn


def breakdown(dc):
    dc.hats8(40, 26)
    dc.hit("sidestick", 8, dc.V(58), 10, dc.song.snare_lag)


def halftime(dc):
    dc.hats8(40, 26)
    dc.hit("kick", 0, dc.V(96))
    dc.hit("kick", 11, dc.V(78))
    dc.hit("snare", 8, dc.V(90), 24, dc.song.snare_lag)


def boombap(style):
    """boombap / boombap_ghost / boombap_busy / ride / soft - the classic swung lofi hip-hop kit."""
    def fn(dc):
        rng, bis, t0, V, J, hit, sec = dc.rng, dc.bis, dc.t0, dc.V, dc.J, dc.hit, dc.sec
        snare_lag = dc.song.snare_lag
        kicks = KICKS.get(style, KICKS["boombap"])[bis % len(KICKS.get(style, KICKS["boombap"]))]
        soft = style == "soft"
        for st in kicks:
            hit("kick", st, V((100 if st == 0 else 84) - (26 if soft else 0)))
        for st in (4, 12):
            hit("snare", st, V(96 - (26 if soft else 0)), 24, snare_lag)
        if not soft and bis % 4 == 3:
            hit("snare", 15, V(40, 4), 16, 2)                      # ghost pickup
        if style == "boombap_ghost" and bis % 2:
            hit("snare", 9, V(34, 4), 16, 2)
        open_step = 14 if (bis % 4 == 3 and not soft) else (6 if style == "boombap_ghost" and bis % 4 == 1 else None)
        for st in range(0, 16, 2):
            if st == open_step:
                hit("open_hat", st, V(58), 30)
                continue
            acc = (64 if st % 4 == 0 else 46) - (18 if soft else 0)
            if style == "ride":
                dc.out.append(("ride", J(t0 + dc.step(st)), 30, V(acc - 6)))
            else:
                dc.out.append(("hat", J(t0 + dc.step(st)), 8, V(acc)))
        if style == "boombap_busy":
            for st in (3, 7, 11, 15):
                dc.out.append(("hat", J(t0 + dc.step(st)), 6, V(26, 4)))
        elif not soft and (style != "boombap" or bis % 2):
            hit("hat", 15, V(28, 4), 6)
        if style in ("boombap_busy", "ride") or sec.get("shaker"):
            for st in (2, 3, 6, 7, 10, 11, 14, 15):
                dc.out.append(("shaker", J(t0 + dc.step(st)), 8, V(36 if st % 4 == 2 else 22, 4)))
    return fn


def fade_out(dc):
    """soft kit -> hats + rim -> silence across the section"""
    q = dc.bis / dc.bars
    target = "soft" if q < 0.5 else ("hats_rim" if q < 0.75 else "none")
    if target == "none":
        return False
    return R.DRUMS[target](dc)


def intro(dc):
    """nothing for the first half, then hats + rim"""
    if dc.bis < dc.bars // 2:
        return False
    return R.DRUMS["hats_rim"](dc)


def bossa(style):
    def fn(dc):
        bis, t0, V, J, hit = dc.bis, dc.t0, dc.V, dc.J, dc.hit
        if style != "bossa_light":
            for st, vel in ((0, 80), (6, 58), (8, 72), (14, 60)):     # the bossa bass drum: 1, 2&, 3, 4&
                hit("kick", st, V(vel, 4))
        for st in ((0, 6, 12) if bis % 2 == 0 else (4, 10)):           # 2-bar rim clave
            hit("sidestick", st, V(66 if st in (0, 4) else 58, 4), 10)
        if style == "bossa_ride":
            for st in range(0, 16, 2):
                dc.out.append(("ride", J(t0 + dc.step(st)), 30, V(50 if st % 4 == 0 else 38)))
        else:
            for st in range(16):
                dc.out.append(("shaker", J(t0 + dc.step(st)), 8, V(44 if st % 4 == 2 else (30 if st % 2 == 0 else 22), 3)))
    return fn


def brushes(style):
    def fn(dc):
        bis, V, hit = dc.bis, dc.V, dc.hit
        for st in (0, 8):
            hit("brush_swirl", st, V(58, 4), 90)
        for st in (4, 12):
            hit("pedal_hat", st, V(50, 4), 10)
        if style == "brushes":
            hit("kick", 0, V(62, 4))
            if bis % 2:
                hit("kick", 8, V(46, 4))
            for st in (4, 12):
                hit("snare", st, V(64, 5), 20, dc.song.snare_lag)
            if bis % 4 == 3:
                hit("snare", 14, V(40, 4), 12, 2)
    return fn


def heartbeat(dc):
    dc.hit("kick", 0, dc.V(70, 3))
    dc.hit("kick", 3, dc.V(50, 3))


def dilla(style):
    def fn(dc):
        rng, bis, t0, V, hit = dc.rng, dc.bis, dc.t0, dc.V, dc.hit
        for st in KICKS[style][bis % 4]:
            hit("kick", st, V(100 if st == 0 else 86))
        for st in (4, 12):
            hit("snare", st, V(92), 24)
            hit("clap", st, V(76), 24)
        if style != "dilla_sparse" and bis % 2 == 1:
            hit("snare", 9 if bis % 4 == 1 else 7, V(34, 4), 12)            # ghost
        if style == "dilla_sparse":
            for st in (0, 4, 8, 12):
                hit("hat", st, V(48), 8)
        else:
            part = "ride" if style == "dilla_ride" else "hat"
            for st in range(0, 16, 2):
                if st == 14 and bis % 4 == 3:
                    hit("open_hat", st, V(56), 30)
                    continue
                if st not in (0, 8) and rng.random() < 0.1:
                    continue                                                # a skipped hat
                acc = 60 if st % 4 == 0 else 42 + rng.randint(-8, 10)
                dc.out.append((part, t0 + dc.step(st), 30 if part == "ride" else 8, V(acc)))
            if bis % 2 == 0:
                hit("hat", 15, V(30, 4), 6)
    return fn


def citypop(style):
    def fn(dc):
        bis, t0, V, J, hit = dc.bis, dc.t0, dc.V, dc.J, dc.hit
        for st in ([0, 4, 8, 12] if style == "disco" else KICKS["citypop"][bis % 4]):
            hit("kick", st, V(100 if st % 8 == 0 else 86))
        for st in (4, 12):
            hit("snare", st, V(94), 24)
            hit("clap", st, V(70), 24)
        for st in range(16):
            if style == "disco" and st in (2, 6, 10, 14):
                hit("open_hat", st, V(56), 20)
            elif style == "citypop" and st == 14 and bis % 2 == 1:
                hit("open_hat", st, V(58), 24)
            elif style == "disco" and st % 2 == 0:
                dc.out.append(("hat", J(t0 + dc.step(st)), 6, V(50)))
            else:
                dc.out.append(("hat", J(t0 + dc.step(st)), 6, V(58 if st % 4 == 0 else (46 if st % 2 == 0 else 30), 4)))
    return fn


for _s in ("hats", "hats_rim"):
    R.drums(_s, hats(_s))
R.drums("breakdown", breakdown)
R.drums("halftime", halftime)
for _s in ("boombap", "boombap_ghost", "boombap_busy", "ride", "soft"):
    R.drums(_s, boombap(_s))
R.drums("fade_out", fade_out)
R.drums("intro", intro)
for _s in ("bossa", "bossa_ride", "bossa_light"):
    R.drums(_s, bossa(_s))
for _s in ("brushes", "brushes_light"):
    R.drums(_s, brushes(_s))
R.drums("heartbeat", heartbeat)
for _s in ("dilla", "dilla_sparse", "dilla_ride"):
    R.drums(_s, dilla(_s))
for _s in ("citypop", "disco"):
    R.drums(_s, citypop(_s))


# ================================================================== hand-percussion layers (section flags)
def perc(dc):
    pat = [("conga_mute", 4, 60), ("conga_hi", 7, 56), ("conga_mute", 12, 58), ("conga_hi", 14, 62),
           ("conga_lo", 15, 66)]
    if dc.bis % 2:
        pat += [("bongo_hi", 2, 44), ("bongo_hi", 10, 46), ("bongo_lo", 11, 40)]
    for part, st, vel in pat:
        dc.out.append((part, dc.J(dc.t0 + dc.step(st)), 16, dc.V(vel, 5)))


def claves(dc):
    for st in ((0, 6, 12) if dc.bis % 2 == 0 else (4, 8)):               # son clave 3-2
        dc.hit("claves", st, dc.V(58, 4), 10)


def tambourine(dc):
    for st in (4, 12):
        dc.hit("tambourine", st, dc.V(52, 4), 16)


R.layer("perc", perc)
R.layer("claves", claves)
R.layer("tambourine", tambourine)
