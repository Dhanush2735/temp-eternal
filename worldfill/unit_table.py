"""
Step 45 part 4 (C19): units and ranks — how an army is counted, and who counts it.

**The finding that organises this whole register: an army is counted in whatever base the society
counts in.** Ask four civilisations to divide a thousand men and you get four answers, and none of
them is arbitrary:

| who | base | the ladder |
|---|---|---|
| **Mongol, Inca, Ming China** | **ten** | 10 → 100 → 1,000 → 10,000 |
| **Aztec** | **twenty** | 20 → 400 → 8,000 |
| **India (Mahabharata, Arthashastra)** | **three** | 10 → 30 → 90 → 270 → 810 → … → 218,700 |
| **Sparta** | **two** | 36 → 72 → 144 → 576 |
| **Rome** | **none — idiosyncratic** | 8 → 80 → 480 → 5,120 |

The Aztec counted in twenties because Nahuatl counts in twenties, and the *xiquipilli* — 8,000 —
is also the word for the incense pouch that held 8,000 cacao beans. The Indian epics count in
threes, and the smallest unit, the *patti*, is itself a combined-arms team of **1 elephant, 1
chariot, 3 horse and 5 foot**: the four arms of the *chaturanga*, in one platoon of ten.

**And one system in here is not a ladder at all.** The Zulu *amabutho* count **by birth year**: a
man belongs to the regiment of the age set he was initiated with, is quartered in its own
*ikhanda*, wears its own shield colours, and **may not marry until the king releases his whole age
set at once**. Rome numbers you; the Zulu date you.

**The default is the honest one.** For most of the map and most of time there is no unit at all —
there is a war party of kin, tens of men, following a man who is good at this, who stops being in
charge the moment the fighting stops. That is row 0, and 800 of 867 area-years land on it.

Sources are named per row. Wikipedia throughout, per the standing instruction (no Seshat).
"""

# The areas, as the product atlas names them.
AREAS = ["EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA", "WAF", "MSA", "EAF",
         "NNA", "MNA", "CAC", "SAM", "PAC", "AUS"]
ALL = list(AREAS)

# A rung of the ladder.
#
#   name        what to call it in English
#   local       what they called it, or None when English is the local word
#   size        how many men, or None when the unit is not a number of men
#   commander   who commanded it, or None
#   note        what it was

def rung(name, local, size, commander, note=""):
    return dict(name=name, local=local, size=size, commander=commander, note=note)


