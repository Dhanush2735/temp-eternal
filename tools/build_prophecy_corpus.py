#!/usr/bin/env python3
"""One corpus of *dated* predictions from many sources, scored against the historical record.

2026-10-27. Everything here follows four rules, written down before the scoring was run:

1. A claim only enters the corpus if it names a date or a bounded date range. Vague verse is recorded but
   marked UNJUDGEABLE, so it cannot pad a source's score either way.
2. `textYear` is when the claim was written, `claimYear` is the date it names. lead = claimYear - textYear.
   A negative lead means the "prophecy" was written after the event: a postdiction, not a prediction.
3. Verdicts: HIT (the named thing verifiably happened), MISS (the named date passed and it verifiably did
   not), PARTIAL, OPEN (date after 2026), UNJUDGEABLE (no checkable criterion).
4. No verdict of HIT is given to a claim whose words could fit any event. Popular "fulfilments" of vague
   verse are recorded as UNJUDGEABLE and flagged, not counted as hits.
"""
import json, os
from collections import Counter, defaultdict

OUT = "/home/user/testrun/verify/prophecy_corpus.json"

W = "https://en.wikipedia.org/wiki/"
LIST = W + "List_of_dates_predicted_for_apocalyptic_events"

# id, source, claimant, textYear, claimYear (float; negative = BCE), kind, claim, verdict, evidence, url, note
C = []


def add(cid, source, claimant, textYear, claimYear, claim, verdict, evidence, url, kind="future",
        note="", postdiction=False, grade="A"):
    C.append({"id": cid, "source": source, "claimant": claimant, "textYear": textYear,
              "claimYear": claimYear, "kind": kind, "claim": claim, "verdict": verdict,
              "evidence": evidence, "url": url, "note": note, "postdiction": postdiction,
              "grade": grade})


# ---------------------------------------------------------------- scripture and ancient
add("dan-1", "Book of Daniel", "anonymous (Maccabean author)", -165, -164,
    "Seventy weeks of years (490 years) from the rebuilding of Jerusalem to an anointed one cut off, then "
    "a desolating abomination.", "HIT (postdiction)",
    "Maps closely onto Antiochus IV, the Maccabean revolt and the rededication of the Temple in 164 BCE - "
    "which is the era the book was written in.",
    W + "Book_of_Daniel", note="The classic case: accurate because it is history written as prophecy.",
    postdiction=True)
add("kali-1", "Hindu Puranic chronology", "Puranas", 500, -3102,
    "The Kali Yuga began on 18 February 3102 BCE and will last 432,000 years, ending about 428,899 CE.",
    "MISS (as a date)",
    "No archaeological or astronomical evidence for a world-age boundary at 3102 BCE; the date is a "
    "later computation, not a record.", W + "Kali_Yuga", kind="past", grade="B",
    note="A claim about the past, testable against the record - and it does not match it.")
add("rev-1", "Book of Revelation", "John of Patmos", 95, 95,
    "A reign of 1,260 days, then the millennium.", "UNJUDGEABLE",
    "No fixed date; the numbers have been applied to every century since.", W + "Book_of_Revelation",
    grade="C")

# ---------------------------------------------------------------- medieval
add("roq-1", "Jean de Roquetaillade", "Jean de Roquetaillade", 1350, 1366,
    "The Antichrist comes in 1366; the Millennium begins in 1368 or 1370.", "MISS",
    "No Antichrist; no millennium.", LIST, grade="A")
add("vil-1", "Arnaldus de Villa Nova", "Arnaldus de Villa Nova", 1300, 1378,
    "The Antichrist comes during this year.", "MISS", "No Antichrist.", LIST)
add("rus-1", "Russian Orthodox millenarians", "Russian Orthodox clergy", 1400, 1492,
    "The world ends in 1492 (year 7000 of the Byzantine calendar).", "MISS",
    "The Russian Church stopped computing Easter past 1491 in expectation; the year passed normally.", LIST)
add("bot-1", "Sandro Botticelli", "Sandro Botticelli", 1500, 1504,
    "The Millennium begins three and a half years after 1500.", "MISS",
    "He painted the claim into The Mystical Nativity; nothing happened.", LIST, grade="B")
add("lon-1", "London astrologers", "a group of London astrologers", 1523, 1524,
    "A flood destroys London on 1 February 1524.", "MISS",
    "20,000 Londoners fled to high ground; the day passed with no flood.", LIST)
add("stof-1", "Johannes Stöffler", "Johannes Stöffler", 1524, 1524,
    "A planetary alignment in Pisces on 20 February 1524 begins the Millennium.", "MISS",
    "Nothing happened; Stöffler recalculated to 1528.", LIST)
