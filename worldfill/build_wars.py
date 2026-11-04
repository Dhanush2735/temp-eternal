#!/usr/bin/env python3
"""Step 2c of the "<50%" plan: wars, Wikipedia first.

Primary: English Wikipedia "List of wars: before 1000", "1000-1499", ... "2020-present" and
the two Low Countries lists (dump 2026-10-01). Each row gives start, finish, the war's name
(usually a link to its article) and the two sides.
Where: the "place =" line of the war article's infobox (Infobox military conflict), read from
the same dump; else the defeated side's state in the start year (Cliopatria), else the
victorious side's.
Every war becomes regional news (confidence "wikipedia_region"): seen across its region for
its years, never a local event to stop. Wars the mod already has as Wikidata war theatres
(same words, overlapping years) are skipped.
Writes worldfill/wars_report.json and history/events_wars.json.gz.
Usage: python3 build_wars.py [--dry-run]
"""
import collections, gzip, hashlib, json, os, re, sys, time

sys.path.insert(0, "/home/user/worldfill")
import build_regional as BR     # noqa: E402
import build_hazards as BH      # noqa: E402  tables(), clean(), years_of()
import modpack as M             # noqa: E402
import wpdump as W              # noqa: E402

REPORT = "/home/user/worldfill/wars_report.json"
PACK_FILE = "events_wars.json.gz"
MAX_YEARS = 60
log = BR.log
PLACE = re.compile(r"\|\s*(?:place|location)\s*=\s*(.*?)(?=\n\s*\|\s*[a-z_0-9 ]+\s*=|\n\}\})", re.S | re.I)
CACHE = os.path.expanduser("~/.cache/wpdump/war_infoboxes.jsonl.gz")


def war_rows():
    with gzip.open(BH.LISTS, "rt", encoding="utf-8") as f:
        pages = [json.loads(l) for l in f]
    rows = []
    for pg in pages:
        if not re.match(r"List of wars", pg["title"]):
            continue
        for names, grid in BH.tables(pg["text"]):
            idx = {}
            for i, n in enumerate(names):
                for role, pat in (("start", r"^start"), ("end", r"^(finish|end)"), ("name", r"name|conflict"),
                                  ("won", r"victor"), ("lost", r"defeat")):
                    if role not in idx and re.search(pat, n):
                        idx[role] = i
            if "start" not in idx or "name" not in idx:
                continue
            bel = [i for i, n in enumerate(names) if "belligerent" in n]
            won = idx.get("won", bel[0] if bel else None)
            lost = idx.get("lost", bel[1] if len(bel) > 1 else None)
            for r in grid:
                def c(i):
                    return BH.clean(r[i]) if i is not None and i < len(r) else ("", [], [], None)
                rows.append({"page": pg["title"], "start": c(idx["start"]), "end": c(idx.get("end")),
                             "name": c(idx["name"]), "won": c(won), "lost": c(lost)})
    return rows


