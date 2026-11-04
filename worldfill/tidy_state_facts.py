"""Step 8: clean language and faith items in history/polity_facts.json.gz ("initially Latin" -> "Latin",
"Predominantly Arabic" -> "Arabic"; "Latin French" (a merged infobox item) -> "French", "Latin")."""
import gzip
import io, json, re, sys, os
sys.path.insert(0, '/home/user/worldfill')
import modpack as M
F = f"{M.HISTORY}/polity_facts.json.gz"
d = json.load(gzip.open(F, "rt", encoding="utf-8"))
QUAL = re.compile(r"(?i)^(initially|predominantly|mainly|mostly|officially|de facto|later|increasingly|primarily|largely|chiefly|also|plus|and|official|unofficial|then)\s+")
fixed = 0
for p in d["polities"]:
    for key in ("lang", "rel"):
        items = p.get(key)
        if not items:
            continue
        out = []
        for x in items:
            y = x
            if re.search(r"(?i)as well or instead|see below|various|several|list|^and$|^or$", y):
                continue
            for _ in range(3):
                y = QUAL.sub("", y).strip(" ,;:")
            y = re.sub(r"(?i)\s+(language|languages)$", "", y)
            if not y or not re.match(r"^[A-ZÀ-ÖØ-Þ]", y) or len(y) > 40:
                continue
            if y not in out:
                out.append(y)
        if "Latin French" in out:
            out = [x for x in out if x != "Latin French"]
            out = ["French"] + out + (["Latin"] if "Latin" not in out else [])
        if out != items:
            fixed += 1
            if out:
                p[key] = out
            else:
                p.pop(key)
with open(F + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
    json.dump(d, fh, ensure_ascii=False, separators=(",", ":"))
json.load(gzip.open(F + ".tmp", "rt", encoding="utf-8"))
os.replace(F + ".tmp", F)
by = {p['q']: p for p in d['polities']}
print('entries tidied', fixed)
for q in ('Q2277', 'Q858', 'Q70972', 'Q145'):
    print(q, by[q].get('lang'), by[q].get('rel'))
print('UK heads:', [r[:4] for r in by['Q145']['head']])
