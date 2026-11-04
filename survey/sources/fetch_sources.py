#!/usr/bin/env python3
"""Download every open non-Wikipedia source measured in OTHER_SOURCES_CENSUS.md into ~/.cache/srcdata (or $SRCDATA).

Raw data is kept outside the workspace on purpose (~100 MB, and the snapshot cap is ~128 MB).
Re-running is safe: files that already exist are skipped. Then run sources_census.py.
"""
import json, os, re, subprocess, time, zipfile

UA = "EternalEngineSurvey/2.0 (historical data survey; research use)"
DST = os.environ.get("SRCDATA", "/home/user/.cache/srcdata")   # main disk, never snapshotted (/tmp is a RAM disk)


def get(url, out=None, tries=4):
    for i in range(tries):
        cmd = ["curl", "-s", "-L", "--max-time", "600", "-A", UA, "-w", "%{http_code}", url]
        if out:
            cmd[1:1] = ["-o", out]
        r = subprocess.run(cmd, capture_output=True)
        code = r.stdout[-3:].decode()
        if code == "200":
            return out if out else r.stdout[:-3].decode("utf-8")
        print(f"  {url[:90]} -> HTTP {code}, retry {i}", flush=True)
        time.sleep(5 * (i + 1))
    return None


def fetch(url, fn):
    if not os.path.exists(fn):
        print("get", fn, flush=True)
        get(url, fn)


os.makedirs(DST, exist_ok=True)
os.chdir(DST)

# single files
fetch("https://atlantides.org/downloads/pleiades/dumps/pleiades-places-latest.csv.gz", "pleiades-places-latest.csv.gz")
fetch("https://ucdp.uu.se/downloads/ged/ged251-csv.zip", "ged251-csv.zip")
fetch("https://webservices.volcano.si.edu/geoserver/GVP-VOTW/ows?service=WFS&version=2.0.0&request=GetFeature"
      "&typeName=GVP-VOTW:Smithsonian_VOTW_Holocene_Eruptions&outputFormat=application/json", "gvp_eruptions.json")
fetch("https://orbis.stanford.edu/o_sites.csv", "orbis_o_sites.csv")
for f in ["Inter-StateWarData_v4.0.csv", "Intra-StateWarData_v4.1.csv", "Extra-StateWarData_v4.0.csv", "Non-StateWarData_v4.0.csv"]:
    fetch("https://correlatesofwar.org/wp-content/uploads/" + f, f)

# NOAA NCEI hazards (paged JSON API)
for name, path, lo in [("quakes", "earthquakes", -3000), ("tsunamis", "tsunamis/events", -3000), ("volcanoes", "volcanoes", -4400)]:
    fn = f"ncei_{name}.json"
    if os.path.exists(fn):
        continue
    items, page = [], 1
    while True:
        d = json.loads(get(f"https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/{path}?minYear={lo}&maxYear=2026&page={page}"))
        items += d.get("items", [])
        if page >= (d.get("totalPages") or 1):
            break
        page += 1
        time.sleep(0.4)
    json.dump(items, open(fn, "w"))
    print("ncei", name, len(items), flush=True)

# plague: Zenodo record 14973 (contains the merged Biraben / Buentgen 2012 / Atanasiu 2008 database)
if not os.path.exists("plague/europe-pnas/resources/plague-db-europe.txt"):
    rec = json.loads(get("https://zenodo.org/api/records/14973"))
    f = rec["files"][0]
    fetch(f["links"]["self"], "plague_" + f["key"])
    with zipfile.ZipFile("plague_" + f["key"]) as z:
        for m in z.namelist():
            if m.endswith(("plague-db-europe.txt", "Plague dataset - sources and notes.txt", "LICENSE", "README.md")):
                z.extract(m, "plague")

# Reba, Reitsma & Seto 2016 (figshare)
for art, name in [("2059494", "chandlerV2.csv"), ("2059497", "modelskiAncientV2.csv"), ("2059500", "modelskiModernV2.csv")]:
    fn = f"reba_{art}_{name}"
    if not os.path.exists(fn):
        a = json.loads(get(f"https://api.figshare.com/v2/articles/{art}"))
        f = next(x for x in a["files"] if x["name"] == name)
        fetch(f["download_url"], fn)

# CHGIS V6 time-series points (Harvard Dataverse): county (CC0) and prefecture (EULA) points, UTF-8 / WGS84
for doi, want in [("doi:10.7910/DVN/Q9VOF5", "v6_time_cnty_pts_utf_wgs84.zip"), ("doi:10.7910/DVN/WW1PD6", "v6_time_pref_pts_utf_wgs84.zip")]:
    fn = "chgis_" + doi.split("/")[-1] + "_" + want
    if os.path.exists(fn):
        continue
    v = json.loads(get("https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=" + doi))["data"]["latestVersion"]
    df = next(f["dataFile"] for f in v["files"] if f["dataFile"]["filename"] == want)
    fetch(f"https://dataverse.harvard.edu/api/access/datafile/{df['id']}?format=original", fn)

print("done:", sorted(os.listdir(".")))
