#!/usr/bin/env python3
"""Fact audit (step 12): looks for wrong facts in the mod's history data. It changes nothing in the mod.

Every rule below is a test a fact can fail: a reign longer than a life, a republic ruled by a king,
a faith older than its founder, a news line whose own words name another year. Wikidata (fetched by
fact_audit_wd.py into fact_audit_wikidata.json.gz) is the outside witness for lifetimes and for the
years a state's name was in use.

Writes:
  worldfill/fact_audit_findings.csv   every finding: area, rule, how sure, seen in game, item, detail
  worldfill/fact_audit_summary.json   counts per rule, examples, and the people-weighted share of the
                                      world that would hear at least one wrong line, by year
Usage: python3 fact_audit.py
"""
import collections
import csv
import gzip
import json
import math
import os
import re
import sys
import unicodedata

import numpy as np

sys.path.insert(0, "/home/user/worldfill")
sys.path.insert(0, "/home/user/harvest")

HIST = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history"
ETER = "/home/user/eternal/src/main/resources/data/eternalengine/eternal"
WF = "/home/user/worldfill"
WD_CACHE = f"{WF}/fact_audit_wikidata.json.gz"
OUT_CSV = f"{WF}/fact_audit_findings.csv"
OUT_JSON = f"{WF}/fact_audit_summary.json"
NOW = 2026
YEARS = [-1000, -500, 1, 500, 1000, 1300, 1500, 1700, 1800, 1850, 1900, 1950, 2000, 2020]

# How sure a finding is, in plain words.
WRONG, LIKELY, ODD, MISSING = "wrong", "likely wrong", "odd", "missing"

FINDINGS = []


def find(area, rule, sure, item, detail="", seen="", source=""):
    FINDINGS.append({"area": area, "rule": rule, "sure": sure, "seen": seen, "item": item,
                     "detail": detail, "source": source})


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def plain(s):
    """Lower case, no accents, no quotes or brackets: for comparing names."""
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = re.sub(r'["“”][^"“”]*["“”]', " ", s)
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def merge(ivs):
    out = []
    for s, e in sorted(ivs):
        if out and s <= out[-1][1] + 1:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def overlap(ivs, s, e):
    return sum(max(0, min(e, b) - max(s, a) + 1) for a, b in ivs)


def covers(ivs, y):
    return any(a <= y <= b for a, b in ivs)


def yr(y):
    return f"{-y} BC" if y < 0 else f"{y}"


def span(s, e):
    return f"{yr(s)}–{yr(e)}" if s != e else yr(s)


# ====================================================================== the map: which state where, when

class MapIndex:
    """Years each state name and Wikidata id is on the mod's border map (world + Deccan registers)."""

    def __init__(self):
        name_iv, qid_iv = collections.defaultdict(list), collections.defaultdict(list)
        qn = collections.defaultdict(lambda: collections.defaultdict(list))
        w = jload(f"{HIST}/world_rulers.json.gz")
        pols = [(p[0], p[1] if len(p) > 1 else None) for p in w["polities"]]
        for t in w["timelines"]:
            for k in range(0, len(t) - 2, 3):
                n, q = pols[t[k]]
                name_iv[n].append((t[k + 1], t[k + 2]))
                if q:
                    qid_iv[q].append((t[k + 1], t[k + 2]))
                    qn[q][n].append((t[k + 1], t[k + 2]))
        d = jload(f"{HIST}/deccan_rulers.json")
        for t in d["timelines"]:
            for sp in t:
                n, q = sp["name"], sp.get("wikidata")
                if n.startswith("("):
                    continue
                name_iv[n].append((sp["start"], sp["end"]))
                if q:
                    qid_iv[q].append((sp["start"], sp["end"]))
                    qn[q][n].append((sp["start"], sp["end"]))
        self.name_iv = {k: merge(v) for k, v in name_iv.items()}
        self.qid_iv = {k: merge(v) for k, v in qid_iv.items()}
        self.qid_names = {q: {n: merge(v) for n, v in m.items()} for q, m in qn.items()}
        self.name_qids = collections.defaultdict(set)
        for q, m in self.qid_names.items():
            for n in m:
                self.name_qids[n].add(q)

    def names_in(self, q, y):
        return [n for n, ivs in self.qid_names.get(q, {}).items() if covers(ivs, y)]


# ====================================================================== words that give a fact away

MONARCH = re.compile(r"(?i)\b(king|queen|monarch|emperor|empress|shah|shahanshah|sultan|sultana|tsar|czar|tsarina|"
                     r"kaiser|emir|amir|pharaoh|maharaja|maharana|raja|rajah|rani|nizam|khagan|bey|dey|negus|"
                     r"mikado|grand duke|archduke|elector|chhatrapati|padishah|caliph|basileus)\b")
PRESIDENT = re.compile(r"(?i)\b(president|chairman|general secretary|first secretary|supreme leader|premier)\b")
REPUBLIC = re.compile(r"(?i)\b(republic|republik|rep[uú]blica|repubblica|jamhuriya|soviet socialist)\b")
KINGDOM = re.compile(r"(?i)\b(kingdom|empire|sultanate|caliphate|khanate|emirate|tsardom|shogunate|raj)\b")
NOT_PERSON = re.compile(
    r"(?i)\b(dynasty|dynasties|kingdom|empire|republic|sultanate|caliphate|khanate|emirate|duchy|archduchy|"
    r"county of|principality|confederation|confederacy|council|consiglio|senate|parliament|assembly|committee|"
    r"junta|directory|directorate|triumvirate|tetrarchy|captains regent|lords|regents|viceroys|governors|"
    r"consuls|presidium|politburo|interregnum|vacant|various|occupation|administration|house of|clan|monarchy|"
    r"government|collective|commission|federation|rule|regime|protectorate|colony|mandate|chiefs|chieftains|"
    r"kings|emperors|sultans|rulers|oligarchy|anarchy|civil war|unknown)\b")
TITLE_ONLY = {"consul", "consuls", "doge", "king", "emperor", "regent", "governor", "president", "ruler", "chief",
              "khan", "sultan", "pharaoh", "shah", "raja", "maharaja", "tsar", "prince", "duke", "count", "lord",
              "queen", "anonymous", "bishop", "abbot", "archbishop", "captain", "mayor", "podesta", "gonfaloniere",
              "stadtholder", "dictator", "tribune", "archon", "ephor", "satrap", "viceroy", "nawab", "nizam", "none",
              "n a", "head of the government", "head of state"}
CO_TITLE = re.compile(r"(?i)\b(co-|co |joint|regent|acting|junior|senior|associate|deputy|vice|consort|titular|"
                      r"pretender|anti-|rival|claimant|consul|tribune|archon|ephor|sub-king|subking|caesar|"
                      r"augustus|augusta|interim|provisional|in exile|exile)")


# ====================================================================== Wikidata, the outside witness

