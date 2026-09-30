# lmms-ai-engine

Skills for Claude Code that compose music in [LMMS](https://lmms.io) from plain-language prompts. Each one writes
an editable `.mmp` project, checks every note against the harmony, renders with LMMS and masters an MP3 (or
seamless OGG loops for games). All sounds are license-safe: LMMS's own synths and samples, FreePats (CC0) and
GeneralUser GS.

| skill | what it makes |
|---|---|
| `lmms-core` | the shared engine: song.json format, harmony checker, instrument catalog, automation, render + master, game-loop export, level measurement, variety history. The genre skills run on it |
| `lmms-hiphop` | lofi: jazzy boom-bap, bossa, sleepy piano, Dilla / neo-soul, 80s city-pop |
| `lmms-gamemusic` | 16-bit game music loops: SNES-style sampled orchestra or Genesis / DOS FM, with intro + loop points |
| `lmms-electronic` | ambient, deep focus, minimal / deep house, downtempo |

## Install

Copy the four folders into `~/.claude/skills/` (lmms-core must sit next to the genre skills, or point the
`LMMS_CORE` environment variable at it). Then, once:

```bash
python ~/.claude/skills/lmms-electronic/scripts/electronic.py doctor
python ~/.claude/skills/lmms-electronic/scripts/electronic.py setup
```

`doctor` finds LMMS (1.2.2), its data folder, ffmpeg and the SoundFonts; `setup` creates `lmms-core/.venv` with
numpy + scipy. Any genre skill's entry script works for these two commands (`lofi.py`, `gamemusic.py`,
`electronic.py`).

## Layout

```
lmms-core/        engine (scripts/), catalog levels (assets/levels.json), format references
lmms-<genre>/     SKILL.md, scripts/<genre>_pack.py (styles + patterns), assets/examples/ (templates),
                  references/ (style guides, feedback map), evals/ (test prompts, grader)
```

`lmms-core/references/genre-packs.md` explains how to add another genre.
