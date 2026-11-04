"""
Step 44 part E6: what part of a meal each food is.

The atlas knows 76 foods and when each reaches a place. What it does not know is that a lentil and
a mango play different parts at a table, and that a place with wheat, lentils, ghee and chillies
has a meal to describe while a place with wheat alone does not.

So every food gets a **seat at the table**. This is hand-written, because no register carries it,
and it is checked against the pack so a role can never be given to a food that does not exist.

The seats are the ones a meal actually has:

- **staple** — the bulk of the calories: a grain or a root
- **pulse** — the protein that keeps, and the partner to the grain
- **green** — leaves and vegetables, the thing that does not keep
- **fruit** — sweet flesh, in season
- **protein** — fish, meat, eggs, and what comes out of an animal
- **fat** — what it is cooked in
- **sour** — what sharpens it: vinegar, lime, tamarind, curd
- **sweet** — what ends it, or what the children are given
- **seasoning** — salt, spice and heat
- **drink** — what is drunk with it, and after
- **stimulant** — tea, coffee, cacao: not food, and not quite drink either

A food may hold more than one seat (coconut is a fat and a fruit; yoghurt is a protein and a
sour), and a seat may be empty, which is a fact about the place and not a gap in the table.
"""

# product id -> the seats it holds, in the order it would be named
SEATS = {
    # ------------------------------------------------------------------ the bulk
    "wheat": ["staple"], "rice": ["staple"], "millet": ["staple"], "sorghum": ["staple"],
    # barley is folded into "wheat and barley" in the atlas, and is not a product of its own
    "maize": ["staple"], "oats": ["staple"], "rye": ["staple"],
    "buckwheat": ["staple"], "potato": ["staple"], "cassava": ["staple"], "roots": ["staple"],
    "breadfruit": ["staple"], "sago": ["staple"], "plantain": ["staple"],
    "sweet_potato": ["staple"], "oilseeds": ["fat"],
    "acorns": ["staple"],
    "wild_food": ["staple", "green", "protein"],

    # ------------------------------------------------------------------ the partner
    "pulses": ["pulse"], "groundnut": ["pulse", "fat"], "soybean": ["pulse"],

    # ------------------------------------------------------------------ what does not keep
    "greens": ["green"], "onions": ["green", "seasoning"], "carrots": ["green"],
    "cucumbers": ["green"], "melons": ["green", "fruit"], "tomatoes": ["green"],
    "apples": ["fruit"], "citrus": ["fruit", "sour"],
    "grapes": ["fruit"], "dates": ["fruit", "sweet"], "olives": ["fruit", "fat"],
    "coconut": ["fruit", "fat"], "pineapple": ["fruit"], "peas": ["green", "pulse"],

    # ------------------------------------------------------------------ from an animal
    "fish": ["protein"], "dried_fish": ["protein"], "salt_meat": ["protein"],
    "meat": ["protein"], "eggs": ["protein"], "dairy": ["protein", "drink"],
    "cheese": ["protein"], "yoghurt": ["protein", "sour"], "ghee": ["fat"],

    # ------------------------------------------------------------------ what it is cooked in
    "olive_oil": ["fat"], "cooking_oil": ["fat"], "palm_oil": ["fat"],

    # ------------------------------------------------------------------ what sharpens it
    "vinegar": ["sour"], "pickles": ["sour", "seasoning"],

    # ------------------------------------------------------------------ what ends it
    "honey": ["sweet"], "sugar": ["sweet"], "jaggery": ["sweet"], "sugarcane": ["sweet"],
    "candy": ["sweet"], "cacao": ["stimulant", "sweet"], "chocolate": ["sweet", "stimulant"],
    "vanilla": ["seasoning"],

    # ------------------------------------------------------------------ salt, spice and heat
    "salt": ["seasoning"], "spices": ["seasoning"], "pepper": ["seasoning"],
    "chillies": ["seasoning"], "ginger": ["seasoning"], "turmeric": ["seasoning"],
    "cumin": ["seasoning"],          # the atlas calls it "cumin and coriander"
    "cardamom": ["seasoning"],
    "cinnamon": ["seasoning"], "cloves": ["seasoning"], "nutmeg": ["seasoning"],
    "saffron": ["seasoning"], "fenugreek": ["seasoning"], "asafoetida": ["seasoning"],

    # ------------------------------------------------------------------ what is drunk
    "beer": ["drink"], "wine": ["drink"], "spirits": ["drink"],
    "toddy": ["drink"], "arrack": ["drink"], "tea": ["stimulant", "drink"],
    "coffee": ["stimulant", "drink"], "coffee_houses": ["stimulant"],

    # ------------------------------------------------------------------ kept against a bad year
    "tinned_food": ["staple", "protein"],
}

