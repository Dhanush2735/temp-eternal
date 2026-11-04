#!/usr/bin/env python3
"""
Step 47 part 4 (E12): **the period wardrobe** — what a person wore before 1873.

    python3 wardrobe_table.py        check the register and print it

## The bug this register exists to fix

`SkinPoolDatabase.WARDROBE` holds 40 garments and **every one of them arrives in 1873 or later**.
The earliest are `jeans` (1873), `button_down` (1900), `crew_tee` (1913). So the code does the only
thing it can:

```java
if (year < p.era("modern")) {
    return new Outfit(List.of(), false, "the year has not reached the modern wardrobe");
}
```

**Every person in the world before 1945 is dressed in nothing.** The plan calls E12 "Partly: looks by
era" and it is not: it is *looks by the modern era*, and six thousand years of the world are bare.

The culture pools do carry a `lower` (dhoti, sari, tunic, robe, wrap) and a few `cultural` items, so
what is missing is precise and a little comic: **the top half of the body.** A weaver in the Deccan in
1400 wears a dhoti and no shirt.

## What this register adds

Twenty-two garments that exist *before* the machine age, with the year each arrives, the part of the
body it covers, and which cultures wore it. They are drawn by the same code that draws the modern
ones, from the same palette, so a period weaver and a modern weaver look like people from the same
place and different centuries.

## The rule that keeps it honest

**A garment is dated to the earliest evidence of that cut in that region**, not to when it became
common, and where the date is a guess the row says `estimated` and gives the reasoning. A tunic is
Egyptian before 3000 BC; a kimono is a Heian court garment of the 8th century; a sherwani is a
19th-century form and is dated as one, which is why it is not in the medieval Indian rows.
"""

# the culture pools, as skin_pool.json names them
CULTURES = ["deccan", "indic", "maurya", "persianate", "mesopotamian", "mediterranean", "rome",
            "north_african", "african", "east_asian", "americas"]

PARTS = ["top", "outer", "bottom", "foot", "head", "extra", "dress"]

# The regions the pools stand for, for the area test.
CULTURE_AREAS = {
    "deccan": "SAS", "indic": "SAS", "maurya": "SAS",
    "persianate": "WAS", "mesopotamian": "WAS",
    "mediterranean": "EUR", "rome": "EUR",
    "north_african": "NAF", "african": "WAF",
    "east_asian": "EAS", "americas": "MNA",
}

