"""Low-level writer for LMMS 1.2.x .mmp project files (plain XML).

Timing: 192 ticks per 4/4 bar, 48 per beat, 12 per 16th.
Pitch:  LMMS key = MIDI note - 12   (MIDI 60 / middle C = LMMS 48, A4 = LMMS 57).
Every XML node/attribute name used here was verified against LMMS 1.2.2 by rendering
(see references/lmms-format.md) - LMMS silently ignores names it does not know.
"""
import gzip
import re
from xml.sax.saxutils import quoteattr

TPB = 192


def attrs(d):
    return " ".join(f"{k}={quoteattr(str(v))}" for k, v in d.items())


def lmms_key(midi_note):
    return midi_note - 12


# ---------------------------------------------------------------- envelopes / instrument filter
def env(att=0, hold=0.5, dec=0.5, sus=0.5, rel=0.1, amt=0):
    """amt=1 enables the envelope (volume env: amt=0 means 'plain gate')."""
    return dict(pdel=0, att=att, hold=hold, dec=dec, sustain=sus, rel=rel, amt=amt, lpdel=0, latt=0,
                lspd=0.1, lamt=0, lshp=0, x100=0, ctlenvamt=0, syncmode=0,
                lspd_numerator=4, lspd_denominator=4, userwavefile="")


def eldata(fcut=14000, fres=0.5, ftype=0, fwet=0, vol=None):
    """Per-instrument filter (ftype 0 = low-pass; fwet=1 turns it on) + volume envelope."""
    vol = vol or env(hold=0, dec=0.5, sus=1, rel=0.1, amt=0)
    return (f'<eldata {attrs(dict(fwet=fwet, ftype=ftype, fres=fres, fcut=fcut))}>'
            f'<elvol {attrs(vol)}/><elcut {attrs(env())}/><elres {attrs(env())}/></eldata>')


# ---------------------------------------------------------------- instruments
def afp(src, amp=100, looped=0, reversed_=0):
    """AudioFileProcessor. src relative to <workingdir>/samples or LMMS factory samples, or absolute.
    looped=1 loops the whole sample while the note is held (tempo-independent textures)."""
    a = dict(src=src, amp=amp, looped=looped, sframe=0, eframe=1, lframe=0, reversed=reversed_, stutter=0, interp=1)
    return f'<instrument name="audiofileprocessor"><audiofileprocessor {attrs(a)}/></instrument>'


def sf2(src, bank=0, patch=0, gain=1.0, reverb=0, chorus=0):
    """SoundFont player (FluidSynth 1.1.6 in LMMS 1.2.2 - SF2 only, no SF3). src: absolute path or
    relative to <workingdir>/samples. Drum kits are bank 128 in GM banks; MIDI note = drum."""
    a = dict(src=src, bank=bank, patch=patch, gain=gain, reverbOn=reverb, reverbRoomSize=0.2, reverbDamping=0,
             reverbWidth=0.5, reverbLevel=0.9, chorusOn=chorus, chorusNum=3, chorusLevel=2, chorusSpeed=0.3,
             chorusDepth=8)
    return f'<instrument name="sf2player"><sf2player {attrs(a)}/></instrument>'


OPL2_DEFAULTS = dict(fm=1, feedback=0, trem_depth=0, vib_depth=0,
                     op1_mul=1, op1_lvl=40, op1_waveform=0, op1_a=0, op1_d=0, op1_s=15, op1_r=8, op1_perc=0,
                     op1_ksr=0, op1_scale=0, op1_trem=0, op1_vib=0,
                     op2_mul=1, op2_lvl=54, op2_waveform=0, op2_a=0, op2_d=0, op2_s=15, op2_r=8, op2_perc=0,
                     op2_ksr=0, op2_scale=0, op2_trem=0, op2_vib=0)


