#!/usr/bin/env python3
"""
Step 47 part 5 (B5, B6, E18): **wild animals, crops, and both as items.**

    python3 wildlife_table.py        check the register and print it

The plan's lines:

- **B5**: *"Wild animals by era (lions and cheetahs in India, aurochs in Europe, no horses in the
  Americas before 1493)."*
- **B6**: *"Crops by era (no maize, potatoes or chillies in India before the 1500s)."*
- **E18**: *"Animals and crops as items, as they spread."*

The survey found the two halves in completely different states. **B6 and E18 are nearly done**:
step 44's products atlas dates 539 products in all 17 areas and the Columbian exchange is visible in
its numbers (`maize` reaches Europe in 1520 and Mesoamerica in 1000 BC; `potato` reaches Europe in
1570 and South Asia in 1615). What is missing is only a **join** that answers *is this crop here in
this year* in one call, and that is `Crops.java`.

**B5 is empty.** The only wild animal anywhere in this project is the bison, in step 46's herd
register, and it is there because it was *hunted in herds*.

## The thing this register is actually a register of

A wild animal's data is not its birth date. It is **its range and the year the range ended**, and
almost every row here is one of three stories:

1. **Extirpation**: the animal is gone from one place and lives in another. The lion left Greece
   around 100 BC and left India in 1884 in the wild outside Gir.
2. **Extinction**: the animal is gone everywhere, and the year is known because somebody was
   counting. The aurochs, 1627. The dodo, by 1681.
3. **The opposite**: the animal was never there, and the absence is the fact. **No horses in the
   Americas before 1493**, and not because they were hunted out: the North American horse died out
   at the end of the Pleistocene and the continent had no horse for ten thousand years.

That third one is the plan's own example and it is the one most often got wrong in games: a horse in
the Americas in 1200 is not a small anachronism, it is the single largest biological fact about the
continent.
"""

AREAS = ["EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA", "WAF", "MSA", "EAF",
         "NNA", "MNA", "CAC", "SAM", "PAC", "AUS"]

# How a species stands in an area. `gone` is a year; `never` is a reason.
STATUS = ["present", "gone"]