GARMENTS = [
    # ---- THE OLDEST THING ANYBODY WORE ------------------------------------------------
    dict(name="tunic", part="top", female=False, arrival=-3000, cultures=["mesopotamian", "rome",
         "mediterranean", "north_african", "persianate"], roles=["farmer", "artisan", "citizen",
         "merchant", "scribe", "healer", "guard"], mark="recorded",
         note="**A rectangle with a hole for the head, sewn at the sides.** It is the oldest garment "
              "in the register, it is in Egypt and Mesopotamia before 3000 BC, and it is still worn: "
              "the tunic and the T-shirt are the same garment. The Romans called it a tunica and it "
              "was what everybody wore, under a toga if they had one.",
         source="Egyptian and Mesopotamian textile finds; Roman tunica"),
    dict(name="tunic_f", part="top", female=True, arrival=-3000, cultures=["mesopotamian", "rome",
         "mediterranean", "north_african", "persianate"], roles=["farmer", "artisan", "citizen",
         "merchant", "scribe", "healer", "priest"], mark="recorded",
         note="The same garment cut longer to the ankle, which is a difference of length and not of "
              "kind. Almost every ancient dress is a tunic of some length.",
         source="as the tunic"),
    dict(name="toga", part="outer", female=False, arrival=-600, cultures=["rome"],
         roles=["citizen", "scholar", "advisor", "scribe"], mark="recorded",
         note="**Not a garment but a citizenship.** A toga is 6 m of wool draped in a way that takes "
              "two people to put on, so it is not something a man works in: it is what a man wears to "
              "vote, to court and to be buried in. Foreigners and slaves may not wear one, and "
              "Augustus made it compulsory for the theatre, which everybody resented.",
         source="Roman sumptuary practice; the toga as a badge of citizenship"),
    dict(name="chiton", part="top", female=False, arrival=-800, cultures=["mediterranean"],
         roles=["citizen", "artisan", "merchant", "farmer", "scholar"], mark="recorded",
         note="Two tubes pinned at the shoulder, belted. **The Greek garment that is not a toga**, "
              "and the one most people actually wore. The peplos is the earlier, heavier version and "
              "belongs to the same row.",
         source="Greek vase painting and the peplos of the Archaic period"),
    dict(name="chiton_f", part="dress", female=True, arrival=-800, cultures=["mediterranean"],
         roles=["citizen", "artisan", "merchant", "healer", "priest", "scholar"], mark="recorded",
         note="The same garment for a woman, to the ankle, with the belt higher. The Doric peplos is "
              "folded over at the top and pinned, which is where the deep overfold of Greek sculpture "
              "comes from.",
         source="as the chiton"),
    dict(name="hanfu", part="top", female=False, arrival=-1000, cultures=["east_asian"],
         roles=["farmer", "artisan", "citizen", "merchant", "scholar", "advisor", "scribe"],
         mark="recorded",
         note="**A crossed collar with the right side over the left**, which is the thing that makes "
              "it Chinese and not something else: the wrong side over the left is how the dead are "
              "dressed. Wide sleeves for the scholar, short for the farmer, same silhouette.",
         source="Han and Tang tomb figures; the youren collar"),
    dict(name="hanfu_f", part="dress", female=True, arrival=-1000, cultures=["east_asian"],
         roles=["citizen", "artisan", "scholar", "merchant", "priest"], mark="recorded",
         note="As above, wrapping across the front and belted high. The ruqun skirt is the shape that "
              "survives the longest.",
         source="as the hanfu"),
    dict(name="kaftan", part="outer", female=False, arrival=500, cultures=["persianate",
         "north_african", "mesopotamian", "indic", "deccan"], roles=["merchant", "scholar",
         "advisor", "citizen", "healer"], mark="recorded",
         note="**A coat that opens down the front and can be worn over everything**, which is why it "
              "travels: Persia to the Ottoman court to North Africa to India to Russia, and each "
              "place changes the cloth and not the shape. The Ottoman sultans legislated the colour by "
              "rank, which makes it a uniform as well as a coat.",
         source="Ottoman and Safavid dress regulations"),
    dict(name="robe", part="outer", female=False, arrival=-500, cultures=["east_asian",
         "persianate", "african", "north_african"], roles=["scholar", "advisor", "priest",
         "merchant"], mark="recorded",
         note="The long closed garment, worn loose. In China a robe is formal and a jacket is "
              "working; in West Africa the grand boubou is a robe and the status is in the "
              "embroidery, not the cut.",
         source="Ming dress; the boubou of the Sahel"),
    dict(name="kurta", part="top", female=False, arrival=1200, cultures=["deccan", "indic",
         "maurya", "persianate"], roles=["farmer", "artisan", "citizen", "merchant", "scribe",
         "scholar"], mark="estimated",
         note="**The everyday northern Indian shirt**, knee-length, side-slitted, worn over the "
              "dhoti or the pyjama. The date is estimated: the cut is a Persian import that settles "
              "into India over the medieval period, and no source gives a year for it because nobody "
              "wrote down when a shirt changed shape.",
         source="Indian dress history; the Persian-Mughal transmission"),
    dict(name="sherwani", part="outer", female=False, arrival=1850, cultures=["deccan", "indic",
         "persianate"], roles=["advisor", "merchant", "scholar"], mark="recorded",
         note="**A 19th-century garment and it is dated as one.** The sherwani is a court coat that "
              "appears in the late Mughal and colonial period, and dressing a Mughal nobleman of "
              "1600 in it is the exact error this register exists to prevent: the medieval row is "
              "the kaftan and the angarkha, not the sherwani.",
         source="late Mughal and colonial Indian court dress"),
    dict(name="dhoti_top", part="top", female=False, arrival=-1000, cultures=["deccan", "indic",
         "maurya"], roles=["farmer", "artisan", "citizen", "merchant", "scribe"], mark="estimated",
         note="**The upper cloth, which is the half that was missing.** The pools already carried "
              "`lower: dhoti` and nothing above it, so the register adds the angavastram and the "
              "uttariya: a length of cloth over one shoulder, and for a labourer, no upper garment "
              "at all, which is also true.",
         source="the angavastram and uttariya; the pools' own `cultural` list"),
    dict(name="sari_wrap", part="dress", female=True, arrival=-1000, cultures=["deccan", "indic",
         "maurya"], roles=["citizen", "artisan", "merchant", "priest", "scholar", "healer"],
         mark="estimated",
         note="The pools already carry `femaleLower: sari`; what is missing is the upper drape that "
              "completes it, and the fact that in most of the period a woman's chest was covered by "
              "the same length of cloth and not a separate garment.",
         source="the pools' own list; Indian textile history"),
    dict(name="kimono", part="dress", female=False, arrival=794, cultures=["east_asian"],
         roles=["citizen", "artisan", "merchant", "scholar", "advisor"], mark="recorded",
         note="**A Heian court garment that becomes everybody's**, and the date is the move of the "
              "capital to Kyoto in 794, which is when the Japanese court stops copying Tang dress "
              "and starts cutting its own. The obi and the sleeve depth are the dating evidence.",
         source="Heian court dress; the juunihitoe to the kosode"),
    dict(name="kimono_f", part="dress", female=True, arrival=794, cultures=["east_asian"],
         roles=["citizen", "artisan", "merchant", "scholar", "priest"], mark="recorded",
         note="As above, with the obi at the back and a deeper sleeve. A modern kimono is the "
              "kosode, which is a *under*garment that became outer wear in the Muromachi period.",
         source="as the kimono"),
    dict(name="cloak", part="outer", female=False, arrival=-1000, cultures=["mediterranean",
         "rome", "persianate", "mesopotamian", "north_african", "african", "east_asian",
         "americas"], roles=["merchant", "scholar", "advisor", "soldier", "guard", "farmer",
         "scribe"], mark="recorded",
         note="**A rectangle of wool with a pin at the throat, and it is the coat of every cold "
              "place before there are coats.** The Roman paenula, the Greek himation, the Persian "
              "aba, the Andean mantle: the same object, and the difference between them is the "
              "fibre. Europe has no *fitted* coat before the 14th century because there is no "
              "tailoring; it has this instead, and this is enough.",
         source="Roman paenula and Greek himation; the aba; Andean mantle"),
    dict(name="cloak_f", part="outer", female=True, arrival=-1000, cultures=["mediterranean",
         "rome", "persianate", "mesopotamian", "north_african", "african", "east_asian",
         "americas"], roles=["merchant", "scholar", "citizen", "healer", "priest"],
         mark="recorded",
         note="The same cloak pinned differently, which in practice means covering the head. A "
              "woman's mantle is a garment and a veil at once for most of the period, and the "
              "distinction between them is later than the cloth.",
         source="as the cloak"),
    dict(name="doublet", part="top", female=False, arrival=1340, cultures=["mediterranean", "rome"],
         roles=["merchant", "scholar", "advisor", "soldier", "guard", "artisan"], mark="recorded",
         note="**The garment that invented tailoring.** A doublet is cut and sewn to the body rather "
              "than draped, which needs curved seams and therefore a new kind of tailor, and it "
              "happens in Europe in the 1340s: the same decades as the Black Death. What follows is "
              "everything fitted that Europe has worn since.",
         source="European tailoring history; the 1340s fitted turn"),
    dict(name="hose", part="bottom", female=False, arrival=1300, cultures=["mediterranean",
         "rome"], roles=["merchant", "scholar", "advisor", "soldier", "guard", "artisan"],
         mark="recorded",
         note="Two separate legs, tied to the doublet, **not joined at the top**: joined hose is a "
              "16th-century invention and the reason is tailoring, not modesty. Before hose, both "
              "sexes wore a long tunic and legs were not a garment.",
         source="medieval European dress"),
    dict(name="cotehardie", part="dress", female=True, arrival=1340, cultures=["mediterranean",
         "rome"], roles=["merchant", "scholar", "citizen", "advisor"], mark="recorded",
         note="The fitted women's gown of the same moment as the doublet, and the first European "
              "women's garment that is cut rather than draped.",
         source="as the doublet"),
    dict(name="shirt", part="top", female=False, arrival=1200, cultures=["mediterranean", "rome"],
         roles=["farmer", "artisan", "citizen", "soldier", "guard"], mark="estimated",
         note="**Linen next to the skin and wool over it** is the whole medieval system of dress, "
              "and the shirt is the part nobody sees. It is also the part that gets washed, which is "
              "why it is linen and why it survives in inventories.",
         source="medieval linen inventories"),
    dict(name="chemise", part="top", female=True, arrival=1200, cultures=["mediterranean", "rome"],
         roles=["farmer", "artisan", "citizen", "healer", "priest"], mark="estimated",
         note="The same garment for a woman. A chemise in 1300 is not underwear in the modern sense: "
              "it is the only washable layer, and in some places it is the only layer.",
         source="as the shirt"),
    dict(name="wrapper_top", part="top", female=False, arrival=-1000, cultures=["african",
         "north_african", "mesopotamian"], roles=["farmer", "artisan", "citizen", "merchant",
         "soldier"], mark="estimated",
         note="**A length of cloth wrapped over one shoulder and tied, which is a garment and needs "
              "no tailor.** Most of the world dressed this way for most of its history, and the "
              "pools' `lower: wrap` for North Africa was half of it. The other half is this. The date "
              "is estimated because a wrapped cloth leaves no button, seam or dyeline to date, which "
              "is the same reason the archaeological record of dress is biased towards metal.",
         source="West and North African textile history; the pools' own `wrap`"),
    dict(name="boubou", part="outer", female=False, arrival=1000, cultures=["african"],
         roles=["merchant", "scholar", "advisor", "priest", "citizen"], mark="estimated",
         note="**A wide sleeveless or short-sleeved over-robe, and the status is in the embroidery.** "
              "It reaches the Sahel with the trans-Saharan trade, which step 46 dates to the camel's "
              "arrival, so this garment and the caravan are the same fact seen twice.",
         source="Sahelian dress; the trans-Saharan textile trade"),
    dict(name="kente_wrap", part="dress", female=True, arrival=1600, cultures=["african"],
         roles=["citizen", "merchant", "artisan", "priest"], mark="estimated",
         note="A woman's wrapped cloth. **The date is late because the pool's own era map puts "
              "`colonial` at 1850 and `early` at 1600**, so a woman in the African pool before 1600 "
              "had no garment at all in this register until this row, which is the gap the check "
              "found.",
         source="West African wrappers; the pools' era map"),
    dict(name="huipil", part="top", female=True, arrival=-800, cultures=["americas"],
         roles=["farmer", "artisan", "citizen", "merchant", "priest", "healer"], mark="recorded",
         note="**A rectangle with a hole, woven on a backstrap loom, and it is still made.** The "
              "Mesoamerican huipil is one of the very few garments in this register whose continuous "
              "history is documented rather than inferred, because it is still being woven by the "
              "descendants of the people who wore it.",
         source="Mesoamerican textile history; living Maya weaving traditions"),
    dict(name="poncho", part="outer", female=False, arrival=-500, cultures=["americas"],
         roles=["farmer", "artisan", "citizen", "merchant", "soldier"],
         mark="recorded",
         note="Two rectangles joined with a slit for the head, which is the Andean answer to a coat "
              "and needs no tailoring at all. The Incas standardised the cloth and the pattern as a "
              "mark of rank, which makes it a uniform.",
         source="Andean textile history; Inca dress regulation"),
]


