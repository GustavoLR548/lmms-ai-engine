"""Song spec (JSON) -> LMMS project, with harmony checks. Genre-neutral: patterns and styles come from
registry.py (the common vocabulary in common.py + whatever genre pack the calling skill loaded).

The spec format is documented in references/spec-format.md. In short: key + bpm + named chord
progressions + named melodies + a list of sections, each choosing a pattern for keys / bass / drums
and optional pad, leads, fills, crashes and risers.
"""
import itertools
import random
import re
from pathlib import Path

import catalog
import lmmsenv
import common  # noqa: F401  (registers the common vocabulary)
import registry as R
from lmmsgen import (TPB, AutomationTrack, InstrumentTrack, Note, Pattern, Project, afp, automatable, eldata, env,
                     fx_bitcrush, fx_delay, fx_dualfilter, fx_eq, fx_reverbsc, lmms_key, log_knob, opl2, sf2, tripleosc,
                     xpf_eldata, xpf_instrument, zyn_from_xiz)

S16 = 12
NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
NAMES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SHARP_KEYS = {7, 2, 9, 4, 11, 6}          # G D A E B F#: spell chords and notes with sharps


def names_for(key_pc):
    return NAMES_SHARP if key_pc in SHARP_KEYS else NAMES
LETTER = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
ROMAN = {"I": 0, "II": 2, "III": 4, "IV": 5, "V": 7, "VI": 9, "VII": 11}

# quality: (voicing tones in semitones above the root, allowed scale relative to the root)
QUALITIES = {
    "maj9": ([4, 7, 11, 14], {0, 2, 4, 7, 9, 11}),
    "maj7": ([0, 4, 7, 11], {0, 2, 4, 7, 9, 11}),
    "6/9": ([4, 7, 9, 14], {0, 2, 4, 7, 9}),
    "m9": ([3, 7, 10, 14], {0, 2, 3, 5, 7, 10}),
    "m11": ([3, 5, 7, 10], {0, 2, 3, 5, 7, 10}),
    "m7": ([0, 3, 7, 10], {0, 2, 3, 5, 7, 10}),
    "m6": ([3, 7, 9, 14], {0, 2, 3, 5, 7, 9}),
    "9": ([4, 7, 10, 14], {0, 2, 4, 7, 9, 10}),
    "13": ([4, 10, 14, 21], {0, 2, 4, 7, 9, 10}),
    "7alt": ([4, 10, 13, 20], {0, 1, 3, 4, 6, 8, 10}),
    "13sus": ([5, 10, 14, 21], {0, 2, 5, 7, 9, 10}),
    "9sus": ([5, 7, 10, 14], {0, 2, 5, 7, 9, 10}),
    "m7b5": ([0, 3, 6, 10], {0, 3, 5, 6, 8, 10}),
    "dim7": ([0, 3, 6, 9], {0, 2, 3, 5, 6, 8, 9, 11}),
    # plain triads (a doubled chord tone makes the 4th voice - any of the three, whichever voice-leads best)
    "triad": ([0, 4, 7, 12], {0, 2, 4, 5, 7, 9, 11}),
    "mtriad": ([0, 3, 7, 12], {0, 2, 3, 5, 7, 8, 9, 10}),
    "dom7": ([0, 4, 7, 10], {0, 2, 4, 5, 7, 9, 10}),
    "sus4": ([0, 5, 7, 12], {0, 2, 5, 7, 9, 10}),
    "sus2": ([0, 2, 7, 12], {0, 2, 5, 7, 9, 11}),
    "dim": ([0, 3, 6, 12], {0, 2, 3, 5, 6, 8, 9, 11}),
    "aug": ([0, 4, 8, 12], {0, 2, 4, 6, 8, 10}),
    "5": ([0, 7, 12, 19], {0, 2, 3, 4, 5, 7, 9, 10}),
}
SUFFIX = {"maj9": "maj9", "maj7": "maj7", "6/9": "6/9", "m9": "m9", "m11": "m11", "m7": "m7", "m6": "m6", "9": "9",
          "13": "13", "7alt": "7alt", "13sus": "13sus", "9sus": "9sus", "m7b5": "m7b5", "dim7": "dim7",
          "triad": "", "mtriad": "m", "dom7": "7", "sus4": "sus4", "sus2": "sus2", "dim": "dim", "aug": "aug", "5": "5"}
ALIAS = {"maj9": "maj9", "M9": "maj9", "maj": "maj9", "maj7": "maj7", "M7": "maj7", "6/9": "6/9", "69": "6/9",
         "add9": "6/9", "m9": "m9", "min9": "m9", "-9": "m9", "m": "m9", "min": "m9", "m11": "m11", "m7": "m7",
         "-7": "m7", "m6": "m6", "7": "9", "9": "9", "dom9": "9", "13": "13", "7alt": "7alt", "alt": "7alt",
         "7b9": "7alt", "7b13": "7alt", "13sus": "13sus", "sus": "13sus", "13sus4": "13sus", "9sus": "9sus",
         "9sus4": "9sus", "7sus4": "9sus", "7sus": "9sus", "m7b5": "m7b5", "ø": "m7b5", "ø7": "m7b5",
         "dim7": "dim7", "o7": "dim7",
         "triad": "triad", "mtriad": "mtriad", "dom7": "dom7", "sus4": "sus4", "sus2": "sus2", "dim": "dim",
         "o": "dim", "aug": "aug", "+": "aug", "5": "5"}
MINOR_NUMERAL = {"": "m9", "9": "m9", "7": "m7", "11": "m11", "6": "m6", "7b5": "m7b5", "ø": "m7b5", "o7": "dim7"}


def _quality(suf, minor_numeral=False):
    """Chord quality for a suffix; a genre pack may change the defaults (registry.chords)."""
    if minor_numeral:
        q = R.MINOR_NUMERAL.get(suf) or MINOR_NUMERAL.get(suf)
        if q:
            return q
    elif suf == "":
        return R.MAJOR_DEFAULT
    return R.CHORD_ALIAS.get(suf) or ALIAS.get(suf)


class Chord:
    def __init__(self, root, quality, key_pc, label, spelling=None):
        self.root, self.quality, self.label = root, quality, label
        tones, scale = QUALITIES[quality]
        self.tones = [(root + t) % 12 for t in tones]
        full = {(root + s) % 12 for s in scale}
        if quality in ("maj9", "maj7", "6/9", "triad") and root != key_pc:
            full.add((root + 6) % 12)                  # Lydian #11 on IV / bVI / bVII / bII
        # melody/bass may use chord tones + the tensions that also belong to the key (so a iii chord
        # doesn't invite a chromatic 9th); borrowed / altered chord tones stay allowed
        key_scale = {(key_pc + x) % 12 for x in (0, 2, 4, 5, 7, 9, 11)}
        self.scale = set(self.tones) | {root} | (full & key_scale)
        names = {"b": NAMES, "#": NAMES_SHARP}.get(spelling) or names_for(key_pc)   # bVI in D is Bb, not A#
        self.name = names[root] + SUFFIX[quality]


