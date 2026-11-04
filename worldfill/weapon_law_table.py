"""
Step 45 part 3 (E9 B): weapon laws — the rows that fill kind 5 of `history/law.json.gz`.

The law register declares **six kinds and populates three**. Kind 5 is `weapons`, and its `gaps`
note says so plainly: *"law codes, weapon laws and caste and class rules are not in this pack
yet."* **237 polities are already there to hang rows on.**

There is no Wikipedia table of weapon laws to scrape, which is why the slot has stayed empty — the
other three kinds are read straight out of three list pages. So these rows are written by hand,
and each names the source it came from.

**The rule this table holds to: a weapon law is a law about a class of person.** Almost none of
them disarm everybody; they disarm *somebody*. The 1181 Assize of Arms requires arms of every
freeman and simultaneously **forbids Jews to keep mail or a breastplate**. The 1878 Indian Arms Act
requires a licence and **exempts Europeans**. The Yuan ban names Han and Southerners. A row that
records the restriction and drops the exemption is not a shorter row, it is a different and wrong
one — the exemption is usually the point of the law.

**And a duty is the opposite of a ban.** Half the rows here *require* people to own weapons. The
Assize of Arms is the ancestor of the militia, not of gun control, and a table that files it under
"restriction" has misread it. So each row says which: `must`, `free`, `licence`, `banned`, or
`banned for a class`.
"""

# A weapon law.
#
#   where    the jurisdiction, as the ruler register names it (build_law joins the name to a
#            polity QID, year-aware, so "Angevin Empire" rather than "England" for 1181)
#   year     when it was made
#   to       the last year it held, or None when it runs on
#   shape    must | free | licence | banned | class — whether the law requires arms, permits
#            them, licences them, forbids them, or forbids them to a named class
#   who      the class the law singles out, or None when it is everyone
#   text     what the law says
#   note     what it meant
#   source   where it came from
#   est      0 recorded, 1 estimated

SHAPES = ["must", "free", "licence", "banned", "class"]