class Witness:
    def __init__(self):
        self.ok = os.path.exists(WD_CACHE)
        c = jload(WD_CACHE) if self.ok else {}
        self.persons = c.get("persons", {})
        self.states = c.get("states", {})
        self.qids = c.get("qids", {})
        self.capitals = c.get("capitals", [])
        self.statelike = c.get("statelike", {})
        self.roles = c.get("roles", {})
        self.source = c.get("source", "")

    @staticmethod
    def tol(prec):
        if prec is None:
            return None
        return 1 if prec >= 9 else 10 if prec == 8 else None

    @staticmethod
    def specific(v):
        """A name that points at one person: two real words, not 'Charles VII' or 'Didda'."""
        words = [w for w in re.split(r"[\s,]+", v) if w and not ROMAN.match(w)
                 and w.lower() not in ("the", "of", "von", "van", "de", "al", "el", "ibn", "bin", "i")]
        return len(words) >= 2

    def people(self, name, specific_only=False):
        import fact_audit_wd as W
        seen, out = set(), []
        for v in W.name_variants(name):
            if specific_only and not self.specific(v):
                continue
            for c in self.persons.get(v, []):
                key = tuple(c)
                if key not in seen:
                    seen.add(key)
                    out.append(c)
        return out

    def candidates(self, name, s, e):
        """People with this (specific) name whose lives come within 30 years of these years."""
        out = []
        for q, b, bp, d, dp in self.people(name, specific_only=True):
            tb, td = self.tol(bp), self.tol(dp)
            b_, d_ = (b if tb is not None else None), (d if td is not None else None)
            if b_ is not None and b_ > e + 30:
                continue
            if d_ is not None and d_ < s - 30:
                continue
            out.append((q, b_, tb, d_, td))
        return out

    def lifetime_check(self, name, s, e):
        """(verdict, candidate): 'after-death' when the only people of that name alive when the reign began
        had died at least 3 years before it ended; 'ok' when someone fits; None when Wikidata cannot say.
        (Namesakes born later or dead long before are other people and are ignored.)"""
        cands = self.candidates(name, s, e)
        if any((c[1] is None or c[1] <= s + c[2]) and (c[3] is None or c[3] >= e - c[4]) for c in cands):
            return "ok", None
        alive_at_start = [c for c in cands if c[1] is not None and c[3] is not None and c[1] <= s + c[2]
                          and c[3] >= s - c[4]]
        if alive_at_start and all(e - c[3] >= 3 for c in alive_at_start):
            return "after-death", max(alive_at_start, key=lambda c: c[3])
        return None, None

    def compatible_qids(self, name, s, e):
        return [c[0] for c in self.candidates(name, s, e)
                if (c[1] is None or c[1] <= s + c[2]) and (c[3] is None or c[3] >= e - c[4])]

    def not_a_ruler(self, name, title, s, e):
        """A philosopher or a strategist listed as a ruler: every matching person is one, with no office
        or title recorded in Wikidata, and the row's own title is a generic 'ruler of …'."""
        if RULER_JOB_WORDS.search(name) or re.search(r"(?i)emperor|king|queen|sultan|shah|khan|duke|count|prince|"
                                                     r"raja|pharaoh|tsar|caliph|emir|bey|mayor|president", title):
            return None
        qs = self.compatible_qids(name, s, e)
        if not qs or any(q not in self.roles for q in qs):
            return None
        jobs = []
        for q in qs:
            occ, held = self.roles[q]
            low = {o.lower() for o in occ}
            if held or not low & {"philosopher", "military strategist", "military theorist"}:
                return None
            if low & RULER_JOBS or any(RULER_JOB_WORDS.search(o) for o in low):
                return None
            jobs.append(f"{q}: " + ", ".join(sorted(low)))
        return "; ".join(jobs)


ROMAN = re.compile(r"^[IVXLCDM]+$|^\d+(st|nd|rd|th)?$")
RULER_JOBS = {"monarch", "politician", "aristocrat", "ruler", "sovereign", "statesperson", "noble", "nobleman",
              "military leader", "head of state", "king", "emperor", "regent", "governor", "dynast", "chieftain",
              "tribal chief", "warlord", "sultan", "pharaoh", "khan", "feudatory", "official", "civil servant"}
RULER_JOB_WORDS = re.compile(r"(?i)king|queen|prince|emperor|monarch|ruler|noble|duke|count|lord|chief|sultan|shah|"
                             r"raja|pharaoh|khan|politic|statesman|governor|regent|consul|minister")
NON_RULER_JOBS = {"philosopher", "writer", "poet", "military strategist", "military theorist", "historian",
                  "scholar", "painter", "composer", "mathematician", "astronomer", "physician", "scientist",
                  "engineer", "architect", "sculptor", "actor", "singer", "musician", "athlete", "economist",
                  "merchant", "explorer", "teacher", "theologian", "essayist", "novelist", "playwright",
                  "linguist", "botanist", "chemist", "physicist", "geographer", "translator", "calligrapher",
                  "military officer", "soldier", "lawyer", "jurist", "journalist", "film director", "photographer",
                  "association football player", "inventor", "businessperson", "monk", "missionary"}


def life(c):
    if not c:
        return ""
    q, b, _tb, d, _td = c
    return f"Wikidata {q}: born {yr(b) if b is not None else '?'}, died {yr(d) if d is not None else '?'}"


# ====================================================================== 1. rulers

GOV_TITLE = re.compile(r"(?i)prime minister|\bpremier\b|chancellor|\bminister|chairman of (?:the )?(?:council|committee)"
                       r"(?! of state)|grand vizier|\bvizier\b|chief minister|first minister|head of (?:the )?government|"
                       r"president of the (?:ministry|council of ministers|government(?! junta))")
# Step 25: a Council of State's chairman (Liberia 1994-1996) and a government junta's president (Peru) were heads of
# state; the rule no longer counts them as prime ministers.
CLAIMANT = re.compile(r"(?i)\bclaimants?\b|\bpretenders?\b")
GROUP = re.compile(r"(?i)^house of\b|\b(dynasty|dynasties|lords|rule|regime|occupation|administration|mandate|colony|"
                   r"protectorate|clan|family|unknown|various|vacant|interregnum|anarchy|civil war|kings|emperors|"
                   r"sultans|rulers|chiefs|chieftains|monarchy|captains regent|consiglio)\b")


