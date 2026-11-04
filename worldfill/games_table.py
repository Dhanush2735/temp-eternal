#!/usr/bin/env python3
"""
Step 47 part 6 (E17): **games and sports** — chess, polo, cricket, kites, theatre, cinema.

    python3 games_table.py           check the register and print it

The plan's row is *"Games and sports: chess, polo, cricket, kites, theatre, cinema"* and the survey
found the state "Not yet", which was accurate on the code side and wrong on the data side: the
products atlas already carries `chess`, `dice`, `backgammon`, `kites`, `playing_cards`, `puppets`,
`dolls`, `drums`, `flutes`, `theatre` and `fireworks` with a year for all 17 areas. **What nothing
carries is the game as a thing people play**: where it came from, who plays it, whether it needs a
field or a board, and whether the crowd is part of it.

## The design decision this register makes, and it is the opposite of the crop register

For crops every area has an arrival year, because the atlas computed one for every area from a
technology and a parent. For games that is not honest: nobody can say in what year polo reached
Java. So here:

* the **origin** is always written, with a year and a place;
* a **spread** year is written only where the record gives one;
* everywhere else the answer is `unknown`, and `unknown` is not the same as `never`.

That is the reverse of B6's `NEVER` sentinel and it is deliberate: for a crop, a missing year means
the atlas says it never arrives; for a game, a missing year means **we did not look and will not
guess**. A game register that invents an arrival for kabaddi in Peru is worse than one that says it
does not know.

## The finding

**A game is the cheapest thing a culture exports and the last thing it gives up.** The board games
travel with merchants (backgammon from Mesopotamia, chess from India, cards from China) and cross
every border within a few centuries; the *sports* travel with empires and then with schools, and the
codified ones are all astonishingly late. Football is a folk game everywhere and a **rule** in 1863;
basketball 1891; the modern Olympics 1896. Before the nineteenth century what a crowd watches is not
a sport but a **spectacle**: the games of Greece, the games of Rome, and the ball game of Mesoamerica,
which is a religious obligation with a ballcourt in the middle of the city and, at the end of some
of them, a death.
"""

AREAS = ["NNA", "MNA", "CAC", "SAM", "EUR", "EEU", "WAS", "NAF", "WAF", "MSA", "EAF", "CAS",
         "SAS", "EAS", "SEA", "AUS", "PAC"]

# What kind of thing it is, because a game and a sport and a play need different towns.
KINDS = ["board", "dice", "ball", "athletic", "combat", "blood", "children", "stage", "screen",
         "hunt"]

# Who is playing: one person, two, a side, or a crowd watching other people.
PLAYERS = ["one", "two", "side", "several", "watched"]

