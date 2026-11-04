import io
#!/usr/bin/env python3
"""Step 6.3: famous people from the Births and Deaths sections of Wikipedia's year pages.

Every year page from 3000 BC to now (already cached from the 2026-10-01 dump) lists people born
and people who died that year: "* [[January 25]] – [[Robert Burns]], Scottish poet (d. 1796)".
Each person gets a birth year, a death year, a few words of description and a home land:

  1. a place linked in the line itself ("[[Florence|Florentine]] painter"), else
  2. the land in a title ("Duke of Burgundy", "King of France"), else
  3. the nationality word in the line or in the article's short description ("Scottish poet").

The land is placed like step-5 regional news: the state that ruled that land in the person's
active years (build_regional.Places), so a "German" of 1600 sits in the Holy Roman Empire.

Writes:
  * history/famous_people.json.gz, read by the mod's FamousPeople (not a gazetteer pack):
    rows [name, description, birth, death, state, lat, lon, radiusKm]; state is the Wikidata id
    of the Cliopatria state of the person's home land (what RulerRegister answers with); birth,
    death or state may be null.
  * ~/.cache/wpdump/people_lines.json.gz: every parsed person (also the unplaced ones), so
    build_polity_facts.py can end a reign at the ruler's recorded death.

    python3 build_people.py --dry
    python3 build_people.py
"""
import collections, gzip, json, os, re, sys

sys.path.insert(0, "/home/user/worldfill")
sys.path.insert(0, "/home/user/harvest")
import modpack as M  # noqa: E402
import wpdump as W  # noqa: E402
import build_regional as BR  # noqa: E402
from wikitext_clean import clean_text  # noqa: E402
import build_polity_facts as PF  # noqa: E402

PAGES = os.path.expanduser("~/.cache/wpdump/yearpages.jsonl.gz")
PAGES_JSON = "/home/user/harvest/events_v2_raw.jsonl.pages.json"
LINES_CACHE = os.path.expanduser("~/.cache/wpdump/people_lines.json.gz")
OUT_FILE = "famous_people.json.gz"
REPORT = "/home/user/worldfill/people_report.json"

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE_PREFIX = re.compile(r"^(?:\[\[)?(?:" + MONTHS + r")(?:\s+\d{1,2})?(?:\]\])?(?:\s*[–-]\s*(?:\[\[)?(?:(?:"
                         + MONTHS + r")\s+)?\d{1,2}(?:\]\])?)?\s*(?:[–—-]|&ndash;|{{snd}}|{{ndash}})?\s*")
SOFT_PREFIX = re.compile(r"^(?:''[^']{1,40}''|c\.|ca\.|circa|probabl[ey]|approximate date|date unknown|"
                         r"possibl[ey]|traditional date|unknown date)\s*(?:[–—-]|&ndash;)?\s*", re.I)
OTHER_YEAR = re.compile(r"\((?:[^()]*?;\s*)?(?:b|d|born|died)\.?\s*(?:c\.\s*|ca\.\s*|circa\s*|after\s*|before\s*)?"
                        r"(?:\[\[)?(\d{1,4})(?:\]\])?\s*(BCE|BC|AD|CE)?", re.I)
OF_TITLE = re.compile(r"\b(?:King|Queen|Emperor|Empress|Duke|Duchess|Prince|Princess|Count|Countess|Sultan|"
                      r"Shah|Archbishop|Bishop|Patriarch|Doge|Earl|Margrave|Margravine|Elector|Electress|"
                      r"Grand Duke|Grand Prince|Khan|Raja|Maharaja|Nawab|Nizam|Governor|President|"
                      r"Prime Minister|Chancellor|Mayor|Caliph|Emir|Pharaoh|Tsar|Lord|Lady|Regent)"
                      r"\s+of\s+(?:the\s+)?([A-Z][\w'’\-]*(?:\s+(?:of|the|and|de|del|la|von|al)?\s*[A-Z][\w'’\-]*)*)")