def check_rulers(pf, mi, wd, polity_names):
    """Heads of state (said in game: 'ruled by …') and heads of government (shown in /ee here)."""
    shown_rows = {}          # (q, row index) -> years the game names this head row
    bad_head = {}            # (q, row index) -> (rule, sure)
    for p in pf:
        q, sname = p["q"], p["n"]
        ivs = mi.qid_iv.get(q, [])
        own = {plain(sname), plain(p.get("a", ""))} | {plain(n) for n in mi.qid_names.get(q, {})}
        heads = p.get("head", [])
        # which head row the game names each year (LeaderRegister.Facts.latest: latest accession wins,
        # the first listed on a tie), only in the years this state is on the map
        if heads and ivs:
            lo = max(min(r[2] for r in heads), -3500)
            hi = min(max(r[3] for r in heads), NOW)
            for a_, b_ in ivs:
                for y in range(max(a_, lo), min(b_, hi) + 1):
                    best = None
                    for i, r in enumerate(heads):
                        if r[2] <= y <= r[3] and (best is None or r[2] > heads[best][2]):
                            best = i
                    if best is not None:
                        shown_rows.setdefault((q, best), []).append(y)
        for kind in ("head", "gov"):
            rows = p.get(kind, [])
            for i, row_ in enumerate(rows):
                name, title, s, e = row_[:4]
                marked = len(row_) > 4 and row_[4] == 1      # step 26 (A5): the data marks it as an estimate
                yrs = shown_rows.get((q, i), []) if kind == "head" else []
                seen = ("yes" if yrs else "no") if kind == "head" else ("/ee here" if overlap(ivs, s, e) else "no")
                item = f"{sname}: {name} ({title}) {span(s, e)}"
                where = f"said in game in {len(yrs)} years" if yrs else ""
                low = plain(name)

                def flag(rule, sure, detail):
                    find("rulers", rule, sure, item, (detail + ("; " + where if where else "")).strip("; "),
                         seen, "polity_facts.json.gz")
                    if kind == "head":
                        bad_head[(q, i)] = (rule, sure)

                state_name = low in own or (low in polity_names and (len(low.split()) >= 2 or KINGDOM.search(name)
                                                                     or REPUBLIC.search(name)))
                if state_name:
                    flag("a state named as the ruler", WRONG, "the 'ruler' is the name of a state")
                    continue
                if low in TITLE_ONLY:
                    flag("a title named as the ruler", WRONG, "the 'ruler' is a title, not a name")
                    continue
                if CLAIMANT.search(name):
                    flag("a claimant named as the ruler", WRONG, "claimants to a throne did not rule")
                    continue
                if GROUP.search(name):
                    flag("a group named as the ruler", ODD, "a dynasty, family or period, not one person")
                    continue
                if s > NOW:
                    flag("years in the future", WRONG, "a BC year written as AD")
                    continue
                nxt = rows[i + 1][2] if i + 1 < len(rows) else None
                if (e > NOW or (e == s + 25 and (nxt is None or nxt > e))) and not marked:
                    find("rulers", "end year guessed", ODD, item,
                         "the builder's guess (start + 25 years) because the source gave no end", seen,
                         "polity_facts.json.gz")
                same_person = any(j != i and plain(r2[0]) == low and r2[2] <= e and r2[3] >= s
                                  and not GOV_TITLE.search(r2[1]) for j, r2 in enumerate(rows))
                if (kind == "head" and GOV_TITLE.search(title) and yrs and not same_person
                        and low not in ("vladimir lenin",)):
                    flag("a head of government named as the ruler", WRONG,
                         "the head of state is hidden behind a prime minister or chairman")
                    continue
                length = e - s
                verdict, cand = wd.lifetime_check(name, s, e) if wd.ok else (None, None)
                if length > 100:
                    flag("impossible reign length", WRONG, f"{length} years" + (f"; {life(cand)}" if cand else ""))
                    continue
                if verdict == "after-death":
                    flag("reign goes on after the ruler died", LIKELY,
                         life(cand) + f"; the reign is given until {yr(e)}")
                    continue
                job = wd.not_a_ruler(name, title, s, e) if wd.ok and kind == "head" else None
                if job:
                    flag("not a ruler at all", LIKELY, f"Wikidata: {job}; no office or title recorded")
                    continue
                if length > 60 and verdict is None:
                    find("rulers", "very long reign", ODD, item, f"{length} years; Wikidata has no dates to compare"
                         + ("; " + where if where else ""), seen, "polity_facts.json.gz")
                bad = []
                if re.search(r"\[\[|\]\]|\{\{|<|>|&[a-z]+;|\|", name):
                    bad.append("markup in the name")
                if re.search(r'["“”]', name):
                    bad.append("nicknames in quotes are said aloud")
                if re.search(r"\(\s*(?:born|b\.|died|d\.|r\.|reigned|c\.)?\s*\d", name):
                    bad.append("dates inside the name")
                if bad:
                    find("rulers", "untidy name", ODD, item, "; ".join(bad), seen, "polity_facts.json.gz")
            # the same person twice, same title, with at least two years in common
            by = collections.defaultdict(list)
            for i, r in enumerate(rows):
                by[(plain(r[0]), plain(r[1]))].append(r)
            for k, lst in by.items():
                for a_ in range(len(lst)):
                    for b_ in range(a_ + 1, len(lst)):
                        ra, rb = lst[a_], lst[b_]
                        if min(ra[3], rb[3]) - max(ra[2], rb[2]) >= 1:
                            find("rulers", "listed twice", ODD, f"{sname}: {ra[0]} ({ra[1]}) {span(ra[2], ra[3])} "
                                 f"and {span(rb[2], rb[3])}", "the same person and title twice, overlapping", "",
                                 "polity_facts.json.gz")
        # a republic ruled by a monarch, a kingdom ruled by a president: per year, as the game says it
        for i, row_ in enumerate(heads):
            name, title, s, e = row_[:4]
            yrs = shown_rows.get((q, i), [])
            if not yrs or (q, i) in bad_head:
                continue
            rep = collections.Counter()
            kin = collections.Counter()
            for y in yrs:
                for n in mi.names_in(q, y):
                    if REPUBLIC.search(n) and MONARCH.search(title):
                        rep[n] += 1
                    if KINGDOM.search(n) and PRESIDENT.search(title) and not MONARCH.search(title):
                        kin[n] += 1
            for n, c in rep.items():
                find("state names", "a republic ruled by a monarch", WRONG,
                     f"“{n}, ruled by {name} ({title})”", f"said in {c} years ({span(min(yrs), max(yrs))})", "yes",
                     "world_rulers + polity_facts")
                bad_head.setdefault((q, i), ("a republic ruled by a monarch", WRONG))
            for n, c in kin.items():
                find("state names", "a kingdom ruled by a president", WRONG,
                     f"“{n}, ruled by {name} ({title})”", f"said in {c} years ({span(min(yrs), max(yrs))})", "yes",
                     "world_rulers + polity_facts")
                bad_head.setdefault((q, i), ("a kingdom ruled by a president", WRONG))
        # gaps: the state is on the map, rulers are named before and after, nobody in between
        if heads and ivs:
            covered = set()
            for r in heads:
                covered.update(range(max(r[2], -3500), min(r[3], NOW) + 1))
            lo, hi = min(r[2] for r in heads), min(max(r[3] for r in heads), NOW)
            run, runs = [], []
            for a_, b_ in ivs:
                for y in range(max(a_, lo), min(b_, hi) + 1):
                    if y in covered:
                        if run:
                            runs.append(run)
                            run = []
                    else:
                        if run and y != run[-1] + 1:
                            runs.append(run)
                            run = []
                        run.append(y)
            if run:
                runs.append(run)
            for r in runs:
                n = len(r)
                if n >= 3 or (n >= 2 and r[0] >= 1800):
                    find("rulers", "no ruler named", MISSING, f"{sname}: {span(r[0], r[-1])}",
                         f"{n} years with no head of state, between named rulers", "yes", "polity_facts.json.gz")
            last_map = max(b_ for a_, b_ in ivs)
            last_head = max(r[3] for r in heads)
            if last_map >= 1950 and last_map - last_head >= 5 and last_head >= min(a_ for a_, b_ in ivs):
                find("rulers", "rulers stop too early", MISSING, f"{sname}: after {yr(last_head)}",
                     f"on the map until {yr(last_map)}, but the last ruler ends in {yr(last_head)}", "yes",
                     "polity_facts.json.gz")
    return shown_rows, bad_head


# ====================================================================== 2. state names

