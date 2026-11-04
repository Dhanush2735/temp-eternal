#!/usr/bin/env python3
"""Step 40 (D10 armies in action), part 4: the numbers behind how a siege comes out.

`war/SiegeEngineController.java` treats a siege as block damage: every five seconds a random block
near the target is cracked, gravelised or deleted. There is no food, no water, no disease, no
relief army, no negotiation, no date it has to end, and no way it ends at all.

This table is the replacement. A siege is **a race between two clocks** — the wall's and the food's
— with five ways it can end, and the commonest of them is the one nobody guesses:

> Under the accepted rules of war a town taken by force could be sacked, and one that surrendered
> could not. So the commonest ending was an agreement: *if no relieving army arrives by a named
> day, we open the gates and march out with our arms and our lives.*

It holds five things:

* **WALLS** — what the wall of this place and year was, what it resists, and whether it can be
  mined or reached at all. Dated and placed, exactly like the formation table, because the
  Theodosian walls in 1453 and a trace italienne in 1600 are not the same problem.
* **METHODS** — what a besieger of this year could do about a wall, how many days the best of them
  needs to open a practicable breach, and what it costs the men working it.

**How the two are calibrated.** A method's `days` is what it needs, working alone at full effort,
to break a wall of `resist` 1.0; a wall's `resist` is the multiplier on that. The numbers were
fitted to sieges whose length a source recorded, and the register lands on them:

| siege | year | wall | the register | the record |
|---|---|---|---|---|
| Rochester | 1215 | curtain, mined | ~50 days | 11 October to 30 November |
| Constantinople | 1453 | theodosian, bombarded | ~53 days | 6 April to 29 May, 53 days |
| Kenilworth | 1266 | curtain, ringed by water | no breach possible; decided by hunger | 172 days, two days of food left |
| Vicksburg | 1863 | field entrenchments | ~52 days | 18 May to 4 July, 47 days |
* **ENDINGS** — the five ways it stops, and how often each.
* **FOOD** — grain per head per day, the ration cut, the dying, and the "useless mouths".
* **CLOCKS** — how long the besiegers can sit there before disease, winter, their own supply line
  or a greater threat elsewhere takes them away.

Sources are on every row. `mark` is one of `recorded` (a source said this number), `derived`
(arithmetic on a source's number) or `estimated` (this register's reading, and the sentence says
so).
"""

# ---------------------------------------------------------------- the walls of the world

class W:
    """One kind of fortification, where and when it stood, and what it is worth."""

    def __init__(self, id, name, start, end, box, scale, mine, storm, resist, note, src,
                 mark="recorded", scope="general"):
        assert id and name, "a wall needs an id and a name"
        assert -4000 <= start < end <= 2026, "%s: years %s..%s" % (id, start, end)
        assert len(box) == 4 and box[0] < box[1] and box[2] < box[3], "%s: box %s" % (id, box)
        assert scale in ("low", "high"), "%s: scale %s" % (id, scale)
        assert mine in ("yes", "no", "part"), "%s: mine %s" % (id, mine)
        assert 1.0 <= storm <= 3.5, "%s: storm %s" % (id, storm)
        # resist is a multiplier on the days the age's best method needs to open a practicable
        # breach in a wall of resist 1.0. It is not a height and it is not a thickness: it is
        # calibrated, wall by wall, against a siege whose length a source recorded.
        assert 0.2 <= resist <= 80.0, "%s: resist %s" % (id, resist)
        assert note and src, "%s needs a note and a source" % id
        assert mark in ("recorded", "derived", "estimated"), "%s: mark %s" % (id, mark)
        # scope is the honest admission that a register working from a latitude and a year cannot
        # know whether this particular castle happens to be concentric. "general" is the ordinary
        # wall of this place and year; "special" is a kind of wall a caller has to name, because
        # the only thing that tells you Krak des Chevaliers is concentric is Krak des Chevaliers.
        assert scope in ("general", "special"), "%s: scope %s" % (id, scope)
        self.scope = scope
        self.id = id
        self.name = name
        self.start = start
        self.end = end
        self.box = box
        self.scale = scale
        self.mine = mine
        self.storm = storm
        self.resist = resist
        self.note = note
        self.src = src
        self.mark = mark


