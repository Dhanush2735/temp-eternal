#!/usr/bin/env python3
"""Build the declared-futures dataset from Kalagnanam (R2-c pilot), 2026-10-27.

Every item records the year it claims, the place it names, and - the important part - the *basis* for
the date and a grade for how firm it is:

    A  the commentator prints a Gregorian date outright (day and month)
    B  the commentator prints a Telugu year name, which is a one-year Gregorian window
    C  no date at all: sequence only ("after this, then that")

Nothing here is a record. The palm-leaf text carries no Gregorian dates; every date below is a
commentator's conversion (Pavuluri Sreenivasachary, "2012 and beyond"). Items whose year has already
passed without the event are kept in a separate list, because a source's near-term track record is the
single most useful fact about it.
"""
import json, os

OUT = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/prophecies.json"
CSV = "/home/user/testrun/verify/kalagnanam_futures.csv"

PANCHA = "https://www.panchamahakalagnanamulu.org/Sri%20Potuluri%20Veera%20Brahmendra%20Swami%20Kalagnanam.html"
PANCHA2 = "https://www.panchamahakalagnanamulu.org/"          # the commentary site as a whole
BLOG = "http://2012latestpredictions-bhaskarganesh.blogspot.com/p/kaalajnam-part-2.html"
WIKI = "https://en.wikipedia.org/wiki/Kalagnanam"

# place -> (lat, lon)
P = {
    "Hyderabad": (17.385, 78.486),
    "Golconda": (17.383, 78.401),
    "Vijayawada": (16.507, 80.648),
    "Kanchipuram": (12.834, 79.703),
    "Varanasi (Kasi)": (25.318, 82.973),
    "Tirumala": (13.683, 79.347),
    "Srisailam": (16.074, 78.868),
    "Yaganti": (15.283, 78.283),
    "Banaganapalle": (15.317, 78.228),
    "Kandimallayapalle": (15.316, 78.233),
    "Hampi": (15.335, 76.460),
    "Anegondi": (15.352, 76.477),
    "Chennai": (13.082, 80.275),
    "Kumbakonam": (10.961, 79.388),
    "Rameshwaram": (9.288, 79.317),
    "Addanki": (15.810, 79.970),
    "Nellore": (14.442, 79.986),
    "Tirunelveli": (8.714, 77.756),
    "Kurnool": (15.828, 78.037),
    "Delhi": (28.614, 77.209),
    "Mumbai": (19.076, 72.877),
    "Bengal": (23.810, 90.412),
    "Mecca": (21.389, 39.857),
}

WORLD = ("world", 0.0, 0.0, 0)


def item(i, text, start, end, month, day, place, scope, grade, basis, verse="", url=PANCHA):
    if scope == "world":
        lat, lon, radius = 0.0, 0.0, 0
    else:
        lat, lon = P[place]
        radius = 120
    return {
        "id": "kalagnanam-%02d" % i,
        "whatWasForetold": text,
        "start": start,
        "end": end,
        "month": month,
        "day": day,
        "place": place,
        "scope": scope,
        "lat": lat,
        "lon": lon,
        "radiusKm": radius,
        "grade": grade,
        "basis": basis,
        "verse": verse,
        "saidBy": "Potuluri Veerabrahmendra Swamy (attrib.), Kalagnanam",
        "asReadBy": "Pavuluri Sreenivasachary, '2012 and beyond' (English), panchamahakalagnanamulu.org",
        "sourceUrl": url,
        "kind": "prophecy",
    }


A = "Gregorian date printed by the commentator"
B = "Telugu year name printed by the commentator; converted to a one-year window"
C = "no date in the text: sequence only"

