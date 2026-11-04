import json,subprocess,time,sys,urllib.parse
UA="EternalEngineResearch/1.0 (historical data survey; single-user research script)"
def api(params, tries=3):
    q=urllib.parse.urlencode(dict(params, format="json", formatversion="2"))
    url="https://en.wikipedia.org/w/api.php?"+q
    for i in range(tries):
        r=subprocess.run(["curl","-s","--max-time","25","-A",UA,url],capture_output=True,text=True)
        if not r.stdout.strip(): time.sleep(5); continue
        try:
            d=json.loads(r.stdout)
            if 'error' in d:
                print("   err:",d['error'].get('code'),d['error'].get('info','')[:80]); time.sleep(5); continue
            return d
        except Exception as e: time.sleep(5)
    return None

print("=== enumerate year articles via category (url-encoded) ===")
for cat in ["Category:3rd millennium BC","Category:2nd millennium BC","Category:1st millennium BC"]:
    d=api({"action":"query","list":"categorymembers","cmtitle":cat,"cmlimit":"500","cmtype":"page"})
    time.sleep(2.5)
    if not d: print(f"  {cat}: FAILED"); continue
    m=[x['title'] for x in d.get('query',{}).get('categorymembers',[])]
    yr=[t for t in m if t.endswith(' BC') or (t.isdigit())]
    print(f"  {cat:30} total={len(m):>4} year-like={len(yr):>4} sample={yr[:8]}")
