#!/usr/bin/env python3
"""Offline English Wikipedia from its public dump files: no API calls, so no rate limit.

The Wikimedia APIs allow about 10 requests a minute without contact details. The dump files on
dumps.wikimedia.org are static files that allow HTTP range requests. This module uses them
instead. The dump is pinned to one date so the stream offsets and the index always agree.

Builds ~/.cache/wpdump/wp.sqlite (a few GB; ~/.cache is never snapshotted):
  titles(title, page_id, off)  every namespace-0 title (articles and redirects) -> page id and
                               the byte offset of its bz2 stream in the multistream dump
  streams(off)                 every stream start, so a stream ends where the next one starts
  redirects(page_id, target)   redirect page id -> target title (namespace 0, fragment dropped)
  geo(page_id, lat, lon, dim, type, country, region)
                               the article's primary {{coord}}, from Wikipedia's own geo_tags
  props(page_id, qid, shortdesc, disambig)
                               Wikidata item id, short description, disambiguation flag

`texts(titles)` returns wikitext, fetching only the streams that hold the wanted pages (each
stream holds about 100 pages).

Usage:
  python3 wpdump.py build          download the four small files and build the database
  python3 wpdump.py page "1066"    print one page's wikitext (smoke test)
  python3 wpdump.py info "Golconda Fort" "France" ...
"""
import bz2, gzip, html, os, re, sqlite3, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

DATE = "20261001"
BASE = f"https://dumps.wikimedia.org/enwiki/{DATE}/"
DIR = os.path.expanduser("~/.cache/wpdump")
DB = os.path.join(DIR, "wp.sqlite")
UA = "EternalEngineWorldFill/1.0 (historical data build; research use)"
FILES = {
    "index": f"enwiki-{DATE}-pages-articles-multistream-index.txt.bz2",
    "xml": f"enwiki-{DATE}-pages-articles-multistream.xml.bz2",
    "redirect": f"enwiki-{DATE}-redirect.sql.gz",
    "geo": f"enwiki-{DATE}-geo_tags.sql.gz",
    "props": f"enwiki-{DATE}-page_props.sql.gz",
}
NS = re.compile(r"^(?:Wikipedia|File|MediaWiki|Template|Help|Category|Portal|Draft|TimedText|"
                r"Module|Event|Topic|Gadget|Gadget definition|Book|Education Program|"
                r"Image|User|Special|Talk|[A-Za-z ]+ talk):")
KEEP_PROPS = {"wikibase_item", "wikibase-shortdesc", "disambiguation"}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def url(key):
    return BASE + FILES[key]


def path(key):
    return os.path.join(DIR, FILES[key])


def _open(u, headers=None, timeout=90):
    h = {"User-Agent": UA}
    h.update(headers or {})
    return urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=timeout)


