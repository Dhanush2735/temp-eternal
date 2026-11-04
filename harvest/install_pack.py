#!/usr/bin/env python3
"""Install the postprocessed Wikipedia pack into the mod, without doubling events the mod
already has.

A Wikipedia bullet is the same event as an existing pin (events_world.json from Wikidata,
the curated events.json, the region packs) when
  * every content word of the pin's name appears in the bullet's text, within 60 km and
    +-1 year ("Battle of Landen" vs "Nine Years' War - Battle of Landen: William III ..."), or
  * both are disasters at the same spot (<= 1.5 km) in the same year +-1 ("An earthquake
    of magnitude 6.6 strikes southern Taiwan" vs "2016 Kaohsiung earthquake"), or both are
    battles / sieges there and share a word ("Battle of Buqqar Ridge" vs "Battle of El
    Buggar Ridge").
The existing pin is kept (it has the cleaner name and real start/end years); the bullet is
left out and listed in install_report.json (next to the input pack).

Usage: python3 install_pack.py <postprocessed.json> [--dry-run]
"""
import collections, json, os, re, sys

sys.path.insert(0, "/home/user/worldfill")
import modpack as M        # noqa: E402

PACK_FILE = "events_wikipedia.json.gz"   # gzipped; HistoryGazetteer reads .gz packs

STOP = set("battle siege of the and in at on a an treaty sack massacre first second third".split())
DISASTER_WORDS = re.compile(r"earthquake|eruption|tsunami|flood|volcan|typhoon|hurricane|cyclone", re.I)


def toks(s):
    """Content words, Unicode-aware ("Brüx" is one word, not "br" + "x")."""
    return {w for w in re.findall(r"[^\W\d_]+", (s or "").lower()) if len(w) > 2 and w not in STOP}


def kind_class(kind, name):
    if kind in ("battle", "siege"):
        return "military"
    if kind == "disaster" or DISASTER_WORDS.search(name or ""):
        return "disaster"
    return None


def main(src, dry=False):
    report_path = os.path.join(os.path.dirname(os.path.abspath(src)), "install_report.json")
    doc = json.load(open(src, encoding="utf-8"))
    events = doc["events"]
    # A war theatre (kind "war") is a background overlay over a whole region and many years, not
    # the same event as a bullet about one battle or treaty inside it: never dedupe against it.
    existing = [x for x in M.existing_events(exclude={PACK_FILE}) if x.get("kind") != "war"]
    grid = M.Grid(existing)
    for x in existing:
        x["_toks"] = toks(x.get("name"))
        x["_class"] = kind_class(x.get("kind"), x.get("name"))

    kept, dropped = [], []
    why = collections.Counter()
    for e in events:
        et = toks(e["name"])
        ec = kind_class(e["kind"], e["name"])
        hit = None
        for x in grid.near(e["lat"], e["lon"]):
            if abs(x["_start"] - e["start"]) > 1:
                continue
            d = M.haversine_km(e["lat"], e["lon"], x["lat"], x["lon"])
            if x["_toks"] and d <= 60 and x["_toks"] <= et:
                hit = (x, "same name"); break
            # Same spot and kind: an earthquake is the same earthquake; two battles must
            # also share a word (the 1812 Siege of Badajoz is not the Battle of Almagro).
            if d <= 1.5 and ec and ec == x["_class"] and (ec == "disaster" or (x["_toks"] & et)):
                hit = (x, "same spot, same kind"); break
        if hit:
            x, reason = hit
            why[(x["_pack"], reason)] += 1
            dropped.append({"wikipedia": e["name"][:160], "year": e["start"], "kept_pin": x.get("id"),
                            "kept_pack": x["_pack"], "kept_name": x.get("name"), "reason": reason})
        else:
            kept.append(e)

    for e in kept:
        M.check_event(e)
    out = dict(doc)
    out["title"] = ("Events harvested from English Wikipedia year, decade and century pages "
                    "(3000 BC to AD 2026), geocoded via Wikidata. Overlay only. Not towns. "
                    "Not attacker spawn.")
    out["comparedSources"] = [
        "English Wikipedia year pages, decade/century/millennium pages (CC BY-SA 4.0), revisions "
        "frozen in wiki_test/snapshot (latest 2026-10-11)",
        "Place coordinates resolved through Wikidata P625, with P276/P131 fallback",
        "Harvester v2: every year looked up on its real page; one year convention; Births/Deaths "
        "and people/reference sections skipped (harvest/FIXES.md)",
    ]
    out["rejected"] = list(doc.get("rejected", [])) + [
        "Bullets under Births, Deaths, Significant people, References and similar sections",
        "Events already in the mod (same event within 60 km and one year in events_world.json, "
        "events.json or a region pack)",
        "Events dated after 2026 (predicted and scheduled)",
    ]
    out["events"] = kept
    report = {
        "source": src, "events_in": len(events), "duplicates_left_out": len(dropped),
        "installed": len(kept),
        "duplicates_by_pack_and_reason": {f"{p} / {r}": n for (p, r), n in why.most_common()},
        "kinds_installed": dict(collections.Counter(e["kind"] for e in kept).most_common()),
        "duplicates": dropped,
    }
    json.dump(report, open(report_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != "duplicates"}, indent=1, ensure_ascii=False))
    if dry:
        print("dry run: nothing written to the mod")
        return
    path = M.write_pack(PACK_FILE, out)
    added = M.register(PACK_FILE, after="events_world.json")
    print(f"wrote {path} ({len(kept)} events); index.json {'updated' if added else 'already lists it'}")


if __name__ == "__main__":
    main(sys.argv[1], dry="--dry-run" in sys.argv)