WEAPON_LAWS = [
    # ------------------------------------------------------------------ Rome
    dict(where="Roman Republic", year=-81, to=None, shape="banned", who="everyone inside the pomerium",
         text="Weapons are forbidden within the pomerium, the sacred boundary of the city: no army "
              "may cross it, a magistrate's lictors take the axes out of the fasces on entering it, "
              "and the Praetorian Guard may come in only in civilian dress, as the cohors togata.",
         note="A religious boundary before it is a legal one. Inside is domi, home; outside is "
              "militiae, on campaign. The distinction is why Caesar's killers could not be charged "
              "with sacrilege — they killed him at the Curia of Pompey, which lay just outside it.",
         source="Wikipedia, Pomerium", est=0),

    dict(where="Roman Empire", year=-17, to=None, shape="licence", who="slaves, and armed gangs",
         text="The Lex Julia de Vi forbids possessing weapons for any purpose other than hunting, "
              "self-defence, or while travelling, on pain of exile and forfeiture.",
         note="Augustus's answer to banditry in Italy, and it fell hardest on the slaves who made "
              "up the armed gangs beyond the towns. Ownership was not abolished; carrying was "
              "made a matter of purpose rather than right.",
         source="IMPERIUM ROMANUM, Ancient Rome and the right to own weapons", est=0),

    # ------------------------------------------------------------------ England: a duty, then a curb
    dict(where="Angevin Empire", year=1181, to=1327, shape="must", who="every freeman, but not Jews",
         text="The Assize of Arms requires every freeman to keep arms according to his rank and "
              "his chattels — a knight mail, helmet, shield and lance; every other freeman a "
              "gambeson, an iron cap and a lance — and forbids him to sell them, pledge them, lend "
              "them or alienate them in any way. On his death his arms pass to his heir. Jews may "
              "not keep a coat of mail or a breastplate.",
         note="**The ancestor of the militia, not of gun control.** Henry II revived the old fyrd "
              "duty: the realm is defended by men who arrive already armed. And it has an "
              "exemption in the same breath — the arms a Jew might not keep is the whole point of "
              "the clause.",
         source="Wikipedia, Assize of Arms of 1181; guncite.com, Historical Bases of the Right To "
                "Keep and Bear Arms", est=0),

    dict(where="Kingdom of England", year=1328, to=None, shape="licence", who="everyone but the King's servants",
         text="The Statute of Northampton: no man great nor small, except the King's servants in "
              "his presence and those answering a cry made for arms to keep the peace, may go or "
              "ride armed by night or by day, in fairs, markets, before the justices, or in any "
              "part elsewhere, on pain of forfeiting his armour and imprisonment at the King's "
              "pleasure.",
         note="A curb on *carrying*, not on *keeping* — the two are different laws in every age "
              "and a table that merges them misreads both. The courts read it narrowly for three "
              "centuries: it forbade going armed to terrify, not keeping arms for defence. Then "
              "James II enforced it against anyone at all in Rex v Knight in 1686, which is what "
              "turned it into a disarming statute.",
         source="Wikipedia, Statute of Northampton 1328; William and Mary Law Review", est=0),

    dict(where="Kingdom of England", year=1388, to=None, shape="free", who="servants and labourers",
         text="A statute permits servants and labourers to bear bucklers, swords and daggers in "
              "wartime, or when they travel out of their own shire in the service of their lord.",
         note="The lower orders carrying swords was itself a thing that needed permitting, which "
              "tells you what the century before it had assumed.",
         source="Supreme Court amicus brief Nos. 25-238, 25-566 (2026), citing 12 Rich. 2", est=0),

    dict(where="Kingdom of England", year=1686, to=None, shape="banned", who="anyone but government employees",
         text="Rex v Knight: the Crown enforces the Statute of Northampton against any person, "
              "other than a government employee, carrying a gun.",
         note="Sir John Knight, a Protestant opponent of James II, was tried for walking about "
              "with a gun. The statute that had been read as a curb on terrorising the public "
              "became a general disarmament, and the same year is why the English Bill of Rights "
              "of 1689 says what it says about Protestants' arms.",
         source="University of Michigan Law Review, It Isn't About Duck Hunting", est=0),

    # ------------------------------------------------------------------ Japan
    dict(where="Japan", year=1588, to=1868, shape="banned", who="the non-noble classes",
         text="The Sword Hunt (taiko no katanagari), proclaimed on 29 August: possession of swords "
              "and of firearms is forbidden to the non-noble classes, and weapons are collected.",
         note="Having conquered Japan, Hideyoshi meant to keep it. The sword became the badge of "
              "the samurai and not merely his tool, and a peasant with a spear became a "
              "contradiction in terms. It held for two hundred and eighty years.",
         source="guncite.com, Japanese Gun Control (Kopel); Wikipedia, Toyotomi Hideyoshi", est=0),

    # ------------------------------------------------------------------ China
    dict(where="Yuan Dynasty", year=1281, to=1368, shape="banned", who="Han and Southerners",
         text="Possession of weapons by Han and Southerner civilians is illegal; they may not "
              "hunt, nor gather in large numbers, nor go abroad at night.",
         note="A Mongol minority ruling a Han majority, and the weapon ban is the sharpest edge "
              "of a graded social order in which the Southerners are the lowest of four classes.",
         source="Wikipedia, Yuan dynasty", est=0),

    dict(where="Qing Dynasty", year=1644, to=1649, shape="banned", who="the general population",
         text="On the conquest, the population is forbidden to own weapons; the ban is lifted in "
              "1649 and the confiscated weapons are returned.",
         note="**The popular story is false and the correction matters**: the Qing did not ban "
              "martial arts, and the weapons ban lasted five years, not the whole dynasty. The "
              "lesson the Qing drew from it was the opposite of the one a censor would draw — "
              "only the law-abiding had handed their guns in, while the outlaws kept theirs, so "
              "later Qing law permitted ownership.",
         source="AskHistorians, Martial arts prohibition during the Qing dynasty (wotan_weevil)",
         est=0),

    dict(where="Qing Dynasty", year=1910, to=1912, shape="licence", who="ordinary individuals",
         text="The new criminal law loosens the state's grip: any ordinary individual may own "
              "either a bird gun or a foreign gun for self-defence, provided it is registered.",
         note="The Great Qing Code had prohibited civilians carrying firearms outright, and the "
              "1910 revision — the dynasty's last — reversed it. Then the dynasty ended.",
         source="Wang, Between Social Control and Popular Power: private guns in the mid to late "
                "Qing, 1781-1911 (American Journal of Chinese Studies 25, 2017)", est=0),

    dict(where="People's Republic of China", year=1957, to=1996, shape="banned", who="the public",
         text="The Act of 22 October 1957 forbids the public to manufacture, repair, buy or "
              "possess firearms or ammunition.",
         note="On the eve of the Great Leap Forward.",
         source="theacru.org, via Jared Weisinger, Mao's Gun Control Policies", est=0),

    dict(where="People's Republic of China", year=1996, to=None, shape="banned", who="individuals and organisations",
         text="The Law of the People's Republic of China on Control of Guns, passed 5 July and in "
              "force from 1 October, forbids all individuals and organisations to possess, "
              "manufacture, buy, sell, transport or lend firearms outside its provisions.",
         note="Framed as state security and public order; there is no right to bear arms and the "
              "state treats civilian disarmament as a public good.",
         source="National People's Congress, Law on Control of Guns (1996)", est=0),

    # ------------------------------------------------------------------ British India
    dict(where="British Raj", year=1878, to=1947, shape="licence", who="Indians, but not Europeans",
         text="The Indian Arms Act requires a licence to own, make, sell or carry arms, and "
              "**exempts Europeans**.",
         note="Eleven years after the rebellion of 1857, and the exemption is the whole of it: a "
              "law to disarm the governed and not the governors. Every decade of the Raj "
              "afterwards produced a new usury or arms law, and none of them bit.",
         source="Indian Arms Act 1878, via iasgyan.in; WEAPONS_RESEARCH.md [L1]", est=0),
]