def opl2(**params):
    """OpulenZ (Yamaha OPL2 / AdLib FM: the DOS and, roughly, Sega Genesis sound). op1 = modulator, op2 =
    carrier. In LMMS's units a/d/r are TIMES (0 = fastest, 15 = slowest), s is the sustain LEVEL (15 = full),
    lvl is output level (63 = loudest; the modulator's lvl sets brightness), mul 0 = x0.5, perc=1 = no sustain."""
    a = dict(OPL2_DEFAULTS, **params)
    return f'<instrument name="OPL2"><OPL2 {attrs(a)}/></instrument>'


def xpf_instrument(path):
    """The <instrument> element of an LMMS instrument preset (.xpf, plain or zlib-compressed) - any plugin."""
    raw = open(path, "rb").read()
    try:
        text = raw.decode("utf-8")
        if "<instrument" not in text:
            raise ValueError
    except (UnicodeDecodeError, ValueError):
        import zlib
        text = zlib.decompress(raw[4:]).decode("utf-8")
    m = re.search(r"<instrument name=.*?</instrument>", text, re.S)
    if m:
        return m.group(0)
    # old (LMMS 0.4 / 1.0) presets: the plugin's element sits directly in <instrumenttrack>, before <eldata>
    body = re.search(r"<instrumenttrack\b[^>]*>(.*?)<eldata", text, re.S).group(1).strip()
    tag = re.match(r"<(\w+)", body).group(1)
    return f'<instrument name="{tag}">{body}</instrument>'


def xpf_eldata(path):
    """The preset's own <eldata> (instrument filter + volume / cutoff envelopes and LFOs) when it does anything -
    TripleOscillator, Organic and BitInvader presets get their pluck / swell / sweep from it - else None. The
    preset's chord / arpeggio settings are never taken: the engine writes the chords itself."""
    raw = open(path, "rb").read()
    try:
        text = raw.decode("utf-8")
        if "<eldata" not in text and "<instrument" not in text:
            raise ValueError
    except (UnicodeDecodeError, ValueError):
        import zlib
        text = zlib.decompress(raw[4:]).decode("utf-8")
    m = re.search(r"<eldata.*?</eldata>", text, re.S)
    if not m:
        return None
    eld = m.group(0)
    active = re.search(r'<eldata[^>]*fwet="1"', eld) or re.search(r'\samt="(?!0")[-\d.]+"', eld) or \
        re.search(r'\slamt="(?!0")[-\d.]+"', eld)
    return eld if active else None


def tripleosc(oscs):
    """oscs: 3 dicts (vol, pan, coarse, wave). wave: 0 sine 1 triangle 2 saw 3 square 4 moog 5 exp 6 noise."""
    a = {}
    for i, o in enumerate(oscs):
        a.update({f"vol{i}": o.get("vol", 0), f"pan{i}": o.get("pan", 0), f"coarse{i}": o.get("coarse", 0),
                  f"finel{i}": o.get("finel", 0), f"finer{i}": o.get("finer", 0), f"phoffset{i}": 0,
                  f"stphdetun{i}": 0, f"wavetype{i}": o.get("wave", 0), f"userwavefile{i}": ""})
    a.update(modalgo1=2, modalgo2=2, modalgo3=2)   # 2 = mix
    return f'<instrument name="tripleoscillator"><tripleoscillator {attrs(a)}/></instrument>'


def zyn_from_xiz(xiz_path, template_path, part_volume=96):
    """Embed a ZynAddSubFX .xiz preset (gzipped XML) into a full Zyn master state (part 0)."""
    raw = open(xiz_path, "rb").read()
    try:
        xiz = gzip.decompress(raw).decode("utf-8")
    except OSError:
        xiz = raw.decode("utf-8")
    inst = re.search(r"<INSTRUMENT>.*</INSTRUMENT>", xiz, re.S).group(0)
    tpl = open(template_path, encoding="utf-8").read()
    p0 = tpl.index('<PART id="0">')
    i0 = tpl.index("<INSTRUMENT>", p0)
    i1 = tpl.index("</INSTRUMENT>", i0) + len("</INSTRUMENT>")
    out = tpl[:i0] + inst + tpl[i1:]
    head_end = out.index("<INSTRUMENT>", p0)
    head = re.sub(r'(<par name="volume" value=")\d+(")', rf"\g<1>{part_volume}\g<2>", out[p0:head_end], count=1)
    return out[:p0] + head + out[head_end:]


