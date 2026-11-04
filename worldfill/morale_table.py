#!/usr/bin/env python3
"""Step 40 (D10 armies in action), part 5: why men stand, and what makes them stop.

`war/BattleSimulator.java`, as it stands, hands morale three integers:

    int attackerMorale = outcome == ATTACKER_VICTORY ? 10 : outcome == DRAW ? -2 : -15;
    int defenderMorale = outcome == DEFENDER_VICTORY ? 10 : outcome == DRAW ? -2 : -15;

No reason, no history, no era, and nothing about what the men were. An army that has not been paid
for four months and an army that has just taken a town get the same ten points. This table is the
other half: **what a body of troops is actually resting on**, and when it goes.

Three rules shape it, and they come from the sources rather than from this file:

* **two different kinds of motivation.** Berkovich's three stages of a soldier's war are to enlist,
  to fight, and -- the one that "covers the bulk of one's military service" -- to put up with the
  hardships of daily army life. The historiography of the American Civil War splits it the same
  way: convictions of duty, honour, patriotism and ideology were the principal *sustaining*
  motivation, while courage, self-respect and group cohesion were the main sources of *combat*
  motivation. A register that adds them together loses the thing worth knowing, so `kind` keeps
  them apart.
* **winning is itself a factor, and one of the largest.** The Naval Institute's study of mutiny is
  blunt about it: "soldiers will endure almost any privation while they are winning... Lee's men
  fought hungry through much of the Civil War, cheerfully and without complaint; it was only when
  Grant and Sherman began to close in that they deserted."
* **dispersion raises the cohesion a formation needs, rather than lowering it.** du Picq: "since
  the invention of fire arms... the more men think themselves isolated, the more need they have of
  high morale. We are brought by dispersion to the need of a cohesion greater than ever before."
  So the `forming` rows read the formation table from part 2 and charge the loose ones for it.

Rules this table shares with every other table in this project:

* no source, no row. Every row names what it came from;
* a row is dated. `start` and `end` are years, negative for BCE, and a row with no end is not
  allowed -- a thing that stopped mattering has to say when it stopped;
* a row is placed. The box is where it held, not where the writer of it lived;
* `weight` is in points of morale on a 0..100 scale, and **every weight is this table's reading**.
  The factors are read; the number of points each one is worth is not something any source put a
  figure on, and it is marked `estimated` accordingly.

What is missing, and said out loud: there is no row here for Oceania, no row for the Americas
before 1491 outside the two that say so, and no row for sub-Saharan Africa. Not because those men
did not break -- they did, and are recorded doing it -- but because nothing was read for them, and
this project does not write a row it has not read.
"""

KINDS = ("sustaining", "combat", "forming", "condition", "breaking")

WHENS = ("always", "winning", "losing", "victory", "defeat", "home", "foreign",
         "paid", "unpaid", "plunder", "noplunder", "besieged", "dispersed", "close",
         "deep", "thin", "hungry", "sick", "long", "drafted", "hired", "raw", "blooded")

MARKS = ("recorded", "mixed", "estimated")

WORLD = (-90.0, 90.0, -180.0, 180.0)


def _box(x):
    lo_la, hi_la, lo_lo, hi_lo = x
    assert -90.0 <= lo_la <= hi_la <= 90.0, "bad latitude %s" % (x,)
    assert -180.0 <= lo_lo <= hi_lo <= 180.0, "bad longitude %s" % (x,)
    return x


class M:
    """One thing that bears on whether a body of troops will stand."""

    def __init__(self, id, name, kind, when, weight, start, end, box,
                 needs, doing, note, src, mark):
        assert kind in KINDS, "%s: unknown kind %s" % (id, kind)
        assert when in WHENS, "%s: unknown when %s" % (id, when)
        assert isinstance(weight, int) and -45 <= weight <= 45, "%s: bad weight %s" % (id, weight)
        assert -3000 <= start <= end <= 2026, "%s: bad years %s..%s" % (id, start, end)
        assert src, "%s: no source" % id
        assert mark in MARKS, "%s: unknown mark %s" % (id, mark)
        self.id, self.name, self.kind, self.when = id, name, kind, when
        self.weight, self.start, self.end = weight, start, end
        self.box = _box(box)
        self.needs, self.doing, self.note, self.src, self.mark = needs, doing, note, src, mark

    def covers(self, year):
        return self.start <= year <= self.end

    def here(self, lat, lon):
        lo_la, hi_la, lo_lo, hi_lo = self.box
        return lo_la <= lat <= hi_la and lo_lo <= lon <= hi_lo

    def as_dict(self):
        return {"id": self.id, "name": self.name, "kind": self.kind, "when": self.when,
                "weight": self.weight, "start": self.start, "end": self.end,
                "box": list(self.box), "needs": self.needs, "doing": self.doing,
                "note": self.note, "src": self.src, "mark": self.mark}