def main(dry=False):
    t0 = time.time()
    rows = war_rows()
    log(f"war rows: {len(rows):,}")
    arts = sorted({r["name"][1][0][0] for r in rows if r["name"][1]})
    log(f"reading {len(arts):,} war articles from the dump for their infobox place")
    box = {}
    if os.path.exists(CACHE):
        with gzip.open(CACHE, "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                box[r["title"]] = r["infobox"]
    need = [a for a in arts if a not in box]
    if need:
        texts = W.Wiki().texts(need, workers=2, progress=lambda d, n: log(f"  streams {d}/{n}"))
        with gzip.open(CACHE, "at", encoding="utf-8") as f:
            for t, (_final, text) in texts.items():
                i = text.find("{{Infobox")
                snip = text[i:i + 8000] if i >= 0 else ""
                box[t] = snip
                f.write(json.dumps({"title": t, "infobox": snip}, ensure_ascii=False) + "\n")
        del texts
    place_of = {}
    for t, snip in box.items():
        m = PLACE.search(snip)
        if m:
            place_of[t] = BH.clean(m.group(1))
    log(f"infobox place found for {len(place_of):,} of {len(arts):,}")
    places = BR.Places(W.Wiki(), BR.Polities(BR.Hyde()))
    st, out, seen, samples = collections.Counter(), [], set(), collections.defaultdict(list)
    for r in rows:
        ys = BH.years_of(r["start"][0])
        if not ys:
            st["no_year"] += 1
            continue
        start = ys[0]
        ye = BH.years_of(r["end"][0]) if r["end"][0] else None
        if re.search(r"ongoing|present", r["end"][0] or "", re.I):
            end = 2026
        else:
            end = ye[1] if ye and ye[1] >= start else (ys[1] if ys[1] >= start else start)
        if start < -3000 or start > 2026:
            st["out_of_range"] += 1
            continue
        art = r["name"][1][0][0] if r["name"][1] else None
        name = (W.norm(art) if art else r["name"][0])[:160]
        if len(name) < 6:
            st["no_name"] += 1
            continue
        key = (name.lower(), start)
        if key in seen:
            st["dupe_row"] += 1
            continue
        seen.add(key)
        best, how = None, ""
        pl = place_of.get(art) if art else None
        if pl:
            for target, alias in pl[1]:
                c = places.candidate(target, alias, start)
                if c and (best is None or c[0] < best[0]):
                    best = c
            for f in pl[2]:
                c = places.candidate(f, None, start)
                if c and (best is None or c[0] < best[0]):
                    best = c
            how = "infobox"
        if best is None:
            for side in ("lost", "won"):
                for target, alias in r[side][1][:3]:
                    c = places.candidate(target, alias, start)
                    if c and c[0] >= 3:
                        best, how = c, "side_" + side
                        break
                for f in r[side][2][:3]:
                    if best:
                        break
                    c = places.candidate(f, None, start)
                    if c and c[0] >= 3:
                        best, how = c, "side_" + side
                if best:
                    break
        if best is None:
            st["unplaced"] += 1
            if len(samples["unplaced"]) < 25:
                samples["unplaced"].append(f"{start}: {name}")
            continue
        rank, lat, lon, rad, chow, _t = best
        rad = max(int(rad), 120)                  # a war covers a region, even if placed at a town
        h = hashlib.sha1(f"war|{name}|{start}".encode()).hexdigest()[:10]
        e = {"id": f"wpw_{h}", "name": name, "start": start, "end": min(end, start + MAX_YEARS) + 1,
             "lat": round(float(lat), 5), "lon": round(float(lon), 5), "radiusKm": rad,
             "kind": "war", "effect": "note", "confidence": BR.REGIONAL}
        out.append(e)
        st["placed_" + how] += 1
        if len(samples[how]) < 10:
            samples[how].append(f"{start}-{end}: {name[:80]} -> {chow} r={rad}")
    log(f"placed {len(out):,} wars")
    # skip wars the mod already has as Wikidata war theatres (same words, overlapping years)
    theatres = [x for x in M.existing_events(exclude={PACK_FILE}) if x.get("kind") == "war"]
    tt = [(BR.toks(x.get("name")), x["_start"], x.get("end", x["_start"] + 1), x.get("name")) for x in theatres]
    kept, dup = [], []
    for e in out:
        et = BR.toks(e["name"])
        hit = next((n for t, s, en, n in tt if t and et and s <= e["end"] and e["start"] <= en
                    and (t <= et or et <= t or len(t & et) / len(t | et) >= 0.6)), None)
        if hit:
            dup.append((e["name"], hit))
        else:
            kept.append(e)
    # and anything already in the other packs (same words within the radius and a year)
    ex = BR.Existing(exclude=PACK_FILE)
    final = [e for e in kept if not ex.match(dict(e, kind="war"))]
    final.sort(key=lambda e: (e["start"], e["name"]))
    for e in final:
        M.check_event(e)
    report = {"seconds": round(time.time() - t0), "rows": len(rows), "articles": len(arts),
              "infobox_places": len(place_of), "stats": dict(sorted(st.items())), "placed": len(out),
              "already_war_theatres": len(dup), "already_other_pins": len(kept) - len(final),
              "installed": len(final),
              "installed_by_era": dict(sorted(collections.Counter(BR.era(e["start"]) for e in final).items())),
              "samples": samples, "theatre_duplicates_sample": dup[:40]}
    json.dump(report, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in report.items() if k not in ("samples", "theatre_duplicates_sample")},
                     indent=1, ensure_ascii=False))
    if dry:
        print("dry run: nothing written to the mod")
        return
    doc = {"id": "wikipedia_wars",
           "title": ("Wars from the Wikipedia 'List of wars' pages, placed by the war article's infobox "
                     "place, else by the defeated or victorious side's state that year. Regional news "
                     "only: never stoppable, never a town, never attacker spawn."),
           "source": "worldfill/build_wars.py", "sites": [],
           "comparedSources": [
               "English Wikipedia 'List of wars' pages and war articles' infobox place (dump 2026-10-01, CC BY-SA 4.0)",
               "Cliopatria v0.2.1 (a side's state extent in the start year) and HYDE 3.2.1 (its centre)",
           ],
           "rejected": ["Wars already in the mod as Wikidata war theatres (events_wikidata_more.json.gz)",
                        "Rows with no start year or no place; wars before 3000 BC"],
           "events": final}
    path = M.write_pack(PACK_FILE, doc)
    added = M.register(PACK_FILE, after="events_wikidata_more.json.gz")
    log(f"wrote {path} ({len(final)} wars); index.json {'updated' if added else 'already lists it'}")


if __name__ == "__main__":
    main(dry="--dry-run" in sys.argv)
