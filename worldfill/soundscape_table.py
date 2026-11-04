#!/usr/bin/env python3
"""Step 43 part 2 (J2, sounds of the era): what a place sounds like, and why.

Why this is hand-written
------------------------

No source states, as a fact, that a given square of the map in a given century was loud with bells.
So this table is a reading, every row is estimated, and every row says so.

**What is not a reading is what makes the row fire.** That is the whole design of this part, and it
is the opposite of the code this step replaces. `HistoricalAudioDirector` picked one of six
soundscapes from the year alone - `x` and `z` were parameters it never read - so China in 1000 came
back *Classical Mediterranean* and everything after 1920 came back *PASTORAL_ANCIENT*. Every row
below instead hangs off a register that the mod already ships and that answers by place:

  * `voice` rows fire from the **faith of the polity that rules here**, which is derived:
    `RulerRegister.rulerAt(lat, lon, year).wikidata()` -> `LeaderRegister.facts(qid).faithIn(year)`.
    Measured in the survey: **959 of the 960 polities carrying a religion join to the ruler
    register - 100%**. The `rel` list has no years of its own, so it is dated by the polity's span,
    which is the trick step 42 part 6 used to fix the C18 law pack.
  * `machine` rows fire from the **technology atlas**, per country and dated: `railway` reaches
    Britain in 1825 and India in 1874 (Wadi to Secunderabad, the Nizam's railway), `car` Germany in
    1886. `TechnologyAtlas.present(id, lat, lon, year, rank)` answers it.
  * `crowd` rows fire from **step 17's own `SettlementDensity.intensity`**, which already scales a
    murmur by the simulated population. That half was good work and is reused, not rewritten.
  * `ground` rows fire from `CountryGrid.nearSea`, which is a real question with a real answer.

So the reading is only ever *what it sounds like*, never *whether it is there*.

Four layers, because they are four different questions
------------------------------------------------------

  * `ground`  - the place, whether or not anybody is in it. Never silent.
  * `crowd`   - how many people are here
  * `voice`   - what they do on purpose, at set hours, because of what they believe
  * `machine` - what has reached this country

Each row carries `when`, because a soundscape is not a list of sounds but a **day**: the call to
prayer is before dawn, the bell is on the hour, the market is in the morning, and a train is when
the train comes.

What this pack cannot do
------------------------

**The mod has no audio assets, and this step cannot record any.** What J2 fixes is *which* sound
belongs here and *why* - the part that is currently nonsense. What is actually heard will still be
played with whatever sounds exist, and that is recorded as a limit rather than hidden.
"""

# --------------------------------------------------------------------------- rows

def voice(rid, name, faiths, what, when, line, priority, source, **extra):
    r = dict(id=rid, kind="voice", name=name, faiths=list(faiths), what=what, when=when,
             line=line, priority=priority, source=source,
             where=None, tech=None, minIntensity=0.0, coast=None, loud=2,
             catchAll=False)
    r.update(extra)
    return r


def machine(rid, name, tech, what, when, line, priority, source, **extra):
    """A machine sound. Fires when the technology has ARRIVED at this place, which the atlas
    dates per country (railway: York 1827, Delhi 1864). `industrial` says whether it is part of
    the Industrial Revolution or only an old machine - a water mill is a machine, but a country
    full of water mills is not an industrial country, and `Here.industrial()` must not say it is."""
    r = dict(id=rid, kind="machine", name=name, tech=tech, what=what, when=when,
             line=line, priority=priority, source=source,
             where=None, faiths=[], minIntensity=0.0, coast=None, loud=2,
             industrial=True)
    r.update(extra)
    return r


def crowd(rid, name, min_intensity, what, when, line, priority, source, **extra):
    r = dict(id=rid, kind="crowd", name=name, minIntensity=min_intensity, what=what, when=when,
             line=line, priority=priority, source=source,
             where=None, faiths=[], tech=None, coast=None, loud=2,
             catchAll=False)
    r.update(extra)
    return r


