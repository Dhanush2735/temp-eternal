package com.eternalengine.lifeprobe;

import com.eternalengine.people.Jobs;
import com.eternalengine.people.Jobs.Job;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Checks the jobs register with no Minecraft and no Gradle: twenty-three rows, every place and year
 * covered, the twenty-four written cases, the three measured English sector splits, and four
 * thousand jobs drawn from each regime compared against the shares the row claims.
 *
 * <p>Nothing here trusts the table. Every number it compares against is a figure published for a
 * place, written down here by hand from the source.
 */
public final class JobRun {

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

    private static final int[] YEARS = {-10000, -5000, -3000, -2000, -1000, -500, -250, -1, 1, 100,
            250, 500, 750, 1000, 1250, 1348, 1450, 1500, 1600, 1688, 1700, 1750, 1800, 1841, 1900,
            1925, 1950, 1975, 1980, 2000, 2020, 2026};

    // name, lat, lon, year, urban, expected row id
    private static final Object[][] CASES = {
            {"London 1688", 51.51, -0.13, 1688, false, "england_1688"},
            {"London 1800", 51.51, -0.13, 1800, false, "england_1800"},
            {"London 1841", 51.51, -0.13, 1841, false, "england_1841"},
            {"London 1880, a town", 51.51, -0.13, 1880, true, "industrial_town"},
            {"Oxfordshire 1688", 51.75, -1.25, 1688, false, "england_1688"},
            {"Bavaria 1700", 48.14, 11.58, 1700, false, "early_modern_europe"},
            {"Rome 1700", 41.90, 12.50, 1700, false, "early_modern_europe"},
            {"Hyderabad 1850", 17.39, 78.49, 1850, false, "british_india"},
            {"Hyderabad 1948", 17.39, 78.49, 1948, false, "british_india"},
            {"Delhi 2020", 28.61, 77.21, 2020, false, "modern_india"},
            {"Kyoto 1700", 35.01, 135.77, 1700, false, "early_modern_world"},
            {"Beijing 1700", 39.90, 116.41, 1700, false, "early_modern_world"},
            {"Beijing 2020", 39.90, 116.41, 2020, false, "modern_east_asia"},
            {"Tokyo 2020", 35.68, 139.69, 2020, false, "modern_east_asia"},
            {"Cusco 1500", -13.53, -71.97, 1500, false, "late_medieval"},
            {"Cahokia 1100", 38.65, -90.06, 1100, false, "medieval_world"},
            {"Timbuktu 1400", 16.77, -3.01, 1400, false, "late_medieval"},
            {"London 2020", 51.51, -0.13, 2020, false, "modern_europe"},
            {"New York 2020", 40.71, -74.01, 2020, false, "modern_europe"},
            {"Lagos 2020", 6.52, 3.38, 2020, false, "modern_africa"},
            {"Cairo 2020", 30.04, 31.24, 2020, false, "modern_mena"},
            {"Cusco 2020", -13.53, -71.97, 2020, false, "modern_latin"},
            {"Yakutsk 2020", 62.03, 129.73, 2020, false, "modern_world"},
            {"Angkor 1300", 13.41, 103.87, 1300, false, "medieval_world"},
    };

    // the measured three-way split, from the Cambridge Group's revision of the English social
    // tables. Nothing else in this table has a published sector split to be checked against.
    private static final Object[][] SECTORS = {
            {"england_1688", 55.6d, 18.5d, 25.9d},
            {"england_1800", 41.7d, 24.7d, 33.6d},
            {"england_1841", 22.2d, 40.5d, 37.3d},
    };

    public static void main(String[] args) {
        System.exit(run());
    }

