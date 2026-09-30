"""Level + octave measurement for new catalog entries (instruments, kit parts, textures).

Every item is rendered next to an already-measured reference of the same role (same material, same
velocity, no effects), then  vol = ref_vol * 10^((L_ref - L_item + T_item - T_ref) / 20)  with T = the
ROLE_TARGET loudness. Pitched items also get an octave / tuning check. Results go to assets/levels.json,
which catalog.py applies on import - so measured values survive without editing code.
"""
import json
import math
import os
import re
import subprocess
import tempfile
from pathlib import Path

import catalog
import lmmsenv
from lmmsgen import (InstrumentTrack, Note, Pattern, Project, afp, eldata, env, lmms_key, sf2, tripleosc,
                     zyn_from_xiz)

LEVELS = lmmsenv.SKILL_DIR / "assets" / "levels.json"
REF_INST = {"keys": "rhodes", "lead": "flute", "pad": "soft_saw_pad", "bass": "warm_sine"}
REF_PART = {"clap": "snare", "pedal_hat": "hat", "brush_swirl": "hat", "tom_hi": "snare", "tom_lo": "snare",
            "conga_hi": "sidestick", "conga_lo": "sidestick", "conga_mute": "sidestick", "bongo_hi": "sidestick",
            "bongo_lo": "sidestick", "claves": "sidestick", "tambourine": "shaker"}
BPM = 120          # 1 bar = 2 s: bars 0-1 pitch probe, bars 2-3 level material


def _inst_xml(spec_i):
    import engine
    return engine.instrument_xml(spec_i)


def _material(role):
    """(probe MIDI note, [(pos, len, midi, vel)]) in ticks; 192 ticks per bar."""
    if role == "bass":
        probe = 45
        mat = [(384, 90, 36, 96), (480, 90, 36, 90), (576, 90, 43, 96), (672, 90, 41, 90)]
    elif role == "lead":
        probe = 69
        mat = [(384 + i * 48, 44, n, 82) for i, n in enumerate([72, 74, 76, 79, 76, 74, 72, 69])]
    else:   # keys / pad / keys2
        probe = 69
        ch1, ch2 = [60, 64, 67, 71], [62, 65, 69, 72]
        mat = [(384, 180, n, 84) for n in ch1] + [(576, 180, n, 84) for n in ch2]
    return probe, [(0, 330, probe, 84)] + mat


def _track(name, xml, eld, role, fixed=None):
    tr = InstrumentTrack(name, xml, vol=100, eld=eld)
    if fixed is not None or role == "drum":
        notes = [Note(384 + i * 96, 40, lmms_key(fixed if fixed is not None else 69), 90) for i in range(4)]
    else:
        _, mat = _material(role)
        notes = [Note(p, ln, lmms_key(n), v) for p, ln, n, v in mat]
    tr.patterns.append(Pattern("m", 0, 768, notes))
    return tr


def _pitch(path, probe, read_audio):
    """Semitones between the sounding and the written pitch. Looks for spectral peaks at the written
    frequency x 2^k and takes the LOWEST octave whose peak is within 12 dB of the loudest one - robust to
    bright pickups (strong overtones) and FM sub layers, unlike a plain harmonic-product spectrum."""
    import numpy as np
    x, sr = read_audio(path)
    m = x.mean(1)[int(0.1 * sr):int(1.0 * sr)]
    if np.abs(m).max() < 1e-4:
        return None
    n = 1 << 17
    sp = np.abs(np.fft.rfft(m * np.hanning(len(m)), n))
    fr = np.fft.rfftfreq(n, 1 / sr)
    want = 440.0 * 2 ** ((probe - 69) / 12)
    top = sp[(fr > 25) & (fr < 5000)].max()
    best = None
    for k in (-2, -1, 0, 1, 2):
        f = want * 2 ** k
        band = (fr > f * 2 ** (-1.5 / 12)) & (fr < f * 2 ** (1.5 / 12))
        if not band.any():
            continue
        i = np.flatnonzero(band)[np.argmax(sp[band])]
        if sp[i] >= top * 10 ** (-12 / 20):
            a, b, c = sp[i - 1], sp[i], sp[i + 1]
            off = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) else 0.0
            best = 12 * math.log2(fr[i] + off * (fr[1] - fr[0])) - 12 * math.log2(want)
            break
    return best


def _lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", "4.0", "-i", str(path), "-af", "ebur128",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    vals = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
    return float(vals[-1]) if vals else -70.0


