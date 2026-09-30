#!/usr/bin/env python3
"""lmms-hiphop command line: the lofi genre pack on top of lmms-core.

Same commands as lmms-core (doctor, setup, new, build, make, render, master, stems, calibrate, styles,
history, measure, audition, textures) - run `python scripts/lofi.py -h`. lmms-core must be installed next to
this skill (~/.claude/skills/lmms-core) or pointed to with the LMMS_CORE environment variable.
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = Path(os.environ.get("LMMS_CORE") or HERE.parents[1] / "lmms-core") / "scripts"
if not (CORE / "lmmscli.py").exists():
    sys.exit(f"lmms-core not found at {CORE.parent} - install the lmms-core skill next to lmms-hiphop "
             "or set LMMS_CORE to its folder")
sys.path[:0] = [str(HERE), str(CORE)]

import lofi_pack  # noqa: E402  (registers the lofi styles and patterns)
import lmmscli  # noqa: E402

if __name__ == "__main__":
    lmmscli.main(lofi_pack)