# Nationality word -> the Wikipedia article for that land (placed through the state that ruled it).
DEMONYM = {
    "English": "England", "Scottish": "Scotland", "Scots": "Scotland", "Welsh": "Wales", "Irish": "Ireland",
    "British": "United Kingdom", "French": "France", "German": "Germany", "Italian": "Italy",
    "Spanish": "Spain", "Portuguese": "Portugal", "Dutch": "Netherlands", "Flemish": "Flanders",
    "Belgian": "Belgium", "Swiss": "Switzerland", "Austrian": "Austria", "Hungarian": "Hungary",
    "Polish": "Poland", "Czech": "Czech Republic", "Bohemian": "Bohemia", "Slovak": "Slovakia",
    "Russian": "Russia", "Ukrainian": "Ukraine", "Belarusian": "Belarus", "Lithuanian": "Lithuania",
    "Latvian": "Latvia", "Estonian": "Estonia", "Finnish": "Finland", "Swedish": "Sweden",
    "Norwegian": "Norway", "Danish": "Denmark", "Icelandic": "Iceland", "Greek": "Greece",
    "Roman": "Roman Empire", "Byzantine": "Byzantine Empire", "Ottoman": "Ottoman Empire",
    "Turkish": "Turkey", "Persian": "Iran", "Iranian": "Iran", "Arab": "Arabian Peninsula",
    "Egyptian": "Egypt", "Moroccan": "Morocco", "Algerian": "Algeria", "Tunisian": "Tunisia",
    "Libyan": "Libya", "Ethiopian": "Ethiopia", "Nigerian": "Nigeria", "Ghanaian": "Ghana",
    "Kenyan": "Kenya", "South African": "South Africa", "Indian": "India", "Pakistani": "Pakistan",
    "Bengali": "Bengal", "Sri Lankan": "Sri Lanka", "Nepalese": "Nepal", "Nepali": "Nepal",
    "Chinese": "China", "Japanese": "Japan", "Korean": "Korea", "Vietnamese": "Vietnam", "Thai": "Thailand",
    "Burmese": "Myanmar", "Cambodian": "Cambodia", "Khmer": "Cambodia", "Indonesian": "Indonesia",
    "Filipino": "Philippines", "Malaysian": "Malaysia", "Mongol": "Mongolia", "Mongolian": "Mongolia",
    "Tibetan": "Tibet", "American": "United States", "Canadian": "Canada", "Mexican": "Mexico",
    "Brazilian": "Brazil", "Argentine": "Argentina", "Argentinian": "Argentina", "Chilean": "Chile",
    "Peruvian": "Peru", "Colombian": "Colombia", "Venezuelan": "Venezuela", "Cuban": "Cuba",
    "Australian": "Australia", "New Zealand": "New Zealand", "Israeli": "Israel", "Syrian": "Syria",
    "Lebanese": "Lebanon", "Iraqi": "Iraq", "Saudi": "Saudi Arabia", "Afghan": "Afghanistan",
    "Armenian": "Armenia", "Georgian": "Georgia (country)", "Azerbaijani": "Azerbaijan",
    "Kazakh": "Kazakhstan", "Uzbek": "Uzbekistan", "Serbian": "Serbia", "Croatian": "Croatia",
    "Bosnian": "Bosnia and Herzegovina", "Bulgarian": "Bulgaria", "Romanian": "Romania",
    "Moldavian": "Moldavia", "Wallachian": "Wallachia", "Albanian": "Albania", "Athenian": "Athens",
    "Spartan": "Sparta", "Carthaginian": "Carthage", "Assyrian": "Assyria", "Babylonian": "Babylonia",
    "Sumerian": "Sumer", "Mughal": "Mughal Empire", "Maratha": "Maratha Confederacy", "Tamil": "Tamil Nadu",
    "Telugu": "Andhra Pradesh", "Kannada": "Karnataka", "Marathi": "Maharashtra", "Gujarati": "Gujarat",
    "Punjabi": "Punjab", "Sindhi": "Sindh", "Kashmiri": "Kashmir", "Malayali": "Kerala", "Odia": "Odisha",
    "Assamese": "Assam", "Hyderabadi": "Hyderabad", "Venetian": "Republic of Venice",
    "Genoese": "Republic of Genoa", "Florentine": "Florence", "Milanese": "Milan",
    "Neapolitan": "Kingdom of Naples", "Sicilian": "Sicily", "Castilian": "Crown of Castile",
    "Aragonese": "Crown of Aragon", "Catalan": "Catalonia", "Navarrese": "Kingdom of Navarre",
    "Prussian": "Prussia", "Bavarian": "Bavaria", "Saxon": "Saxony", "Frankish": "Francia",
    "Visigothic": "Visigothic Kingdom", "Anglo-Saxon": "England", "Norman": "Normandy",
    "Breton": "Brittany", "Burgundian": "Burgundy", "Hessian": "Hesse", "Silesian": "Silesia",
    "Moravian": "Moravia", "Lombard": "Lombardy", "Andalusian": "Al-Andalus", "Moorish": "Al-Andalus",
    "Abbasid": "Abbasid Caliphate", "Umayyad": "Umayyad Caliphate", "Fatimid": "Fatimid Caliphate",
    "Seljuk": "Seljuk Empire", "Safavid": "Safavid Iran", "Timurid": "Timurid Empire", "Aztec": "Aztec Empire",
    "Inca": "Inca Empire", "Maya": "Maya civilization", "Mayan": "Maya civilization",
    "Joseon": "Joseon", "Goryeo": "Goryeo", "Silla": "Silla", "Gupta": "Gupta Empire",
    "Chola": "Chola dynasty", "Hawaiian": "Hawaii", "Puerto Rican": "Puerto Rico", "Jamaican": "Jamaica",
    "Haitian": "Haiti", "Uruguayan": "Uruguay", "Paraguayan": "Paraguay", "Bolivian": "Bolivia",
    "Ecuadorian": "Ecuador", "Guatemalan": "Guatemala", "Honduran": "Honduras", "Salvadoran": "El Salvador",
    "Nicaraguan": "Nicaragua", "Costa Rican": "Costa Rica", "Panamanian": "Panama", "Sudanese": "Sudan",
    "Somali": "Somalia", "Tanzanian": "Tanzania", "Ugandan": "Uganda", "Zimbabwean": "Zimbabwe",
    "Zambian": "Zambia", "Congolese": "Democratic Republic of the Congo", "Senegalese": "Senegal",
    "Malian": "Mali", "Cameroonian": "Cameroon", "Ivorian": "Ivory Coast", "Malagasy": "Madagascar",
    "Angolan": "Angola", "Mozambican": "Mozambique", "Namibian": "Namibia", "Rwandan": "Rwanda",
    "Burundian": "Burundi", "Eritrean": "Eritrea", "Jordanian": "Jordan", "Palestinian": "Palestine (region)",
    "Kuwaiti": "Kuwait", "Emirati": "United Arab Emirates", "Qatari": "Qatar", "Bahraini": "Bahrain",
    "Omani": "Oman", "Yemeni": "Yemen", "Cypriot": "Cyprus", "Maltese": "Malta", "Luxembourgish": "Luxembourg",
    "Slovene": "Slovenia", "Slovenian": "Slovenia", "Montenegrin": "Montenegro", "Tajik": "Tajikistan",
    "Turkmen": "Turkmenistan", "Kyrgyz": "Kyrgyzstan", "Bangladeshi": "Bangladesh", "Bhutanese": "Bhutan",
    "Laotian": "Laos", "Lao": "Laos", "Singaporean": "Singapore", "Taiwanese": "Taiwan", "Fijian": "Fiji",
    "Samoan": "Samoa", "Tongan": "Tonga", "Gaulish": "Gaul", "Gallic": "Gaul", "Phoenician": "Phoenicia",
    "Judean": "Judea", "Parthian": "Parthian Empire", "Sasanian": "Sasanian Empire", "Sassanid": "Sasanian Empire",
    "Achaemenid": "Achaemenid Empire", "Kushan": "Kushan Empire", "Javanese": "Java", "Balinese": "Bali",
    "Siamese": "Thailand", "Ryukyuan": "Ryukyu Kingdom", "Manchu": "Manchuria", "Uyghur": "Xinjiang",
    "Kurdish": "Kurdistan", "Berber": "Maghreb", "Nubian": "Nubia", "Zulu": "Zulu Kingdom",
    "Macedonian": "Macedonia (region)", "Thracian": "Thrace", "Illyrian": "Illyria", "Numidian": "Numidia",
    "Etruscan": "Etruria", "Hittite": "Hittites", "Median": "Medes", "Han": "Han dynasty", "Tang": "Tang dynasty",
    "Song": "Song dynasty", "Ming": "Ming dynasty", "Qing": "Qing dynasty", "Yuan": "Yuan dynasty",
    "Sui": "Sui dynasty", "Jin": "Jin dynasty (1115–1234)", "Liao": "Liao dynasty", "Khitan": "Liao dynasty",
    "Jurchen": "Jin dynasty (1115–1234)", "Holy Roman": "Holy Roman Empire", "Frisian": "Frisia",
    "Galician": "Galicia (Spain)", "Asturian": "Asturias", "Leonese": "Kingdom of León", "Savoyard": "Savoy",
    "Piedmontese": "Piedmont", "Tuscan": "Tuscany", "Sardinian": "Sardinia", "Corsican": "Corsica",
    "Provençal": "Provence", "Occitan": "Occitania", "Gascon": "Gascony", "Basque": "Basque Country (greater region)",
    "Cornish": "Cornwall", "Manx": "Isle of Man", "Northumbrian": "Northumbria", "Mercian": "Mercia",
    "Wessex": "Wessex", "Kievan": "Kievan Rus'", "Muscovite": "Grand Duchy of Moscow", "Novgorodian": "Novgorod Republic",
    "Cossack": "Zaporozhian Host", "Tatar": "Tatarstan", "Crimean": "Crimea", "Circassian": "Circassia",
    "Chechen": "Chechnya", "Dagestani": "Dagestan", "Ossetian": "Ossetia", "Abkhazian": "Abkhazia",
}
SKIP_FIRST = {"Roman Catholic", "Dominican", "Franciscan", "Jesuit", "Benedictine", "Carmelite",
              "Augustinian", "Cistercian", "Anglican", "Lutheran", "Calvinist", "Jewish", "Christian",
              "Muslim", "Buddhist", "Hindu", "Sikh", "Islamic", "Catholic", "Protestant", "Orthodox", "Greek Orthodox"}


