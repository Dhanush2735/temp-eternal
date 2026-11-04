"""
Step 45 part 5 (A13): the item resolver — what goes in a soldier's hand.

**The standing instruction this part exists to obey: weapons defer to other mods.** The mod ships
no weapons of its own. A13's job is to answer "which item is the sword here, in 1650, in Agra?" by
looking at what the player has installed, and to fall back to vanilla when they have nothing.

Three decisions that shape everything below:

**1. Item tags, not item ids, wherever the mod publishes one.** Spartan Weaponry's own wiki warns
that *"ObliviousSpartan changed the registry names for Spartan Weaponry since 1.16.5"*, and a
datapack author had to walk every weapon to fix them. A tag like `spartanweaponry:spears` survives
that; a hard-coded `spartanweaponry:spear_iron` does not. So a tag is preferred, an explicit id is
used only where it is recorded, and both are marked with which they are.

**2. An unknown item is guessed from its name, and the guess is logged.** No register can list
every item of every weapon mod, and nine candidate mods were found for 1.20.1 alone. So the
resolver reads an item id like `spartanweaponry:steel_halberd` and takes it apart: `halberd` is a
pike, `steel` is the material. A wrong guess is visible and fixable; a missing weapon is not.

**3. A missing weapon is never an error.** With no weapon mod installed, every kind falls back to
the vanilla item the armoury already names — part A put a `vanilla` field on all 24 kinds, so this
part does not duplicate that list, it reads it. **Nothing in this part is required for the mod to
work.** That is A13's rule: optional links, and everything also works without them.

**And the fallback is not only for missing mods.** No Indian weapons exist for Java 1.20.1 — the
research found only a Bedrock add-on (talwar, pata, tabar) that cannot be used. So a talwar in 1650
Agra is a Spartan Weaponry saber *carrying the name* talwar. The local name is the honest fix for a
gap no mod fills, and it is cheaper and truer than waiting for someone to model one.
"""

# --------------------------------------------------------------------------- the mods
#
# Checked on Modrinth for 1.20.1 + Forge (see WEAPONS_RESEARCH.md section 5).
#
#   id       the modid, which is what ModList.get().isLoaded() is asked
#   kinds    what it can supply, by the armoury's kind ids
#   needs    other mods it requires, checked before its items are offered
#   licence  what it ships under
#
# `mark` on each entry below: "recorded" when the id or tag is written in the mod's own
# documentation or source; "estimated" when it follows the mod's naming pattern and is not
# confirmed.