def problems():
    """Checks, so a bad row cannot ship silently."""
    out = []
    for r in WEAPON_LAWS:
        i = "%s %s" % (r["where"], r["year"])
        if r["shape"] not in SHAPES:
            out.append("%s: unknown shape '%s'" % (i, r["shape"]))
        if not r.get("text") or len(r["text"]) < 40:
            out.append("%s: text too short" % i)
        if not r.get("note"):
            out.append("%s: no note" % i)
        if not r.get("source"):
            out.append("%s: no source" % i)
        if r["to"] is not None and r["to"] < r["year"]:
            out.append("%s: ends before it begins" % i)
        # a law about a class must name the class, or the exemption is lost
        if r["shape"] in ("banned", "class") and not r.get("who"):
            out.append("%s: forbids but names nobody" % i)
        if r["shape"] == "must" and "not require" not in r["text"] and not r.get("who"):
            out.append("%s: requires arms but says of whom" % i)
    return out


if __name__ == "__main__":
    from collections import Counter
    ps = problems()
    print("weapon laws: %d rows" % len(WEAPON_LAWS))
    print("  by shape:", dict(Counter(r["shape"] for r in WEAPON_LAWS)))
    for r in WEAPON_LAWS:
        print("   %-24s %-6s %-8s %s" % (r["where"], r["year"], r["shape"], (r["who"] or "everyone")))
    for p in ps:
        print("  PROBLEM " + p)
    print("weapon_law_table: %d problem(s)" % len(ps))
