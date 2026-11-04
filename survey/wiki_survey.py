import json,subprocess,time,sys,re,urllib.parse,os
UA="EternalEngineResearch/1.0 (historical data survey; single-user research script)"
OUT="/home/user/survey/wiki_results.jsonl"

def api(params,tries=4,wait=5):
    url="https://en.wikipedia.org/w/api.php?"+urllib.parse.urlencode(dict(params,format="json",formatversion="2"))
    for _ in range(tries):
        r=subprocess.run(["curl","-s","--max-time","30","-A",UA,url],capture_output=True,text=True)
        if not r.stdout.strip(): time.sleep(wait); continue
        try:
            d=json.loads(r.stdout)
            if 'error' in d: time.sleep(wait); continue
            return d
        except Exception: time.sleep(wait)
    return None

def pageinfo(title):
    d=api({"action":"parse","page":title,"prop":"wikitext"})
    if not d or 'parse' not in d: return None
    w=d['parse']['wikitext']
    if w.lstrip().upper().startswith("#REDIRECT"):
        return {"title":title,"kind":"redirect","chars":len(w)}
    bullets=len(re.findall(r'(?m)^\*\s',w))
    links=len(re.findall(r'\[\[(?!File:|Image:|Category:)',w))
    # rough: bullets whose line contains a wikilink (geocoding candidate)
    geo=0
    for line in w.splitlines():
        if line.startswith('* ') and re.search(r'\[\[(?!File:|Image:|Category:)',line): geo+=1
    return {"title":title,"kind":"article","chars":len(w),"bullets":bullets,"links":links,"geo_bullets":geo}

targets=[]
for y in range(3000,0,-50): targets.append(f"{y} BC")
for y in range(50,2030,50):  targets.append(str(y))

f=open(OUT,"w",encoding="utf-8")
art=red=fail=0
for t in targets:
    info=pageinfo(t)
    time.sleep(1.1)
    if info is None: fail+=1; info={"title":t,"kind":"failed"}
    elif info["kind"]=="article": art+=1
    else: red+=1
    f.write(json.dumps(info,ensure_ascii=False)+"\n"); f.flush()
    print(f"  {t:>9} {info['kind']:<9} bullets={info.get('bullets','-'):<4} geo={info.get('geo_bullets','-')}",flush=True)
f.close()
print(f"\nDONE articles={art} redirects={red} failed={fail} of {len(targets)}")
