#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 39 (D9 event scenes): the twenty scenes, hand-written.

D9 asks for twenty: *battle, siege, crowning, court day, procession, festival, prayer, market day,
plague, famine, flight from flood or earthquake, fire, building works, refugees, election, protest,
trial, wedding, funeral, a caravan or ship arriving*. This is that list, one row each.

**What a scene is not.** It is not a list of NPCs. `PresenceLocalSpawner.sceneRoles(effect)` looks at
the event's effect string for the words "military", "lockdown", "memorial" and hands back two or
three copies of `guard`, `citizen` or `merchant`. That is the whole of the mod's scene-making today,
and it cannot tell a coronation from a cattle market. A scene here is five things:

* **what** it is — one of the twenty;
* **when** it is on — the trigger that puts it in the world: a dated event from step 28's
  gazetteer, a hazard in force from step 36, a market or prayer day from step 38's `DayRound`, a
  festival from step 30b's `CultureAtlas`, a migration from step 38, or a generated incident;
* **where** it stands — the kind of ground it needs, which is not the same ground for all of them;
* **who** is in it — a cast given as **sectors** (`farming`, `trade`, `clergy`, `soldier`,
  `craft`, `official`, `scholar`, `service`, `transport`, `miner`, `herding`, `foraging`), because
  that is what step 38's `Jobs` draws from. The register casts the parts from the jobs that
  actually exist in that place and year, so a coronation in a village has a priest and a headman
  rather than a bishop and a chancellor;
* **what they are doing** — the business of the scene, which is what the player walks into.

