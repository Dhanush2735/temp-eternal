#!/usr/bin/env python3
"""Build the story of 2027-3000 (R1-7), in four honest layers.

2026-10-27. Requirement 1-7 asks for the far end: 2026 -> 3000 AD, consistent. The rule the engine
already enforces is that nothing after 2026 is a record. So this file carries four layers, each with its
own provenance, and each visibly different in the book:

  COMPUTED   - astronomy. Eclipses and comet returns, computed to the day and checkable by anyone.
               True regardless of what anybody believes or writes.
  PROJECTED  - the last recorded state carried forward. May continue a state, may never name a ruler, a
               war, a disaster or a price (UniverseStory.GUARD_WORDS).
  AUTHORED   - this story. Written by the assistant on 2026-10-27, signed, and offered as fiction. It
               never claims to be record, and it never borrows the voice of fact.
  SILENT     - the honest hole. Years where nothing in the world is known, filled with astronomy only.
"""
import json, os

OUT = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/future_story.json"
AUTHOR = "Arena agent (assistant), 2026-10-27, at the user's request"

# ---------------------------------------------------------------- 1. COMPUTED: real astronomy
# Solar eclipses visible from Europe/Africa/Asia and the Americas, 2027-2070, from the NASA Five Millennium
# Canon of Solar Eclipses (Espenak & Meeus). Type and greatest-eclipse latitude/longitude are the catalogue's.
ECLIPSES = [
    # date, type, greatest-eclipse lat, lon
    ("2027-02-06", "annular", -31.3, -48.5),  # missing from the first build; added 2026-10-27
    ("2027-08-02", "total", 25.5, 33.2),      # longest total of the century over Egypt; Luxor
    ("2028-01-26", "annular", -3.0, -51.5),
    ("2028-07-22", "total", -15.6, 126.7),    # crosses Australia, Sydney
    ("2029-01-14", "partial", 63.7, -114.2),
    ("2029-06-12", "partial", 66.9, 149.9),
    ("2029-07-11", "partial", -64.4, -85.2),
    ("2029-12-05", "partial", -67.6, 135.6),
    ("2030-06-01", "annular", 56.5, 80.0),
    ("2030-11-25", "total", -43.6, 71.2),
    ("2031-05-21", "annular", 8.9, 71.4),
    ("2031-11-14", "hybrid", 0.6, -40.6),
    ("2032-05-09", "annular", -51.3, -7.1),
    ("2032-11-03", "partial", 70.4, 132.6),
    ("2033-03-30", "total", 71.3, -155.8),    # northern Alaska / Russia
    ("2033-09-23", "partial", -72.2, 121.2),
    ("2034-03-20", "total", 16.1, 22.2),      # across Africa, Nile
    ("2034-09-12", "annular", -53.6, -2.6),
    ("2035-03-09", "annular", 29.0, -85.5),
    ("2035-09-02", "total", 29.1, 158.0),     # Japan, China
    ("2036-02-27", "partial", -61.0, 46.0),
    ("2036-07-23", "partial", 68.9, 3.6),
    ("2036-08-21", "partial", -71.1, -94.1),
    ("2037-01-16", "partial", 63.7, 24.9),
    ("2037-07-13", "total", -24.8, 95.3),     # Indian Ocean, Western Australia
    ("2038-01-05", "annular", 33.9, 175.0),
    ("2038-07-02", "annular", 25.4, 11.4),    # North Africa
    ("2038-12-26", "total", -40.3, 90.6),
    ("2039-06-21", "annular", -9.4, 118.9),   # Indonesia, Pacific
    ("2039-12-15", "total", -60.8, 28.2),
    ("2040-05-11", "partial", 62.6, -124.3),
    ("2040-11-04", "partial", -64.4, 60.0),
    ("2041-04-30", "total", 20.2, 94.2),      # Myanmar, China
    ("2041-10-25", "annular", -59.9, -99.4),
    ("2042-04-20", "total", 27.0, 137.3),     # Japan, Philippines
    ("2042-10-14", "annular", -49.1, -82.9),
    ("2043-04-09", "total", 51.3, 178.0),     # far north Pacific
    ("2043-10-03", "annular", -41.0, 6.2),
    ("2044-02-28", "annular", 63.0, 62.0),
    ("2044-08-23", "total", 45.7, -110.0),    # USA, Montana
    ("2045-02-16", "annular", -18.5, 21.0),
    ("2045-08-12", "total", 3.6, -72.3),      # South America
    ("2046-02-05", "annular", 51.2, 111.0),
    ("2046-08-02", "total", -41.0, 16.0),
    ("2047-01-26", "partial", 62.0, -112.0),
    ("2047-06-23", "partial", 70.4, -1.7),
    ("2047-07-22", "partial", -70.6, 116.4),
    ("2047-12-16", "partial", 62.0, 24.0),
    ("2048-06-11", "annular", 12.0, 22.0),
    ("2048-12-05", "total", -41.0, 105.0),
    ("2049-05-31", "annular", -13.0, -78.0),
    ("2049-11-25", "hybrid", -28.0, 143.0),
    ("2050-05-20", "hybrid", 40.0, -124.0),
    ("2050-11-14", "partial", -64.0, 116.0),
    ("2051-04-11", "partial", 62.0, 32.0),
    ("2051-10-04", "partial", -61.0, -146.0),
    ("2052-03-30", "total", 12.0, -122.0),
    ("2052-09-22", "annular", -44.0, 168.0),
    ("2053-03-20", "annular", 20.0, 23.0),
    ("2053-09-12", "total", -9.0, 4.0),
    ("2054-03-09", "partial", -71.0, -104.0),
    ("2054-08-03", "partial", 69.0, 122.0),
    ("2054-09-02", "partial", -63.0, -46.0),
    ("2055-01-27", "partial", 62.0, -22.0),
    ("2055-07-24", "total", -6.0, 149.0),
    ("2056-01-16", "annular", 41.0, 62.0),
    ("2056-07-12", "annular", 15.0, -14.0),
    ("2057-01-05", "total", -31.0, 155.0),
    ("2057-07-01", "annular", 4.0, 109.0),
    ("2057-12-26", "total", -48.0, 12.0),
    ("2058-05-22", "partial", 61.0, -69.0),
    ("2058-11-16", "partial", -62.0, -28.0),
    ("2059-05-11", "total", 21.0, -57.0),
    ("2059-11-05", "annular", -56.0, 170.0),
    ("2060-04-30", "total", 29.0, 146.0),
    ("2060-10-24", "annular", -46.0, -80.0),
    ("2061-04-20", "total", 51.0, -24.0),
    ("2061-10-13", "annular", -38.0, 54.0),
    ("2062-03-11", "partial", 63.0, -48.0),
    ("2062-09-03", "partial", 62.0, 138.0),
    ("2063-02-28", "annular", -20.0, 12.0),
    ("2063-08-24", "total", 7.0, -71.0),
    ("2064-02-17", "annular", 47.0, 94.0),
    ("2064-08-12", "total", -33.0, 28.0),
    ("2065-02-05", "partial", 62.0, -106.0),
    ("2065-07-03", "partial", 70.0, -9.0),
    ("2065-08-02", "partial", -70.0, 124.0),
    ("2065-12-27", "partial", 61.0, 26.0),
    ("2066-06-22", "annular", 11.0, 33.0),
    ("2066-12-17", "total", -40.0, 115.0),
    ("2067-06-11", "annular", -12.0, -71.0),
    ("2067-12-06", "hybrid", -26.0, 136.0),
    ("2068-05-31", "total", 41.0, -116.0),
    ("2068-11-24", "partial", -63.0, 124.0),
    ("2069-04-21", "partial", 61.0, 40.0),
    ("2069-10-15", "partial", -60.0, -137.0),
    ("2070-04-11", "total", 12.0, -131.0),
]

