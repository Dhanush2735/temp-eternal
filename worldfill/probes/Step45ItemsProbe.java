/* Step 45 part 5: the item resolver (A13).
   Part 4's lesson: a probe that checks by id passes while whole PLACES read wrong. So every
   assertion here that names a place asserts it at that place. */
import com.eternalengine.war.WeaponItems;
import com.eternalengine.war.Armoury;
import java.util.Set;
import java.util.List;

public class Step45ItemsProbe {
    static int checks = 0, failed = 0;

    static void ok(boolean c, String what) {
        checks++;
        if (!c) { failed++; System.out.println("  FAIL " + what); }
    }
    static void eq(Object a, Object b, String what) {
        checks++;
        if (a == null ? b != null : !a.equals(b)) {
            failed++;
            System.out.println("  FAIL " + what + "  expected=" + b + " actual=" + a);
        }
    }

    static final Set<String> NONE = Set.of();
    static final Set<String> SPARTAN = Set.of("spartanweaponry");
    static final Set<String> MUSKET  = Set.of("musketmod", "cloth_config");
    static final Set<String> MUSKET_BROKEN = Set.of("musketmod");
    static final Set<String> EK_ANTIQUE_BROKEN = Set.of("epic_knights_antique", "architectury", "cloth_config");
    static final Set<String> ALL = Set.of("spartanweaponry", "musketmod", "cloth_config",
            "epicknights", "architectury", "epic_knights_antique", "ageofweapons", "tacz",
            "scorched_guns", "geckolib", "curios", "vic_point_blank",
            "chinese_ancient_blade", "playeranimator");

