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

def bucket(cls,lo,hi,coord=True,dateprop="P580"):
    extra="?x wdt:P625 ?l ." if coord else ""
    return f"SELECT (COUNT(?x) AS ?n) WHERE {{ ?x wdt:P31 wd:{cls} . {extra} ?x wdt:{dateprop} ?s . FILTER(YEAR(?s)>={lo} && YEAR(?s)<{hi}) }}"

eras=[(-3000,-1000,"3000-1001 BC"),(-1000,-1,"1000 BC-1 AD"),(1,1000,"1-1000 AD"),
      (1000,1500,"1000-1500"),(1500,1800,"1500-1800"),(1800,1900,"1800-1900"),(1900,2030,"1900-now")]

print("=== BATTLES  (P31=Q178561, with coordinate + start date) ===")
for lo,hi,lab in eras:
    print(f"  {lab:16} {cnt(bucket('Q178561',lo,hi))}"); time.sleep(4)

print("\n=== WARS  (P31=Q124734, with start date; coords rare) ===")
for lo,hi,lab in eras:
    print(f"  {lab:16} {cnt(bucket('Q124734',lo,hi,coord=False))}"); time.sleep(4)
