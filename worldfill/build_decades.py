#!/usr/bin/env python3
"""Step 6.4: events from the decade and century pages that only wiki_test/ had.

wiki_test/snapshot/pages.jsonl.gz (2023 revisions) holds 303 decade and century pages ("1640s",
"220s BC", "11th century BC") that the step-1/5 harvests never read: the mod was built from the
2,707 year pages of the 2026-10-01 dump. Their Events sections hold 3,238 lines. They go through
exactly the step-5 machinery (build_regional.build_events: placed by the line's own links, else by
region/state names learned from the pages' links; then every line already in the mod is left out),
into events_wikipedia_decades.json.gz.

    python3 build_decades.py --dry-run
    python3 build_decades.py
"""
import collections, gzip, json, re, sys, time

sys.path.insert(0, "/home/user/worldfill")
sys.path.insert(0, "/home/user/harvest")
import build_regional as BR  # noqa: E402
import modpack as M  # noqa: E402
import wpdump as W  # noqa: E402

SNAP = "/home/user/wiki_test/snapshot/pages.jsonl.gz"
DUMP_PAGES = BR.PAGE_CACHE
PACK = "events_wikipedia_decades.json.gz"
REPORT = "/home/user/worldfill/decades_report.json"


def years_for(title):
    m = re.match(r"^(\d+)s(?: \(decade\))?$", title)
    if m:
        a = int(m.group(1))
        return list(range(max(a, 1), a + 10))
    m = re.match(r"^(\d+)s BC$", title)
    if m:
        a = int(m.group(1))
        return list(range(-(a + 9), -a + 1)) if a else list(range(-9, 0))
    m = re.match(r"^(\d+)(?:st|nd|rd|th) century BC$", title)
    if m:
        c = int(m.group(1))
        return list(range(-c * 100, -c * 100 + 100))
    m = re.match(r"^(\d+)(?:st|nd|rd|th) century$", title)
    if m:
        c = int(m.group(1))
        return list(range((c - 1) * 100 + 1, c * 100 + 1))
    return None


MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
LEAD = re.compile(r"^(?:c\.\s*|ca\.\s*|circa\s*|by\s+|around\s+)?(?P<y>\d{1,4})(?P<s>s)?\s*(?P<era>BC|BCE|AD|CE)?"
                  r"(?:\s*[–-]\s*(?:c\.\s*)?\d{1,4}s?\s*(?:BC|BCE|AD|CE)?)?\s*[:–—-]\s*")
LEAD_DATE = re.compile(r"^(?:(?:" + MONTHS + r")\s+\d{1,2}(?:\s*[–-]\s*\d{1,2})?,?\s+|\d{1,2}\s+(?:" + MONTHS + r")\s+)"
                       r"(?P<y>\d{3,4})\s*[:–—-]\s*")
_Y = r"(?:\[\[)?(?:c\.\s*|ca\.\s*|circa\s*)?\d{1,4}s?(?:\s*(?:BC|BCE|AD|CE))?(?:\]\])?"
RAW_LEAD = re.compile(r"^(?:c\.\s*|ca\.\s*|circa\s*|by\s+|around\s+)?" + _Y + r"(?:\s*[–-]\s*" + _Y + r")?\s*[:–—-]\s*")
RAW_DATE = re.compile(r"^(?:\[\[)?(?:(?:" + MONTHS + r")\s+\d{1,2}(?:\s*[–-]\s*\d{1,2})?|\d{1,2}\s+(?:" + MONTHS + r"))(?:\]\])?,?\s+"
                      r"(?:\[\[)?\d{3,4}(?:\]\])?\s*[:–—-]\s*")
INJECTED = re.compile(r"^(?:\d{3,4} AD|\d{1,4} BC) – ")


def plain(s):
    t = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    return re.sub(r"'{2,}|<[^>]+>", "", t).strip()


