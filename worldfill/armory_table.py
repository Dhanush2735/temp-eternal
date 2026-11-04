"""
Step 45 part 2 (E9 A): the armoury — what weapons and armour exist, where and when.

The survey found that the raw material is nearly all in the mod already and that **every join is
missing**. Three registers carry pieces of this:

- `technology_atlas.json.gz` — 13 weapon technologies x **258 countries**, with `needs` and
  `replaces` chains. Country-level, spread-modelled. The precise source.
- `products_world.json` — 33 products in a **"weapons and armour"** family, dated in 17 areas.
  Built by step 44 part C. Area-level.
- `formations.json.gz` — 16 dated formations, each naming its `arm`, over a **twelve-word
  vocabulary** D10's casualty bands are keyed to.

**E9 must speak D10's twelve words** (arquebus, bow, cannon, chariot, elephant, horsebow, javelin,
musket, pike, rifle, spear, sword) or the two steps will not join.

**Where the product atlas cannot be trusted for weapons.** Part C derived each product's date from
a *parent* — and for the melee family the parents are **materials**, not weapons:

    spears   <- bows            clubs    <- timber      daggers  <- copper
    shields  <- leather         slings   <- hemp        pikes    <- iron_weapons
    lances   <- iron_weapons    swords   <- bronze_weapons

That is the right heuristic for a product and the wrong one for a weapon. It produces
**`spears` at 1800 in Australia** (inherited from `bows`, which is right about the bow and wrong
about the spear), **`daggers` at 1700 in North America** (from copper, when stone knives are ten
thousand years older), and **`pikes` and `lances` as the same row**. So this register writes the
melee family by hand — there are only ten of them and the literature is not ambiguous about the
basics.

**Two debts this step inherits.**

`bows` carries a note written by step 44 part C and addressed here: *"Australia had no bows; the
weapons step decides who may have them."* This is the answer. The bow was never locally invented
on the Australian continent and never spread to it, though the people of the Torres Strait — the
only part of Australia that had it — used it, and though Australians were in contact with bow-using
peoples to the north. The reasons are measured: **Australian woods are sub-optimal for self-bows**
(George 2024, *Economic Botany*, 326 species tested, 106 of them native Australian), and in local
conditions **a spear from a woomera carries four times the kinetic energy of an arrow from a
compound bow**, so the bow offered no advantage worth taking. The diffusion even ran **backwards**:
the spearthrower spread among Torres Strait Islanders who had previously used the bow (Darmangeat).
So: **no bow in AUS, and `spears` must not inherit `bows`' date.**

`armour` ("Metal armour") says -2000 in West Asia while `mail_armour` says -116 there. Copper
plate is old but a Sumerian of 2000 BC was not wearing a mail shirt; the three armour rows are
reconciled below.

**An absence here is a fact, not a gap.** No metal sword in the Americas before 1492. No bow in
Australia. No plate armour outside Europe and the Spanish conquest.
"""

# A kind of weapon or armour.
#
#   id          a name for the row
#   arm         D10's word for it, from the twelve in formations.json.gz, or None when no
#               formation names it (a shield is not a formation's arm)
#   name        plain words
#   role        melee | missile | mount | siege | protection
#   use         thrust | cut | throw | shoot | charge | besiege | wear
#   tech        the technology atlas row, or None
#   product     the product atlas row, or None
#   material    what it is made from, for the chains join
#   years       per-area first year, 17 areas, written by hand ONLY where the product atlas
#               derives from a material and gets it wrong. Elsewhere None, meaning "read the
#               tech atlas, then the product atlas".
#   never       {area: why} — recorded absences
#   supersedes  kinds this retires
#   vanilla     the Minecraft item to fall back on when no weapon mod is installed
#   mark        recorded | measured | estimated
#   note        what the row means
#   source      where it came from

AREAS = ["EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA", "WAF", "MSA", "EAF",
         "NNA", "MNA", "CAC", "SAM", "PAC", "AUS"]