WORLD = (-60.0, 72.0, -180.0, 180.0)
EURLEV = (28.0, 62.0, -12.0, 45.0)      # Europe and the Latin Levant
MED = (30.0, 45.0, -5.0, 40.0)          # the Mediterranean proper: ashlar is Greek and Roman
NEAREAST = (10.0, 42.0, 24.0, 66.0)     # the Nile to the Zagros
CHINA = (18.0, 46.0, 94.0, 126.0)
CONST = (40.8, 41.2, 28.5, 29.2)        # Constantinople, and only Constantinople

WALLS = [
    W("earthwork", "a ditch, a bank and a palisade", -4000, 1900, WORLD, "low", "yes", 1.0, 0.5,
      "The oldest way to keep people out and the commonest. Earth and timber take a mine happily "
      "and a ladder almost as happily; the bank is the obstacle, not the height.",
      "Wikipedia, 'Siege': fortification by ditch and bank from prehistory; EBSCO, 'Ancient and "
      "Medieval Sieges', on escalade in a 27th-century BC Egyptian wall painting at Dehashe",
      "recorded"),
    W("mudbrick", "mudbrick walls with towers and a glacis", -3000, 1400, NEAREAST, "high", "yes", 1.3, 2.0,
      "Sun-dried brick in enormous thickness, usually on a rampart and often behind a glacis. It "
      "is soft enough to mine and too thick to batter quickly, so most of these places were taken "
      "by hunger, by treaty, or by someone inside opening a gate.",
      "Wikipedia, 'Siege': the Egyptian siege of Megiddo in the fifteenth century BC lasted seven "
      "months before the town sued for peace; the Hittite siege of a rebellious Anatolian vassal "
      "ended when the queen mother came out and begged for mercy",
      "recorded"),
    W("ashlar", "a cut-stone curtain with towers", -500, 600, MED, "high", "yes", 1.7, 3.0,
      "Carefully squared blocks laid without mortar, with towers at intervals so that the wall can "
      "be swept along its own length. A ram works on it only at a corner; a mine works anywhere "
      "the ground is dry.",
      "Wikipedia, 'Siege warfare in ancient Rome': Syracuse held eighteen months and fell only "
      "when the pro-Roman party opened a gate in the night; Numantia held near a year and the "
      "survivors burned the city rather than accept unconditional surrender",
      "recorded"),
    W("rammed_earth", "rammed earth faced with brick", -700, 1900, CHINA, "high", "part", 1.9, 5.0,
      "A core of earth rammed in layers between board frames and faced with brick, often tens of "
      "metres thick: it absorbs what would shatter masonry, and a mine through it is a mine "
      "through a hillside. The gates are the weak point and the gate is where the fighting is.",
      "Wikipedia, 'Siege of Suiyang': Xu Yuan stored a year's food inside, and the siege turned "
      "on the food and not on the wall; the fortifications held months after the stores ran out",
      "estimated"),
    W("curtain_and_tower", "a stone curtain with flanking towers", 1000, 1520, EURLEV, "high",
      "yes", 1.9, 4.1,
      "The ordinary medieval castle or walled town: a stone curtain, towers that let the defenders "
      "shoot along the face, and a gatehouse. Stone-throwing engines knock pieces off it; a mine "
      "brings a piece down; hunger does the rest. 'Usually by hunger, not by assault.'",
      "English Heritage, 'Medieval siege warfare': Kenilworth, 1266, began 25 June and lasted 172 "
      "days, the garrison surrendering with two days' food left; most medieval castle sieges in "
      "Britain lasted under two months. The Castle Rolls: 'Usually by hunger, not by assault'",
      "recorded"),
    W("concentric", "wall within wall", 1150, 1520, EURLEV, "high", "yes", 2.4, 7.0,
      "Two independent rings, the inner commanding the outer, so that losing the first wall does "
      "not lose the place: the attackers win a courtyard and find another wall behind it. It is a "
      "fortification designed to make a breach not mean very much.",
      "Wikipedia, 'Medieval warfare', on the concentric castle and the Crusader examples; "
      "English Heritage on Dover, 1216, where Prince Louis brought down a tower and the garrison "
      "fought him back out of the breach and was never taken",
      "estimated", scope="special"),
    W("theodosian", "the triple land wall of Constantinople", 413, 1453, CONST, "high", "yes",
      2.6, 9.0,
      "A moat, an outer wall, a terrace, an inner wall, and ninety-six towers, standing a thousand "
      "years. It turned every army that came at it until an age arrived that could bring a bronze "
      "monster to the foot of it and feed it shot.",
      "Wikipedia, 'Siege of Constantinople (1453)': 6 April to 29 May, 53 days; ~69 guns; Orban's "
      "Basilic 27 feet long with a 30-inch bore, hurling 540-600 kg over a mile, three hours to "
      "reload, moved by 60-90 oxen and 200-400 men; the barrage opened 12 April along a four-mile "
      "front and the final assault came at half past one on the morning of 29 May",
      "recorded"),
    W("trace_italienne", "low thick sloping ramparts with angular bastions", 1494, 1870, WORLD,
      "low", "yes", 2.1, 4.0,
      "The answer to the siege train: stop building upward, start building outward. Low, thick, "
      "earth-backed, angled into bastions so that every face is swept by fire from another, with a "
      "ditch, a glacis and ravelins in front. It absorbs what a vertical masonry wall cannot.",
      "Rebus, 'Cannon and Fortresses in Early Modern Europe': Charles VIII invaded Italy in 1494 "
      "with 18,000 men and forty siege guns. Modern War Institute: at Monte San Giovanni Campano "
      "in February 1495 his bronze guns did in hours what had taken weeks to months",
      "recorded"),
    W("fortress_belt", "a bastion trace with ravelins, a glacis and outworks", 1670, 1918, WORLD,
      "low", "yes", 2.3, 3.0,
      "The siege become a procedure: an attacker digs forward by saps and parallels, step by step, "
      "and at every step asks whether the garrison will save everyone the trouble. The defence is "
      "an arithmetic of days, and a commander on either side can usually say when the place will "
      "fall.",
      "New World Encyclopedia, 'Siege', on Vauban: zigzag saps so they cannot be enfiladed, a "
      "parallel at artillery range with gun emplacements, the process repeated until the guns are "
      "close enough to breach; and after each step the besiegers asked the besieged to surrender",
      "recorded"),
    W("field_entrenchment", "trenches, redoubts and wire", 1850, 1945, WORLD, "low", "yes", 2.6,
      5.1,
      "No wall at all: a line dug in the ground, deepened and wired until it is a fortification "
      "hundreds of kilometres long. It cannot be outflanked, so it is broken by weight at one "
      "chosen point, or it is simply sat in front of.",
      "Wikipedia, 'Siege': the twentieth century replaced the fortified place with the fortified "
      "front; Britannica, 'Siege of Sarajevo': over 300 shells a day on the city",
      "estimated"),
    W("modern_city", "a city held street by street", 1914, 2026, WORLD, "high", "no",
      3.0, 60.0,
      "In the twentieth century the wall is the ring of guns around the city, and the siege is a "
      "question of what can be carried in past them. Leningrad was never entered in 872 days and "
      "lost a million and a half of its people; Sarajevo was shelled for 1,425 and fed by air.",
      "Wikipedia, 'Siege of Leningrad': 872 days, never taken, an estimated 1.5 million dead of a "
      "prewar 3.2 million; Britannica, 'Siege of Sarajevo': 1,425 days, the longest siege in "
      "modern European history, relieved by an airlift of over 12,000 flights",
      "recorded"),
]

