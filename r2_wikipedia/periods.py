"""Recognize Wikipedia time-period titles, not historical facts.

Ranges use the Eternal Engine convention: negative = BCE, positive = CE, no year 0.
Title matches are *candidates*. A numeric title may be about a number rather than a year;
check the actual page before extracting facts. Ranges intersect the requested years.
"""
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Period:
    kind: str
    start: int
    end: int


def classify(title):
    s = title.strip()
    m = re.fullmatch(r'([1-9]\d*)(?:st|nd|rd|th) (century|millennium)( BC)?', s, re.I)
    if m:
        n = int(m.group(1)); kind = m.group(2).lower(); bc = bool(m.group(3))
        if not n: return None
        width = 100 if kind == 'century' else 1000
        lo, hi = (n - 1) * width + 1, n * width
        start, end = (-hi, -lo) if bc else (lo, hi)
    else:
        # Leading-zero names such as "00s" can be disambiguation pages, not
        # the canonical "0s" decade. Do not silently reinterpret them.
        m = re.fullmatch(r'(0|[1-9]\d*)s( BC)?(?: \(decade\))?', s, re.I)
        if m:
            n, bc = int(m.group(1)), bool(m.group(2)); kind = 'decade'
            lo, hi = max(1, n), n + 9
            start, end = (-hi, -lo) if bc else (lo, hi)
        else:
            m = re.fullmatch(r'(?:AD )?([1-9]\d{0,3})( BC| BCE| CE| AD| \(year\))?', s, re.I)
            if not m: return None
            n, suffix = int(m.group(1)), (m.group(2) or '').strip().upper()
            if not n: return None
            kind = 'year'
            start = end = -n if suffix in ('BC','BCE') else n
    if end < -3000 or start > 3000: return None
    return Period(kind, max(-3000,start), min(3000,end))


def priority(title):
    if title == 'List of decades, centuries, and millennia': return 0
    p = classify(title)
    return {'millennium': 10, 'century': 20, 'decade': 30, 'year': 40}.get(p.kind, 100) if p else 100
