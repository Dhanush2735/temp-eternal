"""Step 37 (A2): which calendar a place wrote its dates in, and when.

Why this file exists
--------------------
`Calendars.java` does the arithmetic: give it a day number and a calendar and it will write the
date. What it cannot know is **which calendar the people there were using**, because that is a
fact about a place and a time and not about arithmetic. This is that fact, written by hand.

The mod has always had one date, a Gregorian one, in every year and every country. That is wrong
nearly everywhere for nearly all of history. Three examples of why, all from one city on one
morning:

    Hyderabad, 14 September 1948
        Fasli 1357 (the revenue calendar, the one on the government's papers)
        10 Dhu al-Qadah 1367 AH (what the Muslims of the city would say)
        29 Bhadrapada 2005 VS (what the Hindus of the city would say)

So a region carries a **list**, in the order a paper would use them, not one calendar. That is the
single most important thing in this file and the reason it is not a `lat -> calendar` map.

Rules for adding a row
----------------------
1. Every row carries the Wikipedia article it came from. No article, no row.
2. Boxes may overlap. The first matching row wins for the primary calendar, and every matching
   row contributes its calendars to the list, so a place can be given the several it used at once.
3. Say what you do not know. The pre-Columbian Americas, most of sub-Saharan Africa and the
   Pacific have calendars this register cannot write, and the row for them says so rather than
   quietly handing back a Gregorian date.
4. Regnal years are handled separately, from `world_rulers.json.gz`. Almost everywhere used them
   alongside whatever else is listed here; they are not repeated in every row.

Fields
------
name       what to call the region
lat0,lat1  the box, south to north
lon0,lon1  the box, west to east
frm, to    the years the row covers; `to` of None means "still"
calendars  the calendars in use, in the order a paper would use them
note       anything a reader needs to know
src        the Wikipedia article
"""

# --- the shape of a row -------------------------------------------------------------------

class R:
    __slots__ = ("name", "lat0", "lat1", "lon0", "lon1", "frm", "to", "calendars", "note", "src")

    def __init__(self, name, lat0, lat1, lon0, lon1, frm, calendars, to=None, note="", src=""):
        assert src, "every row needs a source: " + name
        assert -90 <= lat0 < lat1 <= 90, "bad latitude box: " + name
        assert -180 <= lon0 < lon1 <= 180, "bad longitude box: " + name
        assert frm >= -3000, "year out of range: " + name
        assert to is None or to >= frm, "ends before it starts: " + name
        assert calendars, "no calendars: " + name
        for c in calendars:
            assert c in ("gregorian", "julian", "hijri", "saka", "vikram", "fasli", "chinese"), \
                "unknown calendar %r in %s" % (c, name)
        self.name, self.frm, self.to = name, frm, to
        self.lat0, self.lat1, self.lon0, self.lon1 = lat0, lat1, lon0, lon1
        self.calendars, self.note, self.src = list(calendars), note, src

    def as_dict(self):
        d = {"name": self.name, "lat0": self.lat0, "lat1": self.lat1,
             "lon0": self.lon0, "lon1": self.lon1,
             "from": self.frm, "to": self.to, "calendars": self.calendars}
        if self.note:
            d["note"] = self.note
        d["source"] = self.src
        return d


# --- the table ---------------------------------------------------------------------------

GREG = "Gregorian calendar"
JUL = "Julian calendar"
HIJ = "Islamic calendar"
VIK = "Vikram Samvat"
SAK = "Saka era or Indian national calendar"
FAS = "Fasli era or Fasli calendar"
CHI = "Chinese calendar"
ADOPT = "Adoption of the Gregorian calendar"