def ground(rid, name, coast, what, when, line, priority, source, **extra):
    r = dict(id=rid, kind="ground", name=name, coast=coast, what=what, when=when,
             line=line, priority=priority, source=source,
             where=None, faiths=[], tech=None, minIntensity=0.0, loud=1)
    r.update(extra)
    return r


# --------------------------------------------------------------------------- the ground
# Every place has one of these. A place with nobody in it is not a silent place.

GROUND = [
    ground("sea", "the sea", True,
           "the water on the shore, and the wind over it",
           "always",
           "the sea is the loudest thing here and it does not stop: the breakers, the drag of the "
           "shingle, and everything else a man makes has to be said over the top of it",
           2, "Sea", loud=3),

    ground("inland", "the wind and the trees", False,
           "the wind, and whatever it is moving through",
           "always",
           "inland there is no shore to keep up a noise, so what you hear is the weather: the wind "
           "in whatever grows here, and at night the things that live in it",
           1, "Wind"),
]

# --------------------------------------------------------------------------- the crowd
# Reused from step 17: SettlementDensity.intensity already worked this out, and it is scaled by the
# SIMULATED population rather than the number of people drawn.

CROWD = [
    crowd("market", "the market", 0.35,
          "buying and selling, and the voices raised over it",
          "in the morning, and again towards evening",
          "this is a place with enough people in it to have a market, and a market is not a murmur: "
          "it is men calling what they have, animals, the ring of a coin on a board, and a bargain "
          "conducted at the top of the voice",
          3, "Market (place)", loud=3),

    crowd("murmur", "the murmur", 0.12,
          "people near enough to hear, and not near enough to make out",
          "all day",
          "there are people here. You cannot hear what any of them says, and you can hear that they "
          "are saying it",
          2, "AmbientCrowdSoundManager", loud=1),

    crowd("settled", "a settled place", 0.03,
          "a door, a dog, a beast in a byre",
          "in the day",
          "somebody is living here. Not enough to be a crowd - a door shuts, a dog barks once, "
          "something is fed",
          1, "SettlementDensity", loud=1),
]

# --------------------------------------------------------------------------- the voice
# What the people here do on purpose, at set hours, because of what they believe. Keyed to the 30
# faith families CultureAtlas already matches on, so there is one faith vocabulary in the mod.

