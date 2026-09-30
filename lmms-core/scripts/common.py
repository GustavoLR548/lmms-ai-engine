"""Genre-neutral pattern vocabulary every lmms-* genre skill gets for free.

keys:  whole filtered hold sparse push sync offbeat arp | piano: rolled rolled_half broken | mpc (chopped sample)
bass:  whole kick_lock hook walk halftime bounce octaves
fills: pickup build stop drop toms
Drum grooves are genre identity, so they all live in the genre packs.
"""
import registry as R
from lmmsgen import TPB

S16 = 12


def bass_root(ch):
    return 28 + (ch.root - 28) % 12          # E1 .. Eb2


def lh_root(ch):
    return 36 + (ch.root - 36) % 12          # piano left hand: C2 .. B2


# ------------------------------------------------------------------ keys (data)
# hits: (16th step, length in 16ths, velocity, plays-next-chord)
R.keys("whole", [(0, 16, 80, 0)], strum=2, tie=True)
R.keys("filtered", [(0, 16, 80, 0)], strum=2, tie=True, track="keys_filtered")
R.keys("hold", [(0, 10, 84, 0), (10, 6, 64, 0)], strum=1)
R.keys("sync", [(0, 3, 86, 0), (3, 5, 70, 0), (10, 6, 74, 0)], strum=1)
R.keys("sparse", [(0, 6, 76, 0), (11, 5, 60, 0)], strum=1)
R.keys("push", [(0, 8, 84, 0), (8, 6, 70, 0), (14, 2, 68, 1)], strum=1)
R.keys("offbeat", [(2, 2, 74, 0), (6, 2, 66, 0), (10, 2, 72, 0), (14, 2, 64, 0)], strum=0)


# ------------------------------------------------------------------ keys (procedural)
def arp(song, b, track, rng, inst, pick):
    order = [0, 1, 2, 3, 2, 1, 2, 3]
    for k, st in enumerate(range(0, 16, 2)):
        t = b["tick"] + song.step(st)
        seg = song.seg_at(t)
        end = min(t + 5 * S16, seg["end"])
        song.add(track, "keys", t + 1 + rng.randint(-1, 1), end - t - 2, seg["voicing"][order[k]],
                 (70 if k % 4 == 0 else 58) + rng.randint(-5, 5), b["sec"])