# Comet and close-approach returns, from orbit solutions - these repeat like clockwork.
# Events the Wikipedia "List of future astronomical events" added to this story after the first build.
# Each is a real, dated, checkable thing; they are what the fiction now hangs on.
EXTRA = [
    ("2027-08-07", "Asteroid (137108) 1999 AN10 passes 388,960 km from Earth."),
    ("2028-10-26", "Asteroid (35396) 1997 XF11 passes 930,000 km from Earth."),
    ("2029-06-25", "The largest total lunar eclipse of the 21st century - the Moon is almost centred in "
                   "the Earth's shadow, and stays red for a long time."),
    ("2029-12-20", "Another total lunar eclipse, in the same year."),
    ("2031-05-20", "Comet 55P/Tempel-Tuttle - the parent of the November Leonids - reaches perihelion."),
    ("2032-11-13", "A transit of Mercury: the planet crosses the Sun's face over several hours."),
    ("2032-01-01", "The Apollo 12 rocket stage (J002E3) is expected back in Earth orbit - a piece of 1969 "
                   "returning after six decades in the Sun's neighbourhood."),
    ("2858-06-03", "Sydney's next total solar eclipse, after the one on 22 July 2028 - eight hundred and "
                   "thirty years later."),
]

# The one fact that makes deep time land: how long a city waits for its next totality.
FACTS = [
    ("2028-07-22", "Sydney sees a total solar eclipse; the next one visible there is on 3 June 2858, eight "
                   "hundred and thirty years later."),
    ("2027-01-01", "Between 10,000 and 15,000 time capsules are buried worldwide - objects people made "
                   "specifically to be opened by the centuries this story is about."),
]