# ---------------------------------------------------------------- what a besieger can do


class M:
    """One way of going about a wall, when it was available, and what it costs."""

    def __init__(self, id, name, start, end, days, assault, risk, needs, note, src,
                 mark="recorded"):
        assert id and name, "a method needs an id and a name"
        assert -4000 <= start < end <= 2026, "%s: years %s..%s" % (id, start, end)
        # days is what this method needs, working alone at full effort, to open a practicable
        # breach in a wall of resist 1.0. Zero means it cannot open a breach at all: blockade
        # only starves, and escalade and the siege tower deliver men rather than a hole.
        assert 0 <= days <= 120, "%s: days %s" % (id, days)
        assert isinstance(assault, bool), "%s: assault must be true or false" % id
        assert 0.0 <= risk <= 1.5, "%s: risk %s" % (id, risk)
        assert needs in ("", "ground", "approach", "low"), "%s: needs %s" % (id, needs)
        assert note and src, "%s needs a note and a source" % id
        assert mark in ("recorded", "derived", "estimated"), "%s: mark %s" % (id, mark)
        self.id = id
        self.name = name
        self.start = start
        self.end = end
        self.days = days
        self.assault = assault
        self.risk = risk
        self.needs = needs
        self.note = note
        self.src = src
        self.mark = mark