    public static void main(String[] args) {
        WeaponItems W = WeaponItems.get();
        System.out.println("== " + W + " ==");

        ok(W.hasData(), "the resolver has data");
        eq(W.problem(), null, "the resolver reports no problem");
        ok(W.mods().size() >= 5, "at least five weapon mods are named (" + W.mods().size() + ")");

        // 1. THERE ARE NO WEAPONS TO FIND, AND EVERY KIND STILL RESOLVES.
        //    A13's rule: with no weapon mod installed, everything falls back to vanilla.
        for (Armoury.Kind k : Armoury.get().kinds()) {
            WeaponItems.Resolution r = W.resolve(k.id(), "EUR", 1600, NONE);
            ok(r != null, "no mods: " + k.id() + " still resolves (vanilla fallback)");
            if (r != null) {
                ok(r.isVanilla(), "no mods: " + k.id() + " falls back to vanilla");
                ok(!r.isTag(), "no mods: " + k.id() + " vanilla fallback is an item, not a tag");
                eq(r.mark(), "vanilla", "no mods: " + k.id() + " is marked vanilla");
                eq(r.id(), k.vanilla(), "no mods: " + k.id() + " uses the armoury's own vanilla item");
            }
        }

        // 2. EVERY SINGLE MOD ON ITS OWN: no kind may ever resolve to null.
        String[] modIds = {"spartanweaponry", "musketmod", "epicknights", "epic_knights_antique",
                           "ageofweapons", "tacz", "scorched_guns", "vic_point_blank",
                           "chinese_ancient_blade"};
        for (String m : modIds) {
            WeaponItems.Mod mod = W.mods().stream().filter(x -> x.id().equals(m)).findFirst()
                    .orElse(null);
            ok(mod != null, "mod " + m + " is in the table");
            if (mod == null) continue;
            Set<String> loaded = new java.util.HashSet<>(mod.needs());
            loaded.add(m);
            for (Armoury.Kind k : Armoury.get().kinds()) {
                WeaponItems.Resolution r = W.resolve(k.id(), "EUR", 1600, loaded);
                ok(r != null, "alone/" + m + ": " + k.id() + " resolves without crashing");
            }
        }

        // 3. A TAG BEATS AN ID. Spartan Weaponry renamed its registry between 1.16.5 and 1.19.2
        //    and broke datapacks that hard-coded ids; a tag survives that.
        WeaponItems.Resolution spear = W.resolve("spear", "SEA", 1600, SPARTAN);
        ok(spear != null, "spartan: spear resolves");
        if (spear != null) {
            ok(spear.isTag(), "spartan: spear prefers the item tag over an item id");
            eq(spear.id(), "#spartanweaponry:spears", "spartan: spear tag");
            eq(spear.mod(), "spartanweaponry", "spartan: spear names its mod");
        }
        WeaponItems.Resolution sword = W.resolve("sword", "SEA", 1400, SPARTAN);
        ok(sword != null && sword.isTag(), "spartan: sword also comes as a tag");

        // 4. A RECORDED ID IS WHERE AN ID IS SAFE. Musket Mod's four ids come from its own source.
        WeaponItems.Resolution musket = W.resolve("musket", "EUR", 1700, MUSKET);
        ok(musket != null, "musketmod: musket resolves");
        if (musket != null) {
            eq(musket.id(), "musketmod:musket", "musketmod: musket item id");
            eq(musket.mark(), "recorded", "musketmod: musket is marked recorded");
            ok(!musket.isTag(), "musketmod: musket is an item id, not a tag");
        }
        // Musket Mod is the ONLY mod whose ids are read from its own source rather than guessed,
        // so every one of its five rows is marked recorded. The armoury has 24 kinds and a pistol
        // is not one of them, so the pistol and the blunderbuss are filed under musket - same
        // period, same lock - rather than part 5 inventing a kind.
        boolean pistol = false, blunderbuss = false, bayonet = false, plain = false;
        for (WeaponItems.Entry e : W.entries()) {
            if (!"musketmod".equals(e.mod())) continue;
            if ("musketmod:pistol".equals(e.item())) pistol = true;
            if ("musketmod:blunderbuss".equals(e.item())) blunderbuss = true;
            if ("musketmod:musket_with_bayonet".equals(e.item())) bayonet = true;
            if ("musketmod:musket".equals(e.item())) plain = true;
        }
        ok(plain, "musketmod: musket is in the table");
        ok(pistol, "musketmod: pistol is in the table");
        ok(blunderbuss, "musketmod: blunderbuss is in the table");
        ok(bayonet, "musketmod: musket with bayonet is in the table");
        eq(W.entries().stream().filter(e -> "musketmod".equals(e.mod())
                && "recorded".equals(e.mark())).count(), 5L,
                "all five musketmod rows are recorded, not guessed at");
        eq(W.ammoFor("musketmod", "musket"), "musketmod:cartridge", "musketmod ammunition");

        // 5. THE `needs` CHAIN IS A CHAIN, NOT A LIST. A mod whose dependency is missing is not
        //    usable, and must fall back rather than hand back an item that does not exist.
        WeaponItems.Resolution broken = W.resolve("musket", "EUR", 1700, MUSKET_BROKEN);
        ok(broken != null && broken.isVanilla(),
                "musketmod WITHOUT cloth_config is unusable, so musket falls back to vanilla");
        WeaponItems.Resolution broken2 = W.resolve("club", "EUR", -300, EK_ANTIQUE_BROKEN);
        ok(broken2 != null && broken2.isVanilla(),
                "antique legacy WITHOUT epicknights falls back to vanilla");
        ok(!W.mods().stream().filter(m -> m.id().equals("musketmod")).findFirst().get()
                .usableIn(MUSKET_BROKEN), "Mod.usableIn() sees the missing dependency");
        ok(W.mods().stream().filter(m -> m.id().equals("musketmod")).findFirst().get()
                .usableIn(MUSKET), "Mod.usableIn() accepts a complete mod");

        // 6. PLACES. The same kind in the same year is called different things by different
        //    peoples - this is the whole answer to "no Indian weapons exist for Java 1.20.1".
        // South Asia is the region with NO weapon mod at all, so the name is all it has.
        eq(W.localName("sword", "SAS"), "talwar", "1650 Agra calls its sword a talwar");
        eq(W.localName("dagger", "SAS"), "katar", "a katar is a dagger");
        eq(W.localName("shield", "SAS"), "dhal", "a dhal is a shield");
        eq(W.localName("mail", "SAS"), "zirah", "mail is zirah");
        eq(W.localName("musket", "SAS"), "toradar", "the matchlock gap is closed by a name");
        eq(W.localName("arquebus", "SAS"), "toradar", "and so is the arquebus, being the same gun");
        eq(W.localName("club", "SAS"), "gurj", "a gurj is a mace");
        eq(W.localName("sword", "EAS"), "dao", "China calls its sword a dao");
        eq(W.localName("bow", "EAS"), "gong", "and its bow a gong");
        eq(W.localName("sword", "SEA"), "kampilan", "the archipelago calls it a kampilan");
        eq(W.localName("sword", "WAF"), "takouba", "the Sahel calls its sword a takouba");
        eq(W.localName("club", "MNA"), "macuahuitl", "Mesoamerica's club is the macuahuitl");
        eq(W.localName("musket", "EAS"), null, "East Asia has no recorded local name for a musket");
        eq(W.localName("sword", "AUS"), null, "Australia has no recorded local name for a sword");
        eq(W.localName("nonsense", "SAS"), null, "an unknown kind has no local name");
        eq(W.localName("sword", "NOWHERE"), null, "an unknown area has no local name");

        // The local name must ride along on a REAL resolution, at a place, not just in the table.
        WeaponItems.Resolution agra = W.resolve("sword", "SAS", 1650, NONE);
        ok(agra != null && "talwar".equals(agra.name()),
                "in South Asia in 1650 the vanilla iron sword is CALLED a talwar");
        WeaponItems.Resolution edo = W.resolve("sword", "EAS", 1600, NONE);
        ok(edo != null && "dao".equals(edo.name()),
                "in East Asia in 1600 the vanilla iron sword is CALLED a dao");
        WeaponItems.Resolution plains = W.resolve("sword", "NNA", 1750, NONE);
        ok(plains != null && plains.name() == null,
                "on the northern plains the sword carries no borrowed name");
        WeaponItems.Resolution sydney = W.resolve("spear", "AUS", 1750, NONE);
        ok(sydney != null && "woomera".equals(sydney.name()),
                "in Australia the spear is a woomera");
        ok(W.resolve("sword", "SAS", 1650, NONE).id()
                .equals(W.resolve("sword", "EAS", 1600, NONE).id()),
                "the two places fall back to the same item and differ only in name");

        // 7. GUESSING. A wrong guess is visible and fixable; a missing weapon is not.
        eq(W.guessKind("spartanweaponry:steel_halberd"), "pike", "a halberd guesses to pike");
        eq(W.guessKind("spartanweaponry:iron_greatsword"), "sword",
                "greatsword guesses to sword, and NOT by swallowing the word 'sword' first");
        eq(W.guessKind("musketmod:musket"), "musket", "a musket guesses to musket");
        eq(W.guessKind("tacz:ak47"), "rifle", "an unfamiliar gun still guesses to rifle");
        eq(W.guessKind("mysterymod:khanda"), "sword", "an Indian sword from an unlisted mod");
        eq(W.guessKind("mysterymod:katar"), "dagger", "a katar from an unlisted mod");
        eq(W.guessKind("mysterymod:toradar"), "musket", "a toradar from an unlisted mod");
        eq(W.guessKind("mysterymod:macuahuitl"), "club", "a macuahuitl from an unlisted mod");
        eq(W.guessKind("mysterymod:atlatl"), "spear", "an atlatl is filed as a spear");
        eq(W.guessKind("mysterymod:toradar"), "musket", "a toradar guesses to musket");
        eq(W.guessKind("mysterymod:zzzzz"), null, "an unguessable item guesses to nothing");
        eq(W.guessKind(null), null, "a null item guesses to nothing");
        eq(W.guessKind(""), null, "an empty item guesses to nothing");
        eq(W.guessKind("mysterymod:BOW"), "bow", "guessing is case-insensitive");

        // A guess must lead somewhere: the guessed kind must resolve.
        String guessed = W.guessKind("mysterymod:khanda");
        ok(guessed != null && W.resolve(guessed, "SAS", 1650, NONE) != null,
                "a guessed kind resolves to a real item");
        // And a guess that lands on the right kind lands on the right NAME, which is the point:
        // an unlisted mod's talwar is still called a talwar in South Asia.
        ok("talwar".equals(W.localName(W.guessKind("mysterymod:talwar"), "SAS")),
                "a guessed talwar is still called a talwar");

        // 8. /ee check: what is falling back, and what is installed.
        List<String> noMods = W.fallingBackToVanilla(NONE);
        eq(noMods.size(), Armoury.get().kinds().size(),
                "with no mods, every kind reports as falling back to vanilla");
        List<String> allMods = W.fallingBackToVanilla(ALL);
        ok(allMods.size() < noMods.size(),
                "with every mod loaded, fewer kinds fall back (" + allMods.size() + " of "
                + noMods.size() + ")");
        ok(W.modSummary(NONE).contains("no weapon mods"), "modSummary says so when none are on");
        ok(W.modSummary(SPARTAN).contains("Spartan"), "modSummary names the mod that is on");

        // 9. THE VANILLA LIST IS NOT DUPLICATED. Part A owns it; this pack must read it.
        boolean dup = false;
        for (WeaponItems.Entry e : W.entries()) {
            if (e.item() != null && "minecraft".equals(e.item().split(":")[0])) dup = true;
        }
        ok(!dup, "no entry in the pack re-states a vanilla item - the armoury owns that list");

        System.out.println("== step 45 items: " + checks + " checks, " + failed + " failed ==");
        if (failed > 0) System.exit(1);
    }
}
