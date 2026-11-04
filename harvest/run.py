#!/usr/bin/env python3
import json,os,re,sys,time
sys.path.insert(0,"/home/user/harvest")
from harvester import (api,fetch,bullets,place_from_bullet,clean_name,classify,
                       event_text,is_birth_death,targets_for_year,fetch_with_fallback,named_event)
import html as _html
from geo import resolve_places_v2

def build(years, out_path, verbose=True):
    rows = []
    stats = {"pages_ok":0,"pages_redirect":0,"pages_missing":0,"bullets":0,
             "with_place":0,"geocoded":0,"skipped_noise":0,"pages_reused":0}
    seen_pages = set()
    sink = open(out_path + ".partial", "w", encoding="utf-8")
    pending = []   # (year, line, place)
    for y in years:
        title, w = fetch_with_fallback(y)
        if w is None:
            stats["pages_missing"] += 1
            print(f"  {y}: NO PAGE", flush=True)
            continue
        if title in seen_pages:
            stats["pages_reused"] += 1
            continue
        seen_pages.add(title)
        stats["pages_ok"] += 1
        print(f"  {y} -> {title}", flush=True)
        if False:
            stats["pages_missing"] += 1
            if verbose: print(f"  {y}: NO PAGE", flush=True); continue
        for line in bullets(w):
            stats["bullets"] += 1
            line = _html.unescape(line)          # BEFORE date stripping & place match
            if is_birth_death(line):
                stats["skipped_noise"] += 1; continue
            place = place_from_bullet(line)
            if not place:
                stats["skipped_noise"] += 1; continue
            stats["with_place"] += 1
            # year: prefer explicit BC/AD in the bullet, else the page year
            # year: explicit BC only when NOT part of a century phrase; else page year
            m = re.search(r'(?<!\w)(\d{1,4})\s*(?:BC|BCE)\b(?!\s*centur)', line, re.I)
            if m and not re.search(r'\b\d{1,2}(?:st|nd|rd|th)\s+century', line, re.I):
                yr = -int(m.group(1))
            else:
                m2 = re.search(r'(?<!\w)(\d{3,4})\s*(?:AD|CE)\b', line, re.I)
                yr = int(m2.group(1)) if m2 else y
            pending.append((yr, line, place, named_event(line)))
    # resolve coordinates: Wikipedia -> QID -> Wikidata P625 (with P276/P131 fallback)
    titles = sorted({t for _,_,p,e in pending for t in (p, e) if t})
    if verbose: print(f"  resolving {len(titles)} unique place titles...", flush=True)
    cache = resolve_places_v2(titles)
    for yr, line, place, evname in pending:
        co = cache.get(evname) if evname else None
        src = evname
        if not co:
            co = cache.get(place); src = place
        if not co: continue
        stats["geocoded"] += 1
        name = clean_name(event_text(line))
        if not name or len(name) < 8: continue
        rec = {
            "id": f"wp_{yr}_{len(rows)}",
            "name": name[:300],
            "start": yr, "end": yr,
            "lat": co[0], "lon": co[1],
            "radiusKm": 20,
            "kind": classify(line),
            "effect": "military_presence" if classify(line) in ("battle","siege") else "political",
            "confidence": "wikipedia_year_page",
            "place": src,
        }
        rows.append(rec)
        sink.write(json.dumps(rec, ensure_ascii=False) + "\n"); sink.flush()
    sink.close()
    os.replace(out_path + ".partial", out_path)
    if verbose:
        print(json.dumps(stats,indent=2), flush=True)
        print(f"  -> {len(rows)} events written to {out_path}", flush=True)
    return rows, stats


if __name__ == "__main__":
    spec = sys.argv[1] if len(sys.argv) > 1 else ""
    out  = sys.argv[2] if len(sys.argv) > 2 else "/home/user/harvest/sample.jsonl"
    ys = []
    for part in spec.replace(",", " ").split():
        if not part:
            continue
        if ":" in part:
            lo, hi = part.split(":")
            ys += list(range(int(lo), int(hi) + 1))
        else:
            ys.append(int(part))
    print("harvesting %d years -> %s" % (len(ys), out), flush=True)
    build(ys, out)
