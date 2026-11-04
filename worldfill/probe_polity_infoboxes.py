#!/usr/bin/env python3
"""Measure what Wikipedia's own state articles offer for the 0% categories.

For every Cliopatria state in world_rulers.json.gz (Wikidata id -> enwiki article via the
dump's page_props), read the article's infobox from the 2026-10-01 dump and count how often
it names languages, religion, a capital and rulers (leader1..N with year_leader1..N).
Caches the infobox text in ~/.cache/wpdump/polity_infoboxes.jsonl.gz (reused by the build).
Writes worldfill/polity_infobox_probe.json.
"""
import collections, gzip, json, os, re, sqlite3, sys

sys.path.insert(0, "/home/user/worldfill")
import wpdump as W  # noqa: E402

RES = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/world_rulers.json.gz"
CACHE = os.path.expanduser("~/.cache/wpdump/polity_infoboxes.jsonl.gz")
OUT = "/home/user/worldfill/polity_infobox_probe.json"
FIELDS = {
    "languages": r"(?:common_languages|official_languages|languages|language)",
    "religion": r"(?:religion|state_religion|official_religion)",
    "capital": r"(?:capital|capital_exile)",
    "leader": r"(?:leader\d+|monarch\d*|king\d*|ruler\d*)",
    "leader_years": r"(?:year_leader\d+)",
    "government": r"(?:government_type|government)",
}


def field(box, pat):
    m = re.search(r"\n\s*\|\s*" + pat + r"\s*=\s*([^\n]*(?:\n(?!\s*\|)[^\n]*)*)", box, re.I)
    v = m.group(1).strip() if m else ""
    return v if re.search(r"\w", re.sub(r"<!--.*?-->", "", v)) else ""


def main():
    w = json.load(gzip.open(RES, "rt"))
    pols = w["polities"]
    con = sqlite3.connect("file:" + W.DB + "?mode=ro", uri=True)
    title_of = {}
    for name, qid in pols:
        if not qid:
            continue
        r = con.execute("SELECT t.title FROM props p JOIN titles t ON t.page_id = p.page_id "
                        "WHERE p.qid = ? LIMIT 1", (qid,)).fetchone()
        if r:
            title_of[qid] = r[0]
    box = {}
    if os.path.exists(CACHE):
        for line in gzip.open(CACHE, "rt", encoding="utf-8"):
            d = json.loads(line)
            box[d["title"]] = d["infobox"]
    need = sorted(set(title_of.values()) - set(box))
    if need:
        got = W.Wiki().texts(need, workers=2, progress=lambda d, n: W.log(f"  streams {d}/{n}"))
        with gzip.open(CACHE, "at", encoding="utf-8") as f:
            for t, (_final, text) in got.items():
                i = text.find("{{Infobox")
                snip = text[i:i + 12000] if i >= 0 else ""
                box[t] = snip
                f.write(json.dumps({"title": t, "infobox": snip}, ensure_ascii=False) + "\n")
    cnt, n_leaders, examples = collections.Counter(), 0, {}
    for qid, t in title_of.items():
        b = box.get(t, "")
        if not b:
            cnt["no_infobox"] += 1
            continue
        cnt["with_infobox"] += 1
        for k, pat in FIELDS.items():
            v = field(b, pat)
            if v:
                cnt[k] += 1
                examples.setdefault(k, (t, v[:120]))
        n_leaders += len(re.findall(r"\n\s*\|\s*leader\d+\s*=\s*\S", b))
    rep = {"states": len(pols), "with_wikidata_and_enwiki_article": len(title_of),
           "counts": dict(cnt), "leader_entries_total": n_leaders, "examples": examples}
    json.dump(rep, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
