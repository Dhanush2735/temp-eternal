import com.eternalengine.war.Arms;
import com.eternalengine.war.Units;
import com.eternalengine.war.Units.Army;
import com.eternalengine.war.Units.Rung;
import com.eternalengine.war.Units.Ladder;

import java.util.ArrayList;
import java.util.List;

/**
 * Step 45 part 4 (C19): units and ranks.
 *
 * <p>Checks are printed, so a wrong answer is visible. It reads the real {@code units.json.gz}
 * through the mod's own class and asserts the finding the register exists to record: that the same
 * thousand men were divided five different ways.
 */
public final class Step45UnitsProbe {

    private static int checks = 0;
    private static int failed = 0;

    private static void ok(boolean cond, String what) {
        checks++;
        if (!cond) {
            failed++;
            System.out.println("  FAIL  " + what);
        }
    }

    private static void eq(Object got, Object want, String what) {
        checks++;
        if (got == null ? want != null : !got.equals(want)) {
            failed++;
            System.out.println("  FAIL  " + what + ": got " + got + ", want " + want);
        }
    }

    private static final Object[][] PLACES = {
        {"Uruk, Sumer", 31.3, 45.6, -3000},
        {"Sparta", 37.07, 22.43, -400},
        {"Rome", 41.88, 12.50, 100},
        {"Pataliputra, Maurya", 25.6, 85.1, -250},
        {"Cusco, Inca", -13.53, -71.97, 1500},
        {"Tenochtitlan", 19.43, -99.13, 1500},
        {"Karabalgasun, steppe", 47.0, 103.0, 1250},
        {"Beijing, Ming", 39.9, 116.4, 1500},
        {"Istanbul, Ottoman", 41.01, 28.98, 1600},
        {"Agra, Mughal", 27.18, 78.02, 1650},
        {"Timbuktu, Songhai", 16.77, -3.01, 1500},
        {"Ulundi, Zulu", -28.33, 31.42, 1870},
        {"London, 1400", 51.51, -0.13, 1400},
        {"Blenheim, 1704", 48.4, 10.4, 1704},
        {"Ypres, 1917", 50.85, 2.88, 1917},
        {"Cahokia", 38.65, -90.11, 1100},
        {"Cape York, Australia", -10.7, 142.5, 1700},
        {"Tahiti", -17.65, -149.45, 1750},
    };

