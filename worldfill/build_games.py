#!/usr/bin/env python3
"""Step 47 part 6 (E17): pack the games and sports register."""
import gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                   "eternal", "names", "games.json.gz")
sys.path.insert(0, HERE)
try:
    import games_table as G
finally:
    sys.path.pop(0)


def build():
    problems = list(G.problems())
    rows = [{"id": g["id"], "name": g["name"], "kind": g["kind"], "year": g["year"],
             "home": g["home"], "players": g["players"], "equipment": g["equipment"],
             "spread": g["spread"], "note": g["note"], "source": g["source"]}
            for g in G.GAMES]
    doc = {
        "format": "eternal-games-1", "id": "games", "areas": G.AREAS, "kinds": G.KINDS,
        "players": G.PLAYERS,
        "source": ("the Royal Game of Ur boards; the chaturanga and shatranj texts; the Mamluk "
                   "Topkapi deck; the 1598 Guildford cricket case; the 1863 Football Association "
                   "minutes; Naismith's 1891 rules; the Lumiere 1895 screenings."),
        "note": ("Step 47 part 6 (E17): GAMES AND SPORTS. The plan names chess, polo, cricket, "
                 "kites, theatre and cinema, and the survey said 'not yet' - accurate about the "
                 "code and wrong about the data, because the products atlas already carries chess, "
                 "dice, backgammon, kites, playing_cards, puppets, dolls, drums, flutes, theatre and "
                 "fireworks with a year for all 17 areas. What nothing carried is the GAME as a "
                 "thing people play: where it came from, who plays it, and whether a crowd is part "
                 "of it. 21 games over 9 kinds."),
        "finding": ("**A game is the cheapest thing a culture exports and the last thing it gives "
                    "up.** Board games travel with merchants and cross every border within a few "
                    "centuries (backgammon from Mesopotamia, chess from India, cards from China), "
                    "while the sports travel with empires and then with schools - and the codified "
                    "ones are astonishingly late: football is a folk game everywhere and a RULE in "
                    "1863, basketball is 1891, the modern Olympics are 1896. Before the nineteenth "
                    "century a crowd does not watch a sport, it watches a SPECTACLE: the games of "
                    "Greece, the games of Rome, and the ball game of Mesoamerica, which is a "
                    "religious obligation with a ballcourt in the middle of the city and, at the "
                    "end of some of them, a death. **This register also refuses to guess.** A crop "
                    "has an arrival in every area because the atlas computed one; nobody can say "
                    "when polo reached Java, so a game here has an origin and only the spread years "
                    "the record gives. Everywhere else the answer is `unknown`, which is not the "
                    "same as `never`."),
        "games": rows,
        "counts": {"games": len(rows),
                   "inAllAreas": sum(1 for r in rows if len(r["spread"]) == len(G.AREAS)),
                   "inFewerThanHalf": sum(1 for r in rows
                                          if len(r["spread"]) < len(G.AREAS) / 2),
                   "oldest": min(rows, key=lambda r: r["year"])["id"],
                   "newest": max(rows, key=lambda r: r["year"])["id"]},
    }
    assert not problems, problems
    assert doc["counts"]["games"] >= 18
    return doc, problems


def main():
    doc, problems = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode()
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    print("games.json.gz: %d B (%d raw), %d games, %d problems"
          % (os.path.getsize(OUT), len(raw), len(doc["games"]), len(problems)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
