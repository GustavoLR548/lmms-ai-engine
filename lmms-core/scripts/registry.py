"""The plug-in points a genre pack fills: styles and the pattern vocabulary.

lmms-core ships a genre-neutral common vocabulary (common.py: sustained / comping keys, piano, arp, chopped
samples, the basic bass lines, fills). A genre skill adds its own styles, grooves and figures by importing
this module and calling the register functions below - see references/genre-packs.md.

Pattern kinds
  keys   data:  bars = [[(16th step, length in 16ths, velocity, plays-next-chord), ...], ...] (one list per
                bar variant, cycled by bar-in-section), strum = ticks between notes, tie = hold repeated chords,
                track = "keys" or "keys_filtered"
         fn:    fn(song, b, track, rng, inst, pick)          (piano, arp, mpc ...)
  bass   figure: [(16th step, length in ticks, "r"|"5"|"8"|"last", velocity), ...] resolved per chord
         fn:    fn(song, bc)  where bc = BassCtx
  drums  fn(dc) where dc = DrumCtx; return False to play nothing this bar (skips layers and fills too)
  layers fn(dc), switched on by a section flag of the same name (e.g. "perc": true)
  fills  fn(dc) on the section's last bar ("fill": name)
"""

TONE_DEFAULTS = dict(
    keys_lp=5500, keys_hp=120, keys_reverb=0.22,
    drums_lp=10000, drums_reverb=0.08, drums_crush=0,    # crush: 0 off, 1 light (rate), 2 heavy (rate + depth)
    leads_lp=6500, pad_reverb=0.4, bass_lp=1500,
    master_lp=None,                                        # e.g. 12500 for a cassette top end
    leads_echo_beats=0.75, leads_echo_fb=0.25, leads_echo_wet=0.16, leads_reverb=0.28,   # Leads channel echo
    pad_hp=200, pad_lp=3500, pad_level=1.0,                    # Pad channel band + volume (pads that ARE the song: ~1.6)
    keys_echo_beats=0.75, keys_echo_fb=0.35, keys_echo_wet=0,  # optional echo on the Keys channel (0 = none)
)

GENRE = None            # set by the genre pack (e.g. "lofi")
SKILL = "lmms-hiphop"   # the genre skill's name, for project notes (genre(..., skill=...))
DEFAULT_STYLE = None
# chord language (registry.chords): what a bare "I" / "vi" / "C" means, extra suffix meanings, and how long a
# melody note must overlap a held chord note a half-step away before the checker calls it a rub (ticks)
MAJOR_DEFAULT = "maj9"
MINOR_NUMERAL = {}
CHORD_ALIAS = {}
RUB_MIN_OVERLAP = 12
SECTION_DEFAULTS = {"keys": "hold", "bass": "hook", "drums": "none"}   # a pack may change these
STYLES = {}
KEYS = {}               # name -> dict(bars, strum, tie, track)
KEYS_FN = {}            # name -> fn
KEYS2_EXCLUDE = set()   # keys patterns that make no sense on the second comping instrument
BASS_FIGS = {}
BASS_FN = {}
DRUMS = {}
LAYERS = {}             # insertion order = the order layers are played (keeps renders reproducible)
FILLS = {}
# when a kit has no such part, play this one instead (None = drop the hit)
PART_FALLBACK = {"tom_hi": "snare", "tom_lo": "snare", "pedal_hat": "hat", "brush_swirl": None, "clap": None,
                 "sidestick": "snare", "open_hat": "hat", "ride": "hat", "shaker": None, "conga_hi": None,
                 "conga_lo": None, "conga_mute": None, "bongo_hi": None, "bongo_lo": None, "claves": "sidestick",
                 "tambourine": "shaker", "snare_body": None}


def genre(name, default_style, skill=None, **section_defaults):
    global GENRE, DEFAULT_STYLE, SKILL
    GENRE, DEFAULT_STYLE = name, default_style
    SKILL = skill or SKILL
    SECTION_DEFAULTS.update(section_defaults)