ARMORY = [
    # ---------------------------------------------------------------- the ones that are always there
    #
    # These three are universal and precede every register's floor. The product atlas has them at
    # -10000 everywhere except AUS and PAC, where it inherited 1800 from `bows`. That is the single
    # worst error in the pack, because a spear is the one weapon every human society had.
    dict(id="spear", arm="spear", name="the spear", role="melee", use="thrust",
         tech=None, product="spears", material="wood_stone",
         years={"EUR": -10000, "EEU": -10000, "WAS": -10000, "NAF": -10000, "CAS": -10000,
                "SAS": -10000, "EAS": -10000, "SEA": -10000, "WAF": -10000, "MSA": -10000,
                "EAF": -10000, "NNA": -10000, "MNA": -10000, "CAC": -10000, "SAM": -10000,
                "PAC": -10000, "AUS": -10000},
         never={}, supersedes=[], vanilla="minecraft:stone_sword", mark="recorded",
         endTech="rifle",
         note="Every human society had it, and Australia most of all: the spear and the "
              "spearthrower held the whole of the ranged and the close niche on that continent. "
              "The product atlas had it at 1800 in AUS and PAC because part C derived it from "
              "'bows', which is right about the bow and wrong about the spear. Corrected here.",
         source="Wikipedia, Spear; Woomera (spear-thrower)"),

    dict(id="club", arm=None, name="the club", role="melee", use="cut",
         tech=None, product="clubs", material="wood_stone",
         years={"EUR": -10000, "EEU": -10000, "WAS": -10000, "NAF": -10000, "CAS": -10000,
                "SAS": -10000, "EAS": -10000, "SEA": -10000, "WAF": -10000, "MSA": -10000,
                "EAF": -10000, "NNA": -10000, "MNA": -10000, "CAC": -10000, "SAM": -10000,
                "PAC": -10000, "AUS": -10000},
         never={}, supersedes=[], vanilla="minecraft:wooden_sword", mark="recorded",
         endTech="rifle",
         note="A stick. Everywhere, always. The woomera itself doubled as one.",
         source="Wikipedia, Club (weapon)"),

    dict(id="dagger", arm=None, name="the dagger", role="melee", use="cut",
         tech=None, product="daggers", material="stone",
         years={"EUR": -10000, "EEU": -10000, "WAS": -10000, "NAF": -10000, "CAS": -10000,
                "SAS": -10000, "EAS": -10000, "SEA": -10000, "WAF": -10000, "MSA": -10000,
                "EAF": -10000, "NNA": -10000, "MNA": -10000, "CAC": -10000, "SAM": -10000,
                "PAC": -10000, "AUS": -10000},
         never={}, supersedes=[], vanilla="minecraft:stone_sword", mark="recorded",
         note="A knife is older than metal by tens of thousands of years. The product atlas had "
              "NNA at 1700 because part C derived daggers from 'copper'; the Old Copper Complex "
              "of the Great Lakes is itself four thousand years older than that, and flint "
              "knives older still.",
         source="Wikipedia, Knife; Old Copper Complex"),

    dict(id="bow", arm="bow", name="the bow", role="missile", use="shoot",
         tech=None, product="bows", material="wood_sinew",
         years={"EUR": -10000, "EEU": -10000, "WAS": -10000, "NAF": -10000, "CAS": -10000,
                "SAS": -10000, "EAS": -10000, "SEA": -10000, "WAF": -10000, "MSA": -10000,
                "EAF": -10000, "NNA": -10000, "MNA": -10000, "CAC": -10000, "SAM": -10000,
                "PAC": None, "AUS": None},
         never={"AUS": "the bow was never locally invented on the Australian continent and never "
                       "spread to it, though the Torres Strait - the only part of Australia that "
                       "had it - used it and Australians traded with bow-using peoples to the "
                       "north. Australian woods test as sub-optimal for self-bows, and a spear "
                       "from a woomera carries four times the kinetic energy of an arrow from a "
                       "compound bow, so the bow had nothing to offer. The diffusion ran the "
                       "other way: the spearthrower spread to Torres Strait Islanders who had "
                       "used the bow. Step 44 left a note asking this step to decide.",
                "PAC": "Polynesia had no bow. Papua and the islands to Australia's north did, "
                       "which is what makes the Australian absence a finding rather than an "
                       "artefact of isolation."},
         supersedes=[],
         vanilla="minecraft:bow", mark="recorded",
         endTech="rifle",
         note="The one weapon the product atlas got right to be uncertain about, and the row "
              "step 44 handed to this step. Answered: never in Australia, never in Polynesia.",
         source="Darmangeat, The Bow That Wasn't; George 2024, Is Australian Flora Unsuitable "
                "for the Bow-and-Arrow? (Economic Botany); Wikipedia, Bow and arrow"),

    dict(id="javelin", arm="javelin", name="the javelin", role="missile", use="throw",
         tech=None, product=None, material="wood_bronze",
         years={"EUR": -3000, "EEU": -3000, "WAS": -3000, "NAF": -3000, "CAS": -3000,
                "SAS": -3000, "EAS": -2000, "SEA": -2000, "WAF": -2000, "MSA": -2000,
                "EAF": -2000, "NNA": -3000, "MNA": -3000, "CAC": -3000, "SAM": -3000,
                "PAC": -1000, "AUS": -10000},
         never={}, supersedes=[], vanilla="minecraft:stone_sword", mark="recorded",
         endTech="flintlock",
         note="A spear you throw, which makes it a different weapon from a spear you hold. "
              "**D10 names it and nothing else did**: step 40 ships the roman_triplex at "
              "-300 to 476 with arm=javelin, the pilum's formation, and the product atlas has "
              "no row for it at all - 'Spears and javelins' quietly merges the two. The "
              "velite, the peltast, the aketon, and the Zulu before the horns closed.",
         source="Wikipedia, Javelin; Pilum"),

    dict(id="sling", arm=None, name="the sling", role="missile", use="throw",
         tech=None, product="slings", material="fibre",
         years={"EUR": -3000, "EEU": -3000, "WAS": -5000, "NAF": -3000, "CAS": -3000,
                "SAS": -3000, "EAS": -2000, "SEA": -1000, "WAF": -1000, "MSA": -1000,
                "EAF": -1000, "NNA": -1000, "MNA": -1000, "CAC": -2000, "SAM": -2000,
                "PAC": None, "AUS": None},
         never={"AUS": "the ranged niche in Australia was filled by the boomerang and the "
                       "woomera, not by the sling or the bow",
                "PAC": "no sling in Polynesia"},
         supersedes=[],
         vanilla="minecraft:snowball", mark="estimated",
         endTech="matchlock",
         note="Cheap, ancient, and very widely spread - the Balearic slingers, the Benjaminites "
              "of the Book of Judges, the Inca. The product atlas gave it only eight of "
              "seventeen areas because part C derived it from 'hemp', which is a material and "
              "not a weapon.",
         source="Wikipedia, Sling (weapon)"),

    # ---------------------------------------------------------------- metal melee
    dict(id="sword", arm="sword", name="the sword", role="melee", use="cut",
         tech=None, product="swords", material="bronze",
         years=None,   # the product atlas has this right: derived from bronze_weapons
         never={"NNA": "no metal sword in North America before 1492",
                "MNA": "no metal sword in Mesoamerica before 1492 - the macuahuitl is a club "
                       "with stone blades, which is not the same thing",
                "CAC": "no metal sword in the Circum-Caribbean before 1492",
                "SAM": "no metal sword in South America before 1492",
                "PAC": "no metal in Oceania",
                "AUS": "no metal working at all in pre-contact Australia"},
         supersedes=[],
         vanilla="minecraft:iron_sword", mark="recorded",
         endTech="rifle",
         note="Needs bronze or iron, which is why it is absent from the whole Americas, Oceania "
              "and Australia - a fact the product atlas already has right, and one of the "
              "cleanest absences in the register.",
         source="Wikipedia, Sword; Bronze Age; Iron Age"),

    dict(id="pike", arm="pike", name="the pike", role="melee", use="thrust",
         tech=None, product="pikes", material="iron_steel",
         years={"EUR": -350, "EEU": -350, "WAS": -350, "NAF": -150, "CAS": -150, "SAS": 1500,
                "EAS": 1550, "SEA": 1600, "WAF": 1600, "MSA": 1600, "EAF": 1600,
                "NNA": 1750, "MNA": 1700, "CAC": 1700, "SAM": 1700, "PAC": 1800, "AUS": 1788},
         never={}, supersedes=[], vanilla="minecraft:iron_sword", mark="recorded",
         endTech="flintlock",
         note="Two separate births, and this row carries the earlier one. **The sarissa**: "
              "Philip II of Macedon, mid-fourth century BC, four to six and a half metres, five "
              "rows of points in front of the front rank. Long-shafted staff weapons then fell "
              "out of favour for sixteen centuries, and **the pike was reinvented** by the Swiss "
              "in the late fourteenth - Morgarten 1315 with halberds, Sempach 1386, the pike "
              "square by 1476. The product atlas had EUR at -850 because it derived pikes from "
              "'iron_weapons', and gave pikes and lances the identical row. EAS is 1550 to match "
              "the nagae-yari formation step 40 already ships at 1550-1615.",
         source="Wikipedia, Pike (weapon); Sarissa; Pike square"),

    dict(id="lance", arm=None, name="the lance", role="mount", use="charge",
         tech="stirrup", product="lances", material="wood_iron",
         years={"EUR": 700, "EEU": 800, "WAS": 600, "NAF": 700, "CAS": 600, "SAS": 600,
                "EAS": 700, "SEA": 800, "WAF": 1000, "MSA": 1000, "EAF": 1000,
                "NNA": 1700, "MNA": 1520, "CAC": 1520, "SAM": 1540, "PAC": 1800, "AUS": 1788},
         never={}, supersedes=[], vanilla="minecraft:iron_sword", mark="recorded",
         endTech="rifle",
         note="What makes the lance a lance is the **couched** technique - tucked under the "
              "armpit against a lance rest, so the whole momentum of horse and rider goes into "
              "the point - and that needs the stirrup. So this row is dated from the stirrup, "
              "which the technology atlas carries at 300, spread per country. The product atlas "
              "gave lances the identical row to pikes, both from 'iron_weapons'.",
         source="Wikipedia, Lance; Spear (couched lance technique)"),

    # ---------------------------------------------------------------- protection
    #
    # Three armour rows disagree and this is the reconciliation. "Metal armour" (product `armour`)
    # says -2000 in West Asia; `mail_armour` says -116 there; `plate_armour` says 1400 and only
    # four areas. Copper and bronze plate is genuinely old in West Asia, but mail is not, and the
    # mod would otherwise dress a Sumerian of 2000 BC in a mail shirt.
    dict(id="shield", arm=None, name="the shield", role="protection", use="wear",
         tech=None, product="shields", material="wood_hide",
         years={"EUR": -5000, "EEU": -5000, "WAS": -5000, "NAF": -5000, "CAS": -5000,
                "SAS": -5000, "EAS": -5000, "SEA": -5000, "WAF": -3000, "MSA": -3000,
                "EAF": -3000, "NNA": -3000, "MNA": -3000, "CAC": -3000, "SAM": -3000,
                "PAC": -1000, "AUS": -10000},
         never={}, supersedes=[], vanilla="minecraft:shield", mark="recorded",
         endTech="rifle",
         note="Hide and wood, so it does not wait on metal. **Australia had them** - the "
              "parrying shield and the broad shield - and the product atlas had AUS at 1800 "
              "because it derived shields from 'leather'. Tasmania is the exception: Tasmanian "
              "Aboriginal people used neither shields nor boomerangs nor woomeras.",
         source="Wikipedia, Shield; Australian Aboriginal warfare"),

    dict(id="helmet", arm=None, name="the helmet", role="protection", use="wear",
         tech=None, product="helmets", material="bronze",
         years=None,   # the product atlas derives this from bronze_weapons, which is right
         never={"PAC": "no metal working in Oceania",
                "AUS": "no metal working at all in pre-contact Australia"},
         supersedes=[],
         vanilla="minecraft:iron_helmet", mark="recorded",
         note="The product atlas derives this from bronze_weapons and so has it absent from the "
              "Americas - which is right for a *metal* helmet, though leather, cane and wooden "
              "helmets existed widely. Recorded as a limit rather than filled in.",
         source="Wikipedia, Helmet"),

    dict(id="mail", arm=None, name="mail armour", role="protection", use="wear",
         tech="chain_mail", product="mail_armour", material="iron",
         years=None,   # the tech atlas: 258 countries, first -400
         never={}, supersedes=[], vanilla="minecraft:chainmail_chestplate", mark="recorded",
         endTech="flintlock",
         note="The technology atlas gives this per country from -400, which is right: mail is "
              "Celtic in origin and Roman in adoption. It is not the 'metal armour' of West Asia "
              "in 2000 BC, which is bronze plate. **The two are not the same row and the product "
              "atlas treats them as if they were.**",
         source="Wikipedia, Mail (armour)"),

    dict(id="plate", arm=None, name="plate armour", role="protection", use="wear",
         tech="plate_armour", product="plate_armour", material="steel",
         years=None,   # the tech atlas: 4 areas, EUR 1400, MNA 1519, SAM 1532, EEU 1550
         never={"AUS": "no metal armour in pre-contact Australia",
                "PAC": "no metal working in Oceania"},
         supersedes=["mail"],
         vanilla="minecraft:iron_chestplate", mark="recorded",
         endTech="flintlock",
         note="The best-behaved row in the register: the technology atlas has it in **24 of 258 "
              "countries and 4 of 17 areas**, which is exactly right, and those four happen to "
              "be Europe and the Spanish conquest - which is why Conquistadors met the Aztec in "
              "steel.",
         source="Wikipedia, Plate armour"),

    # ---------------------------------------------------------------- the technology atlas's own
    #
    # These twelve already have per-country arrival years, `needs` and `replaces`. This register
    # adds only what the tech atlas cannot say: which of D10's twelve words it is, what product
    # it joins to, and what vanilla item to fall back on.
    dict(id="chariot", arm="chariot", name="the war chariot", role="mount", use="charge",
         tech="chariot", product="war_chariots", material="wood_horse",
         years=None, supersedes=[], vanilla="minecraft:iron_sword", mark="recorded",
         end={"EUR": 100, "EEU": 100, "WAS": -100, "NAF": -100, "CAS": 100, "SAS": 550,
              "EAS": 500, "SEA": 700},
         never={"WAF": "no war chariots in West Africa - the horse does not survive the tsetse "
                       "belt, and the savannah armies that had horses fought from the saddle",
                "MSA": "no war chariots in Middle Africa - no horses south of the tsetse belt",
                "EAF": "no war chariots in East Africa - no horses south of the tsetse belt",
                "NNA": "no horses in the Americas before the Spanish",
                "MNA": "no horses in the Americas before the Spanish",
                "CAC": "no horses in the Americas before the Spanish",
                "SAM": "no horses in the Americas before the Spanish",
                "PAC": "no horses in Oceania", "AUS": "no horses in Australia"},
         note="Needs the wheel and the horse, and the technology atlas has it in **28 of 258 "
              "countries** - a machine of the Bronze Age palaces that vanished from war within a "
              "thousand years.",
         source="Wikipedia, Chariot"),

    dict(id="crossbow", arm=None, name="the crossbow", role="missile", use="shoot",
         tech="crossbow", product="crossbows", material="wood_steel",
         years=None, supersedes=[], vanilla="minecraft:crossbow", mark="recorded",
         never={"AUS": "no crossbow in pre-contact Australia",
                "PAC": "no crossbow in Polynesia"},
         note="Chinese from about 450 BC, the Song military examination weapon, and the reason "
              "the Pope banned it in 1139 (as far as it went). The tech atlas's diffusion model "
              "propagates it to AUS by 1526, which is an artefact of country-level spread and is "
              "recorded here as never.",
         source="Wikipedia, Crossbow"),

    dict(id="siege_engine", arm="cannon", name="the siege engine", role="siege", use="besiege",
         tech="siege_engines", product="siege_engines", material="wood_rope",
         years=None, supersedes=[], vanilla="minecraft:iron_sword", mark="recorded",
         never={},
         endTech="cannon",
         note="The catapult and the trebuchet, from Assyria and Syracuse. D10's `cannon` arm "
              "covers both, since what a battle band cares about is that the thing throws at "
              "range rather than what it throws.",
         source="Wikipedia, Siege engine"),

    dict(id="cannon", arm="cannon", name="the cannon", role="siege", use="besiege",
         tech="cannon", product="cannons", material="bronze_iron",
         years=None, supersedes=["siege_engine"], vanilla="minecraft:iron_sword", mark="recorded",
         never={},
         note="Babur's fifteen to twenty guns at Panipat in 1526 against an adversary with none. "
              "Supersedes the trebuchet, which the `replaces` chain in the technology atlas does "
              "not itself record.",
         source="Wikipedia, Cannon; First Battle of Panipat"),

    dict(id="arquebus", arm="arquebus", name="the matchlock", role="missile", use="shoot",
         tech="matchlock", product="matchlocks", material="iron_wood",
         years=None, supersedes=["crossbow"], vanilla="minecraft:crossbow", mark="recorded",
         never={},
         note="**The one the research says no mod makes.** It was India's main gun for two "
              "centuries, from the arquebuses a Portuguese writer saw in Gujarat and the Bahmani "
              "kingdom in 1515-18 through Babur's matchlocks at Panipat in 1526 to the Maratha "
              "army of 1650-1818. The product atlas has SAS at 1510 and EAS at 1543, both of "
              "them right. Until a mod supplies one, a musket stands in under a local name.",
         source="Wikipedia, Matchlock; First Battle of Panipat; Maratha Army"),

    dict(id="musket", arm="musket", name="the flintlock musket", role="missile", use="shoot",
         tech="flintlock", product="flintlocks", material="iron_wood",
         years=None, supersedes=["arquebus"], vanilla="minecraft:crossbow", mark="recorded",
         never={},
         note="Marin le Bourgeoys, about 1610. The technology atlas records that it **replaces "
              "the matchlock** - the one obsolescence chain anywhere in the mod.",
         source="Wikipedia, Flintlock"),

    dict(id="rifle", arm="rifle", name="the rifle", role="missile", use="shoot",
         tech="rifle", product="rifles", material="steel",
         years=None, supersedes=["musket", "arquebus"], vanilla="minecraft:crossbow",
         mark="recorded", never={},
         note="The Dreyse needle gun, 1841. Replaces both the flintlock and the matchlock in the "
              "technology atlas's chain. D10 already knows this band kills **fewer** than the "
              "musket band, which is the counter-intuitive part and is why it is here.",
         source="Wikipedia, Dreyse needle gun"),

    dict(id="machine_gun", arm="rifle", name="the machine gun", role="missile", use="shoot",
         tech="machine_gun", product="machine_guns", material="steel",
         years=None, supersedes=[], vanilla="minecraft:crossbow", mark="recorded", never={},
         note="Maxim, 1884. D10's bands stop at the rifle, so this shares the rifle's arm.",
         source="Wikipedia, Maxim gun"),

    dict(id="elephant", arm="elephant", name="the war elephant", role="mount", use="charge",
         tech=None, product=None, material="animal",
         years={"EUR": -280, "EEU": -280, "WAS": -1100, "NAF": -300, "CAS": -300, "SAS": -1100,
                "EAS": 800, "SEA": 800, "WAF": None, "MSA": None, "EAF": None,
                "NNA": None, "MNA": None, "CAC": None, "SAM": None, "PAC": None, "AUS": None},
         # step 40's own war_elephant formation is -1000 to 1800 and boxed to South Asia, and
         # this row takes its end from that rather than inventing one
         end={"SAS": 1800, "EAS": 1000, "SEA": 1400, "WAS": 300, "NAF": 300, "EUR": -100,
              "EEU": -100, "CAS": 1000},
         never={"NNA": "no elephants", "MNA": "no elephants", "CAC": "no elephants",
                "SAM": "no elephants", "PAC": "no elephants", "AUS": "no elephants",
                "WAF": "the forest elephant was not trained for war, unlike the Indian",
                "MSA": "no war elephants in Middle Africa",
                "EAF": "no war elephants in East Africa"},
         supersedes=[],
         vanilla="minecraft:iron_sword", mark="recorded",
         note="**The one arm D10 names that no product covers**, because it is an animal and not "
              "a made thing. Indian from about 1100 BC and used by every power from the "
              "Achaemenids to the Mughals; African forest elephants were not so used. Step 40 "
              "already ships a war_elephant formation boxed to South Asia, -1000 to 1800.",
         source="Wikipedia, War elephant"),

    dict(id="horsebow", arm="horsebow", name="the mounted bow", role="missile", use="shoot",
         tech="stirrup", product="bows", material="wood_sinew",
         years={"EUR": 400, "EEU": 550, "WAS": -800, "NAF": -600, "CAS": -800, "SAS": -500,
                "EAS": -300, "SEA": 900, "WAF": 1000, "MSA": 1200, "EAF": 1400,
                "NNA": 1750, "MNA": None, "CAC": None, "SAM": None, "PAC": None, "AUS": None},
         never={"MNA": "no horses in the Americas before the Spanish brought them, so no "
                       "mounted archery of any kind",
                "CAC": "no horses in the Americas before the Spanish brought them",
                "SAM": "no horses in the Americas before the Spanish brought them",
                "PAC": "no horses anywhere in Oceania before European contact",
                "AUS": "no horses, and no bow either - the continent had neither half of it"},
         supersedes=[],
         vanilla="minecraft:bow", mark="recorded",
         endTech="rifle",
         note="The composite bow from horseback: the Scythian, the Parthian shot, the Mongol. "
              "Dated from the stirrup where the stirrup matters and from the horse where the "
              "horse does. Step 40 ships mongol_horsebow at 1206-1400.",
         source="Wikipedia, Mounted archery; Stirrup"),

    dict(id="tank", arm="rifle", name="the tank", role="mount", use="charge",
         tech="tank", product="tanks", material="steel",
         years=None, supersedes=[], vanilla="minecraft:iron_sword", mark="recorded", never={},
         note="1916, and the technology atlas has it needing the car. Step 46 owns vehicles; "
              "this row exists so that the armoury does not stop in 1884.",
         source="Wikipedia, Tank"),
]


