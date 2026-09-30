"""Sound palette: every instrument, drum kit and texture the engine can use.

`vol` values are LMMS track volumes that hit the mix-role loudness targets (see ROLE_TARGET) with the
engine's fixed mixer (master 50 %, Leads channel 1.75). They were measured by rendering stems, so a
song built from `measured=True` entries is balanced before any calibration.

`octave` is the transposition (semitones) to write so the preset SOUNDS at the written pitch - some Zyn
presets play an octave low (e.g. Soft Vibes). `None` means not yet checked: run
`lofi.py audition <id>` and record the result here (or override per song in the spec's "instruments").
"""

ZYN = "ZynAddSubFX"   # under <lmms data>/presets/
SF2_DIR = "soundfonts"   # under <workingdir>/samples/ - see soundfonts/licenses/ (FreePats CC0 + GeneralUser GS)
GUGS = "soundfonts/generaluser_gs.sf2"


def gs(patch, bank=0):
    """A GeneralUser GS 1.472 preset (General MIDI program numbers, 0-based)."""
    return dict(kind="sf2", file=GUGS, bank=bank, patch=patch)


def fp(name):
    """A FreePats single-instrument SoundFont (CC0)."""
    return dict(kind="sf2", file=f"soundfonts/{name}.sf2", bank=0, patch=0)


def z(preset, label, role, **kw):
    """A ZynAddSubFX factory preset."""
    return dict(label=label, kind="zyn", preset=preset, vol=40, octave=0, role=role, measured=False, retune=True, **kw)


def x(preset, label, role, **kw):
    """An LMMS factory instrument preset (.xpf) - any plugin; its own envelopes / filter come along."""
    return dict(label=label, kind="xpf", preset=preset, vol=40, octave=0, role=role, measured=False, retune=True, **kw)


# Voicing ranges (lowest, highest, centre MIDI note) for the chord instrument; default (52, 74, 62).
PIANO_VOICING = (53, 77, 65)
GUITAR_VOICING = (50, 74, 61)

