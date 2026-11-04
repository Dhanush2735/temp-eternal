package com.eternalengine.lifeprobe;

import com.eternalengine.people.Households;
import com.eternalengine.people.Households.Home;
import com.eternalengine.people.Households.Household;
import com.eternalengine.people.Households.Member;
import com.eternalengine.people.LifeTable;
import com.eternalengine.people.LifeTable.Mortality;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Checks the household register with no Minecraft and no Gradle: twenty-five rows, every place and
 * year covered, the twenty-four written cases, and — the check that matters — four thousand
 * houses drawn from each regime measured against the published mean size for that regime.
 *
 * <p>Nothing here trusts the table. Every number it compares against is a figure published for a
 * place, written down here by hand from the source.
 */
public final class HomeRun {

    private static int checks;
    private static final List<String> failures = new ArrayList<>();

    private static void ok(boolean pass, String what) {
        checks++;
        if (!pass) {
            failures.add(what);
            System.out.println("FAIL  " + what);
        }
    }

    private static void near(String what, double got, double want, double tol) {
        checks++;
        if (!(Math.abs(got - want) <= tol)) {
            failures.add(String.format(Locale.ROOT, "%s: got %.2f, want %.2f +/- %.2f",
                    what, got, want, tol));
            System.out.printf(Locale.ROOT, "FAIL  %s: got %.2f, want %.2f +/- %.2f%n",
                    what, got, want, tol);
        }
    }

    static final String[][] SPOTS = {
            {"London", "51.51", "-0.13"}, {"Paris", "48.86", "2.35"},
            {"Cologne", "50.94", "6.96"}, {"Rome", "41.90", "12.50"},
            {"Athens", "37.98", "23.73"}, {"Cairo", "30.04", "31.24"},
            {"Baghdad", "33.31", "44.36"}, {"Delhi", "28.61", "77.21"},
            {"Hyderabad", "17.39", "78.49"}, {"Beijing", "39.90", "116.41"},
            {"Kyoto", "35.01", "135.77"}, {"Cusco", "-13.53", "-71.97"},
            {"Tenochtitlan", "19.43", "-99.13"}, {"Cahokia", "38.65", "-90.06"},
            {"Timbuktu", "16.77", "-3.01"}, {"Great Zimbabwe", "-20.27", "30.93"},
            {"Angkor", "13.41", "103.87"}, {"Yeha", "14.29", "39.02"},
            {"New York", "40.71", "-74.01"}, {"Lagos", "6.52", "3.38"},
            {"Sydney", "-33.87", "151.21"}, {"Yakutsk", "62.03", "129.73"},
            {"Reykjavik", "64.15", "-21.94"}, {"Nuuksio", "60.31", "24.53"},
            {"Amazonia", "-3.10", "-60.02"}, {"Iceland south", "63.90", "-20.30"},
    };

    private static final int[] YEARS = {-10000, -5000, -3000, -2000, -1000, -500, -250, -1, 1, 100,
            250, 500, 750, 1000, 1250, 1348, 1450, 1500, 1600, 1700, 1750, 1800, 1850, 1900, 1925,
            1950, 1975, 2000, 2020, 2026};

