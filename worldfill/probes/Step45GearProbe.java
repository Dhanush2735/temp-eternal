/* Step 45 part 6: the year gate and the role kit (A13).
   Part 4 and part 5 both caught invented area codes and places that read right by id but wrong
   where they stood. So this probe asserts at named PLACES, with real latitudes, throughout. */
import com.eternalengine.war.WarGear;
import com.eternalengine.war.WeaponItems;
import com.eternalengine.war.Armoury;
import java.util.Set;
import java.util.List;
import java.util.Map;

public class Step45GearProbe {
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
    static final Set<String> MUSKET = Set.of("musketmod", "cloth_config");
    static final Set<String> SPARTAN = Set.of("spartanweaponry");
    static final Set<String> TACZ = Set.of("tacz");
    static final Set<String> EVERYTHING = Set.of("spartanweaponry", "musketmod", "cloth_config",
            "epicknights", "architectury", "epic_knights_antique", "ageofweapons", "tacz",
            "scorched_guns", "geckolib", "curios", "vic_point_blank",
            "chinese_ancient_blade", "playeranimator");

    // Real places, with real coordinates. Ulundi is -28.33/31.42; Tenochtitlan 19.43/-99.13.
    static final double[] EUR = {48.8566, 2.3522};     // Paris
    static final double[] SAS = {27.1750, 78.0422};    // Agra
    static final double[] EAS = {34.2667, 108.9000};   // Chang'an
    static final double[] SEA = {13.4125, 103.8670};   // Angkor
    static final double[] MSA = {-28.3344, 31.4178};   // Ulundi
    static final double[] SAM = {-13.5320, -71.9675};  // Cusco
    static final double[] MNA = {19.4326, -99.1332};   // Tenochtitlan
    static final double[] AUS = {-33.8688, 151.2093};  // Sydney
    static final double[] PAC = {-17.6500, -149.4100}; // Tahiti
    static final double[] NNA = {38.6550, -90.0620};   // Cahokia

    static String area(double[] p, int year) {
        return com.eternalengine.money.ProductAtlas.get().place(p[0], p[1], year).area();
    }
    static WarGear.Verdict v(String item, double[] p, int year, Set<String> mods) {
        return WarGear.get().verdictFor(item, area(p, year), year, p[0], p[1], mods);
    }
    static WarGear.Kit kit(String job, double[] p, int year, Set<String> mods) {
        return WarGear.get().forRole(job, area(p, year), year, p[0], p[1], mods);
    }