METHODS = [
    M("blockade", "sit outside and wait", -4000, 2026, 0, False, 0.0, "",
      "The oldest method and the one most assured to succeed: cut off everyone and everything and "
      "let the stores do the work. It is slow, it is expensive, it exposes the besiegers to a "
      "relieving army behind them, and it is what most sieges actually were.",
      "Wikipedia, 'Siege': 'The most common practice of siege warfare was to lay siege and wait "
      "for the surrender of the enemies inside.' WarHistory.org: the blockade was the final "
      "method and the one most assured to succeed, and the last resort because of the time",
      "recorded"),
    M("escalade", "ladders against the wall", -4000, 1945, 0, True, 1.0, "low",
      "The cheapest attack there is and the likeliest to kill the men who try it. It works against "
      "surprise, against a thin garrison, or against a place whose defenders have already given "
      "up, and commanders used it early precisely because one quick attempt was worth making "
      "before the expensive part began.",
      "EBSCO, 'Ancient and Medieval Sieges': escalade was not effective against walls higher than "
      "ten metres. The Castle Rolls: 'the cheapest attack available and the one most likely to "
      "kill the men who tried it'; Britannica: storm or escalade rarely succeeded except by "
      "surprise or treachery",
      "recorded"),
    M("ram", "a ram or a bore under a penthouse", -2500, 1500, 30, False, 0.5, "approach",
      "A heavy timber swung or worked inside a wheeled shed, brought against a gate or a corner. "
      "Best against timber; against stone it works at the corners, where two faces meet and the "
      "masonry has nothing behind it. The defenders answer with hook-ended ropes to overturn the "
      "shed and with beams dropped from the parapet.",
      "HistoryNet, 'How to Capture a Castle with Siegecraft': rams were most effective against "
      "timber, particularly the oak doors of a gate, and against stone worked best on corners; "
      "defenders countered by grabbing the ram with hooks and dropping beams on the penthouse. "
      "Employed at Acre in 1191",
      "recorded"),
    M("siege_tower", "a wheeled tower with a drawbridge", -900, 1450, 0, True, 0.6, "approach",
      "A timber tower built where it is wanted, tall enough to look over the parapet, with "
      "archers in its upper storeys to sweep the wall-walk and a drawbridge to drop onto it. Built "
      "on the spot because nothing that size travels, and used when ladders have already failed.",
      "Wikipedia, 'Siege tower': of unwieldy dimensions and so mostly built on site; mainly "
      "erected where the defence could not be overcome by escalade, mining or breaking the gates. "
      "Britannica: European engineers built wheeled belfroys from the ninth century",
      "recorded"),
    M("mine", "a gallery under the wall, propped and fired", -4000, 1945, 25, False, 0.4,
      "ground",
      "The most reliable way to break masonry before gunpowder, and it needs no machine at all: "
      "dig under the foundation, hold the cavity on timber props, pack it with brushwood and "
      "grease, fire it, and let the wall drop into the hole. It is answered by counter-mining, it "
      "is defeated by a wet ditch, and living rock defeats it absolutely.",
      "The Castle Rolls: 'Mining was the most reliable way to break masonry before gunpowder.' "
      "English Heritage: at Rochester in 1215 King John asked for forty of the fattest pigs of "
      "the sort least good for eating and put the fat under the props; the south-east corner came "
      "down on 30 November. At Dryslwyn in 1287 the wall came down early and fell on the "
      "attackers. Wikipedia: garrisons countermined, listening for the digging",
      "recorded"),
    M("trebuchet", "a counterweight stone-thrower", 1150, 1500, 60, False, 0.2, "",
      "The outstanding medieval stone-thrower: a beam on a pivot, a counterweight on the short "
      "arm, a sling on the long one. It knocks the tops off towers and the heads off parapets, and "
      "its greatest use was probably to persuade the garrison that it was time to talk.",
      "EBSCO, 'Ancient and Medieval Sieges': the outstanding medieval innovation, the throwing arm "
      "on a pivot with the counterweight end the shorter; the earliest trebuchets used men for "
      "counterweights. English Heritage: the first recorded use in England was at Dover in 1216",
      "recorded"),
    M("bombard", "great bronze bombards", 1420, 1530, 12, False, 0.2, "",
      "The first siege guns: enormous, cast in bronze, hauled to the walls by oxen, firing stone "
      "ball over a mile and taking hours to load. What a mine did in weeks and hunger did in "
      "months, a battery now did in days — which is the whole of what changed in 1453.",
      "The Castle Rolls: 'What a mine did in weeks and hunger did in months, a battery now did in "
      "days'; Bamburgh in 1464 is the first English castle known to have been reduced by gunpowder "
      "artillery. Wikipedia, 'Siege of Constantinople (1453)': Orban's bombard took three hours "
      "to reload and is said to have collapsed under its own recoil after six weeks",
      "recorded"),
    M("battery", "a mobile siege train", 1494, 1860, 8, False, 0.2, "",
      "Guns cast like church bells, light enough to sit on wheeled carriages and be drawn by "
      "horses, arriving with the army and opening fire the day it gets there. In February 1495 "
      "forty of them took a fortress in hours that had previously cost weeks.",
      "Wikipedia, 'Italian Wars': Charles VIII brought the first truly mobile siege train, the "
      "guns mounted on wheeled carriages drawn by horses rather than oxen, so they could be "
      "emplaced on arrival. Modern War Institute: at Monte San Giovanni Campano, roughly forty "
      "horse-drawn bronze guns did in hours what had taken weeks to months",
      "recorded"),
    M("parallel", "saps and parallels, step by step", 1670, 1914, 30, False, 0.1, "ground",
      "Zigzag trenches walked forward so that no defender can fire down their length; a parallel "
      "dug across at artillery range with gun emplacements; then another, and another, until the "
      "guns are close enough to open a breach. After each step the besiegers ask the garrison to "
      "surrender, and most of the time that is how it ends.",
      "New World Encyclopedia, 'Siege': saps had to be sharply jagged so the defenders could not "
      "enfilade them; a parallel followed at artillery range, the process repeated until the guns "
      "could breach; and 'after each step in the process, the besiegers would ask the besieged to "
      "surrender'",
      "recorded"),
    M("heavy_guns", "siege artillery on a modern scale", 1860, 1945, 10, False, 0.2, "",
      "Rifled, breech-loading, firing high explosive, in quantities that make the arithmetic of a "
      "breach a matter of hours. The defence answers by ceasing to be a wall at all and becoming "
      "a trench, a dugout and a wire entanglement.",
      "Wikipedia, 'Siege': twentieth-century siegecraft; Britannica, 'Siege of Budapest': the "
      "Soviet siege reduced the city in about fifty days, 38,000 of the civilians dying of "
      "starvation, military action and massacre",
      "estimated"),
]