# --------------------------------------------------------------------------- sustaining.
# Why a man stays in the army at all. These are the slow ones: they do not decide a battle, they
# decide whether there is an army there to fight it.
SUSTAINING = [

    M("primary_group", "the men beside him", "sustaining", "always", 14, -3000, 2026, WORLD,
      "nothing at all -- this one is the floor under all the others",
      "keeps a man in his place because the four or five men he has eaten and marched with are "
      "still in theirs",
      "Shils and Janowitz, writing on the Wehrmacht in 1948: \"It appears that a soldier's "
      "ability to resist is a function of the capacity of his immediate primary group (his squad "
      "or section) to avoid social disintegration. When the individual's immediate group... met "
      "his basic organic needs, offered him affection and esteem from both officers and comrades, "
      "supplied him with a sense of power and adequately regulated his relations with authority, "
      "the element of self-concern in battle... was minimized.\" Stouffer's men named it "
      "themselves: \"you couldn't let the other men down.\"",
      "Cohesion and disintegration in the Wehrmacht; The American Soldier; Morale", "recorded"),

    M("pay_regular", "regular pay", "sustaining", "paid", 8, -3000, 2026, WORLD,
      "a treasury that is keeping up with its own promises",
      "holds an army together the way a wage holds any body of workers together",
      "Slantchev, on hired troops: they \"were also only as dependable as their pay was regular. "
      "When unpaid, hired troops could passively refuse to fight, mutiny, desert to a higher "
      "bidder, and even plunder their employer's territory.\" The Roman case is the same in "
      "reverse: by the late Republic troops \"increasingly dependent on their generals for pay, "
      "booty, and most importantly for the land grants promised upon discharge, troops began to "
      "attach themselves personally to their commanders.\"",
      "Warfare on Land (Slantchev); Mutiny and Rebellion Among the Legions (UNRV)", "recorded"),

    M("pay_arrears", "pay in arrears", "sustaining", "unpaid", -16, -3000, 2026, WORLD,
      "a treasury that has fallen behind, which is most treasuries most of the time",
      "the single most common cause of mutiny in the record",
      "Syler, on the American Civil War: \"the mutineers did not leave military service, they "
      "vowed instead to do less than their expected duties until their grievances were corrected... "
      "And the grievance was usually that of tardy pay.\" The mutineers of the Army of Flanders "
      "went further and elected their own representatives.",
      "Absent Without Leave (Syler); Army of Flanders; Mutiny", "recorded"),

    M("plunder_taken", "the promise of plunder", "sustaining", "plunder", 10, -3000, 1900, WORLD,
      "an army that has been fed on loot, or has been promised a town",
      "buys the campaign, sometimes literally",
      "Berkovich: \"men were motivated to stand their ground in combat by fear of punishment, "
      "greed for plunder and honour.\" On the Greek case, loot was \"simple distribution in early "
      "days, and by auctioning it in bulk for coin -- which was then distributed to the soldiers -- "
      "when coinage became universal.\" This row ends in 1900: the Hague convention and, more to "
      "the point, the invention of the military paymaster took it out of the ledger.",
      "Motivation in War (Berkovich); BMCR on Greek warfare; Looting", "recorded"),

    M("plunder_denied", "a town closed against them", "sustaining", "noplunder", -8,
      -3000, 1900, WORLD,
      "an army that has been promised a sack and then talked out of it",
      "turns a disciplined army into a mob in a day, and the record is full of it",
      "The mirror of the row above, and the reason commanders from Alexander to Wellington took "
      "a city by storm when they could have had it by treaty: an army denied its loot is an army "
      "that will take it out of you.",
      "Motivation in War (Berkovich); Sack (military)", "estimated"),

    M("land_grant", "land promised on discharge", "sustaining", "always", 10, -200, 476,
      (38.0, 45.0, 7.0, 19.0),
      "a state that still has public land to hand out",
      "binds the soldier to the general who promised it rather than to the state that sent him",
      "\"Both military levies and taxation fell on the peasant population and the absence of "
      "rewards for military service made the soldiers bitter... recruits sided with their "
      "commanders, rather than their government... their general could provide them with land, "
      "booty and other rewards at the end of a soldier's term of service.\" That is the late "
      "Roman Republic, and it is why its armies were loyal to Marius, Sulla, Pompey and Caesar "
      "in turn rather than to Rome.",
      "Mutiny and Rebellion Among the Legions (UNRV); Roman army", "recorded"),

    M("nationalism", "the nation", "sustaining", "always", 14, 1789, 1945,
      (35.0, 71.0, -12.0, 45.0),
      "a state that has taught its people that they are one people",
      "makes a citizen fight for an abstraction, and makes a conscript army hold",
      "Moskos's \"latent ideology\": primary groups hold a soldier in his combat role only when he "
      "has an underlying commitment to the worth of the larger social system he is fighting for. "
      "The date is 1789, and it is not an accident that it is the date of the levée en masse. "
      "Anthony King argues ethno-political motivation was central to the twentieth century and "
      "can be de-emphasised for the twenty-first, so this row ends in 1945 and is European: the "
      "box is where the nation-state was invented, not where it ended up.",
      "Morale; Combat motivation (Wikipedia); Latent ideology (Moskos)", "mixed"),

    M("religion", "religion", "sustaining", "always", 5, -3000, 2026, WORLD,
      "nothing but the men",
      "the oldest answer there is, and still the first-named one",
      "Stouffer's men, asked where they found their support, named **prayer** first, ahead of "
      "group solidarity. It is the one sustaining factor on this list that needs no state, no "
      "paymaster and no officer, which is why it carries from the Bronze Age to today.",
      "The American Soldier; Religion and war", "recorded"),

    M("cause", "the cause", "sustaining", "drafted", 6, 1775, 2026, WORLD,
      "a soldier who can say what he is fighting for",
      "sustains him through the months, and does very little for him in the minute",
      "Stouffer's finding is the important one and it is negative: **ideology, patriotism and the "
      "cause were not major factors** for Second World War soldiers, whose most common answer was "
      "simply ending the war. Leonard Wong found the opposite a generation later in Iraq, where "
      "soldiers did voice moral concepts like freedom and democracy. So the cause is real, and it "
      "is a sustaining motivation rather than a combat one: it is why a man stays, not what makes "
      "him stand.",
      "The American Soldier; Why They Fight (Wong); Combat motivation", "recorded"),

    M("end_of_war", "getting it over", "sustaining", "long", 8, -3000, 2026, WORLD,
      "a war long enough that men have begun to count",
      "makes an army hold through anything, provided it believes it is winning",
      "\"Asked what kept them going, the most common response was getting the war over so they "
      "could go home.\" That is Stouffer, and it is the plainest finding in the whole literature. "
      "It is also the reason the `winning` row below is as large as it is: the two only work "
      "together.",
      "The American Soldier; Morale", "recorded"),

    M("higher_bid", "the other side's bid", "sustaining", "hired", -8, 1200, 1800,
      (35.0, 60.0, -10.0, 40.0),
      "an army that is hired, and a war in which the other side is still solvent",
      "and the loyalty of a hired company ends exactly where its pay does",
      "Slantchev, on hired troops: they were 'only as dependable as their pay was regular. "
      "When unpaid, hired troops could passively refuse to fight, mutiny, desert to a higher "
      "bidder, and even plunder their employer's territory.' The desertion to a higher bidder "
      "is the specific failure this row names, and it is why the mercenary company in the "
      "sides table cannot be bound by a treaty its captain signs.",
      "Warfare on Land (Slantchev); Condottieri; Free company", "recorded"),

    M("conscription", "the draft", "sustaining", "drafted", -8, 1793, 2026, WORLD,
      "a state that has run out of volunteers",
      "gives you numbers, and takes away the reason to use them",
      "Slantchev: conscript troops are \"badly motivated, prone to desertion, and untrained... "
      "their military effectiveness was very low.\" The date is 1793, the levée en masse, and it "
      "is worth noting that the same measure that created the modern nation in arms created the "
      "modern problem of keeping it there.",
      "Warfare on Land (Slantchev); Conscription", "recorded"),
]

