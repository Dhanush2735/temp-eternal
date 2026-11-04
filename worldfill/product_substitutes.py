"""
Step 44 part E (E5): what people use when the thing they would use is not there.

Part D wrote down what each product is made from and who makes it. This is the other half of the
same question: when a thing cannot be had, what takes its place. It cannot be derived — there is
no register of substitutions anywhere in the mod, and no crop, mine or technology implies one — so
it is written out by hand, the way part B's products were, and every row says why.

The shape is: a product, and a list of alternatives with a note on how good a substitute it is.
`good` means people would barely notice; `serves` means it does the job badly; `last resort` means
it is eaten or burned when there is nothing else, which is the interesting case for a famine.

Two rules kept throughout:

1. **The substitute must exist in the pack.** A famine food that is not a product is not an
   answer, so `check_against` rejects any id the atlas does not carry — the same guard as
   product_chains, and it caught four invented ids while this was being written.
2. **The substitute must be plausible in the same world.** Chicory for coffee is real (it was
   drunk through the Continental Blockade and both world wars). Acorns for grain is real (they fed
   Greece, Iberia and California and are the classic famine food). But a substitute is only
   offered for a place and year where *it* is there, which the atlas decides at run time; this
   table only says what would do.
"""

# ----------------------------------------------------------------------------- what stands in