# ---------------------------------------------------------------- the five endings


class E:
    """One way a siege stops."""

    def __init__(self, id, name, share, sack, when, note, src, mark="estimated"):
        assert id and name, "an ending needs an id and a name"
        assert 0.0 < share < 1.0, "%s: share %s" % (id, share)
        assert isinstance(sack, bool), "%s: sack must be true or false" % id
        assert when and note and src, "%s needs when, a note and a source" % id
        assert mark in ("recorded", "derived", "estimated"), "%s: mark %s" % (id, mark)
        self.id = id
        self.name = name
        self.share = share
        self.sack = sack
        self.when = when
        self.note = note
        self.src = src
        self.mark = mark


ENDINGS = [
    E("terms", "the gates open on a date", 0.35, False,
      "the garrison offers to surrender if no relieving army arrives by a named day, and marches "
      "out with its arms and its lives",
      "The commonest ending by a wide margin, and the one the rules of war were built to produce: "
      "a town taken by force could be sacked and one that surrendered could not, so both sides had "
      "every reason to prefer an agreement. It saved the besieger months and the defender a "
      "massacre, and it was honourable on both sides.",
      "The Castle Rolls: 'The commonest ending was an agreement. A garrison would offer a "
      "conditional surrender: if no relieving army arrives by a named date, we open the gates and "
      "march out with our arms and our lives. It saved the besieger months and the defender a "
      "massacre, and it was regarded as honourable on both sides.' Odiham, 1216: thirteen men "
      "held Prince Louis for a week or more and left with the honours of war. Wikipedia, "
      "'Siegecraft': negotiations would frequently take place during the early part of the siege",
      "recorded"),
    E("starvation", "the food runs out", 0.23, True,
      "the stores are gone, the ration has been cut and cut again, and the garrison has not opened "
      "the gates",
      "The ending that decides most of the rest. It is what 'the one most assured to succeed' "
      "actually means in practice, and it is measured in days of bread: Leningrad began its siege "
      "with thirty-five days of grain and flour and buried a million and a half of its people; "
      "Kenilworth's twelve hundred surrendered with two days' food in the magazine.",
      "Wikipedia, 'Effects of the siege of Leningrad': on 12 September 1941 the city's provisions "
      "were calculated to last 35 days for grain and flour, 31 for groats, 33 for meat, 45 for "
      "fats and 60 for sugar; the ration fell to 125 grams of bread a day. English Heritage: "
      "Kenilworth's garrison surrendered in 1266 with two days of food left",
      "recorded"),
    E("relief", "a field army drives the besiegers off", 0.18, False,
      "an army of the defenders' own arrives, and the besiegers either fight it or go",
      "The ending every garrison was waiting for, and the whole reason a wall was worth building: "
      "a fortification existed to hold out long enough for help to come. It does not have to be an "
      "army — at Lilybaeum the siege of nine years was ended by a battle at sea, and at Sarajevo "
      "by an airlift of more than twelve thousand flights.",
      "Wikipedia, 'Siege': at Alesia the Gauls surrendered after their relief force met defeat "
      "against Caesar's auxiliary cavalry. WorldAtlas: the nine-year siege of Lilybaeum ended not "
      "by assault but with the Roman naval victory at the Aegates. Britannica: Sarajevo came near "
      "to starvation before the UN airlift, over 12,000 flights from more than 20 countries",
      "recorded"),
    E("abandonment", "the besiegers go home", 0.14, False,
      "disease in the camp, winter coming on, their own supply failing, or a greater threat "
      "somewhere else",
      "Most sieges in history were lost by the people outside. An army sitting still in its own "
      "filth dies of dysentery and typhus faster than the garrison dies of hunger, it has a "
      "harvest to get home for, and its king may need it three provinces away.",
      "Wikipedia, 'Siege': 'Failing a military outcome, sieges can often be decided by starvation, "
      "thirst, or disease, which can afflict either the attacker or defender.' The History Press: "
      "a besieger that waited 'lost the momentum of his attack on enemy lands, while laying "
      "himself open to the risk of a relieving force arriving and attacking him from behind'",
      "recorded"),
    E("storm", "the place is carried", 0.10, True,
      "a practicable breach, or a ladder on an unwatched wall, and the attackers are inside",
      "The rarest ending and the one that costs everything, because under the accepted rules a "
      "place taken by force could be sacked and one that surrendered could not. That is why a "
      "garrison's officers watched their own bread so carefully: the moment the wall is going to "
      "go, the price of waiting one more day is the town.",
      "WarHistoryOnline: 'Under accepted rules of war, a town captured by force could be ransacked "
      "but one that surrendered could not.' Wikipedia, 'Siege of Constantinople (1453)': the "
      "assault of 29 May after fifty-three days. Britannica, 'Siege of Budapest': about fifty "
      "days, 38,000 civilians dead",
      "recorded"),
]