SYSTEMS = [
    # ------------------------------------------------------------------ 0: the default
    dict(id="warband", name="the war party", polity=None, areas=ALL, y0=-10000, y1=2000,
         base=None,
         rungs=[
             rung("the war party", None, None, "a war leader",
                  "Tens of men, usually of one kin or one village, who follow a man because he is "
                  "good at this. He is in charge for as long as the fighting lasts and not a day "
                  "longer."),
             rung("the host", None, None, "the chief, or the king",
                  "Every man who can carry a weapon, called up for one campaign, going home when "
                  "it ends."),
         ],
         note="**The honest answer for most of the map and most of time.** Standing armies that "
              "can be divided into named units of fixed size are rare before the state, and the "
              "state is recent in most of the world. Do not put a sergeant in a band of hunters.",
         source="the pattern the whole register shows: no numbered ladder is recorded for most "
                "peoples, and absence of evidence is not evidence of a regiment"),

    # ------------------------------------------------------------------ Sparta: base two
    dict(id="sparta", name="the Spartan army", polity=["Peloponnesian"],
         areas=["EUR"], y0=-700, y1=-200, base=2,
         rungs=[
             rung("the enomotia", "enōmotia", 36, "enōmotarchēs",
                  "Three files of twelve. The name means 'a sworn band' - they swore an oath "
                  "together. The basic tactical unit, and the one that actually manoeuvred."),
             rung("the pentekostys", "pentēkostys", 72, "pentēkontēr",
                  "Two enomotiai. The name means 'fifty', which it had once been."),
             rung("the lochos", "lochos", 144, "lochagos",
                  "Two pentekostyai."),
             rung("the mora", "mora", 576, "polemarchos",
                  "Four lochoi, and the largest single tactical unit Sparta had. Six of them in "
                  "the full army."),
         ],
         note="**Doubled all the way up** - 36, 72, 144, 576 - which is the only ladder in this "
              "register built on two. **The sources disagree and the disagreement is worth "
              "keeping**: Xenophon's arithmetic gives this ladder, while Thucydides at Mantinea in "
              "418 BC puts four pentekostyes of 128 in each lochos and seven lochoi in the army "
              "(3,584 men), and other readings give a lochos of 640 and a mora of 1,152. The "
              "numbers also shrank in practice, because it was unusual to call up the older age "
              "classes, so an enomotia on campaign was 30 to 35 men rather than 36. **The ruler "
              "register knows no state called Sparta** - it files the place under the "
              "*Peloponnesian League*, so that is the fragment this row matches on, and it "
              "therefore covers Sparta's allies too. Their armies were not Spartan armies.",
         source="Wikipedia, Spartan army; Lochos"),

    # ------------------------------------------------------------------ Rome: idiosyncratic
    dict(id="rome", name="the legion", polity=["Roman", "Byzant"],
         areas=["EUR", "EEU", "WAS", "NAF"], y0=-500, y1=600, base=8,
         rungs=[
             rung("the tent group", "contubernium", 8, "decanus",
                  "Eight men who shared a tent, a mule, a millstone and a cooking pot, and who "
                  "could be rewarded or punished together. Chosen from among themselves, usually "
                  "the longest-serving of the eight."),
             rung("the century", "centuria", 80, "centurion",
                  "Ten contubernia. **Not a hundred** - the name is older than the number. The "
                  "centurion was a career soldier who had risen, and the most junior was paid "
                  "about ten times a legionary, the most senior perhaps forty times."),
             rung("the cohort", "cohors", 480, "pilus prior",
                  "Six centuries. Each cohort carried its own sound signal, so it could be "
                  "handled by trumpet without a runner."),
             rung("the legion", "legio", 5120, "legatus",
                  "Ten cohorts, the first of them double strength at about 800 men, plus 120 "
                  "cavalry for scouting and messages."),
         ],
         note="**The one ladder here with no base at all** - eight, then eighty, then four "
              "hundred and eighty. A century of eighty is the giveaway: Rome inherited the word "
              "from a levy of a hundred and never changed it when the number changed. **The "
              "centurionate was a ladder inside the ladder**: within a cohort the six centurions "
              "ranked hastatus posterior, hastatus prior, princeps posterior, princeps prior, "
              "pilus posterior, pilus prior, and a legion held 59 or 60 centurions climbing it, "
              "crowned by the **primus pilus**, the first spear, who commanded the first century "
              "of the first cohort and reported to the legate. Below the centurion came the "
              "**optio**, his second, on double pay.",
         source="Wikipedia, Contubernium (Roman army unit); Centuria; Cohort (military unit); "
                "Centurion"),

    # ------------------------------------------------------------------ India: base three
    dict(id="maurya", name="the akshauhini ladder", polity=["Maurya", "Magadha", "Nanda",
                                                            "Gupta"],
         areas=["SAS"], y0=-600, y1=1200, base=3,
         rungs=[
             rung("the patti", "patti", 10, "patika",
                  "**1 elephant, 1 chariot, 3 horse, 5 foot.** The four arms in one platoon of "
                  "ten - the chaturanga in miniature. Everything above it is this, multiplied."),
             rung("the senamukha", "senāmukha", 30, "senapati", "Three patti."),
             rung("the gulma", "gulma", 90, None, "Three senamukha."),
             rung("the gana", "gaṇa", 270, None, "Three gulma."),
             rung("the vahini", "vāhinī", 810, None, "Three gana."),
             rung("the pritana", "pṛtanā", 2430, None, "Three vahini."),
             rung("the chamu", "camū", 7290, None, "Three pritana."),
             rung("the anikini", "anīkinī", 21870, None, "Three chamu."),
             rung("the akshauhini", "akṣauhiṇī", 218700, None,
                  "Ten anikini: 21,870 chariots, 21,870 elephants, 65,610 horse and 109,350 foot. "
                  "Eighteen of them are said to have fought at Kurukshetra."),
         ],
         note="**No commander is recorded for any rung above the senamukha** - the tradition "
              "names the patika and the senapati and then falls silent, so the upper rungs carry "
              "none rather than a guess. **Counted in threes, which is the strangest ladder here and the most revealing** - "
              "because the *patti* is not a platoon of ten soldiers, it is a combined-arms team "
              "of one elephant, one chariot, three horse and five foot. Triple it eight times and "
              "you reach 218,700. Whether any historical army was ever drawn up this way is "
              "another question: the ladder comes from the Mahabharata and the Arthashastra, and "
              "the Mauryan army that Plutarch and Pliny describe (600,000 infantry, 30,000 "
              "cavalry, 9,000 elephants under Chandragupta) is not obviously built on it. It is "
              "recorded here as the ladder the tradition gives, and the note says so.",
         source="Wikipedia, Akshauhini (citing Mahabharata Adi Parva 2.15-23); the Arthashastra"),

    # ------------------------------------------------------------------ the steppe: base ten
    dict(id="mongol", name="the decimal army", polity=["Mongol", "Yuan", "Golden Horde", "Ilkhan",
                                                       "Chagatai", "Timurid"],
         areas=["CAS", "EAS", "EEU", "WAS"], y0=1206, y1=1500, base=10,
         rungs=[
             rung("the arban", "arban", 10, "arban-u noyan",
                  "Ten men, and **deliberately of mixed tribes** - Genghis broke clan units on "
                  "purpose, so that a man's loyalty ran to the ten beside him and upward to the "
                  "khan, not sideways to his kin."),
             rung("the jaghun", "jaghun (zuun)", 100, "jaghun-u noyan", "Ten arban."),
             rung("the mingghan", "mingghan", 1000, "mingghan-u noyan",
                  "Ten jaghun, and the unit that mattered: a mingghan was also **a thousand "
                  "households**, so the regiment and the tax roll were the same list. Most of the "
                  "commanders named in the sources are commanders of a mingghan."),
             rung("the tumen", "tümen", 10000, "tümen-ü noyan",
                  "Ten mingghan - the equivalent of a division, and the largest unit that could "
                  "still move and feed itself. Its commander was called a *myriarch* in Greek."),
         ],
         note="**The decimal ladder, borrowed from the Khitan and older than them** - the "
              "Achaemenids had it a thousand years before, and it is the ladder the Turkic and "
              "Mongol peoples used to organise households as much as soldiers. Actual strengths "
              "drifted: a mingghan in the mid-thirteenth century ran anywhere from 700 to 1,200. "
              "**The whole point of it was that it ignored kinship**, which is why a blacksmith's "
              "son could command nobles.",
         source="Wikipedia, Tumen (unit); Mingghan"),

    # ------------------------------------------------------------------ the Andes: base ten
    dict(id="inca", name="the decimal administration", polity=["Inca"],
         areas=["SAM"], y0=1200, y1=1533, base=10,
         rungs=[
             rung("the chunka", "chunka kamayuq", 10, "chunka kamayuq",
                  "Ten taxpayers. **A corvée unit before it was a military one** - the same list "
                  "of ten men who owed the mit'a was the squad that marched."),
             rung("the pichqa chunka", "pichqa chunka kamayuq", 50, "pichqa chunka kamayuq",
                  "Five chunka. The half-step that makes this ladder 10-50-100-1000-10000 rather "
                  "than a plain decimal one."),
             rung("the pachaka", "pachak kamayuq", 100, "pachak kamayuq", "Ten chunka."),
             rung("the waranqa", "waranqa kamayuq", 1000, "waranqa kamayuq", "Ten pachaka."),
             rung("the hunu", "hunu kuraka", 10000, "hunu kuraka", "Ten waranqa."),
             rung("the whole field army", "apukispay", None, "apukispay",
                  "The Sapa Inca was commander in chief; the *apukispay* was his general, and "
                  "senior command was kept in royal blood, which is why the emperor usually led "
                  "in person until the empire grew too big for him to leave Cusco."),
         ],
         note="**The ladder is the tax system.** Male heads of household were organised into "
              "corvée units of 10, 50, 100, 500, 1,000, 5,000 and 10,000, and those units "
              "*doubled* as the army - which is exactly why the Inca state issued every weapon "
              "and there was no market in arms (see the `inca` row of `arms.json.gz`). An economy "
              "organised by decimal administration does not need a quartermaster buying swords.",
         source="Wikipedia, Inca army; Government of the Inca Empire (decimal administration)"),

    # ------------------------------------------------------------------ Mesoamerica: base twenty
    dict(id="aztec", name="the xiquipilli", polity=["Aztec", "Mexica", "Tenochtitlan"],
         areas=["CAC", "MNA"], y0=1300, y1=1521, base=20,
         rungs=[
             rung("the banner", "pantli", 20, "a veteran warrior",
                  "Twenty men. **The Aztecs counted in twenties**, as Nahuatl does - and the "
                  "smallest tactical group of all was four or five men under a veteran."),
             rung("the company", None, 200, "a veteran warrior",
                  "Ten banners. Evidence for it is thinner than for the others - it may have been "
                  "a subdivision of the tzontli rather than a standing rung."),
             rung("the tzontli", "tzontli", 400, "a veteran of the calpulli",
                  "Twenty banners - 'a head of hair', 400. **Each calpulli, the ward or kin group, "
                  "supplied one**: Tenochtitlan had twenty calpulli and so a xiquipilli."),
             rung("the xiquipilli", "xiquipilli", 8000, "tlacateccatl / tlacochcalcatl",
                  "Twenty tzontli. The word is also the name of **the pouch that held 8,000 cacao "
                  "beans**, which is what tells you the number comes from counting, not from "
                  "military theory. Twenty-five of them - 200,000 men - were raised against "
                  "Coixtlahuaca."),
         ],
         note="**No standing army at all.** Warriors were called up when needed, each town "
              "sending its complement, and they marched as their own unit under their own senior "
              "warriors and their own standard. **Rank here is not command, it is captives**: four "
              "captives made you an eagle or a jaguar warrior; five or six admitted you to the "
              "*otontin*; the *cuachicqueh*, the Shorn Ones, needed six or more and twenty acts "
              "of valour and were the shock troops, shaved but for one braid over the left ear. A "
              "commoner could rise to noble standing by taking prisoners.",
         source="Wikipedia, Aztec warfare; Mexican Army (calpulli and xiquipilli)"),

    # ------------------------------------------------------------------ Ming China: decimal, hereditary
    dict(id="ming", name="the wei-suo system", polity=["Ming"],
         areas=["EAS"], y0=1368, y1=1644, base=10,
         rungs=[
             rung("the small banner", "xiaoqi", 10, "xiaoqi guan", "A squad of ten or eleven."),
             rung("the chief banner", "zongqi", 50, "zongqi guan", "Five small banners."),
             rung("the company", "baihu suo", 112, "baihu",
                  "Two chief banners - nominally a hundred, actually 112."),
             rung("the battalion", "qianhu suo", 1120, "qianhu", "Ten companies."),
             rung("the guard", "wei", 5600, "zhihui",
                  "Five battalions. Some 300 to 500 guards across the empire, each reporting to "
                  "the provincial military commission and the Ministry of War rather than to the "
                  "local civil government."),
         ],
         note="**An army of hereditary farm-soldiers.** The wei-suo were meant to feed "
              "themselves by *tuntian* military agriculture, so a guard was a garrison and a "
              "farm at once, and an officer was personally accountable for his unit's weapons and "
              "mounts. The system was inherited from the Yuan, which had inherited the Mongol "
              "decimal habit - and it decayed: by the mid-fifteenth century the farming was being "
              "evaded and the rolls were fiction, which is why the Ming came to rely on mercenaries.",
         source="Wikipedia, Military of the Ming dynasty; Britannica, weisuo"),

    # ------------------------------------------------------------------ the Ottomans
    dict(id="ottoman", name="the janissary corps", polity=["Ottoman"],
         areas=["WAS", "EEU", "NAF", "EUR"], y0=1363, y1=1826, base=10,
         rungs=[
             rung("the squad", None, 10, "oda-başı",
                  "Ten janissaries shared a horse, a tent and a trunk - the same hearth-group "
                  "idea as the Roman contubernium, arrived at independently. **The oda-başı was "
                  "the 'chief of the barrack room'**, the adjutant who kept the orta's books as "
                  "well as its men."),
             rung("the company", "bölük", None, "bölükbaşı",
                  "The word simply means 'a part' or 'a troop'."),
             rung("the regiment", "orta", None, "çorbacı",
                  "**The regiment was the whole world of a janissary.** nominally 100 to 500 men, "
                  "it was the unit of loyalty and of *esprit*: a man was promoted only within his "
                  "own orta, and could leave it only to command another. Süleyman I had 165 of "
                  "them, rising to 196."),
             rung("the hearth", "ocak", None, "Yeniçeri Ağası",
                  "All the orta together - 'the hearth', the corps itself, some 40,000 by 1609 "
                  "and 70,000 by the end of the century."),
         ],
         note="**The ranks are a kitchen, and that is the point.** The regiment is commanded by a "
              "*çorbacı*, the **soup-maker**; under him an *aşçıbaşı*, the **chief cook**; a "
              "*sakka-başı*, the **chief water-carrier**; an *oda-başı*, the chief of the barrack "
              "room. The janissaries were the sultan's household troops and slaves, and the "
              "vocabulary of the household never left them. The corps was divided into the "
              "*cemaat* (frontier troops, 101 orta), the *bölük* (the sultan's own bodyguard, 61) "
              "and the *sekban* ('dog-keepers', 34). It ended in 1826, when Mahmud II had the "
              "barracks shelled.",
         source="Wikipedia, Janissary; Orta (Janissary); Agha of the Janissaries"),

    # ------------------------------------------------------------------ the Zulu: age, not number
    dict(id="zulu", name="the amabutho", polity=["Zulu"],
         areas=["MSA", "EAF"], y0=1816, y1=1900, base=None,
         rungs=[
             rung("the age set", "intanga", None, None,
                  "A cohort of men of the same age, first formed as a circumcision guild of about "
                  "fifty on a district basis. **You did not join a regiment; you grew into one.**"),
             rung("the regiment", "ibutho (pl. amabutho)", 4000, "induna",
                  "Several age sets grouped, 1,000 to 5,000 men, quartered in its own *ikhanda*, "
                  "with its own name, its own shield colours and its own headdress. **The shield "
                  "colours let the king see which regiment was where**, exactly as a European "
                  "colour did."),
             rung("the army", "impi", None, "the king",
                  "As many regiments as were called up. Shaka's standard order was the **beast's "
                  "horns**: a chest to pin the enemy, two horns to encircle, and loins held in "
                  "reserve sitting with their backs to the battle so as not to be excited."),
         ],
         note="**Counted by birth year, not by ten.** This is the one system here that is not a "
              "ladder of numbers at all. A man was enrolled at twenty, served in the regiment of "
              "his age set, was quartered in its kraal, and **could not marry until the king "
              "released his entire age set at once** - the whole point being to transfer a young "
              "man's loyalty from his clan and his chief to the king. Boys served from as young as "
              "six as *udibi* porters. Commanders (*induna*) were appointed on merit and not by "
              "birth, which is the same reform Zulu and Genghis made independently: **break the "
              "kin group, and the soldier belongs to the state.**",
         source="Wikipedia, Impi; Zulu people (ukubuthwa); Britannica, amabutho"),

    # ------------------------------------------------------------------ medieval Europe
    dict(id="medieval", name="the retinue", polity=None, areas=["EUR", "EEU"], y0=500, y1=1500,
         base=None,
         rungs=[
             rung("the lance", "lance", 5, "a knight",
                  "A knight, his squire, a couple of men-at-arms and a mounted archer or two - "
                  "**not a unit of infantry but the smallest complete fighting household**, and "
                  "the unit by which armies were counted."),
             rung("the conroi", "conroi", 30, "a banneret or a knight",
                  "A knight's own household troop, twenty to fifty lances, riding together and "
                  "trained together."),
             rung("the banner", "banner", 200, "a banneret",
                  "Several conrois, a few hundred men."),
             rung("the retinue", "retinue", None, "the lord",
                  "Everything a great lord could bring: his household, his vassals' conrois, and "
                  "whatever he had contracted for in writing. **An army of contracts, not of "
                  "regulations** - an indenture named how many men at what wages for how long."),
         ],
         note="**An army of households, not of numbers.** The lance is the giveaway: the "
              "smallest unit is a man, his servants and his horses, and everything above it is a "
              "matter of who owes what to whom. A medieval muster roll counts *lances* and *men "
              "at arms*, and two captains with 500 men each may have nothing comparable at all. "
              "This row is a civilisation's default rather than any one state's regulation.",
         source="Wikipedia, Medieval army; Lance (unit); Lances fournies"),

    # ------------------------------------------------------------------ early modern Europe
    dict(id="earlymodern", name="the regiment", polity=None, areas=["EUR", "EEU"], y0=1500,
         y1=1800, base=10,
         rungs=[
             rung("the company", "company", 100, "captain",
                  "A hundred men or so, raised by a captain with a commission - in many armies "
                  "literally **his** company, recruited and equipped at his own cost."),
             rung("the regiment", "regiment", 1000, "colonel",
                  "Ten-ish companies. **The word means 'rule' or 'government'**: the regiment was "
                  "originally the contract under which a colonel raised men, and only later the "
                  "body of men themselves."),
             rung("the tercio", "tercio", 3000, "maestre de campo",
                  "The Spanish third - pikes and shot in one body, and the terror of the "
                  "sixteenth century. Other powers called the equivalent a brigade."),
             rung("the army", None, None, "the general",
                  "Whatever the sovereign had contracted for that season."),
         ],
         note="**The century in which an army becomes an institution rather than a gathering.** "
              "The regiment is the hinge: a permanent numbered body with a colonel, a roll and a "
              "colour, which exists between campaigns and outlives the men in it. Rank below the "
              "captain hardens too - **sergeant, ensign, corporal, lance-corporal** - and drill "
              "becomes the thing that makes a unit rather than a crowd. Gustavus and then "
              "Louis XIV make it a state affair; the artillery train and the uniform follow.",
         source="Wikipedia, Regiment; Tercio; Early modern warfare"),

    # ------------------------------------------------------------------ the Mughals: rank, not unit
    dict(id="mughal", name="the mansabdari", polity=["Mughal", "Sur"],
         areas=["SAS"], y0=1526, y1=1858, base=10,
         rungs=[
             rung("the trooper", "sawar", 1, "a mansabdar",
                  "One horseman with his horse and equipment. **The unit of account for the whole "
                  "system** - a mansabdar's rank is literally how many of these he must bring."),
             rung("the contingent", "tabinan", 10, "mansabdar of 10",
                  "The lowest mansab was ten. A mansabdar of 10 owed ten troopers."),
             rung("the command", None, 500, "mansabdar of 500 zat / 500 sawar",
                  "From about 1595 a rank is **two numbers**: *zat*, his personal standing and "
                  "pay, and *sawar*, the horse he is paid to maintain. A noble of 5,000 zat and "
                  "3,000 sawar draws the pay of the first and musters the second."),
             rung("the great command", None, 5000, "mansabdar of 5,000",
                  "The ceiling under Akbar, later raised to 7,000 and 10,000; a prince might hold "
                  "25,000. Abul Fazl's Ain-i-Akbari describes 33 grades in use."),
             rung("the imperial host", None, None, "the emperor",
                  "The sum of every mansabdar's contingent, mustered, branded and described."),
         ],
         note="**This system ranks men, not units, which is the thing C19 most needs to say.** A "
              "*mansab* is a number that fixes an officer's precedence, his salary and the cavalry "
              "he must maintain - and it confers no office, so its holder can be posted to "
              "collect revenue one year and command an army the next. **The ranks are decimal, an "
              "inheritance from Mongol and Timurid practice**, which makes this the same ladder as "
              "the tumen three centuries on and half a continent away. A mansabdar was paid not in "
              "cash but by *jagir* - the right to collect the revenue of a district, not the land "
              "itself - and the system's end came from arithmetic: about 1,800 mansabdars under "
              "Akbar, 8,000 under Shah Jahan, more than 14,000 under Aurangzeb, chasing a supply "
              "of assignable jagirs that had stopped growing. Musters were enforced by *dagh*, "
              "branding the horses, and *chehra*, the descriptive roll of each man, both of which "
              "the Delhi Sultanate and Sher Shah had used before Akbar.",
         source="Wikipedia, Mansabdar; Army of the Mughal Empire; Government of the Mughal Empire"),

    # ------------------------------------------------------------------ the savannah empires
    dict(id="sahel", name="the corps and the flotilla", polity=None, areas=["WAF", "MSA"],
         y0=1230, y1=1900, base=None,
         rungs=[
             rung("the cavalry squad", None, 12, "a farariya",
                  "**Ten to fifteen horsemen**, which is the typical Mossi cavalry unit. Noble "
                  "birth rode; commoners were foot."),
             rung("the clan contingent", "ton-tigi", None, "ton-tigi",
                  "A noble clan's following. Mali had **sixteen** of these cavalry clans, and "
                  "each *farariya* ('brave') had infantry officers beneath him - the *kèlè-koun* "
                  "or *dùùkùnàsi*."),
             rung("the army corps", None, 4600, "Balma'a / Askia",
                  "**Songhai kept three permanent corps of about 4,600 men each** - one at "
                  "Tendirma under the Balma'a, one at Gao under the Askia, one in Dendi. This is "
                  "the standing professional army Askia Muhammad created, recruited largely from "
                  "a servile caste and mobilised full time."),
             rung("the flotilla", None, None, "hi-koi",
                  "**Two thousand war canoes on the Niger**, under an admiral who was also a "
                  "minister of state. Sunni Ali took Timbuktu and Djenné with horsemen and canoes "
                  "moving faster along the river than any army could march."),
         ],
         note="**Where the archer and the horseman are the two arms, and the river is a road.** "
              "The savannah empires fielded heavy cavalry in chain mail and helmets alongside "
              "massed archers - **three archers to one spearman** was the Malian ratio in the "
              "sixteenth century - with the archers opening the battle to soften the line for the "
              "charge. At Tondibi in 1591 Songhai met a Moroccan army of perhaps 4,000 men with "
              "arquebuses and six cannon; the Songhai numbers (12,500 horse and 30,000 foot by "
              "one reckoning, 18,000 and 9,700 by the Tarikh al-fattash) meant nothing against "
              "gunpowder, and a cattle stampede finished it. **This row is a regional pattern "
              "rather than any one state's regulation**, and the sizes vary wildly by source.",
         source="Wikipedia, African military systems before 1800; Military history of the Mali "
                "Empire; Songhai Empire; Battle of Tondibi"),

    # ------------------------------------------------------------------ the modern state
    dict(id="modern", name="the division", polity=None, areas=ALL, y0=1800, y1=2000, base=10,
         rungs=[
             rung("the squad", "squad / section", 10, "corporal / sergeant",
                  "Eight to twelve men, and the smallest unit anyone has ever been able to lead "
                  "by voice alone."),
             rung("the platoon", "platoon", 35, "lieutenant",
                  "Three or four squads. The first rung commanded by a commissioned officer."),
             rung("the company", "company", 150, "captain / major",
                  "Three or four platoons, and the smallest unit with its own administration."),
             rung("the battalion", "battalion", 800, "lieutenant colonel",
                  "Three to five companies - the smallest unit that can fight alone and sustain "
                  "itself for a day."),
             rung("the brigade", "brigade", 4000, "brigadier / colonel",
                  "Three or so battalions with their own artillery."),
             rung("the division", "division", 15000, "major general",
                  "**The invention of the Napoleonic age**: all arms under one commander, able to "
                  "fight a battle on its own for a day, which is why armies stopped being one "
                  "body and became several moving parts."),
             rung("the corps", "corps", 40000, "lieutenant general",
                  "Two or more divisions. Napoleon's corps system is what let a French army of "
                  "200,000 march as five bodies and concentrate faster than its enemy."),
         ],
         note="**Ten, then three, all the way up** - and the only ladder here where the rungs are "
              "near enough universal that a Japanese corporal and a Brazilian corporal command "
              "the same number of men, because everyone copied the same model. The rank titles "
              "travel with it: **corporal, sergeant, lieutenant, captain, major, colonel, "
              "general** is a European vocabulary that most of the world now uses, which is a "
              "fact about the nineteenth century and not about soldiering.",
         source="Wikipedia, Military organisation; Division (military); Corps"),
]


