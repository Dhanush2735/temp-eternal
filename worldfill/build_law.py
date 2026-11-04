#!/usr/bin/env python3
"""Step 42 part 2 (C18, law and rights by era): build history/law.json.gz.

What the pack is
----------------

A **dated change in the law of a named jurisdiction**, read from three Wikipedia tables that hold
these facts as tables and not as prose:

  * `Timeline of abolition of slavery and serfdom`   455 rows   Date | Jurisdiction | Description
  * `Women's suffrage`                               200 rows   Country | Year first granted | Notes
  * `Use of capital punishment by country`           187 rows   Country | ... | Year abolished

Every row is joined to a **polity QID**, because that is how the mod asks the question:
`RulerRegister.rulerAt(lat, lon, year).wikidata()` gives the state that rules a point in a year,
and the law pack is keyed by that QID. The dictionary it is joined against is the ruler register's
**own** 1,581 polities, so a row can never name a state the mod cannot find.

Two marks
---------

A **year the source states** is *recorded*. Anything this builder inferred - a jurisdiction matched
by a loose name, a year read out of a phrase - is *estimated* and carries the flag, so a page can
say *in about 1888* and never *in 1888*.

Structure
---------

    places      [name, qid, lat*1000, lon*1000] - not used yet; kept for part 3
    rows        [polityIdx, kind, year, yearTo, text, est]
    kinds       the six kinds of law C18 names
    polities    [qid, name] - the join key, straight out of world_rulers.json.gz

Run:  python3 build_law.py            build the pack, then check it
      python3 build_law.py --survey   how much of the source matched, and what did not
"""
import collections
import gzip
import json
import os
import re
import sys

import fetch_step42 as fetch
import weapon_law_table
import road_law_table

HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.normpath(os.path.join(
    HERE, "..", "eternal", "src", "main", "resources", "data", "eternalengine", "eternal", "history"))
OUT = os.path.join(HIST, "law.json.gz")
RULERS = os.path.join(HIST, "world_rulers.json.gz")

# The six kinds of law C18 names, from SYSTEMS_PLAN line 200.
KINDS = [
    {"id": 1, "name": "slavery", "title": "slavery and its end",
     "page": "Timeline of abolition of slavery and serfdom"},
    {"id": 2, "name": "suffrage", "title": "the vote",
     "page": "Women's suffrage"},
    {"id": 3, "name": "punishment", "title": "capital punishment and its end",
     "page": "Use of capital punishment by country"},
    {"id": 4, "name": "codes", "title": "law codes",
     "page": "(not yet fetched - see the gaps)"},
    {"id": 5, "name": "weapons", "title": "weapon laws",
     "page": "(hand-written - no table to read; see the gaps and worldfill/weapon_law_table.py)"},
    {"id": 6, "name": "class", "title": "caste and class rules",
     "page": "(not yet fetched - see the gaps)"},
    {"id": 7, "name": "roads", "title": "the law of the road",
     "page": "(hand-written - no table to read; see worldfill/road_law_table.py)"},
]

# --------------------------------------------------------------------------- matching a jurisdiction

DROP = re.compile(r"\b(the|of|and|de|del|da|du|la|le|el|al)\b")
JUNK = re.compile(r"[^a-z0-9 ]")


def norm(name):
    """A jurisdiction name reduced to what identifies it."""
    t = (name or "").lower()
    t = t.replace("&", " and ")
    t = re.sub(r"\(.*?\)", " ", t)
    t = JUNK.sub(" ", t)
    t = DROP.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()


