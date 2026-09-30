#!/usr/bin/env python3
"""lmms-gamemusic command line: the 16-bit game-music pack on top of lmms-core.

Same commands as lmms-core (doctor, setup, new, build, make, loopcheck, styles, history, measure, ...) - run
`python scripts/gamemusic.py -h`. A song.json with "loop" makes `make` export seamless game-ready loops.
lmms-core must be installed next to this skill (~/.claude/skills/lmms-core) or pointed to with LMMS_CORE.
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = Path(os.environ.get("LMMS_CORE") or HERE.parents[1] / "lmms-core") / "scripts"
if not (CORE / "lmmscli.py").exists():
    sys.exit(f"lmms-core not found at {CORE.parent} - install the lmms-core skill next to lmms-gamemusic "
             "or set LMMS_CORE to its folder")
sys.path[:0] = [str(HERE), str(CORE)]

import game_pack  # noqa: E402  (registers the 16-bit styles and game patterns)
import lmmscli  # noqa: E402

if __name__ == "__main__":
    lmmscli.main(game_pack)