add("mun-1", "Thomas Müntzer", "Thomas Müntzer", 1524, 1525,
    "The Millennium begins in 1525.", "MISS",
    "His followers were destroyed at Frankenhausen; he was executed.", LIST)
add("hut-1", "Hans Hut", "Hans Hut", 1527, 1528,
    "The end comes on 27 May 1528.", "MISS", "The day passed.", LIST)
add("sti-1", "Michael Stifel", "Michael Stifel", 1533, 1533,
    "Judgement Day begins at 8 am on 19 October 1533.", "MISS",
    "The hour passed; Stifel was ridiculed and imprisoned.", LIST)
add("mat-1", "Jan Matthys", "Jan Matthys", 1534, 1534,
    "The apocalypse comes on 5 April 1534 at Münster.", "MISS",
    "He led a failed sortie that day and was killed.", LIST)
add("ser-1", "Michael Servetus", "Michael Servetus", 1553, 1585,
    "The Devil's 1,260-year reign, begun at Nicaea in 325, ends in 1585.", "MISS",
    "The year passed.", LIST)
add("reg-1", "Regiomontanus", "Regiomontanus", 1475, 1588,
    "The world ends in 1588.", "MISS",
    "The Spanish Armada year passed with no end of the world.", LIST)
add("lut-1", "Martin Luther", "Martin Luther", 1530, 1600,
    "The end comes no later than 1600.", "MISS", "The year passed.", LIST)
add("lon-2", "London astrologers", "the same astrologers", 1590, 1624,
    "The flood of 1524, recalculated a century later: 1 February 1624.", "MISS",
    "The date was moved after the first failure; the second failed too.", LIST, grade="A",
    note="Recalculation, not a new prediction.")
add("sab-1", "Sabbatai Zevi", "Sabbatai Zevi", 1648, 1648,
    "The Messiah comes in 1648.", "MISS", "He later moved the date to 1666.", LIST)
add("sab-2", "Sabbatai Zevi", "Sabbatai Zevi and followers", 1648, 1666,
    "The Messiah comes, and the world is redeemed, in 1666.", "MISS",
    "1666 passed; Zevi converted to Islam under Ottoman pressure.", LIST)

# ---------------------------------------------------------------- 19th century
add("mil-1", "William Miller", "William Miller", 1831, 1843,
    "Christ returns between 21 March 1843 and 21 March 1844.", "MISS",
    "The window closed; the date moved to 22 October 1844.", W + "Great_Disappointment")
add("mil-2", "William Miller", "William Miller", 1831, 1844,
    "Christ returns on 22 October 1844.", "MISS",
    "The Great Disappointment: nothing happened; the movement split and reinterpreted the date.",
    W + "Great_Disappointment", note="Recalculation of a failed date.")
add("shi-1", "Mother Shipton", "attrib. Ursula Southeil", 1862, 1881,
    "The world ends in 1881.", "MISS",
    "The year passed; later editions moved the date to 1991. The 1881 line is a Victorian addition to a "
    "text that was itself heavily rewritten.", W + "Mother_Shipton", grade="B",
    note="Textual history is disputed; the prophecy is not in the earliest printed versions.")

# ---------------------------------------------------------------- 20th century
add("jw-1", "Jehovah's Witnesses", "Charles Taze Russell", 1879, 1914,
    "God's kingdom begins in 1914, with the end of the Gentile times.", "MISS",
    "1914 came; the movement reinterpreted it as an invisible heavenly enthronement rather than a visible "
    "end.", W + "Eschatology_of_Jehovah%27s_Witnesses", note="Reinterpreted after the fact, not withdrawn.")
add("jw-2", "Jehovah's Witnesses", "Joseph Franklin Rutherford", 1920, 1925,
    "The resurrection of the patriarchs and the Millennium arrive in 1925.", "MISS",
    "1925 passed; the expected figures did not appear.", W + "Eschatology_of_Jehovah%27s_Witnesses")
add("jw-3", "Jehovah's Witnesses", "Frederick Franz / movement expectation", 1966, 1975,
    "The end of the present system arrives in 1975 (implied by 6,000 years of human history).", "MISS",
    "1975 passed; the movement later said no date had been set.", W + "Eschatology_of_Jehovah%27s_Witnesses",
    grade="B", note="Implication rather than an official date - recorded with that caveat.")
add("cay-1", "Edgar Cayce", "Edgar Cayce", 1940, 1968,
    "Atlantis will rise again near Bimini in 1968 or 1969.", "MISS",
    "The Bimini Road was found in 1968 and is natural beachrock; no Atlantis rose.",
    W + "Edgar_Cayce", grade="B")
