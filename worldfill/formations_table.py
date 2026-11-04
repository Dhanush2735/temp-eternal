#!/usr/bin/env python3
"""Step 40 (D10 armies in action), part 2: how armies actually stood, by place and year.

`war/FormationType.java` offers five shapes -- LINE, PHALANX, SQUARE, WEDGE, SKIRMISH -- and
nothing else: no year, no place, no weapon, no reason. A Roman legion and a Zulu impi are handed
the same five choices. This table is the other half: **which shape this army, in this place, in
this year, would have used**, and what it was for.

Rules, the same ones every table in this project obeys:

* no source, no row. Every row names the article its figures came from;
* a row is dated. `start` and `end` are years, negative for BCE, and a row with no end is not
  allowed: a formation that stopped being used must say when;
* a row is placed. The box is where it was used, not where the people who used it came from;
* `ranks` is 0 where the record does not say how deep it stood. A zero is an honest "not
  recorded"; it is not a guess;
* `mark` says how sure we are: recorded, mixed or estimated, and the estimated ones say so in the
  printed sentence.

What is missing, and said out loud: this table has no row for the Americas before 1491 and none
for Oceania. Not because those peoples did not form up -- they did -- but because no article was
read for them, and this project does not write a row it has not read.
"""

SHAPES = ("LINE", "PHALANX", "SQUARE", "WEDGE", "SKIRMISH")
ARMS = ("chariot", "spear", "pike", "javelin", "bow", "horsebow", "sword", "elephant",
        "arquebus", "musket", "rifle", "cannon")
TROOPS = ("chariot", "infantry", "cavalry", "horse", "elephant", "mixed")
PURPOSES = ("shock", "hold", "missile", "envelope", "screen")
MARKS = ("recorded", "mixed", "estimated")


class F:
    """One way of standing, in one place, for a stretch of years."""

    def __init__(self, id, name, shape, ranks, start, end, box, arm, troop, purpose,
                 needs, doing, note, src, mark):
        assert shape in SHAPES, "%s: unknown shape %s" % (id, shape)
        assert isinstance(ranks, int) and 0 <= ranks <= 60, "%s: bad ranks %s" % (id, ranks)
        assert -3000 <= start <= end <= 2026, "%s: bad years %s..%s" % (id, start, end)
        lo_la, hi_la, lo_lo, hi_lo = box
        assert -90.0 <= lo_la <= hi_la <= 90.0, "%s: bad latitude box %s" % (id, box)
        assert -180.0 <= lo_lo <= hi_lo <= 180.0, "%s: bad longitude box %s" % (id, box)
        assert arm in ARMS, "%s: unknown arm %s" % (id, arm)
        assert troop in TROOPS, "%s: unknown troop %s" % (id, troop)
        assert purpose in PURPOSES, "%s: unknown purpose %s" % (id, purpose)
        assert src, "%s: no source" % id
        assert mark in MARKS, "%s: unknown mark %s" % (id, mark)
        self.id, self.name, self.shape, self.ranks = id, name, shape, ranks
        self.start, self.end, self.box = start, end, box
        self.arm, self.troop, self.purpose = arm, troop, purpose
        self.needs, self.doing, self.note, self.src, self.mark = needs, doing, note, src, mark

    def where(self):
        lo_la, hi_la, lo_lo, hi_lo = self.box
        return (lo_la, hi_la, lo_lo, hi_lo)

    def covers(self, year):
        return self.start <= year <= self.end

    def here(self, lat, lon):
        lo_la, hi_la, lo_lo, hi_lo = self.box
        return lo_la <= lat <= hi_la and lo_lo <= lon <= hi_lo

    def years(self):
        a = abs(self.start)
        b = abs(self.end)
        return ("%s BC" % a if self.start < 0 else "AD %s" % self.start,
                "%s BC" % b if self.end < 0 else "AD %s" % self.end)