MODS = [
    dict(id="spartanweaponry", name="Spartan Weaponry", licence="Apache-2.0", needs=[],
         kinds=["dagger", "sword", "spear", "pike", "lance", "javelin", "bow", "crossbow",
                "club", "shield"],
         note="The broadest melee mod and the most popular (61 M downloads). One weapon type in "
              "every material tier. **Its item tags are what this register uses**, because its "
              "own wiki records that the registry names changed between 1.16.5 and 1.19.2 and "
              "broke datapacks that had hard-coded them.",
         source="WEAPONS_RESEARCH.md [S1]; SpartanWeaponry GitHub wiki, Item Tags"),
    dict(id="musketmod", name="ewewukek's Musket Mod", licence="MIT", needs=["cloth_config"],
         kinds=["musket", "arquebus"],
         note="**The only set of item ids in this register taken straight from the mod's source** "
              "(mc-musketmod Items.java: MUSKET, MUSKET_WITH_BAYONET, PISTOL, CARTRIDGE, plus "
              "the later BLUNDERBUSS and SCOPED_MUSKET). Switch off its option to arm skeletons "
              "and pillagers, or the mod's own year rules are broken by mobs carrying guns.",
         source="WEAPONS_RESEARCH.md [M1]; github.com/ewewukek/mc-musketmod, Items.java"),
    dict(id="epicknights", name="Epic Knights", licence="all rights reserved",
         needs=["architectury", "cloth_config"],
         kinds=["sword", "helmet", "mail", "plate", "shield"],
         note="Medieval armour, weapons and heraldry, and it adds **steel** as a material. Needs "
              "Architectury and Cloth Config.",
         source="WEAPONS_RESEARCH.md [K1]"),
    dict(id="epic_knights_antique", name="Epic Knights: Antique Legacy",
         licence="all rights reserved", needs=["epicknights"],
         kinds=["sword", "spear", "helmet", "mail", "shield"],
         note="Antiquity: 20 weapons, 71 armour pieces, 5 shields. **Bronze is made from copper "
              "plus tin, and tin needs yet another mod** — so its bronze tier is unreachable "
              "without one.",
         source="WEAPONS_RESEARCH.md"),
    dict(id="ageofweapons", name="Age of Weapons - Reforged", licence="MIT", needs=[],
         kinds=["club", "spear", "sword", "bow", "rifle"],
         note="Stone age, antiquity, middle ages, **Edo Japan**, pirate age and modern — the only "
              "candidate that covers the stone age and Japan in one mod. It also ships 'future' "
              "and 'legendary' fantasy items, which must be locked away rather than handed to a "
              "soldier in 1650.",
         source="WEAPONS_RESEARCH.md [AW]"),
    dict(id="tacz", name="TaCZ", licence="GPL-3.0", needs=[],
         kinds=["rifle", "machine_gun"],
         note="1870s to the present, with guns defined in JSON data files, so the ids come from "
              "whatever gun packs are installed. Made at its own gun table.",
         source="WEAPONS_RESEARCH.md [T1]"),
    dict(id="scorched_guns", name="Scorched Guns 2: Flintlocks", licence="GPL-3.0+",
         needs=["geckolib", "curios"],
         kinds=["arquebus", "musket"],
         note="Hand cannon, flintlock, musket and blunderbuss — **the closest thing to a "
              "matchlock**, which no mod supplies. An early version; made at its own Gun Bench.",
         source="WEAPONS_RESEARCH.md"),
    dict(id="vic_point_blank", name="Vic's Point Blank", licence="all rights reserved", needs=[],
         kinds=["rifle", "machine_gun"],
         note="An alternative to TaCZ for modern guns.",
         source="WEAPONS_RESEARCH.md"),
    dict(id="chinese_ancient_blade", name="Chinese Ancient Blade", licence="ISC",
         needs=["playeranimator", "geckolib"],
         kinds=["sword"],
         note="Tang *hengdao*, ring-pommel *dao*, *yanling dao*, *miao dao*. Optional, and it "
              "needs two animation libraries.",
         source="WEAPONS_RESEARCH.md"),
]

# --------------------------------------------------------------------------- what each mod supplies
#
#   mod    the modid
#   kind   the armoury kind
#   tag    an item tag, preferred, written as "#namespace:path"
#   item   an explicit item id, used only when no tag is published
#   mark   recorded | estimated
#   note   anything a reader needs