add("jup-1", "The Jupiter Effect", "John Gribbin and Stephen Plagemann", 1974, 1982,
    "A planetary alignment on 10 March 1982 triggers a great Los Angeles earthquake.", "MISS",
    "No such earthquake; the authors later disowned the prediction.",
    W + "The_Jupiter_Effect")
add("lin-1", "Hal Lindsey", "Hal Lindsey", 1970, 1988,
    "The generation alive in 1948 will not pass before the end: the year 1988 is indicated.", "MISS",
    "1988 passed; Lindsey moved the horizon without withdrawing the method.", W + "Hal_Lindsey", grade="B")
add("whi-1", "Edgar Whisenant", "Edgar C. Whisenant", 1988, 1988,
    "The rapture comes on 11, 12 or 13 September 1988.", "MISS",
    "Nothing happened, in three days running.", LIST, grade="B")
add("cam-1", "Harold Camping", "Harold Camping", 1992, 1994,
    "Christ returns in 1994.", "MISS", "The year passed; a new date was calculated.", W + "Harold_Camping")
add("nos-1", "Nostradamus", "Michel de Nostredame", 1555, 1999,
    "In the year 1999 and seven months a great king of terror comes from the sky (Century X, quatrain 72).",
    "UNJUDGEABLE",
    "Nothing identifiable happened in July 1999; the words fit no specific event, and every later reading "
    "is an interpretation.", W + "Les_Proph%C3%A9ties", grade="C",
    note="The most-quoted dated quatrain in the corpus; still not checkable.")

# ---------------------------------------------------------------- 21st century
add("cam-2", "Harold Camping", "Harold Camping", 2010, 2011,
    "The rapture comes on 21 May 2011, and the world ends on 21 October 2011.", "MISS",
    "Both dates passed; Camping said the end had come 'spiritually' and then retired from prediction.",
    W + "2011_end_times_prediction", note="Two dates; both recorded as one claim.")
add("may-1", "Maya Long Count", "Classic Maya calendar (read by modern interpreters)", 700, 2012,
    "The 13th bak'tun ends on 21 December 2012, ending the world.", "MISS",
    "The Long Count rolled over; no Maya source says the world ends. 21 December 2012 passed.",
    W + "2012_phenomenon", grade="B",
    note="The claim belongs to modern interpreters, not to the surviving Maya texts.")
add("van-1", "Baba Vanga", "Vanga (attrib.)", 1980, 2025,
    "A great war begins in Europe in 2025, and the world's population falls sharply.", "MISS",
    "2025 passed without the described war. The 'predictions' are tabloid reconstructions after her death.",
    W + "Baba_Vanga", grade="D",
    note="Grade D: no verifiable written source in her own hand for the dated claims.")

# ---------------------------------------------------------------- open (after 2026)
add("new-1", "Isaac Newton", "Isaac Newton", 1704, 2060,
    "The world will end no earlier than 2060, by his reading of Daniel.", "OPEN",
    "Not yet due.", W + "Isaac_Newton%27s_occult_studies", kind="future", grade="B")
add("heb-1", "Jewish apocalyptic reckoning", "Talmudic tradition (Sanhedrin)", 500, 2240,
    "The Messiah must come by the year 6000 of the Hebrew calendar (about 2240 CE).", "OPEN", "Not yet due.",
    W + "Year_6000", grade="B")
add("kal-f1", "Kalagnanam", "Potuluri Veerabrahmendra Swamy (attrib.)", 1650, 2027,
    "An eclipse on 2 August 2027; a comet for 33 days; the earth's axis shifts.", "OPEN", "Not yet due.",
    "https://www.panchamahakalagnanamulu.org/Sri%20Potuluri%20Veera%20Brahmendra%20Swami%20Kalagnanam.html",
    grade="A", note="Date printed by a 20th/21st-century commentator, not in the palm leaf.")
add("kal-f2", "Kalagnanam", "Potuluri Veerabrahmendra Swamy (attrib.)", 1650, 2039,
    "A devastating earthquake at Addanki between 24 May and 21 June 2039.", "OPEN", "Not yet due.",
    "https://www.panchamahakalagnanamulu.org/Sri%20Potuluri%20Veera%20Brahmendra%20Swami%20Kalagnanam.html",
    grade="A")
add("kal-f3", "Kalagnanam", "Potuluri Veerabrahmendra Swamy (attrib.)", 1650, 2045,
    "The War of Wars begins between 19 January and 16 February 2045.", "OPEN", "Not yet due.",
    "https://www.panchamahakalagnanamulu.org/Sri%20Potuluri%20Veera%20Brahmendra%20Swami%20Kalagnanam.html",
    grade="A")
