#!/usr/bin/env python3
"""Small, dependency-free wikitext helpers for infobox fields (used by build_polity_facts.py).

infobox_params(text)   -> {name: raw value} for the first {{Infobox ...}} in text, split on the
                          top-level '|' only, so multi-line {{hlist|..}} values stay whole.
clean_items(raw)       -> ["Persian", "Chagatai"]: readable list items from a field value.
years_of(raw)          -> (start, end) years from '1526–1530', 'c. 3150 BC', '1922–1923 (last)'.
"""
import re

LIST_TEMPLATES = {"hlist", "ubl", "unbulleted list", "unbulleted", "plainlist", "plain list",
                  "flatlist", "flat list", "bulleted list", "bulleted", "collapsible list",
                  "unordered list", "cslist", "ordered list", "indented plainlist", "vunblist",
                  "startplainlist", "endplainlist", "enum", "tree list", "nowraplinks", "udl",
                  "unbulleted definition list", "ublist", "bulleted list,", "plainlist2", "fixed list"}
KEEP_FIRST = {"nowrap", "small", "smaller", "big", "larger", "nobold", "noitalic", "nobr", "lang-rtl",
              "noflag", "abbr", "linktext", "sc", "smallcaps", "font", "resize", "plain"}
DROP = {"efn", "sfn", "sfnp", "refn", "cn", "citation needed", "fact", "ref label", "note", "notetag",
        "efn-ua", "efn-lr", "efn-ur", "r", "rp", "harvnb", "harv", "nbsp", "-", "clarify", "when",
        "dubious", "flagicon", "flagicon image", "lang-x", "anchor", "ill", "nbsp;", "better source",
        "verify source", "reflist", "short description", "dead link", "update", "as of"}
JUNK = {"others", "other", "various", "minority", "minorities", "official", "regional", "see below",
        "list", "and others", "unknown", "none", "de facto", "de jure", "spoken", "lingua franca",
        "vernacular", "literary", "majority", "religion", "religions", "languages", "language",
        "local", "native", "and", "or", "etc", "etc.", "see", "including", "various others",
        "state religion", "official religion", "minority religions", "common languages",
        "official languages", "other languages", "court", "administrative", "liturgical",
        "sacred", "ceremonial", "spoken languages", "recognised", "recognized", "national",
        "secular state", "none official", "no official religion", "n/a", "na", "more", "many others",
        "many more", "others below", "majorities", "minorities:", "several", "multiple", "mixed", "diverse", "pluralism", "unofficial", "other religions",
        "other faiths", "irreligion", "no religion", "unaffiliated", "folk religions", "others/none", "none/other"}


def infobox_params(text):
    i = text.find("{{Infobox")
    if i < 0:
        i = text.find("{{infobox")
    if i < 0:
        return {}
    depth_t = depth_l = 0
    j = i
    parts, cur = [], []
    n = len(text)
    while j < n:
        two = text[j:j + 2]
        if two == "{{":
            depth_t += 1
            if depth_t > 1:
                cur.append(two)
            j += 2
            continue
        if two == "}}":
            depth_t -= 1
            if depth_t == 0:
                parts.append("".join(cur))
                break
            cur.append(two)
            j += 2
            continue
        if two == "[[":
            depth_l += 1
            cur.append(two)
            j += 2
            continue
        if two == "]]":
            depth_l = max(0, depth_l - 1)
            cur.append(two)
            j += 2
            continue
        c = text[j]
        if c == "|" and depth_t == 1 and depth_l == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(c)
        j += 1
    out = {}
    for p in parts[1:]:
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        k = k.strip().lower().replace(" ", "_")
        v = re.sub(r"<!--.*?-->", "", v, flags=re.S).strip()
        if k and v and k not in out:
            out[k] = v
    return out


def _expand_template(inner):
    parts = inner.split("|")
    name = parts[0].strip().lower().replace("_", " ")
    args = [a for a in parts[1:]]
    pos = [a for a in args if not re.match(r"^\s*[\w\- ]+\s*=", a)]
    if name in LIST_TEMPLATES:
        # Named values count as items too when they carry text ({{udl|wrap=\n; A\n: B}}).
        named = [a.split("=", 1)[1] for a in args if re.match(r"^\s*[\w\- ]+\s*=", a)
                 and a.split("=", 1)[0].strip().lower() not in ("class", "style", "item_style", "list_style",
                                                                 "title", "titlestyle", "frame_style", "liststyle")]
        return "\n" + "\n".join(pos + named) + "\n"
    if name in DROP or name.startswith("efn") or name.startswith("sfn") or name.startswith("cite"):
        return ""
    if name in ("circa", "c.", "c", "ca", "ca."):
        if len(pos) >= 2:
            return "c. " + pos[0] + "–" + pos[1]
        return "c. " + (pos[0] if pos else "")
    if name in ("lang", "native name", "transl", "transliteration", "native phrase", "script"):
        return pos[-1] if pos else ""
    if name.startswith("lang-") or name.startswith("langx") or name.startswith("script/"):
        return pos[-1] if pos else ""
    if name in KEEP_FIRST:
        return pos[0] if pos else ""
    if name in ("flag", "flagcountry", "flagu", "flagdeco", "country", "flag country"):
        return pos[0] if pos else ""
    if name in ("snd", "spaced ndash", "ndash", "spaced en dash", "en dash", "–", "endash", "nsndns", "spnd", "dash"):
        return " – "
    if name in ("mdash", "em dash"):
        return " — "
    if name in ("br", "break", "-"):
        return "\n"
    if name in ("bce", "bc"):
        return (pos[0] + " BC") if pos else " BC"
    if name in ("ce", "ad"):
        return (pos[0]) if pos else ""
    return ""