def page_year():
    pages = json.load(open(PAGES_JSON, encoding="utf-8"))
    return {t: ys[0] for t, ys in pages.items() if len(ys) == 1}


def sections(text, name):
    m = re.search(r"^==\s*" + name + r"\s*==\s*$", text, re.M)
    if not m:
        return ""
    n = re.search(r"^==[^=].*?==\s*$", text[m.end():], re.M)
    return text[m.end(): m.end() + n.start()] if n else text[m.end():]


def era_year(num, era, page_y, kind):
    y = int(num)
    if era:
        return -y if era.upper() in ("BC", "BCE") else y
    if page_y < 0:
        # "(d. 479)" on a BC page: BC if that makes a plausible life, else AD.
        bc = -y
        if kind == "births" and page_y < bc <= page_y + 110:
            return bc
        if kind == "deaths" and page_y - 110 <= bc < page_y:
            return bc
        if kind == "births" and y > 0 and y - page_y <= 110:
            return y
    return y


def parse_pages():
    years = page_year()
    out = []
    st = collections.Counter()
    for line in gzip.open(PAGES, "rt", encoding="utf-8"):
        d = json.loads(line)
        y = years.get(d["title"])
        if y is None:
            continue
        for kind, sec in (("births", "Births"), ("deaths", "Deaths")):
            body = sections(d["text"], sec)
            for raw in body.split("\n"):
                if not raw.startswith("*"):
                    continue
                s = raw.lstrip("*").strip()
                s = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", s, flags=re.S)
                s = DATE_PREFIX.sub("", s, count=1)
                s = SOFT_PREFIX.sub("", s, count=1)
                st[f"{kind}_lines"] += 1
                m = BR.H.LINK_RE.match(s)
                if not m:
                    continue
                target = m.group(1).strip()
                alias = (m.group(2) or "").strip()
                if BR.H.SKIP_LINK.match("[[" + target) or BR.H.DATE_LINK.match(target):
                    continue
                rest = s[m.end():]
                other = None
                om = OTHER_YEAR.search(rest)
                if om:
                    other = era_year(om.group(1), om.group(2), y, kind)
                desc_raw = re.sub(r"\((?:[^()]*?;\s*)?(?:b|d|born|died)\.?[^()]*\)", "", rest)
                desc_raw = desc_raw.strip(" ,;–-")
                desc = re.sub(r"\s+", " ", clean_text(desc_raw)).strip(" ,;.–-")
                desc = re.sub(r"\([^()]*\)", "", desc).strip(" ,;.")
                name = alias or re.sub(r"\s*\([^()]*\)$", "", target)
                name = re.sub(r"'{2,}", "", name).strip()
                if not name or len(name) > 60:
                    continue
                birth, death = (y, other) if kind == "births" else (other, y)
                if birth is not None and death is not None and not (0 <= death - birth <= 120):
                    if kind == "births":
                        death = None
                    else:
                        birth = None
                st[f"{kind}_people"] += 1
                out.append({"target": target, "name": name, "desc": desc[:80], "desc_raw": desc_raw[:300],
                            "birth": birth, "death": death, "page": y, "kind": kind})
    return out, st


