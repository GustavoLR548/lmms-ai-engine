"""Locate LMMS, its factory data, the user's LMMS working directory and ffmpeg."""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def lmms_exe():
    cands = [os.environ.get("LMMS_EXE"),
             "C:/Program Files/LMMS/lmms.exe", "C:/Program Files (x86)/LMMS/lmms.exe",
             "/Applications/LMMS.app/Contents/MacOS/lmms", shutil.which("lmms")]
    for c in cands:
        if c and Path(c).exists():
            return str(Path(c))
    return None


def lmms_version(exe):
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=30)
        m = re.search(r"LMMS\s+([\d.]+\S*)", out.stdout + out.stderr)
        return m.group(1) if m else "?"
    except Exception:
        return "?"


def data_dir(exe=None):
    """Factory data dir holding presets/ and samples/."""
    exe = exe or lmms_exe()
    cands = [os.environ.get("LMMS_DATA")]
    if exe:
        p = Path(exe).resolve().parent
        cands += [p / "data", p.parent / "share" / "lmms", p.parent / "Resources" / "data"]
    cands += ["/usr/share/lmms", "/usr/local/share/lmms"]
    for c in cands:
        if c and (Path(c) / "presets").exists():
            return Path(c)
    return None


def working_dir():
    """User's LMMS working dir (projects/, samples/), from ~/.lmmsrc.xml when present."""
    rc = Path.home() / ".lmmsrc.xml"
    if rc.exists():
        m = re.search(r'workingdir="([^"]+)"', rc.read_text(encoding="utf-8", errors="replace"))
        if m and Path(m.group(1)).exists():
            return Path(m.group(1))
    for c in (Path.home() / "Documents" / "lmms", Path.home() / "lmms"):
        if c.exists():
            return c
    return Path.home() / "Documents" / "lmms"


def ffmpeg():
    return shutil.which("ffmpeg")


def venv_python():
    sub = "Scripts/python.exe" if os.name == "nt" else "bin/python"
    return SKILL_DIR / ".venv" / sub


def have_numpy():
    try:
        import numpy  # noqa: F401
        import scipy  # noqa: F401
        return True
    except ImportError:
        return False


def soundfont_status():
    d = working_dir() / "samples" / "soundfonts"
    n = len(list(d.glob("*.sf2"))) if d.exists() else 0
    return f"{n} in {d}" if n else f"none in {d} - only Zyn / TripleOsc / sample instruments available"


def doctor():
    exe = lmms_exe()
    rows = [("LMMS", exe or "NOT FOUND - install LMMS 1.2.x or set LMMS_EXE"),
            ("LMMS version", lmms_version(exe) if exe else "-"),
            ("LMMS data", str(data_dir(exe) or "NOT FOUND - set LMMS_DATA")),
            ("Working dir", str(working_dir())),
            ("ffmpeg", ffmpeg() or "NOT FOUND - needed for loudness + mp3"),
            ("python", sys.executable),
            ("numpy+scipy", "ok" if have_numpy() else
             ("in lmms-core/.venv" if venv_python().exists() else "missing - run the `setup` command")),
            ("SoundFonts", soundfont_status())]
    w = max(len(k) for k, _ in rows)
    for k, v in rows:
        print(f"{k:<{w}}  {v}")
    ok = exe and data_dir(exe) and ffmpeg() and (have_numpy() or venv_python().exists())
    print("\nstatus:", "READY" if ok else "NOT READY")
    return bool(ok)