def parse_pc(s):
    pc = LETTER[s[0].upper()]
    for ch in s[1:]:
        pc += {"b": -1, "#": 1}.get(ch, 0)
    return pc % 12


def parse_chord(sym, key_pc):
    sym = sym.strip()
    m = re.match(r"^([b#]?)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i)(.*)$", sym)
    if m and not re.match(r"^[A-G]", sym):
        acc, num, suf = m.groups()
        root = (key_pc + ROMAN[num.upper()] + {"b": -1, "#": 1, "": 0}[acc]) % 12
        q = _quality(suf, num.islower())
        if not q:
            raise ValueError(f"unknown chord quality in {sym!r}")
        return Chord(root, q, key_pc, sym, spelling=acc or None)
    m = re.match(r"^([A-G][b#]?)(.*)$", sym)
    if not m:
        raise ValueError(f"cannot parse chord {sym!r}")
    root = parse_pc(m.group(1))
    q = _quality(m.group(2))
    if not q:
        raise ValueError(f"unknown chord quality in {sym!r}")
    acc = m.group(1)[1:]
    return Chord(root, q, key_pc, sym, spelling=acc or None)


def tonic_ref(key_pc):
    """Reference octave for melody degrees: the tonic between F#4 and F5."""
    return 72 + key_pc if key_pc <= 5 else 60 + key_pc