def merge(rows, wiki):
    """One person per article (redirects resolved): birth from the births line, death from deaths."""
    people = {}
    for r in rows:
        hit = wiki.lookup(r["target"])
        key = hit[0] if hit else r["target"]
        p = people.get(key)
        if p is None:
            p = people[key] = {"article": key, "page_id": hit[1] if hit else None, "name": r["name"],
                               "desc": r["desc"], "desc_raw": r["desc_raw"], "birth": None, "death": None}
        if r["kind"] == "births":
            p["birth"] = r["birth"]
            if p["death"] is None and r["death"] is not None:
                p["death"] = r["death"]
        else:
            p["death"] = r["death"]
            if p["birth"] is None and r["birth"] is not None:
                p["birth"] = r["birth"]
            p["name"] = r["name"] or p["name"]
        if len(r["desc"]) > len(p["desc"]):
            p["desc"], p["desc_raw"] = r["desc"], r["desc_raw"]
    return list(people.values())


def shorten(desc, limit=60):
    """'Empress consort of the Maratha Empire as the first wife of ...' -> the first clause."""
    d = re.sub(r"\s+", " ", desc).strip(" ,;.")
    if len(d) <= limit:
        return d
    for sep in (", ", "; ", " as ", " who ", " and ", " of the "):
        i = d.find(sep, 20)
        if 0 < i <= limit:
            return d[:i].strip(" ,;.")
    cut = d[:limit].rsplit(" ", 1)[0]
    return cut.strip(" ,;.")