INSTRUMENTS = {
    # ---------------------------------------------------------------- keys (chords)
    "rhodes": dict(label="Rhodes", kind="zyn", preset="Rhodes/0041-Soft Rhodes.xiz", vol=153, octave=0,
                   role="keys", measured=True, note="warm, soft attack; the default lofi keys"),
    "dx_rhodes": dict(label="DX Rhodes", kind="zyn", preset="Rhodes/0001-DX Rhodes 1.xiz", vol=150, octave=None,
                      role="keys", measured=False, note="brighter FM tine"),
    "fm_rhodes": dict(label="FM Rhodes", kind="zyn", preset="Rhodes/0033-FM Rhodes 1.xiz", vol=150, octave=None,
                      role="keys", measured=False),
    "soft_piano": dict(label="Soft Piano", kind="zyn", preset="SynthPiano/0001-Soft Piano 1.xiz", vol=150, octave=None,
                       role="keys", measured=False, note="felt-piano-ish alternative to Rhodes"),
    # ---------------------------------------------------------------- leads (melodies)
    "vibes": dict(label="Vibes", kind="zyn", preset="Collection/0003-Soft Vibes.xiz", vol=123, octave=12,
                  role="lead", measured=True, note="preset sounds an octave low; has built-in tremolo"),
    "flute": dict(label="Flute", kind="zyn", preset="ReedAndWind/0001-Flute 1.xiz", vol=101, octave=0,
                  role="lead", measured=True, note="breathy, steady; Nujabes-style hooks and long tones"),
    "bell": dict(label="Soft Bell", kind="tripleosc", vol=13, octave=0, role="lead", measured=True,
                 oscs=[dict(vol=100, wave=0), dict(vol=22, wave=0, coarse=12), dict(vol=12, wave=1, coarse=24)],
                 fcut=3200, env=dict(att=0.004, hold=0.02, dec=0.9, sus=0.15, rel=0.35, amt=1),
                 note="simple sine bell, very unobtrusive - good for voice beds"),
    "vibraphone": dict(label="Vibraphone", kind="zyn", preset="Collection/0002-Vibraphone.xiz", vol=120, octave=12,
                       role="lead", measured=False),
    # ---------------------------------------------------------------- pads
    "soft_saw_pad": dict(label="Pad", kind="zyn", preset="Strings/0045-Soft Saw Pad.xiz", vol=33, octave=0,
                         role="pad", measured=True),
    "dark_strings": dict(label="Strings", kind="zyn", preset="Strings/0034-Dark Strings.xiz", vol=33, octave=12,
                         role="pad", measured=False, note="sounds an octave low"),
    # ---------------------------------------------------------------- bass
    "warm_sine": dict(label="Bass", kind="tripleosc", vol=26, octave=0, role="bass", measured=True,
                      oscs=[dict(vol=100, wave=0), dict(vol=50, wave=1), dict(vol=16, wave=0, coarse=12)],
                      fcut=700, env=dict(att=0.002, hold=0.04, dec=0.55, sus=0.5, rel=0.08, amt=1),
                      note="sine body + triangle harmonics so phones still hear it"),

    # ================================================================ SoundFont instruments
    # (FluidSynth inside LMMS; sampled, so they sound like real instruments - the backbone of the styles)
    # ---------------------------------------------------------------- keys / comping
    "upright_piano": dict(fp("upright_piano_kw"), label="Piano", vol=40, octave=0, role="keys", measured=False,
                          voicing=PIANO_VOICING, note="real Kawai upright, 2 velocity layers - sleepy piano"),
    "grand_piano": dict(gs(0), label="Grand piano", vol=40, octave=0, role="keys", measured=False,
                        voicing=PIANO_VOICING),
    "tine_ep": dict(gs(4), label="Tine EP", vol=40, octave=0, role="keys", measured=False,
                    note="sampled Rhodes-type tine piano - warmer and more real than the Zyn rhodes"),
    "chorus_ep": dict(gs(4, bank=8), label="Chorus EP", vol=40, octave=0, role="keys", measured=False,
                      note="tine EP with chorus - neo-soul / Dilla"),
    "fm_epiano": dict(fp("fm_epiano"), label="FM EP", vol=40, octave=0, role="keys", measured=False,
                      voicing=(52, 77, 64), chorus=1, note="DX7 'E.Piano 1' - the 80s city-pop sound"),
    "drawbar_organ": dict(fp("drawbar_organ"), label="Organ", vol=30, octave=0, role="keys", measured=False,
                          note="Hammond-style drawbar organ - gospel/neo-soul pads and stabs"),
    "clavinet": dict(gs(7), label="Clav", vol=35, octave=0, role="keys", measured=False),
    "nylon_guitar": dict(fp("nylon_guitar"), label="Nylon guitar", vol=40, octave=0, role="keys", measured=False,
                         voicing=GUITAR_VOICING, strum=4, note="Spanish classical guitar - bossa comping"),
    "jazz_guitar": dict(fp("jazz_guitar"), label="Jazz guitar", vol=40, octave=0, role="keys", measured=False,
                        voicing=GUITAR_VOICING, strum=3, note="clean electric (jazz amp) - city-pop / chillhop"),
    "muted_guitar": dict(gs(28), label="Muted guitar", vol=40, octave=0, role="keys", measured=False,
                         voicing=GUITAR_VOICING, strum=2, note="palm-muted electric - city-pop 'cutting'"),
    # ---------------------------------------------------------------- leads
    "tenor_sax": dict(fp("tenor_sax"), label="Tenor sax", vol=40, octave=0, role="lead", measured=False,
                      note="breathy tenor - bossa / city-pop hooks; keep it between Bb3 and F5"),
    "kalimba": dict(fp("kalimba"), label="Kalimba", vol=40, octave=0, role="lead", measured=False,
                    note="plucked thumb piano - sleepy / dreamy answers"),
    "piano_lead": dict(fp("upright_piano_kw"), label="Piano melody", vol=40, octave=0, role="lead", measured=False,
                       note="the upright piano playing the melody (right hand) on the Leads channel"),
    "muted_trumpet": dict(gs(59), label="Muted trumpet", vol=40, octave=0, role="lead", measured=False),
    "gs_vibes": dict(gs(11), label="Vibraphone GS", vol=40, octave=0, role="lead", measured=False,
                     note="sampled vibraphone (no octave quirk, unlike the Zyn vibes)"),
    "music_box": dict(gs(10), label="Music box", vol=40, octave=0, role="lead", measured=False),
    "marimba": dict(gs(12), label="Marimba", vol=40, octave=0, role="lead", measured=False),
    "gs_flute": dict(gs(73), label="Flute GS", vol=40, octave=0, role="lead", measured=False),
    "square_lead": dict(gs(80), label="Square lead", vol=30, octave=0, role="lead", measured=False,
                        note="80s synth lead - city-pop hooks"),
    # ---------------------------------------------------------------- pads
    "synth_strings": dict(fp("synth_strings"), label="Synth strings", vol=30, octave=0, role="pad", measured=False,
                          note="80s string machine - city-pop"),
    "strings": dict(gs(49), label="Strings", vol=30, octave=0, role="pad", measured=False,
                    note="slow orchestral strings - sleepy / cinematic"),
    "warm_pad": dict(gs(89), label="Warm pad", vol=30, octave=0, role="pad", measured=False),
    # ---------------------------------------------------------------- bass
    "upright_bass": dict(gs(32), label="Upright bass", vol=40, octave=0, role="bass", measured=False,
                         note="acoustic double bass - bossa, jazz, sleepy"),
    "finger_bass": dict(fp("finger_bass"), label="Finger bass", vol=40, octave=0, role="bass", measured=False,
                        note="electric bass, fingers - neo-soul, city-pop"),
    "slap_bass": dict(gs(36), label="Slap bass", vol=40, octave=0, role="bass", measured=False),
    "fretless_bass": dict(gs(35), label="Fretless bass", vol=40, octave=0, role="bass", measured=False),
    "lately_bass": dict(fp("lately_bass"), label="Synth bass", vol=40, octave=0, role="bass", measured=False,
                        note="TX81Z 'Lately Bass' - the FM synth bass of 80s pop / city-pop"),

    # ================================================================ General MIDI (GeneralUser GS) - the
    # sample-based 16-bit console palette (SNES / arcade / early CD games used exactly this kind of set)
    "harp": dict(gs(46), label="Harp", vol=40, octave=0, role="keys", measured=False, voicing=PIANO_VOICING, strum=3),
    "pizz_strings": dict(gs(45), label="Pizzicato", vol=40, octave=0, role="keys", measured=False),
    "orch_strings": dict(gs(48), label="Orch strings", vol=30, octave=0, role="pad", measured=False,
                         note="faster-attack string section - usable for comping too"),
    "choir": dict(gs(52), label="Choir", vol=30, octave=0, role="pad", measured=False),
    "harpsichord": dict(gs(6), label="Harpsichord", vol=40, octave=0, role="keys", measured=False),
    "accordion": dict(gs(21), label="Accordion", vol=40, octave=0, role="keys", measured=False),
    "acoustic_guitar": dict(gs(25), label="Acoustic guitar", vol=40, octave=0, role="keys", measured=False,
                            voicing=GUITAR_VOICING, strum=4),
    "dist_guitar": dict(gs(30), label="Dist guitar", vol=30, octave=0, role="keys", measured=False,
                        voicing=GUITAR_VOICING, strum=2, note="distorted guitar - 16-bit boss battles"),
    "glockenspiel": dict(gs(9), label="Glockenspiel", vol=40, octave=0, role="lead", measured=False),
    "celesta": dict(gs(8), label="Celesta", vol=40, octave=0, role="lead", measured=False),
    "xylophone": dict(gs(13), label="Xylophone", vol=40, octave=0, role="lead", measured=False),
    "tubular_bells": dict(gs(14), label="Tubular bells", vol=40, octave=0, role="lead", measured=False),
    "trumpet": dict(gs(56), label="Trumpet", vol=40, octave=0, role="lead", measured=False),
    "french_horns": dict(gs(60), label="Horns", vol=40, octave=0, role="lead", measured=False,
                         note="heroic themes; also as a pad (pad: french_horns)"),
    "brass_section": dict(gs(61), label="Brass", vol=40, octave=0, role="lead", measured=False),
    "synth_brass": dict(gs(62), label="Synth brass", vol=40, octave=0, role="lead", measured=False),
    "oboe": dict(gs(68), label="Oboe", vol=40, octave=0, role="lead", measured=False),
    "clarinet": dict(gs(71), label="Clarinet", vol=40, octave=0, role="lead", measured=False),
    "piccolo": dict(gs(72), label="Piccolo", vol=40, octave=0, role="lead", measured=False),
    "recorder": dict(gs(74), label="Recorder", vol=40, octave=0, role="lead", measured=False),
    "pan_flute": dict(gs(75), label="Pan flute", vol=40, octave=0, role="lead", measured=False),
    "ocarina": dict(gs(79), label="Ocarina", vol=40, octave=0, role="lead", measured=False),
    "saw_lead": dict(gs(81), label="Saw lead", vol=30, octave=0, role="lead", measured=False),
    "contrabass": dict(gs(43), label="Contrabass", vol=40, octave=0, role="bass", measured=False),
    "tuba": dict(gs(58), label="Tuba", vol=40, octave=0, role="bass", measured=False),
    "synth_bass": dict(gs(38), label="Synth bass GS", vol=40, octave=0, role="bass", measured=False),

    # ================================================================ FM (OpulenZ = Yamaha OPL2 / AdLib) - the
    # DOS / Sega Genesis sound. "xpf" = LMMS factory preset; "opl2" = patch defined here (params -> lmmsgen.opl2)
    "opl_brass": dict(kind="xpf", preset="OpulenZ/Brass.xpf", label="FM brass", vol=40, octave=0, role="lead", measured=False),
    "opl_epiano": dict(kind="xpf", preset="OpulenZ/Epiano.xpf", label="FM piano", vol=40, octave=0, role="keys", measured=False),
    "opl_bells": dict(kind="xpf", preset="OpulenZ/Bells.xpf", label="FM bells", vol=40, octave=0, role="lead", measured=False),
    "opl_harp": dict(kind="xpf", preset="OpulenZ/Harp.xpf", label="FM harp", vol=40, octave=0, role="keys", measured=False),
    "opl_organ": dict(kind="xpf", preset="OpulenZ/Organ_leslie.xpf", label="FM organ", vol=40, octave=0, role="keys", measured=False),
    "opl_clarinet": dict(kind="xpf", preset="OpulenZ/Clarinet.xpf", label="FM clarinet", vol=40, octave=0, role="lead", measured=False),
    "opl_pad": dict(kind="xpf", preset="OpulenZ/Halo_pad.xpf", label="FM pad", vol=40, octave=0, role="pad", measured=False),
    "opl_square": dict(kind="xpf", preset="OpulenZ/Square.xpf", label="FM square", vol=40, octave=0, role="lead", measured=False),
    "opl_vibes": dict(kind="xpf", preset="OpulenZ/Vibraphone.xpf", label="FM vibes", vol=40, octave=0, role="lead", measured=False),
    "opl_synth": dict(kind="xpf", preset="OpulenZ/Cheesy_synth.xpf", label="FM synth", vol=40, octave=0, role="keys", measured=False),
    "opl_bass": dict(kind="opl2", label="FM bass", vol=40, octave=0, role="bass", measured=False,
                     params=dict(fm=1, feedback=5, op1_mul=1, op1_lvl=46, op1_a=0, op1_d=8, op1_s=4, op1_r=6, op1_perc=1,
                                 op2_mul=1, op2_lvl=60, op2_a=0, op2_d=6, op2_s=12, op2_r=4),
                     note="plucky Genesis-style FM bass (brightness decays after the attack)"),
    "opl_lead": dict(kind="opl2", label="FM lead", vol=40, octave=0, role="lead", measured=False,
                     params=dict(fm=1, feedback=6, op1_mul=1, op1_lvl=48, op1_a=1, op1_d=8, op1_s=12, op1_r=6,
                                 op2_mul=1, op2_lvl=56, op2_a=1, op2_d=0, op2_s=15, op2_r=6, vib_depth=1, op2_vib=1),
                     note="brassy saw-like FM lead with vibrato"),

    # ================================================================ electronic (LMMS's own synths: Zyn, TripleOscillator,
    # Organic presets - generated sound, nothing to license). Pads / plucks / bells / basses for ambient, deep focus,
    # minimal and downtempo (lmms-electronic). z() = Zyn preset, x() = LMMS factory preset (keeps its envelopes)
    # pads
    "soft_pad": z("Pads/0065-Soft Pad.xiz", "Soft pad", "pad"),
    "ice_pad": z("Collection/0065-Ice Field.xiz", "Ice pad", "pad"),
    "sweep_pad": z("Collection/0061-Sweep Pad.xiz", "Sweep pad", "pad"),
    "dream_pad": z("Fantasy/0033-ImpossibleDream1.xiz", "Dream pad", "pad"),
    "void_pad": z("Fantasy/0001-Emptyness1.xiz", "Void pad", "pad"),
    "analog_pad": z("Pads/0003-Analog Pad 1.xiz", "Analog pad", "pad"),
    "space_choir": z("Fantasy/0065-Long SpaceChoir1.xiz", "Space choir", "pad"),
    "ethereal_pad": x("Organic/pad_ethereal.xpf", "Ethereal pad", "pad"),
    "hi_pad": x("TripleOscillator/HiPad.xpf", "Hi pad", "pad"),
    "wind": z("Noises/0006-Wind.xiz", "Wind", "pad"),
    # plucks / arps (played with keys patterns)
    "house_pluck": z("Plucked/progressive-house-pluck.xiz", "House pluck", "keys"),
    "soft_arp": z("Arpeggios/0039-Soft Arpeggio1.xiz", "Soft arp", "keys"),
    "glass_arp": z("Arpeggios/0068-Glass Arpeggio.xiz", "Glass arp", "keys"),
    "pluck_arp": x("TripleOscillator/PluckArpeggio.xpf", "Pluck arp", "keys"),
    "ping": x("TripleOscillator/ArpeggioPing.xpf", "Ping", "keys"),
    "pluck": z("Plucked/0001-Plucked 1.xiz", "Pluck", "keys"),
    "ice_rhodes": z("Rhodes/0012-Ice Rhodes1.xiz", "Ice Rhodes", "keys"),
    # bells / soft leads
    "chimes": z("Collection/0004-Simple Chimes.xiz", "Chimes", "lead"),
    "soft_hammer": z("Collection/0006-Soft Hammer.xiz", "Soft hammer", "lead"),
    "muffled_bells": z("Companion/0004-Muffled Bells.xiz", "Muffled bells", "lead",
                       note="slow attack: long notes only - short notes are nearly silent"),
    "crystal_bells": z("Misc/0002-Bells 1.xiz", "Crystal bells", "lead"),
    "analog_bell": x("TripleOscillator/AnalogBell.xpf", "Analog bell", "lead"),
    "soft_flute": z("Collection/0057-Soft Flute.xiz", "Soft flute", "lead"),
    # basses
    "sub_bass": dict(label="Sub bass", kind="tripleosc", vol=26, octave=0, role="bass", measured=False,
                     oscs=[dict(vol=100, wave=0), dict(vol=0, wave=0), dict(vol=0, wave=0)],
                     fcut=400, env=dict(att=0.004, hold=0.1, dec=0.4, sus=0.9, rel=0.06, amt=1),
                     note="pure sine sub - felt more than heard; pair with a pluck or keys for the notes"),
    "decay_bass": z("Collection/0044-Decay Bass.xiz", "Decay bass", "bass"),
    "analog_bass": z("Bass/0006-Analogue Bass.xiz", "Analog bass", "bass"),
    "thick_bass": z("Companion/0055-Thick Bass.xiz", "Thick bass", "bass"),
    "pluck_bass": x("TripleOscillator/PluckBass.xpf", "Pluck bass", "bass"),
    "reso_bass": x("TripleOscillator/ResoBass.xpf", "Reso bass", "bass"),
    "acid_bass": x("TripleOscillator/TB303.xpf", "Acid bass", "bass"),
}