def check_state_names(mi, wd):
    """Is each name on the border map used only in the years a state of that name existed? The witnesses
    are Wikidata items named so that are states (not bands or ships), and the map's own Wikidata item
    when its label fits the name."""
    bad_years = {}           # name -> (first good year, last good year), for the people-weighted pass
    if not wd.ok:
        return bad_years

    def tol(p):
        return 1 if (p or 0) >= 9 else 10 if p == 8 else None
    for name, ivs in sorted(mi.name_iv.items()):
        first, last = ivs[0][0], ivs[-1][1]
        cands = [tuple(c) for c in wd.states.get(name, []) if wd.statelike.get(c[0])]
        for q in mi.name_qids.get(name, ()):
            lab, inc, ip, dis, dp = (wd.qids.get(q) or [None] * 5)
            if lab and articleFits(name, lab):
                cands.append((q, inc, ip, dis, dp))
        spans = []
        for q, inc, ip, dis, dp in cands:
            ti, td = tol(ip), tol(dp)
            if (inc is None or ti is None) and (dis is None or td is None):
                continue
            if inc is not None and inc > last:          # a later namesake, not this state
                continue
            a_ = inc - ti if inc is not None and ti is not None else -10 ** 6
            b_ = dis + td if dis is not None and td is not None else 10 ** 6
            spans.append((a_, b_, q, inc, dis))
        if not spans:
            continue
        early = late = 0
        ended = began = None
        for a_, b_ in ivs:
            for y in range(a_, b_ + 1):
                if any(x[0] <= y <= x[1] for x in spans):
                    continue
                before = [x for x in spans if x[1] < y]
                if before:
                    late += 1
                    ended = max(before, key=lambda x: x[1])
                else:
                    early += 1
                    began = min(spans, key=lambda x: x[0])
        if late >= 25:
            find("state names", "name used after the state ended", WRONG if late >= 50 else LIKELY,
                 f"“{name}” on the map until {yr(last)}",
                 f"Wikidata {ended[2]}: the state of that name ended in {yr(ended[4])}; the name is shown {late} "
                 f"years when no state had it", "yes", "world_rulers / deccan_rulers")
        if early >= 50:
            find("state names", "name used before the state began", LIKELY,
                 f"“{name}” on the map from {yr(first)}",
                 f"Wikidata {began[2]}: the state of that name began in {yr(began[3])}; the name is shown "
                 f"{early} years before it", "yes", "world_rulers / deccan_rulers")
        if late >= 25 or early >= 50:
            bad_years[name] = spans
    return bad_years


MICRO = {"Q237", "Q238", "Q347", "Q235", "Q228"}      # Vatican, San Marino, Liechtenstein, Monaco, Andorra
ALIASES = {"Q41": "hellenic greek", "Q142": "french", "Q27": "eire éire irish", "Q1016": "libyan",
           "Q889": "taliban afghan", "Q219060": "israel"}


def check_capitals(wd, reg, dec):
    """Today's capitals: does the map put each one in its own country in 2000 and 2020?"""
    for cq, clabel, caplabel, lat, lon in wd.capitals:
        for y in (2000, 2020):
            q, n = where(reg, dec, lat, lon, y)
            if n is None:
                find("state names", "capital on no state", MISSING, f"{caplabel} ({clabel}) in {y}",
                     "the map has no state at this capital", "yes", "world_rulers")
                continue
            if q == cq:
                continue
            cw = (set(plain(clabel).split()) | set(plain(ALIASES.get(cq, "")).split())) - {
                "the", "of", "and", "republic", "kingdom", "state", "democratic", "people", "s", "federal",
                "islamic", "united", "union"}
            if cw & set(plain(n).split()):
                continue
            if cq in MICRO:
                find("state names", "capital too small for the map", ODD, f"{caplabel} in {y}",
                     f"the map says “{n}”: {clabel} is smaller than one map square", "yes", "world_rulers")
                continue
            find("state names", "capital in another country", LIKELY, f"{caplabel} in {y}",
                 f"the map says “{n}”; it is the capital of {clabel}", "yes", "world_rulers")


def where(reg, dec, lat, lon, y):
    """(qid, name) of the state at a point and year, the way the game looks it up."""
    di, dkm = dec.nearest(lat, lon)
    if di is not None and dkm <= 60:
        for n, s, e, q in dec.tls[dec.pl[di][2]]:
            if s <= y <= e and not n.startswith("("):
                return q, n
    pol = reg.at(lat, lon, y)
    if pol:
        return pol[1], pol[0]
    return None, None


# ====================================================================== 3. languages and faiths

LANG_FROM = {  # earliest year a language under this name can be meant (generous: spoken before written)
    "English": 450, "French": 800, "Spanish": 900, "Castilian": 900, "Portuguese": 1100, "Italian": 900,
    "German": 700, "Dutch": 900, "Russian": 1200, "Ukrainian": 1300, "Belarusian": 1300, "Polish": 1000,
    "Czech": 1000, "Slovak": 1000, "Hungarian": 900, "Turkish": 1000, "Ottoman Turkish": 1299, "Hindi": 1000,
    "Urdu": 1500, "Hindustani": 1300, "Bengali": 900, "Marathi": 900, "Gujarati": 1100, "Punjabi": 1000,
    "Telugu": 500, "Kannada": 400, "Malayalam": 800, "Sinhala": 300, "Malay": 600, "Javanese": 700,
    "Vietnamese": 900, "Thai": 1200, "Lao": 1300, "Burmese": 1000, "Japanese": 600, "Mongolian": 1100,
    "Swahili": 900, "Albanian": 1000, "Romanian": 1000, "Swedish": 800, "Danish": 800, "Norwegian": 800,
    "Icelandic": 870, "Catalan": 900, "Occitan": 900, "Galician": 1000, "Serbian": 850, "Croatian": 850,
    "Bulgarian": 850, "Georgian": -300, "Armenian": -600, "Amharic": 1200, "Tagalog": 900, "Filipino": 1937,
    "Afrikaans": 1700, "Yiddish": 1000, "Modern Greek": 1453, "Turkmen": 1000, "Uzbek": 1500, "Kazakh": 1400,
    "Azerbaijani": 1000, "Tatar": 1200, "Kyrgyz": 1500, "Pashto": 1000, "Nepali": 1300, "Khmer": 600,
    "Korean": 500, "Manchu": 1600, "Arabic": -900, "Persian": -600, "Hebrew": -1200, "Latin": -700,
}
REL_FROM = {
    "Christianity": 30, "Islam": 610, "Sunni Islam": 632, "Shia Islam": 632, "Sunni": 632, "Shia": 632,
    "Ibadi Islam": 650, "Buddhism": -530, "Theravada Buddhism": -250, "Mahayana Buddhism": -100,
    "Tibetan Buddhism": 650, "Jainism": -900, "Confucianism": -500, "Taoism": -600, "Protestantism": 1517,
    "Protestant": 1517, "Lutheranism": 1517, "Lutheran": 1517, "Calvinism": 1536, "Dutch Reformed": 1571,
    "Anglicanism": 1534, "Church of England": 1534, "Sikhism": 1499, "Manichaeism": 240, "Arianism": 318,
    "Nestorian Christianity": 431, "Bahá'í Faith": 1863, "Mormonism": 1830, "State atheism": 1917,
    "Chalcedonian Christianity": 451, "Druze": 1017, "Wahhabism": 1740, "State Shinto": 1868,
    "Armenian Apostolic Church": 301, "Russian Orthodoxy": 988, "Catholicism": 30, "Roman Catholicism": 30,
    "Roman Catholic": 30, "Catholic": 30, "Catholic Church": 30, "Eastern Orthodoxy": 30, "Eastern Orthodox": 30,
    "Orthodox Christianity": 30, "Greek Orthodoxy": 30, "Greek Orthodox": 30, "Nicene Christianity": 325,
    "Latin Christianity": 30, "Eastern Orthodox Church": 30, "Coptic Orthodox Church": 451,
    "Zoroastrianism": -1500, "Hinduism": -1500, "Vaishnavism": -300, "Shaivism": -300,
}
LANG_JUNK = re.compile(r"(?i)\bsign\b|gŭl|hangul|hanja|\bscript\b|alphabet|cyrillic|latin script|devanagari|"
                       r"\bkana\b|braille|^over \d+|languages|\bvarious\b|^official$|official(ly)?\b|regional|"
                       r"\blocal\b|vernacular|^none\b|popularly|as well as|possible|\bwith\b")
