#!/usr/bin/env python3
"""Step 35, part 5: pack the climate of every era into history/climate_periods.json.gz.

    python3 build_climate_periods.py --check   # validate the table and print a report
    python3 build_climate_periods.py           # write the pack
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modpack as M                                     # noqa: E402
import climate_periods_table as tbl                     # noqa: E402

OUT = os.path.join(M.HISTORY, "climate_periods.json.gz")

KINDS = {
    "WARMING":  "a spell of warmer weather than the century before it",
    "COOLING":  "a spell of colder weather than the century before it",
    "VOLCANIC": "a volcanic winter: an eruption put dust and sulfur into the air and the sun dimmed",
    "DROUGHT":  "rain failed, for years or for centuries",
    "PLUVIAL":  "rain came, and kept coming",
    "MONSOON":  "the monsoon failed, or an El Nino turned the winds round",
    "SOLAR":    "the Sun was quiet, or busy, and the world followed",
}

YEAR_MIN, YEAR_MAX = -11000, 3000


def _fail(msg: str) -> None:
    raise ValueError(msg)


def period(p: tuple) -> dict:
    (pid, name, kind, start, end, lat, lon, radius,
     temp, precip, yieldpct, severity, note, certainty) = p

    if not isinstance(pid, str) or not pid:
        _fail(f"bad id: {pid!r}")
    if not isinstance(name, str) or not name:
        _fail(f"{pid}: no name")
    if kind not in KINDS:
        _fail(f"{pid}: kind {kind!r} is not one of {sorted(KINDS)}")
    if not (YEAR_MIN <= start <= YEAR_MAX):
        _fail(f"{pid}: start year {start} outside {YEAR_MIN}..{YEAR_MAX}")
    if not (YEAR_MIN <= end <= YEAR_MAX):
        _fail(f"{pid}: end year {end} outside {YEAR_MIN}..{YEAR_MAX}")
    if end < start:
        _fail(f"{pid}: ends ({end}) before it starts ({start})")
    if not (-90.0 <= lat <= 90.0):
        _fail(f"{pid}: lat {lat} out of range")
    if not (-180.0 <= lon <= 180.0):
        _fail(f"{pid}: lon {lon} out of range")
    if radius < 0:
        _fail(f"{pid}: radius {radius} is negative")
    if not isinstance(severity, int) or not (1 <= severity <= 10):
        _fail(f"{pid}: severity {severity} is not 1..10")
    if certainty not in ("recorded", "estimated"):
        _fail(f"{pid}: certainty must be recorded or estimated, not {certainty!r}")
    if not note:
        _fail(f"{pid}: no note")

    return {
        "id": pid,
        "name": name,
        "type": kind,
        "startYear": start,
        "endYear": end,
        "lat": round(lat, 3),
        "lon": round(lon, 3),
        "radiusKm": int(radius),
        "tempChange": round(temp, 2),
        "precipChange": round(precip, 1),
        "yieldImpact": round(yieldpct, 1),
        "severity": severity,
        "note": note,
        "certainty": certainty,
    }


def report(rows: list[dict]) -> None:
    n = len(rows)
    rec = sum(1 for r in rows if r["certainty"] == "recorded")
    print(f"{n} periods, {rec} recorded / {n - rec} estimated")

    bykind = {}
    for r in rows:
        bykind.setdefault(r["type"], []).append(r)
    print("\nby kind:")
    for k in sorted(bykind, key=lambda k: -len(bykind[k])):
        print(f"  {k:9s} {len(bykind[k]):3d}  {KINDS[k]}")

    print("\nby era:")
    bins = [(-3000, -1000), (-1000, 1), (1, 1000), (1000, 1500),
            (1500, 1800), (1800, 1900), (1900, 2000), (2000, 2100)]
    for lo, hi in bins:
        c = sum(1 for r in rows if r["startYear"] < hi and r["endYear"] >= lo)
        print(f"  {lo:>6}..{hi:<5} {c:3d}")

    glob = sum(1 for r in rows if r["radiusKm"] == 0)
    print(f"\n{glob} are everywhere (radius 0), {n - glob} are regional")

    print("\nthe ten worst:")
    for r in sorted(rows, key=lambda r: -r["severity"])[:10]:
        print(f"  {r['severity']:2d}  {r['startYear']:>5}..{r['endYear']:<5} "
              f"{r['name']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate and report, write nothing")
    args = ap.parse_args()

    rows = [period(p) for p in tbl.PERIODS]

    ids = [r["id"] for r in rows]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        _fail(f"duplicate ids: {dupes}")

    if args.check:
        report(rows)
        return 0

    doc = {
        "format": "eternalengine/climate_periods@1",
        "about": ("Every era's climate: the warm periods, the cold ones, the volcanic winters, the "
                  "megadroughts, the failed monsoons and the famines, from the end of the African "
                  "humid period to the modern warming. Each row carries a centre and a radius, "
                  "because a 2019 synthesis of more than ninety proxy records found that the Roman "
                  "Warm Period, the Medieval Warm Period and the Little Ice Age were regional "
                  "phenomena, not globally coherent episodes. Only the volcanic winters are "
                  "marked as everywhere, and those really are hemispheric within a year or two. "
                  "Temperatures are degrees Celsius against the twentieth-century mean."),
        "generated": time.strftime("%Y-%m-%d"),
        "source": ("Wikipedia, List of periods and events in climate history and Volcanic winter; "
                   "the Journal of Climate study of the 1876-78 Global Famine; and the standard "
                   "regional reconstructions. Numbers are rounded deliberately."),
        "kinds": KINDS,
        "count": len(rows),
        "periods": rows,
    }

    # gzipped so the jar stays small; the register reads it through gzip like every other *.gz
    # pack. The mtime in the header is zeroed so two builds of the same table are byte-identical.
    import gzip as _gzip
    import io as _io
    buf = _io.BytesIO()
    with _gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9, mtime=0) as gz:
        gz.write(json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode())
    raw = buf.getvalue()

    tmp = OUT + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(raw)
    os.replace(tmp, OUT)

    print(f"wrote {OUT}")
    print(f"  {len(rows)} periods, {len(raw)} bytes")
    report(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