add("kal-f4", "Kalagnanam", "Potuluri Veerabrahmendra Swamy (attrib.)", 1650, 2058,
    "Every country surrenders its sovereignty to the king-avatar on 3 February 2058.", "OPEN", "Not yet due.",
    "https://www.panchamahakalagnanamulu.org/Sri%20Potuluri%20Veera%20Brahmendra%20Swami%20Kalagnanam.html",
    grade="A")
add("kal-p1", "Kalagnanam", "Potuluri Veerabrahmendra Swamy (attrib.)", 1650, 2009,
    "The king-avatar begins destroying evil on earth on 9 September 2009.", "MISS", "No such event.",
    "https://www.panchamahakalagnanamulu.org/Sri%20Potuluri%20Veera%20Brahmendra%20Swami%20Kalagnanam.html")
add("kal-p2", "Kalagnanam", "Potuluri Veerabrahmendra Swamy (attrib.)", 1650, 2011,
    "The king-avatar is crowned at noon on 26 December 2011 as an ordinary ruler.", "MISS",
    "No such coronation is recorded.",
    "https://www.panchamahakalagnanamulu.org/Sri%20Potuluri%20Veera%20Brahmendra%20Swami%20Kalagnanam.html")
add("kal-p3", "Kalagnanam", "Potuluri Veerabrahmendra Swamy (attrib.)", 1650, 2024,
    "New Delhi is bombed, the capital moves to Anegondi, and the Nellore region is submerged (2024-25).",
    "MISS", "None of it happened.",
    "https://www.panchamahakalagnanamulu.org/Sri%20Potuluri%20Veera%20Brahmendra%20Swami%20Kalagnanam.html")
add("kal-p4", "Kalagnanam", "Potuluri Veerabrahmendra Swamy (attrib.)", 1650, 2025,
    "A Third World War is under way; the world's population falls to a seventh.", "MISS", "It is not.",
    "https://www.panchamahakalagnanamulu.org/Sri%20Potuluri%20Veera%20Brahmendra%20Swami%20Kalagnanam.html")
add("kal-h1", "Kalagnanam", "readers of the text", 1970, 1757,
    "'Fair-faced people from a white island' will rule the land for a long time - read as British rule.",
    "UNJUDGEABLE",
    "The words fit any sea-borne conqueror; the identification was made by 20th-century readers, after the "
    "event. Not counted as a hit.", W + "Kalagnanam", kind="past", grade="C",
    note="The most-cited 'fulfilled' prophecy of the text, and the weakest kind of evidence.")
add("pop-1", "Prophecy of the Popes", "attrib. Malachy of Armagh", 1140, 2026,
    "112 mottoes describe the popes in order, ending with 'Peter the Roman', after whom Rome is destroyed.",
    "UNJUDGEABLE",
    "The list was published in 1595; its 'successes' cluster before that date and its later mottoes are "
    "generic. Not a usable dated prediction.", W + "Prophecy_of_the_Popes", grade="C")
add("tui-1", "Tui Bei Tu", "attrib. Li Chunfeng and Yuan Tiangang", 700, 3000,
    "Sixty poems describe the dynasties and upheavals of China in order.", "UNJUDGEABLE",
    "No dates; the identifications are made after the fact, poem by poem.",
    W + "Tui_bei_tu", grade="C")

doc = {
    "id": "eternal-prophecy-corpus",
    "format": 1,
    "title": "Dated predictions from many sources, scored against the historical record",
    "built": "2026-10-27",
    "rules": [
        "A claim enters only if it names a date or a bounded date range.",
        "textYear = when the claim was written; claimYear = the date it names; lead = claimYear - textYear.",
        "A negative lead makes it a postdiction, not a prediction.",
        "HIT requires that the named thing verifiably happened; vague words that could fit anything are "
        "UNJUDGEABLE, whatever their popularity.",
        "Verdicts: HIT, HIT (postdiction), PARTIAL, MISS, OPEN, UNJUDGEABLE.",
    ],
    "fields": ["id", "source", "claimant", "textYear", "claimYear", "kind", "claim", "verdict", "evidence",
               "url", "note", "postdiction", "grade"],
    "count": len(C),
    "claims": C,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(doc, open(OUT, "w"), indent=1, ensure_ascii=False)
print("wrote", OUT, "|", len(C), "claims |", len({c["source"] for c in C}), "sources")
print("verdicts:", dict(Counter(c["verdict"] for c in C)))
