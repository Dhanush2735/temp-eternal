import io
#!/usr/bin/env python3
"""Step 7.6: reigns from Wikipedia's "List of state leaders in ..." pages -> polity_facts.json.gz.

62 pages (dump 2026-10-01, CC BY-SA 4.0): one per century from the 4th millennium BC to the 21st
century AD, plus the Holy Roman Empire and South Asia sub-pages. Their layout is regular:

    *[[Byzantine Empire]] ([[List of Byzantine emperors|complete list]]) -
    :*[[Manuel II Palaiologos]], Emperor (1391-1425)
    :*[[Stefan Lazarevic]], Prince (1389-1402), Despot (1402-1427)

The state is the first link of a "*" line; each ruler line gives a person and one or more
"Title (start-end)" spans. A state is tied to the mod's states by its Wikidata id (RulerRegister's
ids), else by the state ruling the article's own coordinates that year when every word of the name
fits that state. These spans are exact, so for each state they replace the rougher reigns (from
accession and death lines) that overlap them; a reign of the same person is replaced by the list's.
"""
import collections, gzip, json, os, re, sqlite3, sys

sys.path.insert(0, "/home/user/worldfill")
import modpack as M  # noqa: E402
import wpdump as W  # noqa: E402
import build_polity_facts as PF  # noqa: E402

FACTS = f"{M.HISTORY}/polity_facts.json.gz"
REPORT = "/home/user/worldfill/state_leaders_report.json"
CACHE = os.path.expanduser("~/.cache/wpdump/state_leader_pages.json.gz")
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")
DAY = r"(?:\d{1,2}\s+[A-Z][a-z]+\s+|[A-Z][a-z]+\s+(?:\d{1,2},\s+)?)?"
SPAN = re.compile(r"(?:(?P<title>[A-Za-zÀ-ÿ][^,;()\[\]]{0,60}?)\s*)?\(\s*(?P<since>since\s+)?(?:c\.\s*|ca\.\s*|r\.\s*)?" + DAY +
                  r"(?P<a>\d{1,4})\s*(?P<ea>BCE|BC|CE|AD)?"
                  r"(?:\s*[–-]\s*(?:c\.\s*|ca\.\s*)?" + DAY + r"(?P<b>\d{1,4}|present)\s*(?P<eb>BCE|BC|CE|AD)?)?\s*\)")
PRESENT = 2026


def pages():
    con = sqlite3.connect("file:" + W.DB + "?mode=ro", uri=True)
    rows = con.execute("SELECT t.title, r.target FROM titles t LEFT JOIN redirects r ON r.page_id = t.page_id "
                       "WHERE t.title LIKE 'List of state leaders in%century%' OR t.title LIKE 'List of state leaders in%millennium%' "
                       "OR t.title LIKE 'List of state leaders in the%BC%' "
                       "OR t.title GLOB 'List of state leaders in the [12][0-9][0-9]0s'").fetchall()
    titles = sorted({t for t, tgt in rows if not tgt})
    if os.path.exists(CACHE):
        cached = json.load(gzip.open(CACHE, "rt", encoding="utf-8"))
        if set(cached) >= set(titles):
            return cached
    got = W.Wiki().texts(titles, workers=2)
    texts = {t: text for t, (_f, text) in got.items()}
    with open(CACHE, "wb") as _gzraw, \
            gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, \
            io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as _gztext:
        json.dump(texts, _gztext)
    return texts


def years(m, bc_page):
    a = int(m.group("a"))
    ea = (m.group("ea") or "").upper()
    b_raw = m.group("b")
    eb = (m.group("eb") or "").upper()
    bc_a = ea in ("BC", "BCE") or (not ea and (eb in ("BC", "BCE") or (bc_page and eb not in ("AD", "CE"))))
    start = -a if bc_a else a
    if b_raw is None:
        return (start, PRESENT) if m.group("since") else (start, start)
    if b_raw == "present":
        return start, PRESENT
    b = int(b_raw)
    if len(b_raw) <= 2 and a >= 100 and not eb:          # "1405-33"
        b = a // 100 * 100 + b
    bc_b = eb in ("BC", "BCE") or (not eb and bc_a)
    end = -b if bc_b else b
    if end < start:
        return None
    return start, end


