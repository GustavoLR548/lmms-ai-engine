#!/usr/bin/env python3
"""lmms-core command line - run through a genre skill's entry script (e.g. lmms-hiphop/scripts/lofi.py),
which loads its genre pack first. Without a pack only `doctor`, `setup`, `measure` and `history` make sense.

  doctor                      check LMMS / ffmpeg / python deps / SoundFonts
  setup                       create lmms-core/.venv with numpy + scipy (one time)
  new <slug> [--template T]   start a project folder + song.json from the genre skill's assets/examples/T.json
  build <song.json>           song.json -> <slug>.mmp, print arrangement + harmony problems
  make <song.json>            build + render + level report + versioned mp3   (the usual command)
                              looping songs ("loop" in song.json): seamless <slug>_loop.ogg (+ intro/full),
                              loop json, preview mp3, seam check; --to <file.ogg> copies it into a game
  loopcheck <file> [--bars N --bpm B]   seam / length / loudness check of a loop file
  render <song.json>          build + render renders/<slug>_mix.wav + level report
  master <song.json>          renders/<slug>_mix.wav -> <slug>_vN.mp3 at --lufs (default -16)
  stems <song.json>           render every track separately (slow: ~20-40 s per track)
  calibrate <song.json>       read stems, write per-track gain corrections into song.json mix.gains
  audition <instrument-id>    render a test note: octave/tuning check + suggested catalog volume
  measure [--instruments ..] [--kits ..]   level + octave of every unmeasured instrument / kit -> assets/levels.json
  styles                      list the genre pack's styles and their pattern vocabulary
  history [-n 10]             recent songs and what they used (variety memory)
  textures [--force]          (re)generate texture samples (vinyl, rain)
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lmmsenv  # noqa: E402

PACK = None        # the genre pack module the entry script loaded (EXAMPLES, PROG)


def reexec_in_venv(cmd):
    """Re-run the ENTRY script (the genre skill's, which loads its pack) inside lmms-core/.venv."""
    if cmd in ("doctor", "setup", "where") or lmmsenv.have_numpy():
        return
    vp = lmmsenv.venv_python()
    if vp.exists() and Path(sys.executable).resolve() != vp.resolve():
        sys.exit(subprocess.call([str(vp), str(Path(sys.argv[0]).resolve())] + sys.argv[1:]))
    sys.exit(f"numpy/scipy missing. Run once:  python {sys.argv[0]} setup")


# ------------------------------------------------------------------ helpers
def load_spec(path):
    path = Path(path).resolve()
    spec = json.loads(path.read_text(encoding="utf-8"))
    slug = spec.get("slug") or path.parent.name
    return path, spec, slug


def paths(spec_path, slug):
    d = spec_path.parent
    return dict(dir=d, mmp=d / f"{slug}.mmp", renders=d / "renders", mix=d / "renders" / f"{slug}_mix.wav",
                stems=d / "renders" / "stems")


def lmms():
    exe = lmmsenv.lmms_exe()
    if not exe:
        sys.exit("LMMS not found - install LMMS 1.2.x or set LMMS_EXE")
    return exe


def run_lmms(args, timeout=3600):
    r = subprocess.run([lmms()] + args, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        sys.exit(f"LMMS failed ({r.returncode}):\n{r.stderr[-2000:]}")


def ffmpeg_loudness(path):
    r = subprocess.run([lmmsenv.ffmpeg() or "ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
    tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1])
    return lufs, tp


def read_audio(path, sr=44100):
    import numpy as np
    raw = subprocess.run([lmmsenv.ffmpeg() or "ffmpeg", "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(sr), "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2), sr


def song_for(spec_path, spec):
    import engine
    song = engine.Song(spec, spec_path)
    song.generate()
    return song


# ------------------------------------------------------------------ commands
def cmd_build(a):
    spec_path, spec, slug = load_spec(a.spec)
    p = paths(spec_path, slug)
    try:
        song = song_for(spec_path, spec)
    except ValueError as e:
        sys.exit(f"spec error: {e}")
    print(song.summary())
    if song.problems:
        print(f"\nHARMONY/SPEC PROBLEMS ({len(song.problems)}):")
        for x in song.problems:
            print("  -", x)
        if not a.force:
            print("\nNot written. Fix the notes/chords above (or pass --force to write anyway).")
            sys.exit(2)
    chops_file = None
    if song.chops:
        import chops
        print("\nrendering the chopped-sample record ...", flush=True)
        chops_file = chops.render(song, p["renders"], lmms(), read_audio)
    project = song.build_project(chops_file)
    for w in dict.fromkeys(song.warnings):
        print("  warning:", w)
    project.save(p["mmp"])
    print(f"\nwrote {p['mmp']}")
    import history
    for line in history.record_and_compare(song, slug):
        print(line)
    return song, p


def cmd_render(a):
    song, p = cmd_build(a)
    p["renders"].mkdir(parents=True, exist_ok=True)
    print("rendering with LMMS ...", flush=True)
    run_lmms(["render", str(p["mmp"]), "-o", str(p["mix"]), "-f", "wav", "-a"])
    report(p["mix"], song)
    return song, p


def report(wav, song):
    import numpy as np
    x, sr = read_audio(wav)
    lufs, tp = ffmpeg_loudness(wav)
    print(f"\nmix: {lufs:.1f} LUFS integrated, true peak {tp:.1f} dBFS, {len(x) / sr:.1f} s")
    print(f"{'section':<14}{'start':>6}{'rms dB':>9}{'peak dBFS':>11}")
    prev, prev_name, prev_move = None, None, None
    for s in song.sections:
        a_ = int(song.seconds(s["start"]) * sr)
        b_ = int(song.seconds(s["start"] + int(s["bars"]) * 192) * sr)
        seg = x[a_:b_]
        if len(seg) == 0:
            continue
        rms = 20 * math.log10(float(np.sqrt(np.mean(seg ** 2))) + 1e-9)
        pk = 20 * math.log10(float(np.abs(seg).max()) + 1e-9)
        flag = "  <- clipping risk" if pk > -0.3 else ""
        moved = any(k.endswith(".level") for k in (s.get("move") or {})) or \
            any(k.endswith(".level") for k in (prev_move or {}))          # fades / swells are meant to jump
        quiet_ok = moved or re.search(r"intro|outro|bridge|break|drop|rise|build|fade", s["name"] + " " +
                                      (prev_name or ""), re.I)
        if prev is not None and abs(rms - prev) > 7 and not quiet_ok:
            flag += "  <- big level jump"
        print(f"{s['name']:<14}{song.fmt(song.seconds(s['start'])):>6}{rms:>9.1f}{pk:>11.1f}{flag}")
        prev, prev_name, prev_move = rms, s["name"], s.get("move")
    if tp > -0.5:
        print("note: mix peaks near 0 dBFS - `master` will limit it, but consider lowering busy tracks via mix.gains")


def cmd_master(a, song=None, p=None):
    if song is None:
        spec_path, spec, slug = load_spec(a.spec)
        p = paths(spec_path, slug)
        song = song_for(spec_path, spec)
    if not p["mix"].exists():
        sys.exit(f"no render at {p['mix']} - run `make` or `render` first")
    lufs, _ = ffmpeg_loudness(p["mix"])
    gain = a.lufs - lufs
    end = song.seconds(song.end)
    tail = 4.0
    slug = p["mmp"].stem
    n = 1 + max([int(m.group(1)) for f in p["dir"].glob(f"{slug}_v*.mp3") if (m := re.search(r"_v(\d+)\.mp3$", f.name))] or [0])
    out = p["dir"] / f"{slug}_v{n}.mp3"
    af = f"volume={gain:.2f}dB,alimiter=limit=0.891:attack=5:release=80:level=disabled,afade=t=out:st={end:.2f}:d={tail}"
    subprocess.run([lmmsenv.ffmpeg() or "ffmpeg", "-loglevel", "error", "-y", "-i", str(p["mix"]), "-af", af, "-t", f"{end + tail:.2f}",
                    "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "320k", str(out)], check=True)
    l2, tp2 = ffmpeg_loudness(out)
    print(f"\nmastered -> {out}\n  {l2:.1f} LUFS, true peak {tp2:.1f} dBFS, {song.fmt(end + tail)}")
    return out


def cmd_make(a):
    spec_path, spec, slug = load_spec(a.spec)
    if spec.get("loop"):
        return cmd_make_loop(a)
    song, p = cmd_render(a)
    return cmd_master(a, song, p)


def cmd_make_loop(a):
    """Looping song (spec "loop"): build, render intro + loop x3, cut a seamless loop, master, encode OGG."""
    import looper
    song, p = cmd_build(a)
    print("rendering the loop (intro + 3 passes) with LMMS ...", flush=True)
    info, wav = looper.make(song, None, p, lmms(), read_audio, target_lufs=a.lufs, to=a.to,
                            ffmpeg=lmmsenv.ffmpeg() or "ffmpeg")
    report(wav, song)
    s = info["seam"]
    print(f"\nloop: {info['loop_bars']} bars = {info['loop_length_seconds']:.2f} s"
          + (f", intro {info['intro_seconds']:.2f} s" if info["intro_samples"] else "")
          + f"  |  {info['lufs']} LUFS, true peak {info['true_peak_dbfs']} dBFS")
    print(f"seam: click {s['click_vs_ref_db']:+.1f} dB and level {s['level_vs_ref_db']:+.1f} dB vs continuous "
          f"playback, jump {s['jump']}, length error {s.get('length_error_ms', 0)} ms -> "
          f"{'SEAMLESS' if s['seamless'] else 'CHECK THE SEAM'}")
    for k, v in info["files"].items():
        print(f"  {k:<8}{p['dir'] / v}")
    if info.get("exported_to"):
        print(f"  copied to {info['exported_to']}")
    return info


def cmd_loopcheck(a):
    """Seam / length / loudness check of any loop file (ogg, wav, mp3)."""
    import looper
    x, sr = read_audio(a.file)
    exp = round(a.bars * 240 / a.bpm * 44100) if (a.bars and a.bpm) else None
    res = looper.seam_check(x.astype("float64"), expected_len=exp)
    lufs, tp = looper.loudness(a.file, lmmsenv.ffmpeg() or "ffmpeg")
    res.update(lufs=round(lufs, 1), true_peak_dbfs=round(tp, 1), seconds=round(len(x) / 44100, 3))
    print(json.dumps(res, indent=2))


def cmd_stems(a):
    song, p = cmd_build(a)
    p["stems"].mkdir(parents=True, exist_ok=True)
    for f in p["stems"].glob("*.wav"):
        f.unlink()
    print("rendering one file per track (slow) ...", flush=True)
    run_lmms(["rendertracks", str(p["mmp"]), "-o", str(p["stems"]) + os.sep, "-f", "wav"], timeout=7200)
    print("stems in", p["stems"])


def cmd_calibrate(a):
    import catalog
    spec_path, spec, slug = load_spec(a.spec)
    p = paths(spec_path, slug)
    song = song_for(spec_path, spec)
    chops_file = p["renders"] / f"{slug}_chops.wav"
    song.build_project(chops_file if chops_file.exists() else None)
    roles = song.label_roles
    gains = spec.setdefault("mix", {}).setdefault("gains", {})
    master_offset = 20 * math.log10(50 / 70)          # targets were measured at master 70 %, projects use 50 %
    for f in sorted(p["stems"].glob("*.wav")):
        label = re.sub(r"^\d+_", "", f.stem)
        role = roles.get(label)
        if role not in catalog.ROLE_TARGET:
            print(f"skip {label} (no target)")
            continue
        lufs, tp = ffmpeg_loudness(f)
        target = catalog.ROLE_TARGET[role] + master_offset
        if role == "pad":                     # the style's deliberate pad boost (electronic) is part of the target
            target += 20 * math.log10(song.tone.get("pad_level", 1.0))
        delta = target - lufs
        if abs(delta) < 0.7:
            print(f"{label:<22}{lufs:7.1f} LUFS  ok")
            continue
        gains[label] = round(gains.get(label, 0) + delta, 1)
        print(f"{label:<22}{lufs:7.1f} LUFS  target {target:.1f}  -> gain {gains[label]:+.1f} dB")
    spec_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print("updated mix.gains in", spec_path)


def cmd_audition(a):
    import numpy as np
    import catalog
    import engine
    from lmmsgen import InstrumentTrack, Note, Pattern, Project, eldata, env, lmms_key, tripleosc, zyn_from_xiz
    iid = a.instrument
    inst = catalog.INSTRUMENTS[iid]
    ref_id = {"keys": "rhodes", "lead": "flute", "pad": "soft_saw_pad", "bass": "warm_sine"}[inst["role"]]
    data = lmmsenv.data_dir()
    tpl = str(lmmsenv.SKILL_DIR / "assets" / "zyn_template.xml")
    P = Project(bpm=90, master_vol=100)
    note = 45 if inst["role"] == "bass" else 69
    for i, key in enumerate([iid, ref_id] if ref_id != iid else [iid]):
        d = catalog.INSTRUMENTS[key]
        if d["kind"] == "zyn":
            tr = InstrumentTrack(key, zyn_from_xiz(str(data / "presets" / catalog.ZYN / d["preset"]), tpl), vol=100)
        else:
            tr = InstrumentTrack(key, tripleosc(d["oscs"]), vol=100, eld=eldata(fcut=d.get("fcut", 14000), fwet=1, vol=env(**d["env"])))
        tr.patterns.append(Pattern("test", 0, 384, [Note(0, 330, lmms_key(note), 100)]))
        P.add(tr)
    P.loop = (0, 384)
    tmp = Path(tempfile.mkdtemp(prefix="audition_"))
    P.save(tmp / "a.mmp")
    run_lmms(["rendertracks", str(tmp / "a.mmp"), "-o", str(tmp) + os.sep, "-f", "wav"])
    res = {}
    for f in tmp.glob("*.wav"):
        key = re.sub(r"^\d+_", "", f.stem)
        x, sr = read_audio(f)
        m = x.mean(1)[int(0.3 * sr):int(1.8 * sr)]
        spec = np.abs(np.fft.rfft(m * np.hanning(len(m)), 8 * len(m)))
        fr = np.fft.rfftfreq(8 * len(m), 1 / sr)
        hps = spec.copy()
        for h in (2, 3, 4):
            dec = spec[::h]
            hps[:len(dec)] *= dec
        band = (fr > 40) & (fr < 2000)
        f0 = fr[band][np.argmax(hps[band])]
        want = 440.0 * 2 ** ((note - 69) / 12)
        semis = 12 * math.log2(f0 / want)
        res[key] = (f0, semis, ffmpeg_loudness(f)[0])
    f0, semis, lufs = res[iid]
    shift = -int(round(semis / 12)) * 12
    cents = (semis + shift) * 100
    print(f"{iid}: fundamental {f0:.1f} Hz for written {engine.NAMES[note % 12]} -> octave shift {shift:+d}, tuning {cents:+.0f} cents")
    if ref_id in res and ref_id != iid:
        rl = res[ref_id][2]
        vol = catalog.INSTRUMENTS[ref_id]["vol"] * 10 ** ((rl - lufs) / 20)
        print(f"level {lufs:.1f} LUFS vs reference {ref_id} {rl:.1f} LUFS -> suggested vol ~{vol:.0f}")
    else:
        vol = inst["vol"]
    if abs(cents) > 10:
        print("warning: preset is noticeably out of tune; prefer another preset")
    print(f"\ncatalog entry: set  octave={shift}, vol={vol:.0f}, measured=True  for {iid!r} in scripts/catalog.py")


def cmd_textures(a):
    import catalog
    import textures
    wd = lmmsenv.working_dir()
    for name, t in catalog.TEXTURES.items():
        f = wd / "samples" / t["file"]
        if a.force and f.exists():
            f.unlink()
        textures.ensure(name, wd / "samples", t["file"])
    print("textures in", wd / "samples" / "lofi")


def cmd_new(a):
    proj = lmmsenv.working_dir() / "projects" / a.slug
    proj.mkdir(parents=True, exist_ok=True)
    spec_file = proj / "song.json"
    if spec_file.exists() and not a.force:
        sys.exit(f"{spec_file} exists (use --force to overwrite)")
    examples = getattr(PACK, "EXAMPLES", None)
    tpl = examples / f"{a.template}.json" if examples else None
    if not tpl or not tpl.exists():
        have = sorted(p.stem for p in examples.glob("*.json")) if examples else []
        sys.exit(f"template {a.template!r} not found (have: {', '.join(have) or 'none - no genre pack loaded'})")
    spec = json.loads(tpl.read_text(encoding="utf-8"))
    spec["slug"] = a.slug
    spec["title"] = a.slug.replace("-", " ").title()
    spec_file.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print(spec_file)


def cmd_measure(a):
    import measure
    rep = measure.run(lmms(), read_audio, inst_ids=a.instruments or None,
                      kit_ids=a.kits or ([] if a.instruments else None), tex_ids=[] if (a.instruments or a.kits) else None)
    print("\n".join(rep))
    print(f"\nsaved to {measure.LEVELS} (applied automatically by catalog.py)")


def cmd_history(a):
    import history
    print(history.show(a.n))


def cmd_styles(a):
    import registry
    if not registry.STYLES:
        sys.exit("no genre pack loaded - run this through a genre skill's script (e.g. lmms-hiphop/scripts/lofi.py)")
    for sid, s in registry.STYLES.items():
        pal = s["palette"]
        print(f"{sid:<8} {s['title']} ({s['bpm'][0]}-{s['bpm'][1]} BPM, swing {s['swing']})\n         {s['about']}")
        print(f"         palette: keys {pal.get('keys')}{', keys2 ' + pal['keys2'] if pal.get('keys2') else ''}, "
              f"bass {pal.get('bass')}, pad {pal.get('pad')}, kit {pal.get('kit')}; leads {', '.join(s['leads'])}")
        print(f"         keys: {' '.join(s['keys'])}" + (f" | keys2: {' '.join(s['keys2'])}" if s.get('keys2') else ""))
        print(f"         bass: {' '.join(s['bass'])} | drums: {' '.join(s['drums'])}\n")


def cmd_setup(a):
    vp = lmmsenv.venv_python()
    if not vp.exists():
        subprocess.run([sys.executable, "-m", "venv", str(lmmsenv.SKILL_DIR / ".venv")], check=True)
    subprocess.run([str(vp), "-m", "pip", "install", "-q", "numpy", "scipy"], check=True)
    print("ready:", vp)


def main(pack=None):
    """pack: the genre pack module (already imported, so its styles/patterns are registered)."""
    global PACK
    PACK = pack
    ap = argparse.ArgumentParser(prog=getattr(pack, "PROG", None), description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    sub.add_parser("setup")
    sub.add_parser("where")
    n = sub.add_parser("new")
    n.add_argument("slug")
    n.add_argument("--template", default=getattr(pack, "DEFAULT_TEMPLATE", None) or
                   (__import__("registry").DEFAULT_STYLE or "default"))
    n.add_argument("--force", action="store_true")
    for c in ("build", "render", "make", "master", "stems", "calibrate"):
        s = sub.add_parser(c)
        s.add_argument("spec")
        s.add_argument("--force", action="store_true", help="write the project even with harmony problems")
        s.add_argument("--lufs", type=float, default=-16.0, help="loudness target of the mp3 / loop files (master/make)")
        s.add_argument("--to", help="looping songs: also copy the game-ready .ogg (+ loop json) to this path")
    lc = sub.add_parser("loopcheck")
    lc.add_argument("file")
    lc.add_argument("--bars", type=int, help="expected loop length in bars (with --bpm)")
    lc.add_argument("--bpm", type=float)
    au = sub.add_parser("audition")
    au.add_argument("instrument")
    me = sub.add_parser("measure")
    me.add_argument("--instruments", nargs="*", help="catalog ids (default: every unmeasured one)")
    me.add_argument("--kits", nargs="*", help="kit ids (default: every unmeasured kit)")
    hi = sub.add_parser("history")
    hi.add_argument("-n", type=int, default=10)
    sub.add_parser("styles")
    t = sub.add_parser("textures")
    t.add_argument("--force", action="store_true")
    a = ap.parse_args()
    reexec_in_venv(a.cmd)
    {"doctor": lambda a: lmmsenv.doctor(), "setup": cmd_setup,
     "where": lambda a: print(lmmsenv.working_dir() / "projects"),
     "new": cmd_new, "build": cmd_build, "render": cmd_render, "make": cmd_make, "master": cmd_master,
     "stems": cmd_stems, "calibrate": cmd_calibrate, "audition": cmd_audition, "textures": cmd_textures,
     "measure": cmd_measure, "history": cmd_history, "styles": cmd_styles, "loopcheck": cmd_loopcheck}[a.cmd](a)


if __name__ == "__main__":
    main()