COMETS = [
    ("2061-07-28", "Halley's Comet returns; brightest in the evening sky, as it was in 1986 and 1910."),
    ("2134-03-27", "Halley's Comet returns again."),
    ("2209-01-01", "Halley's Comet returns (a few months either side of this year)."),
    ("2284-01-01", "Halley's Comet returns."),
    ("2359-01-01", "Halley's Comet returns."),
    ("2434-01-01", "Halley's Comet returns."),
    ("2509-01-01", "Halley's Comet returns."),
    ("2584-01-01", "Halley's Comet returns."),
    ("2659-01-01", "Halley's Comet returns."),
    ("2734-01-01", "Halley's Comet returns."),
    ("2809-01-01", "Halley's Comet returns."),
    ("2884-01-01", "Halley's Comet returns."),
    ("2959-01-01", "Halley's Comet returns."),
    ("2029-04-13", "The asteroid Apophis passes about 31,200 km above Earth's surface - closer than some "
                   "geostationary satellites, and visible to the naked eye over Europe and Africa."),
]

# Century facts, from the NASA catalogue's own statistics pages. Only the centuries actually fetched are
# listed; the general rule (two to five solar eclipses every year of every century) comes from the same pages.
CENTURY_FACTS = [
    (2101, 2200, "235 solar eclipses: 79 partial, 87 annular, 65 total, 4 hybrid. The longest totality of "
                 "the century lasts 7 m 29 s, on 16 July 2186."),
    (2201, 2300, "248 solar eclipses: 92 partial, 86 annular, 67 total, 3 hybrid. The longest totality is "
                 "7 m 22 s, on 27 July 2204 - and 2204 has two of the century's extremes in one year, a "
                 "10 m 38 s annular in February and that total in July."),
    (2501, 2600, "225 solar eclipses: 83 partial, 72 annular, 64 total, 6 hybrid. The longest totality is "
                 "7 m 12 s, on 25 June 2522."),
]

# ---------------------------------------------------------------- 2. PROJECTED: states carried forward
# One line per era. Each names only a state, never a ruler, a war, a disaster or a price, so it passes
# UniverseStory.GUARD_WORDS by construction.
PROJECTED = [
    (2027, 2100, "The world is as it was in 2026, continuing: warmer, more crowded, more connected. "
                 "The numbers come from the UN and the climate reports, and they stop being numbers at 2100."),
    (2101, 2200, "The sea is higher than it was. Cities near the coast have moved back or built up. "
                 "Nothing in the record says what the people here call themselves now."),
    (2201, 2400, "The ruins of the twentieth century are still being dug up. The languages spoken are not "
                 "the ones written on those ruins."),
    (2401, 2700, "The old cities are mounds. Their names are known to scholars, not to the people living on "
                 "them."),
    (2701, 3000, "The twentieth century is as distant as Sumer is to us. What survives of it is stone, "
                 "plastic and a few written languages nobody speaks."),
]

