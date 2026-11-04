import subprocess,json,time,urllib.parse
UA="EternalEngineResearch/1.0 (survey; contact: local research)"
def sparql(q,label):
    url="https://query.wikidata.org/sparql?"+urllib.parse.urlencode({"query":q,"format":"json"})
    r=subprocess.run(["curl","-s","--max-time","120","-A",UA,"-H","Accept: application/sparql-results+json",url],capture_output=True,text=True)
    try:
        d=json.loads(r.stdout)
        rows=d.get("results",{}).get("bindings",[])
        print(f"  {label:44} -> {rows[0]['n']['value'] if rows else '??'}")
    except Exception as e:
        print(f"  {label:44} -> FAILED ({r.stdout[:110]})")

# battles (Q198) with coordinate + start time, by millennium bucket
for lo,hi,lab in [(-3000,-2000,"3000-2001 BC"),(-2000,-1000,"2000-1001 BC"),(-1000,-1,"1000 BC-1 AD"),(1,1000,"1-1000 AD"),(1000,1500,"1000-1500"),(1500,1800,"1500-1800"),(1800,1900,"1800-1900"),(1900,2030,"1900-now")]:
    q=f"""SELECT (COUNT(?x) AS ?n) WHERE {{
      ?x wdt:P31/wdt:P279* wd:Q198 .
      ?x wdt:P625 ?loc . ?x wdt:P580 ?st .
      FILTER(YEAR(?st)>={lo} && YEAR(?st)<{hi}) }}"""
    sparql(q,f"battles w/ coord+date {lab}"); time.sleep(3)