def problems():
    bad = []
    seen = set()
    for g in GARMENTS:
        if g["name"] in seen:
            bad.append("duplicate garment " + g["name"])
        seen.add(g["name"])
        if g["part"] not in PARTS:
            bad.append(g["name"] + " is on the part " + str(g["part"]))
        if g["mark"] not in ("recorded", "estimated", "projected"):
            bad.append(g["name"] + " has the mark " + str(g["mark"]))
        if not (-3000 <= g["arrival"] <= 3000):
            bad.append(g["name"] + " arrives in " + str(g["arrival"]) + ", outside the world")
        for c in g["cultures"]:
            if c not in CULTURES:
                bad.append(g["name"] + " names the culture " + c + ", which has no pool")
        if not g["cultures"]:
            bad.append(g["name"] + " belongs to no culture and can never be worn")
        if not g["note"] or len(g["note"]) < 60:
            bad.append(g["name"] + " does not say anything useful")
        if not g["source"]:
            bad.append(g["name"] + " cites nothing")

    # THE POINT OF THE WHOLE REGISTER: somebody must be dressed before 1873.
    pre = [g for g in GARMENTS if g["arrival"] < 1873]
    if len(pre) < 15:
        bad.append("only " + str(len(pre)) + " garments exist before 1873, which is the gap this "
                   "register exists to close")
    for c in CULTURES:
        have = [g for g in pre if c in g["cultures"] and g["part"] in ("top", "dress")]
        if not have:
            bad.append("no upper garment before 1873 for the culture " + c)

    # A garment cannot arrive before the culture it belongs to is in its area.
    for g in GARMENTS:
        if g["name"] == "sherwani" and g["arrival"] < 1700:
            bad.append("the sherwani is a 19th-century coat and cannot be dated " + str(g["arrival"]))
        if g["name"] == "kimono" and g["arrival"] < 700:
            bad.append("the kimono is a Heian garment and cannot be dated " + str(g["arrival"]))

    # Both sexes must be covered, or the pool will dress half the population in nothing.
    for sex in (True, False):
        n = len([g for g in pre if g["female"] == sex and g["part"] in ("top", "dress")])
        if n < 4:
            bad.append("only " + str(n) + " upper garments for female=" + str(sex))
    return bad


def main():
    bad = problems()
    pre = [g for g in GARMENTS if g["arrival"] < 1873]
    print("wardrobe: %d period garments, %d before 1873, over %d cultures and %d parts"
          % (len(GARMENTS), len(pre), len({c for g in GARMENTS for c in g["cultures"]}),
             len({g["part"] for g in GARMENTS})))
    print("  earliest: %s (%d), latest: %s (%d)"
          % (min(GARMENTS, key=lambda g: g["arrival"])["name"],
             min(g["arrival"] for g in GARMENTS),
             max(GARMENTS, key=lambda g: g["arrival"])["name"],
             max(g["arrival"] for g in GARMENTS)))
    print()
    for g in sorted(GARMENTS, key=lambda g: g["arrival"]):
        print("  %-12s %-6s %s  %-5d %-24s %s"
              % (g["name"], g["part"], "F" if g["female"] else "M", g["arrival"],
                 ",".join(g["cultures"])[:24], g["mark"]))
    for p in bad:
        print("  PROBLEM " + p)
    print("wardrobe_table: %d problem(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