def explicit_years(text, years):
    """Rewrite each bullet so its own year is explicit ("AD 1086 – ..."), as the year-page
    harvester expects; drop bullets that give no year of their own (a decade or century page's
    first year would be up to 99 years off)."""
    lo, hi = min(years), max(years)
    bc_page = hi < 0
    out, st = [], collections.Counter()
    for line in text.split("\n"):
        if not line.startswith("*"):
            out.append(line)
            continue
        body = line.lstrip("*").strip()
        t = plain(body)
        m = LEAD.match(t) or LEAD_DATE.match(t)
        y = None
        if m:
            y = int(m.group("y"))
            era = (m.groupdict().get("era") or "").upper()
            if era in ("BC", "BCE") or (bc_page and era not in ("AD", "CE")):
                y = -y - (9 if m.groupdict().get("s") else 0)
            if not (lo - 1 <= y <= hi + 1):
                y = None
        if y is None:
            st["no_own_year"] += 1
            continue
        # keep the wiki links of the rest: cut the same prefix off the raw body (links allowed)
        rm = RAW_LEAD.match(body) or RAW_DATE.match(body)
        raw_rest = body[rm.end():] if rm else plain(body)[m.end():]
        tag = f"{y:03d} AD" if y > 0 else f"{-y} BC"      # the forms harvest_run.bullet_year reads
        out.append(f"* {tag} – {raw_rest}")
        st["with_year"] += 1
    return "\n".join(out), st


def main(dry=False):
    t0 = time.time()
    have = {json.loads(line)["title"] for line in gzip.open(DUMP_PAGES, "rt", encoding="utf-8")}
    pages, texts, skipped = {}, {}, []
    year_stats = collections.Counter()
    for line in gzip.open(SNAP, "rt", encoding="utf-8"):
        d = json.loads(line)
        if d["title"] in have:
            continue
        ys = years_for(d["title"])
        if not ys:
            skipped.append(d["title"])
            continue
        pages[d["title"]] = ys
        texts[d["title"]], yst = explicit_years(d["wikitext"], ys)
        year_stats.update(yst)
    BR.log(f"{len(pages)} decade/century pages not in the dump harvest; skipped {len(skipped)}: {skipped[:8]}")
    v2 = set()
    with gzip.open(BR.V2_RAW, "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            v2.add((r["name"].lower()[:110], r["start"]))
    places = BR.Places(W.Wiki(), BR.Polities(BR.Hyde()))
    out, st, samples = BR.build_events(pages, texts, v2, places)
    ex = BR.Existing(exclude=PACK) if "exclude" in BR.Existing.__init__.__code__.co_varnames else BR.Existing()
    kept, why = [], collections.Counter()
    for e in out:
        hit = ex.match(e)
        if hit:
            why[f"{hit[0]} / {hit[3]}"] += 1
        else:
            kept.append(e)
    kept.sort(key=lambda e: (e["start"], e["name"]))
    for e in kept:
        e["id"] = e["id"].replace("wpr_", "wpd_")
        e["name"] = INJECTED.sub("", e["name"]).strip()
        e["name"] = re.sub(r"\.?\s*(?:thumb|thumbnail|upright|frame)\|.*$", ".", e["name"]).strip(" .") \
            if re.search(r"(?:thumb|thumbnail|upright|frame)\|", e["name"]) else e["name"]
        M.check_event(e)
    rep = {"seconds": round(time.time() - t0), "pages": len(pages), "bullets": dict(year_stats),
           "stats": dict(sorted(st.items())),
           "placed": len(out), "already_in_mod": len(out) - len(kept), "installed": len(kept),
           "duplicates_by_pack": dict(why.most_common(12)),
           "installed_by_confidence": dict(collections.Counter(e["confidence"] for e in kept)),
           "installed_by_era": dict(sorted(collections.Counter(BR.era(e["start"]) for e in kept).items())),
           "examples": [f"{e['start']}: {e['name'][:100]} ({e['confidence']}, r={e['radiusKm']})"
                        for e in kept[:: max(1, len(kept) // 12)]][:12]}
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    if dry:
        return
    for e in kept:
        e.pop("placedBy", None)
        e.pop("place", None)
    doc = {"id": "wikipedia_decades",
           "title": ("Events from English Wikipedia decade and century pages (2023 revisions kept in "
                     "wiki_test/) that the year-page harvests never read, placed like the regional pack: "
                     "a site through the article's coordinates, else the region or state named (news "
                     "only). Lines already in the mod are left out. Overlay only; not towns; not attackers."),
           "source": "English Wikipedia decade/century pages, 2023 revisions (CC BY-SA 4.0); worldfill/build_decades.py",
           "sites": [], "events": kept}
    path = M.write_pack(PACK, doc)
    M.register(PACK, after="events_wikipedia_regional.json.gz")
    json.dump(rep, open(REPORT, "w"), ensure_ascii=False, indent=1)
    print(f"wrote {path} ({len(kept)} events)")


if __name__ == "__main__":
    main(dry="--dry-run" in sys.argv)
