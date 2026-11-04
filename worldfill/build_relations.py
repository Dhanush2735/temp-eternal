#!/usr/bin/env python3
"""Step 29 (system C28): relations between states by date: alliances, allegiance, vassals, shared rulers, and the
larger realms a state belonged to.

Two sources:
  * Cliopatria v0.2.1 (Seshat Global History Databank, CC BY 4.0), the same file the ruler register is built from, so
    the names match the register's: its RELATION rows ("Alliance between the Byzantine Empire and Khazaria",
    "Allegiance of Joseon to the Ming Dynasty", "Vassalage of the Kingdom of Bohemia to the Holy Roman Empire",
    "Personal union of the Crown of Aragon with the Crown of Castile") and the MemberOf field of its polity rows (a
    duchy of the Holy Roman Empire, a colony of the British Empire), each with its years;
  * Wikidata (CC0, through QLever): military alliances (P31/P279* military alliance) and their members, with the
    years of each membership when Wikidata gives them (P463 with start and end), else the alliance's own years; a
    member is matched to the register's states by its Wikidata number, or by the country (P17) of a register state
    (the French Fifth Republic is France).

    python3 build_relations.py --fetch    download Cliopatria (46 MB zip, into build/relations/, not kept) and fetch the
                                          alliances and the register states' countries from Wikidata
    python3 build_relations.py --build    write history/state_relations.json.gz into the mod
    python3 build_relations.py --check    read it back and check it (exit 1 on a problem)

File layout (history/state_relations.json.gz, JSON):
  relations: [[kind, a, b, from, to, since], ...]   years inclusive; since: the first year of the tie itself (a
      country's alliance membership can be older than the register state that holds it in these years); kind:
      "alliance"   a and b are allied (both ways)
      "allegiance" a owes allegiance to b
      "vassal"     a is a vassal of b
      "union"      a shares its ruler with b (both ways)
      "member"     a is part of the larger realm b (Cliopatria's MemberOf)
      "pact"       a is a member of the military alliance b (Wikidata)
"""
import collections
import gzip
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modpack as M                         # noqa: E402
import fetch_cards_wd as fc                 # noqa: E402
from build_cards import qid_of, literal, rows_in   # noqa: E402

BASE = os.path.join(HERE, "build", "relations")
RAW = os.path.join(BASE, "raw")
ZIP_URL = "https://github.com/Seshat-Global-History-Databank/cliopatria/raw/main/cliopatria.geojson.zip"
ZIP = os.path.join(BASE, "cliopatria.geojson.zip")
GEOJSON = os.path.join(BASE, "cliopatria_polities_only_v021.geojson")
OUT_NAME = "state_relations.json.gz"
OUT = os.path.join(M.HISTORY, OUT_NAME)
REPORT = os.path.join(HERE, "logs", "step29_relations_report.json")
RULERS = os.path.join(M.HISTORY, "world_rulers.json.gz")
NOW = 2026

REL = re.compile(r"^\((Alliance between|Allegiance of|Vassalage of|Personal union of) (.+?) (and|to|with) (.+)\)$")
KIND = {"Alliance between": "alliance", "Allegiance of": "allegiance", "Vassalage of": "vassal",
        "Personal union of": "union"}

# Members of military alliances, with the membership's years when Wikidata has them.
A_MEMBERS = """SELECT ?a ?al ?m ?how ?f ?t ?as ?ae WHERE {
  ?a wdt:P31/wdt:P279* wd:Q1127126 .
  { ?m p:P463 ?st . ?st ps:P463 ?a . OPTIONAL { ?st pq:P580 ?f } OPTIONAL { ?st pq:P582 ?t } BIND("memberof" AS ?how) }
  UNION { ?a wdt:P527 ?m . BIND("haspart" AS ?how) }
  UNION { ?a wdt:P710 ?m . BIND("participant" AS ?how) }
  OPTIONAL { ?a wdt:P571 ?as } OPTIONAL { ?a wdt:P580 ?as } OPTIONAL { ?a wdt:P576 ?ae } OPTIONAL { ?a wdt:P582 ?ae }
  OPTIONAL { ?a rdfs:label ?al . FILTER(LANG(?al) = "en") }
}"""
# The country (P17) of each register state, to match "France" (an alliance member) to the French Fifth Republic.
P_COUNTRY = """SELECT ?x ?c WHERE {
  VALUES ?x { %s }
  ?x wdt:P17 ?c .
}"""


COLONY_WORDS = re.compile(r"(?i)colon|indochina|hebrides|zone|territor|protectorate|mandat|gold coast|ceylon|africa|"
                          r"india|guiana|congo|algeria|somaliland|madagascar|overseas")


def run(query, name):
    old = fc.RAW
    fc.RAW = RAW
    try:
        return fc.run(query, name)
    finally:
        fc.RAW = old