VOICE = [
    voice("adhan", "the call to prayer", ["muslim", "shia"],
          "a man's voice from a high place, five times between before dawn and after dark",
          "before dawn, at noon, in the afternoon, at sunset, and at night",
          "the muezzin calls from the minaret and the whole town keeps the hours by it. Nothing "
          "else in this pack stops the street: the call goes up, the shops wait, and when it is "
          "done the noise comes back",
          5, "Adhan", loud=3),

    voice("church_bells", "the church bells", ["christian_west"],
          "bronze bells in a tower, rung for the hour and for the office",
          "on the hour, and at the hours of prayer",
          "the bells are the clock. A village that owns nothing else owns a bell, and it is rung "
          "for the angelus at dawn and at noon, for a wedding, for a death, and - the sound nobody "
          "forgets - to raise the parish against a fire or a raid",
          5, "Church bell", loud=3),

    voice("orthodox_bells", "the great bell", ["christian_east"],
          "one big bell swung slow, and the chanting inside",
          "before the liturgy, and at the feasts",
          "not a peal but a single great bell swung in a slow stroke, over and over, and underneath "
          "it the singing of a congregation standing - there are no seats, and the singing does not "
          "stop",
          5, "Blagovest; Eastern Orthodox church bell", loud=3),

    voice("temple_bells", "the temple bells and the conch", ["hindu"],
          "a bell at the shrine, the conch blown at dawn, and drums when the image goes out",
          "at dawn and at dusk, and whenever the image is carried",
          "you ring the bell as you come in, so the god knows you have come. At the hour of the "
          "arati the conch goes and the drums start, and on a feast day the whole street is the "
          "procession",
          5, "Hindu temple; Conch", loud=3),

    voice("chanting", "the chanting", ["buddhist", "theravada", "tibetan"],
          "a drone of voices in the temple, and a bell struck between the verses",
          "at dawn and at dusk",
          "the monks chant and the sound that carries is not the words but the drone underneath "
          "them, low and unbroken, with a bell struck at the joins",
          4, "Buddhist chant; Tibetan Buddhism", loud=2),

    voice("kirtan", "the kirtan", ["sikh"],
          "hymns sung in the gurdwara, with a drum and a stringed instrument",
          "from before dawn, and through the day",
          "the singing starts before it is light and it is sung by everybody and not by a choir: a "
          "drum, a harmonium, and the hymn going round the room",
          4, "Kirtan", loud=2),

    voice("shofar", "the shofar", ["jewish"],
          "a ram's horn, blown in the synagogue",
          "at the new year and the day of atonement, and on the sabbath's end",
          "for most of the year there is nothing to hear but the sabbath quiet. Then the horn goes "
          "- a raw sound, not a tune - and it is blown at the times of the year that are about "
          "being called to account",
          3, "Shofar", loud=2),

    voice("firecrackers", "the firecrackers", ["chinese_folk", "vietnamese_folk", "korean_folk"],
          "crackers let off at the temple, and a drum",
          "at the new year, and at any wedding or funeral",
          "the noise is the point of it: crackers are let off to drive off what is bad, so a "
          "festival is measured by how much of the street you cannot hear yourself think in",
          4, "Firecracker", loud=3),

    voice("shrine_clap", "the clap at the shrine", ["shinto"],
          "two claps at the shrine, a bell pulled on its rope, and the noise of a festival",
          "when anyone comes to pray, and at the matsuri",
          "you clap twice to announce yourself, you pull the bell rope, and on a festival day the "
          "whole thing is carried through the streets on men's shoulders to drums and shouting",
          3, "Shinto shrine; Matsuri", loud=2),

    voice("fire_temple", "the fire", ["zoroastrian"],
          "the chanting of the old texts before a fire that is never let out",
          "at the five watches of the day",
          "there is very little to hear, and that is the sound of it: the fire is tended in "
          "silence, and what is said is said in a language nobody outside the priesthood speaks",
          2, "Zoroastrianism", loud=1),

    voice("shaman_drum", "the drum", ["tengri", "folk"],
          "a drum, and a man singing himself somewhere else",
          "when there is cause: a sickness, a death, a thing to be found",
          "not on a schedule. The drum is beaten when someone needs the shaman to go somewhere, "
          "and it goes on until he comes back",
          2, "Shamanism", loud=2),

    voice("temple_rite", "the rite at the temple",
          ["egyptian", "greek", "roman", "mesopotamian", "aztec", "inca"],
          "flutes and drums at the sacrifice, and the crowd that came to see it",
          "on the feast days of the god",
          "the god is carried out, the flutes play, the beast is killed in front of everybody, and "
          "the whole city is there for it. On an ordinary day the temple is quiet - the noise "
          "belongs to the calendar",
          3, "Ancient Egyptian religion; Greco-Roman religion; Aztec religion", loud=2),

    voice("pagan_quiet", "nothing made on purpose",
          ["norse", "slavic", "celtic", "vedic", "manichaean"],
          "the wind, the cattle, and the sound of work",
          "never",
          "there is no bell in this place, because there is no building to hang one in. The gods "
          "are at a grove or a spring or a stone, and what you hear is the farm going about its "
          "day - which is the honest answer, and the one the old soundscape could not give",
          1, "Germanic paganism; Slavic paganism; Celtic polytheism", loud=1),

    voice("jain_silence", "very little", ["jain"],
          "almost nothing: the ideal is silence, and the temples are quiet",
          "rarely",
          "a Jain temple is the quietest building in any town in India. What you hear outside it is "
          "everybody else",
          1, "Jainism", loud=0),

    voice("unknown_gods", "gods the pack does not know", [],
          "people at their devotions, in a way this pack cannot name",
          "at the feast days, whatever they are",
          "there is a faith here and it is not one of the thirty the mod carries - 27 of the 960 "
          "polities with a religion are like this, and the honest answer is to say so rather than "
          "to leave the place silent. Somebody is praying. The pack does not know to whom, or when, "
          "or what it sounds like",
          2, "none - the gap is recorded, not filled", catchAll=True, loud=1),

    voice("loudspeaker", "the loudspeaker", ["soviet"],
          "a loudspeaker on a pole, and the parade",
          "at the set hours, and on the days of the state",
          "the bells have been taken down and what is put up instead is a loudspeaker: it gives the "
          "hour, it gives the news, and on the first of May it gives the parade marching past",
          5, "Soviet Union", loud=3),
]