    static int run() {
        Jobs t = Jobs.get();
        System.out.println();
        System.out.println("=== jobs: " + t.count() + " rows ===");
        ok(t.count() == 23, "expected 23 jobs rows, got " + t.count());

        // -------------------------------------------------- every place, every year
        int holes = 0;
        for (String[] s : HomeRun.SPOTS) {
            for (int y : YEARS) {
                if (t.at(Double.parseDouble(s[1]), Double.parseDouble(s[2]), y) == null) {
                    holes++;
                    System.out.println("FAIL  no jobs row for " + s[0] + " in " + y);
                }
            }
        }
        ok(holes == 0, holes + " place-year combinations with no work");

        // -------------------------------------------------- the written cases
        for (Object[] c : CASES) {
            Job j = t.at((Double) c[1], (Double) c[2], (Integer) c[3], (Boolean) c[4]);
            ok(j != null && j.id().equals(c[5]),
                    (String) c[0] + ": wanted " + c[5] + ", got " + (j == null ? "none" : j.id()));
        }

        // -------------------------------------------------- the measured English series
        System.out.println();
        System.out.println("--- the measured English series ---");
        for (Object[] c : SECTORS) {
            Job j = t.at(51.51, -0.13, (Integer) yearOf((String) c[0]), false);
            ok(j != null && j.id().equals(c[0]), "cannot reach " + c[0]);
            if (j == null) {
                continue;
            }
            near((String) c[0] + " primary", j.sector(1), (Double) c[1], 2.0d);
            near((String) c[0] + " secondary", j.sector(2), (Double) c[2], 2.0d);
            near((String) c[0] + " tertiary", j.sector(3), (Double) c[3], 2.0d);
            System.out.printf(Locale.ROOT,
                    "  %-14s primary %5.1f/%2d  secondary %5.1f/%2d  tertiary %5.1f/%2d%n",
                    j.id(), (Double) c[1], j.sector(1), (Double) c[2], j.sector(2),
                    (Double) c[3], j.sector(3));
        }
        // the one thing the series proves: making things overtakes growing food between 1800 and 1841
        Job e1800 = t.at(51.51, -0.13, 1800, false);
        Job e1841 = t.at(51.51, -0.13, 1841, false);
        ok(e1800.sector(1) > e1800.sector(2), "in 1800 farming still employs more than making");
        ok(e1841.sector(2) > e1841.sector(1),
                "by 1841 making things should employ more than farming");

        // -------------------------------------------------- four thousand jobs each
        System.out.println();
        System.out.println("--- 4,000 jobs drawn from each regime ---");
        System.out.println("    (* = the shares are this table's own, so they cannot test it)");
        String[] regime = {"england_1688", "england_1800", "england_1841", "early_modern_europe",
                "early_modern_world", "british_india", "world_1950", "modern_world",
                "modern_europe", "modern_africa", "modern_india", "modern_east_asia",
                "modern_mena", "modern_latin", "modern_se_asia", "medieval_world",
                "late_medieval", "classical_world", "bronze_old_world", "foraging_band",
                "early_farming", "bronze_world", "industrial_town"};
        // lat, lon, year, urban
        double[][] where = {{51.51, -0.13, 1688, 0}, {51.51, -0.13, 1800, 0},
                {51.51, -0.13, 1841, 0}, {48.14, 11.58, 1700, 0}, {35.01, 135.77, 1700, 0},
                {17.39, 78.49, 1850, 0}, {62.03, 129.73, 1950, 0}, {62.03, 129.73, 2020, 0},
                {51.51, -0.13, 2020, 0}, {6.52, 3.38, 2020, 0}, {28.61, 77.21, 2020, 0},
                {39.90, 116.41, 2020, 0}, {30.04, 31.24, 2020, 0}, {-13.53, -71.97, 2020, 0},
                {-6.21, 106.85, 2020, 0}, {38.65, -90.06, 1100, 0}, {-13.53, -71.97, 1500, 0},
                {41.90, 12.50, 100, 0}, {41.90, 12.50, -1500, 0}, {-3.10, -60.02, -9000, 0},
                {-3.10, -60.02, -5000, 0}, {-3.10, -60.02, -1500, 0}, {51.51, -0.13, 1880, 1}};

        for (int i = 0; i < regime.length; i++) {
            Job j = t.at(where[i][0], where[i][1], (int) where[i][2], where[i][3] > 0);
            ok(j != null && j.id().equals(regime[i]),
                    "regime " + regime[i] + " not reachable in the probe");
            if (j == null) {
                continue;
            }
            int n = 4000;
            Map<String, Integer> tally = new LinkedHashMap<>();
            for (int k = 0; k < n; k++) {
                String w = t.pick(7919L * (k + 1) + 13L * i, where[i][0], where[i][1],
                        (int) where[i][2], where[i][3] > 0);
                tally.merge(w, 1, Integer::sum);
            }
            int bad = 0;
            for (String w : Jobs.WORKS) {
                double got = 100.0d * tally.getOrDefault(w, 0) / n;
                if (j.pub()) {
                    near(regime[i] + " " + w, got, j.share(w), 3.0d);
                }
                if (got > j.share(w) + 4.0d && j.share(w) == 0) {
                    bad++;
                }
            }
            ok(bad == 0, regime[i] + ": drew work the row says nobody does");
            System.out.printf(Locale.ROOT,
                    "%-20s%s farm %2d%%  make %2d%%  rest %2d%%   top: %s %d%%%n",
                    j.id(), j.pub() ? " " : "*", j.sector(1), j.sector(2), j.sector(3),
                    Jobs.plain(top(tally)), 100 * topCount(tally) / n);
        }

        // -------------------------------------------------- jobs hang off the land, not off a list
        System.out.println();
        System.out.println("--- the same row, read against three different landscapes ---");
        int[] none = {0, 0, 0};        // ArchaeoGLOBE: no foraging, no farming, no herding
        int[] pure = {3, 0, 0};        // foragers only
        int[] full = {3, 3, 3};
        for (int[] levels : new int[][]{pure, full, none}) {
            Map<String, Integer> tally = new LinkedHashMap<>();
            for (int k = 0; k < 4000; k++) {
                tally.merge(t.pick(31L * (k + 1), 51.51, -0.13, 1700, false, levels), 1,
                        Integer::sum);
            }
            System.out.printf(Locale.ROOT, "  foraging %d farming %d herding %d -> farm %d%%, "
                            + "herd %d%%, hunt %d%%, craft %d%%%n",
                    levels[0], levels[1], levels[2],
                    pct(tally, "farming"), pct(tally, "herding"), pct(tally, "foraging"),
                    pct(tally, "craft"));
        }
        // a place where nobody farms has almost no farmers, whatever the row for the era says
        Map<String, Integer> noFarm = new LinkedHashMap<>();
        for (int k = 0; k < 4000; k++) {
            noFarm.merge(t.pick(31L * (k + 1), 51.51, -0.13, 1700, false, pure), 1, Integer::sum);
        }
        ok(pct(noFarm, "farming") < 20,
                "a place with no agriculture should have few farmers, got " + pct(noFarm,
                        "farming") + "%");
        Map<String, Integer> allThree = new LinkedHashMap<>();
        for (int k = 0; k < 4000; k++) {
            allThree.merge(t.pick(31L * (k + 1), 51.51, -0.13, 1700, false, full), 1,
                    Integer::sum);
        }
        ok(pct(allThree, "farming") > pct(noFarm, "farming") * 2,
                "a farming landscape should have far more farmers than a foraging one");

        // -------------------------------------------------- six people's work
        System.out.println();
        System.out.println("--- six people, as the game would show them ---");
        String[][] six = {{"London 1688", "51.51", "-0.13", "1688"},
                {"London 1841", "51.51", "-0.13", "1841"},
                {"Hyderabad 1850", "17.39", "78.49", "1850"},
                {"Amazonia -9000", "-3.10", "-60.02", "-9000"},
                {"Lagos 2020", "6.52", "3.38", "2020"},
                {"London 2020", "51.51", "-0.13", "2020"}};
        for (int i = 0; i < six.length; i++) {
            double lat = Double.parseDouble(six[i][1]);
            double lon = Double.parseDouble(six[i][2]);
            int year = Integer.parseInt(six[i][3]);
            StringBuilder sb = new StringBuilder();
            for (int k = 0; k < 8; k++) {
                if (k > 0) {
                    sb.append(", ");
                }
                sb.append(Jobs.plain(t.pick(911L * (i + 1) + 17L * k, lat, lon, year, false)));
            }
            System.out.println("  " + six[i][0] + ": " + sb);
        }

        // -------------------------------------------------- what the table says
        System.out.println();
        System.out.println("--- what the table says, in words ---");
        String[][] words = {{"London", "51.51", "-0.13", "1688"},
                {"London", "51.51", "-0.13", "1841"}, {"Lagos", "6.52", "3.38", "2020"},
                {"London", "51.51", "-0.13", "2020"}, {"Amazonia", "-3.10", "-60.02", "-9000"}};
        for (String[] w : words) {
            System.out.println("  " + w[0] + " " + w[3] + ": "
                    + t.line(Double.parseDouble(w[1]), Double.parseDouble(w[2]),
                    Integer.parseInt(w[3]), false));
        }

        // -------------------------------------------------- provenance
        System.out.println();
        int withSource = 0;
        Map<String, Integer> marks = new LinkedHashMap<>();
        for (String[] s : HomeRun.SPOTS) {
            for (int y : YEARS) {
                Job j = t.at(Double.parseDouble(s[1]), Double.parseDouble(s[2]), y);
                if (j != null && !j.source().isEmpty()) {
                    withSource++;
                    marks.merge(j.mark(), 1, Integer::sum);
                }
            }
        }
        ok(withSource == HomeRun.SPOTS.length * YEARS.length,
                (HomeRun.SPOTS.length * YEARS.length - withSource) + " rows without a source");
        System.out.println("  " + withSource + " place-years, every one carrying a source: " + marks);

        System.out.println();
        System.out.println(failures.isEmpty() ? "ALL " + checks + " CHECKS PASSED"
                : failures.size() + " of " + checks + " CHECKS FAILED");
        for (String f : failures) {
            System.out.println("  - " + f);
        }
        return failures.isEmpty() ? 0 : 1;
    }

    private static int yearOf(String id) {
        return switch (id) {
            case "england_1688" -> 1688;
            case "england_1800" -> 1800;
            default -> 1841;
        };
    }

    private static String top(Map<String, Integer> tally) {
        String best = "service";
        int n = -1;
        for (Map.Entry<String, Integer> e : tally.entrySet()) {
            if (e.getValue() > n) {
                n = e.getValue();
                best = e.getKey();
            }
        }
        return best;
    }

    private static int topCount(Map<String, Integer> tally) {
        int n = -1;
        for (int v : tally.values()) {
            n = Math.max(n, v);
        }
        return n;
    }

    private static int pct(Map<String, Integer> tally, String work) {
        int total = 0;
        for (int v : tally.values()) {
            total += v;
        }
        return total == 0 ? 0 : Math.round(100.0f * tally.getOrDefault(work, 0) / total);
    }
}