ENTRIES = [
    # Spartan Weaponry: tags, because the registry names have moved before.
    dict(mod="spartanweaponry", kind="spear", tag="#spartanweaponry:spears", item=None,
         mark="recorded", note="The tag is written in the mod's own wiki."),
    dict(mod="spartanweaponry", kind="sword", tag="#spartanweaponry:greatswords", item=None,
         mark="recorded", note="Documented tag. Spartan splits swords across longswords, "
                               "greatswords, katanas, sabers and rapiers; the greatsword is the "
                               "general-purpose pick."),
    dict(mod="spartanweaponry", kind="dagger", tag="#spartanweaponry:daggers", item=None,
         mark="estimated", note="Follows the mod's tag pattern; the wiki lists greatswords, "
                                "spears, battleaxes and iron_weapons explicitly."),
    dict(mod="spartanweaponry", kind="bow", tag=None, item="spartanweaponry:longbow",
         mark="estimated", note="The mod calls its bow a longbow; id estimated."),
    dict(mod="spartanweaponry", kind="crossbow", tag=None,
         item="spartanweaponry:heavy_crossbow", mark="estimated",
         note="The mod calls its crossbow a heavy crossbow; id estimated."),
    dict(mod="spartanweaponry", kind="pike", tag=None, item="spartanweaponry:pike_iron",
         mark="estimated", note="Weapon ids follow <weapon>_<material>; iron is the mid tier."),
    dict(mod="spartanweaponry", kind="lance", tag=None, item="spartanweaponry:lance_iron",
         mark="estimated", note="Weapon ids follow <weapon>_<material>."),
    dict(mod="spartanweaponry", kind="javelin", tag=None, item="spartanweaponry:javelin_iron",
         mark="estimated", note="Weapon ids follow <weapon>_<material>."),
    dict(mod="spartanweaponry", kind="club", tag=None, item="spartanweaponry:club_wood",
         mark="estimated", note="Also a warhammer and a battle hammer; the club is the plainest."),

    # Musket Mod: ids taken from the source.
    dict(mod="musketmod", kind="musket", tag=None, item="musketmod:musket", mark="recorded",
         note="Named in mc-musketmod Items.java."),
    dict(mod="musketmod", kind="arquebus", tag=None, item="musketmod:musket", mark="recorded",
         note="No arquebus exists in any mod; the musket stands in under a local name. India's "
              "gun from the 1500s to the 1700s was the matchlock, and it too has no mod."),
    dict(mod="musketmod", kind="musket", tag=None, item="musketmod:pistol", mark="recorded",
         note="Filed under musket because the armoury has no sidearm kind and part 5 does not "
              "invent one: a flintlock pistol is the same weapon - same period, same lock, one "
              "hand instead of two. Damage 12, and it is the one gun that can be fired one-handed."),
    dict(mod="musketmod", kind="musket", tag=None, item="musketmod:musket_with_bayonet",
         mark="recorded", note="Named in mc-musketmod Items.java."),
    dict(mod="musketmod", kind="musket", tag=None, item="musketmod:blunderbuss",
         mark="recorded",
         note="Added in later versions. Damage 21 over nine pellets at close range, so it is the "
              "shotgun of the flintlock age; 200 durability against the musket's 250."),


    # Everything else is estimated, and says so.
    dict(mod="epicknights", kind="sword", tag=None, item="epicknights:steel_sword",
         mark="estimated", note="Id follows the mod's material-prefix naming; not confirmed."),
    dict(mod="epicknights", kind="plate", tag=None, item="epicknights:steel_chestplate",
         mark="estimated", note="Id estimated."),
    dict(mod="epicknights", kind="helmet", tag=None, item="epicknights:steel_helmet",
         mark="estimated", note="Id estimated."),
    dict(mod="epic_knights_antique", kind="sword", tag=None, item="epicknights:bronze_sword",
         mark="estimated", note="Id estimated, and unreachable unless another mod supplies tin."),
    dict(mod="tacz", kind="rifle", tag=None, item="tacz:modern_kinetic_gun", mark="estimated",
         note="TaCZ gun ids come from installed gun packs, so no single id is safe. This one is "
              "the mod's own placeholder, and the register expects to be corrected by config."),
    dict(mod="scorched_guns", kind="musket", tag=None, item="scorched_guns:flintlock",
         mark="estimated", note="Id estimated."),
]

# Ammunition, which must obey the same year rules as the weapon that fires it.
AMMO = [
    dict(mod="musketmod", kind="musket", item="musketmod:cartridge", mark="recorded",
         note="The paper cartridge, named in mc-musketmod Items.java."),
    dict(mod="musketmod", kind="arquebus", item="musketmod:cartridge", mark="recorded",
         note="The same cartridge."),
]

# --------------------------------------------------------------------------- guessing an item's kind
#
# An unknown modded weapon is read from its own name and matched to an armoury kind. Longest
# token first, so "greatsword" is not swallowed by "sword".