    public static void main(String[] args) {
        Units u = Units.get();

        // ------------------------------------------------------------------ the pack itself
        System.out.println("the pack");
        ok(u.hasData(), "the pack loaded (" + u.problem() + ")");
        ok(u.problem() == null, "no problem reading it");
        ok(u.systems().size() >= 10, "%d systems".formatted(u.systems().size()));
        eq(u.areas().size(), 17, "17 areas");

        Ladder def = u.fallback();
        ok(def != null, "there is a default system");
        if (def != null) {
            ok(def.isDefault(), "the default knows it is the default");
            ok(def.sizes().isEmpty(), "the default has no numbers in it");
            ok(def.rungFor(500) == null,
                    "asking the war party what 500 men make you gets no answer, correctly");
            ok(def.base() == null, "the default counts by no base at all");
        }

        // ------------------------------------------------------------------ the finding: five bases
        System.out.println();
        System.out.println("an army is counted in whatever base the society counts in");
        eq(baseOf(u, "mongol"), 10, "the steppe counts in tens");
        eq(baseOf(u, "inca"), 10, "the Andes count in tens");
        eq(baseOf(u, "ming"), 10, "Ming China counts in tens");
        eq(baseOf(u, "aztec"), 20, "the Aztecs count in twenties");
        eq(baseOf(u, "maurya"), 3, "the Indian epics count in threes");
        eq(baseOf(u, "sparta"), 2, "Sparta counts by doubling");
        eq(baseOf(u, "rome"), 8, "Rome counts in eights");
        ok(baseOf(u, "zulu") == null, "the Zulu count by no number at all");

        // the same thousand men, five different ladders
        eq(rungSize(u, "mongol", 1000), 1000, "a thousand men on the steppe is a mingghan");
        eq(rungSize(u, "inca", 1000), 1000, "a thousand men in the Andes is a waranqa");
        eq(rungSize(u, "rome", 480), 480, "480 men in Rome is a cohort");
        eq(rungSize(u, "aztec", 400), 400, "400 men in Mesoamerica is a tzontli");
        eq(rungSize(u, "maurya", 810), 810, "810 men in the epics is a vahini");

        // ------------------------------------------------------------------ the ladders themselves
        System.out.println();
        System.out.println("the ladders");
        checkLadder(u, "rome", new int[]{8, 80, 480, 5120});
        checkLadder(u, "mongol", new int[]{10, 100, 1000, 10000});
        checkLadder(u, "aztec", new int[]{20, 200, 400, 8000});
        checkLadder(u, "sparta", new int[]{36, 72, 144, 576});
        checkLadder(u, "inca", new int[]{10, 50, 100, 1000, 10000});
        checkLadder(u, "ming", new int[]{10, 50, 112, 1120, 5600});
        checkLadder(u, "modern", new int[]{10, 35, 150, 800, 4000, 15000, 40000});
        checkLadder(u, "maurya",
                new int[]{10, 30, 90, 270, 810, 2430, 7290, 21870, 218700});

        // ------------------------------------------------------------------ ranks
        System.out.println();
        System.out.println("ranks");
        eq(rank(u, "rome", 80), "centurion", "eighty men in Rome are led by a centurion");
        eq(rank(u, "rome", 8), "decanus", "eight men in Rome are led by a decanus");
        eq(rank(u, "modern", 800), "lieutenant colonel",
                "eight hundred men in 1917 are led by a lieutenant colonel");
        eq(rank(u, "mongol", 10000), "tümen-ü noyan", "ten thousand on the steppe is a myriarch");
        eq(rank(u, "inca", 100), "pachak kamayuq", "a hundred in the Andes is a pachak kamayuq");
        eq(rank(u, "ottoman", 10), "oda-başı", "ten janissaries answer to the oda-başı");
        eq(rank(u, "zulu", 4000), "induna", "a Zulu regiment answers to an induna");
        ok(rank(u, "maurya", 218700) == null,
                "no commander is recorded for the akshauhini, and none is invented");

        // ------------------------------------------------------------------ every place and year answers
        System.out.println();
        System.out.println("the prose");
        for (Object[] p : PLACES) {
            String name = (String) p[0];
            Army a = u.hereAt((Double) p[1], (Double) p[2], (Integer) p[3]);
            Ladder s = a.system();
            ok(s != null, name + " has an answer");
            if (s == null) {
                continue;
            }
            ok(s.y0() <= (Integer) p[3] && (Integer) p[3] <= s.y1(),
                    name + " system covers its own year");
            ok(s.areas().contains(u.areas().indexOf(a.area())),
                    name + " system covers its own area");
            ok(!s.note().isBlank() && !s.source().isBlank(),
                    name + " has a note and a source");
            String ladder = u.ladderLine((Double) p[1], (Double) p[2], (Integer) p[3]);
            System.out.printf("   %-24s %-4s %-13s %-9s %s%n", name, a.area(), s.id(),
                    a.matched() ? "named" : "default", ladder.isEmpty() ? "(no numbers)" : ladder);
        }

        // ------------------------------------------------------------------ the places that must be right
        System.out.println();
        System.out.println("the places that must be right");
        eq(sysAt(u, 41.88, 12.50, 100).id(), "rome", "Rome in AD 100 has the legion");
        eq(sysAt(u, 19.43, -99.13, 1500).id(), "aztec", "Tenochtitlan in 1500 has the xiquipilli");
        eq(sysAt(u, -13.53, -71.97, 1500).id(), "inca", "Cusco in 1500 has the decimal levy");
        eq(sysAt(u, 39.9, 116.4, 1500).id(), "ming", "Beijing in 1500 has the wei-suo");
        eq(sysAt(u, 41.01, 28.98, 1600).id(), "ottoman", "Istanbul in 1600 has the janissaries");
        eq(sysAt(u, 27.18, 78.02, 1650).id(), "mughal", "Agra in 1650 has the mansabdari");
        eq(sysAt(u, 25.6, 85.1, -250).id(), "maurya", "Pataliputra in 250 BC has the epics' ladder");
        eq(sysAt(u, -28.33, 31.42, 1870).id(), "zulu", "Ulundi in 1870 has the amabutho");
        eq(sysAt(u, 16.77, -3.01, 1500).id(), "sahel", "Timbuktu in 1500 has the Sudanese corps");
        eq(sysAt(u, 48.4, 10.4, 1704).id(), "earlymodern", "Blenheim in 1704 has the regiment");
        eq(sysAt(u, 50.85, 2.88, 1917).id(), "modern", "Ypres in 1917 has the division");

        // The two polity overrides that the area key alone cannot make: East Asia holds both Ming
        // China and Japan, and South Asia holds both the epics' ladder and the Mughals'.
        eq(sysAt(u, 39.9, 116.4, 1500).id(), "ming", "East Asia 1500 reads Ming at Beijing");
        ok(!sysAt(u, 39.9, 116.4, 1500).id().equals("mongol"),
                "and does not read the steppe ladder there");

        // ------------------------------------------------------------------ honesty about the fallback
        System.out.println();
        int defaulted = 0;
        int total = 0;
        for (int ai = 0; ai < u.areas().size(); ai++) {
            for (int year = -3000; year <= 2000; year += 100) {
                total++;
                Ladder s = u.systemIn(u.areas().get(ai), year, null);
                if (s != null && s.isDefault()) {
                    defaulted++;
                }
            }
        }
        System.out.printf("  %d area-years: %d falling to the default%n", total, defaulted);
        ok(defaulted < total, "some area-year has a real system and not just the default");
        // The war party must win in the Pacific and in Australia, because it is true there.
        ok(u.systemIn("AUS", 1700, null).isDefault(), "Australia in 1700 has the war party, truly");
        ok(u.systemIn("PAC", 1700, null).isDefault(), "Polynesia in 1700 has the war party, truly");
        ok(!u.systemIn("EUR", 1917, null).isDefault(), "Europe in 1917 does not");

        // ------------------------------------------------------------------ it agrees with part B
        System.out.println();
        System.out.println("the three halves of this step agree");
        ok(Arms.get().hasData(), "the arms pack loaded too");
        for (Object[] p : new Object[][]{{"Rome", 41.88, 12.50, 100},
                {"Tenochtitlan", 19.43, -99.13, 1500}, {"Ypres", 50.85, 2.88, 1917}}) {
            String area = u.hereAt((Double) p[1], (Double) p[2], (Integer) p[3]).area();
            String armsArea = Arms.get().hereAt((Double) p[1], (Double) p[2], (Integer) p[3]).area();
            eq(area, armsArea, "%s: the unit register and the arms register agree where this is"
                    .formatted(p[0]));
            ok(!u.describe((Double) p[1], (Double) p[2], (Integer) p[3]).isBlank(),
                    p[0] + " has something to say");
        }

        System.out.println();
        System.out.println("units: " + checks + " checks, " + failed + " failed");
        if (failed > 0) {
            System.exit(1);
        }
    }

