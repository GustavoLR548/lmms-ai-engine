#!/usr/bin/env python3
"""Programmatic grader for the lmms-gamemusic evals: writes grading.json into every run folder.

    <lmms-core>/.venv/Scripts/python.exe evals/grade.py <workspace>/iteration-N

Each run folder is <iteration>/eval-<name>/<config>/run-<k>/ with outputs/ holding what the run delivered (song.json,
the loop json, the .ogg files, the preview mp3, response.md; eval 1 also writes into outputs/emberfall/).
The checks re-derive everything from the files - the song is rebuilt in memory (no files written), the loop
files are decoded and measured again - so a run cannot pass by only claiming success.
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

import game_pack  # noqa: E402,F401
import engine  # noqa: E402
import looper  # noqa: E402
from lmmscli import read_audio  # noqa: E402

SR = 44100
MINOR = {"mtriad", "m7", "m9", "m11", "m6", "5", "dim", "m7b5"}
MAJOR = {"triad", "maj7", "maj9", "6/9", "dom7", "9", "13", "sus4", "sus2", "13sus", "9sus"}
AVOID_EMBERFALL = {"saw_lead", "square_lead", "synth_brass", "synth_bass", "lately_bass", "finger_bass", "slap_bass",
                   "fretless_bass", "dist_guitar", "fm_epiano", "synth_strings", "drum_machine", "dilla"}
BUSY_DRUMS = {"battle", "boss", "fm_rock", "adventure"}


def find(outputs, pattern, exclude=None):
    hits = [p for p in outputs.rglob(pattern) if not (exclude and exclude in p.parts)]
    return sorted(hits, key=lambda p: len(p.parts))


def ogg_tags(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream_tags:format_tags", "-of", "json", str(path)],
                       capture_output=True, text=True)
    tags = {}
    try:
        d = json.loads(r.stdout)
        for s in d.get("streams", []):
            tags.update({k.upper(): v for k, v in s.get("tags", {}).items()})
        tags.update({k.upper(): v for k, v in d.get("format", {}).get("tags", {}).items()})
    except json.JSONDecodeError:
        pass
    return tags


class Grader:
    def __init__(self, run_dir, eval_name):
        self.run, self.name = run_dir, eval_name
        self.out = run_dir / "outputs"
        self.results = []

    def check(self, text, fn):
        try:
            ok, ev = fn()
        except Exception as e:                                  # a crashed check is a failed check
            ok, ev = False, f"check could not run: {type(e).__name__}: {e}"
        self.results.append(dict(text=text, passed=bool(ok), evidence=ev))

    # ------------------------------------------------------------------ inputs
    def load(self):
        specs = find(self.out, "song.json", exclude="emberfall")
        self.spec_path = specs[0] if specs else None
        self.spec = json.loads(self.spec_path.read_text(encoding="utf-8")) if self.spec_path else None
        self.song = None
        if self.spec:
            self.song = engine.Song(self.spec, self.spec_path)
            self.song.generate()
        lj = find(self.out, "*_loop.json") or find(self.out, "*.loop.json")
        self.loop_info = json.loads(lj[0].read_text(encoding="utf-8")) if lj else None
        self.loop_json_path = lj[0] if lj else None
        loops = find(self.out, "*_loop.ogg", exclude="emberfall")
        self.loop_ogg = loops[0] if loops else None
        resp = self.out / "response.md"
        self.response = resp.read_text(encoding="utf-8") if resp.exists() else ""

    def loop_bars(self):
        s = self.song
        return [b for b in s.bars if b["bar"] >= s.loop_start_bar]

    def loop_sections(self):
        s = self.song
        return [sec for sec in s.sections if sec["start_bar"] >= s.loop_start_bar]

    def first_last_chords(self):
        lb = self.loop_bars()
        return lb[0]["segs"][0]["chord"], lb[-1]["segs"][-1]["chord"]

    # ------------------------------------------------------------------ common checks
    def common(self, style, lufs_target, loop_file=None):
        s, spec = self.song, self.spec
        self.check("A song.json was delivered and uses the '%s' console style" % "' or '".join(style),
                   lambda: (spec is not None and spec.get("style") in style,
                            f"style = {spec.get('style') if spec else 'no song.json in outputs'}"))
        self.check("song.json is a loop (\"loop\": true or {\"from\": ...})",
                   lambda: (bool(spec and spec.get("loop")), f"loop = {spec.get('loop') if spec else None}"))
        self.check("The song builds with 0 harmony / spec problems",
                   lambda: (s is not None and not s.problems,
                            f"{len(s.problems)} problems: {s.problems[:3]}" if s else "no song"))

        def two_parts():
            progs = {sec["prog"] for sec in self.loop_sections()}
            return len(progs) >= 2, f"loop sections use progressions {sorted(progs)}"
        self.check("The loop has at least two contrasting parts (two or more different progressions)", two_parts)

        def leads_home():
            first, last = self.first_last_chords()
            return first.name != last.name, f"loop starts on {first.name}, last bar ends on {last.name}"
        self.check("The last bar leads back into the loop (its final chord differs from the loop's first chord)",
                   leads_home)
        self.check("make's loop json reports the seam SEAMLESS",
                   lambda: (bool(self.loop_info and self.loop_info["seam"]["seamless"]),
                            json.dumps(self.loop_info["seam"]) if self.loop_info else "no loop json in outputs"))
        f = loop_file or self.loop_ogg

        def independent_seam():
            x, _ = read_audio(f)
            bpm = s.bpm
            bars = s.nbars - s.loop_start_bar
            exp = round(s.seconds(s.end - s.loop_start) * SR)
            res = looper.seam_check(x.astype("float64"), expected_len=exp)
            ok = res["jump"] < 1.0 and abs(res["length_error_ms"]) < 5
            return ok, (f"{f.name}: {len(x)} samples = {len(x) / SR:.3f} s for {bars} bars at {bpm} BPM "
                        f"(expected {exp}); wrap jump {res['jump']}, length error {res['length_error_ms']} ms")
        self.check("Independent check of the loop file: sample-continuous wrap and exact bar length (±5 ms)",
                   independent_seam)

        def loud():
            lufs, tp = looper.loudness(f)
            return abs(lufs - lufs_target) <= 1.0, f"{f.name}: {lufs:.1f} LUFS (target {lufs_target})"
        self.check(f"Loop loudness is {lufs_target} LUFS ±1", loud)

        def peak():
            lufs, tp = looper.loudness(f)
            return tp <= -1.0, f"{f.name}: true peak {tp:.1f} dBFS"
        self.check("True peak of the loop is at or below -1 dBFS", peak)
        self.check("A preview mp3 and the reply (response.md) were delivered",
                   lambda: (bool(find(self.out, "*_preview_v*.mp3")) and len(self.response) > 50,
                            f"previews {[p.name for p in find(self.out, '*_preview_v*.mp3')]}, "
                            f"response {len(self.response)} chars"))

    def first_chord_quality(self, allowed, label):
        def fn():
            first, _ = self.first_last_chords()
            return first.quality in allowed, f"loop starts on {first.name} ({first.quality})"
        self.check(label, fn)

    # ------------------------------------------------------------------ per eval
    def overworld(self):
        proj = self.out / "emberfall"
        dest = proj / "assets" / "audio" / "music" / "overworld.ogg"
        self.check("Exported to assets/audio/music/overworld.ogg (SOUND.md's path) with loop json next to it",
                   lambda: (dest.exists() and dest.with_suffix(".loop.json").exists(),
                            f"overworld.ogg {'exists' if dest.exists() else 'MISSING'}, overworld.loop.json "
                            f"{'exists' if dest.with_suffix('.loop.json').exists() else 'MISSING'}; music folder: "
                            f"{[p.name for p in dest.parent.glob('*')] if dest.parent.exists() else 'none'}"))
        self.common(("snes",), -18.0, loop_file=dest if dest.exists() else None)

        def avoid():
            s = self.song
            used = {v for k, v in s.palette.items() if isinstance(v, str)}
            used |= {ld["inst"] for sec in self.spec["sections"] for ld in sec.get("leads", [])}
            bad = sorted(u for u in used if u in AVOID_EMBERFALL or u.startswith("opl_"))
            return not bad, f"instruments used: {sorted(used)}" + (f"; AVOID violations: {bad}" if bad else "")
        self.check("Instruments respect SOUND.md's Avoid line (no synth / FM leads, distorted guitar, electric or "
                   "synth bass, drum machine)", avoid)
        self.check("Tempo is inside SOUND.md's 80-140 BPM range",
                   lambda: (80 <= self.song.bpm <= 140, f"{self.song.bpm} BPM"))
        self.first_chord_quality(MAJOR, "Exploration theme in a major key, as SOUND.md asks (loop starts on a major chord)")
        orig = (SKILL / "evals" / "files" / "emberfall" / "SOUND.md").read_text(encoding="utf-8")
        now_p = proj / "SOUND.md"
        now = now_p.read_text(encoding="utf-8") if now_p.exists() else ""
        head = lambda t: t.split("## Audio Log")[0]

        def log_row():
            log = now.split("## Audio Log")[-1] if "## Audio Log" in now else ""
            rows = [ln for ln in log.splitlines() if ln.startswith("|") and "overworld" in ln]
            return bool(rows), rows[0] if rows else "no Audio Log row mentions overworld"
        self.check("SOUND.md's Audio Log got a new row for overworld.ogg", log_row)
        self.check("SOUND.md's style sections (everything above the Audio Log) were left unchanged",
                   lambda: (head(now) == head(orig), "identical" if head(now) == head(orig) else "modified"))

    def boss(self):
        self.common(("fm",), -16.0)
        spec, s = self.spec, self.song
        self.check("Has a short play-once intro (loop.from set, 1-8 intro bars)",
                   lambda: (isinstance(spec.get("loop"), dict) and 1 <= s.loop_start_bar <= 8,
                            f"loop = {spec.get('loop')}, intro bars = {s.loop_start_bar}"))
        self.check("Fast tempo for a boss fight (>= 140 BPM)", lambda: (s.bpm >= 140, f"{s.bpm} BPM"))
        self.first_chord_quality(MINOR, "Aggressive / dark harmony (loop starts on a minor or power chord)")

        def files():
            names = [p.name for p in self.out.rglob("*.ogg")]
            need = ["_intro.ogg", "_loop.ogg", "_full.ogg"]
            return all(any(n.endswith(k) for n in names) for k in need), f"ogg files: {names}"
        self.check("Delivers the intro, loop and full (tagged) OGG files", files)

        def tags():
            full = find(self.out, "*_full.ogg")[0]
            t = ogg_tags(full)
            li = self.loop_info
            ok = (int(t.get("LOOPSTART", -1)) == li["loop_start_samples"] and
                  int(t.get("LOOPLENGTH", -1)) == li["loop_length_samples"])
            x, _ = read_audio(full)
            ok = ok and abs(len(x) - li["loop_start_samples"] - li["loop_length_samples"]) <= 2
            return ok, (f"{full.name}: LOOPSTART {t.get('LOOPSTART')} / LOOPLENGTH {t.get('LOOPLENGTH')} vs json "
                        f"{li['loop_start_samples']} / {li['loop_length_samples']}; file {len(x)} samples")
        self.check("full.ogg's LOOPSTART / LOOPLENGTH tags match the loop json and the file length", tags)
        self.check("The reply tells the user how to loop it in Godot (Loop import flag or loop_offset)",
                   lambda: ("godot" in self.response.lower() and
                            bool(re.search(r"loop[_ ]offset|loop\b.*\bon|import", self.response, re.I)),
                            re.sub(r"\s+", " ", next((ln for ln in self.response.splitlines() if "odot" in ln),
                                                     "no line mentions Godot"))[:200]))

    def dungeon(self):
        self.common(("snes", "fm"), -16.0)
        s, spec = self.song, self.spec
        self.check("Loop is about a minute (50-70 s)",
                   lambda: (50 <= s.loop_seconds() <= 70, f"loop {s.loop_seconds():.1f} s "
                                                          f"({s.nbars - s.loop_start_bar} bars at {s.bpm} BPM)"))
        self.check("Slow-to-moderate dungeon tempo (<= 110 BPM)", lambda: (s.bpm <= 110, f"{s.bpm} BPM"))
        self.first_chord_quality(MINOR | {"sus4", "sus2"}, "Tense / dark harmony (loop starts on a minor, power or sus chord)")

        def restrained():
            busy = [(sec["name"], sec.get("drums"), sec.get("keys")) for sec in spec["sections"]
                    if sec.get("drums") in BUSY_DRUMS or sec.get("keys") == "stabs8"]
            return not busy, ("no busy grooves" if not busy else f"busy sections: {busy}") + \
                f"; mode = {spec.get('mode', 'listen')}"
        self.check("Arrangement stays out of the way of combat SFX (no battle / boss / rock drums, no 8th-note stabs)",
                   restrained)


def main(iteration):
    it = Path(iteration)
    for ev in sorted(it.glob("eval-*")):
        name = ev.name[5:]
        for run in sorted(p.parent for p in ev.rglob("outputs") if p.is_dir() and "outputs" not in p.parent.parts):
            g = Grader(run, name)
            g.load()
            {"overworld-snes-soundmd": g.overworld, "boss-fm-intro": g.boss,
             "dungeon-underplay-1min": g.dungeon}[name]()
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
