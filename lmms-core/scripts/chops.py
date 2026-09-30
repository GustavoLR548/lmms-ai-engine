"""Chopped-sample keys ("mpc" pattern): the J Dilla / MPC sound without borrowing anyone's record.

1. record: render the song's chords once, sustained, on the palette's `sample` instrument (default: the keys
   instrument) - one LMMS render of a one-track project.
2. age it like an old record: band-limit, tape saturation, 12-bit / 22 kHz grit, slight wobble.
3. chop: every hit the engine scheduled (Song.chops) re-triggers the ATTACK of the chord sounding at that
   moment (optionally reversed), with short fades - so the harmony stays exactly the song's harmony.

The result is one wav placed on a single "Chops" track. It is cached: the record is only re-rendered when
the chords, tempo or instrument change.
"""
import hashlib
import json
import os
import subprocess
from pathlib import Path

import catalog
import lmmsenv
from lmmsgen import TPB, InstrumentTrack, Note, Pattern, Project, afp, fx_eq, lmms_key, sf2, tripleosc, zyn_from_xiz

SR = 44100


def _record_project(song, inst_id):
    spec_i = dict(catalog.INSTRUMENTS[inst_id], **song.spec.get("instruments", {}).get(inst_id, {}))
    import engine
    xml, _ = engine.instrument_xml(spec_i)
    P = Project(bpm=song.bpm, master_vol=100)
    tr = InstrumentTrack("record", xml, vol=spec_i["vol"], fxch=1)
    notes = []
    shift = spec_i.get("octave") or 0
    for seg in song.segments:
        for i, n in enumerate(seg["voicing"]):
            notes.append(Note(seg["start"] + 2 + i * 3, seg["end"] - seg["start"] - 4, lmms_key(n + shift), 92 - i * 3))
    tr.patterns.append(Pattern("record", 0, -(-song.end // TPB) * TPB + TPB, notes))
    P.add(tr)
    P.channel(1, "Record", 1.0, [fx_eq(hp=100, lp=9000)])
    P.loop = (0, song.end + TPB)
    return P


def _age(x, rng):
    import numpy as np
    from scipy import signal
    b, a = signal.butter(2, [140 / (SR / 2), 4800 / (SR / 2)], "band")
    y = signal.lfilter(b, a, x, axis=0)
    y = y / (np.abs(y).max() + 1e-9)
    y = np.tanh(2.2 * y) / np.tanh(2.2)                        # tape saturation
    held = np.repeat(y[::2], 2, axis=0)[:len(y)]               # 22 kHz sample-and-hold grit
    y = 0.6 * held + 0.4 * y
    y = np.round(y * 2048) / 2048                              # 12-bit
    b, a = signal.butter(2, 6000 / (SR / 2))
    y = signal.lfilter(b, a, y, axis=0)
    t = np.arange(len(y)) / SR                                 # slow record wobble (+/- ~8 cents)
    d = 0.0009 * np.sin(2 * np.pi * 0.55 * t) * SR
    idx = np.clip(np.arange(len(y)) + d, 0, len(y) - 1)
    i0 = idx.astype(int)
    fr = (idx - i0)[:, None]
    y = y[i0] * (1 - fr) + y[np.minimum(i0 + 1, len(y) - 1)] * fr
    return y


def _chop(rec, song):
    import numpy as np
    out = np.zeros((int(song.seconds(song.end + TPB) * SR), 2))
    fin, fout = int(0.003 * SR), int(0.018 * SR)
    for c in song.chops:
        s = int(song.seconds(c["src"]) * SR)
        n = int(song.seconds(c["len"]) * SR)
        piece = rec[s:s + n].copy()
        if len(piece) < fin + fout + 8:
            continue
        if c["rev"]:
            piece = piece[::-1]
        env = np.ones(len(piece))
        env[:fin] = np.linspace(0, 1, fin)
        env[-fout:] = np.linspace(1, 0, fout)
        piece *= (env * (c["vel"] / 100) ** 1.5)[:, None]
        d = int(song.seconds(c["start"]) * SR)
        e = min(len(out), d + len(piece))
        out[d:e] += piece[:e - d]
    return out


def _write(path, x):
    import numpy as np
    import wave
    x = x / (np.abs(x).max() + 1e-9) * 0.7
    w = wave.open(str(path), "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes())
    w.close()


def render(song, out_dir, lmms_exe, read_audio):
    """Create <out_dir>/<slug>_chops.wav for song.chops; returns its path (or None if the song has no chops)."""
    import random
    if not song.chops:
        return None
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = song.spec.get("slug", "song")
    inst_id = song.palette.get("sample") or song.palette.get("keys", "rhodes")
    key = hashlib.sha1(json.dumps([inst_id, song.bpm, [(s["start"], s["end"], s["voicing"]) for s in song.segments]],
                                  sort_keys=True).encode()).hexdigest()[:16]
    rec_wav = out_dir / f"{slug}_record.wav"
    stamp = out_dir / f"{slug}_record.key"
    if not (rec_wav.exists() and stamp.exists() and stamp.read_text() == key):
        mmp = out_dir / f"{slug}_record.mmp"
        _record_project(song, inst_id).save(mmp)
        r = subprocess.run([lmms_exe, "render", str(mmp), "-o", str(rec_wav), "-f", "wav"], capture_output=True, text=True,
                           timeout=1800)
        if r.returncode != 0:
            raise SystemExit(f"LMMS failed rendering the chop record:\n{r.stderr[-1500:]}")
        stamp.write_text(key)
    rec, _ = read_audio(rec_wav)
    aged = _age(rec.astype("float64"), random.Random(song.seed))
    chopped = _chop(aged, song)
    path = out_dir / f"{slug}_chops.wav"
    _write(path, chopped)
    return path