# --------------------------------------------------------------------------- combat.
# What makes a man stand in the minute. These are the fast ones, and they are the ones du Picq
# was writing about.
COMBAT = [

    M("officers_present", "an officer in front of him", "combat", "always", 6,
      -3000, 2026, WORLD,
      "officers who are alive, present, and visible",
      "the simplest answer to the panic, and the one every army has arrived at separately",
      "Shils and Janowitz: the primary group supplies \"affection and esteem from both officers "
      "and comrades\", and it is the officers' presence in the same danger that makes the "
      "regulation of authority work at all. du Picq's point was the same from the other side: "
      "once the officers are gone, \"once basically anyone starts fleeing, cohesion collapse is "
      "rapid\".",
      "Cohesion and disintegration in the Wehrmacht; Battle Studies (du Picq)", "recorded"),

    M("discipline_fear", "the fear of punishment", "combat", "always", 5, -3000, 2026, WORLD,
      "a discipline the men believe will actually be enforced on them",
      "the oldest combat motivation in the record, and the one that costs least to install",
      "du Picq on Rome: discipline was \"secured also by the fear of death. They put to death with "
      "the club; they decimated their cowardly or traitorous units.\" Berkovich puts it first in "
      "his list: \"fear of punishment, greed for plunder and honour.\" Lyall and Zhukov's work on "
      "fratricidal coercion -- violence used by an army against its own -- finds that it *can* "
      "reduce desertion, missing in action and premature surrender, against a literature that "
      "dismisses it as obsolete.",
      "Battle Studies (du Picq); Motivation in War (Berkovich); Fratricidal Coercion in Modern "
      "War (Lyall & Zhukov)", "recorded"),

    M("decimation", "decimation", "combat", "always", 6, -500, 300,
      (38.0, 45.0, 7.0, 19.0),
      "a Roman army, and a unit that has run",
      "kills one man in ten of the cowards, by the hands of the other nine",
      "\"They put to death with the club; they decimated their cowardly or traitorous units.\" "
      "The row is dated to the Republic and the Principate and boxed to Italy, because that is "
      "where it was a standing institution rather than a desperation. Italy in 1917 brought it "
      "back -- 128,000 desertion cases, roughly 750 executed, 391 of them shot -- and Cadorno is "
      "accused of it.",
      "Battle Studies (du Picq); Decimation (Roman army); Desertion", "recorded"),

    M("blocking_detachments", "troops behind their own line", "combat", "always", 8,
      1917, 1991, (40.0, 70.0, -10.0, 140.0),
      "a state willing to shoot its own men to keep them forward",
      "raises compliance and lowers desertion, at a cost no pre-modern state could pay",
      "Lyall and Zhukov, *Fratricidal Coercion in Modern War*: threatening or using violence "
      "against one's own soldiers can improve compliance, reducing desertion, missing in action "
      "and premature surrender. The date and the box are the Soviet case, because that is where "
      "the evidence is.",
      "Fratricidal Coercion in Modern War (Lyall & Zhukov); Barrier troops", "recorded"),

    M("blooded", "battle-hardened", "combat", "blooded", 8, -3000, 2026, WORLD,
      "an army that has already been in a battle and come out of it",
      "the men know what it sounds like now, and the noise no longer does the work",
      "du Picq's whole book is an argument that the terror of battle is the thing to be managed, "
      "and that familiarity with it is the cheapest management there is. Marked estimated: every "
      "army in the record says this and none of them put a number on it.",
      "Battle Studies (du Picq)", "estimated"),

    M("raw", "untried", "combat", "raw", -10, -3000, 2026, WORLD,
      "an army that has not yet been in a battle",
      "the noise does the work on its own",
      "The mirror of the row above, and the reason commanders from Philip of Macedon to the "
      "Prussians put new battalions behind old ones. Estimated, for the same reason.",
      "Battle Studies (du Picq)", "estimated"),
]