items = [
    item(1, "A solar eclipse in which a male shadow-shape is seen in the Sun; a comet is visible for 33 days; "
            "the earth's axis and motion change.", 2027, 2027, 8, 2, "", "world", "A",
         A, verse="Kalagnanam, on the comet and the eclipse of 02.08.2027"),
    item(2, "The motion of Jupiter changes after this year; droughts and irregular rains follow.",
         2027, 2028, 0, 0, "", "world", "B", B + " (Plavanga 2027-28)"),
    item(3, "War and bloodshed on the field of battle; a year of great slaughter.",
         2034, 2035, 0, 0, "", "world", "B", B + " (Ananda 2034-35)",
         verse="Prabhava Paarthiva madhye bahu pralaya nischayam / Ananthare Ananda madhye raktapaathau "
               "ranaranga bhoome bheebhitsau prapancha sthitih"),
    item(4, "From this year Jupiter passes through three signs in a single year.", 2034, 3000, 0, 0, "", "world",
         "B", B, verse="change of velocity of the planets foretold before the end of the age"),
    item(5, "The awaited king-avatar shows his universal form and declares his mission.", 2035, 2035, 3, 15, "",
         "world", "A", A),
    item(6, "The king-avatar moves out with his army for the final war.", 2035, 2035, 3, 30, "", "world", "A", A),
    item(7, "Destruction falls on the western countries.", 2035, 2036, 0, 0, "", "world", "B",
         B + " (Rakshasa 2035-36)"),
    item(8, "On Ashada full moon the palm-leaf Kalagnanam itself is dug out of its pit and read; from then on "
            "nothing in it can be changed.", 2036, 2036, 6, 7, "Kandimallayapalle", "place", "A",
         A + " (Nala 2036-37, 7/8 June 2036)"),
    item(9, "Severe clashes between two religions kill in crores across the world.", 2037, 2038, 0, 0, "", "world",
         "B", B + " (Pingala 2037-38)"),
    item(10, "The same religious war continues; a comet appears in Bhadrapada month.", 2038, 2039, 0, 0, "", "world",
          "B", B + " (Kalayukti 2038-39)"),
    item(11, "A devastating earthquake strikes Addanki and the country around it.",
          2039, 2039, 5, 24, "Addanki", "place", "A", A + " (24/05/2039 to 21/06/2039)"),
    item(12, "The Ganga runs dry at Kasi for forty days.", 2040, 2040, 0, 0, "Varanasi (Kasi)", "place", "B",
          B + " (by 2040)"),
    item(13, "Religious clashes continue and crores die; seven crores die on one day in Makha full moon.",
          2040, 2041, 2, 15, "", "world", "A", A + " (15/16 February 2041, Roudri 2040-41)"),
    item(14, "In Chennai a seven-year-old girl gives birth to a four-armed child, who lives 22 days and on the "
             "23rd declares the War of Wars.", 2044, 2044, 11, 26, "Chennai", "place", "A",
          A + " (26/27-11-2044, Margasira Suddha Saptami)"),
    item(15, "The War of Wars begins: the king-avatar's forces against the evil king Kali.",
          2045, 2045, 1, 19, "", "world", "A", A + " (19/01/2045 to 16/02/2045)"),
    item(16, "The aftermath of the War of Wars runs on.", 2045, 2061, 0, 0, "", "world", "B",
          B + " (commentator: aftermath to 2061)"),
    item(17, "Many rivers flood at once and many cities are submerged.", 2054, 2055, 8, 26, "", "world", "A",
          A + " (26/08/2054, Bhava 2054-55)"),
    item(18, "At a festival on a Sunday, lakhs are drowned by flash floods at Tirunelveli.",
          2055, 2055, 7, 0, "Tirunelveli", "place", "B", B + " (July/August 2055)"),
    item(19, "Only 25 gothras of the Vysya community are left.", 2056, 2057, 0, 0, "", "world", "B",
          B + " (Dhata 2056-57)"),
    item(20, "Every country surrenders its sovereignty to the king-avatar.", 2058, 2058, 2, 3, "", "world", "A",
          A + " (03.02.2058, Magha Suddha Dasami, Eswara)"),
    item(21, "The final phase of the Kali Yuga begins.", 2058, 3000, 2, 3, "", "world", "A",
          A + " (03.02.2058, Abhibhu yuga)", verse="kaliyuga avasaanayuga begins"),
    item(22, "Bloodbath in twenty-five cities, with calamities.", 2058, 2059, 0, 0, "", "world", "B",
          B + " (Bahudhanya 2058-59)"),
    item(23, "The king-avatar rules the whole world for 108 years.", 2058, 2166, 0, 0, "", "world", "B",
          B + " (counted from 03.02.2058)"),
    item(24, "His descendants rule after him for about a thousand years.", 2166, 3166, 0, 0, "", "world", "C", C,
          verse="his descendants about 1000 years"),
    item(25, "Calendars and the reckoning of time change at the end of the age.", 2058, 3000, 0, 0, "", "world",
          "C", C),
    item(26, "A neem tree north of Kurnool is worshipped for a month, then gives off a poisonous gas that kills "
             "thousands.", 2065, 2066, 0, 0, "Kurnool", "place", "B", B + " (Parthiva 2065-66)"),
    item(27, "The calamities of the age come to an end.", 2066, 2066, 0, 0, "", "world", "B",
          B + " (commentator: calamities to 2066)"),
]