REL_JUNK = re.compile(r"(?i)^from |\d|century|majority|minority|^state$|religions?:|^see |;|,")
FAITH_SKIP = re.compile(r"(?i)^(various|several|many|mixed|official|state)")


def shown_faith(rels, periods=None, year=None):
    """The faith the game says: since step 25 the faith of the year ('relP') when one covers it, else the first."""
    for a, b, f in periods or []:
        if year is not None and a <= year <= b:
            return f
    for r in rels:
        if not FAITH_SKIP.match(r.lower()):
            return r
    return None


def check_culture(pf, mi):
    for p in pf:
        q, n = p["q"], p["n"]
        ivs = mi.qid_iv.get(q, [])
        on_map = bool(ivs)
        first, last = (ivs[0][0], ivs[-1][1]) if ivs else (None, None)
        langs = p.get("lang", [])
        for i, l in enumerate(langs):
            seen = "yes" if on_map and i < 2 else "no"
            if LANG_JUNK.search(l):
                kind = ("a sign language" if re.search(r"(?i)\bsign\b", l) else
                        "a writing system, not a language" if re.search(r"(?i)gŭl|hangul|hanja|script|alphabet|"
                                                                         r"cyrillic|devanagari|kana|braille", l)
                        else "not a language name")
                find("languages", "not a spoken language", WRONG if seen == "yes" else ODD, f"{n}: “{l}”", kind,
                     seen, "polity_facts.json.gz")
            base = LANG_FROM.get(l)
            if base is not None and on_map and last < base:
                find("languages", "language older than its time", LIKELY, f"{n} ({span(first, last)}): {l}",
                     f"{l} is not known before about {yr(base)}", seen, "polity_facts.json.gz")
        rels = p.get("rel", [])
        sf = shown_faith(rels)
        periods = p.get("relP", [])
        for r in rels:
            seen = "yes" if on_map and r == sf else "no"
            if periods and REL_FROM.get(r) is not None:
                # the faith of the year is said instead; a later faith is only said in its own years
                if all(not (f == r and a < REL_FROM[r]) for a, b, f in periods):
                    continue
            if REL_JUNK.search(r) and not FAITH_SKIP.match(r.lower()):
                find("faiths", "not a faith name", WRONG if seen == "yes" else ODD, f"{n}: “{r}”",
                     "said as 'The main faith here is …'" if seen == "yes" else "", seen, "polity_facts.json.gz")
            base = REL_FROM.get(r)
            if base is not None and on_map and last < base:
                find("faiths", "faith older than its founding", WRONG if seen == "yes" else LIKELY,
                     f"{n} ({span(first, last)}): {r}", f"{r} began about {yr(base)}", seen, "polity_facts.json.gz")
        for y, shares in p.get("relY", []):
            if any(s[1] < 0 or s[1] > 100 for s in shares):
                find("faiths", "impossible share", WRONG, f"{n} {y}", "a share below 0% or above 100%", "yes",
                     "polity_facts.json.gz")


# ====================================================================== 4. events

YEAR_WORDS = r"(?:BC|BCE|AD|CE)"
MODERN_NOTE = re.compile(r"\((?:modern|present[- ]day|today'?s?|now)[^)]*\)|present-day (?:the )?[A-Z][\w-]+|"
                         r"what is now (?:the )?[A-Z][\w ,-]+|in modern (?:the )?[A-Z][\w-]+|modern-day [A-Z][\w-]+")
NAVAL = re.compile(r"(?i)naval|\bsea\b|ocean|\bbay\b|gulf|strait|channel|\bcape\b|island|sinking|sunk|wreck|"
                   r"torpedo|fleet|\bship|submarine|convoy|maritime|pirat|tsunami|earthquake|eruption|volcano|"
                   r"offshore|reef|atoll|archipelago|harbo|coast|lake|river|flight|\bair\b|crash|plane|aircraft|"
                   r"whal|expedition|voyage|discover|explor|sail|navigat|landing|blockade|\bpier\b|port\b|"
                   r"mediterranean|aegean|baltic|caribbean|pacific|atlantic|arctic|antarctic|cruise|ferry|boat|"
                   r"oil spill|storm|cyclone|hurricane|typhoon|ucdp|fighting in|vessel|\bdeep\b|eclipse|meteor|comet")


ISLANDS = re.compile(r"(?i)maldiv|nauru|tahiti|papeete|fiji|seychell|mauriti|malta|bahrain|singapore|hawai|samoa|"
                     r"tonga|cocos|bermuda|azores|canar|cape verde|comoro|marshall|kiribati|tuvalu|palau|micrones|"
                     r"guam|pitcairn|easter island|gal[aá]pagos|faroe|greenland|antarctic|svalbard|caroline|mariana|"
                     r"solomon|vanuatu|hebrides|zanzibar|bahamas|barbados|grenada|antigua|kitts|lucia|vincent|"
                     r"dominica|tristan|helena|ascension|chagos|diego garcia|andaman|nicobar|lakshadweep|okinawa|"
                     r"ryukyu|bonin|iwo jima|midway|wake|kwajalein|tarawa|guadalcanal|rabaul|truk|saipan|tinian|"
                     r"peleliu|christmas island|norfolk island|chatham|kerguelen|falkland|south georgia|reunion|"
                     r"réunion|mayotte|madeira|socotra|qatar|cyprus|crete|rhodes|sardinia|sicily|corsica|balearic")


def years_named(text, hazard=False):
    """Explicit years the event's own name gives: (year, how exact). Only the safe places to look:
    a year in front ('546 BC—…', '1820: …', 'AD 8 – …'), a year in front of a short title or a disaster
    ('1868 Ecuador earthquakes', '1911 Revolution'), one year in brackets ('Battle of Mława (1920)'),
    and a short title ending in one ('Albanian Revolt of 1911')."""
    out = []
    t = MODERN_NOTE.sub(" ", text)
    if re.match(r"^(c\.\s*)?\d{1,4}\s*(BCE?|AD|CE)?\s*[–-]\s*\d{1,4}", t):
        return out                                   # a range like 'c. 2900 BC–2334 BC:'
    m = re.match(r"^(c\.\s*)?(\d{3,4})\s*(BC|BCE|AD|CE)?\s*(?::|\s[–—-]\s|[–—]\s?)", t) or \
        re.match(r"^(c\.\s*)?(\d{1,4})\s*(BC|BCE|AD|CE)\s*(?::|[–—-])", t)
    if m:
        y = int(m.group(2))
        out.append((-y if m.group(3) in ("BC", "BCE") else y, 25 if m.group(1) else 1))
    m = re.match(r"^AD\s(\d{1,4})\b", t)
    if m:
        out.append((int(m.group(1)), 1))
    if hazard or len(t) < 70:
        m = re.match(r"^(\d{3,4})\s+(?!BCE?\b|AD\b|CE\b)[A-Z]", t)
        if m:
            out.append((int(m.group(1)), 1))
    if len(t) < 70:
        for m in re.finditer(r"\((?:[A-Z][a-z]+(?:[–-][A-Z][a-z]+)?\s)?(\d{3,4})\)", t):
            out.append((int(m.group(1)), 1))
        for m in re.finditer(r"\b(?:of|in)\s(\d{3,4})\s*$", t):
            out.append((int(m.group(1)), 1))
    return out