# ---------------------------------------------------------------- effects (verified node/attribute names)
def effect(name, inner, wet=1.0, on=1):
    a = dict(name=name, on=on, wet=wet, gate=0, autoquit=1, autoquit_numerator=4, autoquit_denominator=4, syncmode=0)
    return f'<effect {attrs(a)}>{inner}</effect>'


def fx_reverbsc(size=0.85, color=8000, input_db=0, output_db=0, wet=0.3):
    a = dict(input_gain=input_db, size=size, color=color, output_gain=output_db)
    return effect("reverbsc", f'<ReverbSCControls {attrs(a)}/>', wet)


def fx_bitcrush(rate=22050, levels=64, in_gain=0, out_gain=0, noise=0, clip=0, wet=1.0):
    a = dict(ingain=in_gain, innoise=noise, outgain=out_gain, outclip=clip, rate=rate, stereodiff=0,
             levels=levels, rateon=1, depthon=1)
    return effect("bitcrush", f'<bitcrushcontrols {attrs(a)}/>', wet)


def fx_delay(time_s=0.375, feedback=0.3, lfo_hz=0.5, lfo_amt=0.0, out_db=0, wet=0.2):
    """Echo; or, with time_s=0.01, feedback=0, wet=1 and lfo_amt~0.0002, a tape-wow pitch wobble
    (measured: lfo_amt 0.001 = +/-21 cents)."""
    a = dict(DelayTimeSamples=time_s, FeebackAmount=feedback, LfoFrequency=lfo_hz, LfoAmount=lfo_amt,
             OutGain=out_db, syncmode=0)
    return effect("delay", f'<Delay {attrs(a)}/>', wet)


def fx_dualfilter(cut1=6000, res1=0.5, filter1=0, gain1=100, wet=1.0):
    """filter1: 0 LP, 1 HP, 7 2xLP, 11 RC LP24, 13 RC HP24. mix=-1 = filter 1 only."""
    a = dict(enabled1=1, filter1=filter1, cut1=cut1, res1=res1, gain1=gain1, mix=-1,
             enabled2=0, filter2=0, cut2=7000, res2=0.5, gain2=100)
    return effect("dualfilter", f'<DualFilterControls {attrs(a)}/>', wet)


def fx_eq(hp=None, lp=None, peaks=(), low_shelf=None, high_shelf=None, out_db=0, slope=12):
    """hp/lp: Hz or None. peaks: up to 4 (Hz, gain_db, bw). shelves: (Hz, gain_db). slope 12/24/48."""
    a = dict(Inputgain=0, Outputgain=out_db, AnalyseIn=0, AnalyseOut=0,
             HPactive=int(hp is not None), HPfreq=hp or 30, HPres=0.707,
             LPactive=int(lp is not None), LPfreq=lp or 18000, LPres=0.707,
             HP12=int(slope == 12), HP24=int(slope == 24), HP48=int(slope == 48),
             LP12=int(slope == 12), LP24=int(slope == 24), LP48=int(slope == 48),
             Lowshelfactive=int(low_shelf is not None), LowShelffreq=(low_shelf or (80, 0))[0],
             Lowshelfgain=(low_shelf or (80, 0))[1], LowShelfres=1.4,
             Highshelfactive=int(high_shelf is not None), Highshelffreq=(high_shelf or (8000, 0))[0],
             Highshelfgain=(high_shelf or (8000, 0))[1], HighShelfres=1.4)
    defaults = [(120, 0, 0.3), (250, 0, 0.3), (2000, 0, 0.3), (4000, 0, 0.3)]
    for i in range(4):
        f, g, bw = peaks[i] if i < len(peaks) else defaults[i]
        a[f"Peak{i+1}active"] = int(i < len(peaks))
        a[f"Peak{i+1}freq"], a[f"Peak{i+1}gain"], a[f"Peak{i+1}bw"] = f, g, bw
    return effect("eq", f'<Eq {attrs(a)}/>')