FORMATIONS = [

    # ------------------------------------------------------------------ the Bronze Age
    F("chariot_swarm", "the chariot swarm", "SKIRMISH", 0, -1500, -1200,
      (12.0, 42.0, 26.0, 60.0), "chariot", "chariot", "missile",
      "flat open ground, and a state rich enough to breed horses and keep carpenters",
      "light cars working in loose order, each crewed by a driver and an archer, loosing arrows "
      "at speed and refusing to be caught",
      "Kadesh (c. 1274 BC) is both the largest chariot battle recorded -- 5,000 to 6,000 cars -- "
      "and the earliest pitched battle anywhere for which tactics are known. Egyptian cars were "
      "built for speed rather than shock: an archer on every vehicle, and a runner alongside to "
      "finish what the arrows started. Ramesses took Sherden mercenaries to run with his own "
      "chariot at Kadesh.",
      "Chariot; Battle of Kadesh; Chariotry in ancient Egypt", "recorded"),

    # ------------------------------------------------------------------ the Classical world
    F("hoplite_phalanx", "the hoplite phalanx", "PHALANX", 8, -800, -350,
      (35.0, 42.0, 19.0, 30.0), "spear", "infantry", "shock",
      "level ground, and citizens willing to stand shoulder to shoulder",
      "a block of spearmen, shields locked, each man's shield covering his neighbour's right; "
      "when the spears broke it became a shoving match -- the othismos, the push of shields",
      "Depth was not fixed: eight was usual, four at Marathon, eight against sixteen at Syracuse, "
      "twenty-five Thebans at Delium, and fifty at Leuctra and Mantinea where Epaminondas built a "
      "hammerhead of his best hoplites on one wing. The phalanx drifted right as men edged behind "
      "the shield on their left. It was unwieldy, and once its ranks broke it was finished.",
      "Phalanx; Hoplite; Ancient Greek warfare", "recorded"),

    F("macedonian_phalanx", "the Macedonian phalanx", "PHALANX", 16, -359, -150,
      (24.0, 42.0, 19.0, 75.0), "pike", "infantry", "shock",
      "level ground above all, and a drilled professional who has trained with a two-handed pike",
      "sixteen ranks of pikes, the first five projecting their points ahead of the front rank, so "
      "the enemy meets a wall of iron before he reaches a man",
      "Philip II's sarissa, introduced around 359/358 BC, was over six metres -- roughly twice a "
      "hoplite spear -- and had to be held in both hands. It bought reach and it cost mobility: "
      "the phalanx that carried it could break almost anything in front of it and could not turn. "
      "The depth is recorded as sixteen, sometimes thirty-two.",
      "Macedonian phalanx; Sarissa", "recorded"),

    F("roman_triplex", "the Roman line of cohorts", "LINE", 3, -300, 476,
      (28.0, 60.0, -10.0, 45.0), "javelin", "infantry", "hold",
      "a state that can train and pay men for years, and officers who can pass orders down",
      "three lines with gaps between the blocks, so a line that is failing can be relieved by the "
      "one behind it without the whole army coming apart",
      "The manipular legion fought in three lines -- hastati, principes, triarii -- in a "
      "checkerboard (quincunx) with deliberate gaps; a maniple was about 120 men. The gaps are "
      "the point: a phalanx is a wall that fails when it cracks, and this is a jointed thing that "
      "can plug a hole, pull a tired unit back, or feed fresh men forward. Marius's reforms ended "
      "the class-divided manipular system and made the cohort the unit, with one kind of heavy "
      "legionary in place of three grades of spearman.",
      "Roman infantry tactics", "recorded"),

    F("war_elephant", "the elephant screen", "WEDGE", 0, -1000, 1800,
      (8.0, 35.0, 68.0, 92.0), "elephant", "elephant", "shock",
      "a kingdom that can catch, feed and train elephants, which is a handful of states and no "
      "more",
      "a line of elephants pushed at the enemy's front to break it, or held as a wall no horse "
      "will charge; behind them the infantry does the killing",
      "India's earliest army was fourfold -- infantry, cavalry, elephants and chariots -- and the "
      "Mahabharata gives the akshauhini as one chariot, one elephant, three horse and five foot. "
      "The war elephant appears in India after 1000 BCE and is central to northern Indian armies "
      "by 500 BCE; Chandragupta Maurya had 9,000 of them, and Darius III took about 50 to "
      "Gaugamela in 331 BC. It was still in use in the early nineteenth century. A mahout rode "
      "the neck and archers or javelin-men sat in the howdah.",
      "War elephant; Military history of India; Ancient warfare", "recorded"),

    # ------------------------------------------------------------------ the middle ages
    F("shield_wall", "the shield wall", "LINE", 2, 450, 1100,
      (50.0, 63.0, -8.0, 18.0), "spear", "infantry", "hold",
      "nothing but men who will stand. It is the cheapest formation in this table and the one "
      "that asks least of a state",
      "a line of men shoulder to shoulder with shields overlapping, spears over the top, and "
      "missiles thrown from behind it before the lines meet",
      "The Anglo-Saxons called it bordweall or scyldburh, the shield-wall and the "
      "shield-fortress; the Old Norse word is fylking. Both words survive in poetry written close "
      "to the fighting -- scyldburh is in The Battle of Maldon, on the 991 raid it describes. At "
      "Hastings in 1066 the English held housecarls in the centre with a shield wall across the "
      "front, and lost because part of the line broke formation and went down after the men it "
      "was chasing. That is what a shield wall does when it stops being a wall.",
      "Shield wall; Anglo-Saxon warfare", "recorded"),

    F("mongol_horsebow", "the steppe horse archers", "SKIRMISH", 0, 1206, 1400,
      (35.0, 55.0, 60.0, 125.0), "horsebow", "horse", "envelope",
      "remounts, and a commander whose men will ride away from a fight on purpose and not read "
      "it as running",
      "loose order of mounted bowmen who will not close, and who will break off and draw a "
      "pursuing army onto an ambush prepared days before",
      "The feigned retreat was the Mongols' most effective tactic and the one that needs the most "
      "discipline: it only works if the men who ride away come back. It could be played out over "
      "days, the riders changing mounts and always keeping just ahead of pursuit, until the "
      "pursuers reached the place the rest of the army was waiting. Almost always outnumbered, "
      "the Mongols won by refusing to stand where they could be counted.",
      "Mongolian Warfare (the TOTA project, on the Mongol military)", "mixed"),

    F("nagae_yari", "the ashigaru pike block", "LINE", 3, 1550, 1615,
      (30.0, 41.0, 130.0, 142.0), "pike", "infantry", "hold",
      "a daimyo who can arm and drill peasants in numbers, and a supply of long shafts",
      "two or three rows of pikes four and a half to six and a half metres long, moving their "
      "points together on the word of command, with matchlocks and short spears in the same line",
      "After the Onin War (1467-77) brought large group battles, ashigaru foot soldiers with the "
      "nagae yari became the main force in Japanese armies in the second half of the sixteenth "
      "century. The pikemen were trained to move their pikes in unison under command -- which is "
      "the whole difference between a pike block and a crowd with sticks -- and they formed lines "
      "with tanegashima matchlocks and short spears alongside them. It is the European pike block "
      "arrived at independently.",
      "Nageyari; Ashigaru", "recorded"),

    F("swiss_square", "the Swiss pike square", "SQUARE", 0, 1400, 1525,
      (45.0, 48.0, 6.0, 11.0), "pike", "infantry", "shock",
      "mountain cantonment, drilled men, and no gentleman on a horse giving orders",
      "a deep compact block of pikes that advances faster than anything on foot has a right to, "
      "and that cavalry cannot touch",
      "The Gewalthaufen is the formation the Spanish tercio was built to answer, and the measure "
      "of it is in what the Spanish changed: the tercio's advantage over 'the Swiss compact "
      "frame' was that it could divide into mobile units, even into individual melee groups, "
      "without losing cohesion. The square could not.",
      "Tercio; Pike and shot", "mixed"),

    # ------------------------------------------------------------------ the gunpowder centuries
    F("tercio", "the Spanish tercio", "SQUARE", 0, 1534, 1704,
      (36.0, 52.0, -10.0, 18.0), "arquebus", "mixed", "hold",
      "a crown that pays its infantry year-round, and officers who can hold a square together "
      "while it breaks into pieces and reforms",
      "pikes in a deep central block, shot on the flanks and loose about the edges, each part "
      "covering the other: the pikes stop the horse, the shot worries the pikes",
      "Standardized by Charles V's ordinance of 1534: about 3,000 men in twelve companies, ten of "
      "pikes and two of arquebusiers, a pike company 219 pikes and 20 muskets, an arquebusier "
      "company 224 and 15. The point of it, and the reason it outlasted the Swiss square, is "
      "that it could come apart into units that fought alone and still behaved like an army. "
      "Philip V abolished it in 1704 and replaced it with the regiment on the French model.",
      "Tercio; Pike and shot", "recorded"),

    F("swedish_brigade", "the Swedish brigade", "LINE", 6, 1631, 1721,
      (55.0, 68.0, 10.0, 30.0), "musket", "mixed", "shock",
      "drill enough to fire on command, and light guns that can move with the infantry",
      "six ranks instead of ten, musketeers massed, and a single volley from three ranks -- "
      "kneeling, crouching and standing -- fired together instead of rank by rank",
      "Gustavus Adolphus cut the line from eight or ten ranks to six, raised the number of "
      "musketeers, and adopted the salvo: the front rank kneeling, the second crouching, the "
      "third standing, all loosing at once. A squadron was 216 pikes to 192 muskets, thirteen "
      "muskets to eight pikes; three or four squadrons made a brigade, drawn up as an arrowhead "
      "or a diamond. The brigade was introduced in 1631. Thinner, quicker to wheel, and able to "
      "put most of its muskets on the same frontage with fewer men -- which is why it beat the "
      "tercio at Breitenfeld.",
      "Line infantry; Battle of Breitenfeld (1631)", "recorded"),

    F("line_and_column", "the line and the column", "LINE", 3, 1791, 1815,
      (40.0, 60.0, -10.0, 30.0), "musket", "mixed", "hold",
      "a battalion drilled to the regulation, officers who can change from column to line under "
      "fire, and skirmishers who can be trusted out in front on their own",
      "column to move, line to shoot: two or three ranks shoulder to shoulder to bring every "
      "musket to bear, and a deep column to get there",
      "The line maximised fire and covered frontage; its thinness made artillery less effective "
      "against it; and long lines were hard to keep dressed over ditches, fences and trees. The "
      "French answered with tirailleurs -- light infantry in open order ahead of the main body, "
      "screening it, harassing the enemy line and disordering it before the close-order battalions "
      "arrived -- and with the ordre mixte, some battalions in line and some in column together. "
      "The term colonne d'attaque appears in the French Reglement of 1791, though historians warn "
      "against reading it as a doctrine of always charging in deep columns.",
      "Napoleonic tactics", "recorded"),

    F("civil_war_skirmish", "the skirmish line", "LINE", 2, 1861, 1865,
      (30.0, 45.0, -95.0, -75.0), "rifle", "infantry", "screen",
      "a company that can be trusted to fight in fours, fifty yards apart, with nobody watching "
      "them",
      "a company split in two: one platoon out in front as a skirmish line in groups of four at "
      "five-pace intervals, the other 150 paces behind as its reserve",
      "The line of battle was still two ranks with files touching elbows, colours in the centre "
      "and a guide at each end. But Earl Hess argues the skirmisher reached its apogee in this "
      "war: the textbook deployment had a company break into two platoons, one forming the "
      "skirmish line and the other a reserve 150 paces back, skirmishers fighting in 'comrades in "
      "battle' groups of four at five-pace intervals and twenty to forty paces between groups. "
      "Rifled muskets had made the shoulder-to-shoulder line expensive to stand in.",
      "Infantry in the American Civil War", "recorded"),

    F("open_order", "open order", "SKIRMISH", 0, 1866, 1918,
      (42.0, 58.0, 2.0, 22.0), "rifle", "infantry", "screen",
      "a breech-loader, a company commander allowed to pick his own line of advance, and men "
      "trained to use cover without being told",
      "companies moving in small columns and shaking out into a skirmish line only once they are "
      "within effective range; the advance is by fire, not by shoulder",
      "In the Franco-Prussian War the Prussians did not advance in column or line: infantry moved "
      "in small groups that artillery and the French chassepot could not get a purchase on, "
      "company columns of about 250 men dispersing into extended order -- a few paces between "
      "each man -- to fire and press the attack, and preferably an enveloping one. The Dreyse "
      "breech-loader is what made it possible; by the 1870s breech-loaders, repeaters and machine "
      "guns had made close-order line infantry obsolete everywhere.",
      "Franco-Prussian War; Line infantry", "mixed"),

    # ------------------------------------------------------------------ Africa, the nineteenth century
    F("zulu_horns", "the horns of the buffalo", "WEDGE", 0, 1817, 1879,
      (-30.0, -22.0, 27.0, 33.0), "spear", "infantry", "envelope",
      "age-grade regiments drilled to run, and a commander who can keep three bodies of men "
      "moving to one plan without anyone seeing the whole field",
      "four bodies: a chest of veterans that pins the enemy's front, two horns of young runners "
      "that go round both flanks, and a reserve held out of sight behind",
      "Systematised by Shaka out of far older local practice during the Ndwandwe-Zulu War of "
      "1817-19. The chest (isifuba) closed and pinned; while it held, the horns (izimpondo) -- "
      "the youngest and fastest -- encircled both flanks and met behind; the loins (umuva) were "
      "the reserve. Shaka also rearmed his men with the iklwa, a short stabbing spear, a larger "
      "shield, and no sandals. It is a formation built to destroy an army rather than to hold "
      "ground, and it did exactly that at Isandlwana.",
      "Impi; Shaka", "recorded"),

    # ------------------------------------------------------------------ the modern centuries
    F("fireteam", "the fire team", "SKIRMISH", 0, 1915, 2026,
      (-60.0, 72.0, -180.0, 180.0), "rifle", "infantry", "envelope",
      "a soldier trusted to choose his own cover and keep moving without an officer telling him "
      "to, which is the rarest requirement in this table",
      "small groups a few paces apart, one laying down fire while another moves, bypassing "
      "anything that can shoot back and going through where the line is weakest",
      "The German army formed its first experimental assault unit in the spring of 1915, and the "
      "Stoßtruppen it grew into fought the way every army fights now: a short sharp bombardment, "
      "then small mutually supporting teams moving in dispersed order, using what cover there is, "
      "avoiding strongpoints rather than assaulting them, and breaking in where the defence is "
      "thinnest. The standard modern fire team is four or fewer men -- an automatic rifleman, a "
      "grenadier, a rifleman and a leader; the US Marines adopted a three-by-three organisation "
      "in 1942 and a thirteen-man squad of three four-man teams in 1943. Infiltration is now so "
      "completely folded into ordinary manoeuvre warfare, down to fire and movement at section "
      "level, that the word no longer means anything separate. This is the only row in the table "
      "that is still in force.",
      "Fireteam; Infiltration tactics; Stormtroopers (Imperial Germany); Trench warfare",
      "recorded"),
]