def register(with_spans=False):
    d = json.load(gzip.open(RULERS, "rt", encoding="utf-8"))
    names = set()
    by_q = collections.defaultdict(set)
    for p in d["polities"]:
        names.add(p[0])
        if len(p) > 1 and p[1]:
            by_q[p[1]].add(p[0])
    if not with_spans:
        return names, by_q
    spans = {}
    for seq in d["timelines"]:
        for i in range(0, len(seq), 3):
            n = d["polities"][seq[i]][0]
            f, t = seq[i + 1], seq[i + 2]
            lo_, hi_ = spans.get(n, (f, t))
            spans[n] = (min(lo_, f), max(hi_, t))
    return names, by_q, spans


def fetch():
    os.makedirs(BASE, exist_ok=True)
    if not os.path.exists(GEOJSON):
        if not os.path.exists(ZIP):
            import requests
            with requests.get(ZIP_URL, stream=True, timeout=600) as r:
                r.raise_for_status()
                with open(ZIP + ".part", "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
            os.replace(ZIP + ".part", ZIP)
        with zipfile.ZipFile(ZIP) as z:
            z.extractall(BASE)
    run(A_MEMBERS, "a_members")
    _, by_q = register()
    qids = sorted({int(q[1:]) for q in by_q})
    for i in range(0, len(qids), 3000):
        run(P_COUNTRY % " ".join(f"wd:Q{q}" for q in qids[i:i + 3000]), f"p_country_{i // 3000:03d}")


def clio_rows():
    """The properties of every Cliopatria row (the polygons are not read)."""
    with open(GEOJSON, encoding="utf-8") as f:
        for line in f:
            if not line.startswith('{ "type": "Feature"'):
                continue
            i = line.index('"properties": ') + len('"properties": ')
            j = line.index(', "geometry"')
            yield json.loads(line[i:j])


def plain(name):
    return name.strip()[1:-1].strip() if name.strip().startswith("(") and name.strip().endswith(")") else name.strip()


def merge(spans):
    """[(kind, a, b, from, to[, since])] -> [kind, a, b, from, to, since] with touching or overlapping years joined.
    `since` is the first year of the tie itself: for a military alliance matched through the country, the year the
    country joined (France since 1949), even when the register's state began later (the Fifth Republic, 1958)."""
    by = collections.defaultdict(list)
    for sp in spans:
        k, a, b, f, t = sp[:5]
        since = sp[5] if len(sp) > 5 else f
        by[(k, a, b)].append((f, t, since))
    out = []
    for (k, a, b), ys in by.items():
        ys.sort()
        cur = list(ys[0])
        for f, t, since in ys[1:]:
            if f <= cur[1] + 1:
                cur[1] = max(cur[1], t)
                cur[2] = min(cur[2], since)
            else:
                out.append([k, a, b, cur[0], cur[1], cur[2]])
                cur = [f, t, since]
        out.append([k, a, b, cur[0], cur[1], cur[2]])
    return sorted(out, key=lambda r: (r[3], r[0], r[1], r[2]))


def build():
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    names, by_q = register()
    report = collections.Counter()
    spans = []
    for p in clio_rows():
        f, t = int(p["FromYear"]), int(p["ToYear"])
        if p.get("Type") == "RELATION":
            m = REL.match(p["Name"].strip())
            if not m:
                report["relation rows not understood"] += 1
                continue
            kind = KIND[m.group(1)]
            a, b = plain(m.group(2)), plain(m.group(4))
            spans.append((kind, a, b, f, t))
            report[f"cliopatria {kind} rows"] += 1
        elif p.get("MemberOf"):
            for whole in p["MemberOf"].split(";"):
                whole = plain(whole)
                if whole and whole != p["Name"]:
                    spans.append(("member", p["Name"].strip(), whole, f, t))
                    report["cliopatria member rows"] += 1
    # Wikidata military alliances
    country_of = collections.defaultdict(set)
    for r in rows_in(RAW, "p_country"):
        country_of[qid_of(r[1])].add(qid_of(r[0]))
    reg_by_q = {int(q[1:]): ns for q, ns in by_q.items()}
    _, _, life = register(with_spans=True)
    alliances = {}
    rows = collections.defaultdict(list)
    for r in rows_in(RAW, "a_members"):
        a, label, m = qid_of(r[0]), literal(r[1]), qid_of(r[2])
        if a and m and label:
            rows[(a, m)].append((r[3].strip('"'), cell_year(r[4]), cell_year(r[5]), cell_year(r[6]), cell_year(r[7]),
                                 label))
    for (a, m), rs in sorted(rows.items()):
        dated = [x for x in rs if x[0] == "memberof" and x[1] is not None]
        label = rs[0][5]
        a_from = min((x[3] for x in rs if x[3] is not None), default=None)
        a_to = max((x[4] for x in rs if x[4] is not None), default=None)
        if dated:
            terms = [(x[1], x[2] if x[2] is not None else (a_to if a_to is not None else NOW)) for x in dated]
        elif a_from is not None and (a_to if a_to is not None else NOW) - a_from <= 15:
            terms = [(a_from, a_to if a_to is not None else NOW)]   # a short alliance: its own years
        else:
            report["alliance members without years (left out)"] += 1
            continue
        # The member itself when the register has it, else the register's states of that country (the French
        # Fifth Republic for France) that existed in those years.
        direct = set(reg_by_q.get(m, set()))
        via = set()
        for pq in country_of.get(m, set()):
            via |= reg_by_q.get(pq, set())
        for start, end in terms:
            if end < start:
                continue
            states = {x for x in direct if x in life and life[x][0] <= end and life[x][1] >= start}
            if not states:
                # No register state with the member's own number in those years: the country's register states,
                # but not its colonies and dependencies (Wikidata gives them the same country).
                states = {x for x in via if x in life and life[x][0] <= end and life[x][1] >= start
                          and not COLONY_WORDS.search(x)}
            if not states:
                report["alliance members not in the register"] += 1
                continue
            alliances[a] = label
            for st in states:
                spans.append(("pact", st, label, max(start, life[st][0]), min(end, life[st][1]), start))
                report["alliance memberships"] += 1
    rels = merge(spans)
    # Only relations that touch a state of the register can ever be said.
    keep = [r for r in rels if r[1] in names or r[2] in names]
    report["relations"] = len(keep)
    report["relations left out (no register state)"] = len(rels) - len(keep)
    report["military alliances"] = len(alliances)
    for k in ("alliance", "allegiance", "vassal", "union", "member", "pact"):
        report[f"kept {k}"] = sum(1 for r in keep if r[0] == k)
    data = {
        "format": 1,
        "id": "state_relations",
        "source": ("Cliopatria v0.2.1 (Seshat Global History Databank, CC BY 4.0): RELATION rows and the MemberOf "
                   "field; Wikidata (CC0) through QLever (qlever.dev), 2026-10-15: military alliances and their "
                   "members (P31/P279* Q1127126; P463 with P580/P582, P527, P710)."),
        "kinds": {"alliance": "allied (both ways)", "allegiance": "a owes allegiance to b", "vassal": "a is a vassal of b",
                  "union": "a shares its ruler with b (both ways)", "member": "a is part of the larger realm b",
                  "pact": "a is a member of the military alliance b"},
        "relations": keep,
    }
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with open(OUT + ".tmp", "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", compresslevel=9, mtime=0) as g:
            g.write(raw)
    json.loads(gzip.open(OUT + ".tmp").read())
    os.replace(OUT + ".tmp", OUT)
    report["gzip bytes"] = os.path.getsize(OUT)
    with open(REPORT, "w") as f:
        json.dump(dict(sorted(report.items())), f, indent=1)
    for k, v in sorted(report.items()):
        print(f"  {k}: {v:,}")


def cell_year(cell):
    """'1949-04-04T00:00:00Z' (Wikidata RDF, year 0 = 1 BCE) -> the mod's year; None if missing or unknown."""
    if not cell or cell.startswith("<"):
        return None
    m = re.match(r'^"?(-?)(\d+)-', cell)
    if not m:
        return None
    y = int(m.group(2)) * (-1 if m.group(1) else 1)
    return y - 1 if y <= 0 else y


def check():
    data = json.load(gzip.open(OUT, "rt", encoding="utf-8"))
    names, _ = register()
    bad = []
    for r in data["relations"]:
        k, a, b, f, t, since = r
        if since > f:
            bad.append(f"since after from {r}")
        if k not in data["kinds"]:
            bad.append(f"kind {k}")
        if not a or not b or a == b:
            bad.append(f"names {r}")
        if t < f or f < -3500 or t > NOW:
            bad.append(f"years {r}")
        if a not in names and b not in names:
            bad.append(f"no register state {r}")

    def has(kind, a, b, year):
        return any(r[0] == kind and r[1] == a and r[2] == b and r[3] <= year <= r[4] for r in data["relations"])

    if not any(r[0] == "pact" and r[1] == "French Fifth Republic" and r[2] == "NATO" and r[5] == 1949
               for r in data["relations"]):
        bad.append("France in NATO since 1949 (through the Fifth Republic)")

    expect = [("allegiance", "Joseon", "Ming Dynasty", 1500), ("vassal", "Kingdom of Bohemia", "Holy Roman Empire", 1400)]
    for kind, a, b, y in expect:
        if not has(kind, a, b, y):
            bad.append(f"missing: {kind} {a} -> {b} in {y}")
    pacts = {r[2] for r in data["relations"] if r[0] == "pact"}
    for want in ("NATO", "Warsaw Pact"):
        if want not in pacts:
            bad.append(f"missing alliance {want}")
    print(f"check: {len(data['relations']):,} relations; {len(bad)} problems")
    for b in bad[:20]:
        print("  " + b)
    return 1 if bad else 0


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "--fetch":
        fetch()
    elif mode == "--build":
        build()
    elif mode == "--check":
        return check()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