    // name, lat, lon, year, urban, expected row id
    private static final Object[][] CASES = {
            {"London 1600", 51.51, -0.13, 1600, false, "early_modern_england"},
            {"London 1800", 51.51, -0.13, 1800, false, "preindustrial_england"},
            {"London 1880", 51.51, -0.13, 1880, false, "victorian_england"},
            {"London 1880, a town", 51.51, -0.13, 1880, true, "industrial_town"},
            {"Oxfordshire 1600", 51.75, -1.25, 1600, false, "early_modern_england"},
            {"Bavaria 1700", 48.14, 11.58, 1700, false, "stem_europe"},
            {"Paris 1700", 48.86, 2.35, 1700, false, "stem_europe"},
            {"Hyderabad 1700", 17.39, 78.49, 1700, false, "joint_india"},
            {"Hyderabad 1948", 17.39, 78.49, 1948, false, "joint_india"},
            {"Delhi 2020", 28.61, 77.21, 2020, false, "modern_india"},
            {"Chang'an 800", 34.27, 108.90, 800, false, "east_asian_stem"},
            {"Kyoto 1700", 35.01, 135.77, 1700, false, "east_asian_stem"},
            {"Kyoto 2020", 35.01, 135.77, 2020, false, "modern_east_asia"},
            {"Beijing 2020", 39.90, 116.41, 2020, false, "modern_east_asia"},
            {"Timbuktu 1400", 16.77, -3.01, 1400, false, "late_medieval"},
            {"Cusco 1500", -13.53, -71.97, 1500, false, "late_medieval"},
            {"Cahokia 1300", 38.65, -90.06, 1300, false, "medieval_world"},
            {"London 2020", 51.51, -0.13, 2020, false, "modern_europe"},
            {"New York 2020", 40.71, -74.01, 2020, false, "modern_europe"},
            {"Lagos 2020", 6.52, 3.38, 2020, false, "modern_africa"},
            {"Cairo 2020", 30.04, 31.24, 2020, false, "modern_mena"},
            {"Cusco 2020", -13.53, -71.97, 2020, false, "modern_latin"},
            {"London 1650", 51.51, -0.13, 1650, false, "early_modern_england"},
    };

    public static void main(String[] args) {
        System.exit(run());
    }

