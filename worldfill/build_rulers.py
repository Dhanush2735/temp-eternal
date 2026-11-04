#!/usr/bin/env python3
"""Step 3b: who ruled every place on Earth, 3400 BC - AD 2024, from Cliopatria v0.2.1.

The mod's RulerRegister answers "who ruled this point in this year" from deccan_rulers.json,
built from Cliopatria v0.2.1 for the Deccan only. This builds the same answer for the whole
world, with the same rule, on a 0.5-degree grid:

  * every plain polity polygon (Type POLITY, name not in parentheses: alliances, allegiances
    and composite empires are facts, never rulers) is rasterised onto 0.5-degree cell centres
    (even-odd scanline; a polity too small to cover any centre is given the cell holding its
    centroid, so no polity disappears);
  * for every cell and year, the ruler is the smallest-area polity covering it - the rule the
    Deccan register uses ("a sultanate beats the empire it sat inside");
  * equal timelines are stored once; cells whose 0.5-degree box holds a Deccan place are left
    to the Deccan register.

Validation: for every Deccan place, the world timeline of its cell is compared with the
Deccan register's own timeline (same source, same rule; only the point differs).

Output: history/world_rulers.json.gz in the mod, "format": 2 (compact; RulerRegister reads it
alongside deccan_rulers.json):
    polities  [[name, wikidata], ...]
    timelines [[polity, start, end, polity, start, end, ...], ...]   (end inclusive)
    places    [lat*100, lon*100, timeline, ...]                     (cell centres)

Usage: python3 build_rulers.py [--dry-run]
"""
import collections, gzip, heapq, json, math, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack as M        # noqa: E402

SRC = os.path.join(os.environ.get("SRCDATA", "/home/user/.cache/srcdata"), "cliopatria_polities_only_v021.geojson")
DECCAN = f"{M.HISTORY}/deccan_rulers.json.gz"
OUT_NAME = "world_rulers.json.gz"
REPORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_rulers_report.json")
CELL = 0.5
LAT0, LON0 = -90 + CELL / 2, -180 + CELL / 2
NR, NC = int(180 / CELL), int(360 / CELL)


