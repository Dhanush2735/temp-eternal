#!/usr/bin/env python3
"""Step 6 clean-up: delete the raw data whose content is now in the mod (the user's plan, turn 15).

Kept: code (.py, .sh), docs (.md), files a doc links to by name, and one 59 KB page list the
builders need (harvest/events_v2_raw.jsonl.pages.json). Deleted: harvest/, wiki_test/ and survey/
data files, and the downloads in ~/.cache (srcdata, wpdump); the JDK and Gradle caches stay
(tools, needed to build the mod). Writes worldfill/CLEANUP_STEP6.md first, then deletes with --do.

    python3 cleanup_step6.py        # report only
    python3 cleanup_step6.py --do   # report, then delete
"""
import os, re, shutil, sys

HOME = "/home/user"
KEEP_EXT = (".py", ".sh", ".md")
KEEP_NAMES = {"events_v2_raw.jsonl.pages.json"}
WHERE = {
    "harvest": ("Wikipedia year-page harvests v1/v2: raw, merged, partial and backup event files, geo "
                "caches, logs, year lists.",
                "v2 is in the mod as events_wikipedia.json.gz (19,368 events; the other 2,624 of its "
                "21,992 were already in the mod, see harvest/FIXES.md); v1 was replaced by v2."),
    "wiki_test": ("2023 snapshot of 3,010 Wikipedia year, decade and century pages, plus per-year test files.",
                  "The 2,707 year pages were rebuilt from the newer 2026 dump (events_wikipedia*, births and "
                  "deaths in famous_people.json.gz); the 303 decade/century pages went in this step as "
                  "events_wikipedia_decades.json.gz (1,763 new events; 839 already in the mod; lines with "
                  "no year of their own left out)."),
    "survey": ("Census and source-survey working files: raw and post-processed census events, geo "
               "caches, work files, Wikidata samples, logs.",
               "Measurements only; their results are written in survey/*.md. The events they counted are "
               "the year-page lines and Wikidata items already in the mod."),
    ".cache/srcdata": ("Downloaded sources: UCDP GED 25.1, plague, Smithsonian volcanoes, NOAA quakes/"
                       "tsunamis/volcanoes, a land mask.",
                       "UCDP -> events_ucdp.json.gz (this step); the rest -> events_hazards.json.gz (step 5)."),
    ".cache/wpdump": ("Offline Wikipedia: wp.sqlite index (2.7 GB), dump index files, cached year pages, "
                      "list pages, war and state infoboxes.",
                      "Year pages -> events_wikipedia_regional, famous_people; list pages -> events_hazards; "
                      "war infoboxes -> events_wars; state infoboxes -> polity_facts.json.gz."),
}


def doc_names(root):
    names = set()
    for dp, _dn, fn in os.walk(root):
        for f in fn:
            if f.endswith(".md"):
                try:
                    names |= set(re.findall(r"[\w.\-]+\.(?:png|csv|json|svg|html)", open(os.path.join(dp, f), encoding="utf-8").read()))
                except Exception:
                    pass
    return names


def candidates():
    out = []
    for top in ("harvest", "wiki_test", "survey"):
        root = os.path.join(HOME, top)
        linked = doc_names(root)
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d != "__pycache__"]
            for f in fn:
                p = os.path.join(dp, f)
                if f.endswith(KEEP_EXT) or f in KEEP_NAMES or f in linked:
                    continue
                out.append((top, p, os.path.getsize(p)))
    for sub in ("srcdata", "wpdump"):
        p = os.path.join(HOME, ".cache", sub)
        if os.path.exists(p):
            size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _d, fn in os.walk(p) for f in fn)
            out.append((".cache/" + sub, p, size))
    return out


def main(do=False):
    c = candidates()
    by = {}
    for top, p, s in c:
        n, b = by.get(top, (0, 0))
        by[top] = (n + 1, b + s)
    lines = ["# Step 6 clean-up: raw data deleted after it went into the mod", "",
             "The user's plan (turn 15): put the data already in the workspace into the mod, then delete it.",
             "Every folder below was checked against the mod first. Code, docs and files a doc links to stay.", "",
             "| Folder | Files | Size | What it was | Where it is now |", "|---|---:|---:|---|---|"]
    for top, (n, b) in by.items():
        what, where = WHERE[top]
        lines.append(f"| `{top}/` | {n} | {b / 1e6:,.1f} MB | {what} | {where} |")
    saved = sum(b for t, (n, b) in by.items() if not t.startswith(".cache"))
    lines += ["", f"Saved space freed (workspace snapshot): about {saved / 1e6:.1f} MB. "
              f"Hidden cache freed (not in snapshots): {sum(b for t, (n, b) in by.items() if t.startswith('.cache')) / 1e9:.2f} GB.", "",
              "Consequence: the step-1 to step-6 builders cannot be re-run without downloading their sources "
              "again (the Wikipedia dump index takes about 11 minutes to rebuild with worldfill/wpdump.py build).", "",
              "## Files deleted", ""]
    for top, p, s in sorted(c, key=lambda x: x[1]):
        lines.append(f"- `{p.replace(HOME + '/', '~/')}` ({s / 1e6:.2f} MB)")
    open(os.path.join(HOME, "worldfill", "CLEANUP_STEP6.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    for top, (n, b) in by.items():
        print(f"{top:16} {n:4} files {b / 1e6:10.1f} MB")
    if not do:
        print("report written; nothing deleted (use --do)")
        return
    for top, p, s in c:
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
    for top in ("harvest", "wiki_test", "survey"):
        for dp, dn, fn in sorted(os.walk(os.path.join(HOME, top)), key=lambda x: -len(x[0])):
            if not os.listdir(dp) and dp != os.path.join(HOME, top):
                os.rmdir(dp)
    print("deleted")


if __name__ == "__main__":
    main(do="--do" in sys.argv)