REGIONS = [

    # ---------------------------------------------------------------- Europe: the Julian lag
    R("Catholic Europe — Italy, Spain, Portugal, France, the Low Countries, Poland",
      36.0, 60.0, -10.0, 25.0, -3000, ["julian"], to=1582,
      note="Julian until October 1582, when the Catholic countries dropped ten days. The "
           "Protestant and Orthodox ones did not, which is why a letter from London in 1700 and "
           "one from Rome in 1700 are dated eleven days apart.",
      src=GREG),
    R("Catholic Europe after the change", 36.0, 60.0, -10.0, 25.0, 1583, ["gregorian"],
      src=ADOPT),

    R("Britain and Ireland", 50.0, 59.0, -11.0, 2.0, -3000, ["julian"], to=1752,
      note="Julian until 2 September 1752, which was followed the next day by 14 September. "
           "The year had begun on 25 March until 1751, so a contemporary paper dates the first "
           "three months of 1700 to 1699 — the register does not try to reproduce that.",
      src=ADOPT),
    R("Britain and Ireland after the change", 50.0, 59.0, -11.0, 2.0, 1753, ["gregorian"],
      src=ADOPT),

    R("Scandinavia", 55.0, 71.0, 4.0, 32.0, -3000, ["julian"], to=1753,
      note="Sweden tried to change over gradually between 1700 and 1712, gave it up, and went "
           "back to Julian before finally changing in 1753; it had a 30 February in 1712.",
      src=ADOPT),
    R("Scandinavia after the change", 55.0, 71.0, 4.0, 32.0, 1754, ["gregorian"], src=ADOPT),

    R("Russia and the lands it ruled", 45.0, 78.0, 25.0, 180.0, -3000, ["julian"], to=1918,
      note="Julian until 31 January 1918, which was followed by 14 February. The October "
           "Revolution is so called because it fell in October by the Julian calendar; by the "
           "Gregorian one that the rest of Europe was keeping it was November.",
      src=ADOPT),
    R("Russia and the Soviet lands after the change", 45.0, 78.0, 25.0, 180.0, 1919,
      ["gregorian"], src=ADOPT),

    R("Greece and the Balkans", 34.0, 48.0, 15.0, 30.0, -3000, ["julian"], to=1923,
      note="Greece changed in 1923, the last country in Europe to do so; Serbia, Romania and "
           "Bulgaria between 1915 and 1919.",
      src=ADOPT),
    R("Greece and the Balkans after the change", 34.0, 48.0, 15.0, 30.0, 1924, ["gregorian"],
      src=ADOPT),

    # ---------------------------------------------------------------- the Islamic world
    R("The Arab world, Egypt and the Levant", 12.0, 40.0, -18.0, 45.0, 634, ["hijri"], to=1875,
      note="The Hijri year begins with the emigration to Medina in 622. Egypt's administration "
           "moved to Gregorian for civil purposes in 1875 while the religious calendar stayed "
           "Hijri, and the Coptic calendar — which is not modelled here — kept the farming year.",
      src=HIJ),
    R("Egypt after the administrative change", 22.0, 32.0, 24.0, 36.0, 1876,
      ["gregorian", "hijri"], src=ADOPT),
    R("The Arab world after the administrative changes", 12.0, 40.0, -18.0, 45.0, 1926,
      ["gregorian", "hijri"],
      note="Turkey changed in 1926 under Ataturk; most of the rest through the twentieth "
           "century. The Hijri year is still what a religious document carries everywhere.",
      src=ADOPT),

    R("The Tarim basin and Dzungaria", 36.0, 50.0, 73.0, 91.0, -100, ["chinese"], to=1911,
      note="Xinjiang: the same calendar as China proper, on the same era names.", src=CHI),
    R("The Tarim basin and Dzungaria after 1912", 36.0, 50.0, 73.0, 91.0, 1912,
      ["gregorian", "chinese"], src=ADOPT),

    R("Anatolia and Persia", 12.0, 42.0, 45.0, 75.0, 634, ["hijri"],
      note="Persia kept a solar Hijri calendar of its own, the Jalali, from 1079, which is "
           "nearer the Saka in shape than the lunar Hijri; it is not modelled separately, and "
           "this register gives the lunar Hijri date and says so.",
      src=HIJ),

    # ---------------------------------------------------------------- South Asia
    R("North India, the Gangetic plain and the Punjab", 20.0, 34.0, 66.0, 93.0, 57,
      ["vikram", "hijri"],
      note="Vikram Samvat begins in 57 BCE and is the calendar of most Hindu documents in the "
           "north; the Muslims of the same towns dated by the Hijri year. From the nineteenth "
           "century the government's papers carry a Christian date as well.",
      src=VIK),
    R("North India under the Raj", 20.0, 34.0, 66.0, 93.0, 1858,
      ["gregorian", "vikram", "hijri"],
      src=VIK),

    R("The Deccan and the south before the Fasli era", 8.0, 22.0, 72.0, 85.0, 57,
      ["saka", "vikram"], to=1555,
      note="The Saka era is the one the inscriptions of the Deccan are dated by from the first "
           "centuries CE — the Satavahanas, the Chalukyas, the Rashtrakutas, Vijayanagara — and "
           "Vikram Samvat is what the north kept. Without this row the Deccan would fall through "
           "to a Gregorian date for a thousand years it never used.",
      src=SAK),
    R("The Deccan and the south — Hyderabad, the Nizam's dominions, Madras", 8.0, 22.0, 72.0,
      85.0, 1556, ["fasli", "hijri", "saka"],
      note="The Fasli era is Akbar's, begun in 1556 = 963 AH, and it is the revenue calendar "
           "of the Deccan: the year number is the Hijri year counted by solar years, so adding "
           "590 gives the Gregorian year. The Deccan year runs from July to June. A Hyderabad "
           "paper of September 1948 is dated Fasli 1358, and also 10 Dhu al-Qadah 1367 AH, and "
           "also 29 Bhadrapada 2005 VS.",
      src=FAS),
    R("The Deccan and the south after the changeover", 8.0, 22.0, 72.0, 85.0, 1957,
      ["gregorian", "saka", "hijri"],
      note="Saka was made India's national calendar in 1957, alongside the Gregorian.",
      src=SAK),

    # ---------------------------------------------------------------- East Asia
    R("China", 29.0, 53.0, 85.0, 135.0, -1000, ["chinese"], to=1911,
      note="Lunisolar, and dated in the West by the reign title: the Kangxi era, the Qianlong "
           "era. Reign years come from world_rulers separately; the sexagenary year name and "
           "the animal are what this register gives.",
      src=CHI),
    R("China after 1912", 29.0, 53.0, 85.0, 135.0, 1912, ["gregorian", "chinese"],
      note="The Republic adopted the Gregorian calendar in 1912 and the era-name dating ended "
           "with the empire; the lunar year is still what a festival is dated by.",
      src=ADOPT),

    R("Japan", 30.0, 46.0, 128.0, 147.0, 600, ["chinese"], to=1872,
      note="Japan kept the Chinese lunisolar calendar with its own era names, the nengo, each "
           "beginning with an emperor's reign or a notable event.",
      src=CHI),
    R("Japan after 1873", 30.0, 46.0, 128.0, 147.0, 1873, ["gregorian", "chinese"],
      src=ADOPT),

    R("Korea", 33.0, 43.0, 125.0, 132.0, -100, ["chinese"], to=1895,
      note="The Chinese calendar with Korean era names; Gregorian from 1896.", src=CHI),
    R("Korea after 1896", 33.0, 43.0, 125.0, 132.0, 1896, ["gregorian"], src=ADOPT),

    R("Vietnam and the lands of the Annamese court", 8.0, 24.0, 102.0, 110.0, -100, ["chinese"],
      to=1886, note="Chinese-derived, with Vietnamese era names. The French brought the "
                    "Gregorian calendar from 1887.", src=CHI),

    R("South-East Asia — Siam, Burma, Java, Cambodia", -11.0, 24.0, 92.0, 142.0, 600,
      ["chinese", "hijri"],
      note="Buddhist era years in Siam and Burma (543 years ahead of the Christian year) and "
           "the Saka era in Java until 1633, when Sultan Agung took over a lunar Hijri "
           "reckoning. The Buddhist era is not modelled here; this register gives the Chinese "
           "and Hijri years and a note.",
      src=CHI),

    # ---------------------------------------------------------------- the rest
    R("The Americas before contact", -56.0, 72.0, -170.0, -34.0, -3000, ["gregorian"], to=1491,
      note="**Not modelled.** The Maya, the Aztec and the peoples of the Andes kept calendars "
           "of their own — the Long Count, the tonalpohualli — and this register has no "
           "arithmetic for any of them. The row hands back a Gregorian date because the mod has "
           "to print something, and the note says plainly that it is not the date anyone there "
           "would have written.",
      src=CHI),
    R("The Americas after contact", -56.0, 72.0, -170.0, -34.0, 1492, ["gregorian"],
      note="The Spanish and Portuguese brought the Julian calendar and then the Gregorian; "
           "Britain's colonies kept Julian until 1752 like Britain did.",
      src=ADOPT),

    R("Sub-Saharan Africa", -35.0, 15.0, -18.0, 52.0, -3000, ["gregorian"],
      note="**Not modelled.** Ethiopia keeps a calendar of its own, seven or eight years behind "
           "the Gregorian, with thirteen months; the rest of the region is a patchwork of "
           "lunar and seasonal reckonings this register cannot write. The row hands back a "
           "Gregorian date and says so. The Sahel north of about 15N — Timbuktu, Kano, the "
           "Hausa cities — is in the Islamic-world row above and does get a Hijri date, "
           "because that is what those cities wrote.",
      src=ADOPT),

    R("The Pacific and Australasia", -50.0, 0.0, 110.0, 180.0, -3000, ["gregorian"],
      note="**Not modelled.** Polynesian and Aboriginal reckonings are seasonal and local. The "
           "row hands back a Gregorian date and says so.",
      src=ADOPT),
]