# --- what ground each one wants -----------------------------------------------------------
#
# Kept as its own table rather than another column because it answers a different question, and
# because it is the reason a battle comes out the way it does: the formation that cannot fight on
# this ground is the formation that loses. "level" wants a flat field and is in trouble the moment
# it is not on one; "open" wants room to move or to shoot; "broken" wants cover, walls, woods or
# rough going; "any" will fight on whatever there is, which is often worth more than being better.
#
# Sourced where the article says it: the Macedonian phalanx is recorded as needing level terrain,
# the Roman maniple as gaining its advantage in rough country, and open order as a direct answer to
# ground where close-order men could not live.

GROUND = {
    "chariot_swarm": "level",
    "hoplite_phalanx": "level",
    "macedonian_phalanx": "level",
    "roman_triplex": "broken",
    "war_elephant": "open",
    "shield_wall": "any",
    "mongol_horsebow": "open",
    "nagae_yari": "any",
    "swiss_square": "level",
    "tercio": "any",
    "swedish_brigade": "open",
    "line_and_column": "open",
    "civil_war_skirmish": "broken",
    "open_order": "broken",
    "zulu_horns": "open",
    "fireteam": "broken",
}
GROUNDS = ("level", "open", "broken", "any")

assert set(GROUND) == set(f.id for f in FORMATIONS), \
    "every formation needs a ground: %s" % (set(f.id for f in FORMATIONS) ^ set(GROUND))
for k, v in GROUND.items():
    assert v in GROUNDS, "%s: unknown ground %s" % (k, v)

GAPS = (
    "No row for the Americas before 1491, none for Oceania, and none for sub-Saharan Africa "
    "outside the Zulu kingdom. Not because those peoples did not form up, but because no article "
    "was read for them and this project does not write a row it has not read."
)
