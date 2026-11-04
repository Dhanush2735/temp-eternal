#!/usr/bin/env python3
"""Read ruler lists from Wikipedia wikitext: tables and bullet lists -> (name, first year, last year, section).

Used by fill_rulers.py. Handles the usual layouts of Wikipedia's ruler lists:
  * wikitables with a name column and a reign column ("Reign", "Period", "Dates", "Ruled"), or
    separate start/end columns ("Accession" / "Ended", "From" / "To"). Cells may span several
    lines; rowspan/colspan are expanded;
  * bullet lines: "* [[Rudrama Devi|Rudrama-devi]] (r. c. 1262-1289), ...";
  * dates: "c. 185–149 BCE", "1 May 1707 – 1 August 1714", "{{circa|2686}}–2613 BC", "r. 1199–1262".
Bare years count as BC when the list says so in the row, in its section heading or (option bc) as a
whole.
"""
import gzip, json, os, re

CACHE = os.path.expanduser("~/.cache/wpdump/ruler_list_pages.json.gz")
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
SKIP_SECTIONS = re.compile(r"(?i)^(see also|references|notes|bibliography|external links|further reading|sources|citations|footnotes|literature|works cited|explanatory notes|gallery)")


def pages():
    return json.load(gzip.open(CACHE, "rt", encoding="utf-8"))


NOISE = re.compile(r"(?i)^\{\{\s*(efn|efn-lr|efn-ua|sfn|sfnm|sfnp|refn|r|rp|collapsible list|age in|age|cite|citation|notetag|"
                   r"note|harvnb|harv|clarify|dubious|cn|citation needed|by whom|which|when|marriage|hiero|image|multiple image|"
                   r"clear|reflist|notelist|main|see also|further|portal|commons|wikisource|lang-|nihongo2|tooltip|abbr|"
                   r"increase|decrease|steady|in lang|small caps|anchor|vanchor|div col|refbegin|refend|bar box|chart|tree chart|"
                   r"familytree|chart top|chart bottom|chart/|flagicon|flag|redirect|short description|hatnote|good article|featured)\b")