# --------------------------------------------------------------------------- the machine
# Fires from the technology atlas, per country and dated, on ARRIVAL. No threshold: the year the
# thing reached this country is measured, so guessing how common it must be before you can hear it
# would only make it less true.
# before you can hear it: one railway in a country is a wonder, a hundred is a noise.

MACHINE = [
    machine("trains", "the trains", "railway",
            "a locomotive, and the noise it brings with it: the shunt, the whistle, the iron",
            "when the train comes, and all night in a yard",
            "the railway does not just add a sound, it adds a new kind of silence between two of "
            "them: a whistle a mile off, then the ground shaking, then the roar, then nothing at "
            "all. In a town near the line the whole day is measured by it",
            5, "Railway; Steam locomotive", loud=3),

    machine("cars", "the traffic", "car",
            "engines, horns, and the hiss of tyres on a made road",
            "all day, and loudest morning and evening",
            "once the motor car is common, no street in the world is ever quiet again. This is the "
            "one sound in this pack that never stops, day or night, anywhere near a road",
            5, "Car; Traffic", loud=3),

    machine("aircraft", "the aircraft", "air_travel",
            "engines overhead, and the window frames ringing",
            "a few times a day, on the line between two cities",
            "you do not hear it for long, and you hear it from miles: the sound arrives from "
            "somewhere you cannot see and takes a long time to go away",
            4, "Aircraft", loud=2),

    machine("steam_works", "the works", "steam_engine",
            "a beam engine going over, all day and all night, and the belts",
            "always - it does not stop",
            "the engine does not stop. That is what is new about it: before this, everything a man "
            "made was quiet when he stopped working, and now there is a thing that beats all night "
            "and nobody is working",
            4, "Steam engine; Factory", loud=2),

    machine("ironworks", "the ironworks", "ironworks",
            "the blast, the hammers, and the slag being tipped",
            "through the working day, and the blast all night",
            "a coke furnace is lit and stays lit for years. The hammers you can hear three valleys "
            "off, and the light of it is on the clouds",
            4, "Ironworks; Blast furnace", loud=3),

    machine("watermill", "the mill", "watermill",
            "the wheel, the stones going round, and the sluice",
            "in the day, whenever there is water",
            "everybody's mill is on the same stream and everybody hears everybody else's. It is the "
            "one machine sound that is older than the country it stands in",
            2, "Watermill", loud=1, industrial=False),
]

ALL = GROUND + CROWD + VOICE + MACHINE

# --------------------------------------------------------------------------- the default
# Not also a row: as a row it matched everywhere and the fallback could never fire - the defect
# F3 hit in step 42 and D7 hit before it.

DEFAULT = {
    "id": "wind", "kind": "ground", "name": "the wind", "faiths": [], "tech": None,
    "what": "the wind, and nothing else",
    "when": "always",
    "line": "there is nobody here and nothing here has been made to make a noise. The wind goes "
            "over the ground and that is the whole of it",
    "priority": 0, "source": "Wind", "where": None, "minIntensity": 0.0,
    "coast": None, "loud": 1,
}