GAMES = [
    # ---- THE BOARD GAMES: the ones that travel with merchants ---------------------------------
    dict(id="dice", name="dice", kind="dice", year=-3000, home="WAS", players="several",
         equipment="dice", spread={"WAS": -3000, "NAF": -3000, "SAS": -2500, "EUR": -2000,
                                  "EAS": -1500, "CAS": -1500, "EEU": -1200, "SEA": -500,
                                  "WAF": 800, "MSA": 800, "EAF": 800, "CAC": 1500, "SAM": 1530,
                                  "NNA": 1600, "MNA": 1500, "AUS": 1788, "PAC": 1800},
         note=(
        "**The oldest game and the one with the fewest rules.** Knucklebones and painted cubes are "
        "in Egyptian tombs and the Rigveda; the loaded die is as old as the honest one. Games of "
        "chance are also the reason divination and gambling are the same word in several languages, "
        "and why the church argued about them for a thousand years."),
         source="the Egyptian and Mesopotamian gaming sets; the Rigveda on the dice"),
    dict(id="backgammon", name="the tables", kind="board", year=-3000, home="WAS",
         players="two", equipment="backgammon",
         spread={"WAS": -3000, "NAF": -3000, "CAS": -2000, "SAS": -2000, "EUR": -1000,
                 "EAS": 700, "EEU": 900, "MSA": 800, "SEA": 900, "CAC": 1500, "SAM": 1530,
                 "NNA": 1600, "MNA": 1500, "AUS": 1788, "PAC": 1800},
         note=(
        "**The Royal Game of Ur is its ancestor and the board is in the British Museum.** It is a "
        "race game with dice, it is played in Mesopotamia by 3000 BC, it reaches Europe as the Roman "
        "*tabula*, it is banned repeatedly in medieval Europe because soldiers gamble on it, and it "
        "is still played in the same form in Iran. **Three thousand years with the same rules is "
        "rare in anything.**"),
         source="the Royal Game of Ur boards; the Roman tabula; the medieval prohibitions"),
    dict(id="chess", name="chess", kind="board", year=600, home="SAS", players="two",
         equipment="chess",
         spread={"SAS": 600, "CAS": 700, "WAS": 750, "NAF": 800, "EUR": 1000, "EAS": 800,
                 "SEA": 1000, "EEU": 1100, "MSA": 1400, "EAF": 1400, "WAF": 1600,
                 "MNA": 1700, "NNA": 1700, "CAC": 1700, "SAM": 1750, "AUS": 1800, "PAC": 1850},
         note=(
        "**A war game with an army in it, invented where the army was.** Chaturanga in Gupta India "
        "about AD 600 has infantry, cavalry, elephants and chariots, which become the pawn, knight, "
        "bishop and rook as it crosses Persia: the *shah mat* of the Persian form is where "
        "'checkmate' comes from. **The queen is the most powerful piece because the game was "
        "changed to make it faster in the 1470s in Spain**, which is the only piece in any old game "
        "whose power is a datable decision."),
         source="the chaturanga and shatranj texts; the 1471 Valencian poem on the new game"),
    dict(id="go", name="go", kind="board", year=-500, home="EAS", players="two", equipment=None,
         spread={"EAS": -500, "SEA": 700, "CAS": 900, "SAS": 1200, "EUR": 1800, "NNA": 1900,
                 "SAM": 1900, "AUS": 1900},
         note=(
        "**The oldest game still played with its original rules and no luck in it at all.** It is "
        "Chinese, it is one of the four arts a gentleman was expected to know, and it stayed inside "
        "East Asia until the nineteenth century. The absence of a Minecraft item is honest and is "
        "recorded: the game needs a board and two colours of stones, and the stones are the point."),
         source="the Zuo Zhuan; the four arts of the Chinese scholar"),
    dict(id="playing_cards", name="playing cards", kind="board", year=800, home="EAS",
         players="several", equipment="playing_cards",
         spread={"EAS": 800, "SEA": 1000, "SAS": 1100, "CAS": 1200, "WAS": 1300, "NAF": 1300,
                 "EUR": 1370, "EEU": 1400, "MSA": 1500, "EAF": 1500, "WAF": 1600, "NNA": 1600,
                 "MNA": 1600, "CAC": 1600, "SAM": 1650, "AUS": 1800, "PAC": 1800},
         note=(
        "**Paper money and paper games come from the same place and the same century.** Cards are "
        "Chinese, they reach Europe through the Mamluk court (the same 52-card deck with four suits "
        "and court cards, and the Mamluk deck is in the Topkapi), and Europe gives them the "
        "printing press. The four suits are a fifteenth-century European choice among dozens."),
         source="the Tang and Song card records; the Mamluk Topkapi deck; the 1377 European ban"),
    dict(id="mahjong", name="mahjong", kind="board", year=1870, home="EAS", players="several",
         equipment=None, spread={"EAS": 1870, "NNA": 1920, "EUR": 1920, "SAS": 1920,
                                 "AUS": 1930},
         note=(
        "**The one game here that is younger than the telegraph and pretends not to be.** It is "
        "assembled in the 1870s in the Yangtze delta out of older card and domino games, and its "
        "twentieth-century career in the West is a fad. **A 'ancient Chinese game' that is "
        "contemporary with the telephone** is exactly the kind of thing this register is for."),
         source="the 1870s Shanghai records; the 1920s Western mahjong boom"),
    # ---- THE SPORTS: the crowd is the point ------------------------------------------------
    dict(id="wrestling", name="wrestling", kind="combat", year=-3000, home="WAS", players="two",
         equipment=None,
         spread={"WAS": -3000, "NAF": -3000, "EUR": -2000, "SAS": -2000, "EAS": -1500, "CAS": -1500,
                 "EEU": -1200, "SEA": -500, "WAF": 0, "MSA": 0, "EAF": 0, "CAC": 1500,
                 "SAM": 1520, "NNA": 1600, "MNA": 1500, "AUS": 1788, "PAC": 1800},
         note=(
        "**The only sport that needs nothing, which is why it is everywhere.** Akkadian and Egyptian "
        "reliefs show it, it is an Olympic event in 708 BC, Japanese sumo is attested in the 8th "
        "century, and Indo-Persian *pehlwani* has a gymnasium culture with its own diet. **It is "
        "also the sport with the most deaths**: Greek wrestling was a break, Roman wrestling was "
        "not, and the difference is the crowd."),
         source="the Beni Hasan tomb paintings; the Olympic programme; the sumo records"),
    dict(id="foot_race", name="the foot race", kind="athletic", year=-3000, home="WAS",
         players="several", equipment=None,
         spread={"WAS": -3000, "NAF": -3000, "EUR": -2000, "SAS": -2000, "EAS": -1500, "CAS": -1500,
                 "EEU": -1200, "SEA": -500, "WAF": 0, "MSA": 0, "EAF": 0, "CAC": 1500,
                 "SAM": 1520, "NNA": 1600, "MNA": 1500, "AUS": 1788, "PAC": 1800},
         note=(
        "**The oldest organised competition we have a date for: 776 BC at Olympia.** A foot race is "
        "the whole of the first thirteen Olympics; everything else is added later. **The marathon is "
        "1896 and is a modern invention that retroactively invents a Greek one**, which is a useful "
        "warning about any sport that claims an ancient pedigree."),
         source="the Olympic victor lists; the 1896 marathon"),
    dict(id="chariot_racing", name="chariot racing", kind="athletic", year=-700, home="WAS",
         players="several", equipment=None,
         spread={"WAS": -700, "EUR": -600, "NAF": -500, "EEU": -500, "CAS": -400, "SAS": -300,
                 "EAS": -200},
         note=(
        "**The biggest spectator sport of the ancient world, and it kills its own fans.** The "
        "Hippodrome in Constantinople holds 100,000 and the *demes* that support the chariot "
        "factions are political parties: the Nika riot of 532 nearly takes the city. **The sport "
        "ends when the horses do not pay**: it survives in Rome and Byzantium and dies with them."),
         source="the Circus Maximus and the Hippodrome records; Procopius on the Nika riot"),
    dict(id="gladiator", name="the gladiator", kind="blood", year=-264, home="EUR",
         players="watched", equipment=None,
         spread={"EUR": -264, "NAF": -200, "WAS": -100, "EEU": -100},
         note=(
        "**A Roman invention, not an Etruscan one, and it begins at a funeral.** The first show is "
        "264 BC in the Forum Boarium, staged by three pairs to honour a dead father: it is a funeral "
        "rite before it is entertainment. **It never spreads outside the Roman world and it is "
        "banned by an emperor in 404 who is himself a Christian, which is a good example of a "
        "practice that is Roman rather than ancient."),
         source="the 264 BC funeral games; the 404 ban"),
    dict(id="polo", name="polo", kind="athletic", year=600, home="CAS", players="side",
         equipment=None,
         spread={"CAS": 600, "WAS": 800, "SAS": 900, "EAS": 900, "EEU": 1000, "EUR": 1860,
                 "NNA": 1870, "SAM": 1880, "AUS": 1880},
         note=(
        "**A cavalry exercise that became a court game and then a British import.** Persian "
        "*chogan* is attested by the 6th century and used as a training exercise for cavalry; "
        "the Mughals play it, and Akbar plays it at night with a burning ball. **The British learn "
        "it in Manipur in the 1850s and take it to England**, which is why the modern rules are "
        "written in London in 1875."),
         source="the Persian chogan records; the Akbarnama; the 1875 Hurlingham rules"),
    dict(id="mesoamerican_ball", name="the ball game", kind="blood", year=-1400, home="CAC",
         players="side", equipment=None,
         spread={"CAC": -1400, "MNA": -1400, "SAM": -1000},
         note=(
        "**The one ball game in this register that is a religious obligation.** A rubber ball, a "
        "stone ballcourt in the middle of the city, protective yokes of stone, and a game that "
        "stands for the movement of the sun; in the Popol Vuh the hero twins play against the lords "
        "of the underworld and the loser dies. **It never leaves Mesoamerica**, which is the "
        "sharpest example of a game that does not travel: it is not entertainment and cannot be "
        "exported without its gods."),
         source="the Popol Vuh; the ballcourts of Chichen Itza and El Tajin"),
    dict(id="kabaddi", name="kabaddi", kind="combat", year=-500, home="SAS", players="side",
         equipment=None, spread={"SAS": -500, "SEA": 1000, "EAS": 1200},
         note=(
        "**A game that needs no equipment, one line on the ground, and a single breath.** The "
        "player who raids must chant 'kabaddi' without stopping, which is the rule that makes it a "
        "test of lung capacity. It stays in South Asia until the twentieth century and becomes a "
        "national sport there only after 1947, which is a reminder that 'ancient national sport' is "
        "usually a nineteenth-century idea."),
         source="the Indian wrestling and akhara tradition; the 1918 rules"),
    dict(id="kites", name="kites", kind="children", year=-400, home="EAS", players="one",
         equipment="kites",
         spread={"EAS": -400, "SEA": 800, "SAS": 1000, "CAS": 1200, "WAS": 1200, "EUR": 1500,
                 "NAF": 1500, "EEU": 1600, "NNA": 1750, "SAM": 1800, "AUS": 1800},
         note=(
        "**A toy that is also a military signal and a weather experiment.** Chinese kites carry "
        "messages, measure wind for artillery, and are flown in spring festivals; the Mughals fight "
        "kites in the air over Lahore. **Franklin's 1752 experiment is the same object used as "
        "science**, and the Wrights' 1899 glider is a kite."),
         source="the Chinese kite records; the Mughal kite-flying accounts; Franklin 1752"),
    dict(id="falconry", name="falconry", kind="hunt", year=-2000, home="CAS", players="one",
         equipment=None,
         spread={"CAS": -2000, "WAS": -1500, "SAS": -1000, "EAS": -500, "EUR": 300, "NAF": 300,
                 "EEU": 500, "WAF": 1000, "NNA": 1600, "MNA": 1600},
         note=(
        "**The only field sport that needs a trained animal and a book about it.** Assyrian reliefs "
        "show it, the Mughals make it a court art with a literature, and medieval Europe ranks it "
        "by the rank of the bird: a kestrel for a knave. **It is a hunt, not a game**, which is why "
        "it is in this register and not in B5: the animal is not the point."),
         source="the Assyrian falconry reliefs; the Mughal and European falconry manuals"),
    dict(id="theatre", name="the theatre", kind="stage", year=-534, home="EUR", players="watched",
         equipment="theatre",
         spread={"EUR": -534, "WAS": -300, "NAF": -200, "SAS": 200, "EAS": 700, "SEA": 1000,
                 "CAS": 1200, "EEU": 1500, "MNA": 1590, "SAM": 1600, "NNA": 1750},
         note=(
        "**A Greek civic institution with a date: the first dramatic contest at Athens is 534 BC.** "
        "It is a religious festival with a state prize, the audience is the citizen body, and the "
        "building is a machine for making one voice carry to fifteen thousand people. **Japan, India "
        "and China have their own theatres centuries old and completely unlike it**; the register "
        "records the European arrival and says so."),
         source="the Athenian didascaliae; the Noh and Sanskrit theatre traditions"),
    dict(id="cinema", name="the cinema", kind="screen", year=1895, home="EUR", players="watched",
         equipment=None,
         spread={"EUR": 1895, "NNA": 1896, "SAS": 1896, "EAS": 1896, "AUS": 1896, "SAM": 1896,
                 "NAF": 1896, "WAS": 1896, "EEU": 1896, "SEA": 1896, "MNA": 1896, "CAS": 1896,
                 "MSA": 1900, "EAF": 1900, "WAF": 1900, "PAC": 1910},
         note=(
        "**The fastest spread in this register and the first art form that is a machine.** The "
        "Lumiere brothers show it in Paris in December 1895 and there is a cinema in Cairo, Bombay "
        "and Tokyo within a year, because the apparatus is a product and can be shipped. **It arrives "
        "before the aeroplane and after the telephone**, and no other item in this register moved "
        "that fast."),
         source="the Lumiere 1895 screenings; the first cinemas of Cairo and Bombay"),
    dict(id="football", name="football", kind="ball", year=1863, home="EUR", players="side",
         equipment=None,
         spread={"EUR": 1863, "SAM": 1870, "NNA": 1869, "EEU": 1890, "WAS": 1900, "NAF": 1900,
                 "SAS": 1870, "EAS": 1900, "SEA": 1900, "AUS": 1880, "CAS": 1900, "MSA": 1900,
                 "EAF": 1900, "WAF": 1900, "MNA": 1900, "CAC": 1900, "PAC": 1920},
         note=(
        "**A folk game everywhere and a RULE nowhere until 1863.** Every village in Europe kicks "
        "something; the Football Association writes the rules in a London tavern in 1863 and the "
        "difference between football and rugby is one meeting and one decision about handling. "
        "**The spread follows the empire and the schools**, which is why the oldest clubs in "
        "Argentina and India are British."),
         source="the 1863 Football Association minutes; the spread by sailors and schools"),
    dict(id="cricket", name="cricket", kind="ball", year=1550, home="EUR", players="side",
         equipment=None,
         spread={"EUR": 1550, "SAS": 1721, "AUS": 1803, "NNA": 1700, "NAF": 1800, "EAF": 1890,
                 "WAF": 1900, "SEA": 1900},
         note=(
        "**A children's game that became the administrative language of an empire.** It is played "
        "in south-east England by 1550 (there is a 1598 court case about a pitch), it is banned "
        "during the Civil War, and it reaches India with sailors by 1721 and Australia by 1803. "
        "**The first international match is 1844 between the United States and Canada**, which "
        "nobody expects."),
         source="the 1598 Guildford court case; the 1844 USA-Canada match"),
    dict(id="basketball", name="basketball", kind="ball", year=1891, home="NNA", players="side",
         equipment=None, spread={"NNA": 1891, "EUR": 1893, "SAS": 1900, "EAS": 1900, "AUS": 1900,
                                 "SAM": 1900, "EEU": 1900, "NAF": 1900},
         note=(
        "**An invented game with a named inventor, which is almost unique among the old sports.** "
        "James Naismith, a YMCA training school in Springfield, Massachusetts, 1891: he is asked for "
        "an indoor game for a winter class and writes thirteen rules in a fortnight. **The peach "
        "basket is the first hoop and it has a bottom in it**, so somebody has to fetch the ball "
        "with a ladder until 1906."),
         source="Naismith's 1891 rules; the 1906 open-net change"),
    dict(id="olympic_games", name="the Olympic games", kind="athletic", year=-776, home="EUR",
         players="several", equipment=None, spread={"EUR": -776, "WAS": -500, "NAF": -300,
                                                    "EEU": -300},
         note=(
        "**A religious festival with a truce, and the modern version is a different event.** The "
        "ancient games run from 776 BC to about AD 393 and are abolished by Theodosius as a pagan "
        "rite; the modern ones start in **1896**, invented by a Frenchman, with a marathon distance "
        "that is standardised only in 1921. **Two thousand years apart and only the name is the "
        "same**, which is the trap this row exists to mark."),
         source="the Olympic victor lists; the 393 abolition; Coubertin 1896"),
]