**Sources.** Every row names one. Where the composition is this table's own reading — how many
people of what sort are in it — the row is marked `estimated`, and the register repeats that word,
the same discipline as step 38. The customs are the parts that had to be right and are sourced: the
route of a Roman triumph, the assize courts and the end of the ordeals in 1215, the royal entry and
its guilds in their colours, the weekly market and the annual fair on its saint's day, the banns
read on three Sundays, and the wake the night before a funeral.
"""


class S:
    """One scene: what it is, when it happens, where it stands, who is in it, what they are doing."""

    __slots__ = ("id", "name", "group", "where", "trigger", "cast", "doing",
                 "note", "src", "mark")

    #: the grounds a scene can stand on
    GROUNDS = ("square", "gate", "temple", "hall", "field", "river", "street",
               "cemetery", "quay", "works")

    #: what puts a scene in the world
    TRIGGERS = ("event", "disaster", "market", "calendar", "migration", "incident", "life")

    #: the twelve work sectors step 38's Jobs draws from
    SECTORS = ("farming", "herding", "foraging", "craft", "miner", "trade", "service",
               "transport", "soldier", "clergy", "official", "scholar")

    def __init__(self, sid, name, group, where, trigger, cast, doing, note, src,
                 mark="recorded"):
        assert isinstance(sid, str) and sid, "scene needs an id"
        assert where in S.GROUNDS, "scene %s stands on an unknown ground: %r" % (sid, where)
        assert trigger in S.TRIGGERS, "scene %s has an unknown trigger: %r" % (sid, trigger)
        assert src and isinstance(src, str), "no source, no row: scene %s" % sid
        assert mark in ("recorded", "mixed", "estimated"), "scene %s: bad mark %r" % (sid, mark)
        bad = [k for k in cast if k not in S.SECTORS]
        assert not bad, "scene %s casts from unknown sectors: %r" % (sid, bad)
        assert sum(cast.values()) > 0, "scene %s has nobody in it" % sid
        self.id = sid
        self.name = name
        self.group = group
        self.where = where
        self.trigger = trigger
        self.cast = cast
        self.doing = doing
        self.note = note
        self.src = src
        self.mark = mark


SCENES = [
    # ------------------------------------------------------------------ power
    S("crowning", "a crowning", "power", "temple", "event",
      {"clergy": 3, "official": 3, "soldier": 2, "craft": 1, "service": 2},
      "one person is being given the crown, everyone else is watching the moment it lands",
      "The Christian *ordo* of crowning — prayers said over the crown by the prelate and only "
      "then the crown set on — goes back to Leo I, crowned by Patriarch Anatolius of "
      "Constantinople in **AD 457**, and every court in Europe imitated it. The scene is the "
      "liturgy, not the party: the feast comes after.",
      "English Wikipedia, 'Coronation'", mark="mixed"),

    S("court_day", "a court day", "power", "hall", "event",
      {"official": 4, "clergy": 1, "craft": 1, "service": 2, "farming": 2},
      "petitions being heard, a lord or his justices sitting, everybody waiting their turn",
      "The assize courts: Henry II's **Assize of Clarendon of 1166** set up itinerant justices "
      "holding county courts, and Magna Carta made them annual and local rather than at "
      "Westminster. They ran in England until **1972**, when the Courts Act 1971 replaced them "
      "with the Crown Court. Before 1215 a man was tried by ordeal, by battle or by compurgation.",
      "English Wikipedia, 'Assizes' and 'Trial by ordeal'; Britannica, 'assize'"),

    S("procession", "a procession", "power", "street", "event",
      {"soldier": 3, "clergy": 2, "craft": 4, "official": 2, "service": 3},
      "a formal line of people walking a set route, in order, to a fixed end",
      "The Roman triumph is the model everybody copied: from the Campus Martius through the "
      "**Porta Triumphalis**, along the **Via Sacra** to the Temple of Jupiter on the Capitoline, "
      "the general in a four-horse chariot in a laurel crown and the *toga picta*, his captives "
      "and spoils behind him, the crowd shouting *Io triumphe*, and his command surrendered at "
      "the *pomerium* on the way. Republic rules: a magistrate with independent command, a major "
      "battle won, **5,000** of the enemy dead, and the war ended.",
      "English Wikipedia, 'Roman triumph'; Britannica, 'triumph'", mark="mixed"),

    S("election", "an election", "power", "square", "incident",
      {"official": 3, "craft": 3, "trade": 2, "farming": 3, "service": 2},
      "people being counted, and a crowd that already knows who it wants",
      "The composition is this table's own. What is sourced is the shape: a public counting in an "
      "open place, in front of witnesses, which is what choosing someone has meant in almost "
      "every polity that has done it.",
      "English Wikipedia, 'Election'; the cast is this table's reading, mark estimated",
      mark="estimated"),

    S("protest", "a protest", "power", "square", "incident",
      {"craft": 4, "trade": 2, "farming": 3, "service": 2, "scholar": 1},
      "a crowd in one place, saying one thing, that did not come to listen",
      "The composition is this table's own. A protest is the one scene here whose whole business "
      "is that the people in it are not where they are supposed to be.",
      "English Wikipedia, 'Protest'; the cast is this table's reading, mark estimated",
      mark="estimated"),

    # ------------------------------------------------------------------ justice and worship
    S("trial", "a trial", "justice", "hall", "incident",
      {"official": 3, "clergy": 1, "craft": 2, "service": 2, "farming": 1},
      "one person's fate being decided in front of witnesses",
      "What is being done has changed three times in the record: **ordeal, battle or "
      "compurgation** before 1215; then the jury, which the Assize of Clarendon set up for land "
      "disputes with a grand assize of **twelve knights** and which spread to crime after the "
      "ordeals were abolished in **1215**; and, in England, the assize courts until 1972. The "
      "register picks the one that belongs to the year.",
      "English Wikipedia, 'Trial by ordeal', 'Assize of Clarendon' and 'Assizes'"),

    S("prayer", "an hour of prayer", "worship", "temple", "calendar",
      {"clergy": 3, "service": 2, "farming": 2, "craft": 1},
      "the day stopping, and everybody stopping with it",
      "How often the day stops and what the hours are called is step 38's `DayRound`, read from "
      "the place and the faith — five for Islam, the eight canonical hours for medieval "
      "Christianity, three for Judaism, Hinduism and Sikhism. This scene is on when the hour "
      "comes round.",
      "Step 38 `DayRound`, sourced there; English Wikipedia, 'Canonical hours', 'Salah', "
      "'Siddur'"),

    S("festival", "a festival", "worship", "street", "calendar",
      {"clergy": 2, "craft": 3, "trade": 3, "service": 3, "farming": 2},
      "the year turning, and a whole place out in the street for it",
      "Which festival and on what day comes from step 30b's `CultureAtlas`, which knows the great "
      "festivals of each faith by date. In medieval England the parish feast was the **wake** or "
      "*vigilia*, held on the anniversary of the church's dedication or its saint's day, and "
      "tradesmen displayed their wares in the churchyard.",
      "Step 30b `CultureAtlas`; English Wikipedia, 'Charter fair' and 'Wake (ceremony)'"),

    # ------------------------------------------------------------------ trade and work
    S("market_day", "a market day", "trade", "square", "market",
      {"trade": 4, "craft": 2, "farming": 3, "service": 1, "herding": 1},
      "stalls, weighing, arguing about price, and everybody from the surrounding country",
      "In medieval England and Wales a **market was held once a week, on a set day and in a set "
      "place**, for which the town paid the Crown a yearly fee for a charter. A **fair** was "
      "different: annual, on a set date, normally the feast of a particular saint, lasting two or "
      "three days to a week or more, trading in the things a weekly market does not carry — "
      "cattle, spices, furs, furniture — with entertainment to bring the crowds. How often the "
      "market comes round *here* is step 38's `DayRound`: every eighth day for the Roman "
      "**nundinae**, every fifth for the Javanese **pasaran**.",
      "Institute of Historical Research, 'Gazetteer of Markets and Fairs to 1516'; English "
      "Wikipedia, 'Charter fair'; step 38 `DayRound`, sourced there"),

    S("caravan_arrival", "a caravan or a ship coming in", "trade", "quay", "event",
      {"transport": 3, "trade": 3, "service": 2, "craft": 1, "official": 1},
      "unloading, counting, and the news from wherever it has been",
      "The arrival of goods is also the arrival of news, and step 37's `NewsTravel` already knows "
      "how long that took. The composition is this table's own.",
      "Step 37 `NewsTravel`; the cast is this table's reading, mark estimated",
      mark="estimated"),

    S("building_works", "building works", "work", "works", "event",
      {"craft": 4, "miner": 1, "service": 2, "farming": 1, "official": 1},
      "something going up, and a great many people carrying things",
      "What is being built and when is step 32's famous buildings and step 34's works. A building "
      "site is the most common large gathering of people in the whole of history and the least "
      "often written about.",
      "Step 32 `FamousBuildings`, step 34 `WaysWorks`; the cast is this table's reading, mark "
      "estimated", mark="estimated"),

    # ------------------------------------------------------------------ suffering
    S("plague", "a plague", "suffering", "street", "disaster",
      {"clergy": 2, "service": 3, "trade": 1, "craft": 1},
      "houses shut, the carts going round, and far fewer people about than there should be",
      "Which sickness, how far along it is and how many it has killed is step 36's hazard pack, "
      "read through step 38's `Health`. The plague scene is the one where **the absence is the "
      "event**: the register says how much quieter the street is, not how many corpses there are.",
      "Step 36 `Disasters`, step 38 `Health`, both sourced there; the cast is this table's "
      "reading, mark estimated", mark="estimated"),

    S("famine", "a famine", "suffering", "field", "disaster",
      {"farming": 4, "official": 1, "clergy": 1, "trade": 1, "service": 1},
      "fields that gave nothing, and people walking out to find somewhere that did",
      "Which famine, in what years, over what radius, is step 36's hazard pack. Step 38's `Needs` "
      "already knows that a famine does not hit everybody the same way: on the Kanki famine of "
      "AD 1229 the grower's food reads 0.00 and the buyer's 0.50.",
      "Step 36 `Disasters`, step 38 `Needs`, both sourced there; the cast is this table's "
      "reading, mark estimated", mark="estimated"),

    S("flight", "a flight from flood, fire or earthquake", "suffering", "street", "disaster",
      {"service": 2, "craft": 2, "farming": 2, "trade": 1, "official": 1},
      "people leaving, on foot, with what they could carry, in the direction away",
      "Which catastrophe and how wide its reach is step 36's hazard pack. What it did to the "
      "buildings they are leaving is step 36's `BuildingLife`.",
      "Step 36 `Disasters` and `BuildingLife`, both sourced there; the cast is this table's "
      "reading, mark estimated", mark="estimated"),

    S("refugees", "refugees on the road", "suffering", "gate", "migration",
      {"service": 2, "farming": 2, "craft": 2, "trade": 1, "soldier": 1},
      "a road full of people who did not choose to be on it, and how long it takes to walk",
      "Which road, how many people, whether anybody made them go, and how many days the walking "
      "takes: step 38's `Migrations`, thirty-eight dated records. The Partition of India — "
      "**15,700,000** people across four roads — is in there, and Lahore to Amritsar is fifty-one "
      "kilometres and about two days on foot.",
      "Step 38 `Migrations`, sourced there; the cast is this table's reading, mark estimated",
      mark="estimated"),

    S("fire", "a fire", "suffering", "street", "disaster",
      {"craft": 3, "service": 3, "official": 1, "trade": 1},
      "a bucket chain, and things being pulled down to stop it",
      "Fire is one of the ten kinds in step 36's hazard pack. A fire in a town of timber is the "
      "fastest scene here: it is over in hours, and everything afterwards is the reckoning.",
      "Step 36 `Disasters`, sourced there; the cast is this table's reading, mark estimated",
      mark="estimated"),

    # ------------------------------------------------------------------ war
    S("battle", "a battle", "war", "field", "event",
      {"soldier": 6, "transport": 1, "service": 1},
      "two bodies of armed people, and the ground between them",
      "Which battle and when is step 28's event gazetteer. **This register does not stage the "
      "fighting** — weapons and army gear are step 45 (E9, C19, A13) and armies in action are "
      "step 40 (D10). What this scene holds is the part of a battle that is not the fighting: the "
      "camp, the baggage, the wounded, and the people who came to watch.",
      "Step 28 `HistoryGazetteer`; the cast is this table's reading, mark estimated",
      mark="estimated"),

    S("siege", "a siege", "war", "gate", "event",
      {"soldier": 4, "craft": 2, "farming": 1, "service": 2, "official": 1},
      "a wall, the people inside it running out of food, and the people outside waiting",
      "`war/SiegeEngineController` already runs sieges mechanically. This scene is what the siege "
      "looks like from inside: the register reads `Needs` for how short of food the town is, "
      "because that is what a siege is actually about.",
      "Step 38 `Needs`; `war/SiegeEngineController`; the cast is this table's reading, mark "
      "estimated", mark="estimated"),

    # ------------------------------------------------------------------ the life of a family
    S("wedding", "a wedding", "life", "temple", "life",
      {"clergy": 1, "service": 2, "craft": 1, "farming": 2, "trade": 1},
      "a couple, two families who are not sure about each other, and a feast",
      "Since the **Fourth Lateran Council of 1215** a marriage in the Latin church had to be "
      "announced first: the banns, the couple's names read out in church on **three Sundays** "
      "running. The feast is the bigger part — medieval wedding feasts ran to three days, with a "
      "high table for the important and stools for everybody else.",
      "English Wikipedia, 'Banns of marriage' and 'Fourth Council of the Lateran'; the cast is "
      "this table's reading, mark estimated", mark="mixed"),

    S("funeral", "a funeral", "life", "cemetery", "life",
      {"clergy": 1, "service": 2, "farming": 2, "craft": 1},
      "a wake that ran through the night, and then the walk to the grave",
      "The wake comes first — the night before, with relatives and neighbours, food and drink set "
      "out — and the procession is in the morning. In most of the world for most of history the "
      "dead were **carried**, by their own male kin on a bier, and not put in a vehicle. How old "
      "the person was when they died is step 38's `LifeTable`, which is the number that decides "
      "whether this is an old person's funeral or a child's.",
      "English Wikipedia, 'Funeral procession' and 'Wake (ceremony)'; step 38 `LifeTable`, "
      "sourced there; the cast is this table's reading, mark estimated", mark="mixed"),
]