BROKEN = [
    (re.compile(r"^Q\d+$"), "no name: only a Wikidata number", WRONG),
    (re.compile(r"^\d{1,2}\s*[–—-]\s"), "a day number left at the start (the month was cut off)", ODD),
    (re.compile(r"^\d{1,2}(?::\d\d)?\s*(?:pm|am)?\s*[:–—-]\s"), "a leftover number at the start", ODD),
    (re.compile(r"^(?:ca\.|c\.|approximate date|approx\.|circa)\s*[A-Za-z]*\s*[–—-]"), "a leftover date note at the start", ODD),
    (re.compile(r"\[\[|\]\]|\{\{|\}\}"), "wiki markup", ODD),
    (re.compile(r"<[a-zA-Z/][^>]*>"), "an HTML tag", ODD),
    (re.compile(r"&[a-z]+;|&#\d+;"), "an HTML code", ODD),
    (re.compile(r"\|"), "a table bar", ODD),
    (re.compile(r"^[^\w\"'(“‘¿¡]"), "starts with a symbol", ODD),
    (re.compile(r"^(?:and|or|but|which|who|whom|whose|with|to|by)\s"), "starts in the middle of a sentence", ODD),
    (re.compile(r"\s[–—-]\s*$|[:,;(]\s*$"), "ends in the middle of a sentence", ODD),
    (re.compile(r"\(\s*\)|\.\s*,|,\s*,|\s,\s(?:this|that|which)\b"), "a gap where something was cut out", ODD),
    (re.compile(r"\bcitation needed\b|\[\d+\]|\[note"), "a footnote", ODD),
]
OCR = re.compile(r"\^|~|[a-z]- [a-z]|[a-z]\d[a-z]|eiglit|recoV|I’ersian|Khiljl|\bUwt\b")


def check_events(hyde_land):
    idx = jload(f"{HIST}/index.json")
    allev = []
    for f in idx["packs"]:
        d = jload(f"{HIST}/{f}")
        for e in d.get("events", []):
            s = e.get("start", e.get("year"))
            en = e.get("end", s)
            allev.append((f, e, s, en))
    counts = collections.Counter()
    by_name = collections.defaultdict(list)
    for f, e, s, en in allev:
        name = e.get("name") or ""
        item = f"{name[:140]} ({span(s, en)})"
        lat, lon = e.get("lat"), e.get("lon")
        if s is None:
            find("events", "no year", WRONG, item, "", "", f)
            continue
        if s > NOW or (en is not None and en < s):
            find("events", "impossible years", WRONG, item, "starts in the future" if s > NOW else "ends before it starts",
                 "yes", f)
            continue
        if lat is not None and (not -90 <= lat <= 90 or not -180 <= lon <= 180 or (abs(lat) < 0.01 and abs(lon) < 0.01)):
            find("events", "impossible place", WRONG, item, f"lat {lat}, lon {lon}", "yes", f)
        for rx, what, sure in BROKEN:
            if rx.search(name):
                find("events", "broken text", sure, item, what, "yes", f)
                break
        else:
            if f == "deccan_events.json" and OCR.search(name):
                find("events", "broken text", ODD, item, "scanning (OCR) errors from the 1909 gazetteer", "yes", f)
        for y, slack in years_named(name, f == "events_hazards.json.gz"):
            lo_ok, hi_ok = s - slack, max(en, s) + slack
            if f == "events_hazards.json.gz" and ("COVID" in name or "pandemic" in name.lower()):
                hi_ok += 3
            if not (lo_ok <= y <= hi_ok):
                if 0 < s < 32 and y >= 100:
                    find("events", "a day of the month read as the year", WRONG, item,
                         f"the text says {yr(y)}; the event is dated AD {s}", "yes", f)
                else:
                    find("events", "the name gives another year", LIKELY, item, f"the text says {yr(y)}", "yes", f)
                break
        if lat is not None and hyde_land is not None and e.get("kind") not in ("conflict",) and abs(lat) < 85:
            r_, c_ = int((lat + 90) / 0.5), int((lon + 180) / 0.5)
            near_land = any(hyde_land.get(((r_ + dy) % 360, (c_ + dx) % 720), False)
                            for dy in (-1, 0, 1) for dx in (-1, 0, 1))
            if (not near_land and not NAVAL.search(name) and not ISLANDS.search(name)
                    and not re.fullmatch(r"Q\d+", name) and (e.get("radiusKm") or 0) < 100):
                find("events", "placed at sea", LIKELY, item, f"lat {lat:.2f}, lon {lon:.2f}: no land within ~50 km",
                     "yes", f)
        key = plain(name)
        if lat is not None and len(key) > 8 and re.match(r"(?i)(battle|siege|treaty|sack|fall|capture|massacre) ", name):
            by_name[key].append((s, lat, lon, f, name))
        counts[f] += 1
    return len(allev)


# ====================================================================== 5. famous people

DESC_JUNK = re.compile(r"(?i)ID=|peerage person|wikimedia|disambiguation|\bQ\d{3,}\b|family name|given name|"
                       r"\bsurname\b|category:|\btaxon\b|\bspecies\b|\bgenus\b|list of|https?://|^\W|^[),;:]")


def check_people():
    rows = jload(f"{HIST}/famous_people.json.gz")["people"]
    for name, desc, b, d, q, lat, lon, rad in rows:
        item = f"{name}" + (f", {desc[:60]}" if desc else "") + f" ({yr(b) if b is not None else '?'}–"
        item += f"{yr(d) if d is not None else '?'})"
        if b is not None and d is not None and d < b:
            find("famous people", "died before being born", WRONG, item, "", "yes", "famous_people.json.gz")
        elif b is not None and d is not None and d - b > 110:
            find("famous people", "impossible lifespan", WRONG, item,
                 f"{d - b} years: talked about as alive for {d - b - 20} years", "yes", "famous_people.json.gz")
        if b is not None and b > NOW or d is not None and d > NOW:
            find("famous people", "years in the future", WRONG, item, "", "yes", "famous_people.json.gz")
        if re.search(r"&[a-z]+;|&#\d+;|\[\[|\{\{|<", name or ""):
            find("famous people", "broken text", ODD, item, "an HTML code or markup in the name", "yes",
                 "famous_people.json.gz")
        if desc and DESC_JUNK.search(desc):
            find("famous people", "broken description", ODD, item, "said aloud after the name", "yes",
                 "famous_people.json.gz")
        if not -90 <= lat <= 90 or not -180 <= lon <= 180:
            find("famous people", "impossible place", WRONG, item, f"lat {lat}, lon {lon}", "yes",
                 "famous_people.json.gz")
    return rows


# ====================================================================== 6. trade routes, places

