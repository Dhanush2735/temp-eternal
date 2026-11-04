import io
#!/usr/bin/env python3
"""Step 8.2: fill the biggest "state known, ruler not named" gaps (history/polity_facts.json.gz).

Wikipedia is the source throughout (enwiki dump 2026-10-01, CC BY-SA 4.0). Run after
fix_state_ids.py. Stages, each safe to run again (rows are deduplicated):

  lists      The century "List of state leaders in ..." pages again (cached by
             build_state_leaders.py), but only for the states whose id fix_state_ids.py repaired.
             States that shared an id in the same years (the two Koreas) are then split by name:
             a ruler the lists give to the repaired state is removed from the old id.
  colonies   A colony's head of state is its home country's monarch or president, from
             Wikipedia's lists ("List of British monarchs", ...). Clipped to the colony's own years
             on the map. Where Wikipedia lists them, governors-general become its head of government.
  targeted   Ruler lists for the biggest remaining gaps ("List of pharaohs", "Gupta Empire", ...).
             Each list is tied to its map state by id, never by guessing.

Usage: python3 fill_rulers.py [lists] [targeted] [colonies]   (default: all three, in this order: a
colony's head of state is its home monarch even where a local king list also reaches it)
Writes worldfill/fill_rulers_report.json.
"""
import collections, gzip, json, os, re, sys

sys.path.insert(0, "/home/user/worldfill")
import modpack as M  # noqa: E402
import wpdump as W  # noqa: E402
import build_polity_facts as PF  # noqa: E402
import build_state_leaders as SL  # noqa: E402

FACTS = f"{M.HISTORY}/polity_facts.json.gz"
FIXREP = "/home/user/worldfill/fix_state_ids_report.json"
REPORT = "/home/user/worldfill/fill_rulers_report.json"
PRESENT = 2026
norm = lambda s: re.sub(r"[^a-z0-9]+", "", PF.strip_accents(s.lower()))


def load():
    return json.load(gzip.open(FACTS, "rt", encoding="utf-8"))


