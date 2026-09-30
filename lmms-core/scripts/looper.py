"""Seamless game-music loops: render, cut, master, encode, verify.

How it stays seamless: the song is rendered as intro + loop body x3 (the SAME notes each pass), so the middle
pass already contains the reverb / echo tails of the pass before it - exactly what the player hears when the
loop wraps. The loop file is that middle pass. Passes are the same music but not the same samples (LMMS
reverbs modulate randomly, note timing drifts by a few samples), so the file's last 30 ms are crossfaded into
the last 30 ms of the FIRST pass - the audio that really precedes the middle pass's first sample. The wrap is
then sample-continuous and the downbeat the loop starts on is untouched (a crossfade at the start would blend
two slightly different downbeats). The intro file ends the same way, so intro -> loop is continuous too.
Mastering (gain + peak limiter) runs on the continuous render before cutting, so it cannot click at the seam.

Outputs next to song.json:
  <slug>_loop.ogg        the loop body - set the player / engine to loop the whole file
  <slug>_intro.ogg       (intro songs) play once, then start the loop file
  <slug>_full.ogg        (intro songs) intro + loop in one file, tagged LOOPSTART / LOOPLENGTH (samples)
  <slug>_loop.json       loop points in seconds and samples, loudness, seam check, engine notes
  <slug>_preview_vN.mp3  intro + the loop played twice + a fade: listen for the seam
"""
import copy
import json
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from lmmsgen import TPB

SR = 44100
XFADE = 0.03


def extended_song(song, passes=3):
    """A copy of the song whose loop body repeats `passes` times (same notes, same humanisation)."""
    ext = copy.copy(song)
    L = song.end - song.loop_start
    body = [e for e in song.events if e["start"] >= song.loop_start and not e["track"].startswith("tex:")]
    events = [dict(e) for e in song.events if not e["track"].startswith("tex:")]
    for k in range(1, passes):
        events += [dict(e, start=e["start"] + k * L) for e in body]
    ext.end = song.end + (passes - 1) * L
    events += [dict(e, len=ext.end + 2 * TPB) for e in song.events if e["track"].startswith("tex:")]
    ext.events = events
    ext.warnings = list(song.warnings)
    return ext


def _limit(x, ceiling_db=-1.5, look_s=0.005):
    """Peak limiter with lookahead (gain never lets a sample exceed the ceiling)."""
    import numpy as np
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    thr = 10 ** (ceiling_db / 20)
    peak = np.abs(x).max(axis=1)
    need = np.minimum(1.0, thr / np.maximum(peak, 1e-9))
    la = max(1, int(look_s * SR))
    g = minimum_filter1d(need, size=2 * la + 1)
    g = uniform_filter1d(g, size=la)
    return x * g[:, None]