    // -------------------------------------------------------------------------------------------------- helpers

    private static Ladder byId(Units u, String id) {
        for (Ladder s : u.systems()) {
            if (s.id().equals(id)) {
                return s;
            }
        }
        return null;
    }

    private static Integer baseOf(Units u, String id) {
        Ladder s = byId(u, id);
        return s == null ? null : s.base();
    }

    /** The size of the rung a commander of this many men holds, in this system. */
    private static Integer rungSize(Units u, String id, int men) {
        Ladder s = byId(u, id);
        if (s == null) {
            return null;
        }
        Rung r = s.rungFor(men);
        return r == null ? null : r.size();
    }

    private static String rank(Units u, String id, int men) {
        Ladder s = byId(u, id);
        return s == null ? null : s.rankFor(men);
    }

    private static void checkLadder(Units u, String id, int[] want) {
        Ladder s = byId(u, id);
        ok(s != null, "the " + id + " system is in the pack");
        if (s == null) {
            return;
        }
        List<Integer> got = new ArrayList<>(s.sizes());
        List<Integer> w = new ArrayList<>();
        for (int n : want) {
            w.add(n);
        }
        eq(got, w, "%s: the ladder is %s".formatted(id, w));
    }

    private static Ladder sysAt(Units u, double lat, double lon, int year) {
        return u.hereAt(lat, lon, year).system();
    }
}