# drum kits: part -> (source, vol, extra)   extra: pan, fcut (instrument low-pass), reversed
# source: a sample path (AudioFileProcessor) or a SoundFont hit {"sf2", "bank", "patch", "note"}.
WP = "soundfonts/world_percussion.sf2"     # FreePats world percussion (CC0), key map in its README
SP = "soundfonts/synth_percussion.sf2"     # FreePats analog-style drum machine (CC0)


def hit(sf2, note, bank=0, patch=0):
    return {"sf2": sf2, "bank": bank, "patch": patch, "note": note}


def brush(note):
    return hit(GUGS, note, 128, 40)          # GeneralUser GS "Brush" kit


REVERSE_CRASH = ("drums/crash02.ogg", 27, {"fcut": 6000, "reversed": 1, "seconds": 2.552721})


def gm_kit(program):
    """A General MIDI drum kit from GeneralUser GS (bank 128): standard GM key map."""
    k = lambda note: hit(GUGS, note, 128, program)
    return {
        "kick": (k(36), 40, {}), "snare": (k(38), 40, {"pan": 3}), "sidestick": (k(37), 40, {"pan": -8}),
        "clap": (k(39), 40, {"pan": -6}), "hat": (k(42), 40, {"pan": 12}), "pedal_hat": (k(44), 40, {"pan": 12}),
        "open_hat": (k(46), 40, {"pan": 15}), "crash": (k(49), 40, {"pan": 20}), "ride": (k(51), 40, {"pan": -18}),
        "tom_hi": (k(48), 40, {"pan": 12}), "tom_lo": (k(43), 40, {"pan": -12}), "tambourine": (k(54), 40, {"pan": 20}),
        "shaker": (k(70), 40, {"pan": -25}), "reverse_crash": REVERSE_CRASH,
    }