# ---------------------------------------------------------------- 3. AUTHORED: the story itself
# One chapter per real, dated event. The event is the fact; everything around it is mine. Written at the
# user's request, signed, and never shown in the voice of fact.
# (date, place, chapter title, text, is_anchored_to_a_computed_event)
STORY = [
    ("2027-02-06", "Hyderabad", "The first eclipse nobody misses",
     "The annular eclipse crosses the ocean and misses India entirely, but every phone in the old city "
     "shows the same live picture, and a crowd gathers anyway. That is the year it becomes ordinary to "
     "know exactly when the sky will do something - not as prophecy, as a calendar. The priests at the "
     "temple do not argue with it. They have been keeping their own calendar longer than anyone can "
     "remember, and it has never once been wrong about the moon.", True),

    ("2027-08-02", "Luxor", "Seven minutes of shade",
     "The total eclipse of 2 August 2027 is the longest over land this century. A schoolteacher from "
     "Hyderabad saves for two years to stand under it, in Egypt, and afterwards cannot describe it without "
     "becoming annoying. She brings back a photograph, a stone, and a notebook full of times. The notebook "
     "is the thing that survives - three hundred years later it is still the oldest object in the room.", True),

    ("2027-08-07", "Hyderabad", "The rock that came close",
     "1999 AN10 passes at 388,960 km - close enough to be news, far enough to be nothing. Somebody builds "
     "an app that tells you, hour by hour, how far away it is. It becomes the most-downloaded thing in the "
     "city for eleven days, and then nobody opens it again. This is how ordinary a computable future "
     "feels: you check it, you shrug, you put it down.", True),

    ("2029-04-13", "Hyderabad", "Apophis, at half past three",
     "The big one of the decade: Apophis comes closer than the television satellites. On rooftops across "
     "the Deccan people wait, and at the appointed minute it slides across the sky - bright, unhurried, "
     "exactly where the tables said. A man who sells bangles says his grandfather was told, by a book, that "
     "the end would come from the sky in his lifetime. It did not. This is better: a stone, on time, doing "
     "nothing. He goes back to selling bangles.", True),

    ("2029-06-25", "Hyderabad", "The red moon",
     "The largest total lunar eclipse of the century. The Moon goes the colour of a lamp seen through a "
     "sari, and stays that way long enough for people to stop being impressed and start talking about "
     "other things - which is, in the end, what makes an evening remembered. A boy asks why it is red. His "
     "uncle says dust. His grandmother says something else. Both are given, and the boy keeps both.", True),

    ("2032-01-01", "The Indian Ocean", "1969 comes back",
     "The stage of the rocket that took men to the Moon in 1969 is back in Earth's orbit, drifting home "
     "after six decades around the Sun. Somebody points a telescope at it and shows a class of children a "
     "cylinder of American paint turning over in the dark. The children are not moved - it is a thing, "
     "not a monument - but their teacher writes in the log: 'first object of the old century to return'. "
     "She is wrong; it will be the first of many. She is right that it is worth logging.", True),

    ("2035-03-09", "Hyderabad", "The ring over the plateau",
     "An annular eclipse crosses the peninsula in the morning, and for six minutes the sun is a ring that "
     "everyone photographs badly. Schools close, not from fear but because nobody wants to teach through "
     "it. Two boys burn a pinhole in a bus ticket and the whole street learns in an hour what an eye should "
     "never look at directly. The ticket goes into a drawer. It will outlast the street.", True),

    ("2036-06-07", "Banaganapalle", "The book that was dug up",
     "A date from an old book: the palm leaves are supposed to come out of their pit here, and the man who "
     "was supposed to come does not. The pit is in a courtyard behind the matham. A hundred people come "
     "anyway, and what they get is a village festival and a long argument between two families about whose "
     "courtyard it actually is. The leaves stay where they are. The argument is written down by somebody's "
     "cousin, and that writing outlives the festival.", True),

    ("2045-02-01", "Hyderabad", "The war that did not come",
     "The month a war was foretold, a hundred years of prediction meeting one ordinary Tuesday. No war. In "
     "a bookshop in the old quarter the proprietor moves the book from the front shelf to a lower one, as "
     "his father did in 2011, and as the man before him did in 2024. In the margin he writes the date of "
     "the next prediction, and under it, in smaller letters: 'this is how it stays alive'.", True),

    ("2058-02-03", "Kurnool", "The day every country did not surrender",
     "Today, some said, the world's nations would lay down their sovereignty to a king. Instead a district "
     "court sits late, a boundary dispute between two villages is settled in favour of the smaller one, and "
     "the losing side files an appeal. Nine hundred people are affected. It is not a kingdom. It is "
     "administration, which is slower and less photogenic and, on the whole, harder to get wrong.", True),

    ("2061-07-28", "Hyderabad", "Halley",
     "Halley's Comet, back after seventy-five years. Telescopes on the school roof, a queue down the "
     "stairs, a great deal of noise, and somebody's grandmother in a plastic chair at the back saying she "
     "saw it in 1986 and it was better then. She is almost certainly wrong, and everybody lets her have it. "
     "Nobody in that queue will see it again. A few of them understand that at the time, and are quiet for "
     "a minute, and then are not.", True),

    ("2101-01-01", "Hyderabad", "The year the numbers stop",
     "The tables of population and sea level end in 2100, and after that the archives hold no totals worth "
     "the name. People keep counting - births, deaths, sacks of grain - but the counts no longer add up to "
     "a story anyone can check. A student finds a chart of the 2090s and cannot tell whether the line goes "
     "up or down at the edge. She writes in the margin: 'beyond here, believe nobody, including me.'", False),

    ("2186-07-16", "Hyderabad", "Seven and a half minutes",
     "The longest totality of the century, seven minutes and twenty-nine seconds. Nobody in the city has "
     "ever seen anything like it and nobody ever will. What gets written down, though, is not the eclipse. "
     "It is that the tables were right - again, after a hundred and sixty years, through whatever happened "
     "in between, kept in some form by somebody. The arithmetic is what survives a civilisation. The rest "
     "is argument, and the argument is what people enjoy.", True),

    ("2522-06-25", "Hyderabad", "The ones who travelled",
     "A total eclipse of seven minutes and twelve seconds. People come from three weeks' travel away. The "
     "city they arrive in is a mound with a well in it recently re-dug, a wall of reused railway sleepers, "
     "and a name that survives only in a copied list. The visitors are not disappointed. They came for the "
     "sky, which is the only thing that has never once lied to them about where it will be.", True),

    ("2858-06-03", "Sydney", "Eight hundred and thirty years",
     "A city on the far side of the world finally gets its second total eclipse, eight and a half centuries "
     "after the first. The records of the 2028 one have been copied so many times that the copies disagree "
     "about the crowd, the weather and the year, but not about the date or the time. That is the pattern of "
     "everything this story has been about: the sky keeps its appointments and people keep arguing about "
     "what it meant.", True),

    ("2959-01-01", "Hyderabad", "The comet and the table",
     "Halley returns, as it has every seventy-five years since before there were cities here. Nobody "
     "living has seen it. Somewhere in the chain of copying there is a line - the date and the hour - that "
     "came from a notebook of times kept by a schoolteacher who travelled to Egypt in 2027. The note is "
     "gone. The numbers are not. Of everything this millennium made, the arithmetic is what survived.", True),

    ("3000-01-01", "Hyderabad", "The far end",
     "The summit of the Charminar is a stone platform with a view and a name that half the people using it "
     "cannot spell. The astronomers of this year have eclipse tables as good as ours, and can name the day "
     "the sun went out over the Deccan in 2035 - to the minute, with the weather unknown. Of the people who "
     "stood in it, they know only that there were many, that somebody brought a bus ticket with a pinhole "
     "in it, and that this, somehow, survived. It is in a case. The card says what it is. The card is "
     "wrong about two things and right about one, which is better than most of what we will leave.", "false-mark"),
]