def chords(major=None, minor_numeral=None, alias=None, rub_min_overlap=None):
    """Change the chord language: e.g. chords(major="triad", minor_numeral={"": "mtriad"}, alias={"m": "mtriad",
    "7": "dom7"}) makes plain triads the default (qualities: engine.QUALITIES)."""
    global MAJOR_DEFAULT, RUB_MIN_OVERLAP
    if major:
        MAJOR_DEFAULT = major
    MINOR_NUMERAL.update(minor_numeral or {})
    CHORD_ALIAS.update(alias or {})
    if rub_min_overlap:
        RUB_MIN_OVERLAP = rub_min_overlap


def style(sid, **d):
    """title, about, bpm=(lo, hi), swing, humanize, snare_lag, wow, palette, leads, keys, bass, drums,
    tone, feel (and optionally keys2)."""
    d.setdefault("tone", {})
    d.setdefault("feel", {})
    STYLES[sid] = d


def get(sid):
    if sid not in STYLES:
        raise ValueError(f"unknown style {sid!r} (have {', '.join(STYLES) or 'none - no genre pack loaded'})")
    return STYLES[sid]


def keys(name, bars, strum=0, tie=False, track=None, keys2=True):
    """bars: a list of hits (one bar) or a list of bar variants."""
    if bars and isinstance(bars[0], tuple):
        bars = [bars]
    KEYS[name] = dict(bars=bars, strum=strum, tie=tie, track=track)
    if not keys2:
        KEYS2_EXCLUDE.add(name)


def keys_fn(name, fn, keys2=True):
    KEYS_FN[name] = fn
    if not keys2:
        KEYS2_EXCLUDE.add(name)


def bass_fig(name, fig):
    BASS_FIGS[name] = fig


def bass_fn(name, fn):
    BASS_FN[name] = fn


def drums(name, fn):
    DRUMS[name] = fn


def layer(flag, fn):
    LAYERS[flag] = fn


def fill(name, fn):
    FILLS[name] = fn


def keys_names():
    return set(KEYS) | set(KEYS_FN) | {"none"}


def bass_names():
    return set(BASS_FIGS) | set(BASS_FN) | {"none"}


def drum_names():
    return set(DRUMS) | {"none"}


class DrumCtx:
    """What a drum pattern function works with: one bar of one section."""

    def __init__(self, song, b, sec, rng):
        self.song, self.b, self.sec, self.rng = song, b, sec, rng
        self.t0, self.bis, self.bars = b["tick"], b["bis"], int(sec["bars"])
        self.out = []                 # (part, tick, length, velocity)

    def step(self, s):
        return self.song.step(s)

    def J(self, t):
        """humanised timing"""
        return t + self.rng.randint(-self.song.humanize, self.song.humanize)

    def V(self, x, s=5):
        """humanised velocity"""
        return x + self.rng.randint(-s, s)

    def hit(self, part, st, vel, ln=24, lag=0):
        self.out.append((part, self.t0 + self.song.step(st) + lag, ln, vel))

    def hats8(self, acc=64, weak=46):
        for st in range(0, 16, 2):
            self.hit("hat", st, self.V(acc if st % 4 == 0 else weak), 8)


class BassCtx:
    """What a bass pattern function works with: one bar, plus the next bar's root and how to end the bar."""

    def __init__(self, song, b, ant, rng, nxt):
        self.song, self.b, self.ant, self.rng, self.nxt = song, b, ant, rng, nxt
        self.t0, self.sec = b["tick"], b["sec"]

    def v(self, x):
        return x + self.rng.randint(-4, 4)

    def last_note(self, seg):
        """(note, is_anticipation) for the bar's last note: the next root if the keys anticipate, else an
        approach note from the current chord's scale that never rubs the held chord."""
        return (self.nxt, True) if self.ant else (self.song.approach(seg, self.nxt), False)