def piano(pattern):
    """Piano with a left hand: 'rolled' (one rolled chord per chord, pedal held), 'rolled_half' (re-rolled on
    beat 3), 'broken' (pedalled broken-chord 8ths: LH root + fifth, then the voicing up and down)."""
    def fn(song, b, track, rng, inst, pick):
        sec = b["sec"]
        for seg in b["segs"]:
            s0, s1 = seg["start"], seg["end"]
            v, root = seg["voicing"], lh_root(seg["chord"])
            fifth = root + 7 if (root + 7) % 12 in seg["chord"].scale else root + 12
            base = 66 + rng.randint(-4, 4)
            if pattern == "broken":
                order = [root, fifth] + [v[i] for i in (0, 1, 2, 3, 2, 1)]
                for k, st in enumerate(range(0, (s1 - s0) // S16, 2)):
                    t = s0 + song.step(st) + (1 if st else 0)
                    song.add(track, "keys", t, s1 - t - 3, order[k % len(order)],
                             (base if k % 4 == 0 else base - 10) + rng.randint(-4, 4), sec)
                continue
            hits = [s0]
            if pattern == "rolled_half" and s1 - s0 >= TPB:
                hits.append(s0 + TPB // 2)
            for h, t in enumerate(hits):
                end = hits[h + 1] if h + 1 < len(hits) else s1
                vel = base - 8 * h
                song.add(track, "keys", t + 1, end - t - 3, root, vel + 2, sec)
                if h == 0 and s1 - s0 >= TPB // 2:
                    song.add(track, "keys", t + S16 * 4 + 2, end - t - S16 * 4 - 4, fifth, vel - 16, sec)
                roll = 7 + rng.randint(0, 4)
                for i, n in enumerate(v):
                    song.add(track, "keys", t + 4 + (i + 1) * roll, end - t - 6 - (i + 1) * roll, n,
                             vel - 4 + i * 2 + rng.randint(-3, 3), sec)
    return fn


# chopped-sample keys (chops.py renders the record): hits (step, length in 16ths, velocity, reverse) per bar
# variant; a pack may replace MPC_VARIANTS with its own chop rhythms
MPC_VARIANTS = [
    [(0, 3, 96, 0), (3, 2, 70, 0), (6, 4, 84, 0), (10, 2, 72, 0), (12, 4, 80, 0)],
    [(0, 6, 94, 0), (7, 2, 70, 0), (10, 3, 80, 0), (14, 2, 72, 1)],
    [(0, 3, 96, 0), (3, 3, 74, 0), (8, 5, 86, 0), (14, 2, 70, 0)],
    [(0, 6, 92, 0), (6, 2, 72, 0), (10, 2, 78, 0), (12, 4, 74, 1)],
]


def mpc(song, b, track, rng, inst, pick):
    """Re-trigger the attack of the chord's 'record'; reversed slices use the current chord (harmony-safe)."""
    variant = MPC_VARIANTS[(b["bis"] + (b["bar"] // 8)) % len(MPC_VARIANTS)]
    for st, ln, vel, rev in variant:
        t = b["tick"] + song.step(st)
        seg = song.seg_at(t)
        end = min(t + ln * S16, seg["end"])
        song.chops.append(dict(start=t, len=end - t, src=seg["start"], vel=vel + rng.randint(-5, 5), rev=rev,
                               sec=b["sec"]))
        for n in seg["voicing"]:               # invisible copy for the harmony checker
            song.add("chops_ref", "keys", t, end - t, n, vel, b["sec"])


R.keys_fn("arp", arp)
for _p in ("rolled", "rolled_half", "broken"):
    R.keys_fn(_p, piano(_p), keys2=False)
R.keys_fn("mpc", mpc, keys2=False)


# ------------------------------------------------------------------ bass
def bass_whole(song, bc):
    sec = bc.sec
    for seg in bc.b["segs"]:
        prev = song.seg_at(seg["start"] - 1) if seg["start"] > 0 else None
        if prev and prev["chord"].name == seg["chord"].name and prev["sec"] == sec and \
                song.sections[sec].get("bass") == "whole":
            continue
        end = seg["end"]
        for nseg in song.segments:
            if nseg["start"] == end and nseg["chord"].name == seg["chord"].name and nseg["sec"] == sec:
                end = nseg["end"]
        song.add("bass", "bass", seg["start"], end - seg["start"] - 6, bass_root(seg["chord"]), bc.v(92), sec)


def bass_classic(style):
    """The original hip-hop bass lines; bars with two chords share one figure."""
    def fn(song, bc):
        b, t0, sec, v = bc.b, bc.t0, bc.sec, bc.v
        if len(b["segs"]) >= 2:
            s1, s2 = b["segs"][0], b["segs"][-1]
            r1, r2 = bass_root(s1["chord"]), bass_root(s2["chord"])
            song.add("bass", "bass", t0, 78, r1, v(98), sec)
            song.add("bass", "bass", t0 + song.step(6), 18, r1 + 12, v(70), sec)
            song.add("bass", "bass", s2["start"], 70, r2, v(96), sec)
            n, is_ant = bc.last_note(s2)
            song.add("bass", "bass", t0 + song.step(14), 22, n, v(74), sec, ant=is_ant)
            return
        seg = b["segs"][0]
        r = bass_root(seg["chord"])
        fifth = r + 7 if (r + 7) % 12 in seg["chord"].scale else r + 12
        n_last, is_ant = bc.last_note(seg)
        if style == "kick_lock":
            notes = [(0, 80, r, 100), (song.step(10), 40, fifth, 80), (song.step(14), 26, n_last, 82)]
        elif style == "hook":
            notes = [(0, 118, r, 100), (song.step(10), 40, r + 12, 76), (song.step(14), 20, n_last, 72)]
        elif style == "walk":
            up = next((n for n in range(r + 1, r + 6) if n % 12 in seg["chord"].scale and not song.rubs(n, seg)),
                      r + 12)
            notes = [(0, 44, r, 98), (48, 44, up, 78), (96, 44, fifth, 84), (144, 44, n_last, 76)]
        elif style == "halftime":
            notes = [(0, 118, r, 96), (song.step(10), 60, fifth, 78)]
            is_ant = False
        else:   # bounce
            pop = r + 12 if b["bis"] % 2 else fifth
            notes = [(0, 80, r, 100), (song.step(7), 16, r, 66), (song.step(10), 40, pop, 80),
                     (song.step(14), 20, n_last, 72)]
        for i, (st, ln, n, vel) in enumerate(notes):
            song.add("bass", "bass", t0 + st, ln, n, v(vel), sec, ant=(is_ant and i == len(notes) - 1))
    return fn


def bass_figure(song, bc, fig):
    """Step-based figure resolved against the chord sounding at each step (see registry.bass_fig)."""
    b, t0, sec = bc.b, bc.t0, bc.sec
    for st, ln, what, vel in fig:
        t = t0 + song.step(st)
        seg = song.seg_at(t)
        r = bass_root(seg["chord"])
        is_ant = False
        if what == "r":
            n = r
        elif what == "8":
            n = r + 12
        elif what == "5":
            n = r + 7 if (r + 7) % 12 in seg["chord"].scale else r + 12
            n = n - 12 if n > 45 else n
        else:   # last: into the next bar
            if seg is not b["segs"][-1]:
                n = r
            else:
                n, is_ant = bc.last_note(seg)
        end = t + ln if is_ant else min(t + ln, seg["end"] - 2)
        song.add("bass", "bass", t, end - t, n, bc.v(vel), sec, ant=is_ant)


R.bass_fn("whole", bass_whole)
for _s in ("kick_lock", "hook", "walk", "halftime", "bounce"):
    R.bass_fn(_s, bass_classic(_s))
R.bass_fig("octaves", [(0, 18, "r", 98), (2, 16, "8", 76), (4, 18, "r", 90), (6, 16, "8", 72), (8, 18, "r", 94),
                       (10, 16, "8", 76), (12, 18, "r", 88), (14, 16, "last", 76)])


# ------------------------------------------------------------------ fills (the section's last bar)
def _fill_stop(dc):
    dc.out = [e for e in dc.out if e[1] < dc.t0 + dc.step(8)]


def _fill_drop(dc):
    dc.out = []


def _fill_pickup(dc):
    dc.out += [("snare", dc.t0 + dc.step(st) + 2, 16, 38 + (st - 13) * 12) for st in (13, 14, 15)]


def _fill_build(dc):
    dc.out = [e for e in dc.out if not (e[0] == "snare" and e[1] >= dc.t0 + dc.step(8))]
    dc.out += [("snare", dc.t0 + dc.step(st) + 2, 16, 40 + (st - 8) * 8) for st in range(8, 16)]


def _fill_toms(dc):
    dc.out = [e for e in dc.out if e[1] < dc.t0 + dc.step(8)]
    dc.out += [("tom_hi" if st < 12 else "tom_lo", dc.t0 + dc.step(st) + 1, 18, 60 + (st - 8) * 5)
               for st in range(8, 16)]


for _n, _f in (("stop", _fill_stop), ("drop", _fill_drop), ("pickup", _fill_pickup), ("build", _fill_build),
               ("toms", _fill_toms)):
    R.fill(_n, _f)