GUESS = [
    ("machine_gun", ["machinegun", "machine_gun", "lmg", "hmg", "smg", "gatling", "maxim",
                     "pkm", "mg42", "lewis"]),
    ("rifle", ["rifle", "assault_rifle", "musketoon", "carbine", "springfield", "kar98",
           "bolt_action", "ak47", "ak74", "akm", "m16", "ar15", "baker", "jezail"]),
    ("musket", ["musket", "blunderbuss", "matchlock", "wheellock", "toradar"]),
    ("arquebus", ["arquebus", "hand_cannon", "handgonne"]),
    ("crossbow", ["crossbow", "arbalest", "arbalist"]),
    ("bow", ["longbow", "shortbow", "recurve", "composite_bow", "yumi", "bow"]),
    ("pike", ["pike", "halberd", "glaive", "poleaxe", "pollaxe", "bill", "naginata", "guandao"]),
    ("lance", ["lance", "contus", "xyston"]),
    ("spear", ["spear", "dory", "hasta", "yari", "qiang", "assegai", "iklwa", "barchha",
               "sibat", "chuqui", "tao", "atlatl", "woomera"]),
    ("javelin", ["javelin", "pilum", "throwing_spear"]),
    ("sword", ["greatsword", "longsword", "broadsword", "shortsword", "arming_sword", "falchion",
               "messer", "saber", "sabre", "scimitar", "shamshir", "katana", "tachi", "dao",
               "jian", "rapier", "estoc", "kilij", "shashka", "kaskara", "takouba", "shotel",
               "hanger", "khanda", "talwar", "tulwar", "firangi", "kora", "kirpan",
               "urumi", "kampilan", "sword"]),
    ("dagger", ["dagger", "dirk", "kris", "keris", "katar", "khanjar", "jambiya", "seax",
                "scramasax", "tanto", "pata", "stiletto", "knuckle", "cestus", "kindjal"]),
    ("club", ["warhammer", "battle_hammer", "mace", "flail", "club", "cudgel", "quarterstaff",
              "bo", "nulla", "mere", "patu", "macuahuitl", "macana", "tomahawk"]),
    ("shield", ["shield", "buckler", "pavise", "dhal", "turs", "sipar"]),
    ("helmet", ["helmet", "helm", "sallet", "bascinet", "great_helm", "kettle_hat", "nasal_helm",
                "khula"]),
    ("plate", ["plate", "cuirass", "chestplate", "char_aina", "lorica"]),
    ("mail", ["mail", "chainmail", "hauberk", "byrnie", "zirah", "lorica_hamata"]),
    ("cannon", ["cannon", "culverin", "bombard", "falconet"]),
    ("siege_engine", ["trebuchet", "catapult", "ballista", "onager", "mangonel"]),
]

# --------------------------------------------------------------------------- local names
#
# The same item, named as the people who carried it would have named it. This is the fix the
# research proposes for the gap no mod fills: no Indian weapons exist for Java 1.20.1, so a
# Spartan saber sold in Agra in 1650 is called a talwar and not a saber.
#
#   area -> kind -> (name, note)

