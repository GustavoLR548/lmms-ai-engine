#!/usr/bin/env python3
"""Programmatic grader for the lmms-electronic evals: writes grading.json into every run folder.

    <lmms-core>/.venv/Scripts/python.exe evals/grade.py <workspace>/iteration-N

Each run folder is <iteration>/eval-<name>/<config>/run-<k>/ with outputs/ holding what the run delivered
(song.json, the mastered mp3, response.md). Everything is re-derived from the files: the song is rebuilt in
memory (nothing written), the mp3 is measured again with ffmpeg.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
CORE = SKILL.parent / "lmms-core" / "scripts"
sys.path[:0] = [str(SKILL / "scripts"), str(CORE)]

import electro_pack  # noqa: E402,F401
import engine  # noqa: E402
import looper  # noqa: E402

KICK_DRUMS = {"four", "four_min", "four_kick"}
CALM_DRUMS = {"pulse", "pulse_soft", "shaker", "ticks", "halfstep", "none", None}


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def mmss(s):
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"


class Grader:
    def __init__(self, run_dir):
        self.run, self.out, self.results = run_dir, run_dir / "outputs", []

    def check(self, text, fn):
        try:
            ok, ev = fn()
        except Exception as e:
            ok, ev = False, f"check could not run: {type(e).__name__}: {e}"
        self.results.append(dict(text=text, passed=bool(ok), evidence=ev))

    def load(self):
        specs = sorted(self.out.rglob("song.json"))
        self.spec = json.loads(specs[0].read_text(encoding="utf-8")) if specs else None
        self.song = None
        if self.spec:
            self.song = engine.Song(self.spec, specs[0])
            self.song.generate()
        mp3s = sorted(self.out.rglob("*_v*.mp3"), key=lambda p: int(re.search(r"_v(\d+)\.mp3$", p.name).group(1)))
        self.mp3 = mp3s[-1] if mp3s else None
        r = self.out / "response.md"
        self.response = r.read_text(encoding="utf-8") if r.exists() else ""

    def secs(self):
        return self.spec["sections"]

    # ------------------------------------------------------------------ common
    def common(self, style, lo_s, hi_s, lufs=(-17.0, -15.0)):
        spec, song = self.spec, self.song
        self.check(f"A song.json was delivered and uses the '{style}' style",
                   lambda: (spec is not None and spec.get("style") == style,
                            f"style = {spec.get('style') if spec else 'no song.json in outputs'}"))
        self.check("The song builds with 0 harmony / spec problems",
                   lambda: (song is not None and not song.problems,
                            f"{len(song.problems)} problems: {song.problems[:3]}" if song else "no song"))

        def length():
            d = duration(self.mp3)
            return lo_s <= d <= hi_s, (f"{self.mp3.name}: {mmss(d)} (asked {mmss(lo_s)}-{mmss(hi_s)}); "
                                       f"song {mmss(song.seconds(song.end))}")
        self.check(f"The mastered mp3 is {mmss(lo_s)}-{mmss(hi_s)} long", length)

        def loud():
            lu, tp = looper.loudness(self.mp3)
            return lufs[0] <= lu <= lufs[1] and tp <= -0.5, f"{lu:.1f} LUFS, true peak {tp:.1f} dBFS"
        self.check(f"Mastered to {lufs[0]:g}..{lufs[1]:g} LUFS with true peak <= -0.5 dBFS", loud)

        def movement():
            n = [s["name"] for s in self.secs() if s.get("move") or any((s.get("pump") or {}).values())]
            return len(n) >= max(3, len(self.secs()) // 2), f"{len(n)}/{len(self.secs())} sections move: {n}"
        self.check("Movement over time: at least half the sections (and 3+) use move / pump automation", movement)

        def changes():
            keys = ("prog", "keys", "keys2", "bass", "drums", "pad", "move", "pump", "leads", "shaker", "perc", "ride",
                    "clap", "fill")
            same = [b["name"] for a, b in zip(self.secs(), self.secs()[1:])
                    if all(a.get(k) == b.get(k) for k in keys)]
            return not same, "every section changes something" if not same else f"identical to the previous: {same}"
        self.check("Every section changes at least one thing from the section before it", changes)
        def no_long_loops():
            song = self.song
            lim = song.loop_max_s
            bad = [f"bars {a + 1}-{b} {mmss(song.seconds(a * 192))}-{mmss(song.seconds(b * 192))} "
                   f"({song.seconds((b - a) * 192):.0f} s)" for a, b, _ in song.loop_stretches()
                   if song.seconds((b - a) * 192) > lim]
            return not bad, f"limit {lim:g} s; " + (f"too long: {bad}" if bad else "no loop runs over it")
        self.check("No 4/8-bar loop plays on longer than the style allows (something changes every ~8 bars)",
                   no_long_loops)
        self.check("A reply with a timestamped section list was delivered (response.md)",
                   lambda: (len(re.findall(r"\b\d:\d\d\b", self.response)) >= 3,
                            f"{len(re.findall(r'[0-9]:[0-9][0-9]', self.response))} timestamps in {len(self.response)} chars"))

    def fades(self, fade_in=True):
        def fn():
            first = (self.secs()[0].get("move") or {}).get("master.level")
            last = (self.secs()[-1].get("move") or {}).get("master.level")
            fin = isinstance(first, list) and first[0] <= 0.2
            fout = isinstance(last, list) and last[-1] <= 0.1
            return (fin or not fade_in) and fout, f"first master.level {first}, last {last}"
        self.check("Fades " + ("in and out" if fade_in else "out") + " with master.level", fn)

    # ------------------------------------------------------------------ per eval
    def focus(self):
        self.common("focus", 210, 270)
        s = self.song
        self.check("Focus tempo 72-100 BPM", lambda: (72 <= s.bpm <= 100, f"{s.bpm} BPM"))

        def calm():
            bad = [(x["name"], x.get("drums")) for x in self.secs() if x.get("drums") not in CALM_DRUMS]
            hits = [x["name"] for x in self.secs() if x.get("crash") or x.get("riser")]
            return not bad and not hits, f"non-calm drums {bad}, crash/riser in {hits}"
        self.check("Nothing distracting: only soft grooves, no crashes or risers", calm)

        def sparse_leads():
            notes = [e for e in s.events if e["role"] == "lead"]
            per_min = len(notes) / (s.seconds(s.end) / 60)
            return per_min <= 24, f"{len(notes)} lead notes = {per_min:.1f} per minute (<= 24)"
        self.check("Melody stays in the background (<= 24 lead notes per minute)", sparse_leads)
        self.fades()

    def minimal(self):
        self.common("minimal", 270, 330)
        s = self.song
        self.check("Minimal tempo 116-128 BPM", lambda: (116 <= s.bpm <= 128, f"{s.bpm} BPM"))

        def kick_share():
            kb = sum(int(x["bars"]) for x in self.secs() if x.get("drums") in KICK_DRUMS)
            return kb / s.nbars >= 0.5, f"{kb}/{s.nbars} bars have the four-on-the-floor kick"
        self.check("Four-on-the-floor kick for at least half the track", kick_share)

        def groove_early():
            t = 0
            for x in self.secs():
                if x.get("drums") in KICK_DRUMS and x.get("bass", "none") != "none":
                    sec = s.seconds(t * 192)
                    return sec <= 16, f"kick + bass from {x['name']} at {mmss(sec)} (<= 0:16)"
                t += int(x["bars"])
            return False, "kick and bass never play together"
        self.check("The groove (kick + bass) is there within 16 s - no long DJ intro", groove_early)

        def breakdown():
            t, found = 0, []
            for i, x in enumerate(self.secs()):
                mid = s.nbars * 0.25 <= t <= s.nbars * 0.75
                after = any(y.get("drums") in KICK_DRUMS for y in self.secs()[i + 1:])
                if mid and x.get("drums") not in KICK_DRUMS and int(x["bars"]) >= 8 and after:
                    found.append(f"{x['name']} (bar {t + 1}, drums={x.get('drums')})")
                t += int(x["bars"])
            return bool(found), f"kickless breakdowns in the middle half: {found or 'none'}"
        self.check("A breakdown (8+ bars without the kick) in the middle half, with the kick coming back", breakdown)

        def pumped():
            n = [x["name"] for x in self.secs() if any((x.get("pump") or {}).values())]
            return bool(n), f"pump in {n}"
        self.check("Sidechain-style pump used", pumped)

        def few_chords():
            # colour changes on one root (Fm9 -> Fm11) are part of the style, so count harmonic roots
            names = {g["chord"].name for g in s.segments}
            roots = {g["chord"].root for g in s.segments}
            return len(roots) <= 4, f"{len(roots)} chord roots ({len(names)} chords: {sorted(names)})"
        self.check("Hypnotic harmony: at most 4 chord roots", few_chords)

    def ambient(self):
        self.common("ambient", 165, 195, lufs=(-24.0, -15.0))
        s, spec = self.song, self.spec
        self.check("No drums anywhere", lambda: (all(x.get("drums") in ("none", None) for x in self.secs()),
                                                  f"drums: {[x.get('drums') for x in self.secs()]}"))

        def under_voice():
            bed = spec.get("mode") == "bed"
            notes = [e for e in s.events if e["role"] == "lead"]
            per_min = len(notes) / (s.seconds(s.end) / 60)
            return bed or per_min <= 12, f"mode = {spec.get('mode', 'listen')}, {per_min:.1f} lead notes per minute"
        self.check("Made to sit under narration: bed mode or a very sparse melody (<= 12 notes / min)", under_voice)

        def slow_harmony():
            durs = []
            for g in s.segments:
                if durs and durs[-1][0] == g["chord"].name:
                    durs[-1][1] += g["end"] - g["start"]
                else:
                    durs.append([g["chord"].name, g["end"] - g["start"]])
            avg = sum(d for _, d in durs) / len(durs) / 192
            return avg >= 2, f"average chord length {avg:.1f} bars ({len(durs)} chord changes)"
        self.check("Slow harmony: chords last 2 bars or more on average", slow_harmony)
        self.fades()

    def downtempo(self):
        self.common("downtempo", 210, 270)
        s, spec = self.song, self.spec
        self.check("Downtempo tempo 80-100 BPM with swing", lambda: (80 <= s.bpm <= 100 and s.swing >= 2,
                                                                     f"{s.bpm} BPM, swing {s.swing}"))

        def flute_hook():
            flutes = {"soft_flute", "gs_flute", "flute"}
            secs = {}
            for x in self.secs():
                for ld in x.get("leads") or []:
                    if ld["inst"] in flutes and ld.get("harmony") != "below":
                        secs.setdefault(ld["melody"], set()).add(x["name"])
            best = max(secs.items(), key=lambda kv: len(kv[1]), default=(None, set()))
            return len(best[1]) >= 2, f"flute melodies by section: { {k: sorted(v) for k, v in secs.items()} }"
        self.check("A flute hook that returns in at least two sections", flute_hook)
        self.check("A broken / swung beat (broken or breaks) in the main sections",
                   lambda: (sum(1 for x in self.secs() if x.get("drums") in ("broken", "breaks")) >= 2,
                            f"drums: {[x.get('drums') for x in self.secs()]}"))
        self.fades(fade_in=False)


def main(iteration):
    it = Path(iteration)
    for ev in sorted(it.glob("eval-*")):
        name = ev.name[5:]
        for run in sorted(p.parent for p in ev.rglob("outputs") if p.is_dir()):
            g = Grader(run)
            g.load()
            {"focus-work-4min": g.focus, "minimal-breakdown-5min": g.minimal, "ambient-narration-bed-3min": g.ambient,
             "downtempo-flute-hook-4min": g.downtempo}[name]()
            passed = sum(r["passed"] for r in g.results)
            out = dict(expectations=g.results,
                       summary=dict(passed=passed, failed=len(g.results) - passed, total=len(g.results),
                                    pass_rate=round(passed / len(g.results), 2)))
            (run / "grading.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
            print(f"{name}/{run.relative_to(ev)}: {passed}/{len(g.results)}")
            for r in g.results:
                print(f"  {'PASS' if r['passed'] else 'FAIL'}  {r['text']}\n        {r['evidence']}")


if __name__ == "__main__":
    main(sys.argv[1])