# Claims whose year has already gone by, kept deliberately: this is the source's track record.
failed = [
    ("The king-avatar is crowned at noon as an ordinary ruler.", 2011, 12, 26,
     "No such coronation is recorded."),
    ("The avatar begins destroying evil on earth.", 2009, 9, 9, "No such event."),
    ("India is attacked; New Delhi is bombed and the capital moves to Anegondi; the Nellore region is "
     "submerged.", 2024, 0, 0, "Did not happen."),
    ("Severe nuclear or terrorist strikes on defence and nuclear establishments around Hyderabad.",
         2024, 0, 0, "Did not happen."),
    ("A Third World War is under way and the world's population falls to a seventh.",
         2025, 0, 0, "Did not happen."),
]

doc = {
    "id": "eternal-prophecies-kalagnanam",
    "format": 1,
    "title": "Declared futures: Kalagnanam (R2-c pilot)",
    "source": "Kalagnanam, a Telugu book of prophecy attributed to Potuluri Veerabrahmendra Swamy "
              "(16th-17th century), as read and translated by Pavuluri Sreenivasachary, '2012 and beyond'",
    "sourceUrl": PANCHA,
    "alsoSeenAt": [WIKI, BLOG],
    "rule": "A prophecy is never a record. The engine may show an item only in the years it claims, only "
            "with the words 'as foretold', and never as news, never as history, never as fact. An item "
            "whose year has passed without the event is not reprinted as if it were still coming: it goes "
            "to the pastClaims list, which is the source's track record.",
    "grades": {
        "A": A,
        "B": B,
        "C": C,
    },
    "fields": ["id", "whatWasForetold", "start", "end", "month", "day", "place", "scope", "lat", "lon",
               "radiusKm", "grade", "basis", "verse", "saidBy", "asReadBy", "sourceUrl", "kind"],
    "count": len(items),
    "items": items,
    "pastClaims": [{"whatWasForetold": t, "year": y, "month": m, "day": d, "outcome": o}
                   for (t, y, m, d, o) in failed],
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(doc, f, indent=1, ensure_ascii=False)
    f.write("\n")

with open(CSV, "w") as f:
    f.write("id,start,end,month,day,grade,scope,place,whatWasForetold,basis\n")
    for it in items:
        f.write('%s,%d,%d,%d,%d,%s,%s,%s,"%s","%s"\n' % (
            it["id"], it["start"], it["end"], it["month"], it["day"], it["grade"], it["scope"],
            it["place"] or "-", it["whatWasForetold"].replace('"', "'"), it["basis"]))

from collections import Counter
print("wrote", OUT)
print("items:", len(items), "| grades:", dict(Counter(i["grade"] for i in items)))
print("span:", min(i["start"] for i in items), "to", max(i["end"] for i in items))
print("dated to the day:", sum(1 for i in items if i["day"]))
print("csv:", CSV)
