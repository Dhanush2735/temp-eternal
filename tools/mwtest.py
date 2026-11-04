import json, urllib.parse, urllib.request, re
UA = "EternalEngineCrossCheck/1.0 (research)"
p = {"action": "query", "format": "json", "generator": "categorymembers",
     "gcmtitle": "Category:Battles in 1619", "gcmlimit": "20", "gcmnamespace": "0",
     "prop": "coordinates|revisions", "rvslots": "main", "rvprop": "content", "colimit": "max"}
url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(p)
req = urllib.request.Request(url, headers={"User-Agent": UA})
with urllib.request.urlopen(req, timeout=60) as r:
    d = json.loads(r.read().decode())
pages = d.get("query", {}).get("pages", {})
print("pages:", len(pages))
n = 0
for _, pg in pages.items():
    co = pg.get("coordinates")
    txt = (pg.get("revisions", [{}])[0].get("slots", {}).get("main", {}).get("*", "") or "")
    m = re.search(r"\|\s*date\s*=\s*([^\n]{0,90})", txt)
    if co and m:
        n += 1
        print(f"  {pg['title'][:34]:36} {co[0]['lat']:8.3f},{co[0]['lon']:9.3f}  date: {m.group(1)[:60]}")
print("with coords+date:", n, "of", len(pages))