def strip_noise(text):
    """Drop refs, comments and footnote/collapsible templates (nested braces handled)."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<ref[^>]*/>", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    out, i, n = [], 0, len(text)
    while i < n:
        j = text.find("{{", i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        if NOISE.match(text[j:j + 40]):
            depth, k = 0, j
            while k < n:
                if text.startswith("{{", k):
                    depth += 1
                    k += 2
                elif text.startswith("}}", k):
                    depth -= 1
                    k += 2
                    if depth == 0:
                        break
                else:
                    k += 1
            i = k
        else:
            out.append("{{")
            i = j + 2
    return _flatten_templates("".join(out))


def _flatten_templates(text):
    """Newlines inside {{...}} become spaces, except in Succession table templates (read separately)."""
    out, i, n = [], 0, len(text)
    while i < n:
        j = text.find("{{", i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        depth, k = 0, j
        while k < n:
            if text.startswith("{{", k):
                depth += 1
                k += 2
            elif text.startswith("}}", k):
                depth -= 1
                k += 2
                if depth == 0:
                    break
            else:
                k += 1
        chunk = text[j:k]
        if "\n{|" in chunk:
            # a table wrapped in a template ({{Row numbers| {| ... |} }}): unwrap, keep its lines
            chunk = re.sub(r"^\{\{[^|{}\n]*\|", "", chunk)
            chunk = chunk[:-2] if chunk.endswith("}}") else chunk
            chunk = chunk.replace("{{=}}", "=").replace("{{!}}", "|")
        elif not re.match(r"(?i)\{\{\s*succession table", chunk):
            chunk = chunk.replace("\n", " ")
        out.append(chunk)
        i = k
    return "".join(out)


def succession_tables(body, bc=False):
    """{{Succession table monarch |name1= |reignstart1= |reignend1= ...}} -> [(name, start, end)]."""
    out = []
    for m in re.finditer(r"\{\{\s*Succession table monarch(.*?)\n\}\}", body, re.S | re.I):
        params = {}
        for pm in re.finditer(r"^\|\s*([a-z_]+?)(\d+)\s*=\s*(.*)$", m.group(1), re.M):
            params.setdefault(int(pm.group(2)), {})[pm.group(1)] = pm.group(3).strip()
        for k in sorted(params):
            d = params[k]
            nm = person(d.get("name", ""))
            if not nm:
                continue
            a = years(clean(d.get("reignstart", "") or d.get("start", "")), bc)
            b = years(clean(d.get("reignend", "") or d.get("end", "")), bc)
            if a is None and d.get("reign"):
                y = years(clean(d["reign"]), bc)
                a, b = (y, y) if y else (None, None)
            if a:
                end = b[1] if b and b[1] >= a[0] else a[1]
                out.append((nm, a[0], end))
    return out


def _tpl(m):
    body = m.group(1)
    parts = [p.strip() for p in body.split("|")]
    name = parts[0].lower().strip()
    pos = [p for p in parts[1:] if "=" not in p or re.match(r"^\d", p)]
    if name in ("circa", "c.", "c", "ca", "ca.", "circa."):
        if len(pos) >= 2:
            return "c. " + pos[0] + "–" + pos[1]
        return "c. " + " ".join(pos) if pos else "c. "
    if name in ("reign", "r.", "r"):
        return "r. " + "–".join(pos[:2]) if pos else "r. "
    if name in ("bce", "bc"):
        return (pos[0] + " BC") if pos else "BC"
    if name in ("ce", "ad"):
        return (pos[0] + " AD") if pos else "AD"
    if name == "=":
        return "="
    if name == "!":
        return "|"
    if name in ("snd", "ndash", "spaced ndash", "mdash", "spnd", "–", "nbsp–", "dash"):
        return " – "
    if name in ("floruit", "fl.", "fl"):
        return "fl. " + " ".join(pos)
    if name in ("nowrap", "small", "big", "nobr", "nts", "abbr", "lang", "transl", "transliteration", "noitalic",
                "sort", "sortname", "nihongo", "tooltip", "hlist", "plainlist", "ubl", "unbulleted list", "smaller",
                "resize", "center", "nobold", "vanchor", "anchor", "ill", "interlanguage link", "sc", "smallcaps",
                "korean", "zh", "hanja", "lang-zh", "linktext", "flagicon", "midsize", "nowrap begin", "angbr"):
        if name in ("sort", "lang", "transl", "transliteration", "tooltip", "lang-zh") and len(pos) >= 2:
            return pos[1] if name != "tooltip" else pos[0]
        if name == "sortname" and len(pos) >= 2:
            return pos[0] + " " + pos[1]
        if name in ("ill", "interlanguage link", "vanchor", "anchor", "linktext"):
            return pos[0] if pos else ""
        return " ".join(pos)
    if name in ("dts", "date", "start date", "end date", "birth date", "death date", "start date and age", "dte"):
        nums = [p for p in pos if re.match(r"^-?\d{1,4}$", p)]
        return " ".join(nums[:1]) if nums else ""
    if name.startswith(("efn", "sfn", "refn", "cn", "citation needed", "r|", "rp", "harvnb", "marriage", "age in",
                        "hiero", "clarify", "dubious", "which", "when", "who", "notetag", "ref label", "#tag",
                        "cite", "coord", "image", "flag", "efn-", "nbsp", "-", "clear", "sup", "note", "ref")):
        return ""
    return " "


def clean(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"\[\[(?:File|Image):(?:[^\[\]]|\[\[[^\]]*\]\])*\]\]", "", s)
    for _ in range(6):
        t = re.sub(r"\{\{([^{}]*)\}\}", _tpl, s)
        if t == s:
            break
        s = t
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[https?://[^\s\]]+\s*([^\]]*)\]", r"\1", s)
    s = re.sub(r"<br\s*/?>|<[^>]+>", " ", s)
    s = s.replace("'''", "").replace("''", "").replace("&nbsp;", " ").replace("&ndash;", "–").replace("&minus;", "−")
    return re.sub(r"\s+", " ", s).strip()


def dates_to_years(s):
    era = lambda m: m.group(2) + (" " + m.group(1) if m.group(1) else "")
    s = re.sub(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{MONTHS})\.?,?\s+(?:(AD|CE)\s+)?(\d{{1,4}})", era, s)
    s = re.sub(rf"\b(?:{MONTHS})\.?\s+\d{{1,2}},?\s+(?:(AD|CE)\s+)?(\d{{1,4}})", era, s)
    s = re.sub(r"\b(AD|CE)\s+(\d{1,4})\b", r"\2 \1", s)
    s = re.sub(rf"\b(?:{MONTHS})\.?\s+(\d{{3,4}})", r"\1", s)
    return s


ONE = r"(?:(?:c\.|ca\.|circa|r\.|fl\.|after|before|by|from)\s*)?(\d{1,4})(?:\s*/\s*\d{1,4})?(?:\s*\?)?\s*(BCE|BC|B\.C\.|CE|AD|A\.D\.)?"
RANGE = re.compile(ONE + r"\s*(?:–|-|—|−|‒|to|until|till)\s*(?:c\.\s*|ca\.\s*)?(\d{1,4}|present|current|now|incumbent)(?:\s*/\s*\d{1,4})?(?:\s*\?)?\s*(BCE|BC|B\.C\.|CE|AD|A\.D\.)?")
SINGLE = re.compile(ONE)


def years(text, bc=False):
    """First year range in a cleaned string -> (start, end) or None. bc: bare years are BC."""
    s = dates_to_years(text)
    s = re.sub(r"\b\d+\s*(?:\+\s*)?(?:or\s+\d+\s+)?(?:years?|yrs?|months?|days?|weeks?)\b", " ", s)
    s = re.sub(r"\b(?:aged?|age)\s+\d+", " ", s)
    m = RANGE.search(s)
    if m:
        a, ea, b, eb = m.group(1), (m.group(2) or "").upper().replace(".", ""), m.group(3), (m.group(4) or "").upper().replace(".", "")
        a = int(a)
        if b in ("present", "current", "now", "incumbent"):
            return (a if not (ea.startswith("B") or (bc and not ea)) else -a), 2026
        b_i = int(b)
        if len(b) <= 2 and a >= 100 and not eb and b_i < a % 100 + 100:      # "1405-33"
            b_i = a // 100 * 100 + b_i
            if b_i < a:
                b_i += 100
        a_bc = ea.startswith("B") or (not ea and (eb.startswith("B") or (bc and not eb.startswith(("A", "C")))))
        b_bc = eb.startswith("B") or (not eb and a_bc and not ea.startswith(("A", "C")))
        if ea.startswith(("A", "C")):
            a_bc = False
        sa, sb = (-a if a_bc else a), (-b_i if b_bc else b_i)
        if sb < sa:
            if a_bc and not b_bc and not eb:     # "185–149" read as BC
                sb = -b_i
            if sb < sa:
                return None
        return sa, sb
    m = SINGLE.search(s)
    if m and int(m.group(1)) >= 1 and (len(m.group(1)) >= 3 or m.group(2) or re.match(r"(?:c\.|ca\.|circa|r\.|fl\.)", m.group(0))):
        e = (m.group(2) or "").upper().replace(".", "")
        y = int(m.group(1))
        y = -y if e.startswith("B") or (bc and not e) else y
        return y, y
    return None


LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")


def person(raw, prefer_target=False):
    """Name from a raw cell or line: the first link that is not a file/year/place-list, else bold or plain text."""
    raw = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>|<!--.*?-->", "", raw, flags=re.S)
    raw = re.sub(r"\[\[(?:File|Image):(?:[^\[\]]|\[\[[^\]]*\]\])*\]\]", "", raw)
    for m in LINK.finditer(raw):
        tgt, alias = m.group(1).strip(), (m.group(2) or "").strip()
        if re.match(r"^\d", tgt) or tgt.lower().startswith(("list of", "category:", "wikt:", "file:", "image:")):
            continue
        nm = clean(tgt if prefer_target and tgt else (alias or tgt))
        nm = re.sub(r"\s*\([^()]*\)$", "", nm).strip()
        if nm and not re.match(r"^\d", nm):
            return nm
    m = re.search(r"'''(.+?)'''", raw)
    txt = clean(m.group(1) if m else raw)
    txt = re.split(r"\s*[\(,;:]\s*|\s+[–-]\s+|\s+r\.\s", txt)[0].strip()
    return txt if txt and not re.match(r"^[\d\W]", txt) and len(txt) <= 60 else ""


def sections(text):
    """[(heading path, body)] with the lead as ''. Skips See also, References and the like."""
    out, path = [], []
    pos, cur = 0, ""
    for m in re.finditer(r"^(={2,6})\s*(.*?)\s*\1\s*$", text, re.M):
        out.append((" / ".join(path), text[pos:m.start()]))
        lvl = len(m.group(1)) - 2
        path = path[:lvl] + [clean(m.group(2))]
        pos = m.end()
    out.append((" / ".join(path), text[pos:]))
    return [(h, b) for h, b in out if not (h and SKIP_SECTIONS.match(h.split(" / ")[-1]))]


def tables(body):
    """Each wikitable -> (header cells, rows of cells, caption), rowspan/colspan expanded. Cells are raw
    wikitext. A table starts at a line beginning "{|" and ends at a line beginning "|}"."""
    out, lines, depth, buf = [], body.split("\n"), 0, []
    for line in lines:
        s = line.lstrip()
        if s.startswith("{|"):
            depth += 1
            if depth == 1:
                buf = []
                continue
        elif s.startswith("|}"):
            depth -= 1
            if depth == 0:
                out.append(_table("\n".join(buf)))
                continue
        if depth >= 1:
            buf.append(line)
    return out


def protect_inner_headings(text):
    """A heading line inside a table (List of Chinese monarchs does this) becomes a marker row, so the
    table stays whole and the rows after it know their heading."""
    out, depth = [], 0
    for line in text.split("\n"):
        s = line.lstrip()
        if s.startswith("{|"):
            depth += 1
        elif s.startswith("|}"):
            depth = max(0, depth - 1)
        m = re.match(r"^(={2,6})\s*(.*?)\s*\1\s*$", line)
        if m and depth > 0:
            out.append("|-")
            out.append("|@@H@@" + clean(m.group(2)))
            out.append("|-")
            continue
        out.append(line)
    return "\n".join(out)


def _cells(line, sep):
    parts = re.split(r"\s*" + re.escape(sep * 2) + r"\s*", line)
    cells = []
    for p in parts:
        attrs, val = "", p
        m = re.match(r"^([^\[\]{}|]*?=[^\[\]{}|]*)\|(?!\|)(.*)$", p, re.S)
        if m and re.search(r"(?i)(?:rowspan|colspan|style|class|scope|align|width|bgcolor|data-sort|valign|id)\s*=", m.group(1)):
            attrs, val = m.group(1), m.group(2)
        rs = re.search(r"(?i)rowspan\s*=\s*\"?(\d+)", attrs)
        cs = re.search(r"(?i)colspan\s*=\s*\"?(\d+)", attrs)
        cells.append((val.strip(), int(rs.group(1)) if rs else 1, int(cs.group(1)) if cs else 1))
    return cells


def _table(t):
    cap = re.search(r"^\s*\|\+\s*(.*)$", t, re.M)
    caption = clean(cap.group(1)) if cap else ""
    rows, cur, header = [], [], []
    is_header_row = []
    for line in t.split("\n"):
        s = line.strip()
        if s.startswith("|-"):
            if cur:
                rows.append(cur)
            cur = []
            continue
        if s.startswith("|+"):
            continue
        if s.startswith("!"):
            cur += [(c, r, k, True) for c, r, k in _cells(s[1:], "!")]
        elif s.startswith("|"):
            cur += [(c, r, k, False) for c, r, k in _cells(s[1:], "|")]
        elif cur:
            c, r, k, h = cur[-1]
            cur[-1] = (c + "\n" + line, r, k, h)
    if cur:
        rows.append(cur)
    # expand spans into a grid
    grid, carry = [], {}
    for row in rows:
        out, col, it = [], 0, iter(row)
        pending = list(row)
        while pending or col in carry:
            if col in carry:
                val, left, hdr = carry[col]
                out.append((val, hdr))
                if left <= 1:
                    del carry[col]
                else:
                    carry[col] = (val, left - 1, hdr)
                col += 1
                continue
            c, r, k, h = pending.pop(0)
            for _ in range(max(1, min(k, 20))):
                out.append((c, h))
                if r > 1:
                    carry[col] = (c, r - 1, h)
                col += 1
        grid.append(out)
    hdr_rows = [r for r in grid if r and all(h for _c, h in r)]
    header = []
    if hdr_rows:
        header = [clean(c).lower() for c, _h in hdr_rows[-1]]
    body = [[c for c, h in r] for r in grid if r and not all(h for _c, h in r)]
    # a leading header cell in a data row ("!scope=row | Name") is data
    return header, body, caption


NAME_H = re.compile(r"\b(names?|regnal names?|rulers?|king|queen|monarch|emperor|empress|pharaoh|sultan|shah|nawab|raja|maharaja|tlatoani|"
                    r"tlatoque|consul|consuls|chanyu|khan|caliph|president|governor|governor-general|prince|duke|imam|"
                    r"posthumous|personal|throne|regnal name|sovereign|lord|chief|negus|mansa|askia|tsar|czar|doge)\b")
REIGN_H = re.compile(r"\b(reign|reigned|ruled|rule|period|dates|date|tenure|term|years|regnal(?! names?)|in office|time in office|duration)\b")
START_H = re.compile(r"\b(accession|from|start|began|begin|took office|assumed office|succeeded|enthroned|acceded)\b")
END_H = re.compile(r"\b(ended|end|to|until|left office|deposed|reign ended)\b")
BAD_H = re.compile(r"\b(birth|born|death|died|spouse|consort|marriage|portrait|image|coat|arms|tomb|burial|notes|comments|claim|house|parents?)\b")


def table_rows(header, body, bc=False, prefer_target=False, name_h=None):
    """-> [(name, start, end)] from one table."""
    data = [r for r in body if not (r and r[0].startswith("@@H@@"))]
    if not data:
        return []
    ncol = max(len(r) for r in data)
    h = header + [""] * (ncol - len(header))
    name_c = next((i for i, x in enumerate(h) if name_h and re.search(name_h, x)), None)
    if name_c is None:
        name_c = next((i for i, x in enumerate(h) if NAME_H.search(x) and not BAD_H.search(x) and not REIGN_H.search(x)), None)
    start_c = next((i for i, x in enumerate(h) if START_H.search(x) and not BAD_H.search(x)), None)
    end_c = next((i for i, x in enumerate(h) if i != start_c and END_H.search(x) and not BAD_H.search(x)), None)
    reign_c = next((i for i, x in enumerate(h) if REIGN_H.search(x) and not BAD_H.search(x) and i not in (start_c, end_c)), None)

    def frac(c, f):
        vals = [r[c] for r in data if c < len(r)]
        return sum(1 for v in vals if f(v)) / max(1, len(vals))
    if name_c is None:
        cand = [c for c in range(ncol) if not BAD_H.search(h[c]) and frac(c, lambda v: bool(LINK.search(v)) and not v.strip().startswith("[[File")) >= 0.5]
        name_c = cand[0] if cand else 0
    if reign_c is None and (start_c is None):
        cand = [c for c in range(ncol) if c != name_c and not BAD_H.search(h[c]) and frac(c, lambda v: RANGE.search(dates_to_years(clean(v))) is not None) >= 0.5]
        reign_c = cand[0] if cand else None
    out, sub = [], ""
    for r in body:
        if r and r[0].startswith("@@H@@"):
            sub = r[0][5:].strip()
            continue
        if name_c >= len(r):
            continue
        nm = person(r[name_c], prefer_target)
        if not nm:
            continue
        y = None
        if start_c is not None and end_c is not None and start_c < len(r):
            a = years(clean(r[start_c]), bc)
            endtxt = clean(r[end_c]) if end_c < len(r) else ""
            b = years(endtxt, bc) if endtxt else None
            if b is None and re.search(r"(?i)present|incumbent|current|reigning", endtxt):
                b = (2026, 2026)
            if a:
                y = (a[0], b[1] if b and b[1] >= a[0] else a[1])
        if y is None and reign_c is not None and reign_c < len(r):
            y = years(clean(r[reign_c]), bc)
        if y is None and start_c is not None and start_c < len(r):
            a = years(clean(r[start_c]), bc)
            b = years(clean(r[end_c]), bc) if end_c is not None and end_c < len(r) else None
            if a:
                y = (a[0], b[1] if b else a[1])
        if y is None:
            y = years(clean(r[name_c]).split(nm, 1)[-1], bc)     # dates written in the name cell
        if y and y[1] >= y[0]:
            out.append((nm, y[0], y[1], sub))
    return out


def bullet_rows(body, bc=False):
    out = []
    for line in body.split("\n"):
        s = line.strip()
        m = re.match(r"^([*#]+)\s*(.*)$", s)
        if not m or len(m.group(1)) > 1:
            continue
        raw = m.group(2)
        nm = person(raw)
        if not nm:
            continue
        c = clean(raw)
        rest = c.split(nm, 1)[-1] if nm in c else c
        y = years(rest, bc)
        if y and y[1] >= y[0]:
            out.append((nm, y[0], y[1]))
    return out


def era_of(head):
    """Bare years are BC when the innermost heading that names an era names BC only
    ("Ancient Iran (c. 727 BC-AD 651) / Achaemenid Empire (550-330 BC)" -> BC)."""
    for seg in reversed(head.split(" / ")):
        b = bool(re.search(r"\bBCE?\b", seg))
        a = bool(re.search(r"\b(AD|CE)\b", seg))
        if b and not a:
            return True
        if a and not b:
            return False
    return False


def extract(text, section=None, bc=False, use_tables=True, use_bullets=True, prefer_target=False, name_h=None):
    """-> [(name, start, end, heading)]. section: regex a heading path must match."""
    out = []
    text = protect_inner_headings(strip_noise(text))
    for head, body in sections(text):
        if section and not re.search(section, head, re.I):
            continue
        sec_bc = bc or era_of(head)
        if use_tables:
            for header, rows, caption in tables(body):
                tb = sec_bc or (bool(re.search(r"\bBCE?\b", caption)) and not re.search(r"\b(AD|CE)\b", caption))
                for nm, a, b, sub in table_rows(header, [r for r in rows], tb, prefer_target, name_h):
                    out.append((nm, a, b, head + (" / " + sub if sub else "") + (" | " + caption if caption else "")))
        for nm, a, b in succession_tables(body, sec_bc):
            out.append((nm, a, b, head))
        if use_bullets:
            nobox = re.sub(r"\{\|.*?\n\|\}", "", body, flags=re.S)
            for nm, a, b in bullet_rows(nobox, sec_bc):
                out.append((nm, a, b, head))
    return out


def main_links(text, section):
    """{{main|List of Gupta emperors}} targets inside the sections matching `section`."""
    out = []
    for head, body in sections(text):
        if re.search(section, head, re.I):
            for m in re.finditer(r"\{\{\s*(?:main|see also|further)\s*\|([^}]*)\}\}", body, re.I):
                out += [p.strip() for p in m.group(1).split("|") if p.strip() and "=" not in p]
    return out