def fx_stereo(width=0):
    return effect("stereoenhancer", f'<stereoenhancercontrols {attrs(dict(width=width))}/>')


def fx_amp(volume=100, pan=0):
    return effect("amplifier", f'<AmplifierControls {attrs(dict(volume=volume, pan=pan, left=100, right=100))}/>')


def automatable(xml, name, obj_id, scale="linear"):
    """Make attribute `name` automatable in the self-closing element that carries it (anywhere in `xml`, e.g. a
    whole fx_dualfilter() effect): LMMS saves an automated knob as a child element <name id=... value=.../>
    that automation patterns point at with <object id=...>. obj_id must be unique in the project."""
    m = re.search(r'<(\w+)([^<>]*?)\s%s="([^"]*)"([^<>]*?)\s*/>' % re.escape(name), xml)
    tag, before, value, after = m.groups()
    child = f'<{name} {attrs(dict(id=obj_id, value=value, scale_type=scale))}/>'
    return xml[:m.start()] + f"<{tag}{before}{after}>{child}</{tag}>" + xml[m.end():]


def log_knob(real, lo, hi):
    """Automation value for a LOG-scaled knob (e.g. a filter cutoff): LMMS reads automation points of such
    knobs as knob positions and maps them through lo + (hi - lo) * position**e, where position = (v - lo) / hi
    (AutomatableModel::setAutomatedValue). So "3000" on a 1-20000 Hz cutoff would really mean ~117 Hz."""
    import math
    pos = ((max(lo, min(hi, real)) - lo) / (hi - lo)) ** (1 / math.e)
    return lo + pos * hi


def fxchain(effects):
    if not effects:
        return '<fxchain numofeffects="0" enabled="0"/>'
    return f'<fxchain numofeffects="{len(effects)}" enabled="1">{"".join(effects)}</fxchain>'


# ---------------------------------------------------------------- song structure
class Note:
    __slots__ = ("pos", "len", "key", "vol", "pan")

    def __init__(self, pos, length, key, vol=100, pan=0):
        self.pos, self.len, self.key = int(round(pos)), int(round(length)), key
        self.vol, self.pan = int(round(vol)), pan

    def xml(self):
        return f'<note pos="{self.pos}" len="{self.len}" key="{self.key}" vol="{max(1, min(200, self.vol))}" pan="{self.pan}"/>'


class Pattern:
    def __init__(self, name, pos, length, notes):
        self.name, self.pos, self.len, self.notes = name, pos, length, notes

    def xml(self):
        body = "".join(n.xml() for n in sorted(self.notes, key=lambda n: (n.pos, n.key)))
        return f'<pattern {attrs(dict(type=1, muted=0, steps=16, name=self.name, pos=self.pos, len=self.len))}>{body}</pattern>'


class InstrumentTrack:
    def __init__(self, name, instrument_xml, vol=100, pan=0, fxch=0, basenote=57, eld=None, muted=0, pitch=0):
        self.name, self.instrument_xml, self.vol, self.pan, self.fxch = name, instrument_xml, vol, pan, fxch
        self.pitch = pitch                # track pitch in cents (-100..100)
        self.basenote, self.eld, self.muted = basenote, eld or eldata(), muted
        self.patterns = []

    def xml(self):
        it = attrs(dict(vol=self.vol, pan=self.pan, fxch=self.fxch, pitch=self.pitch, basenote=self.basenote,
                        usemasterpitch=1, pitchrange=1))
        return (f'<track {attrs(dict(type=0, muted=self.muted, solo=0, name=self.name))}>'
                f'<instrumenttrack {it}>{self.instrument_xml}{self.eld}'
                '<chordcreator chord="0" chordrange="1" chord-enabled="0"/>'
                '<arpeggiator arp="0" arprange="1" arptime="100" arpgate="100" arpdir="0" arpmode="0" syncmode="0" '
                'arp-enabled="0" arptime_numerator="4" arptime_denominator="4"/>'
                '<midiport inputchannel="0" outputchannel="1" inputcontroller="0" outputcontroller="0" fixedinputvelocity="-1" '
                'fixedoutputvelocity="-1" fixedoutputnote="-1" outputprogram="1" basevelocity="127" readable="0" writable="0"/>'
                f'{fxchain([])}</instrumenttrack>{"".join(p.xml() for p in self.patterns)}</track>')