# ---------------------------------------------------------------- food

# Two pounds of grain a day is the Roman march ration; Christine de Pizan allots two litres of
# wheat a man a day for a garrison; Ezekiel's siege ration is eight ounces of bread and about
# twenty-one ounces of water. 0.9 kg sits inside all three.
GRAIN_KG_PER_HEAD_PER_DAY = 0.9

# A commander cuts the ration while he still has bread, not on the day the last of it goes: that
# is the whole trick, and cutting it on the day the magazine empties buys exactly one more day.
# Twenty-one days of full rations left is when a commander who has thought about it halves the
# loaf, and from there the clock doubles.
CUT_AT_DAYS = 21
RATION_CUT = 0.5

# The useless mouths are a measure of the age of the fortified town. After that age a state
# EVACUATES its people instead of driving them out through its own gates: Leningrad got a million
# of its children, its sick and its old out across the lake, which is not the same thing at all as
# de Monluc putting 4,400 Sienese into the ditch.
USELESS_LAST_YEAR = 1789

# And there are garrisons that will not open the gates whatever is left in the magazine, because
# the state they belong to has forbidden it. Leningrad was one. Those places do not end in a
# bargain; they end in starvation or in the breach.
NO_SURRENDER_MORALE = 80

# The dying, as a share of the town a day, once the ration has been cut. Leningrad lost about
# 1.5 million of a prewar 3.2 million across 872 days, most of it in the first terrible winter;
# spread over the months of real starvation that is a little over a tenth of one per cent a day.
FAMINE_DEATHS_PER_DAY = 0.0015