# --------------------------------------------------------------------------- forming.
# These four read the formation table from part 2. They are du Picq's own argument, and they are
# the only rows in this table that depend on another table in this step.
FORMING = [

    M("depth_holds", " depth behind the front rank", "forming", "deep", 10, -3000, 1900, WORLD,
      "a formation standing more than one rank deep",
      "keeps the rear from seeing the carnage, and gives the front somewhere to go",
      "du Picq, on why the Roman *triplex acies* beat the Greek phalanx: \"the Romans were able "
      "to keep soldiers in the rear removed from the fear and panic of the front line\", while "
      "\"the Greek phalanx was a single, deep mass which meant that everyone could see the "
      "carnage at the front and envision it happening to them next.\" Devereaux's summary of "
      "du Picq is the clearest statement of it: \"collapse comes not from the front, but from "
      "the back: the men in the back can see the carnage, they are stuck with the anxiety and "
      "fear of 'waiting their turn' but have none of the impetus to action of being in the "
      "fight.\"",
      "Battle Studies (du Picq); Collections: Military History and Strategy (acoup.blog)",
      "recorded"),

    M("thin_panics", "no depth at all", "forming", "thin", -10, -3000, 1900, WORLD,
      "a formation standing one or two ranks deep",
      "every man can see the whole field, and every man can see the whole field breaking",
      "The same passage read the other way. It is why the line infantry of the eighteenth century "
      "needed a drill so exact that a battalion could advance under fire without thinking: two "
      "ranks have no rear to hide in.",
      "Battle Studies (du Picq); Line infantry", "mixed"),

    M("dispersion_cost", "dispersion", "forming", "dispersed", -12, 1500, 2026, WORLD,
      "a formation in loose order",
      "costs more cohesion than close order does, not less -- the isolated man needs more, not "
      "less, to hold him",
      "This is the row most likely to be got backwards, so here is du Picq in full: \"The more "
      "men think themselves isolated, the more need they have of high morale. We are brought by "
      "dispersion to the need of a cohesion greater than ever before.\" And: \"Combat exacts a "
      "moral cohesion, a solidarity more compact than ever before.\" The skirmish line and the "
      "modern fireteam are *more* demanding of morale than the phalanx was, not less.",
      "Battle Studies (du Picq); Combat motivation", "recorded"),

    M("close_order_confidence", "the shoulder of the man next to him", "forming", "close", 5,
      -3000, 1900, WORLD,
      "a formation in close order",
      "the man cannot see the field, only his neighbours, and that is often enough",
      "The mirror of the row above. It ends in 1900 because after the Boer War nobody stood "
      "shoulder to shoulder any more, and the source of confidence had to move somewhere else.",
      "Battle Studies (du Picq); Line infantry", "mixed"),
]

# --------------------------------------------------------------------------- condition.
# What has been done to the army. These are the ones that move fastest, and the ones a commander
# has least control over.
CONDITION = [

    M("winning", "winning", "condition", "winning", 14, -3000, 2026, WORLD,
      "a campaign that is going their way",
      "the largest single factor in the table, and the one commanders forget to count",
      "From the Naval Institute's study of mutiny: \"soldiers will endure almost any privation "
      "while they are winning. Fundamentally, the feeling is that the victor will ultimately "
      "receive the spoils... There is none of this dreadful sense of impotence to provide for "
      "oneself that hunger in defeat engenders. Thus Lee's men fought hungry through much of the "
      "Civil War, cheerfully and without complaint; it was only when Grant and Sherman began to "
      "close in that they deserted.\"",
      "Mutiny -- A Study (US Naval Institute Proceedings, 1932); Morale in war", "recorded"),

    M("losing", "losing", "condition", "losing", -18, -3000, 2026, WORLD,
      "a campaign that is closing in on them",
      "and it is not the mirror of winning -- it is bigger",
      "The same passage: \"it was only when Grant and Sherman began to close in that they "
      "deserted.\" The asymmetry is deliberate. An army that is winning forgives hunger, arrears "
      "and defeat; an army that is losing forgives none of them. Lee's army did not desert "
      "because it was hungry, it deserted because it was hungry *and* beaten.",
      "Mutiny -- A Study (US Naval Institute Proceedings, 1932); Desertion", "recorded"),

    M("victory", "they won the last one", "condition", "victory", 8, -3000, 2026, WORLD,
      "a battle behind them that went their way",
      "buys the next battle, briefly",
      "Related to `winning` but not the same thing: a single victory does not make a campaign "
      "go well, and an army can win a battle on the retreat. Estimated.",
      "Morale; Morale in war", "estimated"),

    M("defeat", "they lost the last one", "condition", "defeat", -12, -3000, 2026, WORLD,
      "a battle behind them that went against them",
      "and the rout is where the dying happened, so the survivors remember it whole",
      "du Picq's Cannae is the type: \"Uneasiness, then terror, took hold of them... Demoralized "
      "and not feeling themselves supported, the ranks engaged followed them, and the routed "
      "mass let itself be slaughtered. The weapons fell from their hands, says Polybius.\" The "
      "physical loss at Cannae was one thing; the permanent loss was that the survivors remembered "
      "it. Estimated.",
      "Battle Studies (du Picq); Battle of Cannae", "estimated"),

    M("home_ground", "their own ground", "condition", "home", 8, -3000, 2026, WORLD,
      "an army standing on the fields it came from",
      "a man fights differently for his own house behind him",
      "The oldest claim in the literature and one of the hardest to measure, which is why it "
      "carries less weight here than a commander on the spot would have given it. Estimated.",
      "Morale in war; Defence in depth", "estimated"),

    M("foreign_service", "service abroad", "condition", "foreign", -6, -3000, 2026, WORLD,
      "an army a long way from anything it recognises",
      "and every mile is a mile of road home",
      "The mirror of the row above, and the reason the desertion rates below are so much worse "
      "for armies serving abroad. Estimated.",
      "Desertion; Morale in war", "estimated"),

    M("hunger", "hunger", "condition", "hungry", -14, -3000, 2026, WORLD,
      "an army that has run short",
      "and it is only partly about the food",
      "\"There is none of this dreadful sense of impotence to provide for oneself that hunger in "
      "defeat engenders\" -- the same Naval Institute passage, read for what it says about hunger "
      "itself. A hungry army that is winning is a different animal from a hungry army that is "
      "losing, which is why this row is smaller than the one above it.",
      "Mutiny -- A Study (US Naval Institute Proceedings, 1932)", "mixed"),

    M("sickness", "sickness in the camp", "condition", "sick", -8, -3000, 2026, WORLD,
      "an army that has been lying in its own filth long enough",
      "kills the body and the morale at the same time, and mostly the morale",
      "Before the twentieth century disease killed more soldiers than battle did in almost every "
      "war there is a record for. Estimated, and probably understated: the register has no way to "
      "express that a third of the men are on the sick list.",
      "Military history; Disease in war", "estimated"),

    M("shut_up", "shut up in a siege", "condition", "besieged", -8, -3000, 2026, WORLD,
      "an army inside a place that has been surrounded",
      "the men can count the days and cannot change them, which is the worst combination",
      "The besieged soldier is the one case in which the rear rank cannot avoid the carnage and "
      "the front rank cannot avoid the waiting, because there is no front and no rear any more. "
      "du Picq's argument about the back of the formation presupposes a formation; a garrison on "
      "a wall for a hundred days does not have one, which is why part 4's siege register drives "
      "the garrison's morale down day by day rather than by battle. Estimated.",
      "Battle Studies (du Picq); Siege", "estimated"),

    M("exhaustion", "exhaustion", "condition", "long", -10, -3000, 2026, WORLD,
      "an army that has been at it a long time",
      "a man is capable of a given quantity of fear and then not much more",
      "\"Man is capable of but a given quantity of fear, and just in proportion as this quantity "
      "is expended, in the same proportion does he become insensible to the causes of fear.\" "
      "That is du Picq, and it is the reason this row and the `long` condition are the same: an "
      "army that has spent its fear has nothing left to spend on the next battle.",
      "Battle Studies (du Picq); Combat stress reaction", "recorded"),
]