# The order a meal is described in, and the words used for a seat that is empty.
SEAT_ORDER = ["staple", "pulse", "green", "fruit", "protein", "fat", "sour", "sweet",
              "seasoning", "drink", "stimulant"]

# Flour, bread, pasta, porridge and semolina are the grain after it has been milled or cooked,
# not a second thing at the table. Giving them the grain's seat as well meant southern China ate
# "millet, or buckwheat, or porridge" and never got as far as the rice it is famous for. They are
# named here so the check below knows they are meant to hold no seat, rather than forgotten.
PREPARED = {
    "flour": "wheat", "semolina": "wheat", "rice_flour": "rice", "bread": "wheat",
    "porridge": "wheat", "pasta": "wheat",
}

SEAT_WORDS = {
    "staple": "the grain",
    "pulse": "the pulse",
    "green": "the greens",
    "fruit": "the fruit",
    "protein": "the meat or fish",
    "fat": "the fat it is cooked in",
    "sour": "what sharpens it",
    "sweet": "the sweet",
    "seasoning": "the seasoning",
    "drink": "the drink",
    "stimulant": "the stimulant",
}

# Seats without which a place has no meal to speak of. A place with grain and salt has a diet,
# however thin; a place with only a stimulant does not.
BARE_MINIMUM = ["staple"]


def seats_of(pid):
    """The seats this product holds, or an empty list when it is not part of a meal."""
    return SEATS.get(pid, [])


def check_against(products):
    """Every id in this table must be a food the atlas carries, or the seat names nothing."""
    ids = {p["id"] for p in products}
    out = []
    # Every food in the atlas has to sit somewhere. The sweet potato was added to the atlas in
    # part 6 and left out of this table, and the only symptom was that Tahiti in 1300 threw it
    # away for acorns -- which is not the kind of thing a reader is expected to notice.
    for p in products:
        if (p["family"] in ("staple food", "other food and drink") and p["id"] not in SEATS
                and p["id"] not in PREPARED):
            out.append("%s ('%s') is a food but holds no seat" % (p["id"], p["name"]))
    for pid, of in PREPARED.items():
        if pid in SEATS:
            out.append("%s is a preparation of %s and should hold no seat" % (pid, of))
    for pid, seats in SEATS.items():
        if pid not in ids:
            out.append("%s: is not a product" % pid)
        for s in seats:
            if s not in SEAT_ORDER:
                out.append("%s: unknown seat '%s'" % (pid, s))
    return out


if __name__ == "__main__":
    import collections
    import json
    import os

    path = os.path.join("eternal", "src", "main", "resources", "data", "eternalengine",
                        "eternal", "economy", "products_world.json")
    with open(path, encoding="utf-8") as fh:
        prods = json.load(fh)["products"]
    probs = check_against(prods)
    counts = collections.Counter(s for seats in SEATS.values() for s in seats)
    print("diet seats: %d foods, %d seats" % (len(SEATS), len(SEAT_ORDER)))
    for s in SEAT_ORDER:
        print("   %-12s %3d" % (s, counts.get(s, 0)))
    for p in probs:
        print("  PROBLEM", p)
    print("diet_roles: %d problem(s)" % len(probs))