LOCAL_NAMES = {
    "SAS": {
        "sword": ("talwar", "The north Indian sabre, with a disc hilt and a curved blade."),
        "dagger": ("katar", "The punching dagger, held in a fist by two bars across the back of "
                            "the hand and driven forward rather than swung."),
        "spear": ("barchha", "The Indian spear; also *nezabaz*, the javelin of the Mughal horse."),
        "shield": ("dhal", "The round hide shield, usually of buffalo or rhinoceros hide with "
                           "four brass bosses."),
        "helmet": ("khula khud", "The Mughal skull-cap helmet with a sliding nose-guard and a "
                                 "mail curtain."),
        "mail": ("zirah", "The mail shirt."),
        "plate": ("char-aina", "The 'four mirrors': four plates, two over the chest and back and "
                               "two at the sides, buckled together over the mail."),
        "musket": ("toradar", "The Indian matchlock, the country's gun from the 1500s to the "
                              "1700s. **No mod makes one**, so a musket stands in under this "
                              "name."),
        "arquebus": ("toradar", "The same word covers both."),
        "bow": ("kaman", "The bow; the Mughal composite bow is the *charkh-kaman*."),
        "club": ("gurj", "The mace; also *bhuj*, the elephant-goad shaped dagger-axe."),
    },
    "EAS": {
        "sword": ("dao", "China's single-edged blade, from the Han dao to the Ming yanling dao. "
                  "Japan's is the katana, and this coarse area cannot say which is meant."),
        "pike": ("guandao", "The 'Green Dragon Crescent Blade' - a heavy polearm with a crescent "
                 "edge, carried by Guan Yu's tradition rather than by his lifetime."),
        "spear": ("qiang", "The Chinese spear, whose head is a leaf and whose shaft is waxed "
                  "bamboo, so it flexes rather than breaks."),
        "bow": ("gong", "The Chinese bow. Japan's is the yumi, and it is the longest of the two."),
    },
    "WAS": {
        "sword": ("saif", "The Arab straight sword; the Persian curved one is the *shamshir*."),
        "dagger": ("khanjar", "The curved dagger; in the Yemen, the *jambiya*."),
        "bow": ("qaws", "The Arab bow."),
        "shield": ("turs", "The round hide shield."),
        "mail": ("zirah", "The mail shirt, the same word as in Persian India."),
    },
    "EUR": {
        "sword": ("arming sword", "The knightly one-handed sword; the German two-hander is the "
                                  "*zweihänder* and the single-edged one the *messer*."),
        "dagger": ("bollock dagger", "Or the *rondel*, the knight's stiff-bladed thrusting knife."),
        "bow": ("longbow", "The English and Welsh war bow; a crossbow is an *arbalest*."),
        "shield": ("kite shield", "The knight's shield before the heater."),
        "helmet": ("great helm", "The pot helm of the crusades; later the *bascinet* and the "
                                 "*sallet*."),
        "mail": ("hauberk", "The mail shirt, to the knee and with a coif."),
        "plate": ("cuirass", "The breast and back plate."),
    },
    "EEU": {
        "sword": ("shashka", "The Cossack sabre, without a guard."),
        "bow": ("composite bow", "The steppe bow, of horn and sinew on a wooden core."),
        "dagger": ("kindjal", "The Caucasian long dagger."),
    },
    "CAS": {
        "sword": ("kilij", "The Turkic sabre with the flared yelman at the point."),
        "bow": ("composite bow", "The steppe bow, the Mongol's own weapon and the one that made "
                                 "the arban work."),
        "dagger": ("khanjar", "The curved dagger."),
    },
    "SEA": {
        "dagger": ("keris", "The wavy-bladed dagger of Java and the Malay world, a heirloom and "
                            "a spirit-object as much as a weapon."),
        "sword": ("kampilan", "The Filipino long sword; also the *barong* and the *golok*."),
        "spear": ("sibat", "The Filipino spear."),
    },
    "WAF": {
        "sword": ("takouba", "The Tuareg and Songhai straight sword; the broad Sudanese one is "
                             "the *kaskara*."),
        "spear": ("assegai", "The throwing spear."),
        "shield": ("dhal", "The hide shield."),
    },
    "MSA": {
        "spear": ("assegai", "The spear generally; the Zulu short stabbing spear Shaka made "
                             "standard is the *iklwa*, named for the sound it made coming out."),
        "club": ("knobkerrie", "The throwing club."),
        "sword": ("takouba", "The Sahelian sword."),
    },
    "EAF": {
        "sword": ("shotel", "The Ethiopian curved sword, hooked so as to reach round a shield."),
        "spear": ("assegai", "The throwing spear."),
        "club": ("knobkerrie", "The throwing club."),
    },
    "MNA": {
        "club": ("macuahuitl", "The Aztec club, a wooden paddle edged with obsidian blades; the "
                               "plain club is the *macana*."),
        "spear": ("atlatl", "The spearthrower, which is what makes a spear a weapon at range."),
        "dagger": ("tomahawk", "The Algonquian word for the hatchet."),
    },
    "NNA": {
        "club": ("tomahawk", "The hatchet; the ball-headed club is the *gunstock war club*."),
        "spear": ("atlatl", "The spearthrower."),
    },
    "SAM": {
        "club": ("macuahuitl", "The Aztec obsidian club, carried south."),
        "spear": ("chuqui", "The Inca spear."),
    },
    "AUS": {
        "club": ("nulla-nulla", "The hardwood club; the hooked one is the *leangle*."),
        "spear": ("woomera", "The spearthrower, which is the reason Australia never took up the "
                             "bow - a spear from a woomera carries four times the energy of an "
                             "arrow."),
    },
    "PAC": {
        "club": ("patu", "The Māori short club of stone, wood or whalebone; the long one is the "
                         "*taiaha*."),
        "spear": ("tao", "The Polynesian spear."),
    },
}