FACTORS = SUSTAINING + COMBAT + FORMING + CONDITION


# --------------------------------------------------------------------------- how armies were raised
# This is the second half of part 5, and it is the one that decides what an army will put up with.
class R:
    """One way of raising an army, in one place, for a stretch of years."""

    def __init__(self, id, name, start, end, box, paid_in, cohesion, desertion, will_treat,
                 needs, doing, note, src, mark):
        assert -3000 <= start <= end <= 2026, "%s: bad years %s..%s" % (id, start, end)
        assert paid_in in ("pay", "loot", "land", "obligation", "faith", "wage"), "%s: %s" % (
            id, paid_in)
        assert isinstance(cohesion, int) and 0 <= cohesion <= 100, "%s: bad cohesion" % id
        assert isinstance(desertion, (int, float)) and 0.0 <= desertion <= 40.0, "%s: bad %s" % (
            id, desertion)
        assert src, "%s: no source" % id
        assert mark in MARKS, "%s: unknown mark %s" % (id, mark)
        self.id, self.name, self.start, self.end = id, name, start, end
        self.box = _box(box)
        self.paid_in, self.cohesion = paid_in, cohesion
        self.desertion, self.will_treat = desertion, will_treat
        self.needs, self.doing, self.note, self.src, self.mark = needs, doing, note, src, mark

    def covers(self, year):
        return self.start <= year <= self.end

    def here(self, lat, lon):
        lo_la, hi_la, lo_lo, hi_lo = self.box
        return lo_la <= lat <= hi_la and lo_lo <= lon <= hi_lo

    def as_dict(self):
        return {"id": self.id, "name": self.name, "start": self.start, "end": self.end,
                "box": list(self.box), "paidIn": self.paid_in, "cohesion": self.cohesion,
                "desertion": self.desertion, "willTreat": self.will_treat,
                "needs": self.needs, "doing": self.doing, "note": self.note,
                "src": self.src, "mark": self.mark}