KITS = {
    "dusty": {
        "kick": ("drums/kick_hiphop01.ogg", 54, {}),
        "snare": ("drums/snare_hiphop02.ogg", 60, {"fcut": 9000}),
        "snare_body": ("drums/snare_muffled02.ogg", 41, {}),
        "hat": ("drums/hihat_closed03.ogg", 110, {"pan": 12, "fcut": 8000}),
        "open_hat": ("drums/hihat_opened01.ogg", 33, {"pan": 15, "fcut": 7000}),
        "sidestick": ("drums/sidestick01.ogg", 110, {"pan": -10}),
        "shaker": ("drums/shaker02.ogg", 86, {"pan": -25, "fcut": 7000}),
        "ride": ("drums/ride01.ogg", 40, {"pan": -18, "fcut": 7000}),
        "crash": ("drums/crash01.ogg", 49, {"pan": 20, "fcut": 6000}),
        "reverse_crash": REVERSE_CRASH,
    },
    # jazz brushes: sleepy piano, ballads, soft bossa
    "brushes": {
        "kick": (brush(36), 40, {}),
        "snare": (brush(38), 40, {"pan": 5}),
        "brush_swirl": (brush(40), 40, {"pan": -8}),
        "sidestick": (brush(37), 40, {"pan": -10}),
        "hat": (brush(42), 40, {"pan": 12}),
        "pedal_hat": (brush(44), 40, {"pan": 12}),
        "open_hat": (brush(46), 40, {"pan": 15}),
        "ride": (brush(51), 40, {"pan": -18}),
        "crash": (brush(49), 40, {"pan": 20}),
        "shaker": (hit(WP, 56), 40, {"pan": -25}),
        "tom_hi": (brush(45), 40, {"pan": 10}),
        "tom_lo": (brush(41), 40, {"pan": -10}),
        "reverse_crash": REVERSE_CRASH,
    },
    # bossa / latin: jazz kick + rim, real hand percussion
    "latin": {
        "kick": (brush(36), 40, {}),
        "snare": (brush(38), 40, {"pan": 5}),
        "sidestick": (brush(37), 40, {"pan": -8}),
        "hat": (brush(42), 40, {"pan": 12}),
        "open_hat": (brush(46), 40, {"pan": 15}),
        "ride": (brush(51), 40, {"pan": -18}),
        "crash": (brush(49), 40, {"pan": 20}),
        "shaker": (hit(WP, 55), 40, {"pan": -25}),
        "conga_hi": (hit(WP, 63), 40, {"pan": 25}),
        "conga_lo": (hit(WP, 64), 40, {"pan": 30}),
        "conga_mute": (hit(WP, 65), 40, {"pan": 25}),
        "bongo_hi": (hit(WP, 52), 40, {"pan": -30}),
        "bongo_lo": (hit(WP, 53), 40, {"pan": -30}),
        "claves": (hit(WP, 60), 40, {"pan": -15}),
        "tambourine": (hit(WP, 57), 40, {"pan": 20}),
        "reverse_crash": REVERSE_CRASH,
    },
    # 80s drum machine: city-pop
    "drum_machine": {
        "kick": (hit(SP, 48), 40, {}),
        "snare": (hit(SP, 50), 40, {}),
        "clap": (hit(SP, 63), 40, {"pan": -6}),
        "sidestick": (hit(SP, 66), 40, {"pan": -10}),
        "hat": (hit(SP, 52), 40, {"pan": 12}),
        "open_hat": (hit(SP, 54), 40, {"pan": 15}),
        "crash": (hit(SP, 55), 40, {"pan": 20}),
        "ride": (hit(SP, 56), 40, {"pan": -18}),
        "shaker": (hit(SP, 64), 40, {"pan": -25}),
        "tom_hi": (hit(SP, 61), 40, {"pan": 15}),
        "tom_lo": (hit(SP, 57), 40, {"pan": -15}),
        "reverse_crash": REVERSE_CRASH,
    },
    # General MIDI kits (GeneralUser GS): 16-bit console / arcade drums
    "gs_standard": gm_kit(0),
    "gs_power": gm_kit(16),
    # orchestral: concert bass drum + snare, orchestral hi-hats and ride, castanets; the toms are TIMPANI tuned
    # to the song (tonic + fifth, engine.timpani_notes; F2 / C3 below are only the measuring notes), so a
    # "toms" fill is a timpani roll
    "gs_orchestral": {
        "kick": (hit(GUGS, 36, 128, 48), 40, {}),
        "snare": (hit(GUGS, 38, 128, 48), 40, {"pan": 5}),
        "sidestick": (hit(GUGS, 37, 128, 48), 40, {"pan": -8}),
        "claves": (hit(GUGS, 39, 128, 48), 40, {"pan": -15}),       # castanets
        "tom_lo": (hit(GUGS, 41, 128, 48), 40, {"pan": -10, "timpani": "low"}),
        "tom_hi": (hit(GUGS, 48, 128, 48), 40, {"pan": 10, "timpani": "high"}),
        "hat": (hit(GUGS, 27, 128, 48), 40, {"pan": 12}),
        "pedal_hat": (hit(GUGS, 28, 128, 48), 40, {"pan": 12}),
        "open_hat": (hit(GUGS, 29, 128, 48), 40, {"pan": 15}),
        "ride": (hit(GUGS, 30, 128, 48), 40, {"pan": -18}),
        "crash": (hit(GUGS, 57, 128, 48), 40, {"pan": 20}),
        "tambourine": (hit(GUGS, 54, 128, 48), 40, {"pan": 20}),
        "reverse_crash": REVERSE_CRASH,
    },
    # electronic drum machines (lmms-electronic): GeneralUser GS "808/909" kit (bank 128, program 25 - real TR-808 and
    # TR-909 samples) + LMMS's DrumSynth models (drumsynth/*.ds, rendered by AudioFileProcessor)
    "tr808": {
        "kick": (hit(GUGS, 35, 128, 25), 40, {}),
        "snare": (hit(GUGS, 38, 128, 25), 40, {"pan": 4}),
        "clap": (hit(GUGS, 39, 128, 25), 40, {"pan": -6}),
        "sidestick": (hit(GUGS, 37, 128, 25), 40, {"pan": -10}),
        "hat": (hit(GUGS, 42, 128, 25), 40, {"pan": 12}),
        "pedal_hat": (hit(GUGS, 44, 128, 25), 40, {"pan": 12}),
        "open_hat": (hit(GUGS, 46, 128, 25), 40, {"pan": 15}),
        "crash": (hit(GUGS, 49, 128, 25), 40, {"pan": 20}),
        "ride": (hit(GUGS, 51, 128, 25), 40, {"pan": -18}),
        "claves": ("drumsynth/tr808/Clave.ds", 40, {"pan": -15}),
        "tom_hi": ("drumsynth/tr808/Tom_hi.ds", 40, {"pan": 12}),
        "tom_lo": ("drumsynth/tr808/Tom_lo.ds", 40, {"pan": -12}),
        "shaker": (hit(WP, 55), 40, {"pan": -25}),
        "tambourine": (hit(GUGS, 54, 128, 25), 40, {"pan": 20}),
        "reverse_crash": REVERSE_CRASH,
    },
    "tr909": {
        "kick": (hit(GUGS, 36, 128, 25), 40, {}),
        "snare": (hit(GUGS, 40, 128, 25), 40, {"pan": 4}),
        "clap": ("drumsynth/tr909/Clap.ds", 40, {"pan": -6}),
        "sidestick": ("drumsynth/tr808/Rimshot.ds", 40, {"pan": -10}),
        "hat": ("drumsynth/tr909/Hat-c.ds", 40, {"pan": 12}),
        "pedal_hat": ("drumsynth/tr909/Hat-c2.ds", 40, {"pan": 12}),
        "open_hat": ("drumsynth/tr909/Hat-o.ds", 40, {"pan": 15}),
        "crash": (hit(GUGS, 49, 128, 26), 40, {"pan": 20}),
        "ride": (hit(GUGS, 51, 128, 26), 40, {"pan": -18}),
        "tom_hi": ("drumsynth/tr808/Tom_hi.ds", 40, {"pan": 12}),
        "tom_lo": ("drumsynth/tr808/Tom_lo.ds", 40, {"pan": -12}),
        "shaker": (hit(WP, 55), 40, {"pan": -25}),
        "tambourine": (hit(GUGS, 54, 128, 26), 40, {"pan": 20}),
        "reverse_crash": REVERSE_CRASH,
    },
    # soft electronics for focus / ambient pulses: 808 kick, DrumSynth "sleepy" hats, rim, shaker
    "soft_electro": {
        "kick": ("drumsynth/tr808/Kick.ds", 40, {"fcut": 3000}),
        "snare": ("drumsynth/tr808/Snare.ds", 40, {"pan": 4, "fcut": 6000}),
        "clap": ("drumsynth/misc_claps/clap.ds", 40, {"pan": -6, "fcut": 7000}),
        "sidestick": ("drumsynth/tr808/Rimshot.ds", 40, {"pan": -10}),
        "hat": ("drumsynth/misc_hats/sleepy_1.ds", 40, {"pan": 12}),
        "open_hat": ("drumsynth/misc_hats/sleepy_2.ds", 40, {"pan": 15}),
        "ride": ("drumsynth/misc_hats/sleepy_ride.ds", 40, {"pan": -18}),
        "claves": ("drumsynth/tr808/Clave.ds", 40, {"pan": -15}),
        "shaker": (hit(WP, 55), 40, {"pan": -25}),
        "crash": (hit(GUGS, 49, 128, 25), 40, {"pan": 20, "fcut": 7000}),
        "reverse_crash": REVERSE_CRASH,
    },
    # Dilla / neo-soul: dusty samples, snare layered with a clap, crushed on the drum bus (see styles.py)
    "dilla": {
        "kick": ("drums/kick_hiphop01.ogg", 54, {"fcut": 5000}),
        "snare": ("drums/snare_hiphop01.ogg", 55, {"fcut": 8000}),
        "clap": ("drums/clap02.ogg", 40, {"pan": -6, "fcut": 7000}),
        "hat": ("drums/hihat_closed05.ogg", 90, {"pan": 12, "fcut": 7500}),
        "open_hat": ("drums/hihat_opened02.ogg", 30, {"pan": 15, "fcut": 7000}),
        "sidestick": ("drums/rim01.ogg", 80, {"pan": -10}),
        "shaker": ("drums/shaker01.ogg", 70, {"pan": -25, "fcut": 7000}),
        "ride": ("drums/ride02.ogg", 40, {"pan": -18, "fcut": 7000}),
        "crash": ("drums/crash01.ogg", 49, {"pan": 20, "fcut": 6000}),
        "reverse_crash": REVERSE_CRASH,
    },
}
KIT_LABELS = {"kick": "Kick", "snare": "Snare", "snare_body": "Snare body", "hat": "Hat", "open_hat": "Open hat",
              "sidestick": "Sidestick", "shaker": "Shaker", "ride": "Ride", "crash": "Crash",
              "reverse_crash": "Reverse crash", "clap": "Clap", "pedal_hat": "Pedal hat", "brush_swirl": "Brush swirl",
              "tom_hi": "Tom hi", "tom_lo": "Tom lo", "conga_hi": "Conga hi", "conga_lo": "Conga lo",
              "conga_mute": "Conga mute", "bongo_hi": "Bongo hi", "bongo_lo": "Bongo lo", "claves": "Claves",
              "tambourine": "Tambourine"}
