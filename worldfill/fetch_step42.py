#!/usr/bin/env python3
"""Step 42 (C18, law and rights by era): fetch the dated law tables of English Wikipedia.

Prose is not a data source. Reading 164 capital-punishment articles for a year each is a prose
extraction problem, and prose extraction is where a pack quietly goes wrong - a sentence about a
*proposed* abolition reads exactly like one about an enacted one. Three Wikipedia pages hold these
facts as **tables of jurisdiction and year**, which is a different and far safer problem:

  * `Timeline of abolition of slavery and serfdom`   Date | Jurisdiction | Description
  * `Women's suffrage`                               Country | Year women first granted suffrage
  * `Use of capital punishment by country`           Country | ... | Year abolished | Notes

Run:  python3 fetch_step42.py            fetch what is missing
      python3 fetch_step42.py --report   what is on disk, parsed
Nothing else is fetched: no Wikidata query belongs to this file.
"""
import gzip
import io, json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw", "step42")
API = "https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "eternal-engine-data-fetch/1.0 (research; local)"}

PAGES = {
    "slavery": "Timeline of abolition of slavery and serfdom",
    "suffrage": "Women's suffrage",
    "capital": "Use of capital punishment by country",
}

# --------------------------------------------------------------------------- HTML -> plain text
#
# The first version of this file parsed wikitext. It lost the Jurisdiction column wholesale: a cell
# holds `[[File:Owl of Athena.png|22px]] Polis of [[Classical Athens|Athens]]`, and no regex over
# wikitext survives both the nested template and the pipe inside the file link. The rendered HTML
# has already done that work - templates expanded, images down to an <img> tag, links to <a> - so
# this parses HTML instead. Cheaper to get right, and right is what a data pack needs.

import html as _html

TABLE = re.compile(r"<table\b.*?</table>", flags=re.S | re.I)
ROW = re.compile(r"<tr\b.*?</tr>", flags=re.S | re.I)
CELL = re.compile(r"<t[dh]\b([^>]*)>(.*?)</t[dh]>", flags=re.S | re.I)
TAG = re.compile(r"<[^>]+>")
COMMENT = re.compile(r"<!--.*?-->", flags=re.S)
SUP = re.compile(r"<sup\b.*?</sup>", flags=re.S | re.I)


def strip_html(cell):
    """One cell as text: no tags, no footnotes, no images, entities decoded."""
    t = SUP.sub("", cell)
    t = re.sub(r"<img[^>]*>", "", t, flags=re.I)
    t = COMMENT.sub("", t)
    t = re.sub(r"<style\b.*?</style>", "", t, flags=re.S | re.I)
    t = TAG.sub(" ", t)
    t = _html.unescape(t)
    t = t.replace("\u00a0", " ")
    t = re.sub(r"\[\d+\]", "", t)          # leftover footnote markers
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def _span(attrs, name):
    m = re.search(name + r'\s*=\s*"(\d+)"', attrs or "", flags=re.I)
    if m:
        return int(m.group(1))
    m = re.search(name + r"\s*=\s*'(\d+)'", attrs or "", flags=re.I)
    return int(m.group(1)) if m else 1


def tables(page_html):
    """Every table in the page, as rows of equal-length cell lists.

    Row and column spans are **reconstructed rather than ignored**, which matters more than it
    sounds: in the slavery timeline a date such as `1800` is written once and covers the next two
    rows, so a parser that skips a spanned column silently refiles two law changes under the wrong
    year. A carried cell is repeated in every row it covers.
    """
    out = []
    for tm in TABLE.finditer(page_html):
        rows = []
        carried = []                 # (column, how many further rows to cover, text)
        for rm in ROW.finditer(tm.group(0)):
            row = {}
            following = []
            for col, left, text in carried:
                row[col] = text
                if left - 1 > 0:
                    following.append((col, left - 1, text))
            carried = following
            col = 0
            for m in CELL.finditer(rm.group(0)):
                attrs = m.group(1)
                text = strip_html(m.group(2))
                rs, cs = _span(attrs, "rowspan"), _span(attrs, "colspan")
                while col in row:
                    col += 1
                for k in range(max(1, cs)):
                    row[col] = text if k == 0 else ""
                    if rs > 1:
                        carried.append((col, rs - 1, text))
                    col += 1
            if row:
                width = max(row) + 1
                cells = [row.get(i, "") for i in range(width)]
                if any(c for c in cells):
                    rows.append(cells)
        if len(rows) > 1:
            out.append(rows)
    return out


def strip_wiki(text):
    """Kept for the year parser, which is fed plain cells either way."""
    return text or ""


# --------------------------------------------------------------------------- years

MONTHS = ("january february march april may june july august september october november december").split()
ORDINALS = {"early": 0, "mid": 0, "late": 0}

def year_of(text):
    """The year in a cell, or None. '1919' -> 1919; '13 May 1888' -> 1888; 'c. 1865' -> 1865;
    'Early sixth century BC' -> None, which is the honest answer for a date nobody can pin down."""
    if not text:
        return None
    t = strip_wiki(text)
    if not t:
        return None
    t = t.replace(",", " ")
    m = re.search(r"\b(\d{3,4})\b(?:\s*(?:BC|BCE|AD|CE))?", t, flags=re.I)
    if not m:
        # "sixth century BC" and the like: no year can be honestly given
        return None
    y = int(m.group(1))
    if re.search(r"\b(?:BC|BCE)\b", t, flags=re.I):
        y = -y
    if not (-4000 <= y <= 2026):
        return None
    return y


# --------------------------------------------------------------------------- fetch

def wikitext(title):
    """The page, rendered. The name is kept because the callers below read better with it."""
    q = urllib.parse.urlencode({"action": "parse", "page": title, "prop": "text",
                                "format": "json", "redirects": "1"})
    req = urllib.request.Request(API + "?" + q, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as f:
        d = json.load(f)
    if "error" in d:
        raise RuntimeError(d["error"].get("info", str(d["error"])))
    return d["parse"]["text"]["*"]


def fetch():
    os.makedirs(RAW, exist_ok=True)
    for key, title in PAGES.items():
        path = os.path.join(RAW, key + ".html.gz")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            print("  %-10s already on disk" % key)
            continue
        for attempt in range(4):
            try:
                w = wikitext(title)
                with open(path, "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as f:
                    f.write(w)
                print("  %-10s %8d chars -> %s" % (key, len(w), os.path.basename(path)))
                break
            except Exception as e:
                print("  %-10s attempt %d: %s" % (key, attempt, str(e)[:70]))
                time.sleep(15)
        time.sleep(3)


def load(key):
    with gzip.open(os.path.join(RAW, key + ".html.gz"), "rt", encoding="utf-8") as f:
        return f.read()


def report():
    for key in PAGES:
        w = load(key)
        ts = tables(w)
        print("%-10s %d tables, %d rows" % (key, len(ts), sum(len(t) for t in ts)))
        for ti, t in enumerate(ts):
            head = [strip_wiki(c) for c in t[0]]
            print("   table %d: %d rows, header %s" % (ti, len(t), head[:7]))
            for r in t[1:4]:
                print("       " + " | ".join(strip_wiki(c)[:40] for c in r[:7]))


if __name__ == "__main__":
    if "--report" in sys.argv:
        report()
    else:
        fetch()