# Which D10 arm word each kind answers to, for the join to formations and casualty bands.
D10_ARMS = ["arquebus", "bow", "cannon", "chariot", "elephant", "horsebow", "javelin",
            "musket", "pike", "rifle", "spear", "sword"]

ROLES = ["melee", "missile", "mount", "siege", "protection"]
MARKS = ["recorded", "measured", "estimated"]


def problems():
    """Checks, so a bad row cannot ship silently."""
    out = []
    seen = set()

    # every D10 arm must be spoken by some kind, or step 40 and step 45 do not join
    spoken = {k["arm"] for k in ARMORY if k["arm"]}
    for a in D10_ARMS:
        if a not in spoken:
            out.append("D10 arm '%s' is named by no kind: the two registers will not join" % a)

    for k in ARMORY:
        i = k["id"]
        if i in seen:
            out.append("%s: two rows with this id" % i)
        seen.add(i)

        if k["arm"] is not None and k["arm"] not in D10_ARMS:
            out.append("%s: arm '%s' is not one of D10's twelve" % (i, k["arm"]))
        if k["role"] not in ROLES:
            out.append("%s: unknown role '%s'" % (i, k["role"]))
        if k["mark"] not in MARKS:
            out.append("%s: unknown mark '%s'" % (i, k["mark"]))
        if not k.get("note"):
            out.append("%s: no note" % i)
        if not k.get("source"):
            out.append("%s: no source" % i)
        if not k.get("vanilla"):
            out.append("%s: no vanilla item to fall back on" % i)

        # a hand-written year table must cover all seventeen areas
        if k["years"] is not None:
            missing = [a for a in AREAS if a not in k["years"]]
            if missing:
                out.append("%s: hand-written years missing %s" % (i, missing))
            extra = [a for a in k["years"] if a not in AREAS]
            if extra:
                out.append("%s: unknown area %s" % (i, extra))

        # an area may not be both dated and recorded as never
        if k["years"] and k.get("never"):
            both = [a for a in k["never"] if k["years"].get(a) is not None]
            if both:
                out.append("%s: dated and also recorded as never in %s" % (i, both))

        # every recorded absence must say why
        for a, why in (k.get("never") or {}).items():
            if a not in AREAS:
                out.append("%s: unknown area '%s' in never" % (i, a))
            if not why or len(why) < 10:
                out.append("%s: absence in %s has no reason" % (i, a))

        # a kind that supersedes another must name one that exists
        for s in (k.get("supersedes") or []):
            if s not in seen and s not in {x["id"] for x in ARMORY}:
                out.append("%s: supersedes '%s', which is not a kind" % (i, s))

    return out


if __name__ == "__main__":
    from collections import Counter
    ps = problems()
    print("armory: %d kinds" % len(ARMORY))
    print("  by role:", dict(Counter(k["role"] for k in ARMORY)))
    print("  by mark:", dict(Counter(k["mark"] for k in ARMORY)))
    print("  hand-dated:", sum(1 for k in ARMORY if k["years"] is not None),
          " from the atlases:", sum(1 for k in ARMORY if k["years"] is None))
    print("  with a tech row:", sum(1 for k in ARMORY if k["tech"]),
          " with a product row:", sum(1 for k in ARMORY if k["product"]))
    print("  recorded absences:", sum(len(k.get("never") or {}) for k in ARMORY))
    for a in D10_ARMS:
        ks = [k["id"] for k in ARMORY if k["arm"] == a]
        print("   %-9s <- %s" % (a, ", ".join(ks) if ks else "NOTHING"))
    for p in ps:
        print("  PROBLEM " + p)
    print("armory_table: %d problem(s)" % len(ps))