def parse(text, bc_page):
    """-> [(state_title, person, title, start, end)]"""
    out, state = [], None
    lines = text.split("\n")
    i = -1
    while i + 1 < len(lines):
        i += 1
        line = lines[i].strip()
        if line.startswith("{|") and state:
            # a table of rulers under the current state: header cells name the columns
            j, header, rows, cur = i + 1, [], [], []
            while j < len(lines) and not lines[j].strip().startswith("|}"):
                c = lines[j].strip()
                if c.startswith("!"):
                    header += [h.strip().lower() for h in re.split(r"!!|^!", c) if h.strip()]
                elif c.startswith("|-"):
                    if cur:
                        rows.append(cur)
                    cur = []
                elif c.startswith("|"):
                    cur += [x.strip() for x in re.split(r"\|\|", c[1:])]
                j += 1
            if cur:
                rows.append(cur)
            col = {h: k for k, h in enumerate(header)}
            ni, ti, fi, oi = col.get("name"), col.get("title"), col.get("from"), col.get("to")
            if ni is not None and fi is not None:
                for r in rows:
                    if len(r) <= max(x for x in (ni, ti or 0, fi, oi or 0)):
                        continue
                    lm = LINK.search(r[ni])
                    nm = re.sub(r"\s*\([^()]*\)$", "", (lm.group(2) or lm.group(1)) if lm else re.sub(r"\[\[|\]\]", "", r[ni])).strip()
                    tt = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", r[ti]).strip() if ti is not None else "ruler"
                    span = f"x ({r[fi]}–{r[oi]})" if oi is not None and r[oi] else f"x ({r[fi]})"
                    span = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", span)
                    m = SPAN.search(span)
                    y = years(m, bc_page) if m else None
                    if nm and y and len(nm) <= 60:
                        out.append((state, nm, (tt or "ruler")[:40], y[0], y[1]))
            i = j
            continue
        if not line.startswith(("*", ":")):
            if line.startswith("=="):
                state = None
            continue
        depth_marks = re.match(r"^[*:#]+", line).group(0)
        body = line[len(depth_marks):].strip().replace("'''", "")
        # modern pages lead with a flag: "{{flag|India}}" or "[[File:Flag of X.svg|20px]] [[X]]"
        body = re.sub(r"\{\{\s*(?:flag|flagcountry|flagu|flagdeco|flag icon|flagicon|flagg)\s*\|\s*(?:[a-z]{1,4}\|)?([^|}]+)[^}]*\}\}",
                      r"[[\1]]", body, flags=re.I)
        body = re.sub(r"\[\[(?:File|Image):[^\[\]]*(?:\[\[[^\]]*\]\][^\[\]]*)*\]\]\s*", "", body).strip()
        links = [(m.group(1).strip(), (m.group(2) or "").strip(), m.start(), m.end()) for m in LINK.finditer(body)]
        if depth_marks == "*":
            # a new state block: its first link, wherever it sits ("{{USA}} [[United States]]"), unless
            # that link is the "complete list" one: then the plain text before it names the state
            # ("*United States ([[List of presidents...|complete list]])"). A top-level line with no
            # state closes the block, so no ruler is carried over to the wrong state.
            state = None
            if links and not ("complete list" in (links[0][1] or "").lower() or links[0][0].startswith("List of")):
                state = links[0][0]
            else:
                lead = re.sub(r"\{\{[^{}]*\}\}|<[^>]+>|'{2,}", "", body[: links[0][2]] if links else body)
                lead = lead.strip(" (:–-")
                if 2 <= len(lead) <= 60 and re.match(r"^[A-Z]", lead):
                    state = lead
            if not links:
                continue
            rest_links = links[1:]
            # an inline ruler on the state line: "*[[State]] - [[Ruler]], King (1400-1420)"
            body_after = body[links[0][3]:]
            cand = [l for l in rest_links if "complete list" not in (l[1] or "").lower() and not l[0].startswith("List of")]
            if not cand or not SPAN.search(body_after):
                continue
            person_link = cand[0]
            tail = body[person_link[3]:]
        else:
            if not state or not links:
                continue
            person_link = links[0]
            if person_link[2] > 3:
                continue
            tail = body[person_link[3]:]
        target, alias = person_link[0], person_link[1]
        if target.startswith(("File:", "Image:", "List of")):
            continue
        name = re.sub(r"\s*\([^()]*\)$", "", alias or target).strip()
        if not name or len(name) > 60:
            continue
        clean_tail = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", tail)
        clean_tail = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>|\{\{[^{}]*\}\}", "", clean_tail)
        for m in SPAN.finditer(clean_tail):
            title = (m.group("title") or "").strip(" ,–-:") or "ruler"
            if len(title) > 50 or re.search(r"\d", title):
                continue
            y = years(m, bc_page)
            if not y:
                continue
            out.append((state, name, title, y[0], y[1]))
    return out