def active_year(p):
    b, d = p["birth"], p["death"]
    if d is not None and b is not None:
        return min(d, b + 40)
    if d is not None:
        return d - 10
    return b + 35


def state_of(c, target, places, reg, name_qid, year):
    """The Wikidata id of the state a placement belongs to, and the land's own point.

    The land's own coordinates come first (Egypt's own centre in 670 BC, not the centre of the
    Assyrian empire that ruled it), asked of the same register the mod uses; failing that, the
    state named by the placement itself.
    """
    _rank, lat, lon, rad, how, _title = c
    r = places.resolve(target) if target else None
    g = r[1]["geo"] if r and r[1] else None
    if g and how.startswith(("state:", "country")):
        lat, lon = g["lat"], g["lon"]
    pol = reg.at(lat, lon, year)
    q = pol[1] if pol else None
    if not q and ":" in how:
        q = name_qid.get(how.split(":", 1)[1])
    return q, lat, lon, rad


def place(p, places, wiki, reg=None, name_qid=None):
    """((rank, lat, lon, radius, how, title), via, target) or (None, None, None)."""
    year = active_year(p)
    # 1. a place linked in the line
    for target, alias in BR.links(p["desc_raw"]):
        c = places.candidate(target, alias, year)
        if c:
            return c, "link", target
    text = p["desc"]
    # 2. the land in a title
    m = OF_TITLE.search(text)
    if m:
        c = places.candidate(m.group(1).strip(), None, year)
        if c:
            return c, "title", m.group(1).strip()
    # 3. nationality word (line, then the article's short description)
    sd = ""
    if p.get("page_id"):
        try:
            sd = wiki.info(p["page_id"]).get("shortdesc") or ""
        except Exception:
            sd = ""
    for src in (text, sd):
        s = re.sub(r"^(?:an?|the)\s+", "", src.strip(), flags=re.I)
        s = re.sub(r"^(?:Ancient|Medieval|Early|Late|Classical|Imperial)\s+", "", s)
        words = re.findall(r"[A-ZÀ-Þ][\w'’]+(?:-[A-Za-z]+)?", s[:60])
        if not words:
            continue
        first2 = " ".join(s.split()[:2]).replace("-born", "")
        for cand in (first2, re.sub(r"-born$|-American$", "", words[0]).split("-")[0]):
            if cand in SKIP_FIRST:
                break
            t = DEMONYM.get(cand)
            if t:
                c = places.candidate(t, None, year)
                if c:
                    return c, "demonym", t
                break
    return None, None, None