# id -> [(substitute id, how good, why)]
SUBSTITUTES = {
    # ---------------------------------------------------------------- staple food
    "wheat": [          ("millet", "good", "the grain of the dry lands, and of most of Africa and Asia"),
              ("rye", "good", "the grain that grows where wheat will not, on poor cold land"),
              ("oats", "serves", "gruel and oatcakes; more cattle food than bread"),
              ("acorns", "last resort", "leached of their tannin they are the famine food of the oak woods")],
    "rice": [("millet", "good", "the grain of the dry lands, and of most of Africa and Asia"),
             ("cassava", "serves", "a root that yields where rice will not"),
             ("sorghum", "good", "the grain of the dry lands, and of most of Africa and Asia")],
    "maize": [("cassava", "good", "the root that stands in for grain across the tropics"),
              ("potato", "good", "the other American root, and the one that fed Ireland")],
    "potato": [("cassava", "good", "the root that stands in for grain across the tropics"),
               ("maize", "good", "the other American staple")],
    "bread": [("porridge", "good", "the grain boiled instead of baked; no oven, no mill"),
              ("acorns", "last resort", "leached of their tannin they are the famine food of the oak woods")],
    "flour": [("porridge", "good", "the grain boiled instead of baked; no oven, no mill"),
              ("acorns", "last resort", "ground and leached, in a bad year")],

    # ---------------------------------------------------------------- sweet
    "sugar": [("honey", "good", "the sweetener before cane, and the only one in most of the world"),
              ("jaggery", "good", "unrefined cane, made where the crystal sugar is not"),
              ("acorns", "last resort", "leached of their tannin they are the famine food of the oak woods")],
    "honey": [("sugar", "good", "once cane is refined it is cheaper than honey everywhere"),
              ("jaggery", "good", "unrefined cane, made where the crystal sugar is not")],

    # ---------------------------------------------------------------- cloth
    "cotton": [("wool", "good", "the fibre of cold countries and of everywhere without cotton"),
               ("linen", "good", "flax, the oldest cloth in Europe and Egypt"),
               ("hemp", "serves", "coarse, but it grows anywhere and clothes the poor"),
               ("bark_cloth", "serves", "beaten bark: the cloth of the Pacific and of the Congo")],
    "wool": [("linen", "good", "flax, the oldest cloth in Europe and Egypt"),
             ("cotton", "good", "the fibre that replaces wool wherever it can be grown"),
             ("hides_furs", "serves", "what a herding people wears anyway")],
    "silk": [("cotton", "serves", "the common fibre; it does not shine and it does not whisper"),
             ("linen", "serves", "flax, the oldest cloth in Europe and Egypt")],
    "leather": [("mill_cloth", "serves", "woven cloth where hide is scarce or forbidden"),
                ("bark_cloth", "serves", "beaten bark: the cloth of the Pacific and of the Congo")],

    # ---------------------------------------------------------------- fuel and light
    "firewood": [("charcoal", "good", "wood twice burned; the smith's fuel and the town's"),
                 ("peat", "good", "cut and dried, the fuel of the bog countries"),
                 ("dung_fuel", "serves", "dried dung, where there is no wood at all"),
                 ("coal", "good", "the stone that burns, once it is dug")],
    "charcoal": [("firewood", "good", "raw wood, where a kiln is not worth the trouble"),
                 ("coal", "good", "the stone that burns, once it is dug"),
                 ("peat", "serves", "cut and dried, the fuel of the bog countries")],
    "coal": [("firewood", "good", "what everyone burned before coal"),
             ("charcoal", "good", "wood twice burned; the smith's fuel and the town's"),
             ("peat", "good", "cut and dried, the fuel of the bog countries")],
    "oil_lamp": [("candles", "good", "tallow, where there is no oil to burn"),
                 ("tallow_candles", "good", "tallow, where there is no oil to burn"),
                 ("firelight", "serves", "a torch or the hearth itself")],
    "candles": [("oil_lamp", "good", "a lamp of oil, the older light"),
                ("rushlights", "serves", "a rush dipped in fat; the poor man's candle"),
                ("firelight", "serves", "a torch or the hearth itself")],

    # ---------------------------------------------------------------- metals
    "iron": [("bronze", "serves", "the older metal, and better than iron for some things"),
             ("bone", "last resort", "horn and stone, which is what iron replaced")],
    "iron_tools": [("stone_tools", "last resort", "flint and ground stone, which is what came before"),
                   ("bone", "last resort", "horn and stone, which is what iron replaced")],
    "copper": [("bronze", "good", "copper with tin in it: harder, and casts better"),
               ("iron", "serves", "once iron comes it is cheaper than copper everywhere")],
    "bronze": [("iron", "good", "the metal that ended the bronze age"),
               ("brass", "good", "copper with zinc; used for the same vessels and fittings")],

    # ---------------------------------------------------------------- writing
    "paper": [("parchment", "good", "scraped skin; what all of Europe wrote on before paper came"),
              ("palm_leaf", "good", "the leaf-book of India and of South-East Asia"),
              ("clay_tablets", "serves", "clay, which keeps better than either"),
              ("bark_cloth", "serves", "beaten bark, written on where nothing else is")],
    "parchment": [("paper", "good", "cheaper, once it arrives from the east"),
                  ("palm_leaf", "serves", "the leaf-book of India and of South-East Asia")],
    "ink": [("charcoal", "serves", "soot and gum: the ink of Egypt and of China"),
            ("dyes", "last resort", "any dark juice, if it will not wash off")],
    "books": [("palm_leaf", "serves", "the leaf-book of India and of South-East Asia"),
              ("parchment", "serves", "a scroll or a codex of skin, written by hand")],

    # ---------------------------------------------------------------- drink and stimulants
    "coffee": [("tea", "good", "the other caffeine, and the one Asia had first"),
               ("coffee_houses", "serves", "the same bean, ground and roasted at home")],
    "tea": [("coffee", "good", "the other caffeine, and the one the west took up"),
            ("beer", "serves", "weak beer, which is what most of Europe drank anyway")],
    "beer": [("wine", "good", "the drink of the vine countries"),
             ("spirits", "serves", "distilled, where there is grain or fruit to spare")],

    # ---------------------------------------------------------------- the rest
    "soap": [("potash", "last resort", "lye from the ashes; caustic, but it scours"),
             ("clay", "last resort", "fuller's earth, which is how cloth was cleaned")],
    "salt": [("potash", "last resort", "wood ash leached for its salts, where the salt pans are far")],
    "glass": [("mica", "serves", "thin stone in a frame: the window of old Russia and of China"),
              ("oil_lamp", "last resort", "not a window; only something to see by")],
    "pottery": [("baskets", "serves", "woven and lined with clay, a basket will hold grain"),
                ("leather", "serves", "a skin bottle, which is what the steppe uses")],
    "dairy": [("cooking_oil", "serves", "sesame, mustard or coconut, whichever grows")],
    "ghee": [("dairy", "good", "the same fat, unclarified"),
             ("cooking_oil", "good", "sesame, mustard or coconut, whichever grows")],
    "olive_oil": [("cooking_oil", "good", "sesame, mustard or coconut, whichever grows"),
                  ("dairy", "serves", "the fat of the cattle countries")],
    "eggs": [("meat", "serves", "any protein, if there is any")],
    "meat": [("fish", "good", "the river and the sea, which do not need feeding"),
             ("dried_fish", "good", "fish kept, which travels where cattle will not"),
             ("eggs", "serves", "the poor man's meat")],
    "fish": [("meat", "good", "the herd and the flock"),
             ("dried_fish", "good", "fish kept, which travels where cattle will not")],
}