# de Monluc at Siena in 1555 had the useless mouths put out to make the bread last: 4,400 people,
# of a town of something like fifteen thousand. The clock then stretches by one over what is left,
# which is less dramatic than his three months and more honest.
USELESS_SHARE = 0.30
USELESS_GAIN = 1.43

# ---------------------------------------------------------------- the besiegers' own clock

# A besieging army is on a clock too. Machiavelli's rule of thumb was that a city with a year of
# provisions could outlast any siege, which puts the outside limit near 365 days; most medieval
# English castle sieges were over in two months, because most castles had two months of food and
# not because the besiegers gave up. The base below is what an army with indifferent supply can
# sit for, before disease, winter, its own supply line or a war somewhere else takes it away.
# The patience curve is steep on purpose. An army living off the country goes home in about three
# months, whatever it is sitting in front of; an army fed by a railway, or by ships, or by a
# commissariat that has thought about it, can sit for years. days = BASE * (1 + CURVE * s^2).
# Leningrad's besiegers sat outside the city for 872 days and were driven off rather than giving
# up, so a fully supplied army has to be able to sit that long; an army living off the country
# has to be gone in about three months.
BESIEGER_BASE_DAYS = 100
BESIEGER_SUPPLY_CURVE = 10.0

# A wall that cannot be approached at all has no wall clock, and the register says so rather than
# inventing one: Kenilworth was ringed by its mere and could be neither mined nor reached, which
# is why 172 days of hunger decided it.
NO_BREACH_DAYS = -1

# ---------------------------------------------------------------- the assault

# A frontal assault goes in at the odds the numbers give, divided by what the wall is worth. An
# attacker with two men to the defender's one against a wall worth 1.9 goes in at rather better
# than evens; the same two to one against the Theodosian walls is a forlorn hope.
# An assault on a defended wall goes in at the odds below and no better, however many men are
# thrown at it: an unbroken wall is worth more than numbers. Once a practicable breach is open the
# arithmetic changes completely, and that is the whole reason anyone bothered to make one.
STORM_BASE = 0.35
STORM_PER_MAN = 0.15        # added for each attacker over and above the defender, over the wall
STORM_NO_BREACH = 0.15      # the same, when the wall is intact and the garrison is simply thin

# And a failed assault is paid for. Escalade was the cheapest attack and the one most likely to
# kill the men who tried it; the cost below is the share of the attackers a repulse costs,
# multiplied by what the wall is worth.
STORM_COST = 0.05

# A garrison with any fight left in it opens the gates rather than starve: it is the one that has
# come apart that lets the town be taken instead. Below this morale there is nobody left to make
# the decision.
BARGAINING_MORALE = 35

# Water. A cistern and a well are not the same thing and this register does not yet know which a
# town has, so this is a floor under the food clock and nothing more: three days without water
# ends any siege, whatever is in the granary.
WATER_DAYS = 3

MARKS = ("recorded", "derived", "estimated")