def main(dry=False):
    rows, st = parse_pages()
    BR.log(f"parsed {len(rows)} birth/death lines with a linked person")
    wiki = W.Wiki()
    people = merge(rows, wiki)
    BR.log(f"{len(people)} people")
    with open(LINES_CACHE, "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as f:
        json.dump([{"name": p["name"], "article": p["article"], "birth": p["birth"], "death": p["death"],
                    "desc": p["desc"]} for p in people], f, ensure_ascii=False)
    hyde = BR.Hyde()
    pol = BR.Polities(hyde)
    places = BR.Places(wiki, pol)
    reg = PF.Register()
    name_qid = {}
    for n, q in reg.pols:
        if q:
            name_qid.setdefault(n, q)
    out, how = [], collections.Counter()
    for i, p in enumerate(people):
        if i % 20000 == 0:
            BR.log(f"  placing {i}/{len(people)}")
        c, via, target = place(p, places, wiki)
        if not c:
            how["unplaced"] += 1
            continue
        q, lat, lon, rad = state_of(c, target, places, reg, name_qid, active_year(p))
        rad = int(min(800, max(40, rad)))
        how[via] += 1
        how["with_state" if q else "no_state"] += 1
        desc = shorten(p["desc"] or "")
        out.append([p["name"], desc, p["birth"], p["death"], q, round(lat, 2), round(lon, 2), rad])
    out.sort(key=lambda r: (r[3] if r[3] is not None else (r[2] or 0) + 60, r[0]))
    rep = {"lines": dict(st), "people": len(people), "placed": len(out), "placed_by": dict(how),
           "with_birth_and_death": sum(1 for r in out if r[2] is not None and r[3] is not None),
           "states_with_people": len({r[4] for r in out if r[4]}),
           "by_century_of_death": dict(sorted(collections.Counter(
               (r[3] // 100 * 100 if r[3] is not None else None) for r in out if r[3] is not None).items())),
           "examples": [f"{r[0]} | {r[1]} | {r[2]}–{r[3]} | {r[4]} | {r[5]},{r[6]} r{r[7]}" for r in out[::max(1, len(out) // 15)]][:15]}
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    if dry:
        return
    doc = {"format": 1,
           "source": ("worldfill/build_people.py: Births and Deaths sections of the Wikipedia year pages "
                      "(enwiki dump 2026-10-01, CC BY-SA 4.0); home land placed through the Cliopatria "
                      "state that ruled it in the person's active years"),
           "note": ("rows are [name, description, birth, death, state, lat, lon, radiusKm]: state is the "
                    "Wikidata id of the Cliopatria state of the person's home land in their active years "
                    "(the id RulerRegister answers with), or null; birth or death may be null"),
           "people": out}
    path = f"{M.HISTORY}/{OUT_FILE}"
    with open(path + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    json.load(gzip.open(path + ".tmp", "rt", encoding="utf-8"))
    os.replace(path + ".tmp", path)
    rep["bytes"] = os.path.getsize(path)
    json.dump(rep, open(REPORT, "w"), ensure_ascii=False, indent=1)
    print(f"wrote {path} ({rep['bytes'] / 1e6:.2f} MB)")


if __name__ == "__main__":
    main(dry="--dry" in sys.argv)
