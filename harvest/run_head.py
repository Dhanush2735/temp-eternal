#!/usr/bin/env python3
import json,os,re,sys,time
sys.path.insert(0,"/home/user/harvest")
from harvester import (api,fetch,bullets,place_from_bullet,clean_name,classify,
                       resolve,load_cache,save_cache,targets_for_year,OUT)

def build(years, out_path, verbose=True):
    cache = load_cache()
    rows = []
    stats = {"pages_ok":0,"pages_redirect":0,"pages_missing":0,"bullets":0,
             "with_place":0,"geocoded":0,"skipped_noise":0}
    pending = []   # (year, line, place)
    for y in years:
        got = None
        for title in targets_for_year(y):
            w, status = fetch(title); time.sleep(0.7)
            if status == "ok":
                stats["pages_ok"] += 1; got = (title, w); break
            elif status.startswith("redirect"):
                continue
            else:
                continue
        if not got:
            stats["pages_missing"] += 1
            if verbose: print(f"  {y}: NO PAGE", flush=True); continue
        title, w = got
        for line in bullets(w):
            stats["bullets"] += 1
            place = place_from_bullet(line)
            if not place:
                stats["skipped_noise"] += 1; continue
            stats["with_place"] += 1
            # year: prefer explicit BC/AD in the bullet, else the page year
            m = re.search(r'(?<!\w)(\d{1,4})\s*(?:BC|BCE)\b', line, re.I)
            yr = -int(m.group(1)) if m else y
            if not m:
                m2 = re.search(r'(?<!\w)(\d{3,4})\s*(?:AD|CE)\b', line, re.I)
                if m2: yr = int(m2.group(1))
            pending.append((yr, line, place))
    # resolve coordinates in batches
    titles = sorted({p for _,_,p in pending})
    if verbose: print(f"  resolving {len(titles)} unique place titles...", flush=True)
    cache = resolve(titles, cache); save_cache(cache)
    for yr, line, place in pending:
        co = cache.get(place)
        if not co: continue
        stats["geocoded"] += 1
        name = clean_name(line)
        if not name or len(name) < 8: continue
        rows.append({
            "id": f"wp_{yr}_{len(rows)}",
            "name": name[:300],
            "start": yr, "end": yr,
            "lat": co[0], "lon": co[1],
            "radiusKm": 20,
            "kind": classify(line),
            "effect": "military_presence" if classify(line) in ("battle","siege") else "political",
            "confidence": "wikipedia_year_page",
            "place": place,
        })
    with open(out_path,"w",encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+"\n")
    if verbose:
        print(json.dumps(stats,indent=2), flush=True)
        print(f"  -> {len(rows)} events written to {out_path}", flush=True)
    return rows, stats

if __name__ == "__main__":