def hav(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = p2 - p1, math.radians(lo2 - lo1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371 * math.asin(min(1, math.sqrt(a)))


def check_routes():
    d = jload(f"{HIST}/trade_routes.json.gz")
    for r in d["routes"]:
        towns = r["towns"]
        lim = 2500 if r.get("kind") == "sea" else 1500
        for i, (n, la, lo) in enumerate(towns):
            others = [hav(la, lo, t[1], t[2]) for j, t in enumerate(towns) if j != i]
            if others and min(others) > lim:
                find("trade routes", "town far from its route", LIKELY, f"{r['name']}: {n}",
                     f"{min(others):.0f} km from every other town of the route (lat {la}, lon {lo})", "yes",
                     "trade_routes.json.gz")
        if r["start"] >= r["end"]:
            find("trade routes", "impossible years", WRONG, r["name"], f"{r['start']}–{r['end']}", "yes",
                 "trade_routes.json.gz")
    for name, main, s, e, pts in d["roads"]:
        if s > e:
            find("trade routes", "road ends before it starts", WRONG, name, f"{s}–{e}", "yes", "trade_routes.json.gz")


def check_places():
    idx = jload(f"{HIST}/index.json")
    n = 0
    for f in idx["packs"]:
        d = jload(f"{HIST}/{f}")
        for s in d.get("sites", []):
            n += 1
            a, b = s.get("occupiedStart"), s.get("occupiedEnd")
            item = f"{s.get('name') or s.get('id')} ({f})"
            lat, lon = s.get("lat"), s.get("lon")
            if lat is None or not -90 <= lat <= 90 or not -180 <= lon <= 180 or (abs(lat) < .01 and abs(lon) < .01):
                find("places", "impossible place", WRONG, item, f"lat {lat}, lon {lon}", "yes", f)
            if a is not None and b is not None and b < a:
                find("places", "abandoned before founded", WRONG, item, f"{a}–{b}", "yes", f)
            if a is not None and a > NOW:
                find("places", "founded in the future", WRONG, item, f"{a}", "yes", f)
    return n


# ====================================================================== 7. the small foundation files

def check_foundation(wd):
    civs = jload(f"{ETER}/civilizations/foundation_civilizations.json")
    for c in civs:
        a, p, b = c.get("foundingYear"), c.get("peakYear"), c.get("fallYear")
        item = f"{c.get('name')} ({c.get('id')})"
        if a is not None and b is not None and b < a:
            find("foundation data", "falls before it is founded", WRONG, item, f"{a}–{b}", "yes",
                 "foundation_civilizations.json")
        if p is not None and a is not None and b is not None and not (a <= p <= b):
            find("foundation data", "peak outside its own years", WRONG, item, f"founded {a}, peak {p}, fell {b}",
                 "yes", "foundation_civilizations.json")
    for v in jload(f"{ETER}/vips/foundation_vips.json"):
        b, d = v.get("birthYear"), v.get("historicalDeathYear")
        item = f"{v['name']} ({yr(b)}–{yr(d) if d is not None else '?'})"
        if b is not None and d is not None and (d < b or d - b > 110):
            find("foundation data", "VIP with impossible years", WRONG, item, "", "yes", "foundation_vips.json")
    for m in MANUAL:
        find(*m)


# Read by hand: the small foundation files (133 civilizations, 76 events, 102 VIPs, 2 religions, 7 technologies,
# 2 buildings, 2 climate events). Dates and places there are right; these are the exceptions.
MANUAL = [
    ("foundation data", "placeholder numbers", ODD, "foundation_events.json: casualties of all 76 events",
     "every war has 5,000 soldiers and 20,000 civilians killed, every disaster 20,000 (Stalingrad, the Black Death, "
     "the Titanic alike); the game never shows these numbers", "no", "foundation_events.json"),
    ("foundation data", "placeholder numbers", ODD, "foundation_events.json: durationYears of all 76 events",
     "every event lasts 1 year, also the Spanish flu (1918-1920), the Black Death (1347-1351) and the Antonine "
     "Plague (165-180); the event chain uses this, so these stay 'live' for one year only", "yes",
     "foundation_events.json"),
    ("foundation data", "wrong civilization", ODD, "Archimedes of Syracuse (VIP)",
     "listed under Athens; he lived in Syracuse (his spawn point is right)", "yes", "foundation_vips.json"),
    ("foundation data", "wrong civilization", ODD, "Siddhartha Gautama, the Buddha (VIP)",
     "listed under the Maurya Empire, which began about 160 years after his death", "yes", "foundation_vips.json"),
    ("foundation data", "wrong civilization", ODD, "Oda Nobunaga and Toyotomi Hideyoshi (VIPs)",
     "listed under the Tokugawa Shogunate, which began in 1603, after both had died", "yes",
     "foundation_vips.json"),
    ("foundation data", "VIP years", LIKELY, "Chandragupta II (VIP): born 375",
     "375 is the year he became king; his birth year is unknown (about 340s)", "yes", "foundation_vips.json"),
    ("foundation data", "odd civilization fact", ODD, "Rome (civilization): government 'republic'",
     "one entry covers 753 BC-AD 476 with its peak in AD 117, under emperors", "yes",
     "foundation_civilizations.json"),
    ("foundation data", "odd civilization fact", ODD, "Goguryeo (civilization): later name 'Goryeo'",
     "Goryeo (918-1392) was a different, later kingdom", "yes", "foundation_civilizations.json"),
    ("foundation data", "odd civilization fact", ODD, "Ghana Empire (civilization): religion 'traditional_islam'",
     "the kings kept the traditional Soninke religion; Islam was the merchants' faith", "yes",
     "foundation_civilizations.json"),
    ("foundation data", "missing value", ODD, "British India (civilization)",
     "religion and population are empty (null)", "yes", "foundation_civilizations.json"),
]


# ====================================================================== 8. how many people would hear it

def articleFits(state, article):
    stop = {"the", "of", "and", "empire", "kingdom", "dynasty", "state", "states", "republic", "sultanate",
            "caliphate", "principality", "duchy", "great", "first", "second", "third", "later", "early", "late",
            "new", "old", "united", "minor", "period", "in"}

    def words(s):
        s = unicodedata.normalize("NFD", s)
        s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn").lower()
        return {w for w in re.split(r"[^a-z]+", s) if len(w) > 2 and w not in stop}
    a, b = words(state or ""), words(article or "")
    return any(x == y or (len(x) >= 5 and len(y) >= 5 and (x.startswith(y) or y.startswith(x))) for x in a for y in b)


def people_weighted(pf, mi, shown_rows, bad_head, bad_names, reg, dec, hyde):
    """For each sample year: the share of the world's people (HYDE grid) whose villagers would say a line
    this audit found wrong. Also which wrong lines reach the most people."""
    facts = {p["q"]: p for p in pf}
    shown_at = collections.defaultdict(dict)        # q -> year -> head row index
    for (q, i), yrs in shown_rows.items():
        for y in yrs:
            shown_at[q][y] = i
    cells = np.nonzero(hyde.cell >= 0)[0]
    lat = -90 + 0.25 + (cells // 720) * 0.5
    lon = -180 + 0.25 + (cells % 720) * 0.5
    out = {}
    reach = collections.defaultdict(float)          # wrong line -> sum over sample years of % of people
    for y in YEARS:
        ppl = hyde.people(lat, lon, y)
        total = float(ppl.sum())
        tally = collections.Counter()
        for i in np.nonzero(ppl > 0)[0]:
            w = float(ppl[i])
            q, n = where(reg, dec, float(lat[i]), float(lon[i]), y)
            if not n:
                continue
            tally["state named"] += w
            ruler_bad = culture_bad = False
            if n in bad_names:
                if not any(x[0] <= y <= x[1] for x in bad_names[n]):
                    tally["state name out of its time"] += w
                    reach[f"state name: “{n}” in {yr(y)}"] += 100 * w / total
                    ruler_bad = True
            p = facts.get(q) if q else None
            if p:
                hi = shown_at.get(q, {}).get(y)
                if hi is not None:
                    name, title, s_, e_ = p["head"][hi][:4]
                    rule = bad_head.get((q, hi))
                    if rule and rule[1] in (WRONG, LIKELY):
                        tally["ruler: " + rule[0]] += w
                        reach[f"ruler: “{n}, ruled by {name} ({title})” — {rule[0]}"] += 100 * w / total
                        ruler_bad = True
                art = p.get("a") or p["n"]
                if articleFits(n, art) or (articleFits(n, p["n"]) and art == p["n"]):
                    for l in p.get("lang", [])[:2]:
                        if LANG_JUNK.search(l):
                            tally["language: not a spoken language"] += w
                            reach[f"language: {p['n']} “{l}”"] += 100 * w / total
                            culture_bad = True
                            break
                        if LANG_FROM.get(l) is not None and y < LANG_FROM[l] - 50:
                            tally["language: before its time"] += w
                            reach[f"language: {p['n']} “{l}” in {yr(y)}"] += 100 * w / total
                            culture_bad = True
                            break
                    if not p.get("relY") or y < 1945:
                        f_ = shown_faith(p.get("rel", []), p.get("relP"), y)
                        if f_ and REL_JUNK.search(f_):
                            tally["faith: not a faith name"] += w
                            reach[f"faith: {p['n']} “{f_}”"] += 100 * w / total
                            culture_bad = True
                        elif f_ and REL_FROM.get(f_) is not None and y < REL_FROM[f_]:
                            tally["faith: before it began"] += w
                            reach[f"faith: {p['n']} “{f_}” in {yr(y)}"] += 100 * w / total
                            culture_bad = True
            if ruler_bad:
                tally["ruler line wrong"] += w
            if culture_bad:
                tally["language or faith line wrong"] += w
            if ruler_bad or culture_bad:
                tally["any wrong line"] += w
        out[str(y)] = {k: round(100 * v / total, 2) for k, v in sorted(tally.items())}
        out[str(y)]["people_millions"] = round(total / 1e6, 1)
        print(y, {k: out[str(y)][k] for k in ("any wrong line", "ruler line wrong", "language or faith line wrong")
                  if k in out[str(y)]}, flush=True)
    top = sorted(reach.items(), key=lambda kv: -kv[1])[:60]
    return out, [[k, round(v, 2)] for k, v in top]


def far_talk(people, reg, dec, hyde, years=(1500, 1800, 1900, 1948, 2000), n=1500, seed=7):
    """'People here talk about X': how often is X someone born more than 1,000 km away? (The game picks
    among the famous people of the same state who are alive and grown up that year; since step 25 among those
    from within 600 km when there are any.)"""
    by_state = collections.defaultdict(list)
    for name, desc, b, d, q, la, lo, rad in people:
        if q:
            a0 = b + 20 if b is not None else d - 40
            a1 = d if d is not None else b + 70
            by_state[q].append((a0, a1, la, lo))
    cells = np.nonzero(hyde.cell >= 0)[0]
    lat = -90 + 0.25 + (cells // 720) * 0.5
    lon = -180 + 0.25 + (cells % 720) * 0.5
    rng = np.random.default_rng(seed)
    out = {}
    for y in years:
        ppl = hyde.people(lat, lon, y)
        pick = rng.choice(len(cells), size=n, p=ppl / ppl.sum())
        far = tot = 0.0
        for i in pick:
            q, _n = where(reg, dec, float(lat[i]), float(lon[i]), y)
            alive = [(la, lo) for a0, a1, la, lo in by_state.get(q, ()) if a0 <= y <= a1] if q else []
            if not alive:
                continue
            # step 25: the game talks about people from within 600 km first (EventNews.near), others only if none
            near = [(la, lo) for la, lo in alive if hav(float(lat[i]), float(lon[i]), la, lo) <= 600]
            alive = near or alive
            far += sum(1 for la, lo in alive if hav(float(lat[i]), float(lon[i]), la, lo) > 1000) / len(alive)
            tot += 1
        out[str(y)] = round(100 * far / tot, 1) if tot else None
    return out


# ====================================================================== main

def main():
    import build_regional as BR
    import build_polity_facts as PF
    import coverage_people as CP
    pf = jload(f"{HIST}/polity_facts.json.gz")["polities"]
    mi = MapIndex()
    wd = Witness()
    print("Wikidata witness:", "yes" if wd.ok else "NO (run fact_audit_wd.py first)",
          len(wd.persons), "names,", len(wd.states), "state names,", len(wd.qids), "ids,", len(wd.capitals),
          "capitals", flush=True)
    polity_names = {plain(n) for n in mi.name_iv} | {plain(p["n"]) for p in pf} | {plain(p.get("a", "")) for p in pf}
    polity_names.discard("")
    shown_rows, bad_head = check_rulers(pf, mi, wd, polity_names)
    print("rulers done", flush=True)
    bad_names = check_state_names(mi, wd)
    reg, dec, hyde = PF.Register(), CP.Deccan(), BR.Hyde()
    check_capitals(wd, reg, dec)
    print("state names done", flush=True)
    check_culture(pf, mi)
    land = {}
    for ci in np.nonzero(hyde.cell >= 0)[0]:
        land[(int(ci) // 720, int(ci) % 720)] = True
    n_events = check_events(land)
    print("events done", n_events, flush=True)
    people = check_people()
    check_routes()
    n_places = check_places()
    check_foundation(wd)
    print("people, routes, places, foundation done", flush=True)
    weighted, reach = people_weighted(pf, mi, shown_rows, bad_head, bad_names, reg, dec, hyde)
    far = far_talk(people, reg, dec, hyde)
    print("famous person talked about was born over 1,000 km away (% of picks):", far, flush=True)

    FINDINGS.sort(key=lambda f: (f["area"], f["rule"], f["item"]))
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["area", "rule", "sure", "seen", "item", "detail", "source"])
        w.writeheader()
        w.writerows(FINDINGS)
    rules = collections.OrderedDict()
    for f in FINDINGS:
        k = f"{f['area']} | {f['rule']}"
        r = rules.setdefault(k, {"sure": f["sure"], "count": 0, "seen_in_game": 0, "examples": []})
        r["count"] += 1
        r["seen_in_game"] += 1 if f["seen"] in ("yes", "/ee here") else 0
        if len(r["examples"]) < 12:
            r["examples"].append(f"{f['item']} — {f['detail']}".strip(" —"))
    checked = {"head and government rows": sum(len(p.get("head", [])) + len(p.get("gov", [])) for p in pf),
               "states with facts": len(pf), "border-map state names": len(mi.name_iv), "events": n_events,
               "famous people": len(people), "places": n_places,
               "trade routes": len(jload(f"{HIST}/trade_routes.json.gz")["routes"])}
    summary = {"checked": checked, "wikidata": wd.source, "findings": len(FINDINGS),
               "by_sureness": dict(collections.Counter(f["sure"] for f in FINDINGS)),
               "rules": rules, "people_weighted_pct": weighted, "wrong_lines_reaching_most_people": reach,
               "far_away_famous_person_pct": far}
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    print("\nchecked:", checked)
    print("findings:", len(FINDINGS), summary["by_sureness"])
    for k, r in rules.items():
        print(f"  {r['count']:6d} ({r['seen_in_game']:6d} seen)  [{r['sure']}]  {k}")


def fetch_extra():
    """Second round of Wikidata look-ups, for what the first round found: which namesakes are states,
    and what the people matched to head-of-state rows did for a living."""
    import fact_audit_wd as W
    cache = W.load_cache()
    wd = Witness()
    qids = {c[0] for cl in wd.states.values() for c in cl}
    W.fetch_statelike(cache, qids)
    W.save(cache)
    pf = jload(f"{HIST}/polity_facts.json.gz")["polities"]
    need = set()
    for p in pf:
        for r in p.get("head", []):
            need.update(wd.compatible_qids(r[0], r[2], r[3]))
    W.fetch_roles(cache, need)
    W.save(cache)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fetch-extra":
        fetch_extra()
    else:
        main()
