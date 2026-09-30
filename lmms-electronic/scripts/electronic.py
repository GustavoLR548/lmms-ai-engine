#!/usr/bin/env python3
"""lmms-electronic command line: the electronic genre pack (ambient, deep focus, minimal, downtempo) on lmms-core.

Same commands as lmms-core (doctor, setup, new, build, make, render, master, stems, calibrate, styles, history,
measure, audition, textures) - run `python scripts/electronic.py -h`. lmms-core must be installed next to this
skill (~/.claude/skills/lmms-core) or pointed to with the LMMS_CORE environment variable.
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = Path(os.environ.get("LMMS_CORE") or HERE.parents[1] / "lmms-core") / "scripts"
if not (CORE / "lmmscli.py").exists():
    sys.exit(f"lmms-core not found at {CORE.parent} - install the lmms-core skill next to lmms-electronic "
             "or set LMMS_CORE to its folder")
sys.path[:0] = [str(HERE), str(CORE)]

import electro_pack  # noqa: E402  (registers the electronic styles and patterns)
import lmmscli  # noqa: E402

if __name__ == "__main__":
    lmmscli.main(electro_pack)