# The plan names chess, polo, cricket, kites, theatre and cinema. All six must be present, or this
# register has not answered the question it was given.
PLAN_NAMES = ["chess", "polo", "cricket", "kites", "theatre", "cinema"]

# Order of events that must hold, as an independent written expectation.
MUST_PRECEDE = [("dice", "backgammon"), ("dice", "chess"), ("foot_race", "olympic_games"),
                ("theatre", "cinema"), ("chariot_racing", "polo"), ("wrestling", "kabaddi")]


def problems():
    bad = []
    seen = set()
    for g in GAMES:
        if g["id"] in seen:
            bad.append("duplicate game " + g["id"])
        seen.add(g["id"])
        if g["kind"] not in KINDS:
            bad.append(g["id"] + " has the kind " + str(g["kind"]))
        if g["players"] not in PLAYERS:
            bad.append(g["id"] + " has the players " + str(g["players"]))
        if g["home"] not in AREAS:
            bad.append(g["id"] + " comes from " + str(g["home"]) + ", which is not an area")
        if g["home"] not in g["spread"]:
            bad.append(g["id"] + " does not exist in its own home")
        elif g["spread"][g["home"]] != g["year"]:
            bad.append(g["id"] + " is dated " + str(g["year"]) + " and its home says "
                       + str(g["spread"][g["home"]]))
        for a, y in g["spread"].items():
            if a not in AREAS:
                bad.append(g["id"] + " spreads to " + a + ", which is not an area")
            if y < g["year"]:
                bad.append(g["id"] + " is in " + a + " in " + str(y)
                           + ", before it exists (" + str(g["year"]) + ")")
        if not g["note"] or len(g["note"]) < 80:
            bad.append(g["id"] + " does not say anything useful")
        if not g["source"]:
            bad.append(g["id"] + " cites nothing")

    for name in PLAN_NAMES:
        if name not in seen:
            bad.append("the plan names " + name + " and this register does not carry it")

    by = {g["id"]: g for g in GAMES}
    for a, b in MUST_PRECEDE:
        if a not in by or b not in by:
            bad.append("the order check names " + a + " and " + b + ", and one of them is missing")
        elif by[a]["year"] > by[b]["year"]:
            bad.append(a + " cannot come after " + b)
        elif by[a]["year"] == by[b]["year"] and a != "dice":
            bad.append(a + " and " + b + " are the same year, and only the dice may be")

    # THE FINDING, AS A TEST: the codified modern sports are all late, and the ball games that need
    # a field are not modern at all.
    for codified in ("football", "basketball", "cricket"):
        if by[codified]["year"] < 1500:
            bad.append(codified + " is dated " + str(by[codified]["year"])
                       + ": a codified sport cannot be medieval")

    # Cinema comes after the theatre, and the mesoamerican ball game is older than every sport here.
    if by["cinema"]["year"] <= by["theatre"]["year"]:
        bad.append("the cinema cannot precede the theatre")
    for other in ("football", "cricket", "basketball"):
        if by["mesoamerican_ball"]["year"] >= by[other]["year"]:
            bad.append("the ball game of Mesoamerica is the oldest ball game in the register and is "
                       "dated after " + other)

    # AN ABSENCE IS `unknown`, NOT `never`. At least half the games must be unrecorded in most
    # areas, because the register refuses to invent an arrival and that refusal has to show.
    sparse = [g for g in GAMES if len(g["spread"]) < len(AREAS) / 2]
    if len(sparse) < 3:
        bad.append("only " + str(len(sparse)) + " games are unrecorded in most of the world: this "
                   "register is supposed to refuse to guess, and it has guessed everywhere")
    return bad


def main():
    bad = problems()
    print("games: %d games over %d areas; %d recorded in all 17, %d recorded in fewer than half"
          % (len(GAMES), len({a for g in GAMES for a in g["spread"]}),
             len([g for g in GAMES if len(g["spread"]) == len(AREAS)]),
             len([g for g in GAMES if len(g["spread"]) < len(AREAS) / 2])))
    print()
    print("  %-18s %-9s %-9s %-7s %-6s %s"
          % ("game", "kind", "home", "from", "areas", "players"))
    for g in GAMES:
        print("  %-18s %-9s %-9s %-7s %-6s %s"
              % (g["id"], g["kind"], g["home"], g["year"], len(g["spread"]), g["players"]))
    for p in bad:
        print("  PROBLEM " + p)
    print("games_table: %d problem(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
