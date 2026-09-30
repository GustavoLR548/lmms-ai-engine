"""Variety memory: a fingerprint of every song built, so new songs don't drift back into the same sound.

Stored in <lmms workingdir>/projects/.lmms-history.json (one entry per slug, shared by every lmms-* genre
skill, updated on every build). `history` shows recent songs and what they used; `build` warns when a song
matches a recent one on most dimensions.
"""
import datetime
import json
import re

import lmmsenv

DIMENSIONS = ["style", "tempo", "key", "keys", "bass", "kit", "leads", "form", "textures", "chords"]


def _file():
    f = lmmsenv.working_dir() / "projects" / ".lmms-history.json"
    old = f.with_name(".lofi-history.json")          # name used before lmms-core existed
    if old.exists() and not f.exists():
        old.rename(f)
    return f


def load():
    f = _file()
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def fingerprint(song, slug):
    import engine
    leads = sorted({l["inst"] for s in song.sections for l in (s.get("leads") or [])})
    kinds = [re.sub(r"[\s\d]+$", "", s["name"]).strip().lower() for s in song.sections]
    chords = sorted({str(sym) for prog in song.spec.get("progressions", {}).values() for e in prog
                     for sym in (e if isinstance(e, list) else str(e).split())})
    tex = song.palette.get("textures", ["vinyl"])
    return dict(slug=slug, title=song.spec.get("title", slug), date=datetime.date.today().isoformat(),
                genre=song.genre, style=song.style_id, bpm=song.bpm, key=engine.NAMES[song.key_pc],
                keys=song.palette.get("keys"), keys2=song.palette.get("keys2"), bass=song.palette.get("bass"),
                pad=song.palette.get("pad"), kit=song.palette.get("kit", "dusty"), leads=leads,
                textures=sorted(tex if isinstance(tex, list) else tex), form=kinds, chords=chords,
                length=round(song.seconds(song.end)))


def _jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / max(1, len(a | b))


def same(a, b):
    """Which dimensions two fingerprints share."""
    hits = []
    if a["style"] == b["style"]:
        hits.append("style")
    if abs(a["bpm"] - b["bpm"]) <= 4:
        hits.append("tempo")
    if a["key"] == b["key"]:
        hits.append("key")
    if a["keys"] == b["keys"]:
        hits.append("keys")
    if a["bass"] == b["bass"]:
        hits.append("bass")
    if a["kit"] == b["kit"]:
        hits.append("kit")
    if set(a["leads"]) & set(b["leads"]) or (not a["leads"] and not b["leads"]):
        hits.append("leads")
    if _jaccard(a["form"], b["form"]) >= 0.6 and len(a["form"]) == len(b["form"]):
        hits.append("form")
    if a["textures"] == b["textures"]:
        hits.append("textures")
    if _jaccard(a["chords"], b["chords"]) >= 0.4:
        hits.append("chords")
    return hits


def record_and_compare(song, slug, recent=6):
    fp = fingerprint(song, slug)
    hist = [h for h in load() if h.get("slug") != slug]
    lines = []
    scored = sorted(((same(fp, h), h) for h in hist[-recent:]), key=lambda x: -len(x[0]))
    if scored:
        hits, h = scored[0]
        tag = "TOO SIMILAR" if len(hits) >= 6 else "variety ok"
        lines.append(f"variety: closest recent song is {h['slug']!r} - {len(hits)}/{len(DIMENSIONS)} shared "
                     f"({', '.join(hits) or 'nothing'}) -> {tag}")
        if len(hits) >= 6:
            lines.append("  change at least 3 of those (style, instruments, key/tempo, form) unless the user "
                         "asked for something like that song")
    hist.append(fp)
    try:
        _file().write_text(json.dumps(hist, indent=1), encoding="utf-8")
    except OSError as e:
        lines.append(f"(could not update history: {e})")
    return lines


def show(n=10):
    hist = load()[-n:]
    if not hist:
        return "no songs recorded yet"
    out = [f"{'slug':<24}{'style':<9}{'bpm':>4} {'key':<4}{'keys':<15}{'bass':<14}{'kit':<13}{'leads':<22}form"]
    for h in hist:
        out.append(f"{h['slug'][:23]:<24}{h['style']:<9}{h['bpm']:>4g} {h['key']:<4}{(h['keys'] or '-')[:14]:<15}"
                   f"{(h['bass'] or '-')[:13]:<14}{h['kit'][:12]:<13}{','.join(h['leads'])[:21]:<22}"
                   f"{'-'.join(f[:5] for f in h['form'])}")
    last = hist[-4:]
    used = lambda k: sorted({str(h[k]) for h in last})
    out.append("")
    out.append("recently used (last 4) - prefer something else unless asked: "
               f"styles {used('style')}, keys {used('key')}, chord instruments {used('keys')}, kits {used('kit')}")
    return "\n".join(out)