SPECIES = [
    # ---- THE LIONS, WHICH ARE THE PLAN'S OWN EXAMPLE -------------------------------------
    dict(id="lion", name="the lion", areas={
            "EUR": (-3000, -100), "WAS": (-3000, 1900), "SAS": (-3000, 1884),
            "NAF": (-3000, 1900), "EAF": (-3000, None), "WAF": (-3000, None),
            "MSA": (-3000, None), "EEU": (-3000, -500), "CAS": (-3000, 1000)},
         never={"NNA": "the American lion died out at the end of the Pleistocene, before the span",
                "SAM": "as North America", "EAS": "the lion never reached East Asia",
                "SEA": "no lion east of India", "AUS": "no large placental predator ever reached "
                        "Australia; the thylacine is a marsupial and is not a lion",
                "MNA": "as North America", "CAC": "as North America", "PAC": "never"},
         mark="recorded",
         note="**The lion is European.** It is in the Iliad as a predator of the Greek hills, it "
              "fights in Roman arenas, and it is gone from Greece by about 100 BC and from the "
              "Balkans by 500. In India it survives outside Gujarat until **1884**, and in Asiatic "
              "Turkey and Iraq into the 19th century. The lion in the Senegambia and East Africa is "
              "the same species and it never left.",
         source="Iliad XXI; Schnitzler, ecology of the lion in Europe; the Gir population and the "
                "1884 record"),
    dict(id="cheetah", name="the cheetah", areas={
            "SAS": (-3000, 1952), "WAS": (-3000, 1900), "NAF": (-3000, 1900),
            "EAF": (-3000, None), "MSA": (-3000, None), "WAF": (-3000, None),
            "CAS": (-3000, 1900)},
         never={"EUR": "not native; the Romans imported them for the arena and never established "
                       "a population", "EAS": "the cheetah never reached East Asia",
                "NNA": "no cheetah in the Americas", "SAM": "as North America",
                "AUS": "never", "MNA": "as North America", "CAC": "as North America",
                "SEA": "never", "EEU": "never", "PAC": "never"},
         mark="recorded",
         note="**The cheetah is a court animal and that is why it has a date.** Mughal emperors kept "
              "hundreds, Akbar is said to have kept a thousand, and they were used to hunt blackbuck "
              "in exactly the way a falcon is used on a bird. The Indian cheetah was declared "
              "extinct in **1952**, and the last three were shot in 1947 by the Maharaja of "
              "Surguja. India has been reintroducing them from Namibia since 2022.",
         source="Akbarnama; the 1952 extinction declaration; the Kuno reintroduction"),
    # ---- THE ONES THAT WENT ENTIRELY ------------------------------------------------------
    dict(id="aurochs", name="the aurochs", areas={
            "EUR": (-3000, 1627), "EEU": (-3000, 1627), "WAS": (-3000, -1000),
            "NAF": (-3000, -2000), "CAS": (-3000, 1600)},
         never={"SAS": "the Indian aurochs is the zebu's ancestor and is a separate form",
                "EAS": "the aurochs never reached East Asia", "NNA": "no aurochs in the Americas",
                "SAM": "as North America", "AUS": "never", "MNA": "as North America",
                "CAC": "as North America", "SEA": "never", "MSA": "never", "EAF": "never",
                "WAF": "never", "PAC": "never"},
         mark="recorded",
         note="**The wild ancestor of every domestic cow, and it died in a royal park.** A bull "
              "stood about 1.8 m at the shoulder, was black with a pale stripe, and was hunted across "
              "Europe for the whole of the record. The last one died at Jaktorów in Poland in "
              "**1627**, in a reserve kept for hunting, of a disease nobody recorded. The Heck "
              "brothers' 'recreated' aurochs of the 1930s is a breeding experiment and not the "
              "animal.",
         source="the Jaktorów herd records; van Vuure, Retracing the Aurochs"),
    dict(id="dodo", name="the dodo", areas={"MSA": (-3000, 1681)},
         never={"EUR": "known only from specimens and paintings", "SAS": "endemic to Mauritius",
                "EAF": "endemic to Mauritius", "AUS": "never", "NNA": "never", "SAM": "never",
                "EAS": "never", "SEA": "never", "WAS": "never", "NAF": "never", "WAF": "never",
                "CAS": "never", "EEU": "never", "MNA": "never", "CAC": "never", "PAC": "never"},
         mark="recorded",
         note="**A bird that evolved without a predator and met sailors.** It is flightless, it "
              "weighed about 15 kg, and it was extinct by about **1681**, less than a century after "
              "the Portuguese found Mauritius. The date is not exact because nobody was counting, "
              "which is itself the lesson: an extinction nobody records has no year.",
         source="the Mauritius records; Hume, The Dodo"),
    dict(id="passenger_pigeon", name="the passenger pigeon", areas={"NNA": (-10000, 1914)},
         never={"EUR": "an American bird", "SAM": "an American bird, and not this one",
                "EAS": "never", "SAS": "never", "AUS": "never", "WAF": "never", "EAF": "never",
                "MSA": "never", "NAF": "never", "WAS": "never", "CAS": "never", "EEU": "never",
                "MNA": "as North America", "CAC": "as North America", "SEA": "never",
                "PAC": "never"},
         mark="recorded",
         note="**The most numerous bird that has ever lived, and it took forty years to remove.** "
              "Estimates run to three to five billion birds in one nesting flock that took three days "
              "to fly over. The last one, Martha, died in Cincinnati Zoo in **1914**, and by then the "
              "species was already extinct in the wild. **Abundance is not safety**, which is the "
              "only thing this row is for.",
         source="the Cincinnati Zoo record; Schorger, The Passenger Pigeon"),
    dict(id="thylacine", name="the thylacine", areas={"AUS": (-3000, 1936)},
         never={"MSA": "a Tasmanian animal", "NNA": "never", "SAM": "never", "EUR": "never",
                "SAS": "never", "EAS": "never", "SEA": "never", "WAF": "never", "EAF": "never",
                "NAF": "never", "WAS": "never", "CAS": "never", "EEU": "never", "MNA": "never",
                "CAC": "never", "PAC": "never"},
         mark="recorded",
         note="**A marsupial that looked like a wolf, which is the best case of convergent evolution "
              "in the record.** It was declared a pest, a bounty was paid per skin, and the last "
              "known animal died in Hobart Zoo in **1936**, in a cage, in the cold. Every sighting "
              "since is unconfirmed and the searches continue.",
         source="the Hobart Zoo record; the Tasmanian bounty acts"),
    # ---- THE ONES STILL THERE, WITH A RANGE THAT MOVED --------------------------------
    dict(id="tiger", name="the tiger", areas={
            "SAS": (-3000, None), "EAS": (-3000, None), "SEA": (-3000, None),
            "CAS": (-3000, 1950), "WAS": (-3000, 1970), "EEU": (-3000, 1950)},
         never={"EUR": "the Romans imported them; no European population",
                "NAF": "never", "WAF": "never", "EAF": "never", "MSA": "never",
                "NNA": "never", "SAM": "never", "MNA": "never", "CAC": "never",
                "AUS": "never", "PAC": "never"},
         mark="recorded",
         note="**Two subspecies go extinct inside this register's span.** The Caspian tiger is gone "
              "by the 1970s and the Bali tiger by the 1930s; the Javan tiger by the 1970s. The tiger "
              "in Siberia and the tiger in Sumatra are the same species and a different animal.",
         source="IUCN subspecies accounts; the Caspian tiger's last record in Turkey, 1970"),
    dict(id="wolf", name="the wolf", areas={
            "EUR": (-3000, None), "EEU": (-3000, None), "WAS": (-3000, None),
            "CAS": (-3000, None), "EAS": (-3000, None), "NNA": (-10000, None),
            "SAS": (-3000, None),
            # the wolf is extinct in Britain by 1500 and in Japan by 1905, and this register carries
            # the areas it holds, not every local extinction
            },
         never={"SAM": "the South American canid is a different animal and not this wolf",
                "AUS": "never: the dingo arrived with people",
                "MSA": "never", "SEA": "never", "NAF": "the African wolf is a separate species "
                        "and was long mistaken for a jackal", "WAF": "never",
                "EAF": "never", "MNA": "as North America", "CAC": "as North America",
                "PAC": "never"},
         mark="recorded",
         note="**The animal that was exterminated locally and then came back.** Britain's last wolf "
              "is about 1500, Japan's is 1905, and the American wolf was shot and poisoned to a few "
              "hundred by 1960 and reintroduced to Yellowstone in 1995. This register carries the "
              "areas, not every county, and says so.",
         source="British and Japanese extinction dates; the Yellowstone reintroduction"),
    dict(id="elephant_wild", name="the wild elephant", areas={
            "SAS": (-3000, None), "SEA": (-3000, None), "EAS": (-3000, None),
            "EAF": (-3000, None), "WAF": (-3000, None), "MSA": (-3000, None),
            "WAS": (-3000, -100)},
         never={"EUR": "the war elephant was imported; no European breeding population",
                "NAF": "the North African elephant, used by Carthage, is extinct by about AD 100 and "
                        "this row does not carry it as present",
                "NNA": "never", "SAM": "never", "MNA": "never", "CAC": "never",
                "AUS": "never", "PAC": "never", "EEU": "never", "CAS": "never"},
         mark="recorded",
         note="**The elephant is the one animal in this register whose working role is already dated "
              "elsewhere**: step 46 gives it `pull` and `ride` and notes that Minecraft has no "
              "entity for it. What is different here is the range, and the range collapsed: the "
              "Syrian elephant is extinct by 100 BC and the North African by about AD 100.",
         source="the Syrian and North African elephant extinctions; step 46's animal register"),
    dict(id="hippopotamus", name="the hippopotamus", areas={
            "EAF": (-3000, None), "WAF": (-3000, None), "MSA": (-3000, None),
            "NAF": (-3000, 1800)},
         never={"EUR": "the Romans imported them for the arena; none lived in Europe",
                "SAS": "the Indian animal is the pig, the rhino and the gharial; no hippo",
                "WAS": "the hippo was in the Levant in the Pleistocene and is gone long before the "
                       "span", "EAS": "never", "SEA": "never", "NNA": "never", "SAM": "never",
                "MNA": "never", "CAC": "never", "AUS": "never", "PAC": "never",
                "EEU": "never", "CAS": "never"},
         mark="recorded",
         note="**In the Nile, and painted on the walls of Egyptian tombs.** The hippo is a hazard of "
              "the river and a god, and it survives in the Nile delta until the early 19th century "
              "and in the rest of Africa throughout. Its presence is a fact about water, not about "
              "latitude.",
         source="Egyptian tomb painting; the Nile delta extinction"),
    dict(id="crocodile", name="the Nile crocodile", areas={
            "EAF": (-3000, None), "WAF": (-3000, None), "MSA": (-3000, None),
            "NAF": (-3000, None), "SAS": (-3000, None), "SEA": (-3000, None),
            "MNA": (-3000, None), "CAC": (-3000, None), "SAM": (-3000, None)},
         never={"EUR": "no crocodile in Europe", "NNA": "the American alligator is a different "
                "animal and this register does not carry it", "EAS": "the Chinese alligator is a "
                "different animal", "AUS": "the saltwater crocodile is a different animal",
                "WAS": "the crocodile was in the Levant in the Pleistocene and is gone before the "
                       "span", "EEU": "never", "CAS": "never", "PAC": "never"},
         mark="recorded",
         note="**The largest predator a person could meet, and it is on four continents.** Its range "
              "is a map of warm fresh water and it has barely moved in the span. This row exists to "
              "show what a `present` row looks like when nothing has happened to it, which most of "
              "this register cannot be.",
         source="the standard range; Herodotus II on the Egyptian crocodile"),
    # ---- THE ABSENCE THAT MATTERS MOST --------------------------------------------------
    dict(id="horse_wild", name="the wild horse", areas={
            "EEU": (-3000, None), "CAS": (-3000, None), "EAS": (-3000, None),
            "WAS": (-3000, -2000), "EUR": (-3000, 1900)},
         never={"NNA": "**the horse died out in the Americas at the end of the Pleistocene and the "
                       "continent had none for ten thousand years.** Every horse in the Americas "
                       "after 1493 is a descendant of the Spanish imports, so a horse in 1200 is not "
                       "a small anachronism but the largest biological fact about the continent",
                "SAM": "as North America, and the Spanish horse arrives from 1530",
                "AUS": "no horse before 1788", "NAF": "the Barb is an imported domestic form",
                "SAS": "the horse arrives with the Indo-Europeans, from outside",
                "SEA": "no wild horse", "MSA": "never", "EAF": "never", "WAF": "never",
                "MNA": "as North America", "CAC": "as North America", "PAC": "never"},
         mark="recorded",
         note="**The plan's own example, and the reason it is in this register twice.** Step 46 "
              "carries the working horse and the date it reaches each area; this row carries the "
              "*absence* in the Americas as a fact about the wild animal, with the reason. "
              "Przewalski's horse is the last wild horse and was down to a dozen animals in zoos "
              "before reintroduction.",
         source="the Pleistocene extinction of the American horse; the Przewalski's horse recovery"),
    dict(id="bison_wild", name="the wild bison", areas={"NNA": (-10000, None)},
         never={"EUR": "the European bison, the wisent, is a different animal and this register does "
                       "not carry it", "SAM": "never", "EAS": "never", "SAS": "never",
                "AUS": "never", "WAF": "never", "EAF": "never", "MSA": "never",
                "NAF": "never", "WAS": "never", "CAS": "never", "EEU": "never",
                "MNA": "as North America", "CAC": "as North America", "SEA": "never",
                "PAC": "never"},
         mark="recorded",
         note="**The one wild animal step 46 already carries**, and this row exists so the two "
              "registers agree rather than disagree: 30 to 60 million in 1800 and **1,091 counted by "
              "Hornaday in 1889**. `present` is true here all the way to 3000 because the species "
              "survived and recovered, which is why the row is not marked gone and the herd register "
              "is: a herd was destroyed, a species was not.",
         source="Hornaday 1889; the recovery and the NPS herds"),
    # ---- THE SMALLER STORIES -------------------------------------------------------------
    dict(id="beaver", name="the beaver", areas={
            "EUR": (-3000, None), "EEU": (-3000, None), "NNA": (-10000, None),
            "CAS": (-3000, None)},
         never={"SAS": "never", "EAS": "never", "SAM": "the South American coypu is not a beaver",
                "AUS": "never", "NAF": "the North African beaver is extinct before the span",
                "WAF": "never", "EAF": "never", "MSA": "never", "SEA": "never",
                "MNA": "as North America", "CAC": "as North America", "WAS": "the beaver was in the "
                "Levant and is gone before the span", "PAC": "never"},
         mark="recorded",
         note="**The first animal in the record to be hunted almost to extinction for a fashion.** The "
              "European beaver is down to a few hundred by 1900 because of the felt hat, and it is "
              "reintroduced across Europe from the 1920s. The animal is a landscape engineer and "
              "every river it dammed is a river that changed.",
         source="the European beaver's near-extinction and the reintroductions"),
]


