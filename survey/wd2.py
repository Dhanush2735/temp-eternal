import subprocess,json,time,urllib.parse
UA="EternalEngineResearch/1.0 (survey; contact: local research)"
def sparql(q,label):
    url="https://query.wikidata.org/sparql?"+urllib.parse.urlencode({"query":q,"format":"json"})
    r=subprocess.run(["curl","-s","--max-time","180","-A",UA,"-H","Accept: application/sparql-results+json",url],capture_output=True,text=True)
    out=r.stdout.strip()
    if not out: print(f"  {label:42} -> EMPTY RESPONSE"); return
    try: d=json.loads(out)
    except Exception: print(f"  {label:42} -> not json: {out[:120]}"); return
    if 'results' not in d: print(f"  {label:42} -> no results key: {out[:120]}"); return
    rows=d["results"]["bindings"]
    print(f"  {label:42} -> {rows[0]['n']['value'] if rows else '??'}")

print("=== simple, non-transitive counts ===")
sparql("SELECT (COUNT(?x) AS ?n) WHERE { ?x wdt:P31 wd:Q198 . ?x wdt:P625 ?l . ?x wdt:P580 ?s }",
       "P31=Q198 (battle) + coord + start")
time.sleep(4)
sparql("SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P607 ?c . ?x wdt:P625 ?l . ?x wdt:P580 ?s }",
       "has P607 conflict + coord + start")
time.sleep(4)
sparql("SELECT (COUNT(?x) AS ?n) WHERE { ?x wdt:P31 wd:Q178561 . ?x wdt:P625 ?l }",
       "P31=Q178561 (battle) + coord")
time.sleep(4)
sparql("SELECT (COUNT(?x) AS ?n) WHERE { ?x wdt:P31 wd:Q198 }",
       "P31=Q198 total (no filters)")
time.sleep(4)
sparql("SELECT (COUNT(?x) AS ?n) WHERE { ?x wdt:P31 wd:Q124734 . }",
       "P31=Q124734 (war) total")