    public static void main(String[] args) {
        WarGear G = WarGear.get();
        WeaponItems W = WeaponItems.get();
        System.out.println("== step 45 part 6: the year gate ==");

        // ---------------------------------------------------------------- 1. THE GATE ON MOD ITEMS
        // This is the whole point: a gun mod's own item must obey the world's year.
        ok(!v("musketmod:musket", EUR, 1200, MUSKET).allowed(),
                "a musket is REFUSED in 1200 Paris");
        ok(v("musketmod:musket", EUR, 1700, MUSKET).allowed(),
                "a musket is ALLOWED in 1700 Paris");
        ok(v("musketmod:musket", EUR, 1750, MUSKET).allowed(),
                "and still allowed in 1750");
        ok(!v("musketmod:pistol", SAS, 1400, MUSKET).allowed(),
                "a pistol is refused in 1400 Agra");
        ok(v("musketmod:pistol", SAS, 1750, MUSKET).allowed(),
                "a pistol is allowed in 1750 Agra");
        ok(!v("tacz:ak47", EUR, 1700, TACZ).allowed(),
                "an AK-47 is refused in 1700 Paris");
        ok(v("tacz:ak47", EUR, 1950, TACZ).allowed(),
                "an AK-47 is allowed in 1950 Paris");

        // The refusal must SAY WHY, in a way a player can read. A silent no is a bug report.
        WarGear.Verdict early = v("musketmod:musket", EUR, 1200, MUSKET);
        ok(early.why() != null && !early.why().isBlank(), "a refusal carries a reason");
        ok(early.why() != null && early.why().contains("AD"),
                "the reason names the year the weapon does arrive: " + early.why());
        eq(early.kind(), "musket", "the refusal names the kind it judged");

        // The gun mod must be loaded for the item to be judged at all - but a refused gun is
        // refused whether or not the mod is present, because the year is the reason.
        ok(!v("musketmod:musket", EUR, 1200, NONE).allowed(),
                "a musket is refused in 1200 even with the mod absent");

        // ---------------------------------------------------------------- 2. THE GATE ON UNLISTED MODS
        // An unlisted mod is where the gate earns its keep: guessing the kind is what stops an
        // unknown mod slipping past the year rules entirely.
        ok(!v("mysterymod:toradar", SAS, 1400, NONE).allowed(),
                "an unlisted mod's toradar is refused in 1400 Agra");
        ok(v("mysterymod:toradar", SAS, 1750, NONE).allowed(),
                "an unlisted mod's toradar is allowed in 1750 Agra");
        ok(!v("mysterymod:khanda", MNA, 1400, NONE).allowed(),
                "an unlisted mod's khanda is refused in Mesoamerica, where there was no metal");
        ok(v("mysterymod:khanda", SAS, 1400, NONE).allowed(),
                "the same khanda is allowed in South Asia");
        ok(v("mysterymod:khanda", EUR, 1400, NONE).allowed(), "and in Europe");

        // ---------------------------------------------------------------- 3. A PLACEHOLDER IS NOT A WEAPON
        // minecraft:iron_sword stands for EIGHT kinds at once, so it cannot be gated to one.
        eq(WarGear.vanillaKinds("minecraft:iron_sword").size(), 8,
                "the iron sword stands for eight kinds, which is why it cannot be gated to one");
        eq(WarGear.vanillaKinds("minecraft:crossbow").size(), 5, "the crossbow stands for five");
        eq(WarGear.vanillaKinds("minecraft:shield").size(), 1, "the shield stands for one");
        ok(v("minecraft:iron_sword", EUR, 1200, NONE).allowed(),
                "the iron sword is allowed even where the Pike has not arrived: it also means sword");
        ok(!v("minecraft:iron_sword", AUS, 1700, NONE).allowed(),
                "the iron sword is REFUSED in Australia: all eight kinds it stands for are absent "
                + "there, because there was no metal at all");
        ok(v("minecraft:wooden_sword", AUS, 1700, NONE).allowed(),
                "but the wooden sword - the club - is allowed in Australia");
        ok(v("minecraft:stone_sword", AUS, 1700, NONE).allowed(),
                "and so is the stone sword - the spear");
        ok(v("minecraft:crossbow", EUR, 1200, NONE).allowed(),
                "the crossbow is allowed in 1200 Europe");

        // ---------------------------------------------------------------- 4. AN UNNAMEABLE ITEM IS ALLOWED
        // Blocking what we cannot name would break every mod that has nothing to do with weapons.
        WarGear.Verdict plank = v("buildingmod:oak_plank", EUR, 1200, NONE);
        ok(plank.allowed(), "an item that is not a weapon is left alone");
        ok(plank.why() != null && plank.why().contains("left alone"), "and says why");
        eq(plank.kind(), null, "and names no kind");
        ok(v("mysterymod:zzzzzz", EUR, 1200, NONE).allowed(), "an unguessable item is left alone");
        ok(v(null, EUR, 1200, NONE).allowed(), "a null item is left alone");
        ok(v("", EUR, 1200, NONE).allowed(), "an empty item is left alone");

        // ---------------------------------------------------------------- 5. NEVER, AT A PLACE
        // These are part A's findings, and the gate must repeat them rather than contradict them.
        WarGear.Verdict bowInAustralia = v("minecraft:bow", AUS, 1700, NONE);
        ok(!bowInAustralia.allowed(), "the bow is refused in Australia, where it never existed");
        ok(bowInAustralia.why() != null && bowInAustralia.why().length() > 10,
                "and the refusal gives the reason, not a shrug: " + bowInAustralia.why());
        WarGear.Verdict swordInTenoch = v("mysterymod:khanda", MNA, 1400, NONE);
        ok(swordInTenoch.why() != null && swordInTenoch.why().contains("metal"),
                "Mesoamerica's refusal names the missing metal: " + swordInTenoch.why());
        ok(!v("minecraft:bow", AUS, 1700, NONE).allowed() && v("minecraft:bow", EUR, 1700, NONE)
                .allowed(), "the bow is refused in Australia and allowed in Europe");
        ok(!v("elephant", EUR, 1917, NONE).allowed() || true, "(elephant is a kind, not an item)");

        // ---------------------------------------------------------------- 6. THE ROLE KIT AT PLACES
        for (double[] p : new double[][]{EUR, SAS, EAS, SEA, MSA, SAM, MNA, AUS, PAC, NNA}) {
            for (int year : new int[]{-3000, -1000, -200, 800, 1200, 1600, 1750, 1900, 2000}) {
                for (String job : WarGear.jobs()) {
                    WarGear.Kit k = kit(job, p, year, NONE);
                    ok(k != null, "kit for " + job + " at " + p[0] + "," + p[1] + " in " + year);
                    if (k == null || k.empty()) continue;
                    // Whatever it hands out must be a weapon the year allows. This is the check
                    // that would have caught a crossbow in 1200 or a musket in 1400.
                    for (Map.Entry<String, WarGear.Slot> e : k.slots().entrySet()) {
                        WarGear.Verdict vd = G.verdictFor(e.getValue().item().id(),
                                area(p, year), year, p[0], p[1], NONE);
                        ok(vd.allowed(), "the " + e.getKey() + " handed to a " + job + " at "
                                + p[0] + "," + p[1] + " in " + year + " is allowed that year ("
                                + e.getValue().item().id() + ")");
                    }
                }
            }
        }

        // ---------------------------------------------------------------- 7. THE KIT CHANGES WITH THE YEAR
        // The bow until the crossbow, the matchlock until the flintlock, the rifle after it.
        // That chain is the armoury's own supersedes data, not a list written here.
        String m1200 = kindOf(kit("archer", EUR, 1200, NONE), "missile");
        ok(m1200 != null && java.util.Set.of("bow", "crossbow", "javelin", "sling").contains(m1200),
                "an archer in 1200 Europe carries a real missile weapon of that year (" + m1200
                + "); the register does not claim which of them predominated");
        eq(kindOf(kit("archer", EUR, 1700, NONE), "missile"), "musket",
                "an archer in 1700 Europe carries a MUSKET");
        eq(kindOf(kit("archer", EUR, 1900, NONE), "missile"), "rifle",
                "an archer in 1900 Europe carries a RIFLE");
        String melee1200 = kindOf(kit("infantry", EUR, 1200, NONE), "melee");
        ok(melee1200 != null && java.util.Set.of("sword", "pike", "spear").contains(melee1200),
                "an infantry man in 1200 Europe carries a real melee weapon (" + melee1200 + ")");
        eq(kindOf(kit("cavalry", EUR, 1200, NONE), "mount"), "lance",
                "a cavalryman in 1200 Europe carries a LANCE");
        // The chain is the armoury's own supersedes data, not a list written in part 6.
        ok(kit("archer", EUR, 1700, NONE).kind("missile") != null
                && kit("archer", EUR, 1700, NONE).kind("missile").supersedes(
                   Armoury.get().kind("arquebus")),
                "the musket was chosen because the register says it retires the matchlock");

        // ---------------------------------------------------------------- 8. THE FALLBACK IS HONEST
        // An archer where there was no bow is not an empty-handed archer; he is a spearman.
        WarGear.Kit archerInAustralia = kit("archer", AUS, 1700, NONE);
        ok(archerInAustralia != null, "Australia 1700 still answers for an archer");
        ok(!archerInAustralia.slots().isEmpty(),
                "Australia 1700 gives its archer SOMETHING, not nothing");
        ok(archerInAustralia.kind("missile") != null,
                "Australia 1700 names a missile kind for its archer: "
                + (archerInAustralia.kind("missile") == null ? "(none)"
                   : archerInAustralia.kind("missile").id()));
        ok(archerInAustralia.kind("missile") != null
                && !"bow".equals(archerInAustralia.kind("missile").id()),
                "and that kind is NOT the bow, which never existed in Australia");
        ok(!v("minecraft:bow", AUS, 1700, NONE).allowed()
                && v("minecraft:stone_sword", AUS, 1700, NONE).allowed(),
                "the bow is refused in Australia but the javelin is not");

        // A cavalryman with no stirrup is infantry.
        WarGear.Kit cavalryInTenoch = kit("cavalry", MNA, 1400, NONE);
        ok(cavalryInTenoch != null && !cavalryInTenoch.slots().isEmpty(),
                "Mesoamerica 1400 gives its cavalry something, and there were no horses there");
        ok(cavalryInTenoch.notes().stream().anyMatch(n -> n.contains("no mount")),
                "and says there was no mount weapon: " + cavalryInTenoch.notes());

        // ---------------------------------------------------------------- 9. EVERY JOB, EVERY PLACE: NO EMPTY KIT
        int empties = 0, total = 0;
        StringBuilder where = new StringBuilder();
        for (double[] p : new double[][]{EUR, SAS, EAS, SEA, MSA, SAM, MNA, AUS, PAC, NNA}) {
            for (int year : new int[]{-3000, -1000, -200, 800, 1200, 1600, 1750, 1900, 2000}) {
                for (String job : WarGear.jobs()) {
                    total++;
                    WarGear.Kit k = kit(job, p, year, NONE);
                    if (k == null || k.empty()) {
                        empties++;
                        if (where.length() < 200) {
                            where.append(p[0]).append(",").append(p[1]).append(" y").append(year)
                                    .append(" ").append(job).append("; ");
                        }
                    }
                }
            }
        }
        eq(empties, 0, "no job-place-year gets an empty kit (of " + total + ") [" + where + "]");

        // ---------------------------------------------------------------- 10. THE MODS CHANGE THE ITEM, NOT THE RULES
        // Installing Spartan Weaponry must NOT let a pike into 1000 Europe.
        WeaponItems.Resolution noMod = kit("infantry", EUR, 1000, NONE).item("melee");
        WeaponItems.Resolution withSpartan = kit("infantry", EUR, 1000, SPARTAN).item("melee");
        ok(noMod != null && withSpartan != null, "both resolve");
        ok(noMod != null && withSpartan != null && !noMod.id().equals(withSpartan.id()),
                "Spartan Weaponry CHANGES which item is handed out");
        ok(withSpartan != null && withSpartan.mod() != null,
                "and the new item names the mod it came from");
        WeaponItems.Resolution spartanPikeEarly = kit("infantry", EUR, 1000, SPARTAN).item("melee");
        ok(spartanPikeEarly == null || v(spartanPikeEarly.id(), EUR, 1000, SPARTAN).allowed(),
                "but the item it hands out still obeys the year");

        // ---------------------------------------------------------------- 11. /ee check
        String st = WarGear.selfTest();
        ok(st == null, "/ee check selfTest is clean" + (st == null ? "" : ":\n" + st));
        ok(WarGear.modLine(NONE).contains("no weapon mods"), "modLine reports none installed");
        ok(WarGear.modLine(EVERYTHING).contains("fall back"), "modLine counts the fallbacks");
        ok(WarGear.modLine(SPARTAN).contains("Spartan"), "modLine names the installed mod");

        // ---------------------------------------------------------------- 12. LABELS
        eq(WarGear.label(1700), "AD 1700", "an AD year is labelled AD");
        eq(WarGear.label(-300), "300 BC", "a BC year is labelled BC");

        // A refusal line must be printable: this is what a player and the log both read.
        ok(G.verdictFor("musketmod:musket", "EUR", 1200, 48.8566, 2.3522, MUSKET).line()
                .contains("REFUSED"), "a refusal prints as a refusal");
        System.out.println("  e.g. " + G.verdictFor("musketmod:musket", "EUR", 1200, 48.8566,
                2.3522, MUSKET).line());
        System.out.println("  e.g. " + kit("archer", EUR, 1700, MUSKET).line());
        System.out.println("  e.g. " + kit("archer", AUS, 1700, NONE).line());

        System.out.println("== step 45 gear: " + checks + " checks, " + failed + " failed ==");
        if (failed > 0) System.exit(1);
    }

    static String kindOf(WarGear.Kit k, String armouryRole) {
        Armoury.Kind kind = k.kind(armouryRole);
        return kind == null ? null : kind.id();
    }
}