RAISED = [

    R("levy", "the shire levy", -1000, 1500, (40.0, 60.0, -10.0, 30.0), "obligation", 19, 9.0,
      True,
      "a lord with the right to call out his people, and a season to do it in",
      "free men called out for a campaign, bound to serve, bound to go home for the harvest",
      "The oldest way there is of raising an army and the one that decides most of the medieval "
      "west. Its cohesion is middling and its desertion is high, and both come from the same "
      "thing: the men are not soldiers, they are farmers with a legal duty and a harvest to get "
      "back to. Cohesion and desertion are this table's reading -- no source put a percentage on "
      "the Anglo-Saxon fyrd.",
      "Fyrd; Anglo-Saxon warfare; Levy en masse", "estimated"),

    R("citizen_militia", "the citizen militia", -700, 1798, (35.0, 47.0, 6.0, 30.0),
      "obligation", 36, 3.0, True,
      "a city whose men owe it service and can be shamed into giving it",
      "men who know each other, fight beside each other, and answer to each other afterwards",
      "The Greek polis and the Swiss canton. Its cohesion is the highest in this table and it is "
      "not mysterious: Shils and Janowitz's primary group, except the primary group is the whole "
      "neighbourhood and it existed before the war did. The Swiss were the most sought-after "
      "soldiers in Europe for two centuries on the strength of it. Cohesion and desertion "
      "estimated.",
      "Hoplite; Ancient Greek warfare; Swiss mercenaries; Militia", "estimated"),

    R("retinue", "the lord's household", 400, 1550, (35.0, 60.0, -10.0, 30.0), "land", 39, 2.0,
      True,
      "a lord with land to grant and men willing to take it",
      "a sworn following, fed at the lord's table, armed at the lord's cost",
      "The best cohesion in the medieval column and the smallest numbers, which is the trade. "
      "Land buys a fidelity that pay does not, because it cannot be withheld for a month the way "
      "coin can. Cohesion and desertion estimated.",
      "Retinue; Feudal land tenure; Household (military)", "estimated"),

    R("mercenary_company", "the hired company", 1200, 1650, (35.0, 60.0, -10.0, 40.0), "pay", 17,
      14.0, False,
      "a treasury, and a captain who can deliver what he promises",
      "a company contracted for a season, for a price, and renewable at the other side's offer",
      "Slantchev's sentence is the whole row: mercenaries \"were also only as dependable as their "
      "pay was regular. When unpaid, hired troops could passively refuse to fight, mutiny, desert "
      "to a higher bidder, and even plunder their employer's territory.\" **willTreat is false**, "
      "and that is the point of it: a company fighting for its arrears cannot be bound by a "
      "treaty its captain signs, and half the sackings in the Italian wars begin there. "
      "Cohesion and desertion estimated from the sentence above. The date ends in 1650: "
      "after the Thirty Years' War hired men served inside the standing regiments of a "
      "state -- the Hessians George III hired were somebody else's army, not a company "
      "of their own -- and the company as a party goes with that.",
      "Warfare on Land (Slantchev); Condottieri; Free company", "mixed"),

    R("conscript_national", "the conscript army", 1793, 2026, WORLD, "obligation", 26, 5.0, True,
      "a state with a register of its own population and the will to use it",
      "men taken by law, in numbers no volunteer system has ever matched",
      "Slantchev: \"conscript troops are badly motivated, prone to desertion, and untrained... "
      "their military effectiveness was very low.\" And yet the conscript armies of the "
      "Revolutionary and Napoleonic wars beat every professional army in Europe, which is the "
      "reason this row's cohesion is not lower than it is: what the draft costs in motivation it "
      "buys back in numbers and in the `nationalism` row above.",
      "Warfare on Land (Slantchev); Levée en masse; Conscription", "mixed"),

    R("professional_standing", "the standing army", -100, 2026, (-35.0, 60.0, -15.0, 145.0), "wage", 33, 3.2, True,
      "a state with a treasury that can pay every year, which is a rare thing",
      "men who are soldiers for a living, drilled in peace, paid in war and in peace alike",
      "The Roman legion of the Principate, the New Model Army, the Prussian line. This is the "
      "only row in the table with a measured desertion rate attached: **3.2 per cent a year**, "
      "which is the Prussian figure for 1713-1740, the lowest of the three long-service armies "
      "Duffy tabulated. The others were 4.4 (French, 1716-1749) and 7.0 (Saxon, 1717-1727), for "
      "an average of 4.9.",
      "Desertion (Wikipedia); The Military Experience in the Age of Reason (Duffy); Kabinettskriege",
      "recorded"),

    R("slave_soldier", "the slave soldier", 800, 1900, (10.0, 45.0, 5.0, 60.0), "faith", 37, 1.5,
      True,
      "a ruler who would rather own his soldiers than hire them",
      "boys taken young, converted, trained, and bound to the person of the ruler",
      "The Mamluk, the Janissary, the ghulam. The lowest desertion in this table and one of the "
      "highest cohesions, for a reason that sounds like a paradox: the men have nowhere to desert "
      "*to*. They are strangers in the country they garrison, which removes the third of the "
      "three wellsprings of desertion -- opportunities beyond the service -- entirely. Both "
      "figures estimated.",
      "Mamluk; Janissary; Ghulam; Slave soldier", "estimated"),

    R("steppe_following", "the khan's following", -300, 1800, (44.0, 55.0, 30.0, 120.0),
      "loot", 29, 4.0, False,
      "a khan who keeps winning, because the following is what winning buys",
      "a household of sworn companions around a ruler, and a people who ride with them",
      "Taylor on what happened after Alexander: \"an implosion of political legitimacy... "
      "effectively transformed all soldiers into de facto volunteers, who swapped their support "
      "between successors.\" That is even truer of the steppe, where a following is not an "
      "institution but a personal fact about one man. **willTreat is false**: a following that "
      "exists for plunder can be bought off but not bound, and it dissolves when the khan does. "
      "Both figures estimated. The box is the steppe belt and nothing else: 44 to 55 north, "
      "from the Ponto-Caspian to Manchuria. A wider box swallows northern China, and the sown "
      "and the steppe are interleaved along that frontier.",
      "Mongol military tactics and strategy; Nöker; Motivation in War (Berkovich)", "estimated"),

    R("warlord_band", "the warlord band", -3000, 2026, WORLD, "loot", 14, 12.0, False,
      "nothing but a man who can feed and arm the men who follow him",
      "a band held together by the person of its chief and the prospect of the next town",
      "This row exists because Brecke's catalog insists on it: \"conflicts between warlords when "
      "there is no state involvement qualify as violent conflicts.\" It is the default row, and "
      "it is deliberately the worst-behaved one in the table. **willTreat is false**, and that "
      "matters most inside a siege: a conditional surrender is a bargain between two parties who "
      "can each be held to it, and a band has nothing to hold.",
      "Conflict Catalog (Brecke); Notes regarding the Conflict Catalog; Warlord", "estimated"),
]