# ------------------------------------------------------------------ rasterising
def polygons(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    if geom["type"] == "MultiPolygon":
        return geom["coordinates"]
    return []


def raster(geom):
    """0.5-degree cell indices whose centres fall inside the (multi)polygon (even-odd rule)."""
    xs0, ys0, xs1, ys1 = [], [], [], []
    for poly in polygons(geom):
        for ring in poly:
            a = np.asarray(ring, dtype=np.float64)
            if len(a) < 3:
                continue
            if a[0, 0] != a[-1, 0] or a[0, 1] != a[-1, 1]:
                a = np.vstack([a, a[:1]])
            xs0.append(a[:-1, 0]); ys0.append(a[:-1, 1]); xs1.append(a[1:, 0]); ys1.append(a[1:, 1])
    if not xs0:
        return np.zeros(0, dtype=np.int32)
    x0, y0, x1, y1 = (np.concatenate(v) for v in (xs0, ys0, xs1, ys1))
    keep = y0 != y1
    x0, y0, x1, y1 = x0[keep], y0[keep], x1[keep], y1[keep]
    ymin, ymax = np.minimum(y0, y1), np.maximum(y0, y1)
    r0 = np.ceil((ymin - LAT0) / CELL).astype(np.int64)
    r1 = np.ceil((ymax - LAT0) / CELL).astype(np.int64) - 1        # centre in [ymin, ymax)
    r0, r1 = np.clip(r0, 0, NR - 1), np.clip(r1, -1, NR - 1)
    n = r1 - r0 + 1
    ok = n > 0
    if not ok.any():
        return np.zeros(0, dtype=np.int32)
    x0, y0, x1, y1, r0, n = x0[ok], y0[ok], x1[ok], y1[ok], r0[ok], n[ok]
    tot = int(n.sum())
    e = np.repeat(np.arange(len(n)), n)
    rows = r0[e] + (np.arange(tot) - np.repeat(np.cumsum(n) - n, n))
    yc = LAT0 + CELL * rows
    xc = x0[e] + (yc - y0[e]) * (x1[e] - x0[e]) / (y1[e] - y0[e])
    order = np.lexsort((xc, rows))
    rows, xc = rows[order], xc[order]
    _, first, counts = np.unique(rows, return_index=True, return_counts=True)
    rank = np.arange(len(rows)) - np.repeat(first, counts)
    odd_row = np.repeat(counts % 2 == 1, counts)
    last_in_row = rank == np.repeat(counts - 1, counts)
    use = ~(odd_row & last_in_row)                 # a row with an odd count drops its last crossing
    rows, xc, rank = rows[use], xc[use], rank[use]
    starts = rank % 2 == 0
    xa, xb, rr = xc[starts], xc[~starts], rows[starts]
    m = min(len(xa), len(xb))
    xa, xb, rr = xa[:m], xb[:m], rr[:m]
    c0 = np.clip(np.ceil((xa - LON0) / CELL).astype(np.int64), 0, NC)
    c1 = np.clip(np.ceil((xb - LON0) / CELL).astype(np.int64) - 1, -1, NC - 1)
    L = c1 - c0 + 1
    good = L > 0
    c0, L, rr = c0[good], L[good], rr[good]
    if not len(L):
        return np.zeros(0, dtype=np.int32)
    tot = int(L.sum())
    cells = np.repeat(rr * NC + c0, L) + (np.arange(tot) - np.repeat(np.cumsum(L) - L, L))
    return np.unique(cells).astype(np.int32)


def centroid_cell(geom):
    best, area = None, -1.0
    for poly in polygons(geom):
        a = np.asarray(poly[0], dtype=np.float64)
        if len(a) < 3:
            continue
        x, y = a[:, 0], a[:, 1]
        s = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
        if s > area:
            area, best = s, (float(y.mean()), float(x.mean()))
    if best is None:
        return None
    r = min(NR - 1, max(0, int(math.floor((best[0] + 90) / CELL))))
    c = min(NC - 1, max(0, int(math.floor((best[1] + 180) / CELL))))
    return r * NC + c


# ------------------------------------------------------------------ timelines
def timeline(recs):
    """recs: [(from, to_inclusive, area, polity)] -> [(polity, start, end_inclusive)] using the
    smallest-area active record each year (ties: lower polity index)."""
    events = sorted({f for f, _, _, _ in recs} | {t + 1 for _, t, _, _ in recs})
    by_start = collections.defaultdict(list)
    for i, (f, t, a, p) in enumerate(recs):
        by_start[f].append(i)
    heap, out = [], []
    for k in range(len(events) - 1):
        y, nxt = events[k], events[k + 1]
        for i in by_start.get(y, ()):
            f, t, a, p = recs[i]
            heapq.heappush(heap, (a, p, t))
        while heap and heap[0][2] < y:
            heapq.heappop(heap)
        if not heap:
            continue
        a, p, t = heap[0]
        if out and out[-1][0] == p and out[-1][2] == y - 1:
            out[-1] = (p, out[-1][1], nxt - 1)
        else:
            out.append((p, y, nxt - 1))
    return out


def main(dry=False):
    t0 = time.time()
    stats = collections.Counter()
    pol_index, polities = {}, []
    recs = []                         # (from, to, area, polity)
    cell_parts, rec_parts = [], []
    with open(SRC, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith('{ "type": "Feature"'):
                continue
            f = json.loads(line.rstrip(","))
            p = f["properties"]
            stats["features"] += 1
            name = (p.get("Name") or "").strip()
            if p.get("Type") != "POLITY" or not name or name.startswith("("):
                stats["skipped_relation_or_composite"] += 1
                continue
            if name not in pol_index:
                pol_index[name] = len(polities)
                polities.append([name, p.get("Wikidata") or ""])
            cells = raster(f["geometry"])
            if not len(cells):
                c = centroid_cell(f["geometry"])
                if c is None:
                    stats["no_geometry"] += 1
                    continue
                cells = np.array([c], dtype=np.int32)
                stats["polity_rows_smaller_than_a_cell"] += 1
            ri = len(recs)
            recs.append((int(p["FromYear"]), int(p["ToYear"]), float(p["Area"]), pol_index[name]))
            cell_parts.append(cells)
            rec_parts.append(np.full(len(cells), ri, dtype=np.int32))
            stats["polity_rows"] += 1
            if stats["features"] % 2000 == 0:
                print(f"  {stats['features']} features ({time.time() - t0:.0f}s)", flush=True)
    cells = np.concatenate(cell_parts)
    rix = np.concatenate(rec_parts)
    del cell_parts, rec_parts
    stats["cell_polity_pairs"] = int(len(cells))
    order = np.argsort(cells, kind="stable")
    cells, rix = cells[order], rix[order]
    uc, first, counts = np.unique(cells, return_index=True, return_counts=True)
    print(f"rasterised {stats['polity_rows']} polity rows into {len(uc)} cells, {len(cells)} pairs "
          f"({time.time() - t0:.0f}s)", flush=True)

    # cells already covered by the Deccan register
    deccan = json.load(gzip.open(DECCAN, "rt", encoding="utf-8"))
    dcells = set()
    for pl in deccan["places"]:
        r = int(math.floor((pl["lat"] + 90) / CELL)); c = int(math.floor((pl["lon"] + 180) / CELL))
        dcells.add(r * NC + c)

    tl_index, timelines, cell_tl = {}, [], {}
    for k, c in enumerate(uc):
        rs = [recs[i] for i in rix[first[k]:first[k] + counts[k]]]
        tl = tuple(timeline(rs))
        if not tl:
            continue
        if tl not in tl_index:
            tl_index[tl] = len(timelines)
            timelines.append(tl)
        cell_tl[int(c)] = tl_index[tl]
    print(f"timelines: {len(timelines)} distinct over {len(cell_tl)} cells ({time.time() - t0:.0f}s)", flush=True)

    # validation against the Deccan register: same source and rule, cell centre vs place
    agree = years_agree = years_total = 0
    dtl = deccan["timelines"]
    sample = deccan["places"]
    pname = {i: p[0] for i, p in enumerate(polities)}
    for pl in sample:
        r = int(math.floor((pl["lat"] + 90) / CELL)); c = int(math.floor((pl["lon"] + 180) / CELL))
        w = cell_tl.get(r * NC + c)
        d_spans = dtl[pl["timeline"]]
        w_spans = timelines[w] if w is not None else ()
        def at(spans, y, world):
            for s in spans:
                if world:
                    if s[1] <= y <= s[2]:
                        return pname[s[0]]
                elif s["start"] <= y <= s["end"]:
                    return s["name"]
            return None
        same = True
        for y in range(-3000, 2025, 25):
            a, b = at(d_spans, y, False), at(w_spans, y, True)
            if a is None and b is None:
                continue
            years_total += 1
            if a == b:
                years_agree += 1
            else:
                same = False
        agree += same
    stats["deccan_places_checked"] = len(sample)
    stats["deccan_places_identical_every_25_years"] = agree
    stats["deccan_sampled_years_same_ruler_pct"] = round(100.0 * years_agree / max(1, years_total), 2)

    places = []
    for c, ti in sorted(cell_tl.items()):
        if c in dcells:
            stats["cells_left_to_deccan_register"] += 1
            continue
        r, col = divmod(c, NC)
        places += [int(round((LAT0 + CELL * r) * 100)), int(round((LON0 + CELL * col) * 100)), ti]
    used = sorted({places[i + 2] for i in range(0, len(places), 3)})
    remap = {old: new for new, old in enumerate(used)}
    timelines = [timelines[i] for i in used]
    for i in range(2, len(places), 3):
        places[i] = remap[places[i]]
    spans = sum(len(t) for t in timelines)
    doc = {
        "format": 2,
        "id": "world_rulers",
        "source": "Cliopatria v0.2.1 (Seshat Global History Databank), cliopatria_polities_only_v021.geojson, "
                  "CC BY 4.0. Rasterised to 0.5-degree cell centres by worldfill/build_rulers.py.",
        "rule": "Smallest-area plain polity covering the cell centre that year (Type POLITY; parenthesised "
                "alliances, allegiances and composite empires are never rulers). Cells holding a Deccan place "
                "are left to deccan_rulers.json.",
        "cellDegrees": CELL,
        "polities": polities,
        "timelines": [[v for span in t for v in span] for t in timelines],
        "places": places,
    }
    report = {"stats": dict(stats), "polities": len(polities), "timelines": len(timelines), "spans": spans,
              "places": len(places) // 3, "seconds": round(time.time() - t0)}
    json.dump(report, open(REPORT, "w"), indent=1)
    print(json.dumps(report, indent=1), flush=True)
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    print(f"world_rulers: {len(raw) / 1e6:.1f} MB json, {len(gzip.compress(raw, 9)) / 1e6:.1f} MB gzipped", flush=True)
    if dry:
        return doc
    path = f"{M.HISTORY}/{OUT_NAME}"
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(path + ".tmp", "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    json.loads(gzip.open(path + ".tmp").read())
    os.replace(path + ".tmp", path)
    print("wrote", path)
    return doc


if __name__ == "__main__":
    main(dry="--dry-run" in sys.argv)