def clean_text(raw):
    s = raw
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<ref[^>/]*/>", "", s, flags=re.I)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.I | re.S)
    # Links first: a piped link inside a template would otherwise split its arguments.
    s = re.sub(r"\[\[(?:File|Image|Category):[^\[\]]*(?:\[\[[^\]]*\]\][^\[\]]*)*\]\]", "", s, flags=re.I)
    s = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    for _ in range(12):
        new = re.sub(r"\{\{([^{}]*)\}\}", lambda m: _expand_template(m.group(1)), s)
        if new == s:
            break
        s = new
    s = re.sub(r"\{\{|\}\}", "", s)
    s = re.sub(r"\[https?://\S+\s*([^\]]*)\]", r"\1", s)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</?(?:small|big|span|div|sup|sub|center|i|b|u|s|abbr|font|p|li|ul|ol)[^>]*>", "", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&ndash;", "–").replace("&mdash;", "—").replace("&amp;", "&")
    s = re.sub(r"'{2,}", "", s)
    return s


def clean_items(raw, max_items=5, split_and=True):
    s = clean_text(raw)
    s = re.sub(r"\([^()]*\)", "", s)
    s = re.sub(r"\([^()]*\)", "", s)
    s = re.sub(r"\[[^\]]*\]", "", s)
    items = []
    for line in re.split(r"[\n;•·]|\s/\s", s):
        line = line.strip(" *#:-–—,.\t")
        if not line:
            continue
        line = re.sub(r"^(?:majority|minority|minorities|official|officially|predominantly|mainly|"
                      r"common|others?|also|state religion|religions?|languages?|de facto|de jure)\s*:\s*",
                      "", line, flags=re.I)
        for piece in re.split(r",|\band\b" if split_and else r",", line):
            piece = re.sub(r"\d+(?:\.\d+)?\s*(?:[–-]\s*\d+(?:\.\d+)?\s*)?%", "", piece)   # "90–95%"
            piece = re.sub(r"^[\d.\s–-]+(?=[A-Za-z])|(?<=[A-Za-z])[\s–-]*[\d.]+[\s–-]*$", "", piece)
            piece = re.sub(r"\s+", " ", piece).strip(" *#:-–—,.\t\"'")
            if not piece or not re.search(r"[A-Za-z]", piece):
                continue
            if piece.lower() in JUNK or len(piece) > 40 or len(piece) < 2:
                continue
            if re.match(r"(?i)^(see|main|list of|refer)\b", piece):
                continue
            if re.search(r"\d{3,}", piece):
                continue
            if piece not in items:
                items.append(piece)
    return items[:max_items]


_ERA = r"(BCE|BC|B\.C\.|CE|AD|A\.D\.)"


def _yr(num, era):
    y = int(num)
    if era and era.upper().replace(".", "") in ("BC", "BCE"):
        return -y
    return y


def years_of(raw):
    """(start, end) from a year_leaderN value; end None when only one year is given."""
    s = clean_text(raw)
    s = re.sub(r"\([^()]*\)", " ", s)
    s = s.replace("−", "-").replace("—", "–")
    m = re.search(r"(\d{1,4})\s*" + _ERA + r"?\s*(?:–|-|to|until)\s*(?:c\.\s*|ca\.\s*)?(\d{1,4})\s*" + _ERA + r"?", s, re.I)
    if m:
        a, ea, b, eb = m.group(1), m.group(2), m.group(3), m.group(4)
        if not ea and eb and eb.upper().replace(".", "") in ("BC", "BCE"):
            ea = eb
        start, end = _yr(a, ea), _yr(b, eb)
        if start < 0 and end > 0 and not eb:
            end = -end
        if 0 < end < 100 and start > 100 and len(b) <= 2:
            end = start // 100 * 100 + end
        if end < start:
            return None
        return start, end
    m = re.search(r"(\d{1,4})\s*" + _ERA + r"?", s, re.I)
    if m:
        return _yr(m.group(1), m.group(2)), None
    return None


_PARTICLES = {"of", "the", "de", "von", "van", "al", "ibn", "bin", "bint", "la", "le", "da", "di", "del",
              "du", "y", "dos", "das", "der", "den", "zu", "ap", "mac", "ben", "el", "ul", "ud", "un",
              "and", "i", "e", "af", "av", "do", "z", "na"}
_NOT_NAME = re.compile(r"(?i)\b(depends|scholar|unknown|various|disputed|several|list|see|first|last|"
                       r"none|vacant|interregnum|council|collective|committee|regency|position|abolished|"
                       r"title|dynasty|monarchs?|kings?|rulers?|various)\b")


def clean_person(raw):
    """A leader field -> one readable name, or None when it is not one person's name."""
    items = clean_items(raw, 2, split_and=False)
    if not items:
        return None
    name = re.sub(r"\s+", " ", items[0]).strip()
    words = name.split(" ")
    if not (1 <= len(words) <= 6) or _NOT_NAME.search(name):
        return None
    lower = [w for w in words if w[:1].islower() and w.lower() not in _PARTICLES]
    if len(lower) > 1 or not re.match(r"[A-ZÀ-ÞĀ-ž\u0100-\u024F\u1E00-\u1EFF'’]", name):
        return None
    return name