def problems():
    bad = []
    seen = set()
    for s in SPECIES:
        if s["id"] in seen:
            bad.append("duplicate species " + s["id"])
        seen.add(s["id"])
        if s["mark"] not in ("recorded", "estimated", "projected"):
            bad.append(s["id"] + " has the mark " + str(s["mark"]))
        for area, span in s["areas"].items():
            if area not in AREAS:
                bad.append(s["id"] + " names the area " + area + ", which is not real")
            lo, hi = span
            if hi is not None and hi <= lo:
                bad.append(s["id"] + " is gone from " + area + " before it arrived")

        for area in s["never"]:
            if area not in AREAS:
                bad.append(s["id"] + " says never about " + area + ", which is not real")
            if area in s["areas"]:
                bad.append(s["id"] + " is both present and absent in " + area)
            if len(s["never"][area]) < 4:
                bad.append(s["id"] + " says never about " + area + " without even a word")
        if not s["note"] or len(s["note"]) < 60:
            bad.append(s["id"] + " does not say anything useful")
        if not s["source"]:
            bad.append(s["id"] + " cites nothing")

    # THE PLAN'S OWN EXAMPLE, AS A TEST. If a horse is ever present in the Americas before 1493,
    # this register has failed at the one thing it was asked to get right.
    horse = next(x for x in SPECIES if x["id"] == "horse_wild")
    if "NNA" not in horse["never"] or "SAM" not in horse["never"]:
        bad.append("the wild horse must be recorded as ABSENT from the Americas, which is the "
                   "plan's own example")

    # No reason may be a placeholder. Specific reasons are allowed to be specific.
    for s in SPECIES:
        for area, r in s["never"].items():
            if r.strip() in ("", "-", "?", "n/a", "no"):
                bad.append(s["id"] + " has a placeholder reason for " + area)

    # A register of extinctions must contain some.
    gone = [s["id"] for s in SPECIES
            if any(hi is not None and hi < 2026 for _lo, hi in s["areas"].values())]
    if len(gone) < 6:
        bad.append("only " + str(len(gone)) + " species are extirpated somewhere: this is a "
                   "register of ranges ending and it has not got any")
    return bad


def main():
    bad = problems()
    print("wildlife: %d species over %d areas; %d extirpated somewhere in the span"
          % (len(SPECIES), len({a for s in SPECIES for a in s["areas"]}),
             len([s for s in SPECIES
                  if any(hi is not None and hi < 2026 for _lo, hi in s["areas"].values())])))
    print()
    for s in SPECIES:
        gone = [(a, hi) for a, (_lo, hi) in s["areas"].items() if hi is not None]
        older = [a for a, (lo, _hi) in s["areas"].items() if lo < -3000]
        print("  %-16s %-3d areas  gone: %-52s%s"
              % (s["id"], len(s["areas"]),
                 ", ".join("%s %d" % g for g in sorted(gone, key=lambda x: x[1])) or "-",
                 ("   already there in " + str(len(older)) + " areas") if older else ""))
    for p in bad:
        print("  PROBLEM " + p)
    print("wildlife_table: %d problem(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