def _encode(x, path, fmt, tags=None, ffmpeg="ffmpeg"):
    import numpy as np
    raw = np.ascontiguousarray(x.astype(np.float32)).tobytes()
    codec = ["-c:a", "libvorbis", "-q:a", "6"] if fmt == "ogg" else ["-c:a", "libmp3lame", "-b:a", "320k"]
    meta = sum((["-metadata", f"{k}={v}"] for k, v in (tags or {}).items()), [])
    subprocess.run([ffmpeg, "-loglevel", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-"] + codec +
                   meta + [str(path)], input=raw, check=True)


def loudness(path, ffmpeg="ffmpeg"):
    r = subprocess.run([ffmpeg, "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1])


def _write_wav(x, path):
    import numpy as np
    import wave
    w = wave.open(str(path), "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    w.close()


BEFORE, AFTER = int(0.2 * SR), int(0.1 * SR)      # span around the wrap point that seam_check looks at


def seam_check(x, expected_len=None, ref=None):
    """How the file sounds where it wraps (end -> start). x: float (n, 2) of the decoded loop file.
    click_db: high-frequency energy in the 5 ms around the seam vs the loop's typical level (a click = a spike);
    jump: sample step at the wrap / the loop's 99.9th-percentile step (< 1 = no discontinuity);
    level_db: loudness change across the seam (last 100 ms vs first 100 ms).
    ref: what continuous playback sounds like at the same musical point (BEFORE samples before the wrap, AFTER
    after it). A downbeat is naturally louder and brighter than the end of the bar before it, so with a ref the
    click and level numbers are judged against the ref's (click_vs_ref_db, level_vs_ref_db). Without a ref (any
    file via `loopcheck`) the absolute numbers are judged with looser limits."""
    import numpy as np
    from scipy import signal
    m = x.mean(1)
    b, a = signal.butter(4, 3000 / (SR / 2), "high")
    win = int(0.005 * SR)
    hp_all = signal.lfilter(b, a, np.concatenate([m[-BEFORE:], m]))[BEFORE:]
    frames = hp_all[:len(hp_all) // win * win].reshape(-1, win)
    e_typ = float(np.median(np.mean(frames ** 2, axis=1))) + 1e-12

    def click_db(wrap):                      # wrap: BEFORE samples, then AFTER samples, mono
        hp = signal.lfilter(b, a, wrap)
        return 10 * math.log10(float(np.mean(hp[BEFORE - win // 2:BEFORE + win // 2] ** 2)) / e_typ + 1e-12)

    q = int(0.1 * SR)
    rms = lambda s: 20 * math.log10(float(np.sqrt(np.mean(s ** 2))) + 1e-9)
    wrap = np.concatenate([x[-BEFORE:], x[:AFTER]])
    steps = np.abs(np.diff(x, axis=0)).max(axis=1)
    jump = float(np.abs(x[0] - x[-1]).max() / (np.percentile(steps, 99.9) + 1e-9))
    out = dict(click_db=round(click_db(wrap.mean(1)), 1), jump=round(jump, 2),
               level_db=round(rms(x[-q:]) - rms(x[:q]), 1), samples=len(x))
    if expected_len:
        out["length_error_ms"] = round((len(x) - expected_len) / SR * 1000, 2)
    ok = out["jump"] < 1.0 and abs(out.get("length_error_ms", 0)) < 5
    if ref is not None:
        out["click_vs_ref_db"] = round(out["click_db"] - click_db(ref.mean(1)), 1)
        out["level_vs_ref_db"] = round(out["level_db"] - (rms(ref[BEFORE - q:BEFORE]) - rms(ref[BEFORE:BEFORE + q])), 1)
        ok = ok and out["click_vs_ref_db"] < 3 and abs(out["level_vs_ref_db"]) < 1.5
    else:
        ok = ok and out["click_db"] < 6 and abs(out["level_db"]) < 6
    out["seamless"] = ok
    return out


def _usage(loop, intro, full, I):
    """How to loop these files in common engines (file names as the game sees them)."""
    return {
        "any engine": f"loop {loop} as a whole" + (f"; play {intro} once first, then start the loop file" if I else ""),
        "Godot": f"import {loop} with Loop on" + (f"; or import {full} with Loop on and loop_offset = {I / SR:.4f} s"
                                                  if I else ""),
        "Unity": f"AudioSource.loop = true on {loop}" + (
            f"; schedule it with PlayScheduled to start right when {intro} ends" if I else ""),
        "RPG Maker MV / MZ": "reads the LOOPSTART / LOOPLENGTH tags (samples) automatically" + (
            f" - use {full}" if I else ""),
        "GameMaker": f"audio_play_sound(<{loop}>, 0, true)" + (
            f"; play {intro} first and start the loop when it ends" if I else "")}


def make(song, spec, p, lmms_exe, read_audio, target_lufs=-16.0, to=None, ffmpeg="ffmpeg"):
    import numpy as np
    slug = p["mmp"].stem
    renders = p["renders"]
    renders.mkdir(parents=True, exist_ok=True)
    # 1. render intro + body x3
    ext = extended_song(song)
    mmp = renders / f"{slug}_looprender.mmp"
    ext.build_project().save(mmp)
    wav = renders / f"{slug}_looprender.wav"
    r = subprocess.run([lmms_exe, "render", str(mmp), "-o", str(wav), "-f", "wav", "-a"], capture_output=True, text=True,
                       timeout=3600)
    if r.returncode != 0:
        raise SystemExit(f"LMMS failed:\n{r.stderr[-1500:]}")
    A, sr = read_audio(wav)
    A = A.astype(np.float64)
    I = round(song.seconds(song.loop_start) * SR)
    L = round(song.seconds(song.end - song.loop_start) * SR)
    n = int(XFADE * SR)
    if len(A) < I + 2 * L + n:
        A = np.concatenate([A, np.zeros((I + 2 * L + n - len(A), 2))])
    # 2. master on the continuous render: loudness of the loop body -> target, then peak limit
    tmp = Path(tempfile.mkdtemp(prefix="loop_"))
    _write_wav(A[I + L:I + 2 * L], tmp / "body.wav")
    lufs, _ = loudness(tmp / "body.wav", ffmpeg)
    A = _limit(A * 10 ** ((target_lufs - lufs) / 20), ceiling_db=-2.0)     # true peak after encoding stays <= -1
    # 3. cut: loop = middle pass, its end crossfaded into the audio that really precedes the middle pass
    w = np.linspace(0, 1, n)[:, None]
    loop = A[I + L:I + 2 * L].copy()
    loop[-n:] = (1 - w) * A[I + 2 * L - n:I + 2 * L] + w * A[I + L - n:I + L]
    intro = A[:I].copy()
    if I >= n:
        intro[-n:] = (1 - w) * A[I - n:I] + w * A[I + L - n:I + L]
    # 4. encode
    d = p["dir"]
    files = {"loop": d / f"{slug}_loop.ogg"}
    _encode(loop, files["loop"], "ogg", {"LOOPSTART": 0, "LOOPLENGTH": L}, ffmpeg)
    if I:
        files["intro"] = d / f"{slug}_intro.ogg"
        files["full"] = d / f"{slug}_full.ogg"
        _encode(intro, files["intro"], "ogg", None, ffmpeg)
        _encode(np.concatenate([intro, loop]), files["full"], "ogg", {"LOOPSTART": I, "LOOPLENGTH": L}, ffmpeg)
    k = 1 + max([int(m.group(1)) for f in d.glob(f"{slug}_preview_v*.mp3")
                 if (m := re.search(r"_v(\d+)\.mp3$", f.name))] or [0])
    tail = loop[:min(len(loop), 6 * SR)].copy()
    tail *= np.linspace(1, 0, len(tail))[:, None]
    files["preview"] = d / f"{slug}_preview_v{k}.mp3"
    _encode(np.concatenate([intro, loop, loop, tail]), files["preview"], "mp3", None, ffmpeg)
    # 5. verify the actual deliverable (decoded OGG)
    x, _ = read_audio(files["loop"])
    check = seam_check(x.astype(np.float64), expected_len=L, ref=A[I + L - BEFORE:I + L + AFTER])
    lufs2, tp2 = loudness(files["loop"], ffmpeg)
    info = dict(title=song.spec.get("title"), style=song.style_id, bpm=song.bpm, sample_rate=SR,
                intro_seconds=round(I / SR, 4), intro_samples=I,
                loop_start_seconds=round(I / SR, 4), loop_start_samples=I,
                loop_length_seconds=round(L / SR, 4), loop_length_samples=L,
                loop_bars=song.nbars - song.loop_start_bar,
                lufs=round(lufs2, 1), true_peak_dbfs=round(tp2, 1), seam=check,
                files={k2: v.name for k2, v in files.items()},
                how_to_use=_usage(files["loop"].name, files.get("intro") and files["intro"].name,
                                  files.get("full") and files["full"].name, I),
                source=str(p["mmp"]))
    (d / f"{slug}_loop.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    if to:
        # the game copy: the full file (intro songs) or the loop under the requested name, and a loop json that
        # names THOSE files
        dest = Path(to)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(files["full"] if I else files["loop"], dest)
        game = {"full" if I else "loop": dest.name}
        if I:
            game["intro"] = dest.stem + "_intro.ogg"
            game["loop"] = dest.stem + "_loop.ogg"
            shutil.copyfile(files["intro"], dest.with_name(game["intro"]))
            shutil.copyfile(files["loop"], dest.with_name(game["loop"]))
        exported = dict(info, files=game, how_to_use=_usage(game["loop"], game.get("intro"), game.get("full"), I))
        dest.with_suffix(".loop.json").write_text(json.dumps(exported, indent=2), encoding="utf-8")
        info["exported_to"] = str(dest)
    shutil.rmtree(tmp, ignore_errors=True)
    return info, wav
