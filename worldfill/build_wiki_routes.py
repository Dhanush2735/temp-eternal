#!/usr/bin/env python3
"""Towns of the great trade routes, from their Wikipedia articles (used by build_trade_routes.py).

For each route article, the towns are the settlements linked in its route sections (sections about
legacy, modern revival, culture or references are skipped): a link counts when Wikipedia's own
article for it has coordinates and its short description or geo type says city, town, port, oasis
or the like. Towns more than 1,500 km from every other town of the route are dropped as strays.

Years come from each article's lead ("active from the second century BCE until the mid-15th century"
-> -150..1450). Routes whose lead gives no dates (Amber Road, Uttarapatha, Dakshinapatha, Indian Ocean
trade) and very broad ones (Spice trade) are left out rather than guessed; the Appian Way is a road and
comes from Itiner-e.
"""
import collections, math, re, sys

sys.path.insert(0, "/home/user/worldfill")
import wpdump as W  # noqa: E402

ROUTES = [  # article, start, end, kind, the lead's words for the years
    ("Silk Road", -150, 1450, "land", "active from the second century BCE until the mid-15th century"),
    ("Maritime Silk Road", -150, 1450, "sea", "began by the 2nd century BCE and flourished until the 15th century CE"),
    ("Incense trade route", -300, 200, "land", "flourished between roughly the 3rd century BC and the 2nd century AD"),
    ("Trans-Saharan trade", 700, 1620, "land", "the peak of trade extended from the 8th century until the early 17th century"),
    ("Grand Trunk Road", -300, 2026, "land", "built along an ancient route in the 3rd century BCE; still in use"),
    ("Royal Road", -500, -330, "land", "rebuilt for trade in the 5th century BCE by the Achaemenid Empire (to its fall, 330 BC)"),
    ("Hanseatic League", 1180, 1669, "league", "from the late 12th century; its last diet met in 1669"),
    ("Via Maris", -600, 1517, "land", "in use from the 6th century BC until the end of the Mamluk Sultanate"),
    ("King's Highway (ancient)", 640, 1600, "land", "from the 7th century AD until the 16th century the pilgrimage road to Mecca"),
    ("Tea Horse Road", 618, 1950, "land", "from the Tang dynasty to the mid-20th century"),
]
SKIP = re.compile(r"(?i)legacy|modern|revival|contemporary|popular culture|in culture|literature|see also|references|notes|"
                  r"further reading|external links|bibliography|gallery|today|21st|belt and road|influence|tourism|"
                  r"film|music|exhibition|sources|citations|historiography|etymology|name")
TOWN_SD = re.compile(r"(?i)\b(city|town|village|capital|port|oasis|settlement|ancient city|archaeological site|"
                     r"caravanserai|trading post|fortress|fort|municipality|commune|seaport|harbour|harbor|metropolis)\b")
NOT_TOWN = re.compile(r"(?i)\b(country|region|province|empire|kingdom|dynasty|river|sea|ocean|desert|mountain|"
                      r"range|island|lake|state of|continent|people|language)\b")
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


def km(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    d = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(b[1] - a[1]) / 2) ** 2
    return 12742 * math.asin(min(1, math.sqrt(d)))


def sections(text):
    parts = re.split(r"\n(==+)\s*([^=\n]+?)\s*\1\s*\n", text)
    yield "lead", parts[0]
    for i in range(1, len(parts) - 2, 3):
        yield parts[i + 1], parts[i + 2]


def routes():
    wiki = W.Wiki()
    got = wiki.texts([r[0] for r in ROUTES])
    out, st = [], collections.Counter()
    for title, start, end, kind, why in ROUTES:
        if title not in got:
            st["missing_article"] += 1
            continue
        text = got[title][1]
        seen, towns = set(), []
        skip_level = None
        for head, body in sections(text):
            if SKIP.search(head):
                continue
            for m in LINK.finditer(body):
                target = m.group(1).strip()
                if target in seen or target.startswith(("File:", "Image:", "Category:", "List of")):
                    continue
                seen.add(target)
                hit = wiki.lookup(target)
                if not hit:
                    continue
                info = wiki.info(hit[1])
                g = info.get("geo")
                sd = info.get("shortdesc") or ""
                if not g or info.get("disambig"):
                    continue
                if g.get("type") in ("country", "adm1st", "state") or re.search(r"(?i)^(country|sovereign state)\b", sd):
                    continue
                is_town = g.get("type") == "city" or (TOWN_SD.search(sd) and not NOT_TOWN.search(sd.split(",")[0]))
                if not is_town:
                    continue
                towns.append([re.sub(r"\s*\([^()]*\)$", "", hit[0]).split(",")[0], round(g["lat"], 3), round(g["lon"], 3)])
        kept = [t for t in towns if any(km(t[1:], u[1:]) <= 1500 for u in towns if u is not t)]
        st["towns_found"] += len(towns)
        st["strays_dropped"] += len(towns) - len(kept)
        out.append({"name": title.replace(" (ancient)", ""), "start": start, "end": end, "kind": kind,
                    "years_from": why, "towns": kept})
        st[f"route:{title}"] = len(kept)
    return out, dict(st)


if __name__ == "__main__":
    import json
    r, s = routes()
    print(json.dumps(s, indent=1))
    for x in r:
        print(x["name"], len(x["towns"]), [t[0] for t in x["towns"][:14]])
