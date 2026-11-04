import json,subprocess,time,sys
UA="EternalEngineResearch/1.0 (historical data survey; single-user research script)"
def api(params, tries=4):
    url="https://en.wikipedia.org/w/api.php?"+ "&".join(f"{k}={v}" for k,v in params.items())+"&format=json&formatversion=2"
    for i in range(tries):
        r=subprocess.run(["curl","-s","--max-time","25","-A",UA,url],capture_output=True,text=True)
        try:
            d=json.loads(r.stdout)
            if 'error' in d:
                print("  api error:",d['error'].get('code'),file=sys.stderr); time.sleep(6); continue
            return d
        except Exception: time.sleep(6)
    return None

print("=== TEST: enumerate year articles via category ===")
for cat in ["Category:3rd millennium BC","Category:2nd millennium BC","Category:1st millennium BC","Category:1st millennium"]:
    d=api({"action":"query","list":"categorymembers","cmtitle":cat,"cmlimit":"500","cmtype":"page"})
    time.sleep(2)
    if not d: print(f"  {cat}: FAILED"); continue
    m=[x['title'] for x in d.get('query',{}).get('categorymembers',[])]
    yr=[t for t in m if t.endswith(' BC') or t.isdigit()]
    print(f"  {cat:32} total={len(m):>4}  year-like={len(yr):>4}   sample={yr[:6]}")