# The vanilla fallback is NOT here: part A put a `vanilla` field on all 24 kinds of the armoury,
# and the resolver reads it. A list here would be a second copy to keep in step.


def problems():
    """Checks, so a bad row cannot ship silently."""
    out = []
    modids = [m["id"] for m in MODS]
    if len(modids) != len(set(modids)):
        out.append("duplicate mod ids: %s" % [m for m in modids if modids.count(m) > 1])

    kinds = set()
    import armory_table
    for k in armory_table.ARMORY:
        kinds.add(k["id"])

    for m in MODS:
        if not m.get("kinds"):
            out.append("mod %s supplies nothing" % m["id"])
        for k in m["kinds"]:
            if k not in kinds:
                out.append("mod %s supplies kind '%s', which the armoury does not name"
                           % (m["id"], k))
        for key in ("name", "licence", "note", "source"):
            if not m.get(key):
                out.append("mod %s has no %s" % (m["id"], key))

    for e in ENTRIES:
        i = "%s/%s" % (e["mod"], e["kind"])
        if e["mod"] not in modids:
            out.append("%s: no such mod" % i)
        if e["kind"] not in kinds:
            out.append("%s: no such kind" % i)
        if not e.get("tag") and not e.get("item"):
            out.append("%s: neither a tag nor an item" % i)
        if e.get("tag") and not e["tag"].startswith("#"):
            out.append("%s: tag '%s' does not start with #" % (i, e["tag"]))
        if e.get("mark") not in ("recorded", "estimated"):
            out.append("%s: mark is '%s'" % (i, e.get("mark")))
        if e["mod"] not in [m["id"] for m in MODS]:
            continue
        sup = next(m for m in MODS if m["id"] == e["mod"])
        if e["kind"] not in sup["kinds"]:
            out.append("%s: the mod is not listed as supplying it" % i)

    for a in AMMO:
        if a["mod"] not in modids:
            out.append("ammo: no such mod %s" % a["mod"])

    # The guess table must be unambiguous: one token must not map to two kinds.
    seen = {}
    for kind, toks in GUESS:
        for t in toks:
            if t in seen:
                out.append("guess token '%s' is claimed by both %s and %s" % (t, seen[t], kind))
            seen[t] = kind
        if not toks:
            out.append("guess kind %s has no tokens" % kind)

    for area, bykind in LOCAL_NAMES.items():
        if area not in armory_table.AREAS:
            out.append("local names: '%s' is not an area" % area)
        for k, v in bykind.items():
            if k not in kinds:
                out.append("local names: %s/%s is not a kind" % (area, k))
            if not isinstance(v, tuple) or len(v) != 2 or not v[0]:
                out.append("local names: %s/%s is not (name, note)" % (area, k))
    return out


if __name__ == "__main__":
    ps = problems()
    print("weapon items: %d mods, %d entries, %d ammo, %d guess kinds, %d areas with local names"
          % (len(MODS), len(ENTRIES), len(AMMO), len(GUESS), len(LOCAL_NAMES)))
    for m in MODS:
        rec = sum(1 for e in ENTRIES if e["mod"] == m["id"] and e["mark"] == "recorded")
        est = sum(1 for e in ENTRIES if e["mod"] == m["id"] and e["mark"] == "estimated")
        print("   %-24s %-12s %2d recorded, %2d estimated, needs %s"
              % (m["id"], m["licence"], rec, est, ",".join(m["needs"]) or "nothing"))
    for p in ps:
        print("  PROBLEM " + p)
    print("weapon_items_table: %d problem(s)" % len(ps))