def parse_note(x, key_pc):
    """int = semitones from the tonic (F#4..F5); 'Eb5' = note name; "b3", "5'", "7," = scale degree."""
    if isinstance(x, (int, float)):
        return tonic_ref(key_pc) + int(x)
    s = str(x).strip()
    if s[0] in "ABCDEFG":
        m = re.match(r"^([A-G][b#]?)(-?\d)$", s)
        return parse_pc(m.group(1)) + (int(m.group(2)) + 1) * 12
    m = re.match(r"^([b#]*)(\d+)(['’,]*)$", s)
    if not m:
        raise ValueError(f"bad melody note {x!r}")
    acc, deg, octs = m.groups()
    d = int(deg)
    semis = [0, 2, 4, 5, 7, 9, 11][(d - 1) % 7] + 12 * ((d - 1) // 7)
    semis += sum({"b": -1, "#": 1}[a] for a in acc)
    semis += 12 * octs.count("'") + 12 * octs.count("’") - 12 * octs.count(",")
    return tonic_ref(key_pc) + semis


# ------------------------------------------------------------------ voicing
def voice(ch, prev, lo=52, hi=74, center=62):
    """Pick octave placements for the chord's 4 tones: smooth motion from prev, no mud, few clusters.
    lo/hi/center come from the chord instrument's catalog 'voicing' (piano sits higher, guitar lower)."""
    opts = [[n for n in range(lo, hi + 1) if n % 12 == pc] for pc in ch.tones]
    if len(set(ch.tones)) < len(ch.tones):        # triads: the doubled voice may take any chord tone
        pcs = set(ch.tones)
        seen = set()
        for i, pc in enumerate(ch.tones):
            if pc in seen:
                opts[i] = [n for n in range(lo, hi + 1) if n % 12 in pcs]
            seen.add(pc)
    span = 15 if len(set(ch.tones)) >= 3 else 19          # a power chord (2 pitch classes) needs 1-5-8-12
    best, best_cost = None, 1e9
    for combo in itertools.product(*opts):
        v = sorted(combo)
        if len(set(v)) < len(v) or v[-1] - v[0] > span:
            continue
        gaps = [b - a for a, b in zip(v, v[1:])]
        if gaps[0] == 1 or (v[0] < 55 and gaps[0] < 3):
            continue
        semis = sum(1 for g in gaps if g == 1)
        if semis > 1:
            continue
        mean = sum(v) / len(v)
        cost = 0.6 * abs(mean - center) + 2.0 * semis + 0.5 * max(0, v[-1] - (hi - 2))
        if prev:
            cost += sum(abs(a - b) for a, b in zip(v, prev))
        if cost < best_cost:
            best, best_cost = v, cost
    if best is None:
        raise ValueError(f"no voicing found for {ch.name}")
    return best


from common import S16, bass_root, lh_root  # noqa: E402

# section "move" targets: channel -> mixer channel; param -> (default, (min, max))
MOVE_CHANNELS = {"master": 0, "drums": 1, "keys": 2, "bass": 4, "leads": 5, "pad": 6, "fx": 7, "keys2": 8}
MOVE_PARAMS = {"level": (1.0, (0.0, 1.5)), "cutoff": (20000.0, (40.0, 20000.0))}
MOVE_RES = 0.5                   # resonance of the sweep filter (RC 24 dB low-pass; LMMS's Moog type self-oscillates)
PUMP_SHAPE = [(0, 1.0), (8, 0.45), (22, 0.0), (48, 0.0)]   # duck amount over one beat (ticks)


def _curve(v0, v1, x):
    """Perceptual ramp: exponential between non-zero values, quadratic into / out of silence."""
    if v0 == v1:
        return v0
    if v0 > 0 and v1 > 0:
        return v0 * (v1 / v0) ** x
    return v1 * x * x if v0 == 0 else v0 * (1 - x) ** 2


def _pump(depth, phase):
    """Sidechain-style duck on each beat (phase in ticks, 48 per beat): down at the beat, back by ~half a beat."""
    if not depth:
        return 1.0
    for (p0, g0), (p1, g1) in zip(PUMP_SHAPE, PUMP_SHAPE[1:]):
        if p0 <= phase <= p1:
            return 1 - depth * (g0 + (g1 - g0) * (phase - p0) / (p1 - p0))
    return 1.0


def instrument_xml(spec_i):
    """(instrument XML, eldata or None) for a catalog entry of any kind: sf2, zyn, xpf, opl2, tripleosc."""
    kind = spec_i["kind"]
    if kind == "sf2":
        return sf2(spec_i["file"], spec_i.get("bank", 0), spec_i.get("patch", 0), gain=spec_i.get("gain", 1.0),
                   chorus=spec_i.get("chorus", 0)), None
    if kind == "zyn":
        return zyn_from_xiz(str(lmmsenv.data_dir() / "presets" / catalog.ZYN / spec_i["preset"]),
                            str(lmmsenv.SKILL_DIR / "assets" / "zyn_template.xml")), None
    if kind == "xpf":
        path = str(lmmsenv.data_dir() / "presets" / spec_i["preset"])
        return xpf_instrument(path), xpf_eldata(path)
    if kind == "opl2":
        return opl2(**spec_i["params"]), None
    return tripleosc(spec_i["oscs"]), eldata(fcut=spec_i.get("fcut", 14000), fres=0.6, fwet=1, vol=env(**spec_i["env"]))


class Song:
    def __init__(self, spec, spec_path=None):
        self.spec = spec
        self.dir = Path(spec_path).parent if spec_path else Path.cwd()
        self.genre = R.GENRE
        self.style_id = spec.get("style", R.DEFAULT_STYLE)
        st = R.get(self.style_id)
        self.bpm = float(spec.get("bpm", 75))
        self.key_pc = parse_pc(spec.get("key", "Eb"))
        self.swing = int(spec.get("swing", st["swing"]))
        self.humanize = int(spec.get("humanize", st["humanize"]))
        self.snare_lag = int(spec.get("snare_lag", st["snare_lag"]))
        self.wow = float(spec.get("wow", st["wow"]))
        self.mode = spec.get("mode", "listen")
        self.seed = int(spec.get("seed", 1))
        self.palette = dict(st["palette"], **spec.get("palette", {}))
        self.tone = {**R.TONE_DEFAULTS, **st["tone"], **spec.get("tone", {})}
        self.feel = {k: tuple(v) for k, v in dict(st["feel"], **spec.get("feel", {})).items()}
        self.loop_max_s = spec.get("loop_max_s", st.get("loop_max_s"))   # None = no loop check
        self.problems, self.warnings = [], []
        self.events = []        # dicts: track, role, start, len, midi, vel, ant, sec
        self.chops = []         # mpc hits: dict(start, len, src, vel, rev)  (rendered by chops.py)
        self.lead_range = {}    # (section index, instrument) -> (lowest, highest) sounding MIDI note
        self.tracks_used = {}
        self._timeline()
        self._loop_setup()

    def timpani_notes(self):
        """Tuned timpani (kits whose toms are chromatic timpani, MIDI 41-53): the tonic and its fifth, the lower
        one on tom_lo. Tonic = spec "timpani" (a note name) or the root of the first chord (of the loop, if any)."""
        t = self.spec.get("timpani")
        if t:
            pc = parse_pc(t)
        else:
            pc = self.seg_at(self.loop_start if self.looping else 0)["chord"].root
        r = 41 + (pc - 5) % 12                       # F2 .. E3
        f = r + 7 if r + 7 <= 53 else r - 5
        return {"low": min(r, f), "high": max(r, f)}

    # ---------------------------------------------------------- game loops
    def _loop_setup(self):
        """"loop": true loops the whole song; {"from": "<section name>"} plays the sections before it once (intro)
        and loops the rest. With a loop, the last bar leads into the loop start (bass approach, anticipations)."""
        lp = self.spec.get("loop")
        self.loop_start = self.loop_start_bar = None
        if not lp:
            return
        name = lp.get("from") if isinstance(lp, dict) else None
        sec = next((s for s in self.sections if s["name"] == name), None) if name else self.sections[0]
        if sec is None:
            self.problems.append(f"loop.from {name!r} is not a section name")
            return
        self.loop_start_bar, self.loop_start = sec["start_bar"], sec["start"]

    @property
    def looping(self):
        return self.loop_start is not None

    def loop_seconds(self):
        return self.seconds(self.end - self.loop_start)

    # ---------------------------------------------------------- timeline
    def _timeline(self):
        progs = self.spec["progressions"]
        self.bars, self.segments, self.sections = [], [], []
        bar = 0
        cache = {}
        for si, sec in enumerate(self.spec["sections"]):
            prog = progs[sec["prog"]]
            n = int(sec["bars"])
            if n % len(prog):
                self.warnings.append(f"section {sec['name']!r}: {n} bars is not a multiple of progression "
                                     f"{sec['prog']!r} ({len(prog)} bars) - it will be cut mid-cycle")
            self.sections.append(dict(sec, index=si, start_bar=bar, start=bar * TPB))
            for b in range(n):
                entry = prog[b % len(prog)]
                syms = entry if isinstance(entry, list) else str(entry).split()
                t0 = bar * TPB
                segs = []
                for k, sym in enumerate(syms):
                    if sym not in cache:
                        cache[sym] = parse_chord(sym, self.key_pc)
                    s = t0 + k * TPB // len(syms)
                    e = t0 + (k + 1) * TPB // len(syms)
                    seg = dict(start=s, end=e, chord=cache[sym], sec=si, bar=bar)
                    segs.append(seg)
                    self.segments.append(seg)
                self.bars.append(dict(bar=bar, tick=t0, sec=si, bis=b, segs=segs))
                bar += 1
        self.nbars = bar
        self.end = bar * TPB
        keys_inst = catalog.INSTRUMENTS.get(self.palette.get("keys", "rhodes"), {})
        lo, hi, center = keys_inst.get("voicing", (52, 74, 62))
        prev = None
        for seg in self.segments:
            if prev is not None and seg["chord"].name == self._prev_name:
                seg["voicing"] = prev
            else:
                seg["voicing"] = voice(seg["chord"], prev, lo, hi, center)
            prev, self._prev_name = seg["voicing"], seg["chord"].name

    def seg_at(self, tick):
        if tick >= self.end and getattr(self, "loop_start", None) is not None:
            tick = self.loop_start + (tick - self.end) % (self.end - self.loop_start)
        for seg in self.segments:
            if seg["start"] <= tick < seg["end"]:
                return seg
        return self.segments[-1]

    def seconds(self, tick):
        return tick / 48 * 60 / self.bpm

    def step(self, s):
        return s * S16 + (self.swing if s % 2 else 0)

    # ---------------------------------------------------------- note helpers
    def add(self, track, role, start, length, midi, vel, sec, ant=False, check=None):
        self.events.append(dict(track=track, role=role, start=int(start), len=max(4, int(length)), midi=int(midi),
                                vel=int(max(5, min(127, vel))), sec=sec, ant=ant, check=check))

    def rng_for(self, bar):
        return random.Random(self.seed * 100003 + bar)

    # ---------------------------------------------------------- keys / pad
    def keys_bar(self, b, pattern, track, rng, field="keys"):
        if pattern in (None, "none"):
            return
        inst = catalog.INSTRUMENTS.get(self.palette.get(field) or "", {})
        top3 = field == "keys2"                        # second comping instrument: upper 3 notes only
        pick = (lambda v: v[1:]) if top3 else (lambda v: v)
        if pattern in R.KEYS_FN:
            R.KEYS_FN[pattern](self, b, track, rng, inst, pick)
            return
        pat = R.KEYS[pattern]
        hits = pat["bars"][b["bis"] % len(pat["bars"])]
        strum = max(pat["strum"], inst.get("strum", 0))
        tie = pat["tie"]
        for st, ln, vel, nxt in hits:
            t = b["tick"] + self.step(st)
            seg = self.seg_at(b["tick"] + TPB) if nxt else self.seg_at(t)
            end = t + ln * S16 if nxt else min(t + ln * S16, seg["end"])
            if tie and st == 0 and len(b["segs"]) == 1:
                prev_seg = self.seg_at(b["tick"] - 1) if b["tick"] > 0 else None
                prev_bar = self.bars[b["bar"] - 1] if b["bar"] > 0 else None
                if (prev_seg and prev_bar and len(prev_bar["segs"]) == 1 and prev_seg["chord"].name == seg["chord"].name
                        and prev_bar["sec"] == b["sec"] and self.bar_keys(prev_bar, field) == pattern):
                    continue                           # held over from previous bar (extended below)
                end = self._tie_end(b, pattern, seg, field)
            for i, n in enumerate(pick(seg["voicing"])):
                self.add(track, "keys", t + 1 + i * strum, max(6, end - t - 2 - i * strum), n,
                         vel - i * 2 + rng.randint(-4, 4), b["sec"], ant=bool(nxt))
            if len(b["segs"]) > 1 and st == 0 and tie:     # whole-bar pattern over a split bar
                s2 = b["segs"][1]
                for i, n in enumerate(pick(s2["voicing"])):
                    self.add(track, "keys", s2["start"] + 1 + i * strum, s2["end"] - s2["start"] - 2, n, vel - 6, b["sec"])

    def bar_keys(self, b, field="keys"):
        return self.sections[b["sec"]].get(field)

    def _tie_end(self, b, pattern, seg, field="keys"):
        end = seg["end"]
        k = b["bar"] + 1
        while k < self.nbars:
            nb = self.bars[k]
            if (nb["sec"] == b["sec"] and len(nb["segs"]) == 1 and nb["segs"][0]["chord"].name == seg["chord"].name
                    and self.bar_keys(nb, field) == pattern):
                end = nb["segs"][0]["end"]
                k += 1
            else:
                break
        return end

    def pad_bar(self, b, track):
        for seg in b["segs"]:
            prev = self.seg_at(seg["start"] - 1) if seg["start"] > 0 else None
            if prev and prev["chord"].name == seg["chord"].name and prev["sec"] == seg["sec"] and \
                    self.sections[prev["sec"]].get("pad"):
                continue
            end = seg["end"]
            for nseg in self.segments:
                if nseg["start"] == end and nseg["chord"].name == seg["chord"].name and nseg["sec"] == seg["sec"]:
                    end = nseg["end"]
            for n in seg["voicing"][1:]:
                self.add(track, "pad", seg["start"] + 2, end - seg["start"] - 6, n, 70, b["sec"])

    # ---------------------------------------------------------- bass
    @staticmethod
    def rubs(n, seg):
        """True if n sits a half-step from a note the keys are holding (and isn't a chord tone itself)."""
        vp = {v % 12 for v in seg["voicing"]}
        return n % 12 not in vp and n % 12 != seg["chord"].root and any((n - v) % 12 in (1, 11) for v in vp)

    def approach(self, seg, target):
        """Passing note into the next root: in the current chord's scale, never rubbing the held chord."""
        cands = [n for n in range(target - 3, target + 4)
                 if n != target and n % 12 in seg["chord"].scale and not self.rubs(n, seg)]
        if not cands:
            return bass_root(seg["chord"]) + 7 if (bass_root(seg["chord"]) + 7) % 12 in seg["chord"].scale \
                else bass_root(seg["chord"]) + 12
        return min(cands, key=lambda n: (abs(n - target), n > target))

    def bass_bar(self, b, style, ant, rng):
        if style in (None, "none"):
            return
        nxt_seg = self.seg_at(b["tick"] + TPB) if (b["bar"] + 1 < self.nbars or self.looping) else b["segs"][-1]
        bc = R.BassCtx(self, b, ant, rng, bass_root(nxt_seg["chord"]))
        if style in R.BASS_FN:
            R.BASS_FN[style](self, bc)
        else:
            common.bass_figure(self, bc, R.BASS_FIGS[style])

    # ---------------------------------------------------------- drums
    def drums_bar(self, b, style, sec, rng):
        if style in (None, "none"):
            return []
        dc = R.DrumCtx(self, b, sec, rng)
        if R.DRUMS[style](dc) is False:
            return []
        for flag, fn in R.LAYERS.items():              # hand-percussion etc. layers switched on per section
            if sec.get(flag):
                fn(dc)
        fill = sec.get("fill")
        if dc.bis == dc.bars - 1 and fill:
            if fill in R.FILLS:
                R.FILLS[fill](dc)
            else:
                self.warnings.append(f"unknown fill {fill!r} in {sec['name']}")
        return dc.out

    # ---------------------------------------------------------- leads
    def leads(self, sec, lead):
        mel = self.spec.get("melodies", {}).get(lead["melody"])
        if mel is None:
            self.problems.append(f"section {sec['name']!r}: melody {lead['melody']!r} not defined")
            return
        inst = lead["inst"]
        vel = int(lead.get("vel", 80))
        at = int(lead.get("at", 0))
        shift = int(lead.get("transpose", lead.get("octave", 0)))    # semitones (a key-change section: 1, 2 ...)
        rng = self.rng_for(sec["start_bar"] * 7 + len(inst))
        for item in mel:
            bar, st, ln, note = item[:4]
            if bar + at >= int(sec["bars"]):
                self.warnings.append(f"melody {lead['melody']!r} runs past section {sec['name']!r}")
                continue
            t = sec["start"] + (bar + at) * TPB + self.step(int(st))
            n = parse_note(note, self.key_pc) + shift
            if lead.get("harmony") == "below":
                seg = self.seg_at(t)
                tones = set(seg["chord"].tones) | {seg["chord"].root}
                n = next((n - d for d in range(3, 10) if (n - d) % 12 in tones), n - 5)
            self.add(f"lead:{inst}", "lead", t + rng.randint(0, 2), int(ln) * S16 - 3, n,
                     vel + rng.randint(-6, 6), sec["index"])
            lo, hi = self.lead_range.get((sec["index"], inst), (n, n))
            self.lead_range[(sec["index"], inst)] = (min(lo, n), max(hi, n))

    # ---------------------------------------------------------- generate everything
    def validate(self):
        for sec in self.sections:
            for target, val in (sec.get("move") or {}).items():
                ch, _, param = target.partition(".")
                if ch not in MOVE_CHANNELS or param not in MOVE_PARAMS:
                    self.problems.append(f"{sec['name']}: move target {target!r} unknown (channels "
                                         f"{', '.join(MOVE_CHANNELS)}; params {', '.join(MOVE_PARAMS)})")
                    continue
                lo, hi = MOVE_PARAMS[param][1]
                vals = val if isinstance(val, list) else [val]
                if not vals or len(vals) > 2 or any(not isinstance(v, (int, float)) or not lo <= v <= hi for v in vals):
                    self.problems.append(f"{sec['name']}: move {target} = {val!r} - give a number or [from, to] "
                                         f"between {lo} and {hi}")
            for ch, d in (sec.get("pump") or {}).items():
                if ch not in MOVE_CHANNELS or ch in ("master", "drums"):
                    self.problems.append(f"{sec['name']}: pump channel {ch!r} unknown (use keys, keys2, bass, "
                                         f"leads, pad, fx)")
                elif not isinstance(d, (int, float)) or not 0 <= d <= 0.9:
                    self.problems.append(f"{sec['name']}: pump {ch} = {d!r} - a depth between 0 and 0.9")
        pal = self.palette
        for role in ("keys", "keys2", "bass", "pad"):
            if pal.get(role) and pal[role] not in catalog.INSTRUMENTS:
                self.problems.append(f"palette.{role} {pal[role]!r} is not in catalog.INSTRUMENTS")
        if pal.get("kit", "dusty") not in catalog.KITS:
            self.problems.append(f"palette.kit {pal.get('kit')!r} is not in catalog.KITS")
        tex = pal.get("textures", ["vinyl"])
        for t in (tex if isinstance(tex, list) else list(tex)):
            if t not in catalog.TEXTURES:
                self.problems.append(f"texture {t!r} unknown (have {sorted(catalog.TEXTURES)})")
        for s in self.sections:
            D = R.SECTION_DEFAULTS
            k, bs, d = s.get("keys", D["keys"]), s.get("bass", D["bass"]), s.get("drums", D["drums"])
            if k not in R.keys_names():
                self.problems.append(f"{s['name']}: keys pattern {k!r} unknown (have {sorted(R.keys_names())})")
            k2 = s.get("keys2")
            if k2 and k2 not in R.keys_names() - R.KEYS2_EXCLUDE:
                self.problems.append(f"{s['name']}: keys2 pattern {k2!r} unknown")
            if k2 and not pal.get("keys2"):
                self.problems.append(f"{s['name']}: keys2 pattern set but palette has no 'keys2' instrument")
            if bs not in R.bass_names():
                self.problems.append(f"{s['name']}: bass style {bs!r} unknown (have {sorted(R.bass_names())})")
            if d not in R.drum_names():
                self.problems.append(f"{s['name']}: drum style {d!r} unknown (have {sorted(R.drum_names())})")
            if s.get("fill") and s["fill"] not in R.FILLS:
                self.problems.append(f"{s['name']}: fill {s['fill']!r} unknown (have {sorted(R.FILLS)})")
            for lead in s.get("leads") or []:
                if lead.get("inst") not in catalog.INSTRUMENTS:
                    self.problems.append(f"{s['name']}: lead instrument {lead.get('inst')!r} not in catalog")
                elif lead.get("melody") not in self.spec.get("melodies", {}):
                    self.problems.append(f"{s['name']}: melody {lead.get('melody')!r} not defined in 'melodies'")
        if self.looping and any(s.get("keys") == "mpc" for s in self.sections):
            self.problems.append("keys 'mpc' (chopped sample) can't be used in a looping song yet")
        return not self.problems

    def generate(self):
        if not self.validate():
            return
        kit = catalog.KITS[self.palette.get("kit", "dusty")]

        def kit_part(part):
            while part is not None and part not in kit:
                part = R.PART_FALLBACK.get(part)
            return part

        for b in self.bars:
            sec = self.sections[b["sec"]]
            rng = self.rng_for(b["bar"])
            D = R.SECTION_DEFAULTS
            kp = sec.get("keys", D["keys"])
            pat = R.KEYS.get(kp)
            ant = bool(pat) and len(pat["bars"]) == 1 and any(h[3] for h in pat["bars"][0])   # keys anticipate
            self.keys_bar(b, kp, (pat or {}).get("track") or "keys", rng)
            if sec.get("keys2"):
                self.keys_bar(b, sec["keys2"], "keys2", rng, field="keys2")
            self.bass_bar(b, sec.get("bass", D["bass"]), ant, rng)
            if sec.get("pad"):
                self.pad_bar(b, "pad")
            for part, t, ln, vel in self.drums_bar(b, sec.get("drums", D["drums"]), sec, rng):
                part = kit_part(part)
                if part is None:
                    continue
                self.add(f"drum:{part}", "drum", t, ln, 57 + 12, vel, b["sec"])
                if part == "snare" and "snare_body" in kit:
                    self.add("drum:snare_body", "drum", t, ln, 57 + 12, vel, b["sec"])
        rev_ticks = round(kit["reverse_crash"][2]["seconds"] / (60 / self.bpm / 48))
        for sec in self.sections:
            if sec.get("crash"):
                self.add("drum:crash", "drum", sec["start"], 90, 69, 90, sec["index"])
            if sec.get("riser") and sec["start"] >= rev_ticks:
                self.add("drum:reverse_crash", "drum", sec["start"] - rev_ticks, rev_ticks, 69, 80, sec["index"])
            for lead in sec.get("leads", []) or []:
                self.leads(sec, lead)
        tex = self.palette.get("textures", ["vinyl"])
        tex = {t: 0 for t in tex} if isinstance(tex, list) else tex
        for name in tex:
            self.add(f"tex:{name}", "texture", 0, self.end + 2 * TPB, 69, 100, 0)
        self.textures = tex
        self.apply_feel()
        self.check()

    FEEL_GROUP = {"keys": "keys", "keys_filtered": "keys", "keys2": "keys", "chops_ref": "keys", "bass": "bass",
                  "pad": "pad"}

    def apply_feel(self):
        """Per-instrument timing: 'feel': {"kick": [lag, jitter], "bass": [6, 3], ...} in ticks (12 per 16th).
        Positive lag = behind the beat. This is what makes Dilla-style drums 'drunk'."""
        if not self.feel:
            return
        rng = random.Random(self.seed * 7919)
        for e in self.events:
            tr = e["track"]
            part = tr.split(":", 1)[1] if tr.startswith("drum:") else ("lead" if tr.startswith("lead:") else
                                                                       self.FEEL_GROUP.get(tr))
            if part in self.feel:
                lag, jit = self.feel[part]
                e["start"] = max(0, e["start"] + int(lag) + rng.randint(-int(jit), int(jit)))
        if "keys" in self.feel:
            for c in self.chops:
                c["start"] = max(0, c["start"] + int(self.feel["keys"][0]))

    # ---------------------------------------------------------- checks
    def check(self):
        harm = [e for e in self.events if e["role"] in ("keys", "pad")]
        melodic = [e for e in self.events if e["role"] in ("bass", "lead")]
        for e in melodic:
            if e["ant"]:   # anticipation: belongs to the next bar's chord
                nb = e["start"] // TPB + 1
                nb = nb if nb < self.nbars else (self.loop_start_bar if self.looping else self.nbars - 1)
                seg = self.seg_at(self.bars[nb]["tick"])
            else:
                seg = self.seg_at(e["start"])
            ch = seg["chord"]
            pc = e["midi"] % 12
            where = f"bar {e['start'] // TPB + 1} ({self.fmt(self.seconds(e['start']))}, {ch.name})"
            if pc not in ch.scale and pc not in {x % 12 for x in seg["voicing"]}:
                self.problems.append(f"{e['track']} note {NAMES[pc]} is outside {ch.name} at {where}")
                continue
            if pc in {x % 12 for x in seg["voicing"]} or pc == ch.root:
                continue
            for h in harm:
                overlap = min(e["start"] + e["len"], h["start"] + h["len"]) - max(e["start"], h["start"])
                if overlap < R.RUB_MIN_OVERLAP:
                    continue
                if (e["midi"] - h["midi"]) % 12 in (1, 11):
                    self.problems.append(f"{e['track']} {NAMES[pc]} rubs a half-step against the chord's "
                                         f"{NAMES[h['midi'] % 12]} at {where}")
                    break
        leads = [e for e in melodic if e["role"] == "lead"]
        for a, bb in itertools.combinations(leads, 2):
            if a["track"] == bb["track"]:
                continue
            if min(a["start"] + a["len"], bb["start"] + bb["len"]) - max(a["start"], bb["start"]) >= 12 and \
                    (a["midi"] - bb["midi"]) % 12 in (1, 11):
                self.problems.append(f"{a['track']} and {bb['track']} clash a half-step apart at bar {a['start'] // TPB + 1}")
        for e in leads:
            if not 57 <= e["midi"] <= 91:
                self.warnings.append(f"{e['track']} note MIDI {e['midi']} is outside the comfortable lead range")
        self.loop_check()

    def loop_stretches(self):
        """[(first bar, end bar, cycle)] where every bar repeats the bar 4 (or 8) before it: the same parts playing
        the same notes at the same places (within a few ticks of humanize; velocity doesn't count, nor do level /
        filter moves). A stretch starts with the first pass of the loop; a single differing bar (a fill, a
        turnaround) inside it doesn't break it."""
        bars = [{} for _ in range(self.nbars)]
        for e in self.events:
            if e["role"] == "texture":
                continue
            t = e["start"] + 8                     # a note pushed just before a bar line belongs to the next bar
            if t // TPB < self.nbars:
                bars[t // TPB].setdefault(e["track"], []).append((e["midi"], t % TPB, min(e["len"], TPB)))
        for d in bars:
            for v in d.values():
                v.sort()

        def same(a, b):
            if a.keys() != b.keys():
                return False
            for k, x in a.items():
                y = b[k]
                if len(x) != len(y) or any(m1 != m2 or abs(p1 - p2) > 5 or abs(l1 - l2) > max(6, l1 // 4)
                                           for (m1, p1, l1), (m2, p2, l2) in zip(x, y)):
                    return False
            return True

        cyc = [0] * self.nbars
        for i in range(4, self.nbars):
            cyc[i] = 4 if same(bars[i], bars[i - 4]) else (8 if i >= 8 and same(bars[i], bars[i - 8]) else 0)
        out, i = [], 0
        while i < self.nbars:
            if not cyc[i]:
                i += 1
                continue
            j = i
            while j < self.nbars and (cyc[j] or (j + 1 < self.nbars and cyc[j + 1])):   # a lone fill / turnaround
                j += 1                                                                 # bar doesn't end the loop
            a = i - cyc[i]
            if out and a <= out[-1][1]:
                a = out.pop()[0]
            out.append((a, j, cyc[i]))
            i = j
        return out

    def loop_check(self):
        """Warn where one short loop plays on longer than the style allows (style / spec "loop_max_s")."""
        if not self.loop_max_s:
            return
        for a, b, cyc in self.loop_stretches():
            secs = self.seconds((b - a) * TPB)
            if secs <= self.loop_max_s:
                continue
            names = []
            for s in self.sections:
                if s["start_bar"] < b and s["start_bar"] + int(s["bars"]) > a and s["name"] not in names:
                    names.append(s["name"])
            self.warnings.append(
                f"bars {a + 1}-{b} ({self.fmt(self.seconds(a * TPB))}-{self.fmt(self.seconds(b * TPB))}, "
                f"{' / '.join(names)}): the same {cyc}-bar loop for {secs:.0f} s (this style: at most "
                f"{self.loop_max_s:g} s) - change something a listener hears every 8 bars: a part in or out, another "
                f"keys / bass / drum pattern, a chord, a melody entrance, a fill (level and filter moves alone "
                f"don't count)")

    @staticmethod
    def fmt(s):
        return f"{int(s // 60)}:{int(s % 60):02d}"

    # ---------------------------------------------------------- project
    def build_project(self, chops_file=None):
        """chops_file: the rendered chopped-sample audio (chops.py) when the song uses keys "mpc"."""
        data = lmmsenv.data_dir()
        if data is None:
            raise SystemExit("LMMS data dir not found (set LMMS_DATA)")
        wd = lmmsenv.working_dir()
        tpl = str(lmmsenv.SKILL_DIR / "assets" / "zyn_template.xml")
        pal = self.palette
        overrides = self.spec.get("instruments", {})
        gains = self.spec.get("mix", {}).get("gains", {})
        bed = self.mode == "bed"
        tone = self.tone
        P = Project(bpm=self.bpm, master_vol=50)
        tracks = {}
        self.label_roles = {}

        def vol(label, base):
            v = base * 10 ** (gains.get(label, 0) / 20)
            if v > 200:
                self.warnings.append(f"{label}: wanted volume {v:.0f} > 200, clamped - raise its channel instead: "
                                     f"\"move\": {{\"<channel>.level\": {min(1.5, v / 200):.2f}}} in the first section "
                                     f"(it holds until another section moves it)")
            return max(1, min(200, round(v)))

        def inst_track(key, iid, fxch, label_suffix="", role=None, slot=None, scale=1.0):
            spec_i = dict(catalog.INSTRUMENTS[iid], **overrides.get(iid, {}))
            label = spec_i["label"] + label_suffix
            if not spec_i.get("measured"):
                self.warnings.append(f"instrument {iid!r} is not measured yet (level/octave guessed) - "
                                     f"run `lofi.py measure`")
            xml, eld = instrument_xml(spec_i)
            base = spec_i["vol"] * scale
            if slot and spec_i["role"] == "pad" and slot != "pad" and "vol" not in overrides.get(iid, {}):
                # a pad-measured sound (orch_strings, choir) promoted to chords / melody sits at that slot's level
                base *= 10 ** ((catalog.ROLE_TARGET[slot] - catalog.ROLE_TARGET["pad"]) / 20)
            cents = spec_i.get("cents") if spec_i.get("retune") else None
            pitch = -cents if cents and abs(cents) >= 5 else 0      # measured tuning offset, undone (cents)
            tracks[key] = (InstrumentTrack(label, xml, vol=vol(label, base), fxch=fxch, eld=eld, pitch=pitch), spec_i)
            self.label_roles[label] = role or ("keys_filtered" if key == "keys_filtered" else spec_i["role"])

        used = {e["track"] for e in self.events}
        if "keys" in used:
            inst_track("keys", pal.get("keys", "rhodes"), 2, slot="keys")
        if "keys_filtered" in used:
            inst_track("keys_filtered", pal.get("keys", "rhodes"), 3, " (filtered)")
        if "keys2" in used:
            inst_track("keys2", pal["keys2"], 8, "" if pal["keys2"] != pal.get("keys") else " 2", role="keys2")
        if self.chops and chops_file:
            tr = InstrumentTrack("Chops", afp(str(chops_file)), vol=vol("Chops", catalog.CHOPS_VOL), fxch=2)
            tr.patterns.append(Pattern("chopped sample", 0, -(-self.end // TPB) * TPB + TPB,
                                       [Note(0, self.end + TPB // 2, lmms_key(69), 100)]))
            tracks["chops"] = (tr, dict(octave=0))
            self.label_roles["Chops"] = "chops"
        if "bass" in used:
            inst_track("bass", pal.get("bass", "warm_sine"), 4)
        for t in sorted(u for u in used if u.startswith("lead:")):
            inst_track(t, t.split(":", 1)[1], 5, slot="lead")
        if "pad" in used:
            inst_track("pad", pal.get("pad", "soft_saw_pad"), 6, "" if pal.get("pad") != pal.get("keys") else " pad",
                       role="pad", scale=tone["pad_level"])
        kit_id = pal.get("kit", "dusty")
        kit = catalog.KITS[kit_id]
        if kit_id not in catalog.MEASURED_KITS:
            self.warnings.append(f"kit {kit_id!r} is not measured yet (levels guessed) - run `lofi.py measure`")
        for part in kit:
            key = f"drum:{part}"
            if key not in used:
                continue
            src, base, extra = kit[part]
            label = catalog.KIT_LABELS[part]
            if bed and part in ("hat", "shaker", "ride"):
                base *= 0.7
            eld = eldata(fcut=extra["fcut"], fres=0.5, fwet=1) if "fcut" in extra else None
            if isinstance(src, dict):
                xml, fixed = sf2(src["sf2"], src.get("bank", 0), src.get("patch", 0), gain=extra.get("gain", 1.0)), src["note"]
                if "timpani" in extra:
                    fixed = self.timpani_notes()[extra["timpani"]]
            else:
                xml, fixed = afp(src, amp=round(100 * extra.get("gain", 1.0)), reversed_=extra.get("reversed", 0)), None
            tr = InstrumentTrack(label, xml, vol=vol(label, base), pan=extra.get("pan", 0), fxch=1, eld=eld)
            tracks[key] = (tr, dict(octave=0, fixed=fixed))
            self.label_roles[label] = part
        import textures as texmod
        for name, db in self.textures.items():
            t = catalog.TEXTURES[name]
            texmod.ensure(name, wd / "samples", t["file"])
            tr = InstrumentTrack(t["label"], afp(t["file"], looped=1), vol=vol(t["label"], t["vol"] * 10 ** (db / 20)), fxch=7)
            tracks[f"tex:{name}"] = (tr, dict(octave=0))
            self.label_roles[t["label"]] = name

        # notes -> one pattern per section per track
        order = ["keys", "keys_filtered", "keys2", "chops", "bass"] + sorted(k for k in tracks if k.startswith("lead:")) + \
                ["pad"] + [f"drum:{p}" for p in kit] + [k for k in tracks if k.startswith("tex:")]
        for key in order:
            if key not in tracks:
                continue
            tr, spec_i = tracks[key]
            shift = spec_i.get("octave") or 0
            fixed = spec_i.get("fixed")
            groups = {}
            for e in (e for e in self.events if e["track"] == key):
                if key.startswith("tex:"):
                    gid = ("texture", 0)
                elif key == "drum:reverse_crash":
                    gid = ("riser", e["start"])
                else:
                    gid = (self.sections[e["sec"]]["name"], self.sections[e["sec"]]["start"])
                groups.setdefault(gid, []).append(e)
            for (name, pos), es in groups.items():
                end = max(e["start"] + e["len"] for e in es)
                length = max(TPB, -(-(end - pos) // TPB) * TPB)
                notes = []
                for e in es:
                    midi = fixed if fixed is not None else \
                        e["midi"] + (shift if e["role"] in ("keys", "lead", "pad", "bass") else 0)
                    notes.append(Note(max(0, e["start"] - pos), e["len"], lmms_key(midi), e["vel"]))
                tr.patterns.append(Pattern(name, pos, length, notes))
            P.add(tr)

        dip = [(2500, -3.0, 0.5)] if bed else []
        crush = {0: [], 1: [fx_bitcrush(rate=24000, levels=256, wet=1.0)],
                 2: [fx_bitcrush(rate=16000, levels=96, wet=0.7)]}[int(tone.get("drums_crush", 0))]
        P.channel(1, "Drums", 1.0, crush + [fx_eq(hp=30, lp=tone["drums_lp"], peaks=[(3000, -2.0, 0.6)]),
                                            fx_reverbsc(size=0.5, color=6000, wet=tone["drums_reverb"])])
        keys_echo = [fx_delay(time_s=round(60 / self.bpm * tone["keys_echo_beats"], 4), feedback=tone["keys_echo_fb"],
                              wet=tone["keys_echo_wet"])] if tone.get("keys_echo_wet") else []
        P.channel(2, "Keys", 1.0, [fx_eq(hp=tone["keys_hp"], lp=tone["keys_lp"], peaks=[(300, -2.0, 0.5)] + dip)] +
                  keys_echo + [fx_reverbsc(size=0.8, color=6000, wet=tone["keys_reverb"])])
        P.channel(3, "Keys filtered", 2.0, [fx_eq(hp=150, lp=900, slope=24), fx_reverbsc(size=0.85, color=4000, wet=0.35)])
        P.channel(4, "Bass", 1.0, [fx_eq(hp=28, lp=tone["bass_lp"])])
        P.channel(5, "Leads", 1.0 if bed else 1.75,
                  [fx_eq(hp=250, lp=tone["leads_lp"], peaks=dip),
                   fx_delay(time_s=round(60 / self.bpm * tone["leads_echo_beats"], 4), feedback=tone["leads_echo_fb"],
                            wet=tone["leads_echo_wet"]),
                   fx_reverbsc(size=0.85, color=5500, wet=tone["leads_reverb"])])
        P.channel(6, "Pad", 1.0, [fx_eq(hp=tone["pad_hp"], lp=tone["pad_lp"], peaks=dip),
                                  fx_reverbsc(size=0.9, color=4000, wet=tone["pad_reverb"])])
        P.channel(7, "FX / Texture", 1.0, [fx_eq(hp=40, lp=9000)])
        if "keys2" in tracks:
            P.channel(8, "Keys 2", 1.0, [fx_eq(hp=200, lp=tone["keys_lp"], peaks=dip),
                                         fx_reverbsc(size=0.7, color=6000, wet=0.15)])
        master_eq = fx_eq(hp=25, lp=tone["master_lp"]) if tone.get("master_lp") else fx_eq(hp=25)
        wow = self.wow
        lfo = 0.4
        if self.looping:
            lfo = max(1, round(0.4 * self.loop_seconds())) / self.loop_seconds()
        P.master_effects = [master_eq] + ([fx_delay(time_s=0.01, feedback=0.0, lfo_hz=round(lfo, 6) if self.looping else 0.4,
                                                    lfo_amt=wow, wet=1.0)] if wow else [])
        self._apply_automation(P)
        P.loop = (self.loop_start, self.end) if self.looping else (0, self.end)
        P.notes = (f"{self.spec.get('title', 'lofi')} - {self.bpm:g} BPM, key {NAMES[self.key_pc]}, style {self.style_id}. "
                   f"Built by the {R.SKILL} skill from song.json. Sections: " +
                   " | ".join(f"{s['name']} {self.fmt(self.seconds(s['start']))}" for s in self.sections))
        return P

    # ---------------------------------------------------------- automation: section "move" / "pump"
    def automation_curves(self):
        """{(channel, param): [(tick, value)]}. A section's "move" sets a target for its whole length: a number
        holds it, [a, b] ramps from a to b (cutoff and non-zero levels ramp exponentially, fades to / from 0
        quadratically); sections without a move keep the last value. "pump" ducks a channel on every beat
        (depth 0-0.9: sidechain-style) and multiplies its level."""
        targets = {}
        for sec in self.sections:
            for t in (sec.get("move") or {}):
                ch, _, param = t.partition(".")
                targets.setdefault((ch, param), None)
            for ch, d in (sec.get("pump") or {}).items():
                if d:
                    targets.setdefault((ch, "level"), None)
        curves = {}
        for (ch, param) in targets:
            cur = MOVE_PARAMS[param][0]
            pts = []
            for sec in self.sections:
                s0 = sec["start"]
                s1 = s0 + int(sec["bars"]) * TPB
                val = (sec.get("move") or {}).get(f"{ch}.{param}")
                vals = val if isinstance(val, list) else ([val] if val is not None else [cur])
                v0, v1 = float(vals[0]), float(vals[-1])
                depth = float((sec.get("pump") or {}).get(ch, 0)) if param == "level" else 0.0
                ticks = {s0, s1 - 1}
                if v0 != v1:
                    ticks |= set(range(s0, s1, S16 * 4))
                if depth:
                    for b in range(s0, s1, S16 * 4):
                        ticks |= {b, b + 8, b + 22, b + 47}
                for t in sorted(x for x in ticks if s0 <= x < s1):
                    x = (t - s0) / max(1, s1 - 1 - s0)
                    pts.append((t, _curve(v0, v1, x) * _pump(depth, (t - s0) % (S16 * 4))))
                cur = v1
            curves[(ch, param)] = pts
        return curves

    def _apply_automation(self, P):
        curves = self.automation_curves()
        oid = 910000
        for (ch, param), pts in sorted(curves.items()):
            num = MOVE_CHANNELS[ch]
            if num != 0 and num not in P.channels:
                continue                                   # the song never uses that channel
            oid += 1
            if param == "level":
                base = 1.0 if num == 0 else P.channels[num][1]
                P.volume_ids[num] = oid
                P.automation.append(AutomationTrack(f"{ch} level", oid, [(t, min(2.0, base * v)) for t, v in pts]))
            else:                                          # cutoff: a resonant low-pass first in the channel
                filt = automatable(fx_dualfilter(cut1=round(pts[0][1]), res1=MOVE_RES, filter1=11), "cut1", oid, "log")
                if num == 0:
                    P.master_effects.insert(0, filt)
                else:
                    name, vol, fx = P.channels[num]
                    P.channels[num] = (name, vol, [filt] + fx)
                P.automation.append(AutomationTrack(f"{ch} cutoff", oid,
                                                    [(t, log_knob(v, 1.0, 20000.0)) for t, v in pts]))

    # ---------------------------------------------------------- summary
    def summary(self):
        lines = [f"{self.spec.get('title', 'untitled')} [{self.style_id}]: {self.bpm:g} BPM, key {names_for(self.key_pc)[self.key_pc]}, "
                 f"{self.nbars} bars = {self.fmt(self.seconds(self.end))}", ""]
        for s in self.sections:
            segs = [g for g in self.segments if g["sec"] == s["index"]]
            chords, last = [], None
            for g in segs:
                if g["chord"].name != last:
                    chords.append(g["chord"].name)
                last = g["chord"].name
            def rng_txt(inst):
                r = self.lead_range.get((s["index"], inst))
                nm = lambda m: names_for(self.key_pc)[m % 12] + str(m // 12 - 1)
                return f" {nm(r[0])}-{nm(r[1])}" if r else ""
            leads = ", ".join(f"{l['inst']}:{l['melody']}{rng_txt(l['inst'])}" for l in (s.get("leads") or [])) or "-"
            lines.append(f"{self.fmt(self.seconds(s['start'])):>5}  {s['name']:<12} {s['bars']:>2} bars  "
                         f"keys={s.get('keys', R.SECTION_DEFAULTS['keys'])}{'+' + s['keys2'] if s.get('keys2') else ''} bass={s.get('bass', R.SECTION_DEFAULTS['bass'])} drums={s.get('drums', R.SECTION_DEFAULTS['drums'])} "
                         f"pad={'y' if s.get('pad') else '-'} leads={leads}")
            lines.append(f"{'':>7}{' '.join(chords[:16])}{' ...' if len(chords) > 16 else ''}")
            moves = [f"{k} {'->'.join(str(x) for x in (v if isinstance(v, list) else [v]))}"
                     for k, v in (s.get("move") or {}).items()]
            moves += [f"pump {k} {v}" for k, v in (s.get("pump") or {}).items() if v]
            if moves:
                lines.append(f"{'':>7}moves: {', '.join(moves)}")
        return "\n".join(lines)