class AutomationTrack:
    """One automation track moving one knob (obj_id) through (tick, value) points; prog 1 = linear between
    points (dense points make any curve)."""

    def __init__(self, name, obj_id, points, prog=1):
        self.name, self.obj_id, self.points, self.prog = name, obj_id, points, prog

    def xml(self):
        end = max(t for t, _ in self.points)
        length = max(TPB, -(-(end + 1) // TPB) * TPB)
        times = "".join(f'<time pos="{int(t)}" value="{round(v, 5)}"/>' for t, v in self.points)
        pat = attrs(dict(name=self.name, pos=0, len=length, tens=1, mute=0, prog=self.prog))
        return (f'<track {attrs(dict(type=5, muted=0, solo=0, name=self.name))}><automationtrack/>'
                f'<automationpattern {pat}>{times}<object id="{self.obj_id}"/></automationpattern></track>')


class Project:
    def __init__(self, bpm=75, master_vol=50):
        self.bpm, self.master_vol = bpm, master_vol
        self.tracks, self.channels, self.master_effects = [], {}, []
        self.notes, self.loop = "", None
        self.automation = []            # AutomationTrack list
        self.volume_ids = {}            # mixer channel -> automation object id of its volume

    def add(self, track):
        self.tracks.append(track)
        return track

    def channel(self, num, name, volume=1.0, effects=None):
        self.channels[num] = (name, volume, effects or [])

    def xml(self):
        def vol_xml(num, vol):
            if num in self.volume_ids:            # automated: the volume becomes a child element with an id
                return "", f'<volume {attrs(dict(id=self.volume_ids[num], value=vol, scale_type="linear"))}/>'
            return f' volume="{vol}"', ""
        va, vc = vol_xml(0, 1)
        chans = [f'<fxchannel num="0" name="Master"{va} muted="0" soloed="0">{fxchain(self.master_effects)}{vc}</fxchannel>']
        for num in sorted(self.channels):
            name, vol, fx = self.channels[num]
            va, vc = vol_xml(num, vol)
            chans.append(f'<fxchannel num="{num}" name={quoteattr(name)}{va} muted="0" soloed="0">'
                         f'{fxchain(fx)}{vc}<send channel="0" amount="1"/></fxchannel>')
        lp = self.loop or (0, TPB * 4)
        return ('<?xml version="1.0"?>\n<!DOCTYPE lmms-project>\n'
                '<lmms-project version="1.0" creator="LMMS" creatorversion="1.2.2" type="song">'
                f'<head bpm="{self.bpm}" timesig_numerator="4" timesig_denominator="4" mastervol="{self.master_vol}" masterpitch="0"/>'
                '<song><trackcontainer type="song" visible="1" x="5" y="5" width="900" height="500" maximized="0" minimized="0">'
                + "".join(t.xml() for t in self.tracks) + "".join(a.xml() for a in self.automation) +
                '</trackcontainer><track type="6" muted="0" solo="0" name="Automation track"><automationtrack/></track>'
                f'<fxmixer visible="1" x="5" y="520" width="700" height="330" maximized="0" minimized="0">{"".join(chans)}</fxmixer>'
                '<ControllerRackView visible="0" width="258" height="173" x="680" y="310" maximized="0" minimized="0"/>'
                '<pianoroll visible="0" width="640" height="480" x="1" y="1" maximized="0" minimized="0"/>'
                '<automationeditor visible="0" width="640" height="400" x="1" y="1" maximized="0" minimized="0"/>'
                f'<projectnotes visible="0" width="400" height="300" x="700" y="10" maximized="0" minimized="0"><![CDATA[{self.notes}]]></projectnotes>'
                f'<timeline lp0pos="{lp[0]}" lp1pos="{lp[1]}" lpstate="1"/><controllers/></song></lmms-project>\n')

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.xml())