# kit parts that have been level-measured (the rest use a guessed vol until `measure` runs)
MEASURED_KITS = {"dusty"}

# looping textures, generated on first use into <workingdir>/samples/lofi/ by textures.py
TEXTURES = {
    "vinyl": dict(label="Vinyl crackle", file="lofi/vinyl_crackle.wav", vol=39, measured=True),
    "rain": dict(label="Rain", file="lofi/rain.wav", vol=11, measured=True, note="continuous - much denser than vinyl"),
    "tape": dict(label="Tape hiss", file="lofi/tape_hiss.wav", vol=12, measured=False, note="cassette hiss - city-pop, sleepy"),
}

# track volume of the chopped-sample audio (chops.py normalises it to -14 LUFS before it is placed)
CHOPS_VOL = 60

# Per-stem loudness targets (LUFS, gated) at master 70 %, used by `calibrate` (it corrects for the
# engine's master 50 %). They encode the lofi balance: kick/keys/bass on top, lead a bit under,
# hats/perc/textures well below. The catalog vols above already hit these.
ROLE_TARGET = {
    "keys": -24, "keys_filtered": -22, "bass": -24, "lead": -27, "pad": -34,
    "kick": -23, "snare": -26, "snare_body": -32, "hat": -32, "open_hat": -36, "sidestick": -34,
    "shaker": -39, "ride": -34, "crash": -36, "reverse_crash": -34, "vinyl": -37, "rain": -35,
    "keys2": -28, "clap": -31, "pedal_hat": -38, "brush_swirl": -36, "tom_hi": -32, "tom_lo": -32,
    "conga_hi": -35, "conga_lo": -34, "conga_mute": -37, "bongo_hi": -36, "bongo_lo": -36, "claves": -37,
    "tambourine": -39, "tape": -40, "chops": -24,
}


# ---------------------------------------------------------------- measured values (lofi.py measure)
def _apply_levels():
    import json
    from pathlib import Path
    f = Path(__file__).resolve().parent.parent / "assets" / "levels.json"
    if not f.exists():
        return
    lv = json.loads(f.read_text(encoding="utf-8"))
    for iid, d in lv.get("instruments", {}).items():
        if iid in INSTRUMENTS:
            INSTRUMENTS[iid].update({k: v for k, v in d.items() if k in ("vol", "octave", "measured", "gain", "cents")})
    for kid, parts in lv.get("kits", {}).items():
        if kid in KITS:
            for part, d in parts.items():
                if part in KITS[kid]:
                    d = d if isinstance(d, dict) else dict(vol=d)
                    src, _, extra = KITS[kid][part]
                    KITS[kid][part] = (src, d["vol"], dict(extra, **({"gain": d["gain"]} if "gain" in d else {})))
            MEASURED_KITS.add(kid)
    for t, vol in lv.get("textures", {}).items():
        if t in TEXTURES:
            TEXTURES[t].update(vol=vol, measured=True)


_apply_levels()
