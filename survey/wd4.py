import subprocess,json,time,urllib.parse
UA="EternalEngineResearch/1.0 (survey; contact: local research)"
def cnt(q):
    url="https://query.wikidata.org/sparql?"+urllib.parse.urlencode({"query":q,"format":"json"})
    for _ in range(3):
        r=subprocess.run(["curl","-s","--max-time","180","-A",UA,"-H","Accept: application/sparql-results+json",url],capture_output=True,text=True)
        try:
            d=json.loads(r.stdout); b=d["results"]["bindings"]
            return b[0]["n"]["value"] if b else "??"
        except Exception: time.sleep(6)
    return "FAILED"
print("=== which date property do battles actually use? (P31=Q178561 + coord) ===")
print("  total w/ coord            :", cnt("SELECT (COUNT(?x) AS ?n) WHERE { ?x wdt:P31 wd:Q178561 . ?x wdt:P625 ?l }")); time.sleep(4)
print("  ...w/ P580 (start time)   :", cnt("SELECT (COUNT(?x) AS ?n) WHERE { ?x wdt:P31 wd:Q178561 . ?x wdt:P625 ?l . ?x wdt:P580 ?s }")); time.sleep(4)
print("  ...w/ P585 (point in time):", cnt("SELECT (COUNT(?x) AS ?n) WHERE { ?x wdt:P31 wd:Q178561 . ?x wdt:P625 ?l . ?x wdt:P585 ?s }")); time.sleep(4)
print("  ...w/ P580 OR P585        :", cnt("SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P31 wd:Q178561 . ?x wdt:P625 ?l . { ?x wdt:P580 ?s } UNION { ?x wdt:P585 ?s } }")); time.sleep(4)
print("\n=== era breakdown using P580 OR P585, with coordinate ===")
for lo,hi,lab in [(-3000,-1000,"3000-1001 BC"),(-1000,-1,"1000 BC-1 AD"),(1,1000,"1-1000 AD"),(1000,1500,"1000-1500"),(1500,1800,"1500-1800"),(1800,1900,"1800-1900"),(1900,2030,"1900-now")]:
    q=f"SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE {{ ?x wdt:P31 wd:Q178561 . ?x wdt:P625 ?l . {{ ?x wdt:P580 ?s }} UNION {{ ?x wdt:P585 ?s }} FILTER(YEAR(?s)>={lo} && YEAR(?s)<{hi}) }}"
    print(f"  {lab:16} {cnt(q)}"); time.sleep(4)
