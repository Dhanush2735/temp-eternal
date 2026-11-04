import json, subprocess, time, urllib.parse, os
UA = "EternalEngineHarvester/1.0 (historical data build; single-user research script)"

import sys
_last = [0.0]
MIN_GAP = 2.2          # seconds between requests

def _curl(url, tries=6, wait=25):
    for i in range(tries):
        gap = MIN_GAP - (time.time() - _last[0])
        if gap > 0:
            time.sleep(gap)
        r = subprocess.run(["curl","-s","-w","\n%{http_code}","--max-time","90","-A",UA,url],
                           capture_output=True, text=True)
        _last[0] = time.time()
        out = r.stdout
        code = out.rsplit("\n", 1)[-1].strip() if out else ""
        body = out.rsplit("\n", 1)[0] if out else ""
        if code == "429" or "too many requests" in body.lower():
            backoff = wait * (2 ** i)
            print(f"  [429] backing off {backoff}s", file=sys.stderr, flush=True)
            time.sleep(backoff)
            continue
        if body.strip():
            return body
        time.sleep(wait)
    return None

def titles_to_qids(titles):
    """Wikipedia page title -> Wikidata QID, via prop=pageprops ppprop=wikibase_item."""
    out = {}
    todo = list(titles)
    for i in range(0, len(todo), 50):
        chunk = todo[i:i+50]
        url = ("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
            {"action":"query","titles":"|".join(chunk),"prop":"pageprops",
             "ppprop":"wikibase_item","redirects":"1","format":"json","formatversion":"2"}))
        body = _curl(url)
        if not body:
            continue
        try:
            d = json.loads(body)
        except Exception:
            continue
        for p in d.get("query",{}).get("pages",[]):
            t = p.get("title")
            q = p.get("pageprops",{}).get("wikibase_item")
            if t and q:
                out[t] = q
        time.sleep(0.4)
    return out

def qids_to_coords(qids, batch=400):
    """QID -> [lat, lon] via a single VALUES query per batch."""
    out = {}
    ql = sorted(set(qids))
    for i in range(0, len(ql), batch):
        chunk = ql[i:i+batch]
        values = " ".join("wd:"+q for q in chunk)
        q = ("SELECT ?item ?loc WHERE { VALUES ?item { %s } "
             "?item wdt:P625 ?loc . }" % values)
        url = ("https://query.wikidata.org/sparql?" +
               urllib.parse.urlencode({"query":q,"format":"json"}))
        body = None
        for attempt in range(4):
            r = subprocess.run(["curl","-s","--max-time","180","-A",UA,
                                "-H","Accept: application/sparql-results+json",url],
                               capture_output=True, text=True)
            if r.stdout.strip():
                body = r.stdout; break
            time.sleep(10)
        if not body:
            continue
        try:
            d = json.loads(body)
        except Exception:
            time.sleep(10); continue
        for b in d.get("results",{}).get("bindings",[]):
            qid = b["item"]["value"].rsplit("/",1)[-1]
            try:
                latlon = b["loc"]["value"].replace("Point(","").replace(")","").split()
                out[qid] = [round(float(latlon[1]),5), round(float(latlon[0]),5)]
            except Exception:
                pass
        time.sleep(2.0)
    return out

def resolve_places(titles, cache_path="/home/user/harvest/geo_cache.json"):
    cache = {}
    if os.path.exists(cache_path):
        try: cache = json.load(open(cache_path, encoding="utf-8"))
        except Exception: cache = {}
    todo = [t for t in titles if t not in cache]
    if todo:
        t2q = titles_to_qids(todo)
        coords = qids_to_coords(list(t2q.values()))
        for t in todo:
            q = t2q.get(t)
            cache[t] = coords.get(q) if q else None
        tmp = cache_path + ".tmp"
        json.dump(cache, open(tmp,"w",encoding="utf-8")); os.replace(tmp, cache_path)
    return cache

def _json(url):
    b = _curl(url)
    if not b: return None
    try: return json.loads(b)
    except Exception: return None

def resolve_redirects(titles):
    """title -> canonical title, via action=query redirects=1."""
    out = {}
    todo = list(titles)
    for i in range(0, len(todo), 50):
        chunk = todo[i:i+50]
        d = _json("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
            {"action":"query","titles":"|".join(chunk),"redirects":"1",
             "format":"json","formatversion":"2"}))
        if not d: continue
        q = d.get("query",{})
        rmap = {}
        for r in q.get("redirects",[]):
            rmap[r["from"]] = r["to"]
        norm = {n["from"]: n["to"] for n in q.get("normalized",[])}
        for t in chunk:
            out[t] = rmap.get(norm.get(t, t), norm.get(t, t))
        time.sleep(0.35)
    return out

def qids_location_fallback(qids, batch=300):
    """For items with no P625, try P276 (location) / P131 (admin) -> that item's P625."""
    out = {}
    ql = sorted(set(qids))
    for i in range(0, len(ql), batch):
        chunk = ql[i:i+batch]
        values = " ".join("wd:"+q for q in chunk)
        q = ("SELECT ?item ?loc WHERE { VALUES ?item { %s } "
             "{ ?item wdt:P276 ?p } UNION { ?item wdt:P131 ?p } "
             "?p wdt:P625 ?loc . } LIMIT 6000" % values)
        url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query":q,"format":"json"})
        body = None
        for _ in range(4):
            r = subprocess.run(["curl","-s","--max-time","180","-A",UA,
                                "-H","Accept: application/sparql-results+json",url],
                               capture_output=True, text=True)
            if r.stdout.strip(): body = r.stdout; break
            time.sleep(10)
        if not body: continue
        try: d = json.loads(body)
        except Exception: time.sleep(10); continue
        for b in d.get("results",{}).get("bindings",[]):
            qid = b["item"]["value"].rsplit("/",1)[-1]
            if qid in out: continue
            try:
                ll = b["loc"]["value"].replace("Point(","").replace(")","").split()
                out[qid] = [round(float(ll[1]),5), round(float(ll[0]),5)]
            except Exception: pass
        time.sleep(2.0)
    return out

def resolve_places_v2(titles, cache_path="/home/user/harvest/geo_cache.json"):
    cache = {}
    if os.path.exists(cache_path):
        try: cache = json.load(open(cache_path, encoding="utf-8"))
        except Exception: cache = {}
    todo = [t for t in titles if t not in cache]
    if todo:
        canon = resolve_redirects(todo)
        t2q = titles_to_qids(sorted(set(canon.values())))
        have = qids_to_coords(list(t2q.values()))
        missing = [q for q in t2q.values() if q not in have]
        if missing:
            have.update(qids_location_fallback(missing))
        answered = bool(t2q)          # if the QID call worked at all
        for t in todo:
            ct = canon.get(t, t)
            q = t2q.get(ct)
            if q:
                cache[t] = have.get(q)      # definitive: has QID (coords or not)
            elif answered:
                cache[t] = None             # definitive: no QID for this title
            # else: request failed -> leave uncached so it is retried
        tmp = cache_path + ".tmp"
        json.dump(cache, open(tmp,"w",encoding="utf-8")); os.replace(tmp, cache_path)
    return cache