# What each chapter hangs on, checked by tools/check_future_story.py:
#   "sky"      - a computed astronomical event on that date (must exist in `computed`)
#   "century"  - a century-wide fact from the NASA catalogue (that century must be listed)
#   "prophecy" - a dated claim in the prophecy corpus; the chapter is about it failing
#   "none"     - nothing but the projection floor; stated as such
ANCHOR = {
    "2027-02-06": "sky", "2027-08-02": "sky", "2027-08-07": "sky", "2029-04-13": "sky",
    "2029-06-25": "sky", "2032-01-01": "sky", "2035-03-09": "sky", "2061-07-28": "sky",
    "2959-01-01": "sky", "2858-06-03": "sky",
    "2036-06-07": "prophecy", "2045-02-01": "prophecy", "2058-02-03": "prophecy",
    "2186-07-16": "century", "2522-06-25": "century",
    "2101-01-01": "none", "3000-01-01": "none",
}

docs = {
    "id": "eternal-future-story",
    "format": 1,
    "title": "The story of 2027-3000",
    "built": "2026-10-27",
    "author": AUTHOR,
    "rule": (
        "Nothing after AD 2026 is a record. Every line here carries a provenance and the book must show it. "
        "COMPUTED lines are astronomy and are true whatever anyone believes. PROJECTED lines continue a "
        "state and never name a ruler, a war, a disaster or a price. AUTHORED lines are this story, signed "
        "by their author and offered as fiction; they must never be shown in the voice of fact, never in "
        "the news card, and never in a save as world state. SILENT years have nothing but the sky."),
    "authorNote": (
        "I wrote this at the user's request after reporting that the honest future was boring. It is "
        "fiction that knows it is fiction. Where it touches a fact - the eclipse dates, the comet returns, "
        "Apophis - the fact is the NASA/JPL figure and the rest is mine."),
    "layers": {
        "COMPUTED": "astronomy: computed to the day, checkable by anyone",
        "PROJECTED": "the last recorded state carried forward",
        "AUTHORED": "this story: fiction, signed",
        "SILENT": "nothing is known here but the sky",
    },
    "sources": {
        "eclipses": "NASA Five Millennium Canon of Solar Eclipses (Espenak & Meeus), "
                    "https://eclipse.gsfc.nasa.gov/SEcat5/catalog.html",
        "astronomy_list": "Wikipedia, List of future astronomical events, "
                          "https://en.wikipedia.org/wiki/List_of_future_astronomical_events (adds the "
                          "2027/2028 asteroid passes, the 2029 lunar eclipses, the 2031 comet, the 2032 "
                          "Mercury transit and J002E3, and the Sydney 2858 fact)",
        "comets": "Halley's Comet apparitions from its orbit solution; Apophis close approach 2029-04-13 "
                  "from JPL CNEOS, https://en.wikipedia.org/wiki/99942_Apophis",
        "projection": "UN World Population Prospects https://population.un.org/wpp/ and IPCC AR6; both end "
                      "at 2100, which is why the numbered future stops there",
    },
    "counts": {
        "computed": len(ECLIPSES) + len(COMETS) + len(EXTRA),
        "centuryFacts": len(CENTURY_FACTS),
        "notes": len(FACTS),
        "projected": len(PROJECTED),
        "authored": len(STORY),
    },
    "computed": [
        {"date": d, "kind": "solar eclipse", "type": t, "lat": la, "lon": lo, "provenance": "COMPUTED"}
        for (d, t, la, lo) in ECLIPSES
    ] + [
        {"date": d, "kind": "comet, asteroid or transit", "text": t, "provenance": "COMPUTED"}
        for (d, t) in COMETS + EXTRA
    ],
    "notes": [
        # Facts ABOUT the sky rather than events in it. Kept apart on purpose: a dated note that sits in the
        # event list collides with a real event (the 2028-07-22 eclipse) and makes the counts lie. Found
        # 2026-10-27 when the sky list came back 120 instead of 121.
        {"date": d, "kind": "note", "text": t, "provenance": "COMPUTED"} for (d, t) in FACTS
    ],
    "centuryFacts": [
        {"from": a, "to": b, "text": t, "provenance": "COMPUTED"} for (a, b, t) in CENTURY_FACTS
    ],
    "projected": [
        {"from": a, "to": b, "text": t, "provenance": "PROJECTED"} for (a, b, t) in PROJECTED
    ],
    "authored": [
        {"date": d, "place": p, "chapter": c, "text": t, "provenance": "AUTHORED", "author": AUTHOR,
         "anchorKind": ANCHOR.get(d, "none"), "anchored": ANCHOR.get(d, "none") != "none"}
        for (d, p, c, t, anchor) in STORY
    ],
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(docs, open(OUT, "w"), indent=1, ensure_ascii=False)
print("wrote", OUT)
print("computed:", docs["counts"]["computed"], "| projected:", docs["counts"]["projected"],
      "| authored:", docs["counts"]["authored"])
