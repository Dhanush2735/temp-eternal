import subprocess,time,urllib.parse,json
UA="EternalEngineResearch/1.0 (survey; contact: local research)"
def cnt(q,label=None):
    url="https://query.wikidata.org/sparql?"+urllib.parse.urlencode({"query":q,"format":"json"})
    for _ in range(3):
        r=subprocess.run(["curl","-s","--max-time","180","-A",UA,"-H","Accept: application/sparql-results+json",url],capture_output=True,text=True)
        try:
            b=json.loads(r.stdout)["results"]["bindings"]
            v=b[0]["n"]["value"] if b else "??"
            if label: print(f"  {label:44} {v}")
            return v
        except Exception: time.sleep(6)
    if label: print(f"  {label:44} FAILED")
    return "FAILED"

print("=== resolve the real classes ===")
cnt("""SELECT (COUNT(?s) AS ?n) WHERE { ?s wdt:P31/rdfs:label "treaty"@en }""","items typed 'treaty' (any class)")
time.sleep(4)
cnt("""SELECT (COUNT(?s) AS ?n) WHERE { ?s wdt:P31/rdfs:label "epidemic"@en }""","items typed 'epidemic' (any class)")
time.sleep(4)
cnt("""SELECT (COUNT(?s) AS ?n) WHERE { ?s wdt:P31/rdfs:label "pandemic"@en }""","items typed 'pandemic' (any class)")
time.sleep(4)
cnt("""SELECT (COUNT(?s) AS ?n) WHERE { ?s wdt:P31/rdfs:label "siege"@en }""","items typed 'siege' (any class)")
time.sleep(5)
print("\n=== the useful versions ===")
cnt("""SELECT (COUNT(DISTINCT ?s) AS ?n) WHERE { ?s wdt:P31/rdfs:label "treaty"@en . { ?s wdt:P580 ?d } UNION { ?s wdt:P585 ?d } }""","treaties WITH a date")
time.sleep(4)
cnt("""SELECT (COUNT(DISTINCT ?s) AS ?n) WHERE { ?s wdt:P31/rdfs:label "treaty"@en . ?s wdt:P276 ?p . { ?s wdt:P580 ?d } UNION { ?s wdt:P585 ?d } }""","treaties WITH date + location")
time.sleep(4)
cnt("""SELECT (COUNT(DISTINCT ?s) AS ?n) WHERE { ?s wdt:P31/rdfs:label "epidemic"@en . { ?s wdt:P580 ?d } UNION { ?s wdt:P585 ?d } }""","epidemics WITH a date")
time.sleep(4)
cnt("""SELECT (COUNT(DISTINCT ?s) AS ?n) WHERE { ?s wdt:P31/rdfs:label "epidemic"@en . ?s wdt:P276 ?p . { ?s wdt:P580 ?d } UNION { ?s wdt:P585 ?d } }""","epidemics WITH date + location")
