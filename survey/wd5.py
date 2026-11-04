import subprocess,time,urllib.parse,json
UA="EternalEngineResearch/1.0 (survey; contact: local research)"
def cnt(q):
    url="https://query.wikidata.org/sparql?"+urllib.parse.urlencode({"query":q,"format":"json"})
    for _ in range(3):
        r=subprocess.run(["curl","-s","--max-time","180","-A",UA,"-H","Accept: application/sparql-results+json",url],capture_output=True,text=True)
        try:
            b=json.loads(r.stdout)["results"]["bindings"]; return b[0]["n"]["value"] if b else "??"
        except Exception: time.sleep(6)
    return "FAILED"
print("=== TREATIES (P31=Q131361) ===")
print("  total                    :",cnt("SELECT (COUNT(?x) AS ?n) WHERE { ?x wdt:P31 wd:Q131361 }")); time.sleep(4)
print("  with a date (P580/P585)  :",cnt("SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P31 wd:Q131361 . { ?x wdt:P580 ?s } UNION { ?x wdt:P585 ?s } }")); time.sleep(4)
print("  with date AND coordinate :",cnt("SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P31 wd:Q131361 . ?x wdt:P625 ?l . { ?x wdt:P580 ?s } UNION { ?x wdt:P585 ?s } }")); time.sleep(5)
print("\n=== EPIDEMICS (P31=Q4426883) / PANDEMICS (P31=Q17000908) ===")
print("  epidemics total          :",cnt("SELECT (COUNT(?x) AS ?n) WHERE { ?x wdt:P31 wd:Q4426883 }")); time.sleep(4)
print("  epidemics w/ date        :",cnt("SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P31 wd:Q4426883 . { ?x wdt:P580 ?s } UNION { ?x wdt:P585 ?s } }")); time.sleep(4)
print("  epidemics date+coord     :",cnt("SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P31 wd:Q4426883 . ?x wdt:P625 ?l . { ?x wdt:P580 ?s } UNION { ?x wdt:P585 ?s } }")); time.sleep(4)
print("  epidemics w/ location P276:",cnt("SELECT (COUNT(?x) AS ?n) WHERE { ?x wdt:P31 wd:Q4426883 . ?x wdt:P276 ?p }")); time.sleep(4)
print("  pandemics total          :",cnt("SELECT (COUNT(?x) AS ?n) WHERE { ?x wdt:P31 wd:Q17000908 }")); time.sleep(4)
print("  pandemics date+location  :",cnt("SELECT (COUNT(?x) AS ?n) WHERE { ?x wdt:P31 wd:Q17000908 . ?x wdt:P276 ?p . { ?x wdt:P580 ?s } UNION { ?x wdt:P585 ?s } }"))