def remote_size(key):
    req = urllib.request.Request(url(key), method="HEAD", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return int(r.headers["Content-Length"])


def download(key):
    os.makedirs(DIR, exist_ok=True)
    p, tmp = path(key), path(key) + ".part"
    size = remote_size(key)
    if os.path.exists(p) and os.path.getsize(p) == size:
        return p
    have = os.path.getsize(tmp) if os.path.exists(tmp) else 0
    t0, tries = time.time(), 0
    while have < size:
        try:
            with _open(url(key), {"Range": f"bytes={have}-"}) as r, open(tmp, "ab") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
                    have += len(b)
        except Exception as e:                       # resume after a dropped connection
            tries += 1
            if tries > 20:
                raise
            log(f"  {key}: {e}; resuming at {have}")
            time.sleep(min(60, 5 * tries))
    os.rename(tmp, p)
    log(f"downloaded {FILES[key]}: {size / 1e6:.0f} MB in {time.time() - t0:.0f}s")
    return p


# ------------------------------------------------------------------ SQL dump parsing
VAL = r"('(?:[^'\\]|\\.)*'|NULL|[-+0-9.eE]+)"
_UNESC = re.compile(r"\\(.)")
_UNESC_MAP = {"0": "\0", "n": "\n", "r": "\r", "t": "\t", "Z": "\x1a"}


def tuple_re(n):
    return re.compile(r"\(" + ",".join([VAL] * n) + r"\)")


def sval(v):
    """One SQL literal -> str / None / number string."""
    if v == "NULL":
        return None
    if v.startswith("'"):
        return _UNESC.sub(lambda m: _UNESC_MAP.get(m.group(1), m.group(1)), v[1:-1])
    return v


def sql_rows(key, ncols):
    pat = tuple_re(ncols)
    inside = False                       # this MariaDB dump puts one row per line
    with gzip.open(path(key), "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("INSERT INTO"):
                inside = True
            if inside:
                for m in pat.finditer(line):
                    yield m.groups()
                if line.rstrip().endswith(";"):
                    inside = False


def norm(title):
    """MediaWiki title normalisation for namespace 0 (first letter upper case)."""
    t = html.unescape(title or "").replace("_", " ")
    t = t.split("#", 1)[0]
    t = re.sub(r"\s+", " ", t).strip()
    if t.startswith(":"):
        t = t[1:].strip()
    return t[:1].upper() + t[1:] if t else t


# ------------------------------------------------------------------ build
def connect():
    os.makedirs(os.path.join(DIR, "tmp"), exist_ok=True)
    os.environ["SQLITE_TMPDIR"] = os.path.join(DIR, "tmp")    # /tmp is a small RAM disk
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("PRAGMA temp_store=FILE")
    con.execute("PRAGMA cache_size=-150000")                     # 150 MB
    return con


def has_table(con, name):
    return con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                       (name,)).fetchone() is not None


def build_titles(con):
    con.execute("DROP TABLE IF EXISTS titles")
    con.execute("DROP TABLE IF EXISTS streams")
    con.execute("CREATE TABLE titles(title TEXT NOT NULL, page_id INTEGER NOT NULL, off INTEGER NOT NULL)")
    con.execute("CREATE TABLE streams(off INTEGER PRIMARY KEY)")
    rows, offs, last, n, t0 = [], [], -1, 0, time.time()
    with bz2.open(path("index"), "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            a = line.find(":")
            b = line.find(":", a + 1)
            off = int(line[:a])
            if off != last:
                offs.append((off,))
                last = off
            title = line[b + 1:].rstrip("\n")
            if NS.match(title):
                continue
            rows.append((title, int(line[a + 1:b]), off))
            if len(rows) >= 200000:
                con.executemany("INSERT INTO titles VALUES (?,?,?)", rows)
                con.executemany("INSERT OR IGNORE INTO streams VALUES (?)", offs)
                n += len(rows)
                rows.clear()
                offs.clear()
                if n % 2000000 == 0:
                    log(f"  titles {n:,} ({time.time() - t0:.0f}s)")
    con.executemany("INSERT INTO titles VALUES (?,?,?)", rows)
    con.executemany("INSERT OR IGNORE INTO streams VALUES (?)", offs)
    n += len(rows)
    con.commit()
    log(f"  titles {n:,} inserted; indexing ({time.time() - t0:.0f}s)")
    con.execute("CREATE INDEX titles_title ON titles(title)")
    con.commit()
    log(f"titles done: {n:,} ({time.time() - t0:.0f}s)")


def build_redirects(con):
    con.execute("DROP TABLE IF EXISTS redirects")
    con.execute("CREATE TABLE redirects(page_id INTEGER PRIMARY KEY, target TEXT NOT NULL)")
    rows, n, t0 = [], 0, time.time()
    for rd_from, ns, title, _iw, _frag in sql_rows("redirect", 5):
        if ns != "0":
            continue
        rows.append((int(rd_from), norm(sval(title))))
        if len(rows) >= 200000:
            con.executemany("INSERT OR REPLACE INTO redirects VALUES (?,?)", rows)
            n += len(rows)
            rows.clear()
    con.executemany("INSERT OR REPLACE INTO redirects VALUES (?,?)", rows)
    n += len(rows)
    con.commit()
    log(f"redirects done: {n:,} ({time.time() - t0:.0f}s)")


def build_geo(con):
    con.execute("DROP TABLE IF EXISTS geo")
    con.execute("CREATE TABLE geo(page_id INTEGER PRIMARY KEY, lat REAL, lon REAL, dim INTEGER, "
                "type TEXT, country TEXT, region TEXT)")
    rows, n, t0 = [], 0, time.time()
    for r in sql_rows("geo", 13):
        _id, pid, globe, primary, lat, lon, dim, typ, _name, country, region, _a, _b = r
        if sval(globe) != "earth" or primary != "1" or lat in (None, "NULL") or lon in (None, "NULL"):
            continue
        d = sval(dim)
        rows.append((int(pid), float(lat), float(lon), int(float(d)) if d else None,
                     sval(typ) or None, sval(country) or None, sval(region) or None))
        if len(rows) >= 200000:
            con.executemany("INSERT OR IGNORE INTO geo VALUES (?,?,?,?,?,?,?)", rows)
            n += len(rows)
            rows.clear()
    con.executemany("INSERT OR IGNORE INTO geo VALUES (?,?,?,?,?,?,?)", rows)
    n += len(rows)
    con.commit()
    log(f"geo done: {n:,} ({time.time() - t0:.0f}s)")


def build_props(con):
    con.execute("DROP TABLE IF EXISTS props")
    con.execute("CREATE TABLE props(page_id INTEGER PRIMARY KEY, qid TEXT, shortdesc TEXT, disambig INTEGER)")
    rows, n, t0 = [], 0, time.time()
    cur, acc = None, {}

    def flush():
        if cur is not None and acc:
            rows.append((cur, acc.get("wikibase_item"), acc.get("wikibase-shortdesc"),
                         1 if "disambiguation" in acc else 0))

    for page, name, value, _sk in sql_rows("props", 4):
        name = sval(name)
        if name not in KEEP_PROPS:
            continue
        p = int(page)
        if p != cur:
            flush()
            cur, acc = p, {}
            if len(rows) >= 200000:
                con.executemany("INSERT OR REPLACE INTO props VALUES (?,?,?,?)", rows)
                n += len(rows)
                rows.clear()
                if n % 2000000 < 200000:
                    log(f"  props {n:,} ({time.time() - t0:.0f}s)")
        acc[name] = sval(value)
    flush()
    con.executemany("INSERT OR REPLACE INTO props VALUES (?,?,?,?)", rows)
    n += len(rows)
    con.commit()
    log(f"props done: {n:,} ({time.time() - t0:.0f}s)")


def build(force=False):
    t0 = time.time()
    for k in ("geo", "redirect", "index", "props"):
        download(k)
    con = connect()
    for name, fn in (("geo", build_geo), ("redirects", build_redirects),
                     ("titles", build_titles), ("props", build_props)):
        if force or not has_table(con, name) or not con.execute(f"SELECT 1 FROM {name} LIMIT 1").fetchone():
            fn(con)
    con.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
    con.execute("INSERT OR REPLACE INTO meta VALUES ('xml_size', ?)", (str(remote_size("xml")),))
    con.execute("INSERT OR REPLACE INTO meta VALUES ('date', ?)", (DATE,))
    con.commit()
    log(f"BUILD DONE in {time.time() - t0:.0f}s; {os.path.getsize(DB) / 1e9:.2f} GB")


# ------------------------------------------------------------------ lookups
class Wiki:
    def __init__(self):
        self.con = connect()
        self.xml_size = int(self.con.execute("SELECT v FROM meta WHERE k='xml_size'").fetchone()[0])

    def lookup(self, title):
        """title -> (final title, page_id, off, redirected) following up to 3 redirects."""
        t = norm(title)
        seen = False
        for _ in range(4):
            if not t:
                return None
            row = self.con.execute("SELECT page_id, off FROM titles WHERE title=?", (t,)).fetchone()
            if not row:
                return None
            r = self.con.execute("SELECT target FROM redirects WHERE page_id=?", (row[0],)).fetchone()
            if not r:
                return (t, row[0], row[1], seen)
            t, seen = norm(r[0]), True
        return None

    def info(self, page_id):
        g = self.con.execute("SELECT lat, lon, dim, type, country, region FROM geo WHERE page_id=?",
                             (page_id,)).fetchone()
        p = self.con.execute("SELECT qid, shortdesc, disambig FROM props WHERE page_id=?",
                             (page_id,)).fetchone()
        return {
            "geo": None if not g else {"lat": g[0], "lon": g[1], "dim": g[2], "type": g[3],
                                       "country": g[4], "region": g[5]},
            "qid": p[0] if p else None, "shortdesc": p[1] if p else None,
            "disambig": bool(p and p[2]),
        }

    def _stream_end(self, off):
        r = self.con.execute("SELECT off FROM streams WHERE off > ? ORDER BY off LIMIT 1", (off,)).fetchone()
        return (r[0] if r else self.xml_size) - 1

    def texts(self, titles, workers=2, progress=None):
        """{requested title: (final title, wikitext)} for every title that exists."""
        want, by_off = {}, {}
        for t in titles:
            hit = self.lookup(t)
            if hit:
                want[t] = hit
                by_off.setdefault(hit[2], set()).add(hit[1])
        jobs = [(off, self._stream_end(off), ids) for off, ids in sorted(by_off.items())]
        got = {}

        def fetch(job):
            off, end, ids = job
            for attempt in range(8):
                try:
                    with _open(url("xml"), {"Range": f"bytes={off}-{end}"}, timeout=120) as r:
                        data = r.read()
                    return parse_stream(bz2.decompress(data).decode("utf-8", "replace"), ids)
                except Exception as e:
                    time.sleep(min(60, 4 * (attempt + 1)))
                    err = e
            raise err

        done = 0
        with ThreadPoolExecutor(max_workers=workers) as ex:      # dumps policy: <= 2-3 connections
            for res in ex.map(fetch, jobs):
                got.update(res)
                done += 1
                if progress and done % 100 == 0:
                    progress(done, len(jobs))
        return {t: (hit[0], got[hit[1]]) for t, hit in want.items() if hit[1] in got}


PAGE_RE = re.compile(r"<page>(.*?)</page>", re.S)
ID_RE = re.compile(r"<id>(\d+)</id>")
TEXT_RE = re.compile(r"<text\b[^>]*?(?:/>|>(.*?)</text>)", re.S)


def parse_stream(xml, ids):
    out = {}
    for m in PAGE_RE.finditer(xml):
        body = m.group(1)
        pid = int(ID_RE.search(body).group(1))
        if pid in ids:
            t = TEXT_RE.search(body)
            out[pid] = html.unescape(t.group(1) or "") if t else ""
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "build":
        build(force="--force" in sys.argv)
    elif cmd == "page":
        w = Wiki()
        for t, (final, text) in w.texts(sys.argv[2:]).items():
            print(f"=== {t} -> {final} ({len(text)} chars)\n{text[:1500]}")
    elif cmd == "info":
        w = Wiki()
        for t in sys.argv[2:]:
            hit = w.lookup(t)
            print(t, "->", hit, w.info(hit[1]) if hit else None)
    else:
        print(__doc__)