def run(lmms_exe, read_audio, inst_ids=None, kit_ids=None, tex_ids=None, reuse_dir=None):
    if inst_ids is None:
        inst_ids = [i for i, d in catalog.INSTRUMENTS.items() if not d.get("measured")]
    if kit_ids is None:
        kit_ids = [k for k in catalog.KITS if k not in catalog.MEASURED_KITS]
    if tex_ids is None:
        tex_ids = [t for t, d in catalog.TEXTURES.items() if not d.get("measured")]
    items = []      # (track name, kind, id, role/part, fixed note)
    for iid in inst_ids:
        items.append((f"i__{iid}", "inst", iid, catalog.INSTRUMENTS[iid]["role"], None))
    for role in {catalog.INSTRUMENTS[i]["role"] for i in inst_ids}:
        items.append((f"r__{REF_INST[role]}", "inst", REF_INST[role], role, None))
    ref_parts = set()
    for kid in kit_ids:
        for part, (src, _, _) in catalog.KITS[kid].items():
            if part == "reverse_crash":
                continue
            fixed = src["note"] if isinstance(src, dict) else None
            items.append((f"k__{kid}__{part}", "part", (kid, part), part, fixed))
            ref_parts.add(REF_PART.get(part, part))
    for part in ref_parts:
        items.append((f"r__dusty__{part}", "part", ("dusty", part), part, None))
    for t in tex_ids:
        items.append((f"t__{t}", "tex", t, t, None))
    if tex_ids:
        items.append(("r__tex__vinyl", "tex", "vinyl", "vinyl", None))

    P = Project(bpm=BPM, master_vol=100)
    import textures as texmod
    wd = lmmsenv.working_dir()
    for name, kind, ref, role, fixed in items:
        if kind == "inst":
            xml, eld = _inst_xml(catalog.INSTRUMENTS[ref])
            P.add(_track(name, xml, eld, role))
        elif kind == "part":
            src, _, extra = catalog.KITS[ref[0]][ref[1]]
            xml = sf2(src["sf2"], src.get("bank", 0), src.get("patch", 0)) if isinstance(src, dict) else afp(src)
            eld = eldata(fcut=extra["fcut"], fres=0.5, fwet=1) if "fcut" in extra else None
            P.add(_track(name, xml, eld, "drum", fixed))
        else:
            t = catalog.TEXTURES[ref]
            texmod.ensure(ref, wd / "samples", t["file"])
            tr = InstrumentTrack(name, afp(t["file"], looped=1), vol=100)
            tr.patterns.append(Pattern("m", 0, 768, [Note(0, 768, lmms_key(69), 100)]))
            P.add(tr)
    P.loop = (0, 768)
    if reuse_dir:                      # re-evaluate an earlier render (same items) without rendering again
        tmp = Path(reuse_dir)
    else:
        tmp = Path(tempfile.mkdtemp(prefix="measure_"))
        P.save(tmp / "m.mmp")
        print(f"rendering {len(items)} tracks (about {len(items) * 3 // 60 + 1} min) ...", flush=True)
        r = subprocess.run([lmms_exe, "rendertracks", str(tmp / "m.mmp"), "-o", str(tmp) + os.sep, "-f", "wav"],
                           capture_output=True, text=True, timeout=7200)
        if r.returncode != 0:
            raise SystemExit(f"LMMS failed:\n{r.stderr[-1500:]}")
    files = {re.sub(r"^\d+_", "", f.stem): f for f in tmp.glob("*.wav")}
    loud = {name: _lufs(files[name]) for name, *_ in items if name in files}

    levels = json.loads(LEVELS.read_text(encoding="utf-8")) if LEVELS.exists() else {}
    li, lk, lt = levels.setdefault("instruments", {}), levels.setdefault("kits", {}), levels.setdefault("textures", {})
    report = []
    T = catalog.ROLE_TARGET
    for name, kind, ref, role, fixed in items:
        if name.startswith("r__") or name not in loud:
            continue
        if kind == "inst":
            d = catalog.INSTRUMENTS[ref]
            rid = REF_INST[role]
            L_ref = loud[f"r__{rid}"]
            vol = catalog.INSTRUMENTS[rid]["vol"] * 10 ** ((L_ref - loud[name]) / 20)
            probe = _material(role)[0]
            semis = _pitch(files[name], probe, read_audio)
            octave = -int(round(semis / 12)) * 12 if semis is not None else 0
            cents = round((semis + octave) * 100) if semis is not None else None
            entry = dict(vol=round(vol), octave=octave, measured=True, cents=cents, lufs=round(loud[name], 1))
            if entry["vol"] > 160 and d["kind"] == "sf2":      # too quiet: use FluidSynth gain instead
                entry["gain"] = round(entry["vol"] / 100, 2)
                entry["vol"] = 100
            li[ref] = entry
            report.append(f"{ref:<16} vol {entry['vol']:>4}{'  gain ' + str(entry.get('gain')) if 'gain' in entry else '':<11}"
                          f" octave {octave:+d}  tuning {cents if cents is not None else '?':>4} cents")
        elif kind == "part":
            kid, part = ref
            rpart = REF_PART.get(part, part)
            L_ref = loud[f"r__dusty__{rpart}"]
            ref_vol = catalog.KITS["dusty"][rpart][1]
            vol = ref_vol * 10 ** ((L_ref - loud[name] + T[part] - T[rpart]) / 20)
            src = catalog.KITS[kid][part][0]
            if vol > 160:                     # too quiet: SoundFont gain / AudioFileProcessor amp instead
                lk.setdefault(kid, {})[part] = dict(vol=100, gain=round(min(5.0, vol / 100), 2))
            else:
                lk.setdefault(kid, {})[part] = dict(vol=max(1, min(200, round(vol))))
            e = lk[kid][part]
            report.append(f"{kid + '/' + part:<22} vol {e['vol']:>4}" + (f"  gain {e['gain']}" if "gain" in e else "") +
                          ("   (CLAMPED - too quiet)" if vol > 200 and "gain" not in e else ""))
        else:
            vol = catalog.TEXTURES["vinyl"]["vol"] * 10 ** ((loud["r__tex__vinyl"] - loud[name] + T[ref] - T["vinyl"]) / 20)
            lt[ref] = round(vol)
            report.append(f"texture {ref:<14} vol {lt[ref]:>4}")
    LEVELS.write_text(json.dumps(levels, indent=1), encoding="utf-8")
    return report