def save(doc, note):
    if note not in doc["source"]:
        doc["source"] += "; " + note
    with open(FACTS + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    json.load(gzip.open(FACTS + ".tmp", "rt", encoding="utf-8"))
    os.replace(FACTS + ".tmp", FACTS)


def entry(doc, by, q, name):
    p = by.get(q)
    if p is None:
        p = {"q": q, "n": name}
        doc["polities"].append(p)
        by[q] = p
    return p


def merge(p, role, rows, st, replace_overlaps=True):
    """List rows win: an older row of the same person, or one overlapping a list row, is dropped."""
    seen, uniq = set(), []
    for r in sorted(rows, key=lambda r: (r[2], r[3], r[0])):
        k = (norm(r[0]), r[2])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    names = {norm(r[0]) for r in uniq}
    kept = []

    def clash(r, u):
        ov = min(r[3], u[3]) - max(r[2], u[2])
        return ov >= 0 and (ov >= 2 or ov >= 0.5 * (r[3] - r[2]))
    for r in p.get(role, []):
        if norm(r[0]) in names or (replace_overlaps and any(clash(r, u) for u in uniq)):
            st[f"{role}_replaced"] += 1
            continue
        kept.append(r)
    p[role] = sorted(kept + uniq, key=lambda r: (r[2], r[3]))
    st[f"{role}_added"] += len(uniq)
    return uniq


# ---------------------------------------------------------------- stage 1: lists for repaired ids
def stage_lists(st):
    fixrep = json.load(open(FIXREP))
    fixes = fixrep["fixes"]
    newq = {fx["new"] for fx in fixes}
    texts = SL.pages()
    reg = PF.Register()
    import sqlite3
    con = sqlite3.connect("file:" + W.DB + "?mode=ro", uri=True)
    title_of = {}
    for _n, q in reg.pols:
        if q and q not in title_of:
            r = con.execute("SELECT t.title FROM props p JOIN titles t ON t.page_id = p.page_id WHERE p.qid = ? LIMIT 1", (q,)).fetchone()
            if r:
                title_of[q] = r[0]
    names = PF.StateNames(reg, title_of)
    known = {q for _n, q in reg.pols if q}
    wiki = W.Wiki()
    spans = []
    for t, text in texts.items():
        spans += SL.parse(text, "BC" in t or "millenni" in t)
    memo, by_q = {}, collections.defaultdict(list)
    for state, person, title, a, b in spans:
        key = (state, a // 50)
        if key not in memo:
            hit = wiki.lookup(state)
            info = wiki.info(hit[1]) if hit else None
            q = info.get("qid") if info else None
            if q not in known:
                q = None
                g = info.get("geo") if info else None
                if g:
                    pol = reg.at(g["lat"], g["lon"], (a + b) // 2)
                    if pol and pol[1] and PF.key_words(state) and PF.key_words(state) <= names.words.get(pol[1], set()):
                        q = pol[1]
            if not q:
                q = SL.by_name(state, (a + b) // 2, names)
            memo[key] = q
        q = memo[key]
        if q in newq:
            role = "gov" if PF.GOV.search(title) else "head"
            by_q[q].append((role, [person, title[:40], a, min(b, PRESENT)]))
    doc = load()
    by = {p["q"]: p for p in doc["polities"]}
    qname = {q: n for n, q in reg.pols if q}
    added = collections.defaultdict(lambda: collections.defaultdict(list))
    for q, rows in by_q.items():
        p = entry(doc, by, q, qname.get(q, q))
        for role in ("head", "gov"):
            lst = [r for rl, r in rows if rl == role]
            if lst:
                added[q][role] = merge(p, role, lst, st)
                st["states_given_list_rows"] += 1
    # split states that shared an id in the same years: rulers the lists give to the repaired state
    # leave the old id (only inside the repaired state's years)
    for fx in fixes:
        if not fx.get("shares_years_with_old_users"):
            continue
        oldp = by.get(fx["old"])
        if not oldp:
            continue
        a, b = fx["span"]
        for role in ("head", "gov"):
            mine = {norm(r[0]) for r in added[fx["new"]][role]}
            if not mine:
                continue
            before = len(oldp.get(role, []))
            oldp[role] = [r for r in oldp.get(role, []) if not (norm(r[0]) in mine and r[3] >= a - 5 and r[2] <= b + 5)]
            st["split_removed_from_old_id"] += before - len(oldp[role])
    save(doc, "rulers for repaired ids from the 'List of state leaders' pages, worldfill/fill_rulers.py")
    st["lists_states"] = len(by_q)



# ---------------------------------------------------------------- shared helpers for stages 2 and 3
import ruler_lists as RL  # noqa: E402

JUNK_NAME = re.compile(r"(?i)\b(crisis|war|act|government|union|kingdom|empire|dynasty|house of|republic|treaty|battle|"
                       r"siege|mutiny|revolution|rebellion|revolt|policy|non-intervention|interregnum|vacant|unknown|"
                       r"anarchy|council|directory|committee|junta|occupation|commonwealth|protectorate|colony|province|"
                       r"period|era|list|reign|ruler|rulers|regnal|portrait|coat of arms|incumbent|vacancy|none|various|"
                       r"see below|lineage|disputed|claimant|pretender|usurper|anonymous|name|names|title)\b|=|rowspan|style|background|\d|\?$")
PTS = dict(MEMPHIS=(29.849, 31.254), THEBES=(25.719, 32.657), AVARIS=(30.787, 31.821), HERAKLEOPOLIS=(29.085, 30.934),
           TANIS=(30.977, 31.880), SAIS=(30.966, 30.768), BABYLON=(32.536, 44.421), ASSUR=(35.456, 43.262),
           HATTUSA=(40.020, 34.615), SUSA=(32.190, 48.257), KISH=(32.541, 44.604), WASHUKANNI=(36.85, 40.07),
           ROME=(41.893, 12.483), CONSTANTINOPLE=(41.008, 28.978), LONDON=(51.507, -0.128), PARIS=(48.857, 2.352),
           MADRID=(40.417, -3.704), LISBON=(38.722, -9.139), COPENHAGEN=(55.676, 12.568), PAVIA=(45.185, 9.155),
           KYOTO=(35.012, 135.768), NARA=(34.685, 135.805), SEOUL=(37.566, 126.978), GYEONGJU=(35.856, 129.225),
           PYONGYANG=(39.039, 125.762), BUYEO=(36.275, 126.910), KAESONG=(37.970, 126.554), HANOI=(21.028, 105.854),
           HUE=(16.464, 107.590), AYUTTHAYA=(14.353, 100.569), BANGKOK=(13.756, 100.502), SUKHOTHAI=(17.017, 99.703),
           BAGAN=(21.172, 94.860), AVA=(21.856, 95.977), LUANG_PRABANG=(19.886, 102.135), ISFAHAN=(32.655, 51.668),
           DAMASCUS=(33.513, 36.292), BAGHDAD=(33.315, 44.366), CAIRO=(30.044, 31.236), ANURADHAPURA=(8.311, 80.403),
           KANDY=(7.291, 80.636), KOTTE=(6.890, 79.918), POLONNARUWA=(7.940, 81.000), SRINAGAR=(34.084, 74.797),
           ESZTERGOM=(47.790, 18.740), KRAKOW=(50.062, 19.937), MOSCOW=(55.756, 37.617), KYIV=(50.450, 30.523),
           PRAGUE=(50.075, 14.438), TRONDHEIM=(63.430, 10.395), EDINBURGH=(55.953, -3.188), NAPLES=(40.852, 14.268),
           VIENNA=(48.208, 16.373), FRANKFURT=(50.110, 8.682), BERLIN=(52.520, 13.405), VILNIUS=(54.687, 25.280),
           RAS=(43.130, 20.410), TARNOVO=(43.081, 25.629), TBILISI=(41.716, 44.783), YEREVAN=(40.177, 44.513),
           PALERMO=(38.116, 13.361), ZARAGOZA=(41.649, -0.889), BURGOS=(42.344, -3.697), PAMPLONA=(42.812, -1.646),
           LEON=(42.599, -5.567), TENOCHTITLAN=(19.433, -99.133), CUZCO=(-13.532, -71.968), AKSUM=(14.130, 38.719),
           NIANI=(11.383, -8.383), GAO=(16.272, -0.044), MEROE=(16.938, 33.749), CTESIPHON=(33.094, 44.581),
           ANTIOCH=(36.202, 36.160), PELLA=(40.756, 22.524), SPARTA=(37.074, 22.430), DELHI=(28.614, 77.209))


def at_fit(reg, la, lo, year, fit):
    """The state of `year` at the nearest register cell (within 80 km) whose state fits; the plain
    nearest-cell rule can land on an empty sea or border cell (Rome sits between two cells)."""
    cands = []
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            for i in reg.grid.get(reg.key(la + dy * reg.CELL, lo + dx * reg.CELL), ()):
                d = reg.dist(la, lo, reg.lat[i], reg.lon[i])
                if d <= 80:
                    cands.append((d, i))
    for d, i in sorted(cands):
        for pp, s, e in reg.tls[reg.tl[i]]:
            if s <= year <= e:
                pol = reg.pols[pp]
                if pol[1] and re.search(fit, pol[0]):
                    return pol
                break
    return None


def reg_tools():
    reg = PF.Register()
    span, qof = {}, {}
    for i in range(len(reg.lat)):
        for pp, s, e in reg.tls[reg.tl[i]]:
            a, b = span.get(pp, (9999, -9999))
            span[pp] = (min(a, s), max(b, e))
    qspan = {}
    for k, (n, q) in enumerate(reg.pols):
        qof.setdefault(n, q)
        if k in span and q:
            a, b = qspan.get(q, (9999, -9999))
            qspan[q] = (min(a, span[k][0]), max(b, span[k][1]))
    return reg, qof, qspan


def tidy(rows, fill_ends=False):
    """Drop junk names and impossible spans; optionally close single-year rows at the next accession."""
    out = []
    for nm, a, b, h in rows:
        nm = re.sub(r"[^\u0000-\u024F\u1E00-\u1EFF\u2019]+", " ", nm)
        nm = re.sub(r"\s+", " ", nm).strip(" ,;:-–/")
        if not nm or len(nm) > 60 or JUNK_NAME.search(nm) or not re.match(r"^[^\W\d_]", nm):
            continue
        if b < a or b - a > 75 or a < -3600 or b > PRESENT:
            continue
        out.append([nm, a, b, h])
    best = {}
    for r in out:                       # one row per (person, accession): the longest
        k = (norm(r[0]), r[1])
        if k not in best or r[2] > best[k][2]:
            best[k] = r
    out = list(best.values())
    if fill_ends:
        out.sort(key=lambda r: (r[3], r[1]))
        for i, r in enumerate(out):
            if r[1] == r[2] and i + 1 < len(out) and out[i + 1][3] == r[3] and 0 < out[i + 1][1] - r[1] <= 60:
                r[2] = out[i + 1][1]
            elif r[1] == r[2] and r[1] >= 1990 and (i + 1 == len(out) or out[i + 1][3] != r[3]):
                r[2] = PRESENT          # the last ruler of a modern list reigns to this day
    seen, uniq = set(), []
    for r in sorted(out, key=lambda r: (r[1], r[2])):
        k = (norm(r[0]), r[1])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    return uniq


def quality(rows):
    """'replace' (a clean list), 'gaps' (usable only where nobody is named) or 'reject'."""
    if len(rows) < 2:
        return "gaps" if rows else "reject"
    lens = sorted(r[2] - r[1] for r in rows)
    med = lens[len(lens) // 2]
    rs = sorted(rows, key=lambda r: r[1])
    over = sum(1 for x, y in zip(rs, rs[1:]) if y[1] < x[2] - 3) / (len(rs) - 1)
    if med > 45:
        return "reject"           # life dates, not reigns
    if med <= 35 and over <= 0.35:
        return "replace"
    return "gaps"


def add_rows(doc, by, q, name, rows, title, st, mode, role="head"):
    if not rows:
        return
    p = entry(doc, by, q, name)
    new = [[r[0], title, r[1], r[2]] for r in rows]
    if mode == "replace":
        merge(p, role, new, st)
    else:
        have = p.get(role, [])
        free = [r for r in new if not any(h[2] <= r[3] and r[2] <= h[3] for h in have)]
        p[role] = sorted(have + free, key=lambda r: (r[2], r[3]))
        st[f"{role}_gap_rows"] += len(free)


# ---------------------------------------------------------------- stage 3: targeted ruler lists
# page, how rows find their state, title. fixed: map polity names; point: the map state at a place in
# the reign's middle year, kept only if its name matches fit; caption: the dynasty named by the table.
T = [
    dict(page="List of pharaohs", section=r"Dynasty|period", bc=True, title="Pharaoh", point="MEMPHIS",
         points=[(r"Ninth|Tenth", "HERAKLEOPOLIS"), (r"Eleventh Dynasty \(Thebes\)|Sixteenth|Seventeenth|Abydos|High Priests", "THEBES"),
                 (r"Fourteenth|Fifteenth", "AVARIS"), (r"Twenty-first|Twenty-second|Twenty-third", "TANIS"),
                 (r"Twenty-fourth|Twenty-sixth|Proto-Saite", "SAIS")],
         fit=r"Egypt|Dynasty|Hyksos|Ptolemaic"),
    dict(page="First Dynasty of Egypt", bc=True, title="Pharaoh", point="MEMPHIS", fit=r"Egypt|Dynasty"),
    dict(page="Second Dynasty of Egypt", bc=True, title="Pharaoh", point="MEMPHIS", fit=r"Egypt|Dynasty"),
    dict(page="Third Dynasty of Egypt", bc=True, title="Pharaoh", point="MEMPHIS", fit=r"Egypt|Dynasty"),
    dict(page="Fourth Dynasty of Egypt", bc=True, title="Pharaoh", point="MEMPHIS", fit=r"Egypt|Dynasty"),
    dict(page="Fifth Dynasty of Egypt", bc=True, title="Pharaoh", point="MEMPHIS", fit=r"Egypt|Dynasty"),
    dict(page="Sixth Dynasty of Egypt", bc=True, title="Pharaoh", point="MEMPHIS", fit=r"Egypt|Dynasty"),
    dict(page="Ninth Dynasty of Egypt", bc=True, title="Pharaoh", point="HERAKLEOPOLIS", fit=r"Egypt|Dynasty"),
    dict(page="Tenth Dynasty of Egypt", bc=True, title="Pharaoh", point="HERAKLEOPOLIS", fit=r"Egypt|Dynasty"),
    dict(page="Eleventh Dynasty of Egypt", bc=True, title="Pharaoh", point="THEBES", fit=r"Egypt|Dynasty"),
    dict(page="Twelfth Dynasty of Egypt", bc=True, title="Pharaoh", point="MEMPHIS", fit=r"Egypt|Dynasty"),
    dict(page="Thirteenth Dynasty of Egypt", bc=True, title="Pharaoh", point="MEMPHIS", fit=r"Egypt|Dynasty"),
    dict(page="Fifteenth Dynasty of Egypt", bc=True, title="Pharaoh", fixed=["Hyksos", "Fifteenth Dynasty of Egypt"]),
    dict(page="Seventeenth Dynasty of Egypt", bc=True, title="Pharaoh", point="THEBES", fit=r"Egypt|Dynasty"),
    dict(page="Eighteenth Dynasty of Egypt", bc=True, title="Pharaoh", point="THEBES", fit=r"Egypt|Dynasty"),
    dict(page="Nineteenth Dynasty of Egypt", bc=True, title="Pharaoh", point="MEMPHIS", fit=r"Egypt|Dynasty"),
    dict(page="Twentieth Dynasty of Egypt", bc=True, title="Pharaoh", point="THEBES", fit=r"Egypt|Dynasty"),
    dict(page="Twenty-first Dynasty of Egypt", bc=True, title="Pharaoh", point="TANIS", fit=r"Egypt|Dynasty"),
    dict(page="List of kings of Babylon", bc=True, title="King of Babylon", point="BABYLON", fit=r"Babylon|Kassite|Sealand|Isin|Chaldea"),
    dict(page="List of Assyrian kings", bc=True, title="King of Assyria", point="ASSUR", fit=r"Assyria"),
    dict(page="List of Hittite kings", bc=True, title="Hittite king", fixed=["Hittites"]),
    dict(page="List of rulers of Elam", bc=True, title="King of Elam", point="SUSA", fit=r"Elam"),
    dict(page="Akkadian Empire", section=r"ruler|king|list", bc=True, title="King of Akkad", fixed=["Akkadian Empire"]),
    dict(page="Mitanni", section=r"ruler|king|list", bc=True, title="King of Mitanni", fixed=["Mitanni"]),
    dict(page="King of Rome", section=r"king|list|ruler", bc=True, title="King of Rome", fixed=["Roman Kingdom"]),
    dict(page="List of Roman emperors", title="Roman emperor", point="ROME", fit=r"Roman Empire|Western Roman"),
    dict(page="List of Byzantine emperors", title="Byzantine emperor", point="CONSTANTINOPLE", fit=r"Byzantine|Eastern Roman|Roman Empire"),
    dict(page="Ptolemaic dynasty", section=r"ruler|list|pharaoh|monarch", bc=True, title="Pharaoh", fixed=["Ptolemaic Kingdom"]),
    dict(page="Seleucid dynasty", section=r"Seleucid rulers", bc=True, title="Seleucid king", fixed=["Seleucid Empire"]),
    dict(page="List of monarchs of Parthia", section=r"List of kings|Chronology", title="King of Kings", fixed=["Parthian Empire"]),
    dict(page="Achaemenid Empire", section=r"monarch|ruler|king|list", bc=True, title="King of Kings", fixed=["Achaemenid Empire"]),
    dict(page="List of English monarchs", title="English monarch", point="LONDON", fit=r"England|Anglo-Saxon|Norman|Wessex", max_year=1707),
    dict(page="List of British monarchs", title="British monarch", point="LONDON", fit=r"Britain|United Kingdom"),
    dict(page="List of French monarchs", title="French monarch", point="PARIS", fit=r"France|French|Francia|Franks", max_year=1870),
    dict(page="List of Spanish monarchs", title="Spanish head of state", point="MADRID", fit=r"Spain|Spanish|Castile"),
    dict(page="List of Portuguese monarchs", title="Portuguese monarch", point="LISBON", fit=r"Portug", max_year=1910),
    dict(page="List of Chinese monarchs", title="Emperor", caption=True, prefer_target=True, max_year=1912),
    dict(page="Qi (state)", bc=True, title="Ruler of Qi", fixed=["Qi"]),
    dict(page="Jin (Chinese state)", bc=True, title="Ruler of Jin", fixed=["Jin"]),
    dict(page="Lu (state)", bc=True, title="Duke of Lu", fixed=["Lu"]),
    dict(page="Song (state)", bc=True, title="Duke of Song", fixed=["Song"]),
    dict(page="Wei (state)", bc=True, title="Ruler of Wei", fixed=["Wei"]),
    dict(page="Zhao (state)", bc=True, title="Ruler of Zhao", fixed=["Zhao"]),
    dict(page="Han (Warring States)", bc=True, title="Ruler of Han", fixed=["Han"]),
    dict(page="Qin (state)", bc=True, title="Ruler of Qin", fixed=["Qin"]),
    dict(page="Zheng (state)", bc=True, title="Ruler of Zheng", fixed=["Zheng"]),
    dict(page="Zhongshan (state)", bc=True, title="Ruler of Zhongshan", fixed=["Zhongshan"]),
    dict(page="Chu (state)", section=r"ruler|monarch|king|list", bc=True, title="Ruler of Chu", fixed=["Chu"]),
    dict(page="List of Polish monarchs", title="King of Poland and Grand Duke of Lithuania", fixed=["House of Jagiellon"], max_year=1572),
    dict(page="List of Satavahana kings", title="King", fixed=["Satavahana Dynasty"]),
    dict(page="List of Gupta emperors", title="Emperor", fixed=["Gupta Empire"]),
    dict(page="List of Pala emperors", title="Emperor", fixed=["Pala Empire"]),
    dict(page="Shunga Empire", section=r"Shunga emperors", title="Emperor", fixed=["Shunga Empire"]),
    dict(page="Pallava dynasty", section=r"Sastri chronology", title="King", fixed=["Late Pallava Empire"]),
    dict(page="Kushan Empire", section=r"ruler|emperor|monarch|list", title="Emperor", fixed=["Kushan Empire"]),
    dict(page="Mamluk dynasty (Delhi)", section=r"^Sultans|/ Sultans", title="Sultan", fixed=["Mamluk Dynasty"]),
    dict(page="Jaunpur Sultanate", section=r"ruler|sultan|list", title="Sultan", fixed=["Jaunpur Sultanate"]),
    dict(page="Kadamba dynasty", section=r"ruler|king|list", title="King", fixed=["Kadamba Empire"]),
    dict(page="Maitraka dynasty", section=r"ruler|king|list", title="King", fixed=["Maitraka Dynasty"]),
    dict(page="Alchon Huns", section=r"ruler|king|list", title="King", fixed=["White Huns"]),
    dict(page="Vakataka dynasty", section=r"ruler|king|list", title="King", fixed=["Vakataka Kingdom"]),
    dict(page="Gahadavala dynasty", section=r"ruler|king|list", title="King", fixed=["Gahadavala Dynasty"]),
    dict(page="Eastern Ganga dynasty", section=r"ruler|king|list", title="King", fixed=["Eastern Ganga Kingdom"]),
    dict(page="Chahamanas of Shakambhari", section=r"ruler|king|list", title="King", fixed=["Chauhan Dynasty"]),
    dict(page="Kakatiya dynasty", section=r"Sovereign rulers", title="King", fixed=["Kakatiya Dynasty"]),
    dict(page="Nawabs of Awadh", title="Nawab", fixed=["Nawab of Awadh"]),
    dict(page="Western Chalukya Empire", section=r"ruler|king|list", title="King", fixed=["Western Chalukya Empire"]),
    dict(page="Western Satraps", section=r"List of rulers", title="Satrap", fixed=["Western Satraps"]),
    dict(page="Habbari Emirate", section=r"ruler|emir|list", title="Emir", fixed=["Sind-Habbari Dynasty"]),
    dict(page="Paramara dynasty", section=r"ruler|king|list", title="King", fixed=["Paramara Dynasty"]),
    dict(page="Seuna (Yadava) dynasty", section=r"ruler|king|list", title="King", fixed=["Yadava Dynasty"]),
    dict(page="Varman dynasty (Kannauj)", title="King", fixed=["Kannauj-Varman Dynasty"]),
    dict(page="Karkota dynasty", section=r"ruler|king|list", title="King of Kashmir", point="SRINAGAR", fit=r"Kashmir|Karkota|Utpala|Lohara"),
    dict(page="Utpala dynasty", section=r"ruler|king|list", title="King of Kashmir", point="SRINAGAR", fit=r"Kashmir|Karkota|Utpala|Lohara"),
    dict(page="Lohara dynasty", section=r"Lohara dynasty|Vuppadevas", title="King of Kashmir", point="SRINAGAR", fit=r"Kashmir|Karkota|Utpala|Lohara"),
    dict(page="Bahmani Sultanate", section=r"ruler|sultan|list", title="Sultan", fixed=["Bahmani Sultanate"]),
    dict(page="Maurya Empire", section=r"List of rulers", title="Emperor", fixed=["Maurya Empire"]),
    dict(page="Nanda Empire", section=r"Nanda kings", title="King", fixed=["Nanda Empire"]),
    dict(page="Kanva dynasty", section=r"ruler|king|list", title="King", fixed=["Kanva Dynasty"]),
    dict(page="Chola dynasty", section=r"ruler|king|list|monarch", title="King", fixed=["Chola Empire"]),
    dict(page="Rashtrakuta dynasty", section=r"ruler|king|list|emperor", title="Emperor", fixed=["Rashtrakuta Dynasty"]),
    dict(page="List of Chalukya emperors", title="King", fixed=["Chalukya Dynasty"]),
    dict(page="List of Vijayanagara emperors", title="Emperor", fixed=["Vijayanagara Empire"]),
    dict(page="Qutb Shahi dynasty", section=r"List of rulers", title="Sultan", name_h=r"titular", fixed=["Golconda Sultanate"]),
    dict(page="List of emperors of the Mughal Empire", section=r"List of Mughal emperors", title="Mughal emperor", fixed=["Mughal Empire"], max_year=1857),
    dict(page="Nizams of Hyderabad", title="Nizam", fixed=["Hyderabad State"], max_year=1948),
    dict(page="Sena dynasty", section=r"ruler|king|list", title="King", fixed=["Sena Dynasty"]),
    dict(page="Kamarupa", section=r"dynasty \(", title="King", fixed=["Kamarupa Kingdom"]),
    dict(page="Pratihara dynasty", section=r"ruler|king|list", title="King", fixed=["Gurjara-Pratihara Dynasty"]),
    dict(page="Chandela dynasty", section=r"ruler|king|list", title="King", fixed=["Chandela Kingdom"]),
    dict(page="Hoysala Empire", section=r"List of Monarchs", title="King", fixed=["Hoysala Kingdom"]),
    dict(page="List of rulers of Saba and Himyar", section=r"Himyar", title="King of Himyar", fixed=["Himyarite Kingdom"]),
    dict(page="Funan", section=r"ruler|king|list", title="King", fixed=["Funan"]),
    dict(page="Sunda Kingdom", section=r"ruler|king|list|monarch", title="King", fixed=["Sunda Kingdom"]),
    dict(page="Ziyadid dynasty", section=r"ruler|emir|list", title="Emir", fixed=["Ziyadid dynasty"]),
    dict(page="List of kings of the Lombards", title="King of the Lombards", point="PAVIA", fit=r"Lombard|Italy"),
    dict(page="King of Italy", title="King of Italy", point="PAVIA", fit=r"Italy"),
    dict(page="List of rulers of Tenochtitlan", title="Tlatoani", fixed=["Aztec Triple Alliance"]),
    dict(page="Sapa Inca", section=r"ruler|list|inca", title="Sapa Inca", fixed=["Inca Empire"]),
    dict(page="Kingdom of Kush", section=r"ruler|king|list|monarch", bc=True, title="King of Kush", fixed=["Kingdom of Kush"]),
    dict(page="List of kings of Axum", title="King of Aksum", fixed=["Kingdom of Axum"]),
    dict(page="Mali Empire", section=r"ruler|mansa|list", title="Mansa", fixed=["Mali Empire"]),
    dict(page="Songhai Empire", section=r"ruler|askia|list", title="Askia", fixed=["Songhai Empire"]),
    dict(page="List of sultans of Delhi", title="Sultan of Delhi", point="DELHI", fit=r"Delhi|Mamluk|Khalji|Tughlaq|Sayyid|Lodi|Sultanate", max_year=1526),
    dict(page="List of Maurya emperors", title="Emperor", fixed=["Maurya Empire"]),
    dict(page="List of Ottoman sultans", title="Ottoman sultan", fixed=["Ottoman Empire"], max_year=1922),
    dict(page="List of Mamluk sultans of Egypt", title="Mamluk sultan", fixed=["Mamluk Sultanate"]),
    dict(page="List of monarchs of Iran", title="Shah", min_year=224, point="ISFAHAN",
         fit=r"Safavid|Afsharid|Zand|Qajar|Pahlavi|Iran|Persia|Sasanian|Achaemenid|Parthian|Seleucid|Buyid|Samanid|Seljuk|Ilkhan|Timurid|Aq Qoyunlu|Qara Qoyunlu|Khwarazm", max_year=1978),
    dict(page="List of monarchs of Korea", title="King", point="SEOUL",
         points=[(r"Goguryeo", "PYONGYANG"), (r"Baekje", "BUYEO"), (r"Silla|Gaya", "GYEONGJU"), (r"Goryeo", "KAESONG")],
         fit=r"Goguryeo|Baekje|Silla|Goryeo|Joseon|Korea|Balhae|Gaya", max_year=1910),
    dict(page="List of emperors of Japan", title="Emperor of Japan", name_h=r"posthumous", point="KYOTO", fit=r"Japan|Shogunate|Restoration|Kenmu"),
    dict(page="List of Vietnamese monarchs", title="Emperor", point="HANOI", fit=r"Viet|Ly|Tran|Le |Lê|Nguyen|Nguyễn|Mạc|Đại|Ngô|Đinh|Tây Sơn", max_year=1945),
    dict(page="List of monarchs of Thailand", title="King", point="AYUTTHAYA",
         points=[(r"Sukhothai", "SUKHOTHAI"), (r"Thonburi|Rattanakosin|Chakri", "BANGKOK")], fit=r"Ayutthaya|Sukhothai|Thonburi|Rattanakosin|Siam|Thailand"),
    dict(page="List of Burmese monarchs", title="King", point="AVA", points=[(r"Pagan", "BAGAN")], fit=r"Pagan|Toungoo|Konbaung|Burma|Ava|Hanthawaddy|Myinsaing|Pinya|Sagaing", max_year=1885),
    dict(page="List of monarchs of Laos", title="King", point="LUANG_PRABANG", fit=r"Lan Xang|Laos|Luang|Vientiane", max_year=1975),
    dict(page="List of Sri Lankan monarchs", title="King", point="ANURADHAPURA",
         points=[(r"Polonnaruwa", "POLONNARUWA"), (r"Kotte|Dambadeniya|Gampola|Yapahuwa|Kurunegala", "KOTTE"), (r"Kandy|Kandyan", "KANDY")],
         fit=r"^(?!Portuguese|Dutch|British).*(Anuradhapura|Polonnaruwa|Ceylon|Sri Lanka|Kandy|Kotte|Dambadeniya|Jaffna|Rajarata)", max_year=1815),
    dict(page="List of caliphs", title="Caliph", point="BAGHDAD", points=[(r"Rashidun", "DAMASCUS"), (r"Umayyad", "DAMASCUS"), (r"Fatimid", "CAIRO")],
         fit=r"Caliphate|Rashidun|Umayyad|Abbasid|Fatimid", max_year=1517),
    dict(page="List of monarchs of Hungary", title="King of Hungary", point="ESZTERGOM", fit=r"Hungar", max_year=1918),
    dict(page="List of Polish monarchs", title="Polish monarch", point="KRAKOW", fit=r"Poland|Polish|Piast|Jagiell|Commonwealth", max_year=1815),
    dict(page="List of Russian monarchs", section=r"Tsars|Emperors|Grand|Prince", title="Russian monarch", point="MOSCOW", fit=r"Russia|Muscovy|Moscow|Vladimir", max_year=1917),
    dict(page="List of rulers of Bohemia", title="Bohemian monarch", point="PRAGUE", fit=r"Bohemia"),
    dict(page="List of monarchs of Denmark", title="Danish monarch", point="COPENHAGEN", fit=r"Denmark|Danish|Kalmar"),
    dict(page="List of Norwegian monarchs", title="Norwegian monarch", point="TRONDHEIM", fit=r"Norway"),
    dict(page="List of Scottish monarchs", title="Scottish monarch", point="EDINBURGH", fit=r"Scotland|Alba", max_year=1707),
    dict(page="List of monarchs of Naples", title="King of Naples", point="NAPLES", fit=r"Naples|Sicil", max_year=1861),
    dict(page="List of rulers of Austria", title="Ruler of Austria", point="VIENNA", fit=r"Austria|Habsburg", max_year=1918),
    dict(page="List of Holy Roman Emperors", title="Holy Roman Emperor", point="FRANKFURT", fit=r"Holy Roman|Germany|East Francia", max_year=1806),
    dict(page="List of monarchs of Prussia", section=r"Prussia|Brandenburg", title="King of Prussia", point="BERLIN", fit=r"Prussia|Brandenburg", max_year=1918),
    dict(page="List of rulers of Lithuania", title="Grand Duke of Lithuania", point="VILNIUS", fit=r"Lithuania"),
    dict(page="List of Serbian monarchs", title="Serbian monarch", point="RAS", fit=r"Serbia|Rascia", max_year=1918),
    dict(page="List of Bulgarian monarchs", title="Bulgarian monarch", point="TARNOVO", fit=r"Bulgaria", max_year=1946),
    dict(page="List of Georgian monarchs", title="Georgian monarch", point="TBILISI", fit=r"Georgia|Iberia|Kartli|Imereti|Kakheti", max_year=1801),
    dict(page="List of Armenian monarchs", title="Armenian monarch", point="YEREVAN", fit=r"Armenia", max_year=1375),
    dict(page="List of monarchs of Sicily", title="King of Sicily", point="PALERMO", fit=r"Sicily", max_year=1816),
    dict(page="List of Aragonese monarchs", title="King of Aragon", point="ZARAGOZA", fit=r"Aragon", max_year=1516),
    dict(page="List of Castilian monarchs", title="Castilian monarch", point="BURGOS", fit=r"Castile", max_year=1555),
    dict(page="List of Navarrese monarchs", title="King of Navarre", point="PAMPLONA", fit=r"Navarre|Pamplona", max_year=1620),
    dict(page="List of monarchs of Leon", title="King of León", point="LEON", fit=r"León|Leon|Asturias", max_year=1230),
]


def consuls(text):
    """List of Roman consuls: a 'Year | consul | consul' table per century -> one row a year."""
    out = []
    text = RL.protect_inner_headings(RL.strip_noise(text))
    for head, body in RL.sections(text):
        bc = bool(re.search(r"\bBC\b", head))
        for header, rows, cap in RL.tables(body):
            for r in rows:
                if len(r) < 3:
                    continue
                y = re.match(r"^\s*(\d{1,3})\s*$", RL.clean(r[0]))
                if not y:
                    continue
                yr = -int(y.group(1)) if bc else int(y.group(1))
                names = [RL.person(c) for c in r[1:3]]
                names = [n for n in names if n and not JUNK_NAME.search(n)]
                if names:
                    out.append([" and ".join(names), yr, yr, head])
    return out


def all_pages():
    pages = RL.pages()
    for k, v in list(pages.items()):
        if v.get("final") and v["final"] not in pages:
            pages[v["final"]] = v
    return pages


def stage_targeted(st):
    pages = all_pages()
    reg, qof, qspan = reg_tools()
    doc = load()
    by = {p["q"]: p for p in doc["polities"]}
    qname = {q: n for n, q in reg.pols if q}
    wiki = W.Wiki()
    log = []
    # Roman Republic: consuls, two a year
    rows = consuls(pages["List of Roman consuls"]["text"])
    q = qof.get("Roman Republic")
    keep = [r for r in rows if r[1] <= -27]
    add_rows(doc, by, q, "Roman Republic", keep, "Consuls", st, "replace")
    log.append(["List of Roman consuls", "replace", len(keep), {"Roman Republic": len(keep)}])
    for t in T:
        page = pages.get(t["page"])
        if not page or not page["text"]:
            log.append([t["page"], "missing", 0, {}])
            continue
        text = page["text"]
        sec = t.get("section")
        if sec:
            # a ruler section that only says {{main|List of ...}}: read that list instead
            mains = [m for m in RL.main_links(text, sec) if m in pages]
            if mains and not RL.extract(text, sec, t.get("bc", False)):
                text, sec = pages[mains[0]]["text"], None
        raw = RL.extract(text, sec, t.get("bc", False), prefer_target=t.get("prefer_target", False), name_h=t.get("name_h"))
        rows = [r for r in tidy(raw, fill_ends=True) if t.get("min_year", -9999) <= r[1] <= t.get("max_year", PRESENT)]
        rows = [[r[0], r[1], min(r[2], t.get("max_year", PRESENT)), r[3]] for r in rows]
        mode = quality(rows)
        placed = collections.Counter()
        if mode != "reject":
            groups = collections.defaultdict(list)
            for nm, a, b, h in rows:
                if "fixed" in t:
                    for pn in t["fixed"]:
                        q = qof.get(pn)
                        sp = qspan.get(q)
                        if q and sp and a <= sp[1] + 30 and b >= sp[0] - 30:
                            groups[q].append([nm, a, b, h])
                elif t.get("caption"):
                    label = h.split(" | ")[-1] if " | " in h else h.split(" / ")[-1]
                    label = re.split(r"\s*[\(（]", label)[0].strip()
                    label = re.sub(r"(?i)\s+and\s+.*$", "", label)
                    q = None
                    for cand in (label, label + " dynasty", label + " (Ten Kingdoms)", label + " (Sixteen Kingdoms)", label + " (state)"):
                        hit = wiki.lookup(cand)
                        info = wiki.info(hit[1]) if hit else None
                        if info and info.get("qid") in qspan:
                            q = info["qid"]
                            break
                    if q:
                        sp = qspan[q]
                        if a <= sp[1] + 30 and b >= sp[0] - 30:
                            groups[q].append([nm, a, b, h])
                else:
                    ptname = next((p for rx, p in t.get("points", []) if re.search(rx, h)), t["point"])
                    la, lo = PTS[ptname]
                    qs = set()
                    for y in sorted({a, (a + b) // 2, b}):
                        pol = at_fit(reg, la, lo, y, t["fit"])
                        if pol:
                            qs.add(pol[1])
                    for q in qs:
                        groups[q].append([nm, a, b, h])
            for q, rs in groups.items():
                title = t["title"]
                if t.get("caption") and re.search(r"Shang|Zhou dynasty|Western Zhou|Eastern Zhou", rs[0][3]):
                    title = "King"
                add_rows(doc, by, q, qname.get(q, q), rs, title, st, mode)
                placed[qname.get(q, q)] += len(rs)
        log.append([t["page"], mode, len(rows), dict(placed.most_common(8))])
        st[f"pages_{mode}"] += 1
    save(doc, "rulers from Wikipedia's ruler lists, worldfill/fill_rulers.py")
    json.dump(log, open("/home/user/worldfill/fill_rulers_targets.json", "w"), ensure_ascii=False, indent=1)
    for row in log:
        print(f"  {row[0][:40]:40} {row[1]:8} {row[2]:4} {json.dumps(row[3], ensure_ascii=False)[:150]}")


# ---------------------------------------------------------------- stage 2: colonies
HOME = {
    "british": dict(lists=[("List of English monarchs", None, 1707), ("List of British monarchs", 1707, None)], facts=[], title="British monarch"),
    "spanish": dict(lists=[("List of Spanish monarchs", None, None)], facts=["Kingdom of Spain", "Francoist Spain", "Second Spanish Republic", "First Spanish Republic"], title="Spanish head of state"),
    "portuguese": dict(lists=[("List of Portuguese monarchs", None, 1910)], facts=["Kingdom of Portugal", "Portuguese Republic", "Portugal"], title="Portuguese head of state"),
    "french": dict(lists=[("List of French monarchs", None, 1870)], facts=["Kingdom of France", "French First Republic", "French Directory", "French Consulate",
                   "First French Empire", "Bourbon Kingdom of France", "French Second Republic", "Second French Empire", "French Third Republic",
                   "Vichy France", "Free French", "French Fourth Republic", "French Fifth Republic"], title="French head of state"),
    "dutch": dict(lists=[], facts=["Dutch Republic", "Netherlands", "Sovereign Principality of the United Netherlands"], title="Dutch head of state"),
    "danish": dict(lists=[("List of monarchs of Denmark", None, None)], facts=[], title="Danish monarch"),
    "german": dict(lists=[], facts=["German Empire"], title="German emperor"),
    "italian": dict(lists=[("King of Italy", 1861, 1946)], facts=[], title="King of Italy"),
    "belgian": dict(lists=[("List of Belgian monarchs", None, None)], facts=[], title="Belgian monarch"),
}
COLONIES = {
    "british": ["British Colonial Empire", "English Colonial Empire", "British Cape Colony", "British Ceylon", "British Raj",
                "British Gold Coast", "British East Africa", "British Overseas Territories", "Freetown Colony"],
    "spanish": ["Spanish Empire"],
    "portuguese": ["Portuguese Empire", "Portuguese Ceylon"],
    "french": ["French India", "French Algeria", "French Africa", "French Indochina", "French Louisiana", "French Colony of Guiana", "New France", "France Antarctique"],
    "dutch": ["Dutch East Indies", "Dutch Cape Colony", "Dutch Gold Coast", "Dutch Ceylon"],
    "danish": ["Danish Gold Coast", "Danish India"],
    "german": ["German Africa"],
    "italian": ["Italian Africa"],
    "belgian": ["Belgian Congo"],
}
DOMINIONS = [("Islamic Republic of Pakistan", 1947, 1956, "Monarch of Pakistan"), ("Republic of India", 1947, 1950, "Monarch of India"),
             ("Sri Lanka", 1948, 1972, "Monarch of Ceylon")]
GOVERNORS = [("List of governors-general of India", ["British Raj"], "Viceroy and Governor-General of India", 1858, 1947),
             ("List of governors-general of the Dutch East Indies", ["Dutch East Indies"], "Governor-General", 1800, 1949),
             ("List of governors-general of French Indochina", ["French Indochina"], "Governor-General", 1887, 1954)]
GOVLIKE = re.compile(r"(?i)governor|director|viceroy|commissioner|resident|administrator|captain-general|intendant")


def stage_colonies(st):
    pages = all_pages()
    reg, qof, qspan = reg_tools()
    doc = load()
    by = {p["q"]: p for p in doc["polities"]}
    lines = {}
    for home, cfg in HOME.items():
        rows = []
        for page, lo, hi in cfg["lists"]:
            if page in pages and pages[page]["text"]:
                got = tidy(RL.extract(pages[page]["text"]), fill_ends=True)
                rows += [r for r in got if (lo is None or r[2] >= lo) and (hi is None or r[1] <= hi)]
        for pn in cfg["facts"]:
            q = qof.get(pn)
            for r in by.get(q, {}).get("head", []) if q else []:
                if not JUNK_NAME.search(r[0]) and 0 <= r[3] - r[2] <= 75:
                    rows.append([r[0], r[2], r[3], pn])
        seen, line = set(), []
        for r in sorted(rows, key=lambda r: (r[1], r[2])):
            k = (norm(r[0]), r[1])
            if k not in seen and not any(norm(r[0]) == norm(x[0]) and abs(r[1] - x[1]) <= 1 for x in line):
                seen.add(k)
                line.append(r)
        lines[home] = line
        st[f"home_{home}"] = len(line)
    for home, names in COLONIES.items():
        for pn in names:
            q = qof.get(pn)
            sp = qspan.get(q)
            if not q or not sp:
                continue
            p = entry(doc, by, q, pn)
            # local governors listed as heads become heads of government
            heads = p.get("head", [])
            gov_like = [r for r in heads if GOVLIKE.search(r[1] or "")]
            if gov_like:
                p["head"] = [r for r in heads if r not in gov_like]
                p["gov"] = sorted(p.get("gov", []) + gov_like, key=lambda r: (r[2], r[3]))
                st["colony_heads_moved_to_gov"] += len(gov_like)
            rows = [[r[0], HOME[home]["title"], max(r[1], sp[0]), min(r[2], sp[1])] for r in lines[home] if r[2] >= sp[0] and r[1] <= sp[1]]
            if rows:
                merge(p, "head", rows, st)
                st["colonies_filled"] += 1
    for pn, lo, hi, title in DOMINIONS:
        q = qof.get(pn)
        if q:
            rows = [[r[0], title, max(r[1], lo), min(r[2], hi)] for r in lines["british"] if r[2] >= lo and r[1] <= hi]
            if rows:
                merge(entry(doc, by, q, pn), "head", rows, st, replace_overlaps=False)
                st["dominions_filled"] += 1
    for page, names, title, lo, hi in GOVERNORS:
        if page not in pages:
            continue
        rows = [r for r in tidy(RL.extract(pages[page]["text"]), fill_ends=True) if r[2] >= lo and r[1] <= hi]
        if quality(rows) == "reject" or len(rows) < 5:
            st["governor_lists_rejected"] += 1
            continue
        for pn in names:
            q = qof.get(pn)
            if q:
                merge(entry(doc, by, q, pn), "gov", [[r[0], title, r[1], r[2]] for r in rows], st)
                st["governor_lists_used"] += 1
    save(doc, "colonies: home-country heads of state from Wikipedia's monarch lists, worldfill/fill_rulers.py")
    json.dump({h: [r[:3] for r in l] for h, l in lines.items()}, open("/home/user/worldfill/fill_rulers_home_lines.json", "w"), ensure_ascii=False, indent=0)


if __name__ == "__main__":
    stages = sys.argv[1:] or ["lists", "targeted", "colonies"]
    st = collections.Counter()
    rep = json.load(open(REPORT)) if os.path.exists(REPORT) else {}
    for s in stages:
        globals()[f"stage_{s}"](st)
        rep[s] = dict(st)
        print(s, json.dumps(dict(st), ensure_ascii=False))
        st = collections.Counter()
    json.dump(rep, open(REPORT, "w"), ensure_ascii=False, indent=1)