ORDINALS = set("""first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth thirteenth
fourteenth fifteenth sixteenth seventeenth eighteenth nineteenth twentieth twenty thirty thirtieth dynasty
kingdom house period""".split())


def by_name(state, year, names):
    """'Eighteenth Dynasty of Egypt' -> the state of that year named Egypt; 'Babylon' -> Babylonia."""
    words = {w for w in PF.key_words(state) if w not in ORDINALS}
    if not words:
        return None
    fixed = set()
    for w in words:
        if w in names.by_word:
            fixed.add(w)
            continue
        stems = [k for k in names.by_word if len(w) >= 5 and len(k) >= 5 and (k.startswith(w) or w.startswith(k))]
        if len(stems) != 1:
            return None
        fixed.add(stems[0])
    return names.find(fixed, year)


def main():
    texts = pages()
    reg = PF.Register()
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
    st = collections.Counter()
    spans = []
    for t, text in texts.items():
        rows = parse(text, "BC" in t or "millenni" in t)
        st["spans_parsed"] += len(rows)
        spans += rows
    memo = {}
    by_q = collections.defaultdict(list)
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
                q = by_name(state, (a + b) // 2, names)
                if q:
                    st["states_by_name"] += 1
            memo[key] = q
        q = memo[key]
        if not q:
            st["spans_no_state"] += 1
            continue
        role = "gov" if PF.GOV.search(title) else "head"
        by_q[q].append((role, [person, title[:40], a, min(b, PRESENT)]))
        st["spans_placed"] += 1
    doc = json.load(gzip.open(FACTS, "rt", encoding="utf-8"))
    by = {p["q"]: p for p in doc["polities"]}
    qname = {q: n for n, q in reg.pols if q}
    norm = lambda s: re.sub(r"[^a-z0-9]+", "", PF.strip_accents(s.lower()))
    for q, rows in by_q.items():
        p = by.setdefault(q, {"q": q, "n": qname.get(q, q)})
        if q not in [x["q"] for x in doc["polities"][-1:]] and p not in doc["polities"]:
            doc["polities"].append(p)
            st["new_state_entries"] += 1
        for role in ("head", "gov"):
            lst = [r for rl, r in rows if rl == role]
            if not lst:
                continue
            seen, uniq = set(), []
            for r in sorted(lst, key=lambda r: (r[2], r[3], r[0])):
                k = (norm(r[0]), r[2])
                if k not in seen:
                    seen.add(k)
                    uniq.append(r)
            old = p.get(role, [])
            names_in_list = {norm(r[0]) for r in uniq}
            kept = []
            for r in old:
                same_person = norm(r[0]) in names_in_list
                overlaps = any(r[2] <= u[3] and u[2] <= r[3] for u in uniq)
                if same_person or overlaps:
                    st[f"{role}_replaced"] += 1
                    continue
                kept.append(r)
            p[role] = sorted(kept + uniq, key=lambda r: (r[2], r[3]))
            st[f"{role}_list_reigns"] += len(uniq)
    doc["source"] += "; reigns from Wikipedia's 'List of state leaders in ...' pages, worldfill/build_state_leaders.py"
    with open(FACTS + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    json.load(gzip.open(FACTS + ".tmp", "rt", encoding="utf-8"))
    os.replace(FACTS + ".tmp", FACTS)
    # how often a ruled cell's state has a named ruler that year (same measure as build_polity_facts)
    head = {p["q"]: p.get("head", []) for p in doc["polities"]}
    cover = {}
    for y in [-2500, -1500, -500, 1, 500, 1000, 1300, 1500, 1700, 1850, 1900, 1950, 2000, 2020]:
        n = k = 0
        for i in range(0, len(reg.lat), 7):
            pol = next((reg.pols[pp] for pp, s, e in reg.tls[reg.tl[i]] if s <= y <= e), None)
            if not pol:
                continue
            n += 1
            k += any(r[2] <= y <= r[3] for r in head.get(pol[1], ()))
        cover[str(y)] = f"{100.0 * k / n:.0f}% of {n} ruled cells" if n else "-"
    rep = {**dict(st), "states_with_named_rulers": sum(1 for p in doc["polities"] if p.get("head")),
           "head_reigns_total": sum(len(p.get("head", [])) for p in doc["polities"]),
           "gov_reigns_total": sum(len(p.get("gov", [])) for p in doc["polities"]),
           "named_ruler_share_of_ruled_cells": cover, "bytes": os.path.getsize(FACTS),
           "examples": [f"{s[0]} | {s[1]} | {s[2]} | {s[3]}..{s[4]}" for s in spans[:: max(1, len(spans) // 12)]][:12]}
    json.dump(rep, open(REPORT, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