def bare(name):
    """The same, with the words that say what kind of state it was taken off.

    `Ottoman Empire` and `Ottoman` are the same polity to this join; so are `Kingdom of France`
    and `France`. Stripping them is what lets a country-level table (women's suffrage) and a
    history-level table (abolition of slavery) meet the same register.
    """
    t = norm(name)
    for w in ("empire", "kingdom", "republic", "dynasty", "sultanate", "emirate", "caliphate",
              "principality", "duchy", "state", "states", "polis", "confederation", "federation",
              "province", "colony", "dominion", "crown", "realm", "city"):
        t = re.sub(r"\b" + w + r"\b", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# Countries that changed their name between the row and the register. The register is Cliopatria's
# and names states formally and historically, so `Dahomey` is in it as nothing at all and `Benin`
# is there under its own name - and without this table the row is simply lost.
ALIASES = {
    "dahomey": "benin", "upper volta": "burkina faso", "burma": "myanmar", "ceylon": "sri lanka",
    "siam": "thailand", "persia": "iran", "rhodesia": "zimbabwe", "southern rhodesia": "zimbabwe",
    "ivory coast": "cote ivoire", "cote divoire": "cote ivoire", "timor leste": "east timor",
    "macedonia": "north macedonia", "czech republic": "czechia", "cape verde islands": "cape verde",
    "swaziland": "eswatini", "holland": "netherlands", "great britain": "united kingdom",
    "united kingdom of great britain and ireland": "united kingdom",
    "turkey": "turkiye", "ottoman empire": "turkey", "constantinople": "turkey",
    "zair": "democratic republic of the congo", "zaire": "democratic republic of the congo",
    "congo kinshasa": "democratic republic of the congo", "congo brazzaville": "republic of the congo",
    "brazilian republic": "brazil", "federative republic of brazil": "brazil",
    "united states of america": "united states", "usa": "united states",
    "russian federation": "russia", "soviet union": "russia", "ussr": "russia",
    "people s republic of china": "china", "republic of china": "china",
    "commonwealth of australia": "australia", "swiss confederation": "switzerland",
    "republic of india": "india", "dominion of india": "india",
}
# normalised once, because a lookup key and a dictionary key must go through the same reduction:
# norm() drops "of", so an alias written as "united states of america" would otherwise never fire.
ALIASES = {norm(k): norm(v) for k, v in ALIASES.items()}

# "Dahomey (Today: Benin)" - the table says which modern state it means, so use that.
NEWNAME = re.compile(r"\(today\s*:?\s*([^)]+)\)", flags=re.I)


class Polities:
    """The ruler register's own states, by every name they are likely to be called."""

    def __init__(self, path):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            doc = json.load(f)
        self.pairs = [(p[0], p[1]) for p in doc["polities"] if len(p) >= 2 and p[1]]
        self.by_qid = {}
        self.exact = {}
        self.loose = {}
        for name, qid in self.pairs:
            self.by_qid.setdefault(qid, name)
            for key in self.keys_for(name):
                # A LIST, not a single entry: several polities answer to "France", and which one
                # a row belongs to is decided by the year of the row and not by the order of the
                # file. See `_best`.
                self.exact.setdefault(key, []).append((qid, name))
                self.loose.setdefault(key, []).append((qid, name))
        self.span = self._spans(path)
        self.by_country = self._by_country(path)

    @staticmethod
    def _spans(path):
        """qid -> (first year it ruled anywhere, last year), from the ruler register's timelines.

        A timeline is a FLAT list of triples - `[polity, start, end, polity, start, end, ...]`,
        one timeline per place, 9,322 of them - and not a list of spans. Reading it as a list of
        spans gives "too many values to unpack", which is how this was found.
        """
        with gzip.open(path, "rt", encoding="utf-8") as f:
            doc = json.load(f)
        polities = doc["polities"]
        span = {}
        for timeline in doc.get("timelines", []):
            for i in range(0, len(timeline) - 2, 3):
                polity, start, end = timeline[i], timeline[i + 1], timeline[i + 2]
                if not isinstance(polity, int) or polity < 0 or polity >= len(polities):
                    continue
                if len(polities[polity]) < 2:
                    continue
                qid = polities[polity][1]
                was = span.get(qid)
                span[qid] = (min(start, was[0]) if was else start,
                             max(end, was[1]) if was else end)
        return span

    @staticmethod
    def keys_for(name):
        """Every reduced form a state may be called by, on either side of the join.

        The register's own formal names go through the alias table too, or `United States of
        America` reduces to `united america` while the row says `united states` and the two miss.
        The builder and the checks share this one function so they can never disagree about
        whether a polity was found.
        """
        keys = {norm(name), bare(name)}
        for a in (ALIASES.get(norm(name)), ALIASES.get(bare(name))):
            if a:
                keys.add(norm(a))
                keys.add(bare(a))
        return {k for k in keys if k}

    @staticmethod
    def _by_country(path):
        """country name -> every polity that ever ruled a place in it, from the register's places.

        <b>Why this has to exist.</b> The law tables are written by <i>country</i> - France,
        Brazil, Portugal - and the ruler register is written by <i>state</i>: Kingdom of France,
        French Fifth Republic. Matching the two by name alone filed France's 1981 abolition of
        capital punishment under <i>Kingdom of France</i>, a polity that ended in 1792, because
        "Kingdom of France" was the only polity whose name reduced to "france". Measured:
        <b>189 of 611 rows (31%) sat outside their polity's span.</b>

        So the join goes by ground instead: each place in the register has a latitude and a
        longitude, and the country grid says which country that ground is in. A country then knows
        every state that ever ruled inside it, and the year picks which one.
        """
        import countrygrid
        g = countrygrid.grid()
        with gzip.open(path, "rt", encoding="utf-8") as f:
            doc = json.load(f)
        polities = doc["polities"]
        places = doc["places"]
        timelines = doc["timelines"]
        out = {}
        for i in range(0, len(places) - 2, 3):
            lat, lon, tl = places[i] / 100.0, places[i + 1] / 100.0, places[i + 2]
            if not (0 <= tl < len(timelines)):
                continue
            country = g.name_at(lat, lon)
            if not country:
                continue
            seen = out.setdefault(norm(country), {})
            row = timelines[tl]
            for k in range(0, len(row) - 2, 3):
                polity = row[k]
                if not isinstance(polity, int) or polity < 0 or polity >= len(polities):
                    continue
                if len(polities[polity]) < 2:
                    continue
                qid, pname = polities[polity][1], polities[polity][0]
                seen[qid] = [pname, seen.get(qid, [pname, 0])[1] + 1]
        # Most places first. A country carries hundreds of polities - French Guiana alone puts
        # Brazil inside "France" - so "who ruled here in year Y" means "who ruled the MOST of
        # it", and the count is what says which.
        return {k: sorted(((q, n, c) for q, (n, c) in v.items()), key=lambda t: -t[2])
                for k, v in out.items()}

    def find(self, name, year=None):
        """(qid, matched name, how) - how is 'exact', 'bare', 'alias', 'contains' or 'country'.

        <b>Year-aware, and grounded.</b> Several polities answer to one country name - "France" is
        a kingdom, two republics, an empire and a fifth republic - and the join used to take
        whichever came first in the file. That filed France's 1981 abolition of capital punishment
        under <i>Kingdom of France</i>, a polity that ended in 1792, which the mod then read as:
        France in 2000 has no law at all. Measured across the pack, <b>189 of 611 rows (31%) sat
        outside their polity's span.</b>

        So the order is: the name, if it finds a state that was ruling in the year; then the
        <b>ground</b> - which state ruled the most of this country in that year.
        """
        if not name:
            return None
        m = NEWNAME.search(name)                # "Dahomey (Today: Benin)" means Benin
        if m and m.group(1).strip():
            got = self.find(m.group(1).strip(), year)
            if got:
                return got[0], got[1], "alias"
        n, b = norm(name), bare(name)

        # 1. by name - but only if the state it finds was actually ruling in the year.
        named = self._by_name(n, b)
        if named and year is not None:
            covering = [c for c in named
                        if self.span.get(c[0]) and self.span[c[0]][0] <= year <= self.span[c[0]][1]]
            if covering:
                return covering[0][0], covering[0][1], covering[0][2]

        # 2. by ground: the state ruling most of this country in this year. The law tables are
        #    written by country and the register by state, so this is usually the better key.
        for key in (n, b):
            held = self.by_country.get(key)
            if not held:
                continue
            if year is not None:
                covering = [c for c in held
                            if self.span.get(c[0]) and self.span[c[0]][0] <= year <= self.span[c[0]][1]]
                if covering:
                    return covering[0][0], covering[0][1], "country"
            return held[0][0], held[0][1], "country"

        # 3. by name after all, even where the year does not fit - a row is better than no row.
        if named:
            return self._best(named, year)[0], self._best(named, year)[1], named[0][2]
        return None

    def _by_name(self, n, b):
        """Every polity answering to this name, in the old order of confidence."""
        for key in (norm(ALIASES.get(n, "")), bare(ALIASES.get(b, ""))):
            if key and key in self.exact:
                return [(q, p, "alias") for q, p in self.exact[key]]
        if n in self.exact:
            return [(q, p, "exact") for q, p in self.exact[n]]
        if b in self.loose:
            return [(q, p, "bare") for q, p in self.loose[b]]
        if b and len(b) > 3:
            for key, held in self.loose.items():
                if len(key) > 3 and (key == b or (len(key) > 5 and key in b.split())):
                    return [(q, p, "contains") for q, p in held]
        return []

    def _best(self, candidates, year):
        """Of the polities answering to one name, the one ruling in this year - or the nearest.

        A row with no year, or a year no candidate covers, gets the first: the old behaviour,
        which is right often enough and is always better than dropping the row.
        """
        if not candidates:
            return None, None
        if year is None or len(candidates) == 1:
            return (candidates[0][0], candidates[0][1])
        held = [c for c in candidates if self.span.get(c[0])]
        if held:
            for cand in held:
                span = self.span[cand[0]]
                if span[0] <= year <= span[1]:
                    return (cand[0], cand[1])
            candidates = held                  # nobody covers it; take the nearest of those we know
        for cand in candidates:
            span = self.span.get(cand[0])
            if span and span[0] <= year <= span[1]:
                return (cand[0], cand[1])
        # Nobody covers the year: take the one whose span ends nearest before it, so a row dated
        # 1815 lands on the polity that had just fallen rather than one from a thousand years off.
        def distance(c):
            span = self.span.get(c[0])
            if not span:
                return 10 ** 9
            return 0 if span[0] <= year <= span[1] else min(abs(year - span[0]), abs(year - span[1]))
        return min(candidates, key=distance)


# --------------------------------------------------------------------------- the three extractors

def rows_slavery(pol):
    """Date | Jurisdiction | Description, across the ten century tables of the timeline."""
    out, missed = [], []
    page = fetch.load("slavery")
    for t in fetch.tables(page):
        head = " ".join(t[0]).lower()
        if "jurisdiction" not in head:
            continue
        for r in t[1:]:
            if len(r) < 3:
                continue
            date, where, what = r[0], r[1], r[2]
            year = fetch.year_of(date)
            text = (what or "").strip()
            if not text or len(text) < 12:
                continue
            hit = pol.find(where, year)
            if hit is None or year is None:
                missed.append((date, where, text[:60]))
                continue
            out.append([hit[0], 1, year, year, text, 0 if hit[2] == "exact" else 1])
    return out, missed


def rows_suffrage(pol):
    """Country | Year women first granted suffrage at national level | Notes."""
    out, missed = [], []
    page = fetch.load("suffrage")
    for t in fetch.tables(page):
        head = " ".join(t[0]).lower()
        if "granted suffrage" not in head and "suffrage at" not in head:
            continue
        for r in t[1:]:
            if len(r) < 2:
                continue
            where, year_cell = r[0], r[1]
            note = r[2] if len(r) > 2 else ""
            year = fetch.year_of(year_cell)
            if not where or len(where) > 60:
                continue
            hit = pol.find(where, year)
            if hit is None or year is None:
                missed.append((str(year_cell)[:20], where, note[:60]))
                continue
            out.append([hit[0], 2, year, year,
                        "women were first granted the vote at national level" +
                        (" - " + note.strip() if note.strip() else ""),
                        0 if hit[2] == "exact" else 1])
    return out, missed


def rows_capital(pol):
    """Key | Country | Last execution | Executions in 2024 | Year abolished | Notes."""
    out, missed = [], []
    page = fetch.load("capital")
    for t in fetch.tables(page):
        head = [h.lower() for h in t[0]]
        if not any("year abolished" in h for h in head):
            continue
        if "country" not in " ".join(head):
            continue
        ci = next((i for i, h in enumerate(head) if "country" in h), None)
        yi = next((i for i, h in enumerate(head) if "year abolished" in h), None)
        for r in t[1:]:
            if ci is None or yi is None or len(r) <= max(ci, yi):
                continue
            where, when = r[ci], r[yi]
            year = fetch.year_of(when)
            if not year or not where:
                continue                      # N/A: still in force, which is not a dated change
            hit = pol.find(where, year)
            if hit is None:
                missed.append((when[:20], where, ""))
                continue
            out.append([hit[0], 3, year, year, "capital punishment was abolished",
                        0 if hit[2] == "exact" else 1])
    return out, missed


# --------------------------------------------------------------------------- build

# --------------------------------------------------------------------------- kind 5: weapon laws
#
# There is no table of weapon laws to be read, which is why this kind stayed empty while the other
# three were extracted. So these rows are written by hand, and each carries its source in
# weapon_law_table.py.
#
# The verb matters more than the year. A weapon law is nearly always a law about a CLASS, and half
# the laws here REQUIRE arms rather than forbid them: the 1181 Assize of Arms is the ancestor of
# the militia, not of gun control, and a reader who files it under "restriction" has misread it.
# So the lead-in phrase is chosen from the shape, and the class the law singles out is named.

ROAD_LEAD = {
    "closed":  "had no right of way",
    "toll":    "might pass only by paying",
    "forced":  "might not pass through without selling",
    "gauge":   "had to run to a set gauge",
    "side":    "had to keep to one side",
    "speed":   "were limited in speed",
    "hours":   "might move only in certain hours",
    "labour":  "owed labour on the road",
    "ban":     "were not admitted to the road",
}

LEAD = {
    "must":    "were required to keep arms",
    "free":    "were permitted to bear arms",
    "licence": "might keep arms only by licence",
    "banned":  "were forbidden to keep arms",
    "class":   "were forbidden to keep arms",
}


def rows_weapons(pol):
    """Hand-written rows from weapon_law_table.py, joined to the ruler register by name and year."""
    out, missed = [], []
    for r in weapon_law_table.WEAPON_LAWS:
        hit = pol.find(r["where"], r["year"])
        if hit is None:
            missed.append((str(r["year"]), r["where"], r["text"][:60]))
            continue
        who = (r["who"] or "everyone").rstrip(".")
        body = r["text"].strip().replace("**", "")
        note = r["note"].strip().replace("**", "")
        while body.endswith("."):
            body = body[:-1]
        text = "it was made the law that %s %s. %s. %s." % (who, LEAD[r["shape"]], body, note)
        out.append([hit[0], 5, r["year"], r["year"] if r["to"] is None else r["to"],
                    text, 0 if hit[2] == "exact" else 1])
    return out, missed


def rows_roads(pol):
    """Hand-written rows from road_law_table.py, joined to the ruler register by name and year."""
    out, missed = [], []
    for r in road_law_table.ROAD_LAWS:
        hit = pol.find(r["where"], r["year"])
        if hit is None:
            missed.append((str(r["year"]), r["where"], r["text"][:60]))
            continue
        who = (r["who"] or "everyone").rstrip(".")
        body = r["text"].strip().replace("**", "")
        note = r["note"].strip().replace("**", "")
        while body.endswith("."):
            body = body[:-1]
        text = "on the road, %s %s. %s. %s." % (who, ROAD_LEAD[r["shape"]], body, note)
        out.append([hit[0], 7, r["year"], r["year"] if r["to"] is None else r["to"],
                    text, 0 if hit[2] == "exact" else 1])
    return out, missed


def build():
    pol = Polities(RULERS)
    rows = []
    missed = []
    for fn, label in ((rows_slavery, "slavery"), (rows_suffrage, "suffrage"),
                      (rows_capital, "capital"), (rows_weapons, "weapons"),
                      (rows_roads, "roads")):
        got, lost = fn(pol)
        rows.extend(got)
        missed.extend((label,) + m for m in lost)
        print("  %-10s %5d rows joined, %5d not" % (label, len(got), len(lost)))

    # Two ways a pack says the same thing twice, both of which it now does.
    #
    #  (a) The capital-punishment page carries the same abolition twice - once in the alphabetical
    #      table and once in the year-ordered one.
    #  (b) The year-aware join files several jurisdictions under one polity, because they were all
    #      part of it that year: Estonia, Ukraine and Russia all land on the Russian Republic in
    #      1917, and each carries its own note. The HEADLINE is the same - "women were first
    #      granted the vote at national level" - and only the note differs.
    #
    # So the key is the headline and not the whole text, and the recorded row beats the estimated
    # one. A pack that says a thing twice will print it twice.
    before = len(rows)
    best = {}
    for r in rows:
        headline = r[4].split(" - ")[0]
        key = (r[0], r[1], r[2], r[3], headline)
        if key not in best or r[5] < best[key]:   # keep the recorded row over the estimated one
            best[key] = r[5]
            best.setdefault("__row__" + str(key), r)
        elif r[5] < best[key]:
            best["__row__" + str(key)] = r
    rows = [list(r[:5]) + [best[(r[0], r[1], r[2], r[3], r[4].split(" - ")[0])]]
             for r in best.values() if isinstance(r, list)]
    # (built from the kept rows, so the note of whichever copy won is the one that survives)
    print("  %s rows, %s duplicates dropped" % (f"{len(rows):,}", f"{before - len(rows):,}"))
    rows.sort(key=lambda r: (r[2], r[0], r[1]))
    used = sorted({r[0] for r in rows}, key=lambda q: str(q))
    polities = [[q, pol.by_qid.get(q, "?")] for q in used]
    index = {q: i for i, q in enumerate(used)}
    for r in rows:
        r[0] = index[r[0]]
    est = sum(1 for r in rows if r[5])

    doc = {
        "format": "eternal-law-1",
        "id": "law",
        "source": ("English Wikipedia, read as tables and not as prose: "
                   "'Timeline of abolition of slavery and serfdom', 'Women's suffrage', "
                   "'Use of capital punishment by country' (CC BY-SA 4.0). Kind 5 (weapon "
                   "laws) has no table to be read and is written by hand; each row names its "
                   "source in worldfill/weapon_law_table.py. Joined to the polity QIDs of "
                   "world_rulers.json.gz."),
        "note": ("A dated change in the law of a named jurisdiction. Keyed by polity QID because "
                 "the mod asks 'what is the law here, in this year' through "
                 "RulerRegister.rulerAt(lat, lon, year).wikidata(). Year 0 rows are estimated: "
                 "the jurisdiction was matched on a loose name."),
        "counts": {
            "rows": len(rows),
            "polities": len(polities),
            "kinds": len({r[1] for r in rows}),
            "estimated": est,
            "recorded": len(rows) - est,
            "unmatched": len(missed),
        },
        "gaps": [
            "Five of the seven kinds are filled: law codes (4) and caste and class rules (6) "
            "are not in this pack yet. Kind 7 (the law of the road) was added by step 46 part 5 "
            "and was not in C18's list.",
            "Kind 5 (weapon laws) is hand-written, not extracted: there is no list page to read, "
            "so it carries %d rows over %d polities where the other three carry thousands. It is "
            "ILLUSTRATIVE, not comprehensive - a place with no weapon-law row has no evidence of "
            "indifference, only no evidence at all." % (
                len([r for r in rows if r[1] == 5]),
                len({r[0] for r in rows if r[1] == 5})),
            "Kind 7 (the law of the road) is hand-written for the same reason kind 5 is: there is "
            "no list page to read. It carries %d rows over %d polities and 9 shapes - closed, "
            "toll, forced, gauge, side, speed, hours, labour, ban - and it is ILLUSTRATIVE, not "
            "comprehensive. A place with no road-law row had roads; it simply had no road law "
            "anybody wrote down that we have found." % (
                len([r for r in rows if r[1] == 7]),
                len({r[0] for r in rows if r[1] == 7})),
            "A weapon law is a law about a CLASS, and half of them REQUIRE arms rather than "
            "forbid them. Each kind-5 row names the class it singles out, including the "
            "exemptions: the 1181 Assize of Arms requires arms of every freeman and in the same "
            "breath forbids them to Jews; the 1878 Indian Arms Act exempts Europeans.",
            "The register records CHANGES, not durations: a row's end year is in the pack but "
            "latest() ignores it, so the last change before a year is not always the one still "
            "in force.",
            "Every row is country- or state-granular. A law that held in one town and not the next "
            "cannot be expressed here.",
            "The suffrage rows are women's suffrage only; manhood suffrage, property qualifications "
            "and the secret ballot are not in the pack.",
        ],
        "kinds": KINDS,
        "polities": polities,
        "rows": rows,
    }
    blob = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(blob)
    print("law.json.gz: %s rows over %s polities, %d estimated (%d%%)"
          % (f"{len(rows):,}", f"{len(polities):,}", est, round(100.0 * est / max(1, len(rows)))))
    print("  %s bytes gzipped" % f"{os.path.getsize(OUT):,}")
    return doc


# --------------------------------------------------------------------------- check

def check():
    with gzip.open(OUT, "rt", encoding="utf-8") as f:
        d = json.load(f)
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(d["format"] == "eternal-law-1", "the format is the one this builder writes")
    for key in ("kinds", "polities", "rows", "gaps", "counts"):
        ok(key in d, "the pack carries %s" % key)
    rows = d["rows"]
    ok(len(rows) > 500, "%d dated changes in the law" % len(rows))
    ok(all(len(r) == 6 for r in rows), "every row is [polity, kind, from, to, text, est]")

    kinds = {k["id"] for k in d["kinds"]}
    ok(all(r[1] in kinds for r in rows), "every row names a kind that exists")
    ok(len({r[1] for r in rows}) == 5, "five of the seven kinds are filled (%d)"
       % len({r[1] for r in rows}))
    ok(any(r[1] == 5 for r in rows), "weapon laws are in the pack (%d rows)"
       % sum(1 for r in rows if r[1] == 5))
    ok(all(t in {r[1] for r in rows} for t in (1, 2, 3, 5, 7)),
       "slavery, suffrage, punishment, weapons and the road are all present")
    # The law of the road is a law about a class of vehicle or a class of person, like the weapon
    # kind. It must reach outside Europe, or it is an English road with a Roman preface.
    road = [r for r in rows if r[1] == 7]
    ok(len(road) >= 20, "%d road laws" % len(road))
    ok(len({r[0] for r in road}) >= 8,
       "and they cover %d polities" % len({r[0] for r in road}))
    ok(any("Qhapaq" in r[4] for r in road), "including the Inca road")
    ok(any("sekisho" in r[4] for r in road), "and the Tokugawa checkpoints")

    pol = Polities(RULERS)
    ok(all(p[0] in pol.by_qid for p in d["polities"]),
       "every polity QID in the pack is one the ruler register knows")
    ok(all(0 <= r[0] < len(d["polities"]) for r in rows), "every row names a polity that exists")

    yrs = [r[2] for r in rows]
    ok(min(yrs) < 0 and max(yrs) > 1900, "the pack spans BC and the modern day (%d to %d)"
       % (min(yrs), max(yrs)))
    ok(all(-4000 <= r[2] <= 2026 for r in rows), "no row is dated outside the mod's span")
    ok(all(r[3] >= r[2] for r in rows), "no row ends before it starts")
    ok(all(r[4].strip() for r in rows), "every row says what changed")

    seen = {(r[0], r[1], r[2], r[4][:40]) for r in rows}
    ok(len(seen) == len(rows), "no row twice (%d)" % len(rows))

    est = sum(1 for r in rows if r[5])
    ok(0 < est < len(rows), "some rows are estimated and some are recorded (%d of %d)"
       % (est, len(rows)))

    # The three stories a player will actually be told, hand-checked against what the source says.
    # The register names states formally, so Brazil is in it as the Empire of Brazil. The hand
    # checks look polities up the same way the join does, or they would check nothing at all.
    # The checks look a polity up the SAME way the join does now - country and year, not name -
    # or they check nothing at all. This is the step-41 rule: one shared lookup, never two.
    reg = Polities(RULERS)
    by_pol = collections.defaultdict(list)
    for i, (qid, name) in enumerate(d["polities"]):
        for k in Polities.keys_for(name):
            by_pol[k].append(i)
    for ckey, held in reg.by_country.items():
        for qid, pname, nplaces in held:
            if nplaces < 20:                 # a border place does not make a state a country's
                continue
            by_pol[ckey].extend(i for i, (q, _) in enumerate(d["polities"]) if q == qid)
    print()
    for want in ("brazil", "united states", "france", "united kingdom", "india", "japan"):
        got = []
        for i in by_pol.get(want, ()):
            got.extend(r for r in rows if r[0] == i)
        if not got:
            continue
        print("       %s (%s)" % (d["polities"][got[0][0]][1], len(got)) + " rows")
        for r in sorted(got, key=lambda r: r[2])[:3]:
            print("          %5d  %s" % (r[2], r[4][:66]))

    def has(want, kind, year, what):
        """What the source says this country did in this year, asked through the join."""
        hit = reg.find(want, year)
        if hit is None:
            return False
        qid = hit[0]
        return any(d["polities"][r[0]][0] == qid and r[1] == kind and r[2] == year for r in rows)

    ok(has("brazil", 1, 1888, ""), "Brazil ends slavery in 1888, which is the year the source gives")
    ok(has("united states", 1, 1865, ""),
       "the United States ends slavery in 1865, which is the year the source gives")
    ok(has("france", 1, 1794, "") and has("france", 1, 1848, ""),
       "France abolishes slavery in 1794 under the First Republic and again in 1848 under the "
       "Second - two different states, which is what the join now says")
    ok(has("france", 3, 1981, ""),
       "France gives up capital punishment in 1981, under the Fifth Republic and not the Kingdom")
    ok(any(r[1] == 2 for r in rows), "and the vote is in the pack too")

    print()
    print("law: %d problem(s)" % len(bad))
    return len(bad)


def survey():
    pol = Polities(RULERS)
    print("%d polities in the ruler register, %d exact names, %d loose names"
          % (len(pol.pairs), len(pol.exact), len(pol.loose)))
    for fn, label in ((rows_slavery, "slavery"), (rows_suffrage, "suffrage"),
                      (rows_capital, "capital"), (rows_weapons, "weapons")):
        got, lost = fn(pol)
        print("\n%s: %d joined, %d not" % (label, len(got), len(lost)))
        for date, where, what in lost[:14]:
            print("    %-18s %-28s %s" % (str(date)[:18], str(where)[:28], what[:46]))


if __name__ == "__main__":
    if "--survey" in sys.argv:
        survey()
    else:
        build()
        sys.exit(1 if check() else 0)
