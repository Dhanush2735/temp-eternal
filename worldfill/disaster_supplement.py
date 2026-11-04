"""Step 36 (B27): the great disasters `events_hazards.json.gz` does not carry, written by hand.

Why this file exists
--------------------
`build_hazards.py` produced 26,997 hazards, which sounds like a lot, and for a question like
"did anything happen in this region in this century" it is. It is not a roll of the great
disasters. Of thirty famous ones checked against it, fourteen are absent outright — Vesuvius in
AD 79, Krakatau in 1883, San Francisco in 1906, Messina in 1908, Tangshan in 1976, Tohoku in
2011, Haiti in 2010, the Yellow River flood of 1887, the North Sea flood of 1953, the Plague of
Justinian, the Antonine Plague, the Spanish flu, the Heimaey eruption, Damghan in 856 — and
another six are matched only by a loose substring to the wrong event. A player who walks into
Pompeii in AD 80 and asks what happened here has to be told about the mountain.

So this is a hand table, like `water_changes_table.py` in step 35 and the era tables in step 34:
the places a bulk scrape misses, written down one at a time. Every row is sourced to the
Wikipedia article it came from. It is deliberately short — about sixty events, not six hundred —
because it is hand-checked, and a hand-checked row is worth more than ten scraped ones.

Rules for adding a row
----------------------
1. The event must be absent from `events_hazards.json.gz`, or present with a year or radius that
   is plainly wrong (New Madrid 1811-12 is in the pack filed under AD 7; Lisbon 1755 is in it with
   a 50 km radius that does not reach Lisbon).
2. It must be big enough that a world without it is a wrong world: it destroyed a city, emptied a
   region, or killed more than a hundred thousand people.
3. Every row carries the Wikipedia article it came from. No article, no row.
4. Coverage over volume: every inhabited continent, and every millennium from 2000 BCE to now.

Fields
------
name      what to call it
year      the year it began; negative for BCE
end       the year it ended, or None for a single year
lat, lon  where
kind      one of the kinds in Disasters.Kind: earthquake volcano tsunami flood plague epidemic
          pandemic famine fire
radius    how far its effects reached, in km. The handful of events that covered a
          continent or the world get a radius big enough to cover it and no more:
          the Black Death at 5,500 km from the Crimea reaches London and Delhi and
          West Africa and not the Americas, which is right; the Spanish flu at
          15,000 km reaches everywhere, which is also right.
dead      how many it killed, or None where the count is unknown
mag       magnitude for an earthquake, VEI for a volcano, or None
sev       an explicit 0-1 severity, for the events where neither the magnitude nor the dead give
          it: the Great Fire of London killed six people and burned thirteen thousand houses
note      anything a reader needs to know
src       the Wikipedia article
"""

# --- the shape of a row -------------------------------------------------------------------

class E:
    __slots__ = ("name", "year", "end", "lat", "lon", "kind", "radius",
                 "dead", "mag", "sev", "global_", "note", "src")

    def __init__(self, name, year, lat, lon, kind, radius, end=None, dead=None,
                 mag=None, sev=None, note="", src=""):
        assert src, "every row needs a source: " + name
        assert -3000 <= year <= 2026, "year out of range: " + name
        assert -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0, "bad point: " + name
        assert kind in ("earthquake", "volcano", "tsunami", "flood", "plague",
                        "epidemic", "pandemic", "famine", "fire"), "bad kind: " + name
        assert radius >= 0, "bad radius: " + name
        if end is not None:
            assert end >= year, "ends before it starts: " + name
        self.name, self.year, self.end = name, year, end
        self.lat, self.lon, self.kind, self.radius = lat, lon, kind, radius
        self.dead, self.mag, self.sev = dead, mag, sev
        self.note, self.src = note, src

    def as_dict(self):
        d = {"name": self.name, "start": self.year,
             "end": self.year if self.end is None else self.end,
             "lat": self.lat, "lon": self.lon, "kind": self.kind, "radiusKm": self.radius}
        if self.dead is not None:
            d["dead"] = self.dead
        if self.mag is not None:
            d["mag"] = self.mag
        if self.sev is not None:
            d["sev"] = self.sev
        if self.note:
            d["note"] = self.note
        d["source"] = self.src
        d["confidence"] = "hand"
        return d


# --- the table ---------------------------------------------------------------------------

