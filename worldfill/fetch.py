#!/usr/bin/env python3
"""Download the open datasets the world-fill packs are built from, into ~/.cache/srcdata
(or $SRCDATA). Raw data never goes into the saved workspace (~128 MB cap); ~/.cache is on
the main disk and is never snapshotted. Re-running skips files that already exist.

  python3 fetch.py places      # step 2: Pleiades, CHGIS V6 county points, Reba et al. 2016
"""
import json, os, subprocess, sys, time

UA = "EternalEngineWorldFill/1.0 (historical data build; research use)"
DST = os.environ.get("SRCDATA", "/home/user/.cache/srcdata")


def get(url, out, tries=4):
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "900", "-A", UA, "-o", out + ".part",
                            "-w", "%{http_code}", url], capture_output=True)
        code = r.stdout.decode()[-3:]
        if code == "200":
            os.replace(out + ".part", out)
            return out
        print(f"  {url[:90]} -> HTTP {code}, retry {i}", flush=True)
        time.sleep(5 * (i + 1))
    raise SystemExit(f"download failed: {url}")


def get_json(url):
    r = subprocess.run(["curl", "-s", "-L", "--max-time", "120", "-A", UA, url], capture_output=True)
    return json.loads(r.stdout)


def fetch(url, fn):
    path = os.path.join(DST, fn)
    if not os.path.exists(path):
        print("get", fn, flush=True)
        get(url, path)
    return path


def places():
    fetch("https://atlantides.org/downloads/pleiades/dumps/pleiades-places-latest.csv.gz",
          "pleiades-places-latest.csv.gz")
    for art, name in [("2059494", "chandlerV2.csv"), ("2059497", "modelskiAncientV2.csv"),
                      ("2059500", "modelskiModernV2.csv")]:
        fn = f"reba_{art}_{name}"
        if not os.path.exists(os.path.join(DST, fn)):
            a = get_json(f"https://api.figshare.com/v2/articles/{art}")
            f = next(x for x in a["files"] if x["name"] == name)
            fetch(f["download_url"], fn)
    # CHGIS V6 county points: CC0 1.0 (the prefecture points sit behind a separate EULA and
    # are not used for the mod)
    doi, want = "doi:10.7910/DVN/Q9VOF5", "v6_time_cnty_pts_utf_wgs84.zip"
    fn = "chgis_Q9VOF5_" + want
    if not os.path.exists(os.path.join(DST, fn)):
        v = get_json("https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=" + doi)
        v = v["data"]["latestVersion"]
        df = next(f["dataFile"] for f in v["files"] if f["dataFile"]["filename"] == want)
        fetch(f"https://dataverse.harvard.edu/api/access/datafile/{df['id']}?format=original", fn)


if __name__ == "__main__":
    os.makedirs(DST, exist_ok=True)
    what = sys.argv[1:] or ["places"]
    for w in what:
        globals()[w]()
    print("in", DST, ":", sorted(os.listdir(DST)))