# A shock to the land, the hands or the roofs does not hit every good alike. Part D gave every
# product the kind of work that makes it, and that is what decides: a crop fails and the food
# goes; the sickness takes the people and the making goes; the wall comes down and the workshop
# goes with it.
#
# (shares of the field shock, the labour shock, the roof shock, the trade shock)
WORK_SENSITIVITY = {
    "farming":  (1.0, 0.5, 0.0, 0.0),   # the crop is the thing; fewer hands helps little
    "herding":  (0.7, 0.5, 0.0, 0.0),   # pasture fails with the rain, and herds are tended
    "foraging": (0.8, 0.3, 0.0, 0.0),   # wild food fails with the season too
    "craft":    (0.1, 0.6, 0.8, 0.2),   # hands and a roof above all
    "miner":    (0.0, 0.7, 0.5, 0.1),   # the pit needs men and a working headframe
    "trade":    (0.0, 0.4, 0.2, 1.0),   # a merchant dies if the road shuts
    "service":  (0.0, 0.7, 0.3, 0.0),
    "transport": (0.0, 0.6, 0.2, 1.0),
    "official": (0.0, 0.7, 0.5, 0.1),   # a clerk needs a roof and a government
    "scholar":  (0.0, 0.7, 0.5, 0.1),
    "clergy":   (0.0, 0.6, 0.4, 0.0),
    "soldier":  (0.0, 0.8, 0.1, 0.0),
}

DEFAULT_SENSITIVITY = (0.2, 0.5, 0.4, 0.2)


def sensitivity(work):
    """How hard a shock to the land, the hands, the roofs and the road hits this kind of work."""
    return WORK_SENSITIVITY.get(work, DEFAULT_SENSITIVITY)


def for_product(pid):
    """What stands in for this product, best first."""
    return SUBSTITUTES.get(pid, [])


def check_against(products):
    """
    Every id in this table must be a product the atlas carries, or the answer names something that
    does not exist. Same guard as product_chains.check_against, and it earns its keep: it caught
    four ids invented while this was being written.
    """
    ids = {p["id"] for p in products}
    problems = []
    for pid, subs in SUBSTITUTES.items():
        if pid not in ids:
            problems.append("%s: is not a product" % pid)
        for sub, how, why in subs:
            if sub not in ids:
                problems.append("%s: substitute '%s' is not a product" % (pid, sub))
            if how not in ("good", "serves", "last resort"):
                problems.append("%s: '%s' is not a rating" % (pid, how))
            if not why:
                problems.append("%s: '%s' has no reason" % (pid, sub))
    # and the chain should not point a thing at itself
    for pid, subs in SUBSTITUTES.items():
        for sub, _, _ in subs:
            if sub == pid:
                problems.append("%s: substitutes itself" % pid)
    return problems


if __name__ == "__main__":
    import json
    import os

    path = os.path.join("eternal", "src", "main", "resources", "data", "eternalengine",
                        "eternal", "economy", "products_world.json")
    with open(path, encoding="utf-8") as fh:
        prods = json.load(fh)["products"]
    probs = check_against(prods)
    print("substitutes: %d products, %d links, %d kinds of work" % (
        len(SUBSTITUTES), sum(len(v) for v in SUBSTITUTES.values()), len(WORK_SENSITIVITY)))
    for p in probs:
        print("  PROBLEM", p)
    print("product_substitutes: %d problem(s)" % len(probs))