EVENTS = [

    # ---------------------------------------------------------------- the ancient world
    E("Minoan eruption of Santorini", -1600, 36.40, 25.40, "volcano", 400, mag=7,
      note="Buried the town at Akrotiri under tens of metres of ash and sent a tsunami across "
           "the eastern Mediterranean; the date is still argued over, 1627 to 1500 BCE.",
      src="Minoan eruption"),

    E("Eruption of Vesuvius, Pompeii and Herculaneum", 79, 40.82, 14.37, "volcano", 60,
      dead=1500, mag=5,
      note="The reason there is a Pompeii to walk through. The pack has Vesuvius erupting in "
           "787 and 860 but not in 79.",
      src="Eruption of Mount Vesuvius in 79 AD"),

    E("464 BC Sparta earthquake", -464, 37.07, 22.43, "earthquake", 100, dead=20000,
      note="Brought the Spartan walls down and started the helot revolt; the twenty thousand "
           "dead are from ancient sources and are certainly too high, but the walls came down.",
      src="464 BC Sparta earthquake"),

    E("373 BC Helike earthquake and tsunami", -373, 38.25, 22.15, "tsunami", 150, sev=0.75,
      note="Helike sank into the Gulf of Corinth in one night with all its people and was never "
           "rebuilt; ships were still striking its walls under water two centuries later. An "
           "explicit severity, because no count of the dead survives.",
      src="Helike"),

    E("226 BC Rhodes earthquake", -226, 36.43, 28.22, "earthquake", 200, sev=0.60,
      note="Toppled the Colossus of Rhodes, which had stood for fifty-four years and was one of "
           "the seven wonders; the Rhodians were sent money for the rebuilding from across the "
           "Greek world and then left it lying where it fell.",
      src="Colossus of Rhodes"),

    E("115 Antioch earthquake", 115, 36.20, 36.15, "earthquake", 200, dead=260000,
      note="Trajan was in the city and was pulled from a window. The count of 260,000 is "
           "ancient and probably too high, but not by the whole of it.",
      src="115 Antioch earthquake"),

    E("365 Crete earthquake and tsunami", 365, 35.00, 24.00, "earthquake", 600, mag=8.5,
      dead=50000,
      note="Lifted the west of Crete nine metres and drowned Alexandria's harbours.",
      src="365 Crete earthquake"),

    E("526 Antioch earthquake", 526, 36.20, 36.15, "earthquake", 250, dead=250000,
      src="526 Antioch earthquake"),

    E("Plague of Justinian", 541, 45.00, 30.00, "plague", 5000, end=750, dead=25000000,
      note="Began at Pelusium in Egypt and returned in waves for two hundred years. Nothing was "
           "damaged; there was simply nobody left to keep anything up.",
      src="Plague of Justinian"),

    E("Antonine Plague", 165, 41.90, 12.50, "plague", 1800, end=180, dead=5000000,
      note="Brought back from the siege of Seleucia. Probably smallpox or measles.",
      src="Antonine Plague"),

    E("856 Damghan earthquake", 856, 36.17, 54.33, "earthquake", 250, dead=200000,
      src="856 Damghan earthquake"),

    E("893 Ardabil earthquake", 893, 38.25, 48.28, "earthquake", 200, dead=150000,
      src="893 Ardabil earthquake"),

    E("1202 Syria earthquake", 1202, 34.50, 36.00, "earthquake", 500, dead=1100000,
      note="The 1.1 million figure is medieval and almost certainly includes the famine and "
           "plague that followed; the shaking itself ran from Egypt to Armenia.",
      src="1202 Syria earthquake"),

    E("1268 Cilicia earthquake", 1268, 37.50, 35.50, "earthquake", 300, dead=60000,
      src="1268 Cilicia earthquake"),

    E("1290 Chihli earthquake", 1290, 41.50, 119.30, "earthquake", 300, dead=100000,
      src="1290 Chihli earthquake"),

    E("Great Famine of 1315-1317", 1315, 50.50, 5.00, "famine", 1200, end=1317, dead=5000000,
      note="Rain from May 1315 to July 1317 across northern Europe; a tenth to a quarter of "
           "every town's people gone.",
      src="Great Famine of 1315–1317"),

    E("Black Death", 1346, 45.00, 35.00, "plague", 5500, end=1353, dead=25000000,
      note="The pack files a 'Black Death, Europe and the Mamluk Sultanate' as a famine with a "
           "744 km radius, which is the wrong kind and half the reach. This row replaces it.",
      src="Black Death"),

    # ---------------------------------------------------------------- the early modern world
    E("Smallpox epidemic in Mexico, Tenochtitlan", 1520, 19.43, -99.13, "epidemic", 700,
      dead=5500000, end=1521,
      note="Carried by the Spanish; within two years a third to a half of central Mexico was "
           "dead. The houses stood. Nobody thatched them.",
      src="Smallpox epidemic in Mexico"),

    E("Cocoliztli epidemic, New Spain", 1545, 19.43, -99.13, "epidemic", 900,
      dead=10000000, end=1550,
      note="The worst epidemic in the history of Mexico; probably a viral haemorrhagic fever "
           "worsened by the drought of the same years.",
      src="Cocoliztli epidemic"),

    E("Great Fire of London", 1666, 51.51, -0.09, "fire", 6, end=1666, sev=0.92,
      note="Officially six dead, which is why it carries an explicit severity rather than one "
           "taken from the dead: it burned 13,200 houses, 87 churches and St Paul's, and left "
           "70,000 of 80,000 Londoners homeless.",
      src="Great Fire of London"),

    E("Great Fire of Meireki, Edo", 1657, 35.69, 139.69, "fire", 8, sev=0.90, dead=100000,
      note="Burned most of Edo and killed more people than any fire between then and Hiroshima.",
      src="Great Fire of Meireki"),

    # Step 39 (D9) asked for a fire scene, and the hazard pack had two fires in all of history --
    # London in 1666 and Edo in 1657. That is a hole, not a judgement: a scraped pack of 26,997
    # hazards carries earthquakes and volcanoes and plagues and not one fire. These four are the
    # fires a world without them would be wrong about, each on a different continent in a
    # different century, and each carrying the article its figures came from.
    E("Great Fire of Rome", 64, 41.89, 12.49, "fire", 8, sev=0.85,
      note="Began in the shops around the Circus Maximus on the night of 18-19 July AD 64 and "
           "ran for six days. Of Rome's fourteen districts three were razed, seven left as "
           "scorched ruins and only four untouched. No count of the dead survives, so it carries "
           "an explicit severity rather than one taken from the dead.",
      src="Great Fire of Rome"),

    E("1547 Great Fire of Moscow", 1547, 55.75, 37.62, "fire", 8, sev=0.72, dead=2700,
      note="Between 2,700 and 3,700 dead and 80,000 left homeless; the dead are the low end of "
           "the range the sources give, because the low end is the one both of them name. The "
           "first of the three great fires that made a wooden city burn.",
      src="Conflagrations"),

    E("Fire of Moscow (1812)", 1812, 55.75, 37.62, "fire", 10, sev=0.88,
      note="Raged from 14 to 18 September 1812 as the Russians left and Napoleon's vanguard "
           "came in after Borodino: 6,496 of the city's 9,151 residential buildings and 122 of "
           "its 329 churches, three-quarters of Moscow. It is why the 1812 campaign failed.",
      src="Fire of Moscow (1812)"),

    E("Great Chicago Fire", 1871, 41.88, -87.63, "fire", 8, sev=0.70, dead=300,
      note="Burned from 8 to 10 October 1871: about 300 dead, more than 17,000 buildings over "
           "some three and a half square miles, and 100,000 people left with nowhere to sleep. "
           "It is the reason Chicago is built of what it is built of.",
      src="Great Chicago Fire"),

    E("1693 Sicily earthquake", 1693, 37.15, 15.00, "earthquake", 300, dead=60000,
      note="Levelled forty towns in south-east Sicily, which were then rebuilt in the Sicilian "
           "Baroque that is still standing.",
      src="1693 Sicily earthquake"),

    E("1737 Calcutta cyclone", 1737, 22.57, 88.36, "flood", 300, dead=300000,
      src="1737 Calcutta cyclone"),

    E("1759 Near East earthquakes", 1759, 34.00, 36.20, "earthquake", 350, dead=20000,
      note="Four months of shocks from Baalbek to Safed; Baalbek's temples went down in them.",
      src="1759 Near East earthquakes"),

    E("1783 Calabrian earthquakes", 1783, 38.15, 15.55, "earthquake", 300, dead=35000,
      end=1786,
      note="Five shocks over three months that rebuilt the toe of Italy from the ground up; the "
           "tsunami that followed the first of them took Reggio.",
      src="1783 Calabrian earthquakes"),

    E("Great Famine of 1876-1878", 1876, 20.00, 78.00, "famine", 1500, end=1878,
      dead=31000000,
      note="Drought across India, China, Brazil and North Africa under an El Nino; the figure is "
           "the low end of the range and the high end runs past sixty million. Step 35's "
           "climate_periods carries it as a drought; this is the famine it became.",
      src="1876–1878 famine"),

    # ---------------------------------------------------------------- the industrial age
    E("1883 eruption of Krakatoa", 1883, -6.10, 105.42, "volcano", 500, dead=36417, mag=6,
      note="The pack has Krakatau erupting in 1684 and then not until 1932. The loudest sound "
           "in the historical record, and it took the island with it.",
      src="1883 eruption of Krakatoa"),

    E("1886 eruption of Mount Tarawera", 1886, -38.23, 176.51, "volcano", 200, dead=153,
      mag=5, note="Buried the Pink and White Terraces, which were the eighth wonder.",
      src="1886 eruption of Mount Tarawera"),

    E("1887 Yellow River flood", 1887, 34.80, 113.60, "flood", 500, dead=1500000, end=1888,
      note="Estimates run from 900,000 to two million dead; eleven cities and three hundred "
           "villages under water for a year.",
      src="1887 Yellow River flood"),

    E("1889 Johnstown Flood", 1889, 40.33, -78.92, "flood", 40, dead=2209,
      src="Johnstown Flood"),

    E("1900 Galveston hurricane", 1900, 29.30, -94.79, "flood", 150, dead=10000,
      note="Still the deadliest natural disaster in the history of the United States.",
      src="1900 Galveston hurricane"),

    E("1902 eruption of Mount Pelee", 1902, 14.81, -61.17, "volcano", 40, dead=29000, mag=4,
      note="A pyroclastic flow erased Saint-Pierre in two minutes and left one survivor in the "
           "city, a prisoner in an underground cell.",
      src="1902 eruption of Mount Pelée"),

    E("1902 eruption of Santa Maria", 1902, 14.75, -91.55, "volcano", 250, dead=6000, mag=6,
      src="1902 eruption of Santa María"),

    E("1349 Rome earthquake", 1349, 41.89, 12.49, "earthquake", 250, dead=1000, sev=0.62,
      note="Took the whole south side of the Colosseum down, which is why two thirds of it is "
           "standing and the outer wall on that side is not; it also brought the tower of the "
           "Senate down and cracked Santa Maria Maggiore. The pack carries no earthquake in Rome "
           "in this century at all.",
      src="1349 Rome earthquake"),

    E("1906 San Francisco earthquake", 1906, 37.77, -122.42, "earthquake", 300, dead=3000,
      mag=7.9,
      note="The fire that followed did more damage than the shaking; the pack carries only a "
           "'Tsunami at N. California'.",
      src="1906 San Francisco earthquake"),

    E("1908 Messina earthquake", 1908, 38.15, 15.55, "earthquake", 200, dead=80000, mag=7.1,
      note="The deadliest earthquake in European history, followed by a tsunami that took "
           "Messina and Reggio both.",
      src="1908 Messina earthquake"),

    E("1918 Spanish flu", 1918, 40.00, 10.00, "pandemic", 15000, dead=50000000, end=1920,
      note="A third of the world infected, in three waves, in two years. It damaged nothing and "
           "left nobody to mend anything.",
      src="Spanish flu"),

    E("Typhus epidemic in Russia, 1918-1922", 1918, 55.75, 37.62, "epidemic", 800,
      dead=2500000, end=1922, src="Typhus"),

    E("1920 Haiyuan earthquake", 1920, 36.50, 105.30, "earthquake", 400, dead=273000, mag=7.8,
      note="Landslides buried whole villages; some estimates of the dead run to 273,000.",
      src="1920 Haiyuan earthquake"),

    E("1927 Gulang earthquake", 1927, 37.50, 102.50, "earthquake", 300, dead=40900, mag=7.6,
      src="1927 Gulang earthquake"),

    E("Great Mississippi Flood of 1927", 1927, 34.00, -90.50, "flood", 400, dead=500,
      end=1927, sev=0.70,
      note="Twenty-seven thousand square miles under water for months and seven hundred "
           "thousand people put out; the dead are few because they were counted in the camps.",
      src="Great Mississippi Flood of 1927"),

    E("1931 Hawke's Bay earthquake", 1931, -39.50, 176.90, "earthquake", 200, dead=256,
      mag=7.8,
      note="Raised forty square kilometres of seabed into dry land and rebuilt Napier in "
           "Art Deco.",
      src="1931 Hawke's Bay earthquake"),

    E("1931 China floods", 1931, 30.60, 114.30, "flood", 700, dead=2000000, end=1931,
      note="Estimates of the dead run from 145,000 to four million; the Yangtze, the Huai and "
           "the Grand Canal all over their banks at once.",
      src="1931 China floods"),

    E("Dust Bowl, 1930-1936", 1930, 36.00, -100.00, "famine", 600, end=1936, dead=7000,
      note="Not a famine in the old sense but it emptied the southern plains: three hundred "
           "thousand people left Oklahoma and the topsoil went with them.",
      src="Dust Bowl"),

    E("1934 Nepal-Bihar earthquake", 1934, 26.86, 86.63, "earthquake", 300, dead=10000,
      mag=8.0, src="1934 Nepal–Bihar earthquake"),

    E("1935 Quetta earthquake", 1935, 30.18, 66.98, "earthquake", 200, dead=45000, mag=7.7,
      note="Quetta was destroyed in thirty seconds; the death count runs from 30,000 to 60,000.",
      src="1935 Quetta earthquake"),

    E("1939 Erzincan earthquake", 1939, 39.75, 39.50, "earthquake", 300, dead=32700, mag=7.8,
      src="1939 Erzincan earthquake"),

    E("1950 Assam-Tibet earthquake", 1950, 28.50, 96.70, "earthquake", 500, dead=4800,
      mag=8.6,
      note="The largest earthquake ever recorded on land; landslides dammed the Subansiri and "
           "the dams then burst.",
      src="1950 Assam–Tibet earthquake"),

    E("North Sea flood of 1953", 1953, 52.00, 4.00, "flood", 250, dead=2551,
      note="Drowned 1,836 people in the Netherlands and 307 in England in one night, and is why "
           "the Delta Works and the Thames Barrier exist.",
      src="North Sea flood of 1953"),

    E("1959-1961 Great Chinese Famine", 1959, 34.00, 110.00, "famine", 1200, end=1961,
      dead=30000000,
      note="The largest famine in recorded history; the low end of the estimates is fifteen "
           "million dead and the high end forty-five.",
      src="Great Chinese Famine"),

    E("1960 Valdivia earthquake", 1960, -38.24, -73.05, "earthquake", 800, dead=6000, mag=9.5,
      note="The largest earthquake ever instrumentally recorded; its tsunami crossed the Pacific "
           "and took 61 in Hawaii and 138 in Japan.",
      src="1960 Valdivia earthquake"),

    E("1963 Vajont Dam disaster", 1963, 46.27, 12.33, "flood", 40, dead=1917,
      note="A mountainside slid into a reservoir and the wall of water went over the dam and "
           "into Longarone. Not a natural disaster, but it is what the ground did.",
      src="Vajont Dam disaster"),

    E("1964 Alaska earthquake", 1964, 61.02, -147.72, "earthquake", 700, dead=131, mag=9.2,
      src="1964 Alaska earthquake"),

    E("1970 Bhola cyclone", 1970, 22.00, 90.50, "flood", 350, dead=400000,
      note="The deadliest tropical cyclone ever recorded, and the proximate cause of the "
           "Bangladesh Liberation War.",
      src="1970 Bhola cyclone"),

    E("1975 Banqiao Dam failure", 1975, 32.60, 113.60, "flood", 400, dead=171000,
      note="Sixty-two dams went in one typhoon; the official death count was 85,600 and other "
           "estimates run past 240,000.",
      src="1975 Banqiao Dam failure"),

    E("1976 Tangshan earthquake", 1976, 39.63, 118.18, "earthquake", 400, dead=242769,
      mag=7.6,
      note="The pack carries it as 'Earthquake in China, Hebei (242,769 dead)' with no "
           "magnitude; this row supplies it.",
      src="1976 Tangshan earthquake"),

    E("1973 Heimaey eruption", 1973, 63.43, -20.28, "volcano", 20, dead=1, mag=3,
      note="A third of the town went under lava before it was stopped by spraying sea water on "
           "the flow; the whole island was evacuated overnight.",
      src="Eldfell"),

    E("1980 eruption of Mount St. Helens", 1980, 46.20, -122.18, "volcano", 400, dead=57,
      mag=5, note="The pack files it as an earthquake.",
      src="1980 eruption of Mount St. Helens"),

    E("1985 Mexico City earthquake", 1985, 19.43, -99.13, "earthquake", 400, dead=10000,
      mag=8.0, src="1985 Mexico City earthquake"),

    E("1986 Lake Nyos disaster", 1986, 6.44, 10.30, "volcano", 30, dead=1746,
      note="The lake turned over and a cloud of carbon dioxide rolled down two valleys; the "
           "villages are still empty.",
      src="Lake Nyos disaster"),

    E("1983-1985 famine in Ethiopia", 1983, 12.00, 39.00, "famine", 800, end=1985,
      dead=1000000, src="1983–1985 famine in Ethiopia"),

    E("1999 Izmit earthquake", 1999, 40.75, 29.87, "earthquake", 250, dead=17118, mag=7.6,
      src="1999 İzmit earthquake"),

    E("2003 Bam earthquake", 2003, 29.00, 58.33, "earthquake", 150, dead=34000, mag=6.6,
      note="Three quarters of the Arg-e Bam, the largest adobe building in the world, came down.",
      src="2003 Bam earthquake"),

    E("2004 Indian Ocean earthquake and tsunami", 2004, 3.31, 95.85, "tsunami", 1200,
      dead=227898, mag=9.1,
      note="Fourteen countries; the pack's nearest entry is an 'Earthquake at Indian Ocean: "
           "Felt In Maldives' three thousand kilometres away.",
      src="2004 Indian Ocean earthquake and tsunami"),

    E("2005 Hurricane Katrina", 2005, 29.95, -90.07, "flood", 250, dead=1392,
      note="Eighty per cent of New Orleans under water for weeks, and a hundred and eighty "
           "thousand houses made uninhabitable.",
      src="Hurricane Katrina"),

    E("2005 Kashmir earthquake", 2005, 34.54, 73.59, "earthquake", 250, dead=87350, mag=7.6,
      src="2005 Kashmir earthquake"),

    E("2010 Haiti earthquake", 2010, 18.46, -72.45, "earthquake", 200, dead=200000, mag=7.0,
      note="Port-au-Prince was destroyed in thirty-five seconds. The government's own count was "
           "316,000 dead and other estimates are lower; 200,000 is the middle.",
      src="2010 Haiti earthquake"),

    E("2010 eruption of Eyjafjallajokull", 2010, 63.63, -19.62, "volcano", 300, dead=0,
      mag=4, sev=0.45,
      note="Killed nobody and grounded a hundred thousand flights; the ash closed European "
           "airspace for a week. An explicit severity, because the dead give none.",
      src="2010 eruptions of Eyjafjallajökull"),

    E("2011 Tohoku earthquake and tsunami", 2011, 38.30, 142.37, "tsunami", 600, dead=19747,
      mag=9.1,
      note="Moved Honshu two metres east and turned the clock back eleven microseconds; the "
           "pack carries it as two duplicate 'Earthquake in Japan, Tohoku' rows.",
      src="2011 Tōhoku earthquake and tsunami"),

    E("2011 Christchurch earthquake", 2011, -43.53, 172.64, "earthquake", 100, dead=185,
      mag=6.3,
      note="Only 185 dead, but the central city was condemned and eighteen hundred buildings "
           "were pulled down over the next five years.",
      src="2011 Christchurch earthquake"),

    E("2011 Thailand floods", 2011, 14.00, 100.50, "flood", 400, dead=815, end=2012,
      src="2011 Thailand floods"),

    E("2015 Nepal earthquake", 2015, 28.23, 84.73, "earthquake", 300, dead=8962, mag=7.8,
      src="April 2015 Nepal earthquake"),

    E("2023 Turkey-Syria earthquakes", 2023, 37.17, 37.08, "earthquake", 500, dead=59488,
      mag=7.8, src="2023 Turkey–Syria earthquakes"),

    E("COVID-19 pandemic", 2019, 30.00, 20.00, "pandemic", 15000, dead=7000000, end=2023,
      note="The first pandemic the mod's own data reaches into; the official count is 7.1 "
           "million dead and the excess-mortality estimates run to three times that.",
      src="COVID-19 pandemic"),

    # ---------------------------------------------------------------- the ones the pack lost
    E("1811-1812 New Madrid earthquakes", 1811, 36.60, -89.60, "earthquake", 700, dead=1000,
      mag=7.5, end=1812,
      note="The pack carries this event three times, filed under AD 7, AD 16 and AD 23, because "
           "the year did not survive the parsing. This is the real one.",
      src="1811–1812 New Madrid earthquakes"),
]