# --------------------------------------------------------------------------- desertion, measured
class D:
    """One measured desertion rate. These are recorded, not read off; where a figure is this
    table's arithmetic on a recorded count it says so."""

    def __init__(self, id, army, start, end, per_year, total_pct, count, raised,
                 note, src, mark):
        assert -3000 <= start <= end <= 2026, "%s: bad years %s..%s" % (id, start, end)
        assert per_year is None or 0.0 <= per_year <= 60.0, "%s: bad per_year" % id
        assert total_pct is None or 0.0 <= total_pct <= 100.0, "%s: bad total_pct" % id
        assert per_year is not None or total_pct is not None or count is not None, \
            "%s: no figure at all" % id
        assert src, "%s: no source" % id
        assert mark in MARKS, "%s: unknown mark %s" % (id, mark)
        self.id, self.army, self.start, self.end = id, army, start, end
        self.per_year, self.total_pct, self.count = per_year, total_pct, count
        self.raised, self.note, self.src, self.mark = raised, note, src, mark

    def as_dict(self):
        return {"id": self.id, "army": self.army, "start": self.start, "end": self.end,
                "perYear": self.per_year, "totalPct": self.total_pct, "count": self.count,
                "raised": self.raised, "note": self.note, "src": self.src, "mark": self.mark}


DESERTION = [

    D("prussia_1713", "Prussian army, long service", 1713, 1740, 3.2, None, None,
      "professional_standing",
      "The lowest of the three long-service rates Duffy tabulated, from a state that made a "
      "religion of the drill square.",
      "The Military Experience in the Age of Reason (Duffy), via Kabinettskriege; Desertion",
      "recorded"),

    D("france_1716", "French army, long service", 1716, 1749, 4.4, None, None,
      "professional_standing",
      "Forty years and two states apart from the Prussian figure, and not the same population.",
      "The Military Experience in the Age of Reason (Duffy), via Kabinettskriege; Desertion",
      "recorded"),

    D("saxony_1717", "Saxon army", 1717, 1727, 7.0, None, None, "professional_standing",
      "The worst of the three, and a warning against taking any single one of them as the rate "
      "for the century.",
      "The Military Experience in the Age of Reason (Duffy), via Kabinettskriege; Desertion",
      "recorded"),

    D("ancien_regime_1700", "French army, whole period", 1700, 1763, None, 20.0, None,
      "professional_standing",
      "Corvisier's estimate: **about a fifth of all French troops** deserted across 1700-1763. "
      "Note that this is a share of everyone who ever served, not an annual rate, so it is not "
      "directly comparable with the three rows above.",
      "L'Armée française de la fin du XVIIe siècle au ministère de Choiseul (Corvisier), via "
      "Kabinettskriege; Desertion", "recorded"),

    D("continental_1775", "Continental Army", 1775, 1783, None, 22.5, None, "conscript_national",
      "20 to 25 per cent, which is the highest total figure in this table apart from the "
      "Confederate one, from an army that was short of everything at once.",
      "Desertion (Wikipedia); Continental Army", "recorded"),

    D("us_regulars_1820", "United States regulars", 1820, 1860, 14.8, None, None,
      "professional_standing",
      "The worst annual rate in this table, from a peacetime army: in 1830 alone 1,251 of 5,231 "
      "enlisted men deserted, which is 21 per cent in a single year.",
      "Desertion (Wikipedia), citing the National Park Service at Fort Scott", "recorded"),

    D("union_1861", "Union Army", 1861, 1865, None, 10.5, 200000, "conscript_national",
      "About 200,000 desertions from roughly 2.1 million mustered, which is 9 to 12 per cent.",
      "Desertion (Wikipedia); Union Army", "recorded"),

    D("confederate_1861", "Confederate Army", 1861, 1865, None, 12.5, 104000,
      "conscript_national",
      "About 104,000 desertions from 800,000 to 1,000,000 enlistments, 10 to 15 per cent -- and "
      "the rate in the last year of the war was **as high as one in three**. Virginia's own "
      "troops deserted at 10 to 15 per cent. This is the clearest measured case in the whole "
      "table of the `losing` row above: the same men held for three years and went home in the "
      "fourth.",
      "Desertion (Wikipedia); Encyclopedia Virginia; Confederate States Army", "recorded"),

    D("britain_1803", "British Army", 1803, 1815, None, None, 77696, "professional_standing",
      "77,696 cases across the Napoleonic wars, against a punishment that was, on paper, death. "
      "**Between a third and a half of all British deserters went back to their units** -- which "
      "is the finding that matters here, because it means desertion in this period was often a "
      "temporary withdrawal of labour rather than a departure from the army. The count is "
      "recorded; this table has not converted it into a rate, because the denominator is not "
      "settled.",
      "Desertion (Wikipedia), citing White Rose Research Online; British Army", "recorded"),

    D("italy_1914", "Italian Army", 1914, 1918, None, None, 128000, "conscript_national",
      "128,000 desertion cases; 15,096 life sentences; roughly 750 executed, 391 of them by "
      "firing squad. Cadorno is accused of reviving decimation. The count is recorded and the "
      "register has not turned it into a rate.",
      "Desertion (Wikipedia); Decimation (punishment); Italian Army", "recorded"),

    D("us_vietnam", "United States Army, draft era", 1965, 1973, None, 6.0, None,
      "conscript_national",
      "5 to 7 per cent, against **under 1 per cent** for the all-volunteer force that replaced "
      "it. The literature explains the difference the same way it explains the Confederate "
      "figure: rates rise where civilian wages exceed military pay by 20 to 30 per cent, and "
      "improved compensation and unit cohesion outperform punishment administered afterwards.",
      "Desertion (Wikipedia); United States Army", "recorded"),
]