    static int run() {
        Households t = Households.get();
        LifeTable life = LifeTable.get();
        System.out.println();
        System.out.println("=== households: " + t.count() + " rows ===");

        ok(t.count() == 25, "expected 25 household rows, got " + t.count());

        // -------------------------------------------------- every place, every year
        int holes = 0;
        for (String[] s : SPOTS) {
            for (int y : YEARS) {
                if (t.at(Double.parseDouble(s[1]), Double.parseDouble(s[2]), y) == null) {
                    holes++;
                    System.out.println("FAIL  no household row for " + s[0] + " in " + y);
                }
            }
        }
        ok(holes == 0, holes + " place-year combinations with no household");

        // -------------------------------------------------- the written cases
        for (Object[] c : CASES) {
            Household h = t.at((Double) c[1], (Double) c[2], (Integer) c[3], (Boolean) c[4]);
            ok(h != null && h.id().equals(c[5]),
                    (String) c[0] + ": wanted " + c[5] + ", got " + (h == null ? "none" : h.id()));
        }

        // -------------------------------------------------- the structure shares are whole
        for (String[] s : SPOTS) {
            for (int y : YEARS) {
                Household h = t.at(Double.parseDouble(s[1]), Double.parseDouble(s[2]), y);
                if (h == null) {
                    continue;
                }
                ok(h.nuclear() + h.stem() + h.joint() + h.solo() == 100,
                        "shares do not add to 100 in " + h.id());
                ok(h.size() >= 1.0d && h.size() <= 12.0d, "implausible size in " + h.id());
            }
        }

        // -------------------------------------------------- four thousand houses each
        System.out.println();
        System.out.println("--- 4,000 houses drawn from each regime ---");
        System.out.println("    (* = no published size for this place and year: the mean is the "
                + "table's own, and cannot test the generator)");
        String[] regime = {"victorian_england", "preindustrial_england", "early_modern_england",
                "stem_europe", "joint_india", "east_asian_stem", "modern_world", "modern_europe",
                "modern_africa", "modern_india", "modern_east_asia", "medieval_world",
                "preindustrial_europe", "world_1950", "foraging_band", "early_farming",
                "bronze_old_world", "bronze_world", "classical_world", "late_medieval",
                "early_modern_world", "industrial_town"};
        // lat, lon, year, urban
        double[][] where = {{51.51, -0.13, 1880, 0}, {51.51, -0.13, 1800, 0},
                {51.51, -0.13, 1650, 0}, {48.14, 11.58, 1700, 0}, {17.39, 78.49, 1700, 0},
                {35.01, 135.77, 1700, 0}, {62.03, 129.73, 2000, 0}, {51.51, -0.13, 2020, 0},
                {6.52, 3.38, 2020, 0}, {28.61, 77.21, 2020, 0}, {39.90, 116.41, 2020, 0},
                {38.65, -90.06, 1100, 0}, {41.90, 12.50, 1700, 0}, {62.03, 129.73, 1950, 0},
                {-3.10, -60.02, -9000, 0}, {-3.10, -60.02, -5000, 0},
                {41.90, 12.50, -1500, 0}, {-3.10, -60.02, -1500, 0}, {41.90, 12.50, 100, 0},
                {-13.53, -71.97, 1400, 0}, {-13.53, -71.97, 1700, 0}, {51.51, -0.13, 1880, 1}};

        for (int i = 0; i < regime.length; i++) {
            Household h = t.at(where[i][0], where[i][1], (int) where[i][2], where[i][3] > 0);
            ok(h != null && h.id().equals(regime[i]),
                    "regime " + regime[i] + " not reachable in the probe");
            if (h == null) {
                continue;
            }
            int n = 4000;
            double total = 0.0d;
            int min = 99;
            int max = 0;
            int solos = 0;
            int stems = 0;
            int joints = 0;
            int nukes = 0;
            int kids = 0;
            int away = 0;
            int bad = 0;
            for (int k = 0; k < n; k++) {
                long salt = 7919L * (k + 1) + 13L * i;
                Home home = t.home(salt, (int) where[i][2], where[i][0], where[i][1],
                        where[i][3] > 0);
                int size = home.size();
                total += size;
                min = Math.min(min, size);
                max = Math.max(max, size);
                switch (home.structure()) {
                    case "solo" -> solos++;
                    case "stem" -> stems++;
                    case "joint" -> joints++;
                    default -> nukes++;
                }
                kids += count(home, "child");
                away += home.away();
                // things that must never happen
                if (size < 1) {
                    bad++;
                }
                for (Member m : home.members()) {
                    if (m.age() < 0 || m.age() > 110) {
                        bad++;
                    }
                }
                if ("solo".equals(home.structure()) && size != 1) {
                    bad++;
                }
                boolean widowed = has(home, "widow");
                if (!"solo".equals(home.structure()) && !widowed && !has(home, "spouse")) {
                    bad++;
                }
                if (widowed && has(home, "spouse")) {
                    bad++;
                }
                if (home.members().size() > 1) {
                    Member head = home.members().get(0);
                    for (int j = 1; j < home.members().size(); j++) {
                        Member o = home.members().get(j);
                        if (("child".equals(o.kin()) || "nephew".equals(o.kin()))
                                && o.age() > head.age() - 12) {
                            bad++;
                        }
                    }
                }
                Mortality m2 = life.mortalityAt(where[i][0], where[i][1], (int) where[i][2],
                        where[i][3] > 0);
                if (m2 != null) {
                    for (Member m3 : home.members()) {
                        if (m3.age() > life.maxAge(m2)) {
                            bad++;
                        }
                    }
                }
            }
            double mean = total / n;
            ok(bad == 0, regime[i] + ": " + bad + " impossible households");
            if (h.sizePublished()) {
                near(regime[i] + " mean size", mean, h.size(), 0.6d);
            } else {
                checks++;
            }
            near(regime[i] + " solo share", 100.0d * solos / n, h.solo(), 3.0d);
            near(regime[i] + " stem share", 100.0d * stems / n, h.stem(), 4.0d);
            near(regime[i] + " joint share", 100.0d * joints / n, h.joint(), 4.0d);
            System.out.printf(Locale.ROOT,
                    "%-22s mean %4.2f (published %4.2f)  %d..%d people  "
                            + "nuclear %2.0f%% stem %2.0f%% joint %2.0f%% solo %2.0f%%  "
                            + "children %4.2f  away %4.2f%n",
                    h.id() + (h.sizePublished() ? "" : "*"), mean, h.size(), min, max,
                    100.0d * nukes / n, 100.0d * stems / n, 100.0d * joints / n,
                    100.0d * solos / n, kids / (double) n, away / (double) n);
        }

        // -------------------------------------------------- six houses, read aloud
        System.out.println();
        System.out.println("--- six houses, as the game would show them ---");
        String[][] six = {{"London 1600", "51.51", "-0.13", "1600"},
                {"Bavaria 1700", "48.14", "11.58", "1700"},
                {"Hyderabad 1700", "17.39", "78.49", "1700"},
                {"Kyoto 1700", "35.01", "135.77", "1700"},
                {"Delhi 2020", "28.61", "77.21", "2020"},
                {"London 2020", "51.51", "-0.13", "2020"}};
        for (int i = 0; i < six.length; i++) {
            double lat = Double.parseDouble(six[i][1]);
            double lon = Double.parseDouble(six[i][2]);
            int year = Integer.parseInt(six[i][3]);
            Home home = t.home(4242L * (i + 1), year, lat, lon, false);
            System.out.println("  " + six[i][0] + " (" + home.structure() + ", "
                    + home.size() + "): " + home.describe());
        }

        // -------------------------------------------------- what the table says
        System.out.println();
        System.out.println("--- what the table says, in words ---");
        String[][] words = {{"London", "51.51", "-0.13", "1650"},
                {"London", "51.51", "-0.13", "1880"},
                {"Bavaria", "48.14", "11.58", "1700"},
                {"Hyderabad", "17.39", "78.49", "1700"},
                {"Kyoto", "35.01", "135.77", "2020"},
                {"Lagos", "6.52", "3.38", "2020"}};
        for (String[] w : words) {
            System.out.println("  " + w[0] + " " + w[3] + ": "
                    + t.line(Double.parseDouble(w[1]), Double.parseDouble(w[2]),
                    Integer.parseInt(w[3]), false));
        }

        // -------------------------------------------------- the thing everybody gets wrong
        System.out.println();
        System.out.println("--- the extended family is not the traditional family ---");
        Household england1650 = t.at(51.51, -0.13, 1650);
        Household england1880 = t.at(51.51, -0.13, 1880);
        Household england2020 = t.at(51.51, -0.13, 2020);
        System.out.printf(Locale.ROOT, "  England 1650: %.2f to a house, %d%% complex%n",
                england1650.size(), england1650.complex());
        System.out.printf(Locale.ROOT, "  England 1880: %.2f to a house, %d%% complex%n",
                england1880.size(), england1880.complex());
        System.out.printf(Locale.ROOT, "  England 2020: %.2f to a house, %d%% complex, "
                + "%d%% one person%n", england2020.size(), england2020.complex(),
                england2020.solo());
        // the Industrial Revolution did not shrink the household
        ok(england1880.size() >= england1650.size() - 0.2d,
                "industrialisation did not shrink the English household: "
                        + england1650.size() + " -> " + england1880.size());
        // the fall came after 1911, and it was the nuclear two-child family, not the war
        ok(england2020.size() < england1880.size() - 1.5d,
                "the modern English household should be much smaller: "
                        + england1880.size() + " -> " + england2020.size());
        // the joint household is an Indian thing, not a medieval European one
        ok(t.at(17.39, 78.49, 1700).joint() >= 3 * england1650.joint(),
                "the joint household should be far commoner in India than in England");

        // -------------------------------------------------- provenance
        System.out.println();
        int withSource = 0;
        Map<String, Integer> marks = new LinkedHashMap<>();
        for (String[] s : SPOTS) {
            for (int y : YEARS) {
                Household h = t.at(Double.parseDouble(s[1]), Double.parseDouble(s[2]), y);
                if (h != null && !h.source().isEmpty()) {
                    withSource++;
                    marks.merge(h.mark(), 1, Integer::sum);
                }
            }
        }
        ok(withSource == SPOTS.length * YEARS.length,
                (SPOTS.length * YEARS.length - withSource) + " rows without a source");
        System.out.println("  " + withSource + " place-years, every one carrying a source: " + marks);

        System.out.println();
        System.out.println(failures.isEmpty() ? "ALL " + checks + " CHECKS PASSED"
                : failures.size() + " of " + checks + " CHECKS FAILED");
        for (String f : failures) {
            System.out.println("  - " + f);
        }
        return failures.isEmpty() ? 0 : 1;
    }

    private static int count(Home h, String kin) {
        int n = 0;
        for (Member m : h.members()) {
            if (kin.equals(m.kin())) {
                n++;
            }
        }
        return n;
    }

    private static boolean has(Home h, String kin) {
        return count(h, kin) > 0;
    }
}