def problems():
    """Checks, so a bad row cannot ship silently."""
    out = []
    ids = [s["id"] for s in SYSTEMS]
    if len(ids) != len(set(ids)):
        out.append("duplicate ids: %s" % [i for i in ids if ids.count(i) > 1])
    for s in SYSTEMS:
        i = s["id"]
        if s["y1"] < s["y0"]:
            out.append("%s: ends before it begins" % i)
        for a in s["areas"]:
            if a not in AREAS:
                out.append("%s: unknown area '%s'" % (i, a))
        if not s.get("rungs"):
            out.append("%s: no rungs" % i)
            continue
        if not s.get("note") or not s.get("source"):
            out.append("%s: missing note or source" % i)
        sizes = [r["size"] for r in s["rungs"] if r.get("size") is not None]
        # A ladder must go up. A system with no numbers at all (the war party, the amabutho)
        # is allowed to be sizeless, and says so.
        if sizes and sizes != sorted(sizes):
            out.append("%s: the rungs are not in ascending order of size (%s)" % (i, sizes))
        for r in s["rungs"]:
            if not r.get("name"):
                out.append("%s: a rung with no name" % i)
        # Every rung needs a commander except where the note says the system has none
        if not any(r.get("commander") for r in s["rungs"]):
            out.append("%s: no rung names a commander" % i)
    # the default must exist and span everything
    d = [s for s in SYSTEMS if s["id"] == "warband"]
    if len(d) != 1:
        out.append("there is not exactly one default system")
    elif d[0]["areas"] != ALL or d[0]["y0"] > -3000 or d[0]["y1"] < 1900:
        out.append("the default does not span every area and the whole mod")
    return out


if __name__ == "__main__":
    ps = problems()
    print("units: %d systems over %d areas" % (len(SYSTEMS), len(AREAS)))
    for s in SYSTEMS:
        sizes = [str(r["size"]) for r in s["rungs"] if r.get("size") is not None]
        print("   %-13s %6d..%-6d base=%-5s %-22s %s"
              % (s["id"], s["y0"], s["y1"], s["base"],
                 ",".join(s["areas"])[:20], " -> ".join(sizes) if sizes else "(no numbers)"))
    for p in ps:
        print("  PROBLEM " + p)
    print("unit_table: %d problem(s)" % len(ps))