def check():
    """Everything this table asserts about itself."""
    p = []
    for name, rows in (("wall", WALLS), ("method", METHODS), ("ending", ENDINGS)):
        seen = set()
        for r in rows:
            if r.id in seen:
                p.append("%s id used twice: %s" % (name, r.id))
            seen.add(r.id)
    if abs(sum(e.share for e in ENDINGS) - 1.0) > 0.005:
        p.append("the five endings come to %.3f, not 1: %s"
                 % (sum(e.share for e in ENDINGS),
                    ", ".join("%s %.2f" % (e.id, e.share) for e in ENDINGS)))
    if len(ENDINGS) != 5:
        p.append("there are %d ways a siege ends, and the plan says five" % len(ENDINGS))
    if any(e.sack for e in ENDINGS if e.id in ("terms", "relief", "abandonment")):
        p.append("terms, relief and abandonment do not sack the town")
    if not all(e.sack for e in ENDINGS if e.id in ("storm", "starvation")):
        p.append("a place carried by assault or starved out is at discretion")
    if not (0.5 <= sum(e.share for e in ENDINGS if not e.sack) <= 0.9):
        p.append("the share of sieges that do not end in a sack is %.2f, which is not the point "
                 "of the register" % sum(e.share for e in ENDINGS if not e.sack))
    # every year from 1500 BC to today must have at least one wall and one method available
    for y in range(-1500, 2027, 100):
        if not any(w.start <= y <= w.end for w in WALLS):
            p.append("no kind of wall was standing in %d" % y)
        if not any(m.start <= y <= m.end for m in METHODS):
            p.append("no way of attacking a wall was known in %d" % y)
    # the whole world must be covered, not one favourite corner
    if not any(w.box == WORLD for w in WALLS):
        p.append("not one kind of wall is worldwide: the rest of the world gets no answer")
    # and a wall must be findable on every inhabited continent
    for label, lat, lon in (("Europe", 48.0, 10.0), ("Africa", 6.0, 20.0), ("Asia", 30.0, 100.0),
                            ("the Americas", -10.0, -60.0), ("Oceania", -25.0, 150.0)):
        hit = [w for w in WALLS if w.box[0] <= lat <= w.box[1] and w.box[2] <= lon <= w.box[3]]
        if not hit:
            p.append("nothing standing in %s, ever" % label)
    if USELESS_GAIN < 1.0 / (1.0 - USELESS_SHARE) - 0.02:
        p.append("putting out %.0f%% of the mouths cannot stretch the bread by less than %.2f"
                 % (USELESS_SHARE * 100, 1.0 / (1.0 - USELESS_SHARE)))
    if not all(w.scope in ("general", "special") for w in WALLS):
        p.append("every wall must say whether it can be inferred from a map reference or named")
    if not any(w.scope == "special" for w in WALLS):
        p.append("the register is claiming it can tell a concentric castle from a curtain wall by "
                 "latitude alone, which it cannot")
    if not (0 < CUT_AT_DAYS <= 90):
        p.append("a commander cutting the ration with %d days of bread left is not managing a "
                 "siege" % CUT_AT_DAYS)
    if not 0 <= NO_SURRENDER_MORALE <= 100:
        p.append("a garrison cannot refuse to surrender at morale %d" % NO_SURRENDER_MORALE)
    if FAMINE_DEATHS_PER_DAY <= 0 or FAMINE_DEATHS_PER_DAY > 0.01:
        p.append("%.4f of a town dying a day is not a famine anyone recorded" %
                 FAMINE_DEATHS_PER_DAY)
    if GRAIN_KG_PER_HEAD_PER_DAY < 0.4 or GRAIN_KG_PER_HEAD_PER_DAY > 2.0:
        p.append("%.1f kg of grain a head a day is not a siege ration" %
                 GRAIN_KG_PER_HEAD_PER_DAY)
    return p


if __name__ == "__main__":
    bad = check()
    print("walls   %d: %s" % (len(WALLS), ", ".join(w.id for w in WALLS)))
    print("methods %d: %s" % (len(METHODS), ", ".join(m.id for m in METHODS)))
    print("endings %d: %s" % (len(ENDINGS),
                              ", ".join("%s %.0f%%" % (e.id, e.share * 100) for e in ENDINGS)))
    for p in bad:
        print("  - " + p)
    print("%d problems" % len(bad))