# --------------------------------------------------------------------------- how an army breaks
class B:
    """One way of stopping. `lossPct` is the share of the army that has gone before it happens."""

    def __init__(self, id, name, loss_pct, start, end, needs, doing, note, src, mark):
        assert isinstance(loss_pct, (int, float)) and 0.0 <= loss_pct <= 100.0, "%s: %s" % (
            id, loss_pct)
        assert -3000 <= start <= end <= 2026, "%s: bad years %s..%s" % (id, start, end)
        assert src, "%s: no source" % id
        assert mark in MARKS, "%s: unknown mark %s" % (id, mark)
        self.id, self.name, self.loss_pct = id, name, loss_pct
        self.start, self.end = start, end
        self.needs, self.doing, self.note, self.src, self.mark = needs, doing, note, src, mark

    def as_dict(self):
        return {"id": self.id, "name": self.name, "lossPct": self.loss_pct,
                "start": self.start, "end": self.end, "needs": self.needs,
                "doing": self.doing, "note": self.note, "src": self.src, "mark": self.mark}


BREAKING = [

    B("rout", "the rout", 12.0, -3000, 2026,
      "an army that has lost its formation",
      "the formation comes apart and the killing starts",
      "The single most important fact about battle casualties, and the one the mod does not have "
      "at all: **the rout is where the dying happens.** du Picq, on Cannae: \"The physical "
      "pressure was unimportant... Demoralized and not feeling themselves supported, the ranks "
      "engaged followed them, and the routed mass let itself be slaughtered. The weapons fell "
      "from their hands, says Polybius.\" The 12 per cent is Peter Krentz's measured breaking "
      "point for hoplite battles, and this table uses it as the threshold at which formation "
      "gives way -- at which point the losing side stops losing men at the fighting rate and "
      "starts losing them at the pursuit rate.",
      "Battle Studies (du Picq); Casualties in Hoplite Battles (Krentz); Rout (military)",
      "recorded"),

    B("pursuit", "the pursuit", 15.0, -3000, 2026,
      "an army that has turned and run",
      "the winners kill the losers, and there is nothing the losers can do about it",
      "The rout is the decision; the pursuit is the bill. This figure is **the losers' whole "
      "share, not the extra**: Krentz's measured figures for hoplite battles give 3 to 10 per "
      "cent for the winners and 10 to 20 per cent for the losers, and the whole gap between the "
      "two is the pursuit -- men killed from behind, with their shields on their backs. The "
      "register therefore takes the losers at 15 and the winners at 6.5, and the 8.5 points "
      "between them are pursuit and nothing else. Any battle model that charges both sides the "
      "same percentage is modelling the fighting and not the battle.",
      "Casualties in Hoplite Battles (Krentz); Battle Studies (du Picq); Rout (military)",
      "recorded"),

    B("mutiny", "mutiny", 0.0, -3000, 2026,
      "an army with a grievance, and usually an unpaid one",
      "the men do not go; they stop doing what is asked of them until it is answered",
      "Syler's distinction is the one worth keeping: \"Desertion is the act of one or two or "
      "three; mutiny can involve an entire army.\" And: \"the mutineers did not leave military "
      "service, they vowed instead to do less than their expected duties until their grievances "
      "were corrected... And the grievance was usually that of tardy pay.\" The mutineers of the "
      "Army of Flanders elected their own representatives. Note the loss percentage is zero: a "
      "mutiny is not caused by casualties at all, which is why it needs its own row.",
      "Absent Without Leave (Syler); Army of Flanders; Mutiny", "recorded"),

    B("mass_desertion", "mass desertion", 0.0, 1789, 2026,
      "an army whose reason for fighting has been pulled out from under it",
      "the army dissolves, and the men go home in units rather than one at a time",
      "*Why Armies Break* ties mass desertion to \"the prewar nature of the collective identity a "
      "regime uses to legitimate its rule\": the more exclusionary that identity is toward "
      "internal populations, the greater the odds a military will break on the battlefield. It is "
      "a different thing from ordinary desertion and it happens for a different reason, which is "
      "why the loss percentage is zero here too.",
      "Why Armies Break: Explaining Mass Desertion in Conventional War; Desertion", "recorded"),
]


CASUALTIES = {
    # Peter Krentz, 'Casualties in Hoplite Battles' (Greek, Roman and Byzantine Studies): 3 to 10
    # per cent for the winners of a hoplite battle and 10 to 20 per cent for the losers. The
    # register takes the midpoints. **The gap between the two is not the fighting -- it is the
    # pursuit**, and that is the single most important number in this part.
    "winnerPct": 6.5,
    "loserPct": 15.0,
    "routAt": 12.0,
    "note": "Krentz's measured bands, at their midpoints. A battle model that charges both sides "
            "the same percentage is modelling the fighting and not the battle: the winners lose "
            "their share in the fight, and the losers lose theirs in the fight and then again in "
            "the rout that follows it.",
    "src": "Casualties in Hoplite Battles (Krentz, GRBS); Battle Studies (du Picq)",
    "mark": "recorded",
}


GAPS = [
    "No row for Oceania, and none for the Americas before 1491 outside the two that say so. "
    "Peoples there fought and broke like everyone else; nothing was read for them, and this "
    "project does not write a row it has not read.",

    "No row for sub-Saharan Africa. The same reason, and it is a worse gap here than in the "
    "formation table, because the desertion figures below are European and North American to a "
    "man.",

    "The desertion rates are point estimates from particular armies in particular decades, and "
    "they are spread across a band. The Prussian 3.2 per cent and the Saxon 7.0 per cent are "
    "forty years apart and are not the same population.",

    "Every `weight` in this table is this table's reading. The factors are read; the number of "
    "points each one is worth is not something any source put a figure on, and every weight is "
    "marked estimated or mixed accordingly.",

    "The register does not model individual commanders. du Picq, and everyone who has written "
    "since, would say that is where most of it lives.",

    "Brecke's Conflict Catalog was not loaded -- it is a binary file, and no row of it was read. "
    "The kinds of party in the sides table are read from the catalog's own description; the "
    "conflicts in it are not.",
]
